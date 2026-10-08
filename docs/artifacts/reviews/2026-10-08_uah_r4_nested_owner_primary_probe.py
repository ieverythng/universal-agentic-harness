"""Independent frozen-artifact probes; run against current and exact-before."""

import hashlib
import json

import pytest

from ab_harness import DomainLifecycleAdmission, LifecycleLedger
from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.contracts import EffectEvidence, OwnerExecutionResult
from ab_harness.domain_lifecycle import ExecutionLease
from ab_harness.environment import ExecutionReceipt
from ab_harness.lifecycle import AcceptanceFact
from ab_harness.proposal_admission import AdmittedOperation, TypedProposal
from test_admitted_object_snapshot import FRESH_EFFECT, authority_fixture, owner_for
from test_two_stage_admission import _proposal, _semantic_admission


def install_masks(artifacts, calls):
    for artifact in artifacts:
        wire = artifact.to_dict()
        object.__setattr__(artifact, "to_dict", lambda w=wire: calls.append("wire") or w)
        object.__setattr__(artifact, "verify_identity", lambda: calls.append("verify"))
        object.__setattr__(artifact, "verified_copy", lambda: calls.append("copy"))


def receipt_inputs(admitted):
    result = OwnerExecutionResult("native:independent", True, (FRESH_EFFECT,))
    evidence = EffectEvidence(
        result.evidence_ref, admitted.object_id, admitted.binding_id,
        admitted.environment_id, admitted.binding_owner, True, (FRESH_EFFECT,),
    )
    return result, evidence


@pytest.mark.parametrize("field", ["proposal", "admission", "lease", "both", "owner", "snapshot"])
@pytest.mark.parametrize("crossing", ["wire", "domain", "dispatch", "receipt", "provenance", "ledger_start"])
def test_independent_stale_fields_reject_before_any_effect(tmp_path, field, crossing):
    _, catalog, environment, ledger, admitted, lease = authority_fixture(tmp_path)
    calls, native = [], []
    install_masks((admitted.proposal, admitted, lease), calls)
    calls.clear()
    if field in {"proposal", "both"}:
        object.__setattr__(admitted.proposal, "arguments_json", '{"label":"mug"}')
    if field in {"admission", "both"}:
        object.__setattr__(admitted, "admission_id", "admission:sha256:stale")
    if field == "lease":
        object.__setattr__(lease, "execution_lease_id", "execution-lease:sha256:stale")
    if field == "owner":
        object.__setattr__(admitted, "binding_owner", "foreign_owner")
    if field == "snapshot":
        object.__setattr__(admitted.object_snapshot, "observable_success", ())
    before = ledger.path.read_bytes()
    with pytest.raises(ValueError):
        if crossing == "wire":
            ExecutionLease.to_dict(lease)
        elif crossing == "domain":
            if field == "lease":
                ExecutionLease.verify_identity(lease)
            else:
                DomainLifecycleAdmission(
                    environment_run=environment, environment_id="nao_fake",
                    lifecycle_ledger=ledger,
                ).request_execution(admitted)
        elif crossing == "dispatch":
            owner_for(catalog, environment, ledger, lambda args: native.append(args)).execute(lease)
        elif crossing == "receipt":
            result, evidence = receipt_inputs(admitted)
            ExecutionReceipt.issue(lease=lease, owner_result=result, evidence=evidence)
        elif crossing == "provenance":
            if field == "lease":
                ExecutionLease.verify_identity(lease)
            else:
                ledger.require_current_admission(admitted)
        else:
            ledger.start_execution(lease)
    assert native == []
    assert calls == []
    assert ledger.path.read_bytes() == before


@pytest.mark.parametrize("field", ["arguments", "snapshot", "outer", "all"])
@pytest.mark.parametrize("outcome", ["success", "evidence_rejection", "failure"])
def test_independent_callback_mutation_retains_dispatch_receipt_and_replay(tmp_path, field, outcome):
    compiled, catalog, environment, ledger, admitted, lease = authority_fixture(tmp_path)
    original_wire = ExecutionLease.to_dict(lease)
    calls = []

    def handler(arguments):
        calls.append(arguments)
        if field in {"arguments", "all"}:
            object.__setattr__(admitted.proposal, "arguments_json", '{"label":"mug"}')
        if field in {"snapshot", "all"}:
            object.__setattr__(admitted.object_snapshot, "observable_success", ("direct_speech",))
        if field in {"outer", "all"}:
            object.__setattr__(admitted, "admission_id", "admission:sha256:changed")
            object.__setattr__(lease, "lease_owner_id", "foreign_owner")
        if outcome == "failure":
            raise RuntimeError("native owner failed after caller mutation")
        effects = (FRESH_EFFECT,) if outcome == "success" else ("direct_speech",)
        return OwnerExecutionResult("native:callback-control", True, effects)

    owner = owner_for(catalog, environment, ledger, handler)
    if outcome == "failure":
        with pytest.raises(RuntimeError, match="native owner failed"):
            owner.execute(lease)
        expected_stage = "execution"
    else:
        decision = owner.execute(lease)
        if outcome == "success":
            receipt = decision.receipt
            assert receipt is not None
            ExecutionReceipt.verify_identity(receipt)
            assert receipt.execution_lease_id == original_wire["execution_lease_id"]
            assert receipt.admission_id == original_wire["admitted_operation"]["admission_id"]
            acceptance = TaskAcceptanceEvaluator().evaluate(compiled.effect_obligations, (receipt.evidence,))
            ledger.record(AcceptanceFact(compiled, (receipt.evidence,), acceptance))
            expected_stage = None
        else:
            assert decision.receipt is None
            assert decision.rejection.reason_codes == ("undeclared_observed_effect",)
            expected_stage = "evidence"
    assert calls == [{"label": "cup"}]
    replay = LifecycleLedger(ledger.path).replay(compiled.trace_id)
    assert replay.failure_stage == expected_stage
    assert replay.terminal_status == ("accepted" if outcome == "success" else None)
    assert len([event for event in replay.events if event.event_type == "execution_started"]) == 1


@pytest.mark.parametrize("order", [("operation:first", "operation:second"), ("operation:second", "operation:first")])
def test_independent_two_operations_are_distinct_in_both_orders(tmp_path, order):
    compiled, catalog, environment, ledger, admitted, lease = authority_fixture(tmp_path)
    leases = {admitted.operation_id: lease}
    for operation_id in order:
        proposal = _proposal(compiled, operation_id=operation_id)
        fresh = _semantic_admission(catalog).admit(compiled, proposal).admitted_operation
        ledger.record(proposal)
        ledger.record(fresh)
        leases[operation_id] = DomainLifecycleAdmission(
            environment_run=environment, environment_id="nao_fake", lifecycle_ledger=ledger,
        ).request_execution(fresh).execution_lease
    calls = []
    owner = owner_for(catalog, environment, ledger, lambda args: calls.append(args) or OwnerExecutionResult("native:multi", True, (FRESH_EFFECT,)))
    receipts = [owner.execute(leases[operation_id]).receipt for operation_id in order]
    assert [receipt.operation_id for receipt in receipts] == list(order)
    assert len({receipt.execution_lease_id for receipt in receipts}) == 2
    assert calls == [{"label": "cup"}, {"label": "cup"}]
    reloaded = LifecycleLedger(ledger.path)
    assert [event.operation_id for event in reloaded.events() if event.event_type == "execution_completed"] == list(order)
    for operation_id in order:
        with pytest.raises(ValueError, match="already"):
            owner.execute(leases[operation_id])


@pytest.mark.parametrize("crossing", ["admitted_wire", "lease_wire", "domain", "dispatch", "receipt", "provenance"])
def test_independent_valid_nested_identity_cannot_hide_stale_outer(tmp_path, crossing):
    _, catalog, environment, ledger, admitted, lease = authority_fixture(tmp_path)
    original = TypedProposal.to_dict(admitted.proposal)
    changed = dict(original, arguments_json='{"label":"mug"}')
    content = {key: value for key, value in changed.items() if key != "proposal_id"}
    changed["proposal_id"] = "proposal:sha256:" + hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    alternative = TypedProposal(**changed)
    TypedProposal.verify_identity(alternative)
    object.__setattr__(alternative, "to_dict", lambda: original)
    object.__setattr__(admitted, "proposal", alternative)
    before = ledger.path.read_bytes()
    with pytest.raises(ValueError, match="identity"):
        if crossing == "admitted_wire":
            AdmittedOperation.to_dict(admitted)
        elif crossing == "lease_wire":
            ExecutionLease.to_dict(lease)
        elif crossing == "domain":
            DomainLifecycleAdmission(environment_run=environment, environment_id="nao_fake", lifecycle_ledger=ledger).request_execution(admitted)
        elif crossing == "dispatch":
            owner_for(catalog, environment, ledger, lambda _: pytest.fail("native dispatch")).execute(lease)
        elif crossing == "receipt":
            result, evidence = receipt_inputs(admitted)
            ExecutionReceipt.issue(lease=lease, owner_result=result, evidence=evidence)
        else:
            ledger.require_current_admission(admitted)
    assert ledger.path.read_bytes() == before
