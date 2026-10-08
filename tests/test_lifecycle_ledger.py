import hashlib
import json

import pytest

from ab_harness.lifecycle import LifecycleLedger
from ab_harness.lifecycle import LifecycleSequenceConflict
from ab_harness.lifecycle import TaskIngressFact
from ab_harness.lifecycle import TraceEvent
from ab_harness.observatory import project_observatory
from ab_harness.observatory import render_observatory
from ab_harness.task_registry import EnvironmentTaskRegistry


INGRESS_ARTIFACT_ID = "environment-ingress:sha256:8f47a0e41c10ef678add0842429b05018bfe4144d0fe1ebe424a53160d11dc3b"
DECISION_ID = "task-ingress-decision:sha256:eea014719cba0f6034378376423e5538d07c0bbb739bbeb9cfe33bb24cfe5cf1"
DOMAIN_REVISION = "sha256:dadb666ec64ed9fe37fab31d201a32dcd45e60d103b411b42e2205aafaacb731"
TRACE_ID = "trace:sha256:2c443758d1b81e09308e6fc742e2f1456418ea5618cba40708c5ae2290ff0e43"


def _ledger(path):
    from ab_harness import EnvironmentIngress, TaskIngressAuthority
    from test_environment_ingress import DOMAIN_PACK, _active_environment_run

    ledger = LifecycleLedger(path, clock=lambda: "2026-09-28T13:00:00Z")
    run = _active_environment_run("environment-run:ledger:001")
    decision = TaskIngressAuthority(
        environment_profile_id=run.attestation.environment_profile_id,
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=ledger,
    ).admit(
        run,
        EnvironmentIngress(
            environment_ingress_id="ingress:ledger:start",
            environment_run_id=run.environment_run_id,
            binding_id="binding:synthetic.request:v1",
            ingress_type="user_request",
            payload_artifact_id="artifact:ledger:start",
            native_lineage=(("goal_id", "task:ledger:001"),),
            observed_at="2026-09-28T13:00:00Z",
        )
    )
    ledger.record(
        TaskIngressFact(
            environment_run_id="environment-run:ledger:001",
            task_id="task:ledger:001",
            trace_id=decision.trace_id,
            environment_ingress_id="ingress:ledger:resume",
            ingress_artifact_id="environment-ingress:sha256:ledger-resume",
            decision_id="task-ingress-decision:sha256:ledger-resume",
            domain_contract_pack_revision=decision.domain_contract_pack_revision,
            action="resume_task",
        )
    )
    return ledger


def test_common_ledger_round_trips_strict_events_and_registry_projection(tmp_path):
    path = tmp_path / "lifecycle.jsonl"
    ledger = _ledger(path)

    restarted = LifecycleLedger(path)
    registry = EnvironmentTaskRegistry(restarted)

    assert restarted.events() == ledger.events()
    lineage = registry.require_start(
        environment_run_id="environment-run:ledger:001",
        environment_ingress_id="ingress:ledger:start",
        ingress_artifact_id=INGRESS_ARTIFACT_ID,
        decision_id=DECISION_ID,
        domain_contract_pack_revision=DOMAIN_REVISION,
        task_id="task:ledger:001",
        trace_id=TRACE_ID,
    )
    assert lineage.starting_decision_id == DECISION_ID


def test_trace_event_rejects_modified_content():
    event = _ledger(None).events()[0]
    payload = event.to_dict()
    payload["task_id"] = "task:tampered"

    with pytest.raises(ValueError, match="identity does not match"):
        TraceEvent.from_dict(payload)


@pytest.mark.parametrize("source", ["events", "replay", "commit"])
def test_public_event_exports_do_not_alias_ledger_authority(source):
    ledger = _ledger(None)
    if source == "events":
        exported = ledger.events()[-1]
    elif source == "replay":
        exported = ledger.replay(TRACE_ID).events[-1]
    else:
        exported = ledger.record(
            TaskIngressFact(
                environment_run_id="environment-run:ledger:001",
                task_id="task:ledger:001",
                trace_id=TRACE_ID,
                environment_ingress_id="ingress:ledger:notify",
                ingress_artifact_id="environment-ingress:sha256:ledger-notify",
                decision_id="task-ingress-decision:sha256:ledger-notify",
                domain_contract_pack_revision=DOMAIN_REVISION,
                action="notify_task",
            )
        ).events[-1]
    original = tuple(event.to_dict() for event in ledger.events())
    object.__setattr__(exported, "event_type", "terminal_task_accepted")

    assert tuple(event.to_dict() for event in ledger.events()) == original
    assert ledger.replay(TRACE_ID).terminal_status is None
    assert project_observatory(ledger).traces[0].status.value == "open"


@pytest.mark.parametrize("consumer", ["data", "serialization", "render"])
@pytest.mark.parametrize("mutation", ["event_type", "data_json"])
def test_foreign_event_with_stale_identity_is_rejected(consumer, mutation):
    events = _ledger(None).events()
    value = "terminal_task_accepted" if mutation == "event_type" else '{"forged":true}'
    object.__setattr__(events[-1], mutation, value)

    with pytest.raises(ValueError, match="identity does not match"):
        if consumer == "data":
            events[-1].data
        elif consumer == "serialization":
            events[-1].to_dict()
        else:
            render_observatory(events)


@pytest.mark.parametrize("file_backed", [False, True])
@pytest.mark.parametrize("source", ["events", "commit", "replay", "source_fact"])
def test_exported_budget_mutation_cannot_grant_extra_model_calls(
    tmp_path, file_backed, source
):
    from test_two_stage_admission import _admission_fixture
    from test_two_stage_admission import _record_task_start
    from ab_harness.runtime_controls import TaskBudgetAuthority

    compiled, _, _ = _admission_fixture()
    ledger = LifecycleLedger(tmp_path / "budget.jsonl" if file_backed else None)
    _record_task_start(ledger, compiled)
    commit = ledger.record(compiled)
    authority = TaskBudgetAuthority(ledger)
    for index in range(3):
        decision = authority.consume(
            trace_id=compiled.trace_id,
            resource="model_call",
            subject_id="invocation:ledger:%s" % index,
        )
        assert decision.outcome == "granted"

    if source == "source_fact":
        object.__setattr__(compiled.task_spec.budgets, "model_calls", 99)
    else:
        events = {
            "events": ledger.events(),
            "commit": commit.events,
            "replay": ledger.replay(compiled.trace_id).events,
        }[source]
        exported = next(
            event for event in events if event.event_type == "task_compiled"
        )
        data = exported.data
        data["budgets"]["model_calls"] = 99
        object.__setattr__(
            exported,
            "data_json",
            json.dumps(data, sort_keys=True, separators=(",", ":")),
        )

    assessment = authority.assess(
        trace_id=compiled.trace_id,
        resource="model_call",
        subject_id="invocation:ledger:extra",
    )
    assert (assessment.decision.outcome, assessment.decision.limit) == ("exhausted", 3)
    decision = authority.consume(
        trace_id=compiled.trace_id,
        resource="model_call",
        subject_id="invocation:ledger:extra",
    )
    assert (decision.outcome, decision.limit, decision.consumed_after) == (
        "exhausted",
        3,
        3,
    )
    assert ledger.replay(compiled.trace_id).terminal_status is None
    if file_backed:
        assert LifecycleLedger(ledger.path).events() == ledger.events()


def test_common_ledger_rejects_an_unterminated_record(tmp_path):
    path = tmp_path / "unterminated.jsonl"
    path.write_text(json.dumps(_ledger(None).events()[0].to_dict()), encoding="utf-8")

    with pytest.raises(ValueError, match="unterminated final record"):
        LifecycleLedger(path)


def test_common_ledger_rejects_a_blank_record(tmp_path):
    path = tmp_path / "blank.jsonl"
    first, second = _ledger(None).events()
    path.write_text(
        json.dumps(first.to_dict()) + "\n\n" + json.dumps(second.to_dict()) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="line 2"):
        LifecycleLedger(path)


def test_common_ledger_rejects_non_utf8_content(tmp_path):
    path = tmp_path / "invalid-utf8.jsonl"
    path.write_bytes(b"\xff\n")

    with pytest.raises(ValueError, match="not valid UTF-8"):
        LifecycleLedger(path)


def test_expected_sequence_rejects_a_stale_writer(tmp_path):
    ledger = _ledger(tmp_path / "sequence.jsonl")

    with pytest.raises(LifecycleSequenceConflict, match="sequence conflict"):
        ledger.record(
            TaskIngressFact(
                environment_run_id="environment-run:ledger:001",
                task_id="task:ledger:001",
                trace_id="trace:ledger:001",
                environment_ingress_id="ingress:ledger:notify",
                ingress_artifact_id="environment-ingress:sha256:ledger-notify",
                decision_id="task-ingress-decision:sha256:ledger-notify",
                domain_contract_pack_revision=DOMAIN_REVISION,
                action="notify_task",
            ),
            expected_sequence=1,
        )


def test_missing_ledger_path_starts_as_an_empty_ledger(tmp_path):
    ledger = LifecycleLedger(tmp_path / "not-created-yet.jsonl")

    assert ledger.events() == ()


def test_common_ledger_rejects_a_duplicated_event_record(tmp_path):
    event = _ledger(None).events()[0]
    path = tmp_path / "duplicate.jsonl"
    encoded = json.dumps(event.to_dict())
    path.write_text(encoded + "\n" + encoded + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="sequence"):
        LifecycleLedger(path)


def test_common_ledger_rejects_an_unknown_event_type(tmp_path):
    first, second = _ledger(None).events()
    payload = second.to_dict()
    payload["event_type"] = "invented_lifecycle_event"
    identity = {key: value for key, value in payload.items() if key != "event_id"}
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    payload["event_id"] = "trace-event:sha256:%s" % hashlib.sha256(encoded).hexdigest()
    path = tmp_path / "unknown-event.jsonl"
    path.write_text(
        json.dumps(first.to_dict()) + "\n" + json.dumps(payload) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unsupported lifecycle event type"):
        LifecycleLedger(path)


def test_common_ledger_fences_existing_task_ingress_across_stale_writers(tmp_path):
    path = tmp_path / "contended-ingress.jsonl"
    _ledger(path)
    first = LifecycleLedger(path, clock=lambda: "2026-09-28T13:00:01Z")
    stale = LifecycleLedger(path, clock=lambda: "2026-09-28T13:00:02Z")
    fact = TaskIngressFact(
        environment_run_id="environment-run:ledger:001",
        task_id="task:ledger:001",
        trace_id=TRACE_ID,
        environment_ingress_id="ingress:ledger:contended",
        ingress_artifact_id="environment-ingress:sha256:ledger-contended",
        decision_id="task-ingress-decision:sha256:ledger-contended",
        domain_contract_pack_revision=DOMAIN_REVISION,
        action="resume_task",
    )

    first.record(fact)
    with pytest.raises(ValueError, match="duplicate task ingress"):
        stale.record(fact)

    assert tuple(
        event.data.get("environment_ingress_id")
        for event in LifecycleLedger(path).events()
        if event.event_type in {"task_started", "task_resumed", "task_notified"}
    ).count(fact.environment_ingress_id) == 1
