"""Public authority regressions for admitted object semantics."""

from dataclasses import replace
import hashlib
import json

import pytest

from ab_harness import BindingCatalog, DomainLifecycleAdmission
from ab_harness import EnvironmentIngress, LifecycleLedger
from ab_harness import RegistrySnapshot, TaskIngressAuthority
from ab_harness.contracts import OwnerExecutionResult
from ab_harness.environment import InProcessEnvironmentOwner
from ab_harness.environment import ExecutionReceipt
from ab_harness.contracts import EffectEvidence
from ab_harness.proposal_admission import AdmittedOperation
from test_two_stage_admission import _admission_fixture
from test_two_stage_admission import _domain_pack_for_compiled
from test_two_stage_admission import _proposal
from test_two_stage_admission import _semantic_admission


FRESH_EFFECT = "fresh detector-backed result returned"


def authority_fixture(tmp_path):
    compiled, catalog, environment = _admission_fixture()
    ledger = LifecycleLedger(tmp_path / "lifecycle.jsonl")
    ingress = TaskIngressAuthority(
        environment_profile_id=environment.attestation.environment_profile_id,
        domain_contract_pack=_domain_pack_for_compiled(compiled),
        lifecycle_ledger=ledger,
    ).admit(
        environment,
        EnvironmentIngress(
            environment_ingress_id=compiled.environment_ingress_id,
            environment_run_id=compiled.environment_run_id,
            binding_id="binding:nao.request:v1",
            ingress_type="user_request",
            payload_artifact_id="artifact:request:admission-001",
            native_lineage=(("goal_id", compiled.task_id),),
            observed_at="2026-09-28T09:00:01Z",
        ),
    )
    assert ingress.task_id == compiled.task_id and ingress.trace_id == compiled.trace_id
    ledger.record(compiled)
    proposal = _proposal(compiled)
    admitted = _semantic_admission(catalog).admit(compiled, proposal).admitted_operation
    assert admitted is not None
    ledger.record(proposal)
    ledger.record(admitted)
    lease = (
        DomainLifecycleAdmission(
            environment_run=environment,
            environment_id="nao_fake",
            lifecycle_ledger=ledger,
        )
        .request_execution(admitted)
        .execution_lease
    )
    assert lease is not None
    return compiled, catalog, environment, ledger, admitted, lease


def owner_for(catalog, environment, ledger, handler):
    return InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={"fake_nao.skills:find_object": handler},
    )


def test_catalog_semantic_widening_after_admission_rejects_before_native_effect(
    tmp_path,
):
    _, catalog, environment, ledger, _, lease = authority_fixture(tmp_path)
    original = catalog.object_for("find_object")
    changed = replace(
        original, observable_success=(*original.observable_success, "direct_speech")
    )
    drifted = BindingCatalog(
        RegistrySnapshot((changed,), source="synthetic:drift", version="changed"),
        catalog.bindings_for("find_object"),
    )
    native_calls = []

    def handler(arguments):
        native_calls.append(arguments)
        return OwnerExecutionResult(
            "native:forbidden", True, (FRESH_EFFECT, "direct_speech")
        )

    with pytest.raises(ValueError, match="object semantics"):
        owner_for(drifted, environment, ledger, handler).execute(lease)
    assert native_calls == []
    assert not ledger.has_operation_event(
        trace_id=lease.admitted_operation.trace_id,
        operation_id=lease.operation_id,
        event_type="execution_started",
    )


def test_recorded_admission_retains_exact_versioned_object_snapshot_after_restart(
    tmp_path,
):
    _, _, _, ledger, admitted, lease = authority_fixture(tmp_path)
    assert admitted.schema_version == "uah.admitted_operation/v3"
    assert (
        lease.to_dict()["admitted_operation"]["object_snapshot"]
        == admitted.to_dict()["object_snapshot"]
    )
    restarted = LifecycleLedger(ledger.path)
    event = next(
        event
        for event in restarted.events()
        if event.event_type == "semantic_admission_accepted"
    )
    assert event.data["schema_version"] == "uah.admitted_operation/v3"
    assert event.data["object_snapshot"]["object_id"] == "find_object"
    assert event.data["object_snapshot"]["owner_package"] == "object_finder"
    assert event.data["object_snapshot"]["observable_success"] == [FRESH_EFFECT]
    assert event.data["object_snapshot"]["expected_effects"] == list(
        admitted.object_snapshot.expected_effects
    )
    assert restarted.replay(admitted.trace_id).terminal_status is None


def test_mid_handler_catalog_mutation_cannot_widen_verified_observables(tmp_path):
    _, catalog, environment, ledger, admitted, lease = authority_fixture(tmp_path)
    native_calls = []
    original = catalog.object_for("find_object")

    def handler(arguments):
        native_calls.append(arguments)
        object.__setattr__(
            original, "observable_success", (FRESH_EFFECT, "direct_speech")
        )
        return OwnerExecutionResult(
            "native:already-happened", True, (FRESH_EFFECT, "direct_speech")
        )

    decision = owner_for(catalog, environment, ledger, handler).execute(lease)
    assert len(native_calls) == 1
    assert admitted.object_snapshot.observable_success == (FRESH_EFFECT,)
    assert decision.receipt is None
    assert decision.rejection.reason_codes == ("undeclared_observed_effect",)
    assert decision.rejection.owner_result.observed_effects == (
        FRESH_EFFECT,
        "direct_speech",
    )
    replay = LifecycleLedger(ledger.path).replay(admitted.trace_id)
    assert replay.terminal_status is None and replay.failure_stage == "evidence"


@pytest.mark.parametrize(
    "attack", ["nested", "foreign", "missing", "old_version", "outer_id"]
)
@pytest.mark.parametrize("crossing", ["lease", "dispatch", "evidence", "serialization"])
def test_mutated_snapshot_cannot_cross_active_authority(tmp_path, attack, crossing):
    _, catalog, environment, ledger, admitted, lease = authority_fixture(tmp_path)
    if attack == "nested":
        object.__setattr__(
            admitted.object_snapshot,
            "observable_success",
            (FRESH_EFFECT, "direct_speech"),
        )
    elif attack == "foreign":
        object.__setattr__(
            admitted,
            "object_snapshot",
            replace(admitted.object_snapshot, object_id="foreign"),
        )
    elif attack == "missing":
        object.__setattr__(admitted, "object_snapshot", None)
    elif attack == "old_version":
        object.__setattr__(admitted, "schema_version", "uah.admitted_operation/v2")
    else:
        object.__setattr__(admitted, "admission_id", "admission:sha256:stale")
    native_calls = []

    def handler(arguments):
        native_calls.append(arguments)
        return OwnerExecutionResult("native:untouched", True, (FRESH_EFFECT,))

    with pytest.raises(ValueError, match="snapshot|identity|schema"):
        if crossing == "lease":
            DomainLifecycleAdmission(
                environment_run=environment,
                environment_id="nao_fake",
                lifecycle_ledger=ledger,
            ).request_execution(admitted)
        elif crossing == "dispatch":
            owner_for(catalog, environment, ledger, handler).execute(lease)
        elif crossing == "evidence":
            result = OwnerExecutionResult(
                "native:constructed-only", True, (FRESH_EFFECT,)
            )
            evidence = EffectEvidence(
                "native:constructed-only",
                "find_object",
                admitted.binding_id,
                "nao_fake",
                "object_finder",
                True,
                (FRESH_EFFECT,),
            )
            ExecutionReceipt.issue(lease=lease, owner_result=result, evidence=evidence)
        else:
            lease.to_dict()
    assert native_calls == []


def test_untouched_snapshot_executes_and_wire_copies_cannot_mutate_it(tmp_path):
    _, catalog, environment, ledger, admitted, lease = authority_fixture(tmp_path)
    payload = admitted.to_dict()
    payload["object_snapshot"]["owner_package"] = "foreign"
    assert admitted.object_snapshot.owner_package == "object_finder"
    decision = owner_for(
        catalog,
        environment,
        ledger,
        lambda _arguments: OwnerExecutionResult(
            "native:unchanged", True, (FRESH_EFFECT,)
        ),
    ).execute(lease)
    assert decision.receipt is not None
    assert decision.receipt.evidence.observed_effects == (FRESH_EFFECT,)
    assert (
        LifecycleLedger(ledger.path).replay(admitted.trace_id).terminal_status is None
    )


def rewrite_semantic_record(ledger, mutate):
    payloads = []
    for event in ledger.events():
        payload = event.to_dict()
        payloads.append(payload)
        if event.event_type == "semantic_admission_accepted":
            data = event.data
            mutate(data)
            payload["data_json"] = json.dumps(
                data, sort_keys=True, separators=(",", ":")
            )
            identity = {
                key: value for key, value in payload.items() if key != "event_id"
            }
            encoded = json.dumps(
                identity, sort_keys=True, separators=(",", ":")
            ).encode()
            payload["event_id"] = (
                "trace-event:sha256:" + hashlib.sha256(encoded).hexdigest()
            )
            break
    ledger.path.write_text("".join(json.dumps(payload) + "\n" for payload in payloads))


def test_rehashed_trace_event_cannot_replace_admitted_snapshot_bytes(tmp_path):
    _, _, _, ledger, _, _ = authority_fixture(tmp_path)
    rewrite_semantic_record(
        ledger,
        lambda data: data["object_snapshot"]["observable_success"].append(
            "direct_speech"
        ),
    )
    with pytest.raises(ValueError, match="snapshot|identity|admitted"):
        LifecycleLedger(ledger.path)


@pytest.mark.parametrize(
    "attack",
    [
        "missing_body",
        "missing_snapshot",
        "nested_tamper",
        "active_v2",
        "missing_version",
        "alias_type",
    ],
)
def test_current_record_wire_cannot_lose_or_change_nested_authority(tmp_path, attack):
    _, _, _, ledger, _, _ = authority_fixture(tmp_path)

    def mutate(data):
        artifact = data["admitted_operation"]
        if attack == "missing_body":
            data.pop("admitted_operation")
        elif attack == "missing_snapshot":
            artifact.pop("object_snapshot")
        elif attack == "nested_tamper":
            artifact["object_snapshot"]["observable_success"].append("direct_speech")
        elif attack == "active_v2":
            artifact["schema_version"] = "uah.admitted_operation/v2"
        elif attack == "missing_version":
            artifact.pop("schema_version")
        else:
            data["ab_level"] = True

    rewrite_semantic_record(ledger, mutate)
    with pytest.raises(ValueError, match="snapshot|identity|admitted|schema"):
        LifecycleLedger(ledger.path)


def test_current_artifact_round_trip_revalidates_nested_identity(tmp_path):
    _, _, _, _, admitted, _ = authority_fixture(tmp_path)
    wire = json.loads(json.dumps(admitted.to_dict()))
    assert AdmittedOperation.from_dict(wire) == admitted
    wire["object_snapshot"]["observable_success"].append("direct_speech")
    with pytest.raises(ValueError, match="identity"):
        AdmittedOperation.from_dict(wire)
