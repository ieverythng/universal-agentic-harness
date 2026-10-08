"""Independent adversarial R4 public-boundary probes on isolated copies."""
from pathlib import Path
from tempfile import TemporaryDirectory
from dataclasses import replace
import hashlib
import json
import sys

from ab_harness import BindingCatalog, RegistrySnapshot, DomainLifecycleAdmission
from ab_harness.lifecycle import LifecycleLedger, AcceptanceFact
from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.proposal_admission import AdmittedOperation
from ab_harness.contracts import OwnerExecutionResult
from test_admitted_object_snapshot import authority_fixture, owner_for
from test_two_stage_admission import _proposal, _semantic_admission, _admission_fixture

EFFECT = "fresh detector-backed result returned"

def identity(prefix, data, exclude):
    return prefix + ":sha256:" + hashlib.sha256(json.dumps(
        {key: value for key, value in data.items() if key != exclude},
        sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()

def output(case, **data):
    print(json.dumps({"case": case, **data}, sort_keys=True))

def rewrite(ledger, mutate):
    rows = []
    ids = {}
    for event in ledger.events():
        row = event.to_dict()
        original_id = row["event_id"]
        if row["event_type"] == "semantic_admission_accepted":
            data = event.data
            mutate(data)
            row["data_json"] = json.dumps(data, sort_keys=True, separators=(",", ":"))
        if row["parent_event_id"] in ids:
            row["parent_event_id"] = ids[row["parent_event_id"]]
        row["event_id"] = identity("trace-event", row, "event_id")
        ids[original_id] = row["event_id"]
        rows.append(row)
    # Synthetic adversarial JSONL input only; runtime sources are untouched.
    ledger.path.write_text("".join(json.dumps(row) + "\n" for row in rows))

def control(kind):
    with TemporaryDirectory() as directory:
        compiled, catalog, environment, ledger, admitted, lease = authority_fixture(Path(directory))
        calls = []
        original = catalog.object_for("find_object")
        if kind == "pre_drift":
            changed = replace(original, observable_success=(EFFECT, "direct_speech"))
            catalog = BindingCatalog(RegistrySnapshot((changed,), source="review:drift", version="r4"), catalog.bindings_for("find_object"))
        def handler(arguments):
            calls.append(arguments)
            if kind == "mid_drift":
                object.__setattr__(original, "observable_success", (EFFECT, "direct_speech"))
            return OwnerExecutionResult("native:review", True, (EFFECT, "direct_speech") if kind != "valid" else (EFFECT,))
        try:
            decision = owner_for(catalog, environment, ledger, handler).execute(lease)
            output(kind, native_calls=len(calls), receipt=decision.receipt is not None,
                reasons=[] if decision.rejection is None else decision.rejection.reason_codes,
                replay_failure=LifecycleLedger(ledger.path).replay(compiled.trace_id).failure_stage)
        except Exception as exc:
            output(kind, native_calls=len(calls), error=str(exc))

def replay_case(kind):
    with TemporaryDirectory() as directory:
        compiled, catalog, environment, ledger, admitted, lease = authority_fixture(Path(directory))
        if kind == "export_history":
            Path("/tmp/uah_r4_second_history.jsonl").write_text(ledger.path.read_text())
            output(kind, schema=admitted.schema_version)
            return
        def mutate(data):
            if kind.startswith("strip_all"):
                for key in ("admitted_operation", "object_snapshot", "schema_version"):
                    data.pop(key, None)
                if kind == "strip_all_wrong_frame":
                    data["frame_id"] = "foreign_frame"
            elif kind.startswith("missing_"):
                data.pop(kind.removeprefix("missing_"), None)
            elif kind.startswith("alias_"):
                key = kind.removeprefix("alias_")
                data[key] = "foreign" if key != "ab_level" else True
            elif kind == "nested_rehash_stale_outer":
                proposal = data["admitted_operation"]["proposal"]
                proposal["arguments_json"] = '{"label":"knife"}'
                proposal["proposal_id"] = identity("proposal", proposal, "proposal_id")
            elif kind == "snapshot_empty":
                data["admitted_operation"]["object_snapshot"] = {}
            elif kind == "active_v2":
                data["admitted_operation"]["schema_version"] = "uah.admitted_operation/v2"
        try:
            rewrite(ledger, mutate)
            restarted = LifecycleLedger(ledger.path)
            replay = restarted.replay(compiled.trace_id)
            event = next(e for e in restarted.events() if e.event_type == "semantic_admission_accepted")
            outcome = {"loaded": True, "snapshot_present": "object_snapshot" in event.data, "frame": event.data["frame_id"]}
            if kind.startswith("strip_all"):
                rerequested = DomainLifecycleAdmission(environment_run=environment, environment_id="nao_fake", lifecycle_ledger=restarted).request_execution(admitted).execution_lease
                calls = []
                def handler(arguments):
                    calls.append(arguments)
                    return OwnerExecutionResult("native:review", True, (EFFECT,))
                owner = owner_for(catalog, environment, restarted, handler)
                decision = owner.execute(rerequested)
                outcome["native_calls"] = len(calls)
                outcome["admission_id_unchanged"] = event.data["admission_id"] == admitted.admission_id
                outcome["lease_id_unchanged"] = rerequested.execution_lease_id == lease.execution_lease_id
                outcome["active_dispatch_receipt"] = decision.receipt is not None
                evidence = (decision.receipt.evidence,)
                acceptance = TaskAcceptanceEvaluator().evaluate(compiled.effect_obligations, evidence)
                restarted.record(AcceptanceFact(compiled, evidence, acceptance))
                final = LifecycleLedger(ledger.path).replay(compiled.trace_id)
                outcome["replay_failure"] = final.failure_stage
                outcome["terminal_status"] = final.terminal_status
            output(kind, **outcome)
        except Exception as exc:
            output(kind, loaded=False, error=str(exc), type=type(exc).__name__)

def active_wire():
    with TemporaryDirectory() as directory:
        _, _, _, _, admitted, _ = authority_fixture(Path(directory))
        for case in ("object_snapshot", "schema_version"):
            wire = admitted.to_dict()
            del wire[case]
            try:
                AdmittedOperation.from_dict(wire)
                output("active_missing_" + case, accepted=True)
            except Exception as exc:
                output("active_missing_" + case, accepted=False, error=str(exc))

def revised_binding():
    compiled, catalog, environment = _admission_fixture()
    old_binding = catalog.bindings_for("find_object")[0]
    binding = replace(old_binding, binding_id="review.find_object.v2", source_revision="review-rev-2", locator="review.find_object:v2")
    revised = BindingCatalog(RegistrySnapshot((catalog.object_for("find_object"),), source="review:compatible", version="review-v2"), (binding,))
    decision = _semantic_admission(revised).admit(compiled, _proposal(compiled))
    output("revised_binding", accepted=decision.accepted, reasons=decision.reason_codes)

if sys.argv[1] == "base":
    for case in ("valid", "pre_drift", "mid_drift"):
        control(case)
    revised_binding()
    replay_case("export_history")
    replay_case("strip_all_wrong_frame")
else:
    for case in ("valid", "pre_drift", "mid_drift"):
        control(case)
    revised_binding()
    active_wire()
    for case in ("missing_admitted_operation", "missing_object_snapshot", "missing_schema_version", "snapshot_empty", "active_v2", "nested_rehash_stale_outer", "alias_frame_id", "alias_object_id", "alias_input_schema_id", "alias_ab_level", "strip_all", "strip_all_wrong_frame"):
        replay_case(case)
    historical = LifecycleLedger("/tmp/uah_r4_second_history.jsonl")
    output("genuine_historical_read", events=len(historical.events()), snapshot_present=any("object_snapshot" in e.data for e in historical.events()))
