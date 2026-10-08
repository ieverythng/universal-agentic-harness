"""Current active authority cannot come from historical admission metadata."""

import importlib.util
from importlib.machinery import SourceFileLoader
import hashlib
import json
from pathlib import Path
import sys

import pytest

from ab_harness import DomainLifecycleAdmission, LifecycleLedger
from ab_harness.contracts import EffectEvidence, OwnerExecutionResult
from ab_harness.environment import ExecutionReceipt
from ab_harness.lifecycle import AcceptanceFact, ExecutionStartedFact
from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.proposal_admission import AdmittedOperation
from test_admitted_object_snapshot import FRESH_EFFECT, authority_fixture, owner_for
from test_two_stage_admission import _admission_fixture


ROOT = Path(__file__).resolve().parents[1]
OLD_EVIDENCE = (
    ROOT / "docs/artifacts/reviews/2026-10-08_uah_r4_admitted_object_snapshot_evidence"
)
FIX_EVIDENCE = ROOT / "docs/artifacts/reviews/2026-10-08_uah_r4_fix_evidence"


def old_module(name, filename):
    spec = importlib.util.spec_from_file_location(
        name,
        OLD_EVIDENCE / filename,
        loader=SourceFileLoader(name, str(OLD_EVIDENCE / filename)),
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authentic_old_admitted():
    module = old_module(
        "retained_v2_proposal_admission", "proposal_admission.py.before"
    )
    values = json.loads((FIX_EVIDENCE / "authentic_v2_admitted.fixture").read_text())
    values["proposal"] = module.TypedProposal(**values["proposal"])
    values["effect_obligation_ids"] = tuple(values["effect_obligation_ids"])
    return module.AdmittedOperation(**values)


def authentic_old_lease():
    module = old_module("retained_v2_domain_lifecycle", "domain_lifecycle.py.before")
    event = json.loads(
        (FIX_EVIDENCE / "authentic_v2_leased.fixture").read_text().splitlines()[-1]
    )
    data = json.loads(event["data_json"])
    _, _, environment = _admission_fixture()
    return module.ExecutionLease(
        execution_lease_id=data["execution_lease_id"],
        admitted_operation=authentic_old_admitted(),
        lease_owner_id=data["lease_owner_id"],
        environment_attestation_id=environment.attestation.attestation_id,
    )


def test_authentic_old_concrete_admission_cannot_obtain_current_lease(tmp_path):
    _, _, environment, _, _, _ = authority_fixture(tmp_path)
    rows = (FIX_EVIDENCE / "authentic_v2_leased.fixture").read_text().splitlines()
    path = tmp_path / "historical.jsonl"
    path.write_text("\n".join(rows[:-1]) + "\n")
    ledger = LifecycleLedger(path)
    before = len(ledger.events())
    admitted = authentic_old_admitted()
    assert admitted.schema_version == "uah.admitted_operation/v2"
    admitted.verify_identity()
    with pytest.raises(ValueError, match="current|supported|artifact"):
        DomainLifecycleAdmission(
            environment_run=environment,
            environment_id="nao_fake",
            lifecycle_ledger=ledger,
        ).request_execution(admitted)
    assert len(ledger.events()) == before


def test_authentic_old_lease_cannot_issue_current_effect_receipt():
    lease = authentic_old_lease()
    lease.verify_identity()
    result = OwnerExecutionResult("native:old", True, (FRESH_EFFECT,))
    evidence = EffectEvidence(
        "native:old",
        "find_object",
        lease.binding_id,
        "nao_fake",
        "object_finder",
        True,
        (FRESH_EFFECT,),
    )
    with pytest.raises(ValueError, match="current|supported|artifact"):
        ExecutionReceipt.issue(lease=lease, owner_result=result, evidence=evidence)


def strip_current_markers(ledger, *, wrong_frame=False):
    rows, ids = [], {}
    for event in ledger.events():
        row = event.to_dict()
        previous = row["event_id"]
        if event.event_type == "semantic_admission_accepted":
            data = event.data
            for key in ("admitted_operation", "object_snapshot", "schema_version"):
                data.pop(key)
            if wrong_frame:
                data["frame_id"] = "foreign_frame"
            row["data_json"] = json.dumps(data, sort_keys=True, separators=(",", ":"))
        row["parent_event_id"] = ids.get(row["parent_event_id"], row["parent_event_id"])
        payload = {key: value for key, value in row.items() if key != "event_id"}
        row["event_id"] = (
            "trace-event:sha256:"
            + hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
        )
        ids[previous] = row["event_id"]
        rows.append(json.dumps(row))
    ledger.path.write_text("\n".join(rows) + "\n")


@pytest.mark.parametrize("wrong_frame", [False, True])
def test_stripped_current_body_cannot_reuse_recorded_lease(tmp_path, wrong_frame):
    _, _, environment, ledger, admitted, _ = authority_fixture(tmp_path)
    strip_current_markers(ledger, wrong_frame=wrong_frame)
    historical = LifecycleLedger(ledger.path)
    assert len(historical.events()) == 5
    before = historical.path.read_bytes()
    with pytest.raises(ValueError, match="current|semantic|provenance"):
        DomainLifecycleAdmission(
            environment_run=environment,
            environment_id="nao_fake",
            lifecycle_ledger=historical,
        ).request_execution(admitted)
    assert historical.path.read_bytes() == before


def test_stripped_current_body_cannot_authorize_new_execution_fact(tmp_path):
    _, _, _, ledger, _, lease = authority_fixture(tmp_path)
    strip_current_markers(ledger)
    historical = LifecycleLedger(ledger.path)
    before = historical.path.read_bytes()
    with pytest.raises(ValueError, match="current|semantic|provenance"):
        historical.start_execution(lease)
    assert historical.path.read_bytes() == before


@pytest.mark.parametrize(
    "crossing", ["dispatch", "raw_start", "complete", "acceptance"]
)
def test_historical_shaped_body_cannot_authorize_current_continuation(
    tmp_path, crossing
):
    compiled, catalog, environment, ledger, _, lease = authority_fixture(tmp_path)
    result = OwnerExecutionResult("native:valid", True, (FRESH_EFFECT,))
    native_calls = []
    receipt = None
    if crossing in {"complete", "acceptance"}:
        receipt = (
            owner_for(catalog, environment, ledger, lambda _: result)
            .execute(lease)
            .receipt
        )
        assert receipt is not None
        if crossing == "complete":
            ledger.path.write_text(
                "\n".join(ledger.path.read_text().splitlines()[:-2]) + "\n"
            )
    strip_current_markers(ledger)
    historical = LifecycleLedger(ledger.path)
    before = historical.path.read_bytes()
    with pytest.raises(ValueError, match="current|semantic|provenance"):
        if crossing == "dispatch":

            def handler(arguments):
                native_calls.append(arguments)
                return result

            owner_for(catalog, environment, historical, handler).execute(lease)
        elif crossing == "raw_start":
            historical.record(ExecutionStartedFact(lease))
        elif crossing == "complete":
            historical.complete_execution(receipt)
        else:
            evidence = (receipt.evidence,)
            acceptance = TaskAcceptanceEvaluator().evaluate(
                compiled.effect_obligations, evidence
            )
            historical.record(AcceptanceFact(compiled, evidence, acceptance))
    assert native_calls == []
    assert historical.path.read_bytes() == before


@pytest.mark.parametrize("crossing", ["lease", "dispatch", "receipt", "ledger_start"])
def test_foreign_or_old_verifiers_do_not_supply_current_authority(tmp_path, crossing):
    _, catalog, environment, ledger, _, _ = authority_fixture(tmp_path)
    old = authentic_old_lease()
    old.verify_identity()
    before = ledger.path.read_bytes()
    result = OwnerExecutionResult("native:foreign", True, (FRESH_EFFECT,))
    evidence = EffectEvidence(
        "native:foreign",
        "find_object",
        old.binding_id,
        "nao_fake",
        "object_finder",
        True,
        (FRESH_EFFECT,),
    )
    calls = []
    with pytest.raises((ValueError, TypeError)):
        if crossing == "lease":
            DomainLifecycleAdmission(
                environment_run=environment,
                environment_id="nao_fake",
                lifecycle_ledger=ledger,
            ).request_execution(old.admitted_operation)
        elif crossing == "dispatch":
            owner_for(
                catalog, environment, ledger, lambda args: calls.append(args)
            ).execute(old)
        elif crossing == "receipt":
            ExecutionReceipt.issue(lease=old, owner_result=result, evidence=evidence)
        else:
            ledger.start_execution(old)
    assert calls == []
    assert ledger.path.read_bytes() == before


def test_foreign_verifier_and_subclass_cannot_supply_current_admission(tmp_path):
    _, _, environment, ledger, admitted, _ = authority_fixture(tmp_path)

    class Foreign:
        def verify_identity(self):
            return None

    class Alternate(AdmittedOperation):
        def verify_identity(self):
            return None

    alternate = object.__new__(Alternate)
    alternate.__dict__.update(admitted.__dict__)
    for foreign in (Foreign(), alternate):
        with pytest.raises(ValueError, match="current|supported"):
            DomainLifecycleAdmission(
                environment_run=environment,
                environment_id="nao_fake",
                lifecycle_ledger=ledger,
            ).request_execution(foreign)


def test_current_serialized_admission_and_restart_keep_active_success(tmp_path):
    compiled, catalog, environment, ledger, admitted, lease = authority_fixture(
        tmp_path
    )
    restored = AdmittedOperation.from_dict(json.loads(json.dumps(admitted.to_dict())))
    restarted = LifecycleLedger(ledger.path)
    decision = DomainLifecycleAdmission(
        environment_run=environment,
        environment_id="nao_fake",
        lifecycle_ledger=restarted,
    ).request_execution(restored)
    assert decision.execution_lease == lease
    calls = []

    def handler(arguments):
        calls.append(arguments)
        return OwnerExecutionResult("native:current", True, (FRESH_EFFECT,))

    receipt = owner_for(catalog, environment, restarted, handler).execute(lease).receipt
    assert receipt is not None and len(calls) == 1
    evidence = (receipt.evidence,)
    acceptance = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations, evidence
    )
    restarted.record(AcceptanceFact(compiled, evidence, acceptance))
    replay = LifecycleLedger(ledger.path).replay(compiled.trace_id)
    assert replay.terminal_status == "accepted"
    assert replay.verified_trace_digest is not None


def test_genuine_old_completed_history_remains_readable_without_snapshot(tmp_path):
    path = tmp_path / "legacy.jsonl"
    path.write_bytes((OLD_EVIDENCE / "legacy_v2_control.fixture").read_bytes())
    historical = LifecycleLedger(path)
    event = next(
        event
        for event in historical.events()
        if event.event_type == "semantic_admission_accepted"
    )
    assert "admitted_operation" not in event.data
    replay = historical.replay(event.trace_id)
    assert replay.terminal_status == "accepted"
    assert (
        replay.verified_trace_digest.digest_id
        == "verified-trace-digest:sha256:f9f65439cc22226974386beb322d01cf5290632f3b9cfde23d30284001d72441"
    )
