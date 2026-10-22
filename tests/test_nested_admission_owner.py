"""Artifact owners validate concrete nested fields, not instance methods."""

import hashlib
import json

import pytest

from ab_harness.proposal_admission import AdmittedOperation, TypedProposal
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.contracts import OwnerExecutionResult
from ab_harness.contracts import EffectEvidence
from ab_harness import DomainLifecycleAdmission
from ab_harness.domain_lifecycle import ExecutionLease
from ab_harness.environment import ExecutionReceipt
from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.lifecycle import AcceptanceFact
from test_admitted_object_snapshot import FRESH_EFFECT, authority_fixture, owner_for


def substitute_proposal_with_misreported_wire(admitted):
    original = admitted.proposal.to_dict()
    changed = dict(original, arguments_json='{"label":"mug"}')
    payload = {key: value for key, value in changed.items() if key != "proposal_id"}
    changed["proposal_id"] = (
        "proposal:sha256:"
        + hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )
    proposal = TypedProposal(**changed)
    object.__setattr__(proposal, "to_dict", lambda: dict(original))
    object.__setattr__(admitted, "proposal", proposal)
    return original


def test_outer_identity_uses_actual_nested_fields_despite_instance_serializer(tmp_path):
    _, _, _, ledger, admitted, _ = authority_fixture(tmp_path)
    before = ledger.path.read_bytes()
    original = substitute_proposal_with_misreported_wire(admitted)
    assert admitted.proposal.arguments == {"label": "mug"}
    assert admitted.proposal.to_dict() == original
    TypedProposal.verify_identity(admitted.proposal)
    with pytest.raises(ValueError, match="identity"):
        AdmittedOperation.verify_identity(admitted)
    assert ledger.path.read_bytes() == before


def test_dispatch_and_receipt_use_detached_authority_when_caller_fields_change(
    tmp_path,
):
    _, catalog, environment, ledger, admitted, lease = authority_fixture(tmp_path)
    original_admission = admitted.admission_id
    calls = []

    def handler(arguments):
        calls.append(arguments)
        object.__setattr__(admitted.proposal, "arguments_json", '{"label":"mug"}')
        return OwnerExecutionResult("native:detached", True, (FRESH_EFFECT,))

    decision = owner_for(catalog, environment, ledger, handler).execute(lease)
    assert calls == [{"label": "cup"}]
    assert decision.receipt is not None
    assert decision.receipt.admission_id == original_admission
    assert admitted.proposal.arguments == {"label": "mug"}


def test_proposal_record_ignores_instance_noop_verifier(tmp_path):
    _, _, _, ledger, admitted, _ = authority_fixture(tmp_path)
    ledger.path.write_text("\n".join(ledger.path.read_text().splitlines()[:2]) + "\n")
    ledger = LifecycleLedger(ledger.path)
    proposal = admitted.proposal
    object.__setattr__(proposal, "arguments_json", '{"label":"mug"}')
    object.__setattr__(proposal, "verify_identity", lambda: None)
    before = ledger.path.read_bytes()
    with pytest.raises(ValueError, match="identity"):
        ledger.record(proposal)
    assert ledger.path.read_bytes() == before


@pytest.mark.parametrize("attack", ["serializer", "verifier", "both"])
@pytest.mark.parametrize(
    "crossing",
    ["fresh_lease", "reuse_lease", "dispatch", "receipt", "wire", "provenance"],
)
def test_nested_instance_methods_cannot_hide_actual_fields(tmp_path, attack, crossing):
    _, catalog, environment, ledger, admitted, lease = authority_fixture(tmp_path)
    if crossing == "fresh_lease":
        ledger.path.write_text(
            "\n".join(ledger.path.read_text().splitlines()[:-1]) + "\n"
        )
        ledger = LifecycleLedger(ledger.path)
    hooks, native = [], []
    if attack in {"serializer", "both"}:
        original = substitute_proposal_with_misreported_wire(admitted)

        def misreport():
            hooks.append("serializer")
            return dict(original)

        object.__setattr__(admitted.proposal, "to_dict", misreport)
    else:
        object.__setattr__(admitted.proposal, "arguments_json", '{"label":"mug"}')
    if attack in {"verifier", "both"}:
        for item in (admitted.proposal, admitted, lease):
            object.__setattr__(
                item, "verify_identity", lambda: hooks.append("verifier")
            )
            object.__setattr__(item, "verified_copy", lambda: hooks.append("copy"))
    before = ledger.path.read_bytes()
    with pytest.raises(ValueError, match="identity"):
        if crossing.endswith("lease"):
            DomainLifecycleAdmission(
                environment_run=environment,
                environment_id="nao_fake",
                lifecycle_ledger=ledger,
            ).request_execution(admitted)
        elif crossing == "dispatch":
            owner_for(
                catalog, environment, ledger, lambda args: native.append(args)
            ).execute(lease)
        elif crossing == "receipt":
            result = OwnerExecutionResult("native:no-call", True, (FRESH_EFFECT,))
            evidence = EffectEvidence(
                "native:no-call",
                "find_object",
                admitted.binding_id,
                "nao_fake",
                "object_finder",
                True,
                (FRESH_EFFECT,),
            )
            ExecutionReceipt.issue(lease=lease, owner_result=result, evidence=evidence)
        elif crossing == "wire":
            ExecutionLease.to_dict(lease)
        else:
            ledger.require_current_admission(admitted)
    assert hooks == []
    assert native == []
    assert ledger.path.read_bytes() == before


@pytest.mark.parametrize("attack", ["missing", "mutated"])
def test_snapshot_fields_reject_even_with_instance_methods_overridden(tmp_path, attack):
    _, catalog, environment, ledger, admitted, lease = authority_fixture(tmp_path)
    if attack == "missing":
        object.__delattr__(admitted, "object_snapshot")
    else:
        object.__setattr__(
            admitted.object_snapshot,
            "observable_success",
            (FRESH_EFFECT, "direct_speech"),
        )
    for item in (admitted, lease):
        object.__setattr__(item, "verify_identity", lambda: None)
    before = ledger.path.read_bytes()
    calls = []
    with pytest.raises(ValueError, match="snapshot|identity"):
        owner_for(
            catalog, environment, ledger, lambda args: calls.append(args)
        ).execute(lease)
    assert calls == []
    assert ledger.path.read_bytes() == before


def test_original_wire_lease_receipt_and_restart_remain_exact(tmp_path):
    compiled, catalog, environment, ledger, admitted, lease = authority_fixture(
        tmp_path
    )
    original_wire = admitted.to_dict()
    clone = AdmittedOperation.from_dict(json.loads(json.dumps(original_wire)))
    assert clone.to_dict() == original_wire
    assert ExecutionLease.to_dict(lease)["admitted_operation"] == original_wire
    restarted = LifecycleLedger(ledger.path)
    reused = (
        DomainLifecycleAdmission(
            environment_run=environment,
            environment_id="nao_fake",
            lifecycle_ledger=restarted,
        )
        .request_execution(clone)
        .execution_lease
    )
    assert reused == lease
    calls = []

    def handler(arguments):
        calls.append(arguments)
        return OwnerExecutionResult("native:control", True, (FRESH_EFFECT,))

    receipt = (
        owner_for(catalog, environment, restarted, handler).execute(reused).receipt
    )
    assert receipt is not None and calls == [{"label": "cup"}]
    receipt.verify_identity()
    evidence = (receipt.evidence,)
    acceptance = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations, evidence
    )
    restarted.record(AcceptanceFact(compiled, evidence, acceptance))
    assert (
        LifecycleLedger(ledger.path).replay(compiled.trace_id).terminal_status
        == "accepted"
    )


def test_valid_concrete_fields_ignore_instance_methods_through_dispatch(tmp_path):
    _, catalog, environment, ledger, admitted, lease = authority_fixture(tmp_path)
    original = AdmittedOperation.to_dict(admitted)
    hooks = []

    def misreport():
        hooks.append("wire")
        return {"not": "the actual fields"}

    def no_verify():
        hooks.append("verify")

    for item in (admitted.proposal, admitted, lease):
        object.__setattr__(item, "to_dict", misreport)
        object.__setattr__(item, "verify_identity", no_verify)
    assert AdmittedOperation.to_dict(admitted) == original
    assert ExecutionLease.to_dict(lease)["admitted_operation"] == original
    reused = (
        DomainLifecycleAdmission(
            environment_run=environment,
            environment_id="nao_fake",
            lifecycle_ledger=ledger,
        )
        .request_execution(admitted)
        .execution_lease
    )
    calls = []

    def handler(arguments):
        calls.append(arguments)
        return OwnerExecutionResult("native:actual-fields", True, (FRESH_EFFECT,))

    assert (
        owner_for(catalog, environment, ledger, handler).execute(reused).receipt
        is not None
    )
    assert calls == [{"label": "cup"}]
    assert hooks == []
