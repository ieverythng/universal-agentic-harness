import hashlib
import json

import pytest

from ab_harness.lifecycle import LifecycleLedger
from ab_harness.lifecycle import LifecycleSequenceConflict
from ab_harness.lifecycle import TaskIngressFact
from ab_harness.lifecycle import TaskStartedFact
from ab_harness.lifecycle import TraceEvent
from ab_harness.task_registry import EnvironmentTaskRegistry


INGRESS_ARTIFACT_ID = "environment-ingress:sha256:ledger-start"
DECISION_ID = "task-ingress-decision:sha256:ledger-start"
DOMAIN_REVISION = "sha256:ledger-domain-pack"


def _ledger(path):
    ledger = LifecycleLedger(path, clock=lambda: "2026-09-28T13:00:00Z")
    ledger.record(
        TaskStartedFact(
            environment_run_id="environment-run:ledger:001",
            task_id="task:ledger:001",
            trace_id="trace:ledger:001",
            environment_ingress_id="ingress:ledger:start",
            ingress_artifact_id=INGRESS_ARTIFACT_ID,
            decision_id=DECISION_ID,
            domain_contract_pack_revision=DOMAIN_REVISION,
        )
    )
    ledger.record(
        TaskIngressFact(
            environment_run_id="environment-run:ledger:001",
            task_id="task:ledger:001",
            trace_id="trace:ledger:001",
            environment_ingress_id="ingress:ledger:resume",
            ingress_artifact_id="environment-ingress:sha256:ledger-resume",
            decision_id="task-ingress-decision:sha256:ledger-resume",
            domain_contract_pack_revision=DOMAIN_REVISION,
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
        trace_id="trace:ledger:001",
    )
    assert lineage.starting_decision_id == DECISION_ID


def test_trace_event_rejects_modified_content():
    event = _ledger(None).events()[0]
    payload = event.to_dict()
    payload["task_id"] = "task:tampered"

    with pytest.raises(ValueError, match="identity does not match"):
        TraceEvent.from_dict(payload)


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
        trace_id="trace:ledger:001",
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
