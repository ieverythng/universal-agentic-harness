"""Independent paired probes; run with isolated src/tests on PYTHONPATH."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import hashlib
import importlib.util
from importlib.machinery import SourceFileLoader
import itertools
import json
from pathlib import Path
import sys

import pytest

from ab_harness import BindingCatalog, DomainLifecycleAdmission, LifecycleLedger
from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.contracts import EffectEvidence, OwnerExecutionResult
from ab_harness.domain_lifecycle import ExecutionLease
from ab_harness.environment import ExecutionReceipt
from ab_harness.lifecycle import AcceptanceFact, ExecutionStartedFact
from ab_harness.proposal_admission import AdmittedOperation
from ab_harness.runtime_controls import TaskBudgetAuthority
from test_admitted_object_snapshot import authority_fixture, owner_for


ROOT = Path("/home/juanbeck/universal-agentic-harness")
FIX = ROOT / "docs/artifacts/reviews/2026-10-08_uah_r4_fix_evidence"
OLD = (
    ROOT / "docs/artifacts/reviews/2026-10-08_uah_r4_admitted_object_snapshot_evidence"
)
EFFECT = "fresh detector-backed result returned"
MARKERS = ("admitted_operation", "object_snapshot", "schema_version")
SUBSETS = [s for n in range(1, 4) for s in itertools.combinations(MARKERS, n)]


def rewrite(path, rows, removed=(), foreign=False):
    remap = {}
    for row in rows:
        previous = row["event_id"]
        data = json.loads(row["data_json"])
        if row["event_type"] == "semantic_admission_accepted":
            for key in removed:
                data.pop(key, None)
            if foreign:
                data["frame_id"] = "foreign-frame"
        row["data_json"] = json.dumps(data, sort_keys=True, separators=(",", ":"))
        row["parent_event_id"] = remap.get(
            row["parent_event_id"], row["parent_event_id"]
        )
        body = {k: v for k, v in row.items() if k != "event_id"}
        row["event_id"] = (
            "trace-event:sha256:"
            + hashlib.sha256(
                json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
        )
        remap[previous] = row["event_id"]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))


def authority(environment, ledger):
    return DomainLifecycleAdmission(
        environment_run=environment, environment_id="nao_fake", lifecycle_ledger=ledger
    )


def receipt(lease):
    result = OwnerExecutionResult("native:second-review", True, (EFFECT,))
    evidence = EffectEvidence(
        "native:second-review",
        lease.object_id,
        lease.binding_id,
        "nao_fake",
        "object_finder",
        True,
        (EFFECT,),
    )
    return ExecutionReceipt.issue(lease=lease, owner_result=result, evidence=evidence)


@pytest.mark.parametrize("removed", SUBSETS, ids=lambda s: "+".join(s))
@pytest.mark.parametrize(
    "route",
    ["lease", "start", "raw_start", "owner", "complete", "raw_complete", "acceptance"],
)
def test_removed_marker_authority(tmp_path, removed, route):
    compiled, catalog, environment, ledger, admitted, lease = authority_fixture(
        tmp_path
    )
    created = receipt(lease)
    if route == "raw_start":
        grant = TaskBudgetAuthority(ledger).assess(
            trace_id=compiled.trace_id,
            resource="tool_call",
            subject_id=lease.operation_id,
        )
        ledger.record(grant.decision)
    if route in ("complete", "raw_complete", "acceptance"):
        ledger.start_execution(lease)
    if route == "acceptance":
        ledger.complete_execution(created)
    rewrite(ledger.path, [e.to_dict() for e in ledger.events()], removed)
    before = ledger.path.read_bytes()
    calls = []
    with pytest.raises((ValueError, TypeError)):
        active = LifecycleLedger(ledger.path)
        if route == "lease":
            authority(environment, active).request_execution(admitted)
        elif route == "start":
            active.start_execution(lease)
        elif route == "raw_start":
            active.record(ExecutionStartedFact(lease))
        elif route == "owner":
            owner_for(
                catalog,
                environment,
                active,
                lambda args: calls.append(args) or created.owner_result,
            ).execute(lease)
        elif route == "complete":
            active.complete_execution(created)
        elif route == "raw_complete":
            active.record(created)
        else:
            evidence = (created.evidence,)
            result = TaskAcceptanceEvaluator().evaluate(
                compiled.effect_obligations, evidence
            )
            active.record(AcceptanceFact(compiled, evidence, result))
    assert not calls
    assert ledger.path.read_bytes() == before


def load_old(name, file):
    spec = importlib.util.spec_from_file_location(
        name, OLD / file, loader=SourceFileLoader(name, str(OLD / file))
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def old_pair(environment):
    admission_module = load_old(
        "second_review_v2_admission", "proposal_admission.py.before"
    )
    lease_module = load_old("second_review_v2_lease", "domain_lifecycle.py.before")
    data = json.loads((FIX / "authentic_v2_admitted.fixture").read_text())
    data["proposal"] = admission_module.TypedProposal(**data["proposal"])
    data["effect_obligation_ids"] = tuple(data["effect_obligation_ids"])
    admitted = admission_module.AdmittedOperation(**data)
    admitted.verify_identity()
    row = json.loads((FIX / "authentic_v2_leased.fixture").read_text().splitlines()[-1])
    lease_data = json.loads(row["data_json"])
    lease = lease_module.ExecutionLease(
        execution_lease_id=lease_data["execution_lease_id"],
        admitted_operation=admitted,
        lease_owner_id=lease_data["lease_owner_id"],
        environment_attestation_id=environment.attestation.attestation_id,
    )
    lease.verify_identity()
    return admitted, lease


@pytest.mark.parametrize(
    "route", ["lease", "start", "raw_start", "owner", "receipt", "raw_lease"]
)
def test_authentic_v2_real_verifier_rejected(tmp_path, route):
    _, catalog, environment, _, _, _ = authority_fixture(tmp_path)
    admitted, lease = old_pair(environment)
    path = tmp_path / "old.jsonl"
    path.write_bytes((FIX / "authentic_v2_leased.fixture").read_bytes())
    active = LifecycleLedger(path)
    before = path.read_bytes()
    with pytest.raises((ValueError, TypeError)):
        if route == "lease":
            authority(environment, active).request_execution(admitted)
        elif route == "start":
            active.start_execution(lease)
        elif route == "raw_start":
            active.record(ExecutionStartedFact(lease))
        elif route == "owner":
            owner_for(
                catalog,
                environment,
                active,
                lambda _: OwnerExecutionResult("bad", True, (EFFECT,)),
            ).execute(lease)
        elif route == "receipt":
            receipt(lease)
        else:
            active.record(lease)
    assert path.read_bytes() == before


class NoOpVerifier:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, name):
        return getattr(self.wrapped, name)

    def verify_identity(self):
        return None


@pytest.mark.parametrize("route", ["lease", "receipt", "start", "raw_start", "owner"])
def test_foreign_noop_verifier_rejected(tmp_path, route):
    _, catalog, environment, ledger, admitted, lease = authority_fixture(tmp_path)
    if route == "lease":
        argument = NoOpVerifier(admitted)
    else:
        argument = object.__new__(ExecutionLease)
        argument.__dict__.update(lease.__dict__)
        object.__setattr__(argument, "admitted_operation", NoOpVerifier(admitted))
    before = ledger.path.read_bytes()
    with pytest.raises((ValueError, TypeError)):
        if route == "lease":
            authority(environment, ledger).request_execution(argument)
        elif route == "receipt":
            receipt(argument)
        elif route == "start":
            ledger.start_execution(argument)
        elif route == "raw_start":
            ledger.record(ExecutionStartedFact(argument))
        else:
            owner_for(
                catalog,
                environment,
                ledger,
                lambda _: OwnerExecutionResult("bad", True, (EFFECT,)),
            ).execute(argument)
    assert ledger.path.read_bytes() == before


@pytest.mark.parametrize("missing", ["admission_and_lease", "lease", "foreign_frame"])
@pytest.mark.parametrize("route", ["start", "owner", "complete"])
def test_current_artifact_is_not_recorded_authority(tmp_path, missing, route):
    _, catalog, environment, ledger, _, lease = authority_fixture(tmp_path)
    created = receipt(lease)  # Pure construction is permitted, not durable authority.
    rows = [e.to_dict() for e in ledger.events()]
    if missing == "admission_and_lease":
        rows = rows[:3]
    elif missing == "lease":
        rows = rows[:4]
    rewrite(
        ledger.path,
        rows,
        MARKERS if missing == "foreign_frame" else (),
        missing == "foreign_frame",
    )
    active = LifecycleLedger(ledger.path)
    before = ledger.path.read_bytes()
    calls = []
    with pytest.raises((ValueError, TypeError)):
        if route == "start":
            active.start_execution(lease)
        elif route == "complete":
            active.complete_execution(created)
        else:
            owner_for(
                catalog,
                environment,
                active,
                lambda args: calls.append(args) or created.owner_result,
            ).execute(lease)
    assert not calls
    assert ledger.path.read_bytes() == before


def test_current_full_wire_restart_and_competing_writer_control(tmp_path):
    compiled, catalog, environment, ledger, admitted, lease = authority_fixture(
        tmp_path
    )
    restored = AdmittedOperation.from_dict(json.loads(json.dumps(admitted.to_dict())))
    restarted = LifecycleLedger(ledger.path)
    assert (
        authority(environment, restarted).request_execution(restored).execution_lease
        == lease
    )
    calls = []

    def attempt(_):
        try:
            return (
                owner_for(
                    catalog,
                    environment,
                    LifecycleLedger(ledger.path),
                    lambda args: (
                        calls.append(args)
                        or OwnerExecutionResult("native:race", True, (EFFECT,))
                    ),
                )
                .execute(lease)
                .receipt
            )
        except (ValueError, RuntimeError):
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, range(2)))
    assert len(calls) == 1
    done = next(x for x in results if x is not None)
    evidence = (done.evidence,)
    result = TaskAcceptanceEvaluator().evaluate(compiled.effect_obligations, evidence)
    restarted.record(AcceptanceFact(compiled, evidence, result))
    replay = LifecycleLedger(ledger.path).replay(compiled.trace_id)
    assert replay.terminal_status == "accepted"
    assert replay.verified_trace_digest is not None


def test_binding_revision_control(tmp_path):
    _, catalog, environment, ledger, _, lease = authority_fixture(tmp_path)
    original = catalog.bindings_for("find_object")[0]
    revised = replace(original, source_revision="independent-revision")
    from ab_harness.registry import RegistrySnapshot

    changed = BindingCatalog(
        RegistrySnapshot(
            (catalog.object_for("find_object"),), source="control", version="control"
        ),
        (revised,),
    )
    before = ledger.path.read_bytes()
    calls = []
    with pytest.raises(ValueError):
        owner_for(
            changed, environment, ledger, lambda args: calls.append(args)
        ).execute(lease)
    assert not calls
    assert ledger.path.read_bytes() == before


def test_genuine_v2_completed_history_readonly(tmp_path):
    path = tmp_path / "completed-v2.jsonl"
    path.write_bytes((OLD / "legacy_v2_control.fixture").read_bytes())
    before = path.read_bytes()
    ledger = LifecycleLedger(path)
    semantic = next(
        e for e in ledger.events() if e.event_type == "semantic_admission_accepted"
    )
    assert all(marker not in semantic.data for marker in MARKERS)
    replay = ledger.replay(semantic.trace_id)
    assert replay.terminal_status == "accepted"
    assert (
        replay.verified_trace_digest.digest_id
        == "verified-trace-digest:sha256:f9f65439cc22226974386beb322d01cf5290632f3b9cfde23d30284001d72441"
    )
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "field",
    [
        "admission_id",
        "execution_lease_id",
        "environment_run_id",
        "task_id",
        "trace_id",
        "operation_id",
        "object_id",
        "owner",
    ],
)
def test_current_self_consistent_receipt_foreign_lineage_rejected(tmp_path, field):
    _, _, _, ledger, _, lease = authority_fixture(tmp_path)
    ledger.start_execution(lease)
    good = receipt(lease)
    payload = good.to_dict()
    if field in ("object_id", "owner"):
        payload["evidence"][field] = "foreign:" + field
    else:
        payload[field] = "foreign:" + field
    body = {k: v for k, v in payload.items() if k != "execution_result_id"}
    payload["execution_result_id"] = (
        "execution-receipt:sha256:"
        + hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )
    altered = ExecutionReceipt.from_dict(payload)
    altered.verify_identity()
    before = ledger.path.read_bytes()
    with pytest.raises((ValueError, TypeError)):
        ledger.complete_execution(altered)
    assert ledger.path.read_bytes() == before
