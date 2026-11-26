"""Public issuer containment and protected existing-task ingress behavior."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Barrier
from pathlib import Path

import pytest

from ab_harness import EnvironmentIngress, EnvironmentTaskRegistry, LifecycleLedger
from ab_harness import TaskIngressAuthority
from ab_harness import DomainContractPack, EnvironmentRun, InProcessEnvironmentOwner
from ab_harness import (
    OwnerExecutionResult,
    RegistrySnapshot,
    TaskIngressRule,
    TaskSpecCompiler,
)
from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.domain_lifecycle import DomainLifecycleAdmission
from ab_harness.lifecycle import AcceptanceFact, TaskIngressFact
from test_environment_ingress import (
    DOMAIN_PACK,
    OTHER_DOMAIN_PACK,
    _active_environment_run,
)
from test_two_stage_admission import _admission_fixture, _domain_pack_for_compiled
from test_two_stage_admission import _proposal, _semantic_admission


CLOCK = "2026-11-11T02:00:00Z"
CASES = (
    ("resume_task", "resume_request", "task_resumed"),
    ("notify_task", "task_notification", "task_notified"),
)


def authority_for(ledger, run, pack=DOMAIN_PACK, profile_id=None):
    return TaskIngressAuthority(
        environment_profile_id=profile_id or run.attestation.environment_profile_id,
        domain_contract_pack=pack,
        lifecycle_ledger=ledger,
    )


def start_task(path):
    run = _active_environment_run()
    ledger = LifecycleLedger(path, clock=lambda: CLOCK)
    authority = authority_for(ledger, run)
    ingress = EnvironmentIngress(
        environment_ingress_id="ingress:selection:start",
        environment_run_id=run.environment_run_id,
        binding_id="binding:synthetic.request:v1",
        ingress_type="user_request",
        payload_artifact_id="artifact:selection:start",
        native_lineage=(("goal_id", "goal:selection:001"),),
        observed_at=CLOCK,
    )
    start = authority.admit(run, ingress)
    assert start.action == "start_task" and start.reason_code == "matched_rule"
    assert len(ledger.events()) == 1
    assert ledger.replay(start.trace_id).terminal_status is None
    assert (
        EnvironmentTaskRegistry(ledger)
        .require_start(
            environment_run_id=run.environment_run_id,
            environment_ingress_id=ingress.environment_ingress_id,
            ingress_artifact_id=ingress.ingress_artifact_id,
            decision_id=start.decision_id,
            domain_contract_pack_revision=DOMAIN_PACK.revision,
            task_id=start.task_id,
            trace_id=start.trace_id,
        )
        .task_id
        == "goal:selection:001"
    )
    return ledger, authority, run, start


def feedback(run, action, ingress_type, task_id="goal:selection:001", suffix=""):
    return EnvironmentIngress(
        environment_ingress_id="ingress:selection:" + action + suffix,
        environment_run_id=run.environment_run_id,
        binding_id="binding:synthetic.feedback:v1",
        ingress_type=ingress_type,
        payload_artifact_id="artifact:selection:" + action + suffix,
        native_lineage=(("goal_id", task_id),),
        observed_at=CLOCK,
    )


def assert_association(ledger, start, ingress, decision, action, event_type, before):
    assert (
        decision.action == action and decision.reason_code == "matched_registered_task"
    )
    assert (decision.task_id, decision.trace_id) == (start.task_id, start.trace_id)
    assert decision.domain_contract_pack_revision == start.domain_contract_pack_revision
    events = ledger.events()
    assert len(events) == len(before) + 1
    assert events[:-1] == before
    event = events[-1]
    assert event.event_type == event_type
    assert (event.task_id, event.trace_id, event.environment_run_id) == (
        start.task_id,
        start.trace_id,
        start.environment_run_id,
    )
    assert event.parent_event_id == before[-1].event_id
    assert event.artifact_refs == (
        ingress.ingress_artifact_id,
        decision.decision_id,
        start.domain_contract_pack_revision,
    )
    assert event.data == dict(
        environment_ingress_id=ingress.environment_ingress_id,
        ingress_artifact_id=ingress.ingress_artifact_id,
        decision_id=decision.decision_id,
        domain_contract_pack_revision=start.domain_contract_pack_revision,
    )
    assert ledger.replay(start.trace_id).events == events


def raw_fact(start, ingress, decision):
    return TaskIngressFact(
        environment_run_id=start.environment_run_id,
        task_id=start.task_id,
        trace_id=start.trace_id,
        environment_ingress_id=ingress.environment_ingress_id,
        ingress_artifact_id=ingress.ingress_artifact_id,
        decision_id=decision.decision_id,
        domain_contract_pack_revision=start.domain_contract_pack_revision,
        action=decision.action,
    )


def genuine_reference(path, action, ingress_type, event_type):
    ledger, authority, run, start = start_task(path)
    prefix = path.read_bytes()
    before = ledger.events()
    ingress = feedback(run, action, ingress_type)
    decision = authority.admit(run, ingress)
    assert_association(ledger, start, ingress, decision, action, event_type, before)
    assert path.read_bytes().startswith(prefix)
    return prefix, start, ingress, decision


@pytest.mark.parametrize("action,ingress_type,event_type", CASES)
def test_genuine_ingress_reopens_and_duplicate_has_zero_append(
    tmp_path, action, ingress_type, event_type
):
    path = tmp_path / "genuine.jsonl"
    ledger, authority, run, start = start_task(path)
    prefix = path.read_bytes()
    before = ledger.events()
    ingress = feedback(run, action, ingress_type)
    decision = authority.admit(run, ingress)
    assert_association(ledger, start, ingress, decision, action, event_type, before)
    assert path.read_bytes().startswith(prefix)
    after = path.read_bytes()
    restarted = LifecycleLedger(path)
    assert restarted.events() == ledger.events()
    duplicate = authority_for(restarted, run).admit(run, ingress)
    assert duplicate.action == "reject"
    assert duplicate.reason_code == "duplicate_environment_ingress"
    assert (duplicate.task_id, duplicate.trace_id) == (start.task_id, start.trace_id)
    assert restarted.events() == ledger.events()
    assert path.read_bytes() == after


@pytest.mark.parametrize("action,ingress_type,event_type", CASES)
@pytest.mark.parametrize("destination", ("original-object", "reopened-object"))
def test_exported_fact_is_not_destination_issuer_authority(
    tmp_path, action, ingress_type, event_type, destination
):
    prefix, origin_start, ingress, decision = genuine_reference(
        tmp_path / "origin.jsonl",
        action,
        ingress_type,
        event_type,
    )
    path = tmp_path / "destination.jsonl"
    ledger, authority, run, start = start_task(path)
    assert path.read_bytes() == prefix
    assert start == origin_start
    if destination == "reopened-object":
        ledger = LifecycleLedger(path, clock=lambda: CLOCK)
    assert (
        EnvironmentTaskRegistry(ledger).lineage_for_ingress(
            environment_run_id=run.environment_run_id,
            environment_ingress_id=ingress.environment_ingress_id,
        )
        is None
    )
    before = ledger.events()
    with pytest.raises((TypeError, ValueError)):
        ledger.record(raw_fact(start, ingress, decision))
    assert ledger.events() == before
    assert path.read_bytes() == prefix
    assert LifecycleLedger(path).events() == before


@pytest.mark.parametrize("action,ingress_type,event_type", CASES)
@pytest.mark.parametrize(
    "field",
    (
        "task_id",
        "trace_id",
        "environment_run_id",
        "domain_contract_pack_revision",
        "action",
        "opposite-action",
    ),
)
def test_raw_mismatched_lineage_never_appends(
    tmp_path, action, ingress_type, event_type, field
):
    prefix, _, ingress, decision = genuine_reference(
        tmp_path / "origin.jsonl", action, ingress_type, event_type
    )
    path = tmp_path / "destination.jsonl"
    ledger, _, _, start = start_task(path)
    fact = raw_fact(start, ingress, decision)
    changed = "start_task" if field == "action" else "mismatch:" + field
    if field == "opposite-action":
        fact = replace(
            fact, action="notify_task" if action == "resume_task" else "resume_task"
        )
    else:
        fact = replace(fact, **{field: changed})
    before = ledger.events()
    with pytest.raises((TypeError, ValueError)):
        ledger.record(fact)
    assert ledger.events() == before
    assert path.read_bytes() == prefix


@pytest.mark.parametrize("action,ingress_type,event_type", CASES)
@pytest.mark.parametrize(
    "mismatch,reason",
    (
        ("ingress-run", "environment_run_mismatch"),
        ("other-active-run", "unknown_task_identity"),
        ("profile", "policy_environment_profile_mismatch"),
        ("pack", "policy_contract_revision_mismatch"),
        ("unknown-task", "unknown_task_identity"),
        ("missing-task", "missing_task_identity"),
        ("unsupported-type", "unsupported_ingress_type"),
    ),
)
def test_genuine_policy_rejection_preserves_prefix_and_valid_control(
    tmp_path, action, ingress_type, event_type, mismatch, reason
):
    path = tmp_path / "policy.jsonl"
    ledger, authority, run, start = start_task(path)
    before = ledger.events()
    prefix = path.read_bytes()
    ingress = feedback(run, action, ingress_type)
    wrong_run, wrong_authority, wrong_ingress = run, authority, ingress
    if mismatch == "ingress-run":
        wrong_ingress = replace(ingress, environment_run_id="environment-run:other")
    elif mismatch == "other-active-run":
        wrong_run = _active_environment_run(
            "environment-run:synthetic:002", "attestation:other"
        )
        wrong_ingress = replace(
            ingress, environment_run_id=wrong_run.environment_run_id
        )
    elif mismatch == "profile":
        wrong_authority = authority_for(
            ledger, run, profile_id="environment-profile:other"
        )
    elif mismatch == "pack":
        wrong_authority = authority_for(ledger, run, pack=OTHER_DOMAIN_PACK)
    elif mismatch == "unknown-task":
        wrong_ingress = replace(ingress, native_lineage=(("goal_id", "goal:unknown"),))
    elif mismatch == "missing-task":
        wrong_ingress = replace(ingress, native_lineage=())
    else:
        wrong_ingress = replace(ingress, ingress_type="unsupported_event")
    rejected = wrong_authority.admit(wrong_run, wrong_ingress)
    assert rejected.action == "reject" and rejected.reason_code == reason
    assert ledger.events() == before
    assert path.read_bytes() == prefix
    assert LifecycleLedger(path).events() == before
    admitted = authority.admit(run, ingress)
    assert_association(ledger, start, ingress, admitted, action, event_type, before)
    assert path.read_bytes().startswith(prefix)


@pytest.mark.parametrize("action,ingress_type,event_type", CASES)
def test_two_public_issuers_have_one_duplicate_winner(
    tmp_path, action, ingress_type, event_type
):
    path = tmp_path / "contended.jsonl"
    seeded, _, run, start = start_task(path)
    before = seeded.events()
    prefix = path.read_bytes()
    writers = [LifecycleLedger(path, clock=lambda: CLOCK) for _ in range(2)]
    issuers = [authority_for(writer, run) for writer in writers]
    ingress = feedback(run, action, ingress_type)
    ready = Barrier(2)

    def submit(issuer):
        ready.wait(timeout=5)
        return issuer.admit(run, ingress)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(submit, issuer) for issuer in issuers]
        decisions = [future.result(timeout=10) for future in futures]
    assert sorted(decision.action for decision in decisions) == sorted(
        (action, "reject")
    )
    winner = next(decision for decision in decisions if decision.action == action)
    loser = next(decision for decision in decisions if decision.action == "reject")
    assert loser.reason_code == "duplicate_environment_ingress"
    assert (loser.task_id, loser.trace_id) == (start.task_id, start.trace_id)
    restarted = LifecycleLedger(path)
    assert_association(restarted, start, ingress, winner, action, event_type, before)
    assert path.read_bytes().startswith(prefix)


def acceptance_fixture(path, outcome):
    """New current fixture with BOTH frozen rules and real public acceptance."""
    registry_path = Path(__file__).resolve().parent / "fixtures" / "ab_registry.json"
    template, catalog, original_run = _admission_fixture(registry_path=registry_path)
    original_pack = _domain_pack_for_compiled(template)
    pack = DomainContractPack.issue(
        domain_contract_pack_id=original_pack.domain_contract_pack_id,
        frame_id=original_pack.frame_id,
        registry_version=original_pack.registry_version,
        allowed_role_ids=original_pack.allowed_role_ids,
        supported_task_type_ids=original_pack.supported_task_type_ids,
        ingress_rules=(
            *original_pack.ingress_rules,
            TaskIngressRule(
                binding_id="binding:nao.feedback:v1",
                ingress_type="task_notification",
                action="notify_task",
                task_id_lineage_key="goal_id",
            ),
        ),
        effect_rules=original_pack.effect_rules,
    )
    run = EnvironmentRun(
        replace(original_run.attestation, domain_contract_pack_revision=pack.revision)
    )
    ledger = LifecycleLedger(path, clock=lambda: "2026-09-28T12:00:00Z")
    authority = authority_for(ledger, run, pack)
    start_ingress = EnvironmentIngress(
        environment_ingress_id=template.environment_ingress_id,
        environment_run_id=run.environment_run_id,
        binding_id="binding:nao.request:v1",
        ingress_type="user_request",
        payload_artifact_id="artifact:boundary:acceptance-start",
        native_lineage=(("goal_id", template.task_id),),
        observed_at="2026-09-28T09:00:01Z",
    )
    start = authority.admit(run, start_ingress)
    assert start.action == "start_task"
    compiled = TaskSpecCompiler().compile(
        task_ingress_decision=start,
        task_spec=replace(
            template.task_spec,
            domain_contract_pack_revision=pack.revision,
            trace_id=start.trace_id,
        ),
        role=template.interaction_module.role,
        frame=template.interaction_module.frame,
        registry=RegistrySnapshot.from_json_file(registry_path),
        domain_contract_pack=pack,
        task_registry=EnvironmentTaskRegistry(ledger),
    )
    ledger.record(compiled)
    evidence = ()
    if outcome != "suspended":
        proposal = _proposal(compiled, operation_id="operation:boundary:acceptance")
        ledger.record(proposal)
        admitted = (
            _semantic_admission(catalog).admit(compiled, proposal).admitted_operation
        )
        assert admitted is not None
        ledger.record(admitted)
        lease = (
            DomainLifecycleAdmission(
                environment_run=run,
                environment_id="nao_fake",
                lifecycle_ledger=ledger,
            )
            .request_execution(admitted)
            .execution_lease
        )
        assert lease is not None
        succeeded = outcome == "accepted"
        owner = InProcessEnvironmentOwner(
            environment_id="nao_fake",
            environment_run=run,
            catalog=catalog,
            lifecycle_ledger=ledger,
            handlers={
                "fake_nao.skills:find_object": lambda _arguments: OwnerExecutionResult(
                    evidence_ref="fake-nao://boundary/acceptance",
                    succeeded=succeeded,
                    observed_effects=("fresh detector-backed result returned",)
                    if succeeded
                    else (),
                )
            },
        )
        receipt = owner.execute(lease).receipt
        assert receipt is not None
        evidence = (receipt.evidence,)
    acceptance = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations, evidence
    )
    assert acceptance.status == outcome
    ledger.record(AcceptanceFact(compiled, evidence, acceptance))
    replay = LifecycleLedger(path).replay(compiled.trace_id)
    assert replay.terminal_status == (None if outcome == "suspended" else outcome)
    assert any(
        event.event_type
        == ("task_suspended" if outcome == "suspended" else "terminal_task_" + outcome)
        for event in replay.events
    )
    return ledger, run, pack, start, compiled


def acceptance_feedback(run, start, action, ingress_type):
    return EnvironmentIngress(
        environment_ingress_id="ingress:boundary:after-acceptance:" + action,
        environment_run_id=run.environment_run_id,
        binding_id="binding:nao.feedback:v1",
        ingress_type=ingress_type,
        payload_artifact_id="artifact:boundary:after-acceptance",
        native_lineage=(("goal_id", start.task_id),),
        observed_at="2026-09-28T12:01:00Z",
    )


@pytest.mark.parametrize("action,ingress_type,event_type", CASES)
@pytest.mark.parametrize("outcome", ("accepted", "rejected"))
def test_durable_terminal_judgment_rejects_later_ingress_without_append(
    tmp_path, action, ingress_type, event_type, outcome
):
    path = tmp_path / "terminal.jsonl"
    ledger, run, pack, start, compiled = acceptance_fixture(path, outcome)
    before, prefix = ledger.events(), path.read_bytes()
    restarted = LifecycleLedger(path)
    decision = authority_for(restarted, run, pack).admit(
        run, acceptance_feedback(run, start, action, ingress_type)
    )
    assert decision.action == "reject" and decision.reason_code == "task_terminal"
    assert decision.task_status == outcome
    assert (decision.task_id, decision.trace_id) == (start.task_id, start.trace_id)
    assert restarted.events() == before
    assert path.read_bytes() == prefix
    assert restarted.replay(compiled.trace_id).terminal_status == outcome


@pytest.mark.parametrize("action,ingress_type,event_type", CASES)
def test_real_suspended_task_remains_associable_without_recompile_or_budget_reset(
    tmp_path, action, ingress_type, event_type
):
    path = tmp_path / "suspended.jsonl"
    ledger, run, pack, start, compiled = acceptance_fixture(path, "suspended")
    before, prefix = ledger.events(), path.read_bytes()
    compiled_before = [
        event.to_dict() for event in before if event.event_type == "task_compiled"
    ]
    restarted = LifecycleLedger(path)
    ingress = acceptance_feedback(run, start, action, ingress_type)
    decision = authority_for(restarted, run, pack).admit(run, ingress)
    assert_association(restarted, start, ingress, decision, action, event_type, before)
    assert path.read_bytes().startswith(prefix)
    assert [
        event.to_dict()
        for event in restarted.events()
        if event.event_type == "task_compiled"
    ] == compiled_before
    assert not any(event.event_type == "budget_granted" for event in restarted.events())
    assert restarted.replay(compiled.trace_id).terminal_status is None
    assert LifecycleLedger(path).events() == restarted.events()


@pytest.mark.parametrize("action,ingress_type,event_type", CASES)
def test_recreated_issuer_can_admit_fresh_ingress_on_same_file(
    tmp_path, action, ingress_type, event_type
):
    path = tmp_path / "restart-before-association.jsonl"
    ledger, _, run, start = start_task(path)
    before, prefix = ledger.events(), path.read_bytes()
    restarted = LifecycleLedger(path, clock=lambda: CLOCK)
    ingress = feedback(run, action, ingress_type)
    decision = authority_for(restarted, run).admit(run, ingress)
    assert_association(restarted, start, ingress, decision, action, event_type, before)
    assert path.read_bytes().startswith(prefix)
    assert LifecycleLedger(path).events() == restarted.events()
