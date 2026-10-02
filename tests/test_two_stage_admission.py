from dataclasses import replace
import hashlib
import inspect
import json

import pytest

from ab_harness import ABControlBand
from ab_harness import ABImplementationBinding
from ab_harness import AbstractionFrame
from ab_harness import AgentOutput
from ab_harness import AgentRoleSpec
from ab_harness import BindingCatalog
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
from ab_harness.environment import InProcessEnvironmentOwner
from ab_harness.contracts import OwnerExecutionResult
from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.lifecycle import AcceptanceFact
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.lifecycle import TaskStartedFact
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


def _admission_fixture(*, include_best_effort=False, budgets=None):
    registry = RegistrySnapshot.from_json_file("tests/fixtures/ab_registry.json")
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
        prohibited_effects=("direct_speech",),
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


def _task_start(compiled):
    return TaskStartedFact(
        environment_run_id=compiled.environment_run_id,
        task_id=compiled.task_id,
        trace_id=compiled.trace_id,
        environment_ingress_id=compiled.environment_ingress_id,
        ingress_artifact_id="artifact:ingress:%s" % compiled.environment_ingress_id,
        decision_id="decision:start:%s" % compiled.environment_ingress_id,
        domain_contract_pack_revision=compiled.domain_contract_pack_revision,
    )


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
    ledger.record(_task_start(compiled))
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
    ledger.record(_task_start(compiled))
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
    ledger.record(_task_start(compiled))
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


def test_semantic_rejection_is_a_replayable_typed_fact(tmp_path):
    compiled, catalog, _environment_run = _admission_fixture()
    proposal = _proposal(
        compiled,
        object_id="resolve_target_reference",
        operation_id="operation:semantic-rejected",
    )
    path = tmp_path / "semantic-rejection.jsonl"
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-01T09:00:00Z")
    ledger.record(_task_start(compiled))
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
    ledger.record(_task_start(compiled))
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
    ledger.record(_task_start(compiled))
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


def test_environment_owner_records_typed_evidence_rejection():
    compiled, catalog, environment_run = _admission_fixture()
    proposal = _proposal(compiled, operation_id="operation:evidence-rejected")
    semantic = _semantic_admission(catalog).admit(compiled, proposal)
    assert semantic.admitted_operation is not None
    ledger = _ledger_for_admission(compiled, proposal, semantic.admitted_operation)
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
    writer.record(_task_start(compiled))
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


def test_terminal_required_effect_failure_replays_as_counterexample_digest(tmp_path):
    compiled, catalog, environment_run = _admission_fixture()
    path = tmp_path / "terminal-counterexample.jsonl"
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-02T09:20:00Z")
    ledger.record(_task_start(compiled))
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


def test_common_ledger_records_pre_dispatch_suspension():
    compiled, _catalog, _environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-09-28T12:07:00Z")
    ledger.record(_task_start(compiled))
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
    ledger.record(_task_start(compiled))
    ledger.record(compiled)

    with pytest.raises(ValueError, match="already has a compiled task"):
        ledger.record(compiled)


def test_common_ledger_rejects_a_proposal_from_an_unrecorded_compiled_task():
    compiled, _catalog, _environment_run = _admission_fixture()
    alternate = _alternate_compiled_task(compiled)
    ledger = LifecycleLedger(clock=lambda: "2026-09-28T12:25:00Z")
    ledger.record(_task_start(compiled))
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
    ledger.record(_task_start(compiled))
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
    ledger.record(_task_start(compiled))
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
    ledger.record(_task_start(compiled))
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
    ledger.record(_task_start(compiled))
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


def test_timeout_check_can_progress_from_within_budget_to_recorded_timeout():
    compiled, _catalog, _environment_run = _admission_fixture()
    ledger = LifecycleLedger(clock=lambda: "2026-10-02T09:00:00Z")
    ledger.record(_task_start(compiled))
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
