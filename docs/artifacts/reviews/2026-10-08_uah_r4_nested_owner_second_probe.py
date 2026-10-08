"""Independent public probes; run against either isolated source tree."""

from dataclasses import fields
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path.cwd() / "tests"))

from test_admitted_object_snapshot import FRESH_EFFECT, authority_fixture, owner_for
from ab_harness import DomainLifecycleAdmission, LifecycleLedger
from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.contracts import EffectEvidence, OwnerExecutionResult
from ab_harness.domain_lifecycle import ExecutionLease
from ab_harness.environment import EvidenceRejection, ExecutionReceipt
from ab_harness.lifecycle import AcceptanceFact
from ab_harness.proposal_admission import AdmittedOperation, TypedProposal


results = []


def run(name, action):
    with tempfile.TemporaryDirectory(prefix="uah-independent-probe-") as folder:
        try:
            detail = action(Path(folder))
            results.append({"name": name, "status": "pass", "detail": detail})
        except Exception as exc:
            results.append({"name": name, "status": "fail", "error": str(exc), "type": type(exc).__name__})


def result_and_evidence(admitted):
    result = OwnerExecutionResult("native:independent", True, (FRESH_EFFECT,))
    evidence = EffectEvidence(
        result.evidence_ref, "find_object", admitted.binding_id, "nao_fake",
        "object_finder", True, (FRESH_EFFECT,),
    )
    return result, evidence


def truncate(ledger, count):
    rows = ledger.path.read_text().splitlines()
    ledger.path.write_text("\n".join(rows[:count]) + "\n")
    return LifecycleLedger(ledger.path)


def wrong(value):
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, tuple):
        return (*value, "unexpected")
    return value + ":changed"


def attack(tmp, layer, field, crossing, hooks, rehash=False):
    _, catalog, environment, ledger, admitted, lease = authority_fixture(tmp)
    if crossing == "fresh_lease":
        ledger = truncate(ledger, 4)
    if crossing == "record_proposal":
        ledger = truncate(ledger, 2)
    if crossing == "record_admitted":
        ledger = truncate(ledger, 3)
    if crossing == "record_lease":
        ledger = truncate(ledger, 4)
    layers = {"proposal": admitted.proposal, "snapshot": admitted.object_snapshot,
              "admitted": admitted, "lease": lease}
    wires = {"proposal": admitted.proposal.to_dict(), "admitted": admitted.to_dict(),
             "lease": lease.to_dict()}
    calls = []
    target = layers[layer]
    if field == "missing":
        object.__delattr__(admitted, "object_snapshot")
    elif field == "empty_obligations":
        object.__setattr__(admitted, "effect_obligation_ids", ())
    elif field == "two_fields":
        object.__setattr__(admitted.proposal, "arguments_json", '{"label":"mug"}')
        object.__setattr__(admitted.object_snapshot, "observable_success", (FRESH_EFFECT, "direct_speech"))
    else:
        changed = '{"label":"mug"}' if rehash and field == "arguments_json" else wrong(getattr(target, field))
        object.__setattr__(target, field, changed)
    if rehash:
        values = {f.name: getattr(target, f.name) for f in fields(target)}
        payload = {key: value for key, value in values.items() if key != "proposal_id"}
        values["proposal_id"] = "proposal:sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        proposal = TypedProposal(**values)
        object.__setattr__(admitted, "proposal", proposal)
        layers["proposal"] = proposal
    if hooks:
        for name in ("proposal", "admitted", "lease"):
            item = layers[name]
            wire = wires[name]
            object.__setattr__(item, "to_dict", lambda wire=wire: dict(wire))
            object.__setattr__(item, "verify_identity", lambda: calls.append("verifier"))
            object.__setattr__(item, "verified_copy", lambda: calls.append("copy"))
    original = ledger.path.read_bytes()
    native = []
    try:
        if crossing in {"fresh_lease", "reuse_lease"}:
            DomainLifecycleAdmission(environment_run=environment, environment_id="nao_fake", lifecycle_ledger=ledger).request_execution(admitted)
        elif crossing == "provenance":
            ledger.require_current_admission(admitted)
        elif crossing == "dispatch":
            owner_for(catalog, environment, ledger, lambda args: native.append(args)).execute(lease)
        elif crossing == "receipt":
            result, evidence = result_and_evidence(admitted)
            ExecutionReceipt.issue(lease=lease, owner_result=result, evidence=evidence)
        elif crossing == "rejection":
            result, _ = result_and_evidence(admitted)
            EvidenceRejection.issue(lease=lease, owner_result=result, reason_codes=("undeclared_observed_effect",))
        elif crossing == "wire":
            ExecutionLease.to_dict(lease)
        elif crossing == "record_proposal":
            ledger.record(admitted.proposal)
        elif crossing == "record_admitted":
            ledger.record(admitted)
        elif crossing == "record_lease":
            ledger.record(lease)
    except (ValueError, TypeError, AttributeError) as exc:
        assert not native, native
        assert not calls, calls
        assert ledger.path.read_bytes() == original
        return {"rejected": type(exc).__name__, "message": str(exc)}
    raise AssertionError("altered authority accepted")


with tempfile.TemporaryDirectory() as folder:
    _, _, _, _, sample, lease_sample = authority_fixture(Path(folder))
    chosen = {
        "proposal": [f.name for f in fields(sample.proposal)],
        "snapshot": [f.name for f in fields(sample.object_snapshot)],
        "admitted": [f.name for f in fields(sample) if f.name not in {"proposal", "object_snapshot"}],
        "lease": [f.name for f in fields(lease_sample) if f.name != "admitted_operation"],
    }

for layer, names in chosen.items():
    crossings = ["dispatch", "receipt", "rejection", "wire", "record_lease"]
    if layer != "lease":
        crossings += ["fresh_lease", "reuse_lease", "provenance", "record_admitted"]
    if layer == "proposal":
        crossings += ["record_proposal"]
    for field in names:
        for crossing in crossings:
            for hooks in (False, True):
                run(f"tamper:{layer}:{field}:{crossing}:hooks={hooks}",
                    lambda tmp, layer=layer, field=field, crossing=crossing, hooks=hooks:
                    attack(tmp, layer, field, crossing, hooks))
for field in ("missing", "empty_obligations", "two_fields"):
    for crossing in ("fresh_lease", "provenance", "dispatch", "receipt", "rejection", "wire"):
        run(f"combined:{field}:{crossing}", lambda tmp, field=field, crossing=crossing:
            attack(tmp, "admitted", field, crossing, True))

for field in ("arguments_json", "raw_output_artifact_id", "output_type", "task_id", "object_id", "operation_id"):
    for crossing in ("fresh_lease", "reuse_lease", "provenance", "dispatch", "receipt", "rejection", "wire", "record_admitted", "record_lease"):
        run(f"valid_nested_rehash:{field}:{crossing}", lambda tmp, field=field, crossing=crossing:
            attack(tmp, "proposal", field, crossing, True, rehash=True))


def coherent(tmp, mutation, bad_effect):
    compiled, catalog, environment, ledger, admitted, lease = authority_fixture(tmp)
    original = admitted.to_dict()
    clone = AdmittedOperation.from_dict(json.loads(json.dumps(original)))
    assert clone.to_dict() == original
    restarted = LifecycleLedger(ledger.path)
    reused = DomainLifecycleAdmission(environment_run=environment, environment_id="nao_fake", lifecycle_ledger=restarted).request_execution(clone).execution_lease
    assert ExecutionLease.to_dict(reused) == ExecutionLease.to_dict(lease)
    calls = []

    def handler(arguments):
        calls.append(dict(arguments))
        if mutation == "proposal":
            object.__setattr__(clone.proposal, "arguments_json", '{"label":"mug"}')
        elif mutation == "snapshot":
            object.__setattr__(clone.object_snapshot, "observable_success", (FRESH_EFFECT, "direct_speech"))
        elif mutation == "admitted":
            object.__setattr__(clone, "binding_owner", "other_owner")
            object.__setattr__(clone, "effect_obligation_ids", ())
        elif mutation == "lease":
            object.__setattr__(reused, "lease_owner_id", "other_owner")
        arguments["label"] = "local handler mutation"
        effects = (FRESH_EFFECT, "direct_speech") if bad_effect else (FRESH_EFFECT,)
        return OwnerExecutionResult("native:coherent", True, effects)

    decision = owner_for(catalog, environment, restarted, handler).execute(reused)
    assert calls == [{"label": "cup"}]
    if bad_effect:
        assert decision.receipt is None
        assert decision.rejection.reason_codes == ("undeclared_observed_effect",)
        assert decision.rejection.lease.admitted_operation.to_dict() == original
        assert LifecycleLedger(ledger.path).replay(compiled.trace_id).failure_stage == "evidence"
        return "coherent rejection with frozen lease"
    receipt = decision.receipt
    receipt.verify_identity()
    assert receipt.admission_id == original["admission_id"]
    assert receipt.evidence.owner == original["binding_owner"]
    evidence = (receipt.evidence,)
    accepted = TaskAcceptanceEvaluator().evaluate(compiled.effect_obligations, evidence)
    restarted.record(AcceptanceFact(compiled, evidence, accepted))
    assert LifecycleLedger(ledger.path).replay(compiled.trace_id).terminal_status == "accepted"
    return "coherent accepted receipt and restart"


for mutation in ("none", "proposal", "snapshot", "admitted", "lease"):
    for bad in (False, True):
        run(f"handler:{mutation}:bad_effect={bad}", lambda tmp, mutation=mutation, bad=bad: coherent(tmp, mutation, bad))


def historical(tmp, crossing):
    from test_admission_active_provenance import authentic_old_admitted, authentic_old_lease

    _, catalog, environment, ledger, admitted, lease = authority_fixture(tmp)
    calls = []
    if crossing.startswith("old"):
        old_admitted = authentic_old_admitted()
        old_lease = authentic_old_lease()
        old_admitted.verify_identity()
        old_lease.verify_identity()
    else:
        rewritten = []
        changed_ids = {}
        for event in ledger.events():
            wire = event.to_dict()
            previous = wire.pop("event_id")
            body = json.loads(wire["data_json"])
            if event.event_type == "semantic_admission_accepted":
                for marker in ("admitted_operation", "object_snapshot", "schema_version"):
                    body.pop(marker)
            wire["data_json"] = json.dumps(body, sort_keys=True, separators=(",", ":"))
            wire["parent_event_id"] = changed_ids.get(wire["parent_event_id"], wire["parent_event_id"])
            event_id = "trace-event:sha256:" + hashlib.sha256(json.dumps(wire, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            changed_ids[previous] = event_id
            rewritten.append(json.dumps({"event_id": event_id, **wire}))
        ledger.path.write_text("\n".join(rewritten) + "\n")
        ledger = LifecycleLedger(ledger.path)
        assert len(ledger.events()) == 5
    original = ledger.path.read_bytes()
    try:
        if crossing == "old_lease":
            DomainLifecycleAdmission(environment_run=environment, environment_id="nao_fake", lifecycle_ledger=ledger).request_execution(old_admitted)
        elif crossing == "old_receipt":
            result, evidence = result_and_evidence(admitted)
            ExecutionReceipt.issue(lease=old_lease, owner_result=result, evidence=evidence)
        elif crossing == "old_dispatch":
            owner_for(catalog, environment, ledger, lambda args: calls.append(args)).execute(old_lease)
        elif crossing == "marker_lease":
            DomainLifecycleAdmission(environment_run=environment, environment_id="nao_fake", lifecycle_ledger=ledger).request_execution(admitted)
        elif crossing == "marker_dispatch":
            owner_for(catalog, environment, ledger, lambda args: calls.append(args)).execute(lease)
        elif crossing == "marker_start":
            ledger.start_execution(lease)
        else:
            ledger.require_current_admission(admitted)
    except (ValueError, TypeError) as exc:
        assert calls == []
        assert ledger.path.read_bytes() == original
        return {"rejected": type(exc).__name__, "message": str(exc)}
    raise AssertionError("historical authority accepted")


for crossing in ("old_lease", "old_receipt", "old_dispatch", "marker_lease", "marker_dispatch", "marker_start", "marker_provenance"):
    run(crossing, lambda tmp, crossing=crossing: historical(tmp, crossing))

summary = {"total": len(results), "passed": sum(row["status"] == "pass" for row in results),
           "failed": sum(row["status"] == "fail" for row in results),
           "failures": [row for row in results if row["status"] != "pass"],
           "matrix": chosen,
           "rejection_messages": dict(Counter(row["detail"]["message"] for row in results if row["status"] == "pass" and isinstance(row.get("detail"), dict)))}
print(json.dumps(summary, sort_keys=True))
