from dataclasses import replace

import pytest

from ab_harness.bindings import BindingCatalog
from ab_harness.contracts import ABControlBand
from ab_harness.contracts import ABImplementationBinding
from ab_harness.contracts import ABObjectView
from ab_harness.contracts import AbstractionFrame
from ab_harness.contracts import AgentOutput
from ab_harness.contracts import AgentRoleSpec
from ab_harness.domain_contracts import DomainContractPack
from ab_harness.domain_contracts import DomainEffectRule
from ab_harness.domain_contracts import TaskIngressRule
from ab_harness.environment_ingress import EnvironmentIngress
from ab_harness.environment_runs import EnvironmentRun
from ab_harness.environment_runs import EnvironmentRunAttestation
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.proposal_admission import ProposalNormalizer
from ab_harness.proposal_admission import SemanticAdmission
from ab_harness.registry import RegistrySnapshot
from ab_harness.schema_validation import ArgumentField
from ab_harness.schema_validation import InMemoryArgumentSchemaRegistry
from ab_harness.schema_validation import ObjectArgumentSchema
from ab_harness.task_compiler import TaskBudgets
from ab_harness.task_compiler import TaskEffectRequest
from ab_harness.task_compiler import TaskSpec
from ab_harness.task_compiler import TaskSpecCompiler
from ab_harness.task_ingress_authority import TaskIngressAuthority
from ab_harness.task_registry import EnvironmentTaskRegistry


SCHEMA_REF = "schema://find_object/input/v1"


def _semantic_admission_case(arguments, *, register_schema=True):
    registry = RegistrySnapshot(
        (
            ABObjectView(
                object_id="find_object",
                ab_level=1,
                kind="skill",
                category="perception",
                owner_package="object_finder",
                expected_effects=("target observed",),
                observable_success=("target observed",),
                runtime_callable=True,
            ),
        ),
        source="test:argument-schema-validation",
        version="registry:argument-schema-validation:v1",
    )
    role = AgentRoleSpec(
        role_id="planner",
        allowed_output_types=("executable_plan",),
        control_band=ABControlBand(1, 1, 1),
    )
    frame = AbstractionFrame(
        frame_id="test_runtime",
        substrate="typed test runtime",
        atomicity_rule="AB1 objects are callable skills",
        registry_version=registry.version,
    )
    domain = DomainContractPack.issue(
        domain_contract_pack_id="domain-pack:test:argument-schema:v1",
        frame_id=frame.frame_id,
        registry_version=registry.version,
        allowed_role_ids=(role.role_id,),
        supported_task_type_ids=("find_and_report",),
        ingress_rules=(
            TaskIngressRule(
                binding_id="binding:test.request:v1",
                ingress_type="user_request",
                action="start_task",
                task_id_lineage_key="goal_id",
            ),
        ),
        effect_rules=(
            DomainEffectRule(
                effect_id="target observed",
                object_id="find_object",
                evidence_owner="object_finder",
                failure_policy="terminal",
            ),
        ),
    )
    run = EnvironmentRun(
        EnvironmentRunAttestation(
            environment_run_id="environment-run:test:argument-schema",
            environment_profile_id="environment-profile:test:argument-schema:v1",
            domain_contract_pack_revision=domain.revision,
            native_runtime_revision="test-runtime:v1",
            environment_owner_id="test.owner",
            attestation_id="attestation:test:argument-schema",
            started_at="2026-10-01T09:00:00Z",
            readiness_evidence_refs=("artifact:readiness:test",),
        )
    )
    ledger = LifecycleLedger()
    task_registry = EnvironmentTaskRegistry(ledger)
    ingress = TaskIngressAuthority(
        environment_profile_id=run.attestation.environment_profile_id,
        domain_contract_pack=domain,
        lifecycle_ledger=ledger,
    ).admit(
        run,
        EnvironmentIngress(
            environment_ingress_id="environment-ingress:test:argument-schema",
            environment_run_id=run.environment_run_id,
            binding_id="binding:test.request:v1",
            ingress_type="user_request",
            payload_artifact_id="artifact:request:test:argument-schema",
            native_lineage=(("goal_id", "goal:test:argument-schema"),),
            observed_at="2026-10-01T09:00:01Z",
        ),
    )
    task = TaskSpec(
        task_id=ingress.task_id,
        trace_id=ingress.trace_id,
        task_type_id="find_and_report",
        role_id=role.role_id,
        frame_id=frame.frame_id,
        domain_contract_pack_revision=domain.revision,
        goal="find a cup",
        requested_effects=(
            TaskEffectRequest(
                obligation_id="target_observed",
                effect_id="target observed",
                requirement="required",
            ),
        ),
        prohibited_effects=(),
        budgets=TaskBudgets(wall_time_seconds=30, model_calls=1, tool_calls=1),
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
        binding_id="binding:test.find_object:v1",
        object_id="find_object",
        environment_id="test",
        implementation_owner="object_finder",
        interface_kind="python_method",
        locator="test_runtime:find_object",
        source_revision="test-runtime:7d91",
        input_schema_ref=SCHEMA_REF,
        output_schema_ref="schema://find_object/output/v1",
        evidence_adapter="test_runtime:evidence",
        runtime_modes=("test",),
        status="approved",
    )
    normalization = ProposalNormalizer().normalize(
        compiled_task=compiled,
        operation_id="operation:test:argument-schema",
        raw_output_artifact_id="artifact:model-output:test:argument-schema",
        output=AgentOutput(
            output_type="executable_plan",
            payload={"object_id": "find_object", "arguments": arguments},
            referenced_objects=("find_object",),
        ),
    )
    assert normalization.proposal is not None
    schema = ObjectArgumentSchema.issue(
        schema_ref=SCHEMA_REF,
        fields=(ArgumentField(name="label", value_type="string"),),
        required=("label",),
    )
    admission = SemanticAdmission(
        catalog=BindingCatalog(registry, (binding,)),
        environment_id="test",
        runtime_mode="test",
        schema_validator=InMemoryArgumentSchemaRegistry(
            (schema,) if register_schema else ()
        ),
    )
    return admission, compiled, normalization.proposal, schema


def test_in_memory_registry_validates_a_content_addressed_object_schema():
    schema = ObjectArgumentSchema.issue(
        schema_ref="schema://find_object/input/v1",
        fields=(ArgumentField(name="label", value_type="string"),),
        required=("label",),
        allow_additional_properties=False,
    )
    registry = InMemoryArgumentSchemaRegistry((schema,))

    assert schema.schema_id == (
        "input-schema:sha256:"
        "5b9e04eb5d392aad4f5e4cdfc8f722963f228a99b60437b88f5a48b46e467ccc"
    )

    accepted = registry.validate_arguments(
        schema_ref=schema.schema_ref,
        arguments={"label": "cup"},
    )
    rejected = registry.validate_arguments(
        schema_ref=schema.schema_ref,
        arguments={"label": 7, "unreviewed": True},
    )
    missing = registry.validate_arguments(
        schema_ref=schema.schema_ref,
        arguments={},
    )

    assert accepted.accepted
    assert accepted.schema_id == schema.schema_id
    assert rejected.violations == (
        "unexpected_property:unreviewed",
        "invalid_type:label:expected_string",
    )
    assert missing.violations == ("missing_required_property:label",)


def test_in_memory_registry_rejects_a_tampered_schema_identity():
    schema = ObjectArgumentSchema.issue(
        schema_ref="schema://find_object/input/v1",
        fields=(ArgumentField(name="label", value_type="string"),),
        required=("label",),
    )

    with pytest.raises(ValueError, match="schema identity does not match content"):
        InMemoryArgumentSchemaRegistry(
            (replace(schema, schema_id="input-schema:sha256:forged"),)
        )


def test_object_schema_identity_is_independent_of_field_order():
    first = ObjectArgumentSchema.issue(
        schema_ref="schema://ordered/input/v1",
        fields=(ArgumentField("count", "integer"), ArgumentField("label", "string")),
        required=("label", "count"),
    )
    reordered = ObjectArgumentSchema.issue(
        schema_ref="schema://ordered/input/v1",
        fields=tuple(reversed(first.fields)),
        required=tuple(reversed(first.required)),
    )

    assert reordered.schema_id == first.schema_id
    assert reordered.fields == first.fields
    assert reordered.required == first.required


def test_validators_report_an_unregistered_schema_without_accepting_arguments():
    validator = InMemoryArgumentSchemaRegistry(())

    result = validator.validate_arguments(
        schema_ref="schema://missing/input/v1",
        arguments={"label": "cup"},
    )

    assert not result.accepted
    assert result.schema_id is None
    assert result.violations == ("schema_not_registered",)


def test_semantic_admission_rejects_arguments_that_do_not_match_the_binding_schema():
    admission, compiled, proposal, _schema = _semantic_admission_case({"label": 7})

    decision = admission.admit(compiled, proposal)

    assert decision.admitted_operation is None
    assert decision.reason_codes == ("proposal_arguments_schema_invalid",)


def test_semantic_admission_rejects_an_unresolved_binding_schema():
    admission, compiled, proposal, _schema = _semantic_admission_case(
        {"label": "cup"},
        register_schema=False,
    )

    decision = admission.admit(compiled, proposal)

    assert decision.admitted_operation is None
    assert decision.reason_codes == ("input_schema_unavailable",)


def test_admitted_operation_pins_the_validated_input_schema_identity():
    admission, compiled, proposal, schema = _semantic_admission_case({"label": "cup"})

    decision = admission.admit(compiled, proposal)

    assert decision.admitted_operation is not None
    assert decision.admitted_operation.schema_version == "uah.admitted_operation/v3"
    assert decision.admitted_operation.input_schema_ref == schema.schema_ref
    assert decision.admitted_operation.input_schema_id == schema.schema_id
