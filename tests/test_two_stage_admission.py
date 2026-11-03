from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
import hashlib
import inspect
import json
from pathlib import Path
from threading import Event

import pytest

from ab_harness import ABControlBand
from ab_harness import ABImplementationBinding
from ab_harness import AbstractionFrame
from ab_harness import AgentOutput
from ab_harness import AgentRoleSpec
from ab_harness import BindingCatalog
from ab_harness import CompiledTask
from ab_harness import DomainContractPack
from ab_harness import DomainEffectRule
from ab_harness import DomainLifecycleAdmission
from ab_harness import EffectEvidence
from ab_harness import EnvironmentIngress
from ab_harness import EnvironmentProfile
from ab_harness import EnvironmentProfileRegistry
from ab_harness import EnvironmentRun
from ab_harness import EnvironmentRunAttestation
from ab_harness import EnvironmentRunRegistry
from ab_harness import ProposalNormalizer
from ab_harness import RegistrySnapshot
from ab_harness import SemanticAdmission
from ab_harness import TaskBudgets
from ab_harness import TaskEffectRequest
from ab_harness import TaskIngressAuthority
from ab_harness import TaskIngressRule
from ab_harness import TaskSpec
from ab_harness import TaskSpecCompiler
from ab_harness.environment import ExecutionReceipt
from ab_harness.environment import EXECUTION_RECEIPT_SCHEMA
from ab_harness.environment import EvidenceRejection
from ab_harness.environment import InProcessEnvironmentOwner
from ab_harness.contracts import OwnerExecutionResult
from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.lifecycle import AcceptanceFact
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.lifecycle import VerifiedTraceDigest
from ab_harness.operation_edges import OperationEdge
from ab_harness.runtime_controls import BudgetExhaustedError
from ab_harness.runtime_controls import ExecutionFailure
from ab_harness.runtime_controls import RetryAuthority
from ab_harness.runtime_controls import TaskRuntimeControlAuthority
from ab_harness.task_registry import EnvironmentTaskRegistry
from ab_harness.schema_validation import ArgumentField
from ab_harness.schema_validation import InMemoryArgumentSchemaRegistry
from ab_harness.schema_validation import ObjectArgumentSchema


def _admission_fixture(
    *,
    include_best_effort=False,
    budgets=None,
    prohibited_effects=("direct_speech",),
    registry_path="tests/fixtures/ab_registry.json",
):
    registry = RegistrySnapshot.from_json_file(registry_path)
    role = AgentRoleSpec(
        role_id="planner",
        allowed_output_types=("executable_plan",),
        control_band=ABControlBand(1, 1, 1, inspect_down_to_level=0),
    )
    frame = AbstractionFrame(
        frame_id="nao_runtime",
        substrate="typed robot task runtime",
        atomicity_rule="AB1 objects are directly callable",
        registry_version=registry.version,
    )
    domain = DomainContractPack.issue(
        domain_contract_pack_id="domain-pack:nao:v1",
        frame_id=frame.frame_id,
        registry_version=registry.version,
        allowed_role_ids=(role.role_id,),
        supported_task_type_ids=("find_and_report",),
        ingress_rules=(
            TaskIngressRule(
                binding_id="binding:nao.request:v1",
                ingress_type="user_request",
                action="start_task",
                task_id_lineage_key="goal_id",
            ),
            TaskIngressRule(
                binding_id="binding:nao.feedback:v1",
                ingress_type="resume_request",
                action="resume_task",
                task_id_lineage_key="goal_id",
            ),
        ),
        effect_rules=(
            DomainEffectRule(
                effect_id="fresh detector-backed result returned",
                object_id="find_object",
                evidence_owner="object_finder",
                failure_policy="terminal",
            ),
            *(
                (
                    DomainEffectRule(
                        effect_id="one terminal result event emitted",
                        object_id="report_result",
                        evidence_owner="dialogue_runtime",
                        failure_policy="retryable",
                    ),
                )
                if include_best_effort
                else ()
            ),
        ),
    )
    environment_run_id = "environment-run:nao:admission-001"
    profile = EnvironmentProfile(
        environment_profile_id="environment-profile:nao:admission:v1",
        domain_contract_pack_id=domain.domain_contract_pack_id,
        domain_contract_pack_revision=domain.revision,
        native_runtime_revision="nao-fake-runtime:v1",
        environment_owner_id="nao_fake.lifecycle_owner",
        required_interface_ids=("find_object",),
    )
    environment_run = EnvironmentRunRegistry(
        EnvironmentProfileRegistry((profile,))
    ).register(
        EnvironmentRunAttestation(
            environment_run_id=environment_run_id,
            environment_profile_id=profile.environment_profile_id,
            domain_contract_pack_revision=domain.revision,
            native_runtime_revision=profile.native_runtime_revision,
            environment_owner_id=profile.environment_owner_id,
            attestation_id="environment-attestation:admission-001",
            started_at="2026-09-28T09:00:00Z",
            readiness_evidence_refs=("artifact:readiness:admission-001",),
        )
    )
    ingress_ledger = LifecycleLedger()
    task_registry = EnvironmentTaskRegistry(ingress_ledger)
    normalized_ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:admission-001",
        environment_run_id=environment_run_id,
        binding_id="binding:nao.request:v1",
        ingress_type="user_request",
        payload_artifact_id="artifact:request:admission-001",
        native_lineage=(("goal_id", "goal:find-cup:admission-001"),),
        observed_at="2026-09-28T09:00:01Z",
    )
    ingress = TaskIngressAuthority(
        environment_profile_id=profile.environment_profile_id,
        domain_contract_pack=domain,
        lifecycle_ledger=ingress_ledger,
    ).admit(environment_run, normalized_ingress)
    task = TaskSpec(
        task_id="goal:find-cup:admission-001",
        trace_id=ingress.trace_id,
        task_type_id="find_and_report",
        role_id=role.role_id,
        frame_id=frame.frame_id,
        domain_contract_pack_revision=domain.revision,
        goal="find the red cup",
        requested_effects=(
            TaskEffectRequest(
                obligation_id="target_observed",
                effect_id="fresh detector-backed result returned",
                requirement="required",
            ),
            *(
                (
                    TaskEffectRequest(
                        obligation_id="result_reported",
                        effect_id="one terminal result event emitted",
                        requirement="best_effort",
                    ),
                )
                if include_best_effort
                else ()
            ),
        ),
        prohibited_effects=prohibited_effects,
        budgets=budgets
        or TaskBudgets(
            wall_time_seconds=90,
            model_calls=3,
            tool_calls=12,
        ),
    )
    compiled = TaskSpecCompiler().compile(
        task_ingress_decision=ingress,
        task_spec=task,
        role=role,
        frame=frame,
        registry=registry,
        domain_contract_pack=domain,
        task_registry=task_registry,
    )
    binding = ABImplementationBinding(
        binding_id="nao_fake.find_object.v1",
        object_id="find_object",
        environment_id="nao_fake",
        implementation_owner="object_finder",
        interface_kind="python_method",
        locator="fake_nao.skills:find_object",
        source_revision="fixture-rev-1",
        input_schema_ref="schema://find_object/input/v1",
        output_schema_ref="schema://find_object/result/v1",
        evidence_adapter="fake_nao.evidence:fresh_detection",
        runtime_modes=("fake",),
        status="approved",
    )
    return compiled, BindingCatalog(registry, (binding,)), environment_run


def _proposal(compiled, *, object_id="find_object", operation_id="operation:test"):
    normalization = ProposalNormalizer().normalize(
        compiled_task=compiled,
        operation_id=operation_id,
        raw_output_artifact_id="artifact:model-output:test",
        output=AgentOutput(
            output_type="executable_plan",
            payload={
                "object_id": object_id,
                "arguments": {"label": "cup"},
            },
            referenced_objects=(object_id,),
        ),
    )
    assert normalization.proposal is not None
    return normalization.proposal


def _semantic_admission(catalog):
    schema = ObjectArgumentSchema.issue(
        schema_ref="schema://find_object/input/v1",
        fields=(ArgumentField("label", "string"),),
        required=("label",),
    )
    return SemanticAdmission(
        catalog=catalog,
        environment_id="nao_fake",
        runtime_mode="fake",
        schema_validator=InMemoryArgumentSchemaRegistry((schema,)),
    )


def _domain_pack_for_compiled(compiled):
    return DomainContractPack.issue(
        domain_contract_pack_id=compiled.domain_contract_pack_id,
        frame_id=compiled.interaction_module.frame.frame_id,
        registry_version=compiled.interaction_module.frame.registry_version,
        allowed_role_ids=(compiled.interaction_module.role.role_id,),
        supported_task_type_ids=(compiled.task_type_id,),
        ingress_rules=(
            TaskIngressRule(
                binding_id="binding:nao.request:v1",
                ingress_type="user_request",
                action="start_task",
                task_id_lineage_key="goal_id",
            ),
            TaskIngressRule(
                binding_id="binding:nao.feedback:v1",
                ingress_type="resume_request",
                action="resume_task",
                task_id_lineage_key="goal_id",
            ),
        ),
        effect_rules=tuple(
            DomainEffectRule(
                effect_id=item.effect_id,
                object_id=item.object_id,
                evidence_owner=item.evidence_owner,
                failure_policy=item.failure_policy,
            )
            for item in compiled.effect_obligations
        ),
    )


def _record_task_start(ledger, compiled):
    domain = _domain_pack_for_compiled(compiled)
    run = EnvironmentRun(EnvironmentRunAttestation(
        environment_run_id=compiled.environment_run_id,
        environment_profile_id="environment-profile:admission-fixture",
        domain_contract_pack_revision=domain.revision,
        native_runtime_revision="fixture:v1",
        environment_owner_id="fixture.owner",
        attestation_id="attestation:admission-fixture",
        started_at="2026-09-28T09:00:00Z",
        readiness_evidence_refs=("artifact:readiness:fixture",),
    ))
    ingress = EnvironmentIngress(
        environment_ingress_id=compiled.environment_ingress_id,
        environment_run_id=compiled.environment_run_id,
        binding_id="binding:nao.request:v1",
        ingress_type="user_request",
        payload_artifact_id="artifact:ingress:%s" % compiled.environment_ingress_id,
        native_lineage=(("goal_id", compiled.task_id),),
        observed_at="2026-09-28T09:00:01Z",
    )
    decision = TaskIngressAuthority(
        environment_profile_id=run.attestation.environment_profile_id,
        domain_contract_pack=domain,
        lifecycle_ledger=ledger,
    ).admit(run, ingress)
    assert decision.action == "start_task"
    assert decision.trace_id == compiled.trace_id
    return decision


def _alternate_compiled_task(compiled):
    registry = RegistrySnapshot.from_json_file("tests/fixtures/ab_registry.json")
    domain = DomainContractPack.issue(
        domain_contract_pack_id=compiled.domain_contract_pack_id,
        frame_id=compiled.interaction_module.frame.frame_id,
        registry_version=registry.version,
        allowed_role_ids=(compiled.interaction_module.role.role_id,),
        supported_task_type_ids=(compiled.task_type_id,),
        ingress_rules=(
            TaskIngressRule(
                binding_id="binding:nao.request:v1",
                ingress_type="user_request",
                action="start_task",
                task_id_lineage_key="goal_id",
            ),
            TaskIngressRule(
                binding_id="binding:nao.feedback:v1",
                ingress_type="resume_request",
                action="resume_task",
                task_id_lineage_key="goal_id",
            ),
        ),
        effect_rules=tuple(
            DomainEffectRule(
                effect_id=item.effect_id,
                object_id=item.object_id,
                evidence_owner=item.evidence_owner,
                failure_policy=item.failure_policy,
            )
            for item in compiled.effect_obligations
        ),
    )
    environment_run = EnvironmentRun(
        EnvironmentRunAttestation(
            environment_run_id=compiled.environment_run_id,
            environment_profile_id="environment-profile:nao:alternate:v1",
            domain_contract_pack_revision=domain.revision,
            native_runtime_revision="nao-fixture:v1",
            environment_owner_id="nao_fixture.owner",
            attestation_id="environment-attestation:nao:alternate",
            started_at="2026-09-28T09:00:00Z",
            readiness_evidence_refs=("artifact:readiness:nao:alternate",),
        )
    )
    ingress_ledger = LifecycleLedger()
    task_registry = EnvironmentTaskRegistry(ingress_ledger)
    normalized_ingress = EnvironmentIngress(
        environment_ingress_id=compiled.environment_ingress_id,
        environment_run_id=compiled.environment_run_id,
        binding_id="binding:nao.request:v1",
        ingress_type="user_request",
        payload_artifact_id="artifact:request:admission-001",
        native_lineage=(("goal_id", compiled.task_id),),
        observed_at="2026-09-28T09:00:01Z",
    )
    ingress = TaskIngressAuthority(
        environment_profile_id=environment_run.attestation.environment_profile_id,
        domain_contract_pack=domain,
        lifecycle_ledger=ingress_ledger,
    ).admit(environment_run, normalized_ingress)
    return TaskSpecCompiler().compile(
        task_ingress_decision=ingress,
        task_spec=replace(compiled.task_spec, goal="a different frozen goal"),
        role=compiled.interaction_module.role,
        frame=compiled.interaction_module.frame,
        registry=registry,
        domain_contract_pack=domain,
        task_registry=task_registry,
    )


def _record_successful_operation(
    *,
    compiled,
    catalog,
    environment_run,
    ledger,
    operation_id,
    evidence_ref,
):
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    proposal = _proposal(compiled, operation_id=operation_id)
    ledger.record(proposal)
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger.record(semantic.admitted_operation)
    lease_decision = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(semantic.admitted_operation)
    assert lease_decision.execution_lease is not None
    lease = lease_decision.execution_lease
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={
            "fake_nao.skills:find_object": lambda _arguments: OwnerExecutionResult(
                evidence_ref=evidence_ref,
                succeeded=True,
                observed_effects=("fresh detector-backed result returned",),
            )
        },
    )
    decision = owner.execute(lease)
    assert decision.receipt is not None
    return lease, decision.receipt


def _ledger_for_admission(compiled, proposal, admitted):
    ledger = LifecycleLedger(clock=lambda: "2026-09-28T11:00:00Z")
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    ledger.record(proposal)
    ledger.record(admitted)
    return ledger


def test_typed_proposal_requires_both_admission_stages_before_a_lease():
    compiled, catalog, environment_run = _admission_fixture()
    normalization = ProposalNormalizer().normalize(
        compiled_task=compiled,
        operation_id="operation:find-cup:001",
        raw_output_artifact_id="artifact:model-output:find-cup:001",
        output=AgentOutput(
            output_type="executable_plan",
            payload={
                "object_id": "find_object",
                "arguments": {"label": "cup"},
            },
            referenced_objects=("find_object",),
        ),
    )

    assert normalization.reason_codes == ()
    proposal = normalization.proposal
    assert proposal is not None
    assert proposal.arguments == {"label": "cup"}

    semantic = _semantic_admission(catalog).admit(compiled, proposal)

    assert semantic.reason_codes == ()
    admitted = semantic.admitted_operation
    assert admitted is not None
    assert admitted.proposal_id == proposal.proposal_id
    assert admitted.binding_id == "nao_fake.find_object.v1"
    assert admitted.effect_obligation_ids == ("target_observed",)
    ledger = _ledger_for_admission(compiled, proposal, admitted)

    domain = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(admitted)

    assert domain.reason_codes == ()
    assert domain.execution_lease is not None
    assert domain.execution_lease.admission_id == admitted.admission_id
    assert domain.execution_lease.operation_id == proposal.operation_id
    assert domain.execution_lease.environment_attestation_id == (
        "environment-attestation:admission-001"
    )


def test_proposal_normalization_collects_model_contract_errors_before_admission():
    compiled, _catalog, _environment_run = _admission_fixture()

    normalization = ProposalNormalizer().normalize(
        compiled_task=compiled,
        operation_id="operation:find-cup:invalid",
        raw_output_artifact_id="artifact:model-output:invalid",
        output=AgentOutput(
            output_type="",
            payload={
                "object_id": "find_object",
                "arguments": {"label": "cup"},
            },
            referenced_objects=("walk_to",),
            claimed_effects=("fresh detector-backed result returned",),
        ),
    )

    assert normalization.proposal is None
    assert normalization.reason_codes == (
        "missing_output_type",
        "model_effect_claim_forbidden",
        "proposal_object_reference_mismatch",
    )


def test_proposal_normalization_rejection_is_replayable_and_nonterminal(tmp_path):
    compiled, _catalog, _environment_run = _admission_fixture()
    path = tmp_path / "proposal-rejection.jsonl"
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-02T09:10:00Z")
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    result = ProposalNormalizer().normalize(
        compiled_task=compiled,
        operation_id="",
        raw_output_artifact_id="",
        output=AgentOutput(
            output_type="executable_plan",
            payload={"invalid": True},
        ),
    )
    assert result.rejection is not None
    with pytest.raises(ValueError, match="identity does not match"):
        replace(result.rejection, reason_codes=("tampered",))

    commit = ledger.record(result.rejection)

    assert commit.events[0].event_type == "proposal_rejected"
    assert commit.events[0].operation_id is None
    replay = LifecycleLedger(path).replay(compiled.trace_id)
    assert replay.failure_stage == "proposal_normalization"
    assert replay.terminal_status is None
    assert replay.events[-1].data["reason_codes"] == [
        "missing_operation_id",
        "missing_raw_output_artifact_id",
        "invalid_proposal_payload",
    ]


def test_proposal_normalization_rejects_non_string_output_type():
    compiled, _catalog, _environment_run = _admission_fixture()

    normalization = ProposalNormalizer().normalize(
        compiled_task=compiled,
        operation_id="operation:find-cup:invalid-output-type",
        raw_output_artifact_id="artifact:model-output:invalid-output-type",
        output=AgentOutput(
            output_type=None,
            payload={
                "object_id": "find_object",
                "arguments": {"label": "cup"},
            },
            referenced_objects=("find_object",),
        ),
    )

    assert normalization.proposal is None
    assert normalization.reason_codes == ("invalid_output_type",)


def test_semantic_admission_rejects_an_incomplete_binding_contract():
    compiled, catalog, _environment_run = _admission_fixture()
    binding = catalog.bindings_for("find_object")[0]
    registry = RegistrySnapshot.from_json_file("tests/fixtures/ab_registry.json")
    incomplete_catalog = BindingCatalog(
        registry,
        (replace(binding, evidence_adapter=""),),
    )
    normalization = ProposalNormalizer().normalize(
        compiled_task=compiled,
        operation_id="operation:find-cup:incomplete-binding",
        raw_output_artifact_id="artifact:model-output:incomplete-binding",
        output=AgentOutput(
            output_type="executable_plan",
            payload={
                "object_id": "find_object",
                "arguments": {"label": "cup"},
            },
            referenced_objects=("find_object",),
        ),
    )
    assert normalization.proposal is not None

    decision = _semantic_admission(incomplete_catalog).admit(
        compiled, normalization.proposal
    )

    assert decision.admitted_operation is None
    assert decision.reason_codes == ("binding_contract_incomplete",)


def test_semantic_admission_rejects_catalog_effect_drift_before_a_lease(tmp_path):
    compiled, catalog, environment_run = _admission_fixture()
    object_view = catalog.object_for("find_object")
    drifted_object = replace(
        object_view,
        expected_effects=(*object_view.expected_effects, "direct_speech"),
        observable_success=(*object_view.observable_success, "direct_speech"),
    )
    drifted_catalog = BindingCatalog(
        RegistrySnapshot(
            (drifted_object,),
            source="synthetic:changed-catalog",
            version="changed-registry",
        ),
        catalog.bindings_for("find_object"),
    )
    proposal = _proposal(compiled)

    decision = _semantic_admission(drifted_catalog).admit(compiled, proposal)

    assert decision.admitted_operation is None
    assert decision.reason_codes == ("catalog_object_mismatch",)
    ledger = LifecycleLedger(tmp_path / "drift.jsonl")
    TaskIngressAuthority(
        environment_profile_id=environment_run.attestation.environment_profile_id,
        domain_contract_pack=_domain_pack_for_compiled(compiled),
        lifecycle_ledger=ledger,
    ).admit(
        environment_run,
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
    ledger.record(compiled)
    ledger.record(proposal)
    ledger.record(decision.rejection)
    replay = LifecycleLedger(tmp_path / "drift.jsonl").replay(compiled.trace_id)
    assert replay.failure_stage == "semantic_admission"
    assert replay.terminal_status is None
    assert not any(
        event.event_type in {"domain_admission_leased", "execution_started"}
        for event in replay.events
    )


def test_semantic_admission_allows_reviewed_binding_change_without_object_drift():
    compiled, catalog, _environment_run = _admission_fixture()
    binding = replace(
        catalog.bindings_for("find_object")[0],
        binding_id="nao_fake.find_object.v2",
        source_revision="fixture-rev-2",
        locator="fake_nao.skills_v2:find_object",
    )
    compatible_catalog = BindingCatalog(
        RegistrySnapshot(
            (catalog.object_for("find_object"),),
            source="synthetic:reviewed-binding-change",
            version="different-registry-label",
        ),
        (binding,),
    )

    decision = _semantic_admission(compatible_catalog).admit(
        compiled, _proposal(compiled)
    )

    assert decision.reason_codes == ()
    assert decision.admitted_operation is not None
    assert decision.admitted_operation.binding_id == "nao_fake.find_object.v2"
    assert decision.admitted_operation.binding_source_revision == "fixture-rev-2"


def test_semantic_admission_rejects_inspection_only_decomposition():
    compiled, catalog, _environment_run = _admission_fixture()

    decision = _semantic_admission(catalog).admit(
        compiled,
        _proposal(compiled, object_id="resolve_target_reference"),
    )

    assert decision.admitted_operation is None
    assert decision.reason_codes == (
        "object_inspection_only",
        "object_not_runtime_callable",
        "missing_effect_obligation",
    )


def test_semantic_admission_rejects_false_callable_with_matching_obligation(
    tmp_path,
):
    registry_payload = json.loads(
        Path("tests/fixtures/ab_registry.json").read_text(encoding="utf-8")
    )
    for item in registry_payload["objects"]:
        if item["object_id"] == "find_object":
            item["metadata"]["runtime_callable"] = False
    registry_path = tmp_path / "noncallable-registry.json"
    registry_path.write_text(json.dumps(registry_payload), encoding="utf-8")
    compiled, catalog, _environment_run = _admission_fixture(
        registry_path=registry_path
    )

    decision = _semantic_admission(catalog).admit(compiled, _proposal(compiled))

    assert decision.admitted_operation is None
    assert decision.reason_codes == ("object_not_runtime_callable",)


def test_semantic_admission_eligibility_fails_closed_after_invalid_runtime_mutation():
    compiled, catalog, _environment_run = _admission_fixture()
    object_view = compiled.interaction_module.object_for("find_object")
    assert object_view is not None
    object.__setattr__(object_view, "runtime_callable", "false")
    try:
        reasons = SemanticAdmission.static_object_rejection_reasons(
            compiled,
            "find_object",
        )
    finally:
        object.__setattr__(object_view, "runtime_callable", True)

    assert "object_not_runtime_callable" in reasons


def test_semantic_rejection_is_a_replayable_typed_fact(tmp_path):
    compiled, catalog, _environment_run = _admission_fixture()
    proposal = _proposal(
        compiled,
        object_id="resolve_target_reference",
        operation_id="operation:semantic-rejected",
    )
    path = tmp_path / "semantic-rejection.jsonl"
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-01T09:00:00Z")
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    ledger.record(proposal)

    decision = _semantic_admission(catalog).admit(compiled, proposal)

    assert decision.rejection is not None
    with pytest.raises(ValueError, match="semantic rejection identity"):
        replace(decision.rejection, reason_codes=("tampered_reason",))
    commit = ledger.record(decision.rejection)
    assert tuple(event.event_type for event in commit.events) == (
        "semantic_admission_rejected",
    )
    assert commit.events[0].data["reason_codes"] == [
        "object_inspection_only",
        "object_not_runtime_callable",
        "missing_effect_obligation",
    ]
    replay = LifecycleLedger(path).replay(compiled.trace_id)
    assert replay.failure_stage == "semantic_admission"
    assert replay.terminal_status is None
    assert not any(
        event.event_type == "domain_admission_leased" for event in replay.events
    )


def test_semantic_admission_rejects_cross_task_api_misuse_before_decision():
    compiled, catalog, _environment_run = _admission_fixture()
    other_compiled, _other_catalog, _other_run = _admission_fixture(
        include_best_effort=True
    )
    proposal = _proposal(compiled, operation_id="operation:wrong-compiled-task")

    with pytest.raises(ValueError, match="compiled task does not match proposal"):
        _semantic_admission(catalog).admit(other_compiled, proposal)


def test_semantic_admission_rejects_candidate_binding():
    compiled, catalog, _environment_run = _admission_fixture()
    binding = catalog.bindings_for("find_object")[0]
    registry = RegistrySnapshot.from_json_file("tests/fixtures/ab_registry.json")
    candidate_catalog = BindingCatalog(
        registry,
        (replace(binding, status="candidate"),),
    )

    decision = _semantic_admission(candidate_catalog).admit(
        compiled, _proposal(compiled)
    )

    assert decision.admitted_operation is None
    assert decision.reason_codes == ("binding_unavailable",)


def test_semantic_admission_rejects_binding_owned_by_another_component():
    compiled, catalog, _environment_run = _admission_fixture()
    binding = catalog.bindings_for("find_object")[0]
    registry = RegistrySnapshot.from_json_file("tests/fixtures/ab_registry.json")
    wrong_owner_catalog = BindingCatalog(
        registry,
        (replace(binding, implementation_owner="planner_llm"),),
    )

    decision = _semantic_admission(wrong_owner_catalog).admit(
        compiled, _proposal(compiled)
    )

    assert decision.admitted_operation is None
    assert decision.reason_codes == ("binding_owner_mismatch",)


def test_domain_lifecycle_replays_the_same_lease_idempotently():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled)
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(compiled, proposal, semantic.admitted_operation)
    lifecycle = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    )

    first = lifecycle.request_execution(semantic.admitted_operation)
    retry = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(semantic.admitted_operation)

    assert first.execution_lease is not None
    assert retry.execution_lease == first.execution_lease
    assert retry.reason_codes == ()
    replay = ledger.replay(compiled.trace_id)
    assert replay.failure_stage is None
    assert (
        sum(event.event_type == "domain_admission_leased" for event in replay.events)
        == 1
    )


def test_domain_lifecycle_rejects_a_different_admission_for_a_leased_operation():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled)
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(compiled, proposal, semantic.admitted_operation)
    lifecycle = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    )
    lifecycle.request_execution(semantic.admitted_operation)
    changed_binding = replace(
        catalog.bindings_for("find_object")[0],
        source_revision="fixture-rev-2",
    )
    changed_catalog = BindingCatalog(
        RegistrySnapshot.from_json_file("tests/fixtures/ab_registry.json"),
        (changed_binding,),
    )
    changed_semantic = _semantic_admission(changed_catalog).admit(compiled, proposal)
    assert changed_semantic.admitted_operation is not None
    assert (
        changed_semantic.admitted_operation.admission_id
        != semantic.admitted_operation.admission_id
    )

    with pytest.raises(ValueError, match="exact admitted operation"):
        lifecycle.request_execution(changed_semantic.admitted_operation)


def test_domain_lifecycle_rechecks_domain_revision_before_leasing():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled)
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    changed_environment = replace(
        environment_run,
        attestation=replace(
            environment_run.attestation,
            domain_contract_pack_revision="sha256:changed-domain-pack",
        ),
    )

    decision = DomainLifecycleAdmission(
        environment_run=changed_environment,
        environment_id="nao_fake",
        lifecycle_ledger=_ledger_for_admission(
            compiled,
            proposal,
            semantic.admitted_operation,
        ),
    ).request_execution(semantic.admitted_operation)

    assert decision.execution_lease is None
    assert decision.reason_codes == ("domain_contract_revision_mismatch",)


def test_domain_rejection_is_recorded_and_replayed_by_its_owner(tmp_path):
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled, operation_id="operation:domain-rejected")
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    path = tmp_path / "domain-rejection.jsonl"
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-01T09:05:00Z")
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    ledger.record(proposal)
    ledger.record(semantic.admitted_operation)
    changed_environment = replace(
        environment_run,
        attestation=replace(
            environment_run.attestation,
            domain_contract_pack_revision="sha256:changed-domain-pack",
        ),
    )

    decision = DomainLifecycleAdmission(
        environment_run=changed_environment,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(semantic.admitted_operation)

    assert decision.rejection is not None
    with pytest.raises(ValueError, match="domain rejection identity"):
        replace(decision.rejection, reason_codes=("tampered_reason",))
    replay = LifecycleLedger(path).replay(compiled.trace_id)
    assert replay.failure_stage == "domain_admission"
    assert tuple(event.event_type for event in replay.events)[-1] == (
        "domain_admission_rejected"
    )
    assert replay.events[-1].data["reason_codes"] == [
        "domain_contract_revision_mismatch"
    ]
    assert not any(event.event_type == "execution_started" for event in replay.events)


def test_authority_artifacts_reject_content_tampering():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled)
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(
        compiled,
        proposal,
        semantic.admitted_operation,
    )
    lease_decision = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(semantic.admitted_operation)
    assert lease_decision.execution_lease is not None

    with pytest.raises(ValueError, match="proposal identity does not match"):
        replace(proposal, object_id="walk_to")
    with pytest.raises(ValueError, match="admitted operation identity does not match"):
        replace(semantic.admitted_operation, binding_id="binding:tampered")
    with pytest.raises(ValueError, match="execution lease identity does not match"):
        replace(lease_decision.execution_lease, lease_owner_id="owner:tampered")


def test_semantic_admission_reverifies_its_content_addressed_inputs():
    compiled, catalog, _environment_run = _admission_fixture()
    proposal = _proposal(compiled, operation_id="operation:semantic-reverification")
    admission = _semantic_admission(catalog)

    object.__setattr__(proposal, "arguments_json", '{"label":"tampered"}')
    with pytest.raises(ValueError, match="proposal identity does not match"):
        admission.admit(compiled, proposal)

    proposal = _proposal(compiled, operation_id="operation:compiled-reverification")
    object.__setattr__(compiled.task_spec, "goal", "tampered after compilation")
    with pytest.raises(ValueError, match="compiled task identity does not match"):
        admission.admit(compiled, proposal)


def test_lifecycle_ledger_reverifies_authority_artifacts_before_recording():
    compiled, _catalog, _environment_run = _admission_fixture()
    proposal = _proposal(compiled, operation_id="operation:ledger-reverification")
    ledger = LifecycleLedger(clock=lambda: "2026-09-28T11:00:00Z")
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    object.__setattr__(proposal, "arguments_json", '{"label":"tampered"}')

    with pytest.raises(ValueError, match="proposal identity does not match"):
        ledger.record(proposal)

    assert tuple(event.event_type for event in ledger.events()) == (
        "task_started",
        "task_compiled",
    )


def test_environment_owner_executes_only_the_exact_operation_lease():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled)
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(
        compiled,
        proposal,
        semantic.admitted_operation,
    )
    lease_decision = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(semantic.admitted_operation)
    assert lease_decision.execution_lease is not None
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={
            "fake_nao.skills:find_object": lambda arguments: OwnerExecutionResult(
                evidence_ref="fake-nao://evidence/lease-bound-001",
                succeeded=True,
                observed_effects=("fresh detector-backed result returned",),
                payload={"arguments": arguments},
            )
        },
    )

    decision = owner.execute(lease_decision.execution_lease)
    assert decision.receipt is not None
    receipt = decision.receipt

    assert receipt.execution_lease_id == (
        lease_decision.execution_lease.execution_lease_id
    )
    assert receipt.evidence.binding_id == "nao_fake.find_object.v1"
    assert receipt.evidence.payload == {"arguments": {"label": "cup"}}
    assert ExecutionReceipt.from_dict(receipt.to_dict()) == receipt
    with pytest.raises(ValueError, match="does not match lease"):
        ExecutionReceipt.issue(
            lease=lease_decision.execution_lease,
            owner_result=receipt.owner_result,
            evidence=replace(receipt.evidence, object_id="walk_to"),
        )
    with pytest.raises(ValueError, match="already consumed"):
        owner.execute(lease_decision.execution_lease)
    receipt.evidence.payload["tampered"] = True
    with pytest.raises(ValueError, match="receipt identity does not match"):
        receipt.to_dict()


def _prepared_execution_lease(*, ledger, compiled, catalog, environment_run, operation_id):
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    proposal = _proposal(compiled, operation_id=operation_id)
    ledger.record(proposal)
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger.record(semantic.admitted_operation)
    decision = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(semantic.admitted_operation)
    assert decision.execution_lease is not None
    return decision.execution_lease


@pytest.mark.parametrize("succeeded", (True, False))
def test_boolean_execution_receipts_keep_their_outcome_through_restart(
    succeeded, tmp_path
):
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(
        tmp_path / "lifecycle.jsonl",
        clock=lambda: "2026-09-28T12:00:00Z",
    )
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:boolean-control:%s" % succeeded,
    )
    ledger.start_execution(lease)
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/boolean-control",
        succeeded=succeeded,
        observed_effects=("fresh detector-backed result returned",),
    )
    evidence = EffectEvidence(
        evidence_ref=owner_result.evidence_ref,
        object_id=lease.object_id,
        binding_id=lease.binding_id,
        environment_id="nao_fake",
        owner=lease.admitted_operation.binding_owner,
        succeeded=succeeded,
        observed_effects=owner_result.observed_effects,
    )

    receipt = ExecutionReceipt.issue(
        lease=lease,
        owner_result=owner_result,
        evidence=evidence,
    )
    ledger.complete_execution(receipt)
    acceptance = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations,
        (receipt.evidence,),
    )
    if succeeded:
        assert acceptance.status == "accepted"
    else:
        assert acceptance.status != "accepted"
        assert "target_observed" not in acceptance.satisfied_obligation_ids
    ledger.record(
        AcceptanceFact(
            compiled_task=compiled,
            evidence_set=(receipt.evidence,),
            acceptance=acceptance,
        )
    )

    restarted = LifecycleLedger(tmp_path / "lifecycle.jsonl")
    replayed = restarted.replay(compiled.trace_id)
    assert replayed.terminal_status == acceptance.status
    assert replayed.verified_trace_digest is not None


def _rehash_execution_receipt(payload):
    identity = {
        key: value for key, value in payload.items() if key != "execution_result_id"
    }
    encoded = json.dumps(
        identity,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "execution-receipt:sha256:%s" % hashlib.sha256(encoded).hexdigest()


def _rewrite_ledger_event(path, event_type, field, value):
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    renamed = {}
    for row in rows:
        old_event_id = row["event_id"]
        parent_event_id = row["parent_event_id"]
        if parent_event_id in renamed:
            row["parent_event_id"] = renamed[parent_event_id]
        if row["event_type"] == event_type:
            event_data = json.loads(row["data_json"])
            event_data[field] = value
            row["data_json"] = json.dumps(
                event_data,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        identity = {key: item for key, item in row.items() if key != "event_id"}
        encoded = json.dumps(
            identity,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        row["event_id"] = "trace-event:sha256:%s" % hashlib.sha256(
            encoded
        ).hexdigest()
        renamed[old_event_id] = row["event_id"]
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    ("malformed_shape", "owner_changes", "evidence_changes"),
    (
        (
            "evidence_ref",
            {"evidence_ref": 1},
            {"evidence_ref": 1},
        ),
        (
            "observed_effects_member",
            {"observed_effects": ("effect", 1)},
            {"observed_effects": ("effect", 1)},
        ),
        (
            "observed_effects_container",
            {"observed_effects": ["effect"]},
            {"observed_effects": ["effect"]},
        ),
        (
            "payload_container",
            {"payload": []},
            {"payload": []},
        ),
        (
            "nested_tuple",
            {"payload": {"nested": ("x",)}},
            {"payload": {"nested": ("x",)}},
        ),
        (
            "mapping_key_alias",
            {"payload": {1: "x"}},
            {"payload": {"1": "x"}},
        ),
    ),
)
def test_execution_receipt_issue_rejects_malformed_json_wire_shapes(
    malformed_shape, owner_changes, evidence_changes
):
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-10-21T00:00:00Z")
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:malformed-wire:%s" % malformed_shape,
    )
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/malformed-wire",
        succeeded=False,
        observed_effects=("effect",),
        payload={"nested": [None, True, 1, 1.5, "x"]},
    )
    evidence = EffectEvidence(
        evidence_ref=owner_result.evidence_ref,
        object_id=lease.object_id,
        binding_id=lease.binding_id,
        environment_id="nao_fake",
        owner=lease.admitted_operation.binding_owner,
        succeeded=False,
        observed_effects=owner_result.observed_effects,
        payload=owner_result.payload,
    )

    with pytest.raises(ValueError):
        ExecutionReceipt.issue(
            lease=lease,
            owner_result=replace(owner_result, **owner_changes),
            evidence=replace(evidence, **evidence_changes),
        )


def test_execution_receipt_round_trips_exact_nested_json_and_false_outcome():
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-10-21T00:00:00Z")
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:valid-json-roundtrip",
    )
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/valid-json-roundtrip",
        succeeded=False,
        observed_effects=("effect was not observed",),
        payload={"nested": [None, True, 1, 1.5, "x", {"empty": []}]},
    )
    evidence = EffectEvidence(
        evidence_ref=owner_result.evidence_ref,
        object_id=lease.object_id,
        binding_id=lease.binding_id,
        environment_id="nao_fake",
        owner=lease.admitted_operation.binding_owner,
        succeeded=False,
        observed_effects=owner_result.observed_effects,
        payload=owner_result.payload,
    )

    receipt = ExecutionReceipt.issue(
        lease=lease,
        owner_result=owner_result,
        evidence=evidence,
    )
    wire = json.loads(json.dumps(receipt.to_dict(), allow_nan=False))
    restored = ExecutionReceipt.from_dict(wire)

    assert restored == receipt
    assert restored.owner_result.succeeded is False
    assert restored.owner_result.payload == owner_result.payload


def test_execution_receipt_from_dict_rejects_non_json_nested_payload():
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-10-21T00:00:00Z")
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:from-dict-non-json-payload",
    )
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/from-dict-non-json-payload",
        succeeded=True,
        observed_effects=("effect",),
    )
    evidence = EffectEvidence(
        evidence_ref=owner_result.evidence_ref,
        object_id=lease.object_id,
        binding_id=lease.binding_id,
        environment_id="nao_fake",
        owner=lease.admitted_operation.binding_owner,
        succeeded=True,
        observed_effects=owner_result.observed_effects,
    )
    payload = ExecutionReceipt.issue(
        lease=lease,
        owner_result=owner_result,
        evidence=evidence,
    ).to_dict()
    payload["owner_result"]["payload"] = {"nested": ("tuple is not JSON",)}
    payload["execution_result_id"] = _rehash_execution_receipt(payload)

    with pytest.raises(ValueError, match="must contain JSON values"):
        ExecutionReceipt.from_dict(payload)


def test_execution_completion_rejects_non_json_payload_without_ledger_write(
    tmp_path,
):
    compiled, catalog, environment_run = _admission_fixture()
    ledger_path = tmp_path / "completion-non-json-payload.jsonl"
    ledger = LifecycleLedger(
        ledger_path,
        clock=lambda: "2026-10-21T00:00:00Z",
    )
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:completion-non-json-payload",
    )
    ledger.start_execution(lease)
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/completion-non-json-payload",
        succeeded=True,
        observed_effects=("effect",),
    )
    evidence = EffectEvidence(
        evidence_ref=owner_result.evidence_ref,
        object_id=lease.object_id,
        binding_id=lease.binding_id,
        environment_id="nao_fake",
        owner=lease.admitted_operation.binding_owner,
        succeeded=True,
        observed_effects=owner_result.observed_effects,
    )
    receipt = ExecutionReceipt.issue(
        lease=lease,
        owner_result=owner_result,
        evidence=evidence,
    )
    forged_payload = receipt.to_dict()
    forged_payload["owner_result"]["payload"] = {"nested": {1: "alias"}}
    forged_payload["evidence"]["payload"] = {"nested": {"1": "alias"}}
    forged_payload["execution_result_id"] = _rehash_execution_receipt(forged_payload)
    object.__setattr__(receipt.owner_result, "payload", {"nested": {1: "alias"}})
    object.__setattr__(receipt.evidence, "payload", {"nested": {"1": "alias"}})
    object.__setattr__(
        receipt,
        "execution_result_id",
        forged_payload["execution_result_id"],
    )
    events_before = ledger.events()

    with pytest.raises(ValueError, match="mapping keys must be strings"):
        ledger.complete_execution(receipt)

    assert ledger.events() == events_before


def test_execution_completion_uses_detached_receipt_verification(tmp_path):
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(
        tmp_path / "completion-overridden-receipt.jsonl",
        clock=lambda: "2026-10-21T00:00:00Z",
    )
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:overridden-receipt-verifier",
    )
    ledger.start_execution(lease)
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/overridden-receipt-verifier",
        succeeded=True,
        observed_effects=("fresh detector-backed result returned",),
        payload={"value": True},
    )
    receipt = ExecutionReceipt.issue(
        lease=lease,
        owner_result=owner_result,
        evidence=EffectEvidence(
            evidence_ref=owner_result.evidence_ref,
            object_id=lease.object_id,
            binding_id=lease.binding_id,
            environment_id="nao_fake",
            owner=lease.admitted_operation.binding_owner,
            succeeded=True,
            observed_effects=owner_result.observed_effects,
            payload=owner_result.payload,
        ),
    )
    object.__setattr__(
        receipt.owner_result,
        "payload",
        {"nested": ("not a JSON wire value",)},
    )
    object.__setattr__(receipt, "verify_identity", lambda: None)
    object.__setattr__(receipt, "_identity_payload", lambda: {})
    events_before = ledger.events()

    with pytest.raises(ValueError):
        ledger.complete_execution(receipt)

    assert ledger.events() == events_before


@pytest.mark.parametrize("nested_artifact", ("owner_result", "evidence"))
def test_execution_completion_rejects_nested_artifact_overrides(
    nested_artifact, tmp_path
):
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(
        tmp_path / ("completion-nested-override-%s.jsonl" % nested_artifact),
        clock=lambda: "2026-10-21T00:00:00Z",
    )
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:nested-override:%s" % nested_artifact,
    )
    ledger.start_execution(lease)
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/nested-override",
        succeeded=True,
        observed_effects=("fresh detector-backed result returned",),
        payload={"value": True},
    )
    evidence = EffectEvidence(
        evidence_ref=owner_result.evidence_ref,
        object_id=lease.object_id,
        binding_id=lease.binding_id,
        environment_id="nao_fake",
        owner=lease.admitted_operation.binding_owner,
        succeeded=True,
        observed_effects=owner_result.observed_effects,
        payload=owner_result.payload,
    )
    receipt = ExecutionReceipt.issue(
        lease=lease,
        owner_result=owner_result,
        evidence=evidence,
    )

    if nested_artifact == "owner_result":

        class OverriddenOwnerResult(OwnerExecutionResult):
            def __getattribute__(self, name):
                if name == "payload":
                    return {"value": True}
                return super().__getattribute__(name)

        nested = OverriddenOwnerResult(
            evidence_ref=owner_result.evidence_ref,
            succeeded=True,
            observed_effects=owner_result.observed_effects,
            payload={"nested": ("not JSON",)},
        )
    else:

        class OverriddenEvidence(EffectEvidence):
            def __getattribute__(self, name):
                if name == "payload":
                    return {"value": True}
                return super().__getattribute__(name)

        nested = OverriddenEvidence(
            evidence_ref=evidence.evidence_ref,
            object_id=evidence.object_id,
            binding_id=evidence.binding_id,
            environment_id=evidence.environment_id,
            owner=evidence.owner,
            succeeded=True,
            observed_effects=evidence.observed_effects,
            payload={"nested": ("not JSON",)},
        )

    object.__setattr__(receipt, nested_artifact, nested)
    object.__setattr__(receipt, "verify_identity", lambda: None)
    events_before = ledger.events()

    with pytest.raises(ValueError):
        ledger.complete_execution(receipt)

    assert ledger.events() == events_before


def test_execution_completion_rejects_receipt_subclass_verifier_override():
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-10-21T00:00:00Z")
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:receipt-subclass-verifier",
    )
    ledger.start_execution(lease)
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/receipt-subclass-verifier",
        succeeded=True,
        observed_effects=("fresh detector-backed result returned",),
    )
    valid = ExecutionReceipt.issue(
        lease=lease,
        owner_result=owner_result,
        evidence=EffectEvidence(
            evidence_ref=owner_result.evidence_ref,
            object_id=lease.object_id,
            binding_id=lease.binding_id,
            environment_id="nao_fake",
            owner=lease.admitted_operation.binding_owner,
            succeeded=True,
            observed_effects=owner_result.observed_effects,
        ),
    )

    class OverriddenReceipt(ExecutionReceipt):
        def verify_identity(self):
            return None

    forged = OverriddenReceipt(
        execution_result_id=valid.execution_result_id,
        execution_lease_id=valid.execution_lease_id,
        admission_id=valid.admission_id,
        environment_run_id=valid.environment_run_id,
        task_id=valid.task_id,
        trace_id=valid.trace_id,
        operation_id=valid.operation_id,
        owner_result=valid.owner_result,
        evidence=valid.evidence,
        schema_version=valid.schema_version,
    )
    events_before = ledger.events()

    with pytest.raises(ValueError, match="concrete receipt type"):
        ledger.complete_execution(forged)

    assert ledger.events() == events_before


@pytest.mark.parametrize(
    ("event_type", "field", "malformed"),
    (
        ("execution_completed", "execution_result_id", 1),
        ("evidence_issued", "evidence_artifact_id", 1),
        ("evidence_issued", "native_evidence_ref", 1),
        ("evidence_issued", "observed_effects", ["effect", 1]),
        ("evidence_rejected", "native_evidence_ref", 1),
        ("evidence_rejected", "reason_codes", [1]),
    ),
)
def test_receipt_replay_rejects_malformed_wire_evidence_fields(
    tmp_path, event_type, field, malformed
):
    compiled, catalog, environment_run = _admission_fixture()
    ledger_path = tmp_path / "malformed-receipt-replay.jsonl"
    ledger = LifecycleLedger(
        ledger_path,
        clock=lambda: "2026-10-21T00:00:00Z",
    )
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:malformed-replay:%s:%s" % (event_type, field),
    )
    ledger.start_execution(lease)
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/malformed-replay",
        succeeded=True,
        observed_effects=("effect",),
    )
    evidence = EffectEvidence(
        evidence_ref=owner_result.evidence_ref,
        object_id=lease.object_id,
        binding_id=lease.binding_id,
        environment_id="nao_fake",
        owner=lease.admitted_operation.binding_owner,
        succeeded=True,
        observed_effects=owner_result.observed_effects,
    )
    if event_type == "evidence_rejected":
        ledger.record(
            EvidenceRejection.issue(
                lease=lease,
                owner_result=owner_result,
                reason_codes=("invalid_evidence",),
            )
        )
    else:
        ledger.complete_execution(
            ExecutionReceipt.issue(
                lease=lease,
                owner_result=owner_result,
                evidence=evidence,
            )
        )
    _rewrite_ledger_event(ledger_path, event_type, field, malformed)

    with pytest.raises(ValueError):
        LifecycleLedger(ledger_path).replay(compiled.trace_id)


def test_receipt_consistency_holds_through_construction_completion_and_restart(
    tmp_path,
):
    compiled, catalog, environment_run = _admission_fixture()
    ledger_path = tmp_path / "receipt-consistency.jsonl"
    ledger = LifecycleLedger(
        ledger_path,
        clock=lambda: "2026-10-20T00:00:00Z",
    )
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:receipt-consistency",
    )
    ledger.start_execution(lease)
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/receipt-consistency",
        succeeded=True,
        observed_effects=("fresh detector-backed result returned",),
    )
    evidence = EffectEvidence(
        evidence_ref=owner_result.evidence_ref,
        object_id=lease.object_id,
        binding_id=lease.binding_id,
        environment_id="nao_fake",
        owner=lease.admitted_operation.binding_owner,
        succeeded=True,
        observed_effects=owner_result.observed_effects,
    )
    receipt = ExecutionReceipt.issue(
        lease=lease,
        owner_result=owner_result,
        evidence=evidence,
    )
    mismatched = receipt.to_dict()
    mismatched["owner_result"]["succeeded"] = False
    mismatched["execution_result_id"] = _rehash_execution_receipt(mismatched)
    inconsistent_owner_result = replace(owner_result, succeeded=False)

    with pytest.raises(ValueError, match="does not match owner result"):
        ExecutionReceipt.from_dict(mismatched)
    with pytest.raises(ValueError, match="does not match owner result"):
        replace(
            receipt,
            execution_result_id=mismatched["execution_result_id"],
            owner_result=inconsistent_owner_result,
        )

    events_before_completion = ledger.events()
    object.__setattr__(receipt.owner_result, "succeeded", False)
    object.__setattr__(
        receipt,
        "execution_result_id",
        mismatched["execution_result_id"],
    )
    with pytest.raises(ValueError, match="does not match owner result"):
        ledger.complete_execution(receipt)
    assert ledger.events() == events_before_completion

    restarted = LifecycleLedger(ledger_path)
    assert restarted.replay(compiled.trace_id).terminal_status is None


def test_receipt_projection_is_replay_verifiable_after_event_rehash(tmp_path):
    compiled, catalog, environment_run = _admission_fixture()
    ledger_path = tmp_path / "receipt-projection.jsonl"
    ledger = LifecycleLedger(
        ledger_path,
        clock=lambda: "2026-10-20T00:00:00Z",
    )
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:receipt-projection",
    )
    ledger.start_execution(lease)
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/receipt-projection",
        succeeded=True,
        observed_effects=("fresh detector-backed result returned",),
        payload={"value": "native"},
    )
    evidence = EffectEvidence(
        evidence_ref=owner_result.evidence_ref,
        object_id=lease.object_id,
        binding_id=lease.binding_id,
        environment_id="nao_fake",
        owner=lease.admitted_operation.binding_owner,
        succeeded=owner_result.succeeded,
        observed_effects=owner_result.observed_effects,
        payload=owner_result.payload,
    )
    receipt = ExecutionReceipt.issue(
        lease=lease,
        owner_result=owner_result,
        evidence=evidence,
    )
    ledger.complete_execution(receipt)

    completed = next(
        event for event in ledger.events() if event.event_type == "execution_completed"
    )
    issued = next(
        event for event in ledger.events() if event.event_type == "evidence_issued"
    )
    assert completed.data["receipt_projection_version"] == EXECUTION_RECEIPT_SCHEMA
    assert completed.data["execution_receipt"] == receipt.to_dict()
    assert issued.data["receipt_projection_version"] == EXECUTION_RECEIPT_SCHEMA
    LifecycleLedger(ledger_path).replay(compiled.trace_id)

    original_ledger = ledger_path.read_bytes()
    _rewrite_ledger_event(
        ledger_path,
        "evidence_issued",
        "native_evidence_ref",
        "fake-nao://evidence/forged-after-rehash",
    )
    with pytest.raises(ValueError, match="receipt projection|native evidence"):
        LifecycleLedger(ledger_path).replay(compiled.trace_id)

    for event_type, field in (
        ("execution_completed", "execution_receipt"),
        ("evidence_issued", "receipt_projection_version"),
    ):
        ledger_path.write_bytes(original_ledger)
        _rewrite_ledger_event(ledger_path, event_type, field, None)
        with pytest.raises(ValueError, match="receipt projection"):
            LifecycleLedger(ledger_path).replay(compiled.trace_id)


@pytest.mark.parametrize(
    ("native_value", "normalized_value"),
    ((False, 0), (True, 1), (1, 1.0)),
)
def test_receipt_requires_type_exact_json_agreement_through_issue_and_replay(
    native_value, normalized_value, tmp_path
):
    compiled, catalog, environment_run = _admission_fixture()
    ledger_path = tmp_path / "typed-json-receipt.jsonl"
    ledger = LifecycleLedger(
        ledger_path,
        clock=lambda: "2026-10-20T00:00:00Z",
    )
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:typed-json-receipt:%s"
        % type(native_value).__name__,
    )
    ledger.start_execution(lease)
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/typed-json-receipt",
        succeeded=True,
        observed_effects=(),
        payload={"nested": {"value": native_value}},
    )
    evidence = EffectEvidence(
        evidence_ref=owner_result.evidence_ref,
        object_id=lease.object_id,
        binding_id=lease.binding_id,
        environment_id="nao_fake",
        owner=lease.admitted_operation.binding_owner,
        succeeded=True,
        observed_effects=(),
        payload={"nested": {"value": normalized_value}},
    )

    with pytest.raises(ValueError, match="does not match (?:lease and )?owner result"):
        ExecutionReceipt.issue(
            lease=lease,
            owner_result=owner_result,
            evidence=evidence,
        )
    assert not any(
        event.event_type in {"execution_completed", "evidence_issued"}
        for event in ledger.events()
    )

    valid_owner_result = replace(owner_result, payload=evidence.payload)
    valid_receipt = ExecutionReceipt.issue(
        lease=lease,
        owner_result=valid_owner_result,
        evidence=evidence,
    )
    forged_payload = valid_receipt.to_dict()
    forged_payload["owner_result"]["payload"] = owner_result.payload
    forged_payload["execution_result_id"] = _rehash_execution_receipt(forged_payload)
    with pytest.raises(ValueError, match="does not match (?:lease and )?owner result"):
        ExecutionReceipt.from_dict(forged_payload)
    with pytest.raises(ValueError, match="does not match (?:lease and )?owner result"):
        replace(
            valid_receipt,
            owner_result=owner_result,
            execution_result_id=forged_payload["execution_result_id"],
        )

    object.__setattr__(valid_receipt, "owner_result", owner_result)
    object.__setattr__(
        valid_receipt,
        "execution_result_id",
        forged_payload["execution_result_id"],
    )
    with pytest.raises(ValueError, match="does not match (?:lease and )?owner result"):
        ledger.complete_execution(valid_receipt)
    assert not any(
        event.event_type in {"execution_completed", "evidence_issued"}
        for event in ledger.events()
    )
    assert LifecycleLedger(ledger_path).replay(compiled.trace_id).terminal_status is None


@pytest.mark.parametrize(
    ("native_value", "normalized_value"),
    ((False, 0), (True, 1), (1, 1.0)),
)
def test_receipt_issue_requires_type_exact_observed_effects(
    native_value, normalized_value
):
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-10-20T00:00:00Z")
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:typed-effects:%s" % type(native_value).__name__,
    )
    ledger.start_execution(lease)
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/typed-effects",
        succeeded=True,
        observed_effects=(native_value,),
    )
    evidence = EffectEvidence(
        evidence_ref=owner_result.evidence_ref,
        object_id=lease.object_id,
        binding_id=lease.binding_id,
        environment_id="nao_fake",
        owner=lease.admitted_operation.binding_owner,
        succeeded=True,
        observed_effects=(normalized_value,),
    )

    with pytest.raises(
        ValueError,
        match=(
            "execution receipt effects must be tuples of strings|"
            "does not match (?:lease and )?owner result"
        ),
    ):
        ExecutionReceipt.issue(
            lease=lease,
            owner_result=owner_result,
            evidence=evidence,
        )


@pytest.mark.parametrize("malformed", ("false", "true", 0, 1, None))
def test_execution_receipt_issue_rejects_non_boolean_success_before_evidence(
    malformed,
):
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-09-28T12:00:00Z")
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:malformed-success:%s" % type(malformed).__name__,
    )
    ledger.start_execution(lease)
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/malformed-success",
        succeeded=malformed,
        observed_effects=("fresh detector-backed result returned",),
    )
    evidence = EffectEvidence(
        evidence_ref=owner_result.evidence_ref,
        object_id=lease.object_id,
        binding_id=lease.binding_id,
        environment_id="nao_fake",
        owner=lease.admitted_operation.binding_owner,
        succeeded=malformed,
        observed_effects=owner_result.observed_effects,
    )

    with pytest.raises(ValueError, match="success values must be booleans"):
        ExecutionReceipt.issue(
            lease=lease,
            owner_result=owner_result,
            evidence=evidence,
        )

    event_types = tuple(event.event_type for event in ledger.events())
    assert "execution_completed" not in event_types
    assert "evidence_issued" not in event_types


def _replace_ledger_event_success(path, event_type, malformed):
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    parent_event_id = None
    for row in rows:
        if row["event_type"] == event_type:
            data = json.loads(row["data_json"])
            data["succeeded"] = malformed
            row["data_json"] = json.dumps(
                data, allow_nan=False, sort_keys=True, separators=(",", ":")
            )
        row["parent_event_id"] = parent_event_id
        identity = {key: value for key, value in row.items() if key != "event_id"}
        row["event_id"] = "trace-event:sha256:%s" % hashlib.sha256(
            json.dumps(
                identity, allow_nan=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        parent_event_id = row["event_id"]
    path.write_text(
        "".join(
            json.dumps(row, allow_nan=False, sort_keys=True, separators=(",", ":"))
            + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )


def _replace_ledger_event_success_values(path, replacements):
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    parent_event_id = None
    for row in rows:
        if row["event_type"] in replacements:
            data = json.loads(row["data_json"])
            data["succeeded"] = replacements[row["event_type"]]
            row["data_json"] = json.dumps(
                data, allow_nan=False, sort_keys=True, separators=(",", ":")
            )
        row["parent_event_id"] = parent_event_id
        identity = {key: value for key, value in row.items() if key != "event_id"}
        row["event_id"] = "trace-event:sha256:%s" % hashlib.sha256(
            json.dumps(
                identity, allow_nan=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        parent_event_id = row["event_id"]
    path.write_text(
        "".join(
            json.dumps(row, allow_nan=False, sort_keys=True, separators=(",", ":"))
            + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )


@pytest.mark.parametrize("event_type", ("execution_completed", "evidence_issued"))
def test_lifecycle_reload_rejects_non_boolean_execution_success(event_type, tmp_path):
    compiled, catalog, environment_run = _admission_fixture()
    ledger_path = tmp_path / "lifecycle.jsonl"
    ledger = LifecycleLedger(
        ledger_path,
        clock=lambda: "2026-09-28T12:00:00Z",
    )
    _record_successful_operation(
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        ledger=ledger,
        operation_id="operation:reload-bool-check",
        evidence_ref="fake-nao://evidence/reload-bool-check",
    )

    _replace_ledger_event_success(ledger_path, event_type, "false")

    with pytest.raises(ValueError, match="success values must be booleans"):
        LifecycleLedger(ledger_path)


def test_lifecycle_reload_rejects_owner_evidence_success_disagreement(tmp_path):
    compiled, catalog, environment_run = _admission_fixture()
    ledger_path = tmp_path / "receipt-outcome-mismatch.jsonl"
    ledger = LifecycleLedger(
        ledger_path,
        clock=lambda: "2026-10-20T00:00:00Z",
    )
    _lease, receipt = _record_successful_operation(
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        ledger=ledger,
        operation_id="operation:receipt-outcome-mismatch",
        evidence_ref="fake-nao://evidence/receipt-outcome-mismatch",
    )
    acceptance = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations,
        (receipt.evidence,),
    )
    ledger.record(
        AcceptanceFact(
            compiled_task=compiled,
            evidence_set=(receipt.evidence,),
            acceptance=acceptance,
        )
    )
    assert acceptance.status == "accepted"

    _replace_ledger_event_success_values(
        ledger_path,
        {"execution_completed": False, "evidence_issued": True},
    )

    with pytest.raises(ValueError, match="does not match execution result"):
        LifecycleLedger(ledger_path)


@pytest.mark.parametrize("malformed", ("false", "true", 0, 1, None))
def test_evidence_rejection_issue_rejects_non_boolean_success(malformed):
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-10-20T00:00:00Z")
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:evidence-rejection-non-bool:%s"
        % type(malformed).__name__,
    )
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/rejected-non-bool",
        succeeded=malformed,
        observed_effects=(),
    )

    with pytest.raises(ValueError, match="success values must be booleans"):
        EvidenceRejection.issue(
            lease=lease,
            owner_result=owner_result,
            reason_codes=("invalid_evidence",),
        )


def test_evidence_rejection_keeps_literal_false_and_rejects_mutated_value():
    compiled, catalog, environment_run = _admission_fixture()
    lease = _prepared_execution_lease(
        ledger=LifecycleLedger(clock=lambda: "2026-10-20T00:00:00Z"),
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:evidence-rejection-false-control",
    )
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/false-result",
        succeeded=False,
        observed_effects=(),
    )
    rejection = EvidenceRejection.issue(
        lease=lease,
        owner_result=owner_result,
        reason_codes=("owner_reported_failure",),
    )

    assert rejection.owner_result.succeeded is False
    with pytest.raises(ValueError, match="success values must be booleans"):
        replace(
            rejection,
            owner_result=replace(owner_result, succeeded="false"),
        )


@pytest.mark.parametrize(
    "malformed_result",
    (
        {"evidence_ref": 1},
        {"observed_effects": ("effect", 1)},
        {"payload": {"nested": ("tuple",)}},
        {"payload": {1: "not a string key"}},
    ),
)
def test_evidence_rejection_rejects_non_wire_owner_result_shape(malformed_result):
    compiled, catalog, environment_run = _admission_fixture()
    lease = _prepared_execution_lease(
        ledger=LifecycleLedger(clock=lambda: "2026-10-20T00:00:00Z"),
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:evidence-rejection-wire-shape",
    )
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/rejected-wire-shape",
        succeeded=False,
        observed_effects=("effect",),
        payload={"nested": ["valid"]},
    )

    with pytest.raises(ValueError):
        EvidenceRejection.issue(
            lease=lease,
            owner_result=replace(owner_result, **malformed_result),
            reason_codes=("invalid_evidence",),
        )


@pytest.mark.parametrize("malformed", ("false", "true", 0, 1, None))
def test_task_acceptance_rejects_non_boolean_evidence(malformed):
    compiled, _catalog, _environment_run = _admission_fixture()
    obligation = compiled.effect_obligations[0]
    evidence = EffectEvidence(
        evidence_ref="fake-nao://evidence/non-boolean-acceptance",
        object_id=obligation.object_id,
        binding_id="nao_fake.find_object.v1",
        environment_id="nao_fake",
        owner=obligation.evidence_owner,
        succeeded=malformed,
        observed_effects=(obligation.effect_id,),
    )

    with pytest.raises(ValueError, match="success values must be booleans"):
        TaskAcceptanceEvaluator().evaluate(
            compiled.effect_obligations,
            (evidence,),
        )


@pytest.mark.parametrize(
    "policy,attack",
    (
        (False, "none"),
        (True, "none"),
        ("false", "none"),
        (0, "none"),
        (1, "none"),
        (None, "none"),
        (False, "shadow_before_registry"),
        (False, "shadow_after_registry"),
    ),
)
def test_additional_argument_policy_is_boolean_before_admission_and_owner_dispatch(
    policy, attack
):
    compiled, catalog, environment = _admission_fixture()
    native_calls = []

    def admit_and_execute():
        schema = ObjectArgumentSchema.issue(
            schema_ref="schema://find_object/input/v1",
            fields=(ArgumentField("label", "string"),),
            required=("label",),
            allow_additional_properties=policy,
        )
        if attack == "shadow_before_registry":
            object.__setattr__(schema, "allow_additional_properties", "false")
            object.__setattr__(schema, "verify_identity", lambda: None)
        proposal = (
            ProposalNormalizer()
            .normalize(
                compiled_task=compiled,
                operation_id="operation:strict-policy",
                raw_output_artifact_id="artifact:strict-policy",
                output=AgentOutput(
                    "executable_plan",
                    {
                        "object_id": "find_object",
                        "arguments": {"label": "cup", "extra": True},
                    },
                    ("find_object",),
                ),
            )
            .proposal
        )
        validator = InMemoryArgumentSchemaRegistry((schema,))
        if attack == "shadow_after_registry":
            object.__setattr__(schema, "allow_additional_properties", "false")
            object.__setattr__(schema, "verify_identity", lambda: None)
        semantic = SemanticAdmission(
            catalog=catalog,
            environment_id="nao_fake",
            runtime_mode="fake",
            schema_validator=validator,
        ).admit(compiled, proposal)
        if not semantic.accepted:
            return semantic.reason_codes
        ledger = _ledger_for_admission(compiled, proposal, semantic.admitted_operation)
        lease = (
            DomainLifecycleAdmission(
                environment_run=environment,
                environment_id="nao_fake",
                lifecycle_ledger=ledger,
            )
            .request_execution(semantic.admitted_operation)
            .execution_lease
        )

        def native(arguments):
            native_calls.append(arguments)
            return OwnerExecutionResult(
                "artifact:strict-policy-evidence",
                True,
                ("fresh detector-backed result returned",),
            )

        return InProcessEnvironmentOwner(
            environment_id="nao_fake",
            environment_run=environment,
            catalog=catalog,
            lifecycle_ledger=ledger,
            handlers={"fake_nao.skills:find_object": native},
        ).execute(lease)

    if attack == "shadow_before_registry":
        with pytest.raises(TypeError, match="additional properties.*boolean"):
            admit_and_execute()
        assert native_calls == []
    elif type(policy) is not bool:
        with pytest.raises(TypeError, match="additional properties.*boolean"):
            admit_and_execute()
        assert native_calls == []
    elif policy is False:
        assert admit_and_execute() == ("proposal_arguments_schema_invalid",)
        assert native_calls == []
    else:
        assert admit_and_execute().receipt is not None
        assert native_calls == [{"label": "cup", "extra": True}]


def test_environment_owner_records_typed_evidence_rejection():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled, operation_id="operation:evidence-rejected")
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(compiled, proposal, semantic.admitted_operation)
    lease = (
        DomainLifecycleAdmission(
            environment_run=environment_run,
            environment_id="nao_fake",
            lifecycle_ledger=ledger,
        )
        .request_execution(semantic.admitted_operation)
        .execution_lease
    )
    assert lease is not None
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={
            "fake_nao.skills:find_object": lambda _arguments: OwnerExecutionResult(
                evidence_ref="",
                succeeded=True,
                observed_effects=(),
            )
        },
    )

    decision = owner.execute(lease)

    assert decision.receipt is None
    assert decision.rejection is not None
    assert decision.rejection.reason_codes == (
        "missing_evidence_reference",
        "successful_result_without_observable",
    )
    with pytest.raises(ValueError, match="identity does not match"):
        replace(decision.rejection, reason_codes=("tampered",))
    replay = ledger.replay(compiled.trace_id)
    assert tuple(event.event_type for event in replay.events)[-2:] == (
        "execution_completed",
        "evidence_rejected",
    )
    assert replay.failure_stage == "evidence"
    assert replay.terminal_status is None


@pytest.mark.parametrize(
    ("observed_effects", "payload"),
    (
        (["fresh detector-backed result returned"], {}),
        (("fresh detector-backed result returned",), [("value", False)]),
    ),
)
def test_environment_owner_rejects_malformed_native_result_without_evidence(
    observed_effects, payload
):
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-10-21T00:00:00Z")
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:malformed-native-result",
    )
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={
            "fake_nao.skills:find_object": lambda _arguments: OwnerExecutionResult(
                evidence_ref="fake-nao://evidence/malformed-native-result",
                succeeded=True,
                observed_effects=observed_effects,
                payload=payload,
            )
        },
    )

    with pytest.raises(ValueError):
        owner.execute(lease)

    event_types = tuple(event.event_type for event in ledger.events())
    assert event_types[-2:] == ("execution_started", "execution_failed")
    assert "execution_completed" not in event_types
    assert "evidence_issued" not in event_types


def test_environment_owner_rejects_a_proposal_changed_after_lease_issuance():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled, operation_id="operation:tampered-after-lease")
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(compiled, proposal, semantic.admitted_operation)
    lease_decision = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(semantic.admitted_operation)
    assert lease_decision.execution_lease is not None
    dispatched_arguments = []
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={
            "fake_nao.skills:find_object": lambda arguments: (
                dispatched_arguments.append(arguments)
                or OwnerExecutionResult(
                    evidence_ref="fake-nao://evidence/must-not-dispatch",
                    succeeded=True,
                    observed_effects=("fresh detector-backed result returned",),
                )
            )
        },
    )
    object.__setattr__(proposal, "arguments_json", '{"label":"tampered"}')

    with pytest.raises(ValueError, match="proposal identity does not match"):
        owner.execute(lease_decision.execution_lease)

    assert dispatched_arguments == []


@pytest.mark.parametrize("runtime_callable", (1, 1.0))
def test_environment_owner_requires_literal_runtime_callable_before_dispatch(
    runtime_callable,
):
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-10-21T00:00:00Z")
    lease = _prepared_execution_lease(
        ledger=ledger,
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        operation_id="operation:malformed-runtime-callable",
    )
    item = catalog.object_for(lease.object_id)
    assert item is not None
    object.__setattr__(item, "runtime_callable", runtime_callable)
    dispatched_arguments = []
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={
            "fake_nao.skills:find_object": lambda arguments: (
                dispatched_arguments.append(arguments)
                or OwnerExecutionResult(
                    evidence_ref="fake-nao://evidence/malformed-runtime-callable",
                    succeeded=True,
                    observed_effects=("fresh detector-backed result returned",),
                )
            )
        },
    )

    with pytest.raises(ValueError, match="not runtime callable"):
        owner.execute(lease)

    assert dispatched_arguments == []
    assert not any(
        event.event_type == "execution_started" for event in ledger.events()
    )


def test_environment_owner_consumes_a_lease_when_native_execution_fails():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled, operation_id="operation:native-failure")
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(
        compiled,
        proposal,
        semantic.admitted_operation,
    )
    lease_decision = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(semantic.admitted_operation)
    assert lease_decision.execution_lease is not None
    calls: list[dict[str, object]] = []

    def fail_after_dispatch(arguments):
        calls.append(arguments)
        raise RuntimeError("native owner failed after accepting the operation")

    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={"fake_nao.skills:find_object": fail_after_dispatch},
    )

    with pytest.raises(RuntimeError, match="native owner failed"):
        owner.execute(lease_decision.execution_lease)
    restarted_owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={"fake_nao.skills:find_object": fail_after_dispatch},
    )
    with pytest.raises(ValueError, match="already consumed"):
        restarted_owner.execute(lease_decision.execution_lease)
    assert calls == [{"label": "cup"}]


def test_environment_owner_records_receipt_validation_failure():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled, operation_id="operation:invalid-receipt")
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(compiled, proposal, semantic.admitted_operation)
    lease = (
        DomainLifecycleAdmission(
            environment_run=environment_run,
            environment_id="nao_fake",
            lifecycle_ledger=ledger,
        )
        .request_execution(semantic.admitted_operation)
        .execution_lease
    )
    assert lease is not None
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={
            "fake_nao.skills:find_object": lambda _arguments: OwnerExecutionResult(
                evidence_ref="fake-nao://evidence/invalid-receipt",
                succeeded=True,
                observed_effects=("fresh detector-backed result returned",),
                payload={"confidence": float("nan")},
            )
        },
    )

    with pytest.raises(ValueError, match="finite JSON"):
        owner.execute(lease)

    assert tuple(event.event_type for event in ledger.replay(compiled.trace_id).events)[
        -2:
    ] == ("execution_started", "execution_failed")


def test_environment_owner_consumes_a_lease_once_across_ledger_instances(tmp_path):
    compiled, catalog, environment_run = _admission_fixture()
    path = tmp_path / "contended-lifecycle.jsonl"
    writer = LifecycleLedger(path, clock=lambda: "2026-09-28T11:30:00Z")
    proposal = _proposal(compiled, operation_id="operation:cross-process-once")
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    _record_task_start(writer, compiled)
    writer.record(compiled)
    writer.record(proposal)
    writer.record(semantic.admitted_operation)
    lease = (
        DomainLifecycleAdmission(
            environment_run=environment_run,
            environment_id="nao_fake",
            lifecycle_ledger=writer,
        )
        .request_execution(semantic.admitted_operation)
        .execution_lease
    )
    assert lease is not None

    first_ledger = LifecycleLedger(path, clock=lambda: "2026-09-28T11:30:01Z")
    stale_ledger = LifecycleLedger(path, clock=lambda: "2026-09-28T11:30:02Z")
    calls = []

    def handler(arguments):
        calls.append(arguments)
        return OwnerExecutionResult(
            evidence_ref="fake-nao://evidence/cross-process-once",
            succeeded=True,
            observed_effects=("fresh detector-backed result returned",),
        )

    first_owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=first_ledger,
        handlers={"fake_nao.skills:find_object": handler},
    )
    stale_owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=stale_ledger,
        handlers={"fake_nao.skills:find_object": handler},
    )

    first_owner.execute(lease)
    with pytest.raises(ValueError, match="already consumed"):
        stale_owner.execute(lease)

    assert calls == [{"label": "cup"}]
    assert LifecycleLedger(path).has_operation_event(
        trace_id=compiled.trace_id,
        operation_id=lease.operation_id,
        event_type="execution_completed",
    )


def test_environment_owner_has_no_direct_object_dispatch_interface():
    _compiled, catalog, environment_run = _admission_fixture()
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=LifecycleLedger(),
        handlers={},
    )

    assert tuple(inspect.signature(owner.execute).parameters) == ("lease",)
    with pytest.raises(TypeError, match="unexpected keyword argument 'object_id'"):
        owner.execute(
            object_id="find_object",
            arguments={"label": "cup"},
            runtime_mode="fake",
        )


def test_environment_owner_rejects_a_lease_from_a_stale_activation_attestation():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled, operation_id="operation:stale-attestation")
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(compiled, proposal, semantic.admitted_operation)
    lease = (
        DomainLifecycleAdmission(
            environment_run=environment_run,
            environment_id="nao_fake",
            lifecycle_ledger=ledger,
        )
        .request_execution(semantic.admitted_operation)
        .execution_lease
    )
    assert lease is not None
    restarted_run = replace(
        environment_run,
        attestation=replace(
            environment_run.attestation,
            attestation_id="environment-attestation:admission-002",
        ),
    )
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=restarted_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={},
    )

    with pytest.raises(ValueError, match="stale environment attestation"):
        owner.execute(lease)


def test_environment_owner_rejects_a_lease_issued_by_another_owner():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled, operation_id="operation:foreign-owner")
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(
        compiled,
        proposal,
        semantic.admitted_operation,
    )
    lease_decision = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(semantic.admitted_operation)
    assert lease_decision.execution_lease is not None
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=replace(
            environment_run,
            attestation=replace(
                environment_run.attestation,
                environment_owner_id="another.lifecycle.owner",
            ),
        ),
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={},
    )

    with pytest.raises(ValueError, match="another environment owner"):
        owner.execute(lease_decision.execution_lease)


def test_environment_owner_rejects_binding_drift_under_the_same_revision():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled, operation_id="operation:binding-drift")
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(
        compiled,
        proposal,
        semantic.admitted_operation,
    )
    lease_decision = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(semantic.admitted_operation)
    assert lease_decision.execution_lease is not None
    lease = lease_decision.execution_lease
    original_binding = catalog.bindings_for("find_object")[0]
    drifted_catalog = BindingCatalog(
        RegistrySnapshot.from_json_file("tests/fixtures/ab_registry.json"),
        (replace(original_binding, locator="changed.skills:find_object"),),
    )
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=drifted_catalog,
        lifecycle_ledger=ledger,
        handlers={"changed.skills:find_object": lambda _arguments: None},
    )

    with pytest.raises(ValueError, match="binding no longer matches"):
        owner.execute(lease)


def test_lifecycle_ledger_rejects_a_self_consistent_receipt_with_forged_lineage():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled, operation_id="operation:forged-receipt")
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(compiled, proposal, semantic.admitted_operation)
    lease = (
        DomainLifecycleAdmission(
            environment_run=environment_run,
            environment_id="nao_fake",
            lifecycle_ledger=ledger,
        )
        .request_execution(semantic.admitted_operation)
        .execution_lease
    )
    assert lease is not None
    ledger.start_execution(lease)
    owner_result = OwnerExecutionResult(
        evidence_ref="fake-nao://evidence/forged-receipt",
        succeeded=True,
        observed_effects=("fresh detector-backed result returned",),
    )
    valid = ExecutionReceipt.issue(
        lease=lease,
        owner_result=owner_result,
        evidence=EffectEvidence(
            evidence_ref=owner_result.evidence_ref,
            object_id=lease.object_id,
            binding_id=lease.binding_id,
            environment_id="nao_fake",
            owner="object_finder",
            succeeded=True,
            observed_effects=owner_result.observed_effects,
        ),
    )
    payload = valid.to_dict()
    payload["evidence"]["owner"] = "forged.owner"
    identity = {
        key: value for key, value in payload.items() if key != "execution_result_id"
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    payload["execution_result_id"] = (
        "execution-receipt:sha256:" + hashlib.sha256(encoded).hexdigest()
    )
    forged = ExecutionReceipt.from_dict(payload)

    with pytest.raises(ValueError, match="does not match admitted operation"):
        ledger.complete_execution(forged)


def test_common_ledger_replays_the_full_accepted_authority_chain(tmp_path):
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(
        tmp_path / "lifecycle.jsonl",
        clock=lambda: "2026-09-28T12:00:00Z",
    )
    lease, receipt = _record_successful_operation(
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        ledger=ledger,
        operation_id="operation:ledger-accepted",
        evidence_ref="fake-nao://evidence/ledger-accepted",
    )
    acceptance = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations,
        (receipt.evidence,),
    )
    ledger.record(
        AcceptanceFact(
            compiled_task=compiled,
            evidence_set=(receipt.evidence,),
            acceptance=acceptance,
        )
    )

    restarted_ledger = LifecycleLedger(tmp_path / "lifecycle.jsonl")
    replayed = restarted_ledger.replay(compiled.trace_id)

    assert tuple(event.event_type for event in replayed.events) == (
        "task_started",
        "task_compiled",
            "proposal_normalized",
            "semantic_admission_accepted",
            "domain_admission_leased",
            "budget_granted",
            "execution_started",
        "execution_completed",
        "evidence_issued",
        "effect_obligation_satisfied",
        "terminal_task_accepted",
    )
    assert replayed.terminal_status == "accepted"
    assert replayed.verified_trace_digest is not None
    assert replayed.verified_trace_digest.execution_lease_ids == (
        lease.execution_lease_id,
    )
    assert replayed.verified_trace_digest.native_evidence_refs == (
        "fake-nao://evidence/ledger-accepted",
    )
    assert (
        VerifiedTraceDigest.from_dict(replayed.verified_trace_digest.to_dict())
        == replayed.verified_trace_digest
    )
    domain_pack = _domain_pack_for_compiled(compiled)
    assert domain_pack.revision == compiled.domain_contract_pack_revision
    decision = TaskIngressAuthority(
        environment_profile_id=environment_run.attestation.environment_profile_id,
        domain_contract_pack=domain_pack,
        lifecycle_ledger=restarted_ledger,
    ).admit(
        environment_run,
        EnvironmentIngress(
            environment_ingress_id="ingress:after-terminal-restart",
            environment_run_id=compiled.environment_run_id,
            binding_id="binding:nao.feedback:v1",
            ingress_type="resume_request",
            payload_artifact_id="artifact:feedback:after-terminal",
            native_lineage=(("goal_id", compiled.task_id),),
            observed_at="2026-10-01T10:00:00Z",
        ),
    )
    assert decision.action == "reject"
    assert decision.reason_code == "task_terminal"
    assert decision.task_status == "accepted"


def test_task_acceptance_waits_for_every_dispatched_native_operation(tmp_path):
    compiled, catalog, environment_run = _admission_fixture()
    ledger_path = tmp_path / "unsettled-native-operation.jsonl"
    ledger = LifecycleLedger(
        ledger_path,
        clock=lambda: "2026-09-28T12:00:00Z",
    )
    _first_lease, first_receipt = _record_successful_operation(
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        ledger=ledger,
        operation_id="operation:settlement:first",
        evidence_ref="fake-nao://evidence/settlement-first",
    )

    pending_proposal = _proposal(
        compiled,
        operation_id="operation:settlement:pending",
    )
    ledger.record(pending_proposal)
    pending_admission = _semantic_admission(catalog).admit(
        compiled,
        pending_proposal,
    )
    assert pending_admission.admitted_operation is not None
    ledger.record(pending_admission.admitted_operation)
    pending_lease = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(pending_admission.admitted_operation).execution_lease
    assert pending_lease is not None

    handler_started = Event()
    release_handler = Event()

    def blocked_handler(_arguments):
        handler_started.set()
        assert release_handler.wait(timeout=5)
        return OwnerExecutionResult(
            evidence_ref="fake-nao://evidence/settlement-pending",
            succeeded=True,
            observed_effects=("fresh detector-backed result returned",),
        )

    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={"fake_nao.skills:find_object": blocked_handler},
    )
    acceptance_before_settlement = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations,
        (first_receipt.evidence,),
    )

    with ThreadPoolExecutor(max_workers=1) as executor:
        dispatched = executor.submit(owner.execute, pending_lease)
        assert handler_started.wait(timeout=5)
        events_before_acceptance = ledger.events()
        try:
            with pytest.raises(ValueError, match="settled native execution"):
                ledger.record(
                    AcceptanceFact(
                        compiled_task=compiled,
                        evidence_set=(first_receipt.evidence,),
                        acceptance=acceptance_before_settlement,
                    )
                )
        finally:
            release_handler.set()
        pending_decision = dispatched.result(timeout=5)

    assert pending_decision.receipt is not None
    assert ledger.events()[: len(events_before_acceptance)] == events_before_acceptance
    settled_evidence = (first_receipt.evidence, pending_decision.receipt.evidence)
    settled_acceptance = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations,
        settled_evidence,
    )
    ledger.record(
        AcceptanceFact(
            compiled_task=compiled,
            evidence_set=settled_evidence,
            acceptance=settled_acceptance,
        )
    )

    replay = LifecycleLedger(ledger_path).replay(compiled.trace_id)
    assert replay.terminal_status == "accepted"
    assert replay.verified_trace_digest is not None
    assert replay.verified_trace_digest.execution_result_ids == tuple(
        event.data["execution_result_id"]
        for event in replay.events
        if event.event_type == "execution_completed"
    )


def test_terminal_required_effect_failure_replays_as_counterexample_digest(tmp_path):
    compiled, catalog, environment_run = _admission_fixture()
    path = tmp_path / "terminal-counterexample.jsonl"
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-02T09:20:00Z")
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    proposal = _proposal(compiled, operation_id="operation:negative-result")
    ledger.record(proposal)
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger.record(semantic.admitted_operation)
    lease = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(semantic.admitted_operation).execution_lease
    assert lease is not None
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={
            "fake_nao.skills:find_object": lambda _arguments: OwnerExecutionResult(
                evidence_ref="fake-nao://evidence/not-found",
                succeeded=False,
                observed_effects=(),
                payload={"reason": "not_found"},
            )
        },
    )
    evidence_decision = owner.execute(lease)
    assert evidence_decision.receipt is not None
    acceptance = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations,
        (evidence_decision.receipt.evidence,),
    )
    ledger.record(
        AcceptanceFact(
            compiled_task=compiled,
            evidence_set=(evidence_decision.receipt.evidence,),
            acceptance=acceptance,
        )
    )

    replay = LifecycleLedger(path).replay(compiled.trace_id)

    assert acceptance.status == "rejected"
    assert replay.terminal_status == "rejected"
    assert replay.failure_stage == "task_acceptance"
    assert replay.verified_trace_digest is not None
    assert replay.verified_trace_digest.failed_obligation_ids == (
        "target_observed",
    )
    assert replay.verified_trace_digest.native_evidence_refs == (
        "fake-nao://evidence/not-found",
    )


@pytest.mark.parametrize(
    "success_value",
    ("false", "true", 0, 1, None, [], {}),
    ids=("string-false", "string-true", "zero", "one", "none", "list", "object"),
)
def test_owner_rejects_non_boolean_success_before_issuing_evidence(
    tmp_path, success_value
):
    compiled, catalog, environment_run = _admission_fixture()
    ledger_path = tmp_path / "non-boolean-owner-result.jsonl"
    ledger = LifecycleLedger(
        ledger_path,
        clock=lambda: "2026-10-17T00:00:00Z",
    )
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    proposal = _proposal(compiled, operation_id="operation:non-boolean-owner")
    ledger.record(proposal)
    admitted = _semantic_admission(catalog).admit(compiled, proposal).admitted_operation
    assert admitted is not None
    ledger.record(admitted)
    lease = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(admitted).execution_lease
    assert lease is not None
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={
            "fake_nao.skills:find_object": lambda _arguments: OwnerExecutionResult(
                evidence_ref="fake://non-boolean-owner-result",
                succeeded=success_value,
                observed_effects=("fresh detector-backed result returned",),
            )
        },
    )

    with pytest.raises(TypeError, match="succeeded must be a boolean"):
        owner.execute(lease)

    event_types = tuple(event.event_type for event in ledger.events())
    assert "evidence_issued" not in event_types
    assert "terminal_task_accepted" not in event_types
    assert LifecycleLedger(ledger_path).replay(compiled.trace_id).terminal_status is None


def test_common_ledger_replays_an_accepted_task_with_best_effort_deficit(tmp_path):
    compiled, catalog, environment_run = _admission_fixture(include_best_effort=True)
    ledger = LifecycleLedger(
        tmp_path / "deficit-lifecycle.jsonl",
        clock=lambda: "2026-09-28T12:05:00Z",
    )
    _lease, receipt = _record_successful_operation(
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        ledger=ledger,
        operation_id="operation:ledger-deficit",
        evidence_ref="fake-nao://evidence/ledger-deficit",
    )
    acceptance = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations,
        (receipt.evidence,),
    )

    ledger.record(
        AcceptanceFact(
            compiled_task=compiled,
            evidence_set=(receipt.evidence,),
            acceptance=acceptance,
        )
    )
    replayed = LifecycleLedger(tmp_path / "deficit-lifecycle.jsonl").replay(
        compiled.trace_id
    )

    assert acceptance.status == "accepted_with_deficit"
    assert replayed.terminal_status == "accepted_with_deficit"
    assert replayed.verified_trace_digest is not None
    assert replayed.verified_trace_digest.satisfied_obligation_ids == (
        "target_observed",
    )
    assert replayed.verified_trace_digest.deficit_obligation_ids == ("result_reported",)


@pytest.mark.parametrize(
    ("field", "malformed"),
    (
        ("status", "rejected"),
        ("satisfied_obligation_ids", ["invented-satisfied"]),
        ("deficit_obligation_ids", []),
        ("pending_obligation_ids", ["invented-pending"]),
        ("failed_obligation_ids", ["invented-failed"]),
        ("evidence_refs", ["fake-nao://evidence/invented"]),
        ("acceptance_id", "task-acceptance:sha256:invented"),
    ),
)
def test_replay_rejects_resigned_terminal_acceptance_mismatches(
    field,
    malformed,
    tmp_path,
):
    compiled, catalog, environment_run = _admission_fixture(include_best_effort=True)
    path = tmp_path / ("acceptance-mismatch-%s.jsonl" % field)
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-02T09:20:00Z")
    _lease, receipt = _record_successful_operation(
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        ledger=ledger,
        operation_id="operation:acceptance-mismatch:%s" % field,
        evidence_ref="fake-nao://evidence/acceptance-mismatch:%s" % field,
    )
    acceptance = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations,
        (receipt.evidence,),
    )
    ledger.record(
        AcceptanceFact(
            compiled_task=compiled,
            evidence_set=(receipt.evidence,),
            acceptance=acceptance,
        )
    )

    assert acceptance.status == "accepted_with_deficit"
    _rewrite_ledger_event(
        path,
        "terminal_task_accepted_with_deficit",
        field,
        malformed,
    )

    with pytest.raises(ValueError):
        LifecycleLedger(path)


def test_common_ledger_records_pre_dispatch_suspension():
    compiled, _catalog, _environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-09-28T12:07:00Z")
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    acceptance = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations,
        (),
    )

    commit = ledger.record(
        AcceptanceFact(
            compiled_task=compiled,
            evidence_set=(),
            acceptance=acceptance,
        )
    )

    assert acceptance.status == "suspended"
    assert tuple(event.event_type for event in commit.events) == (
        "effect_obligation_pending",
        "task_suspended",
    )
    replayed = ledger.replay(compiled.trace_id)
    assert replayed.terminal_status is None
    assert replayed.verified_trace_digest is None


def test_ledger_rejects_tampered_compiled_task_before_acceptance_append(tmp_path):
    compiled, _catalog, _environment_run = _admission_fixture()
    ledger_path = tmp_path / "tampered-compiled-task.jsonl"
    ledger = LifecycleLedger(
        ledger_path,
        clock=lambda: "2026-09-28T12:00:00Z",
    )
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    before = ledger.events()

    object.__setattr__(
        compiled,
        "effect_obligations",
        tuple(
            replace(item, requirement="best_effort")
            for item in compiled.effect_obligations
        ),
    )
    object.__setattr__(compiled, "verify_identity", lambda: None)
    acceptance = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations,
        (),
    )
    assert acceptance.status == "accepted_with_deficit"

    with pytest.raises((TypeError, ValueError), match="compiled task"):
        ledger.record(
            AcceptanceFact(
                compiled_task=compiled,
                evidence_set=(),
                acceptance=acceptance,
            )
        )

    assert ledger.events() == before
    assert LifecycleLedger(ledger_path).replay(compiled.trace_id).terminal_status is None


def test_ledger_rejects_tampered_compiled_task_before_compiled_event(tmp_path):
    compiled, _catalog, _environment_run = _admission_fixture()
    ledger_path = tmp_path / "tampered-compiled-event.jsonl"
    ledger = LifecycleLedger(
        ledger_path,
        clock=lambda: "2026-09-28T12:00:00Z",
    )
    _record_task_start(ledger, compiled)
    before = ledger.events()
    object.__setattr__(
        compiled,
        "effect_obligations",
        tuple(
            replace(item, requirement="best_effort")
            for item in compiled.effect_obligations
        ),
    )
    object.__setattr__(compiled, "verify_identity", lambda: None)

    with pytest.raises((TypeError, ValueError), match="compiled task"):
        ledger.record(compiled)

    assert ledger.events() == before
    assert LifecycleLedger(ledger_path).replay(compiled.trace_id).terminal_status is None


@pytest.mark.parametrize("field", (
    "goal", "requested_effects", "requested_requirement", "model_calls",
    "tool_calls", "wall_time_seconds", "retry_attempts",
))
@pytest.mark.parametrize("consumer", (
    "export", "record", "normalize", "admit", "accept", "timeout",
))
def test_compiled_task_consumers_reject_changed_source_before_progress(
    tmp_path, field, consumer,
):
    compiled, catalog, _environment_run = _admission_fixture()
    path = tmp_path / "consumer-source.jsonl"
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-02T09:00:00Z")
    _record_task_start(ledger, compiled)
    if consumer != "record":
        ledger.record(compiled)
    before = ledger.events()
    trace_id = compiled.trace_id
    proposal = _proposal(compiled, operation_id="operation:source-integrity")
    if field == "goal":
        object.__setattr__(compiled.task_spec, "goal", "changed task intent")
    elif field == "requested_effects":
        object.__setattr__(
            compiled.task_spec.requested_effects[0], "effect_id", "different effect",
        )
    elif field == "requested_requirement":
        object.__setattr__(
            compiled.task_spec.requested_effects[0], "requirement", "best_effort",
        )
    else:
        object.__setattr__(compiled.budgets, field, 999)
    object.__setattr__(compiled, "verify_identity", lambda: None)

    with pytest.raises((TypeError, ValueError)):
        if consumer == "export":
            compiled.to_dict()
        elif consumer == "record":
            ledger.record(compiled)
        elif consumer == "normalize":
            ProposalNormalizer().normalize(
                compiled_task=compiled,
                operation_id="operation:source-integrity",
                raw_output_artifact_id="model-output:source-integrity",
                output=AgentOutput(
                    output_type="executable_plan",
                    payload={"object_id": "find_object", "arguments": {}},
                    referenced_objects=("find_object",),
                ),
            )
        elif consumer == "admit":
            _semantic_admission(catalog).admit(compiled, proposal)
        elif consumer == "accept":
            ledger.record(AcceptanceFact(
                compiled_task=compiled, evidence_set=(),
                acceptance=TaskAcceptanceEvaluator().evaluate(
                    compiled.effect_obligations, (),
                ),
            ))
        else:
            TaskRuntimeControlAuthority(ledger).evaluate_timeout(
                compiled_task=compiled, observed_at="2026-10-02T09:00:30Z",
                policy_revision="timeout-policy:v1",
            )

    assert ledger.events() == before
    replay = LifecycleLedger(path).replay(trace_id)
    assert replay.terminal_status is None
    assert not any(event.event_type == "execution_started" for event in replay.events)


def test_compiled_task_verified_copy_detaches_and_checks_nested_contracts():
    compiled, _catalog, _environment_run = _admission_fixture()
    snapshot = CompiledTask.verified_copy(compiled)

    assert snapshot == compiled
    assert snapshot is not compiled
    assert snapshot.task_spec is not compiled.task_spec
    assert snapshot.interaction_module is not compiled.interaction_module
    assert snapshot.effect_obligations[0] is not compiled.effect_obligations[0]

    object.__setattr__(
        compiled.effect_obligations[0],
        "requirement",
        "best_effort",
    )

    with pytest.raises(ValueError, match="compiled task identity does not match content"):
        CompiledTask.verified_copy(compiled)
    assert snapshot.effect_obligations[0].requirement == "required"


def test_compiled_task_verified_copy_rejects_top_level_and_nested_subclasses():
    compiled, _catalog, _environment_run = _admission_fixture()

    class CompiledTaskSubclass(CompiledTask):
        pass

    subclass = object.__new__(CompiledTaskSubclass)
    for field_name in CompiledTask.__dataclass_fields__:
        object.__setattr__(subclass, field_name, getattr(compiled, field_name))

    with pytest.raises(TypeError, match="concrete owner type"):
        CompiledTask.verified_copy(subclass)

    original = compiled.interaction_module
    module_type = type(original)

    class InteractionModuleSubclass(module_type):
        pass

    nested = InteractionModuleSubclass(
        task_id=original.task_id,
        role=original.role,
        frame=original.frame,
        objects=original.objects,
        registry_source=original.registry_source,
    )
    nested_subclass_task = replace(compiled, interaction_module=nested)

    with pytest.raises(TypeError, match="trusted concrete dataclass"):
        CompiledTask.verified_copy(nested_subclass_task)


def test_proposal_normalizer_rejects_shadow_verified_task_before_proposal():
    compiled, _catalog, _environment_run = _admission_fixture()
    object.__setattr__(
        compiled,
        "effect_obligations",
        tuple(
            replace(item, requirement="best_effort")
            for item in compiled.effect_obligations
        ),
    )
    object.__setattr__(compiled, "verify_identity", lambda: None)

    with pytest.raises((TypeError, ValueError), match="compiled task"):
        ProposalNormalizer().normalize(
            compiled_task=compiled,
            operation_id="operation:shadowed-task",
            raw_output_artifact_id="model-output:shadowed-task",
            output=AgentOutput(
                output_type="executable_plan",
                payload={"object_id": "find_object", "arguments": {}},
                referenced_objects=("find_object",),
            ),
        )


def test_semantic_admission_rejects_shadow_verified_task_before_decision():
    compiled, catalog, _environment_run = _admission_fixture()
    proposal = _proposal(compiled, operation_id="operation:shadowed-task")
    object.__setattr__(
        compiled,
        "effect_obligations",
        tuple(
            replace(item, requirement="best_effort")
            for item in compiled.effect_obligations
        ),
    )
    object.__setattr__(compiled, "verify_identity", lambda: None)

    with pytest.raises((TypeError, ValueError), match="compiled task"):
        _semantic_admission(catalog).admit(compiled, proposal)


def test_semantic_admission_does_not_consume_removed_task_prohibition():
    compiled, catalog, _environment_run = _admission_fixture(
        prohibited_effects=("requested object localized",)
    )
    proposal = _proposal(compiled, operation_id="operation:prohibited-task")
    object.__setattr__(compiled, "prohibited_effects", ())
    object.__setattr__(compiled, "verify_identity", lambda: None)

    with pytest.raises((TypeError, ValueError), match="compiled task"):
        _semantic_admission(catalog).admit(compiled, proposal)


def test_common_ledger_rejects_a_crash_truncated_acceptance_commit(tmp_path):
    compiled, catalog, environment_run = _admission_fixture()
    complete_path = tmp_path / "complete-lifecycle.jsonl"
    ledger = LifecycleLedger(
        complete_path,
        clock=lambda: "2026-09-28T12:10:00Z",
    )
    _lease, receipt = _record_successful_operation(
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        ledger=ledger,
        operation_id="operation:truncated-acceptance",
        evidence_ref="fake-nao://evidence/truncated-acceptance",
    )
    acceptance = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations,
        (receipt.evidence,),
    )
    ledger.record(
        AcceptanceFact(
            compiled_task=compiled,
            evidence_set=(receipt.evidence,),
            acceptance=acceptance,
        )
    )
    lines = complete_path.read_text(encoding="utf-8").splitlines()
    truncated_path = tmp_path / "truncated-lifecycle.jsonl"
    truncated_path.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="incomplete commit"):
        LifecycleLedger(truncated_path)


def test_common_ledger_rejects_unrecorded_evidence_at_task_acceptance():
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-09-28T12:15:00Z")
    _lease, receipt = _record_successful_operation(
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        ledger=ledger,
        operation_id="operation:forged-evidence",
        evidence_ref="fake-nao://evidence/recorded",
    )
    forged_evidence = replace(
        receipt.evidence,
        evidence_ref="fake-nao://evidence/not-recorded",
    )
    forged_acceptance = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations,
        (forged_evidence,),
    )

    with pytest.raises(ValueError, match="incomplete or unrecorded"):
        ledger.record(
            AcceptanceFact(
                compiled_task=compiled,
                evidence_set=(forged_evidence,),
                acceptance=forged_acceptance,
            )
        )


def test_common_ledger_rejects_acceptance_that_omits_recorded_evidence():
    compiled, catalog, environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-09-28T12:17:00Z")
    _lease, _receipt = _record_successful_operation(
        compiled=compiled,
        catalog=catalog,
        environment_run=environment_run,
        ledger=ledger,
        operation_id="operation:omitted-evidence",
        evidence_ref="fake-nao://evidence/omitted",
    )
    incomplete = TaskAcceptanceEvaluator().evaluate(
        compiled.effect_obligations,
        (),
    )

    with pytest.raises(ValueError, match="incomplete or unrecorded"):
        ledger.record(
            AcceptanceFact(
                compiled_task=compiled,
                evidence_set=(),
                acceptance=incomplete,
            )
        )


def test_common_ledger_rejects_a_second_compiled_task_for_one_trace():
    compiled, _catalog, _environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-09-28T12:20:00Z")
    _record_task_start(ledger, compiled)
    ledger.record(compiled)

    with pytest.raises(ValueError, match="already has a compiled task"):
        ledger.record(compiled)


def test_common_ledger_rejects_a_proposal_from_an_unrecorded_compiled_task():
    compiled, _catalog, _environment_run = _admission_fixture()
    alternate = _alternate_compiled_task(compiled)
    ledger = LifecycleLedger(clock=lambda: "2026-09-28T12:25:00Z")
    _record_task_start(ledger, compiled)
    ledger.record(compiled)

    with pytest.raises(ValueError, match="does not match recorded compiled task"):
        ledger.record(
            _proposal(
                alternate,
                operation_id="operation:alternate-compiled-task",
            )
        )


def test_operation_edge_replays_same_frame_decomposition(tmp_path):
    compiled, catalog, _environment_run = _admission_fixture()
    source = _proposal(compiled, operation_id="operation:deliver")
    target = _proposal(compiled, operation_id="operation:find")
    source_admission = _semantic_admission(catalog).admit(compiled, source)
    target_admission = _semantic_admission(catalog).admit(compiled, target)
    assert source_admission.admitted_operation is not None
    assert target_admission.admitted_operation is not None
    path = tmp_path / "operation-edge.jsonl"
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-02T09:00:00Z")
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    for proposal, decision in (
        (source, source_admission),
        (target, target_admission),
    ):
        ledger.record(proposal)
        ledger.record(decision.admitted_operation)
    edge = OperationEdge.issue(
        environment_run_id=compiled.environment_run_id,
        task_id=compiled.task_id,
        trace_id=compiled.trace_id,
        source_operation_id=source.operation_id,
        target_operation_id=target.operation_id,
        relation="decomposes_to",
        source_frame_id=compiled.interaction_module.frame.frame_id,
        target_frame_id=compiled.interaction_module.frame.frame_id,
    )
    assert OperationEdge.from_dict(edge.to_dict()) == edge
    with pytest.raises(ValueError, match="identity does not match"):
        replace(edge, target_operation_id="operation:tampered")

    commit = ledger.record(edge)

    assert commit.events[0].event_type == "operation_edge_recorded"
    replay = LifecycleLedger(path).replay(compiled.trace_id)
    assert replay.events[-1].data == edge.to_dict()


def test_operation_edge_requires_existing_operations_and_acyclic_graph():
    compiled, catalog, _environment_run = _admission_fixture()
    source = _proposal(compiled, operation_id="operation:source")
    target = _proposal(compiled, operation_id="operation:target")
    source_admission = _semantic_admission(catalog).admit(compiled, source)
    target_admission = _semantic_admission(catalog).admit(compiled, target)
    assert source_admission.admitted_operation is not None
    assert target_admission.admitted_operation is not None
    ledger = LifecycleLedger()
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    ledger.record(source)
    ledger.record(source_admission.admitted_operation)
    unknown = OperationEdge.issue(
        environment_run_id=compiled.environment_run_id,
        task_id=compiled.task_id,
        trace_id=compiled.trace_id,
        source_operation_id=source.operation_id,
        target_operation_id="operation:unknown",
        relation="continues_with",
        source_frame_id="nao_runtime",
        target_frame_id="nao_runtime",
    )

    with pytest.raises(ValueError, match="edge target operation is not recorded"):
        ledger.record(unknown)

    ledger.record(target)
    ledger.record(target_admission.admitted_operation)
    ledger.record(
        OperationEdge.issue(
            environment_run_id=compiled.environment_run_id,
            task_id=compiled.task_id,
            trace_id=compiled.trace_id,
            source_operation_id=source.operation_id,
            target_operation_id=target.operation_id,
            relation="decomposes_to",
            source_frame_id="nao_runtime",
            target_frame_id="nao_runtime",
        )
    )
    with pytest.raises(ValueError, match="operation edge would create a cycle"):
        ledger.record(
            OperationEdge.issue(
                environment_run_id=compiled.environment_run_id,
                task_id=compiled.task_id,
                trace_id=compiled.trace_id,
                source_operation_id=target.operation_id,
                target_operation_id=source.operation_id,
                relation="decomposes_to",
                source_frame_id="nao_runtime",
                target_frame_id="nao_runtime",
            )
        )


def test_operation_edge_relation_rules_are_frame_relative():
    common = {
        "environment_run_id": "environment-run:test",
        "task_id": "task:test",
        "trace_id": "trace:test",
        "source_operation_id": "operation:source",
        "target_operation_id": "operation:target",
    }

    with pytest.raises(ValueError, match="non-delegation edge must remain"):
        OperationEdge.issue(
            **common,
            relation="decomposes_to",
            source_frame_id="frame:one",
            target_frame_id="frame:two",
        )
    with pytest.raises(ValueError, match="delegation must cross frames"):
        OperationEdge.issue(
            **common,
            relation="delegates_to",
            source_frame_id="frame:one",
            target_frame_id="frame:one",
            artifact_contract_ref="schema://delegation/v1",
        )
    with pytest.raises(ValueError, match="delegation requires an artifact contract"):
        OperationEdge.issue(
            **common,
            relation="delegates_to",
            source_frame_id="frame:one",
            target_frame_id="frame:two",
        )


def test_tool_budget_exhaustion_is_recorded_before_second_dispatch():
    compiled, catalog, environment_run = _admission_fixture(
        budgets=TaskBudgets(
            wall_time_seconds=90,
            model_calls=1,
            tool_calls=1,
            retry_attempts=0,
        )
    )
    ledger = LifecycleLedger()
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    leases = []
    for operation_id in ("operation:first", "operation:second"):
        proposal = _proposal(compiled, operation_id=operation_id)
        ledger.record(proposal)
        semantic = _semantic_admission(catalog).admit(compiled, proposal)
        assert semantic.admitted_operation is not None
        ledger.record(semantic.admitted_operation)
        lease = DomainLifecycleAdmission(
            environment_run=environment_run,
            environment_id="nao_fake",
            lifecycle_ledger=ledger,
        ).request_execution(semantic.admitted_operation).execution_lease
        assert lease is not None
        leases.append(lease)
    calls = []
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={
            "fake_nao.skills:find_object": lambda arguments: (
                calls.append(arguments)
                or OwnerExecutionResult(
                    evidence_ref="fake-nao://evidence/budget",
                    succeeded=True,
                    observed_effects=("fresh detector-backed result returned",),
                )
            )
        },
    )

    assert owner.execute(leases[0]).accepted
    with pytest.raises(BudgetExhaustedError, match="tool_call"):
        owner.execute(leases[1])

    assert calls == [{"label": "cup"}]
    grant, started = tuple(
        event
        for event in ledger.events()
        if event.operation_id == leases[0].operation_id
        and event.event_type in {"budget_granted", "execution_started"}
    )
    assert (grant.commit_id, grant.commit_size, grant.commit_index) == (
        started.commit_id,
        2,
        1,
    )
    assert started.commit_index == 2
    replay = ledger.replay(compiled.trace_id)
    assert replay.failure_stage == "budget"
    assert replay.terminal_status is None
    assert tuple(event.event_type for event in replay.events)[-1] == "budget_exhausted"


def test_owner_authorized_pre_dispatch_cancellation_blocks_execution():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled, operation_id="operation:cancelled")
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(compiled, proposal, semantic.admitted_operation)
    lease = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(semantic.admitted_operation).execution_lease
    assert lease is not None
    calls = []
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        lifecycle_ledger=ledger,
        handlers={
            "fake_nao.skills:find_object": lambda arguments: calls.append(arguments)
        },
    )

    cancellation = owner.cancel(
        lease,
        requester_id="operator:test",
        request_artifact_id="artifact:cancel:test",
        reason_code="operator_cancelled",
    )

    assert cancellation.outcome == "accepted"
    with pytest.raises(ValueError, match="cancelled"):
        owner.execute(lease)
    assert calls == []
    replay = ledger.replay(compiled.trace_id)
    assert replay.failure_stage == "cancellation"
    assert replay.terminal_status is None


def test_recorded_timeout_replays_without_consulting_current_clock(tmp_path):
    compiled, _catalog, _environment_run = _admission_fixture()
    path = tmp_path / "timeout.jsonl"
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-02T09:00:00Z")
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    authority = TaskRuntimeControlAuthority(ledger)

    decision = authority.evaluate_timeout(
        compiled_task=compiled,
        observed_at="2026-10-02T09:01:31Z",
        policy_revision="timeout-policy:v1",
    )

    assert decision.outcome == "timed_out"
    replay = LifecycleLedger(
        path, clock=lambda: "2099-01-01T00:00:00Z"
    ).replay(compiled.trace_id)
    assert replay.failure_stage == "timeout"
    assert replay.terminal_status is None
    assert replay.events[-1].data["observed_at"] == "2026-10-02T09:01:31Z"


def test_timeout_authority_rejects_tampered_compiled_task_before_record(tmp_path):
    compiled, _catalog, _environment_run = _admission_fixture()
    path = tmp_path / "tampered-timeout-source.jsonl"
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-02T09:00:00Z")
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    before = ledger.events()
    object.__setattr__(compiled, "prohibited_effects", (*compiled.prohibited_effects, "forged"))
    object.__setattr__(compiled, "verify_identity", lambda: None)

    with pytest.raises((TypeError, ValueError), match="compiled task"):
        TaskRuntimeControlAuthority(ledger).evaluate_timeout(
            compiled_task=compiled,
            observed_at="2026-10-02T09:00:30Z",
            policy_revision="timeout-policy:v1",
        )

    assert ledger.events() == before


def test_timeout_check_can_progress_from_within_budget_to_recorded_timeout():
    compiled, _catalog, _environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-10-02T09:00:00Z")
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    authority = TaskRuntimeControlAuthority(ledger)

    within = authority.evaluate_timeout(
        compiled_task=compiled,
        observed_at="2026-10-02T09:00:30Z",
        policy_revision="timeout-policy:v1",
    )
    timed_out = authority.evaluate_timeout(
        compiled_task=compiled,
        observed_at="2026-10-02T09:01:31Z",
        policy_revision="timeout-policy:v1",
    )

    assert within.outcome == "within_budget"
    assert timed_out.outcome == "timed_out"
    assert ledger.replay(compiled.trace_id).failure_stage == "timeout"


def test_timeout_observations_must_progress_monotonically():
    compiled, _catalog, _environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-10-02T09:00:00Z")
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    authority = TaskRuntimeControlAuthority(ledger)
    authority.evaluate_timeout(
        compiled_task=compiled,
        observed_at="2026-10-02T09:00:30Z",
        policy_revision="timeout-policy:v1",
    )

    with pytest.raises(ValueError, match="monotonic"):
        authority.evaluate_timeout(
            compiled_task=compiled,
            observed_at="2026-10-02T09:00:20Z",
            policy_revision="timeout-policy:v1",
        )


def test_retry_exhaustion_is_bounded_by_compiled_task_budget():
    compiled, catalog, environment_run = _admission_fixture(
        budgets=TaskBudgets(
            wall_time_seconds=90,
            model_calls=1,
            tool_calls=2,
            retry_attempts=0,
        )
    )
    proposal = _proposal(compiled, operation_id="operation:failed")
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(compiled, proposal, semantic.admitted_operation)
    lease = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(semantic.admitted_operation).execution_lease
    assert lease is not None
    ledger.start_execution(lease)
    failure = ExecutionFailure.issue(
        lease=lease,
        failure_ref="failure:native:retryable",
        failure_code="temporary_unavailable",
        failure_stage="native_execution",
        retry_disposition="retryable",
    )
    ledger.record(failure)

    retry = RetryAuthority(ledger).decide(
        compiled_task=compiled,
        source_failure=failure,
        target_operation_id="operation:retry-1",
        policy_revision="retry-policy:v1",
    )

    assert retry.outcome == "exhausted"
    replay = ledger.replay(compiled.trace_id)
    assert replay.failure_stage == "retry"
    assert replay.terminal_status is None


def test_retry_authority_rejects_tampered_compiled_budget_before_record():
    compiled, catalog, environment_run = _admission_fixture(
        budgets=TaskBudgets(
            wall_time_seconds=90,
            model_calls=1,
            tool_calls=2,
            retry_attempts=0,
        )
    )
    proposal = _proposal(compiled, operation_id="operation:retry-source")
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(compiled, proposal, semantic.admitted_operation)
    lease = DomainLifecycleAdmission(
        environment_run=environment_run,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(semantic.admitted_operation).execution_lease
    assert lease is not None
    ledger.start_execution(lease)
    failure = ExecutionFailure.issue(
        lease=lease,
        failure_ref="failure:native:retry-budget-tamper",
        failure_code="temporary_unavailable",
        failure_stage="native_execution",
        retry_disposition="retryable",
    )
    ledger.record(failure)
    before = ledger.events()
    object.__setattr__(compiled.budgets, "retry_attempts", 1)
    object.__setattr__(compiled, "verify_identity", lambda: None)

    with pytest.raises(
        (TypeError, ValueError), match="compiled task source fields"
    ):
        RetryAuthority(ledger).decide(
            compiled_task=compiled,
            source_failure=failure,
            target_operation_id="operation:retry-tampered",
            policy_revision="retry-policy:v1",
        )

    assert ledger.events() == before
