from dataclasses import replace

import pytest

from ab_harness import ABControlBand
from ab_harness import AbstractionFrame
from ab_harness import AgentRoleSpec
from ab_harness import DomainContractPack
from ab_harness import DomainEffectRule
from ab_harness import EnvironmentIngress
from ab_harness import EnvironmentRun
from ab_harness import EnvironmentRunAttestation
from ab_harness import EnvironmentTaskRegistry
from ab_harness import RegistrySnapshot
from ab_harness import TaskBudgets
from ab_harness import TaskEffectRequest
from ab_harness import TaskIngressPolicy
from ab_harness import TaskIngressRule
from ab_harness import TaskSpec
from ab_harness import TaskSpecCompiler


def _compiler_inputs():
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
        allowed_role_ids=("planner",),
        supported_task_type_ids=("find_and_report",),
        ingress_rules=(
            TaskIngressRule(
                binding_id="binding:nao.request:v1",
                ingress_type="user_request",
                action="start_task",
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
        ),
        prohibited_effects=("direct_kb_write",),
    )
    task_registry = EnvironmentTaskRegistry()
    environment_run = EnvironmentRun(
        EnvironmentRunAttestation(
            environment_run_id="environment-run:nao:001",
            environment_profile_id="environment-profile:nao:v1",
            domain_contract_pack_revision=domain.revision,
            native_runtime_revision="nao-fixture:v1",
            environment_owner_id="nao_fixture.owner",
            attestation_id="environment-attestation:nao:001",
            started_at="2026-09-28T09:00:00Z",
            readiness_evidence_refs=("artifact:readiness:nao:001",),
        )
    )
    normalized_ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:find-cup:001",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:nao.request:v1",
        ingress_type="user_request",
        payload_artifact_id="artifact:request:find-cup:001",
        native_lineage=(("goal_id", "goal:find-cup:001"),),
        observed_at="2026-09-28T09:00:01Z",
    )
    ingress = TaskIngressPolicy(
        environment_profile_id=environment_run.attestation.environment_profile_id,
        domain_contract_pack=domain,
        task_registry=task_registry,
    ).classify(environment_run, normalized_ingress)
    task = TaskSpec(
        task_id=ingress.task_id,
        trace_id=ingress.trace_id,
        task_type_id="find_and_report",
        role_id="planner",
        frame_id=frame.frame_id,
        domain_contract_pack_revision=domain.revision,
        goal="find the red cup and report the grounded result",
        requested_effects=(
            TaskEffectRequest(
                obligation_id="target_observed",
                effect_id="fresh detector-backed result returned",
                requirement="required",
            ),
        ),
        prohibited_effects=("direct_speech",),
        budgets=TaskBudgets(
            wall_time_seconds=90,
            model_calls=3,
            tool_calls=12,
        ),
    )
    return {
        "task_ingress_decision": ingress,
        "task_spec": task,
        "role": role,
        "frame": frame,
        "registry": registry,
        "domain_contract_pack": domain,
        "task_registry": task_registry,
    }


def _reissue_domain(domain, **changes):
    values = {
        "domain_contract_pack_id": domain.domain_contract_pack_id,
        "frame_id": domain.frame_id,
        "registry_version": domain.registry_version,
        "allowed_role_ids": domain.allowed_role_ids,
        "supported_task_type_ids": domain.supported_task_type_ids,
        "ingress_rules": domain.ingress_rules,
        "effect_rules": domain.effect_rules,
        "prohibited_effects": domain.prohibited_effects,
    }
    values.update(changes)
    return DomainContractPack.issue(**values)


def _use_domain(inputs, domain):
    previous = inputs["task_ingress_decision"]
    environment_run = EnvironmentRun(
        EnvironmentRunAttestation(
            environment_run_id=previous.environment_run_id,
            environment_profile_id="environment-profile:nao:v1",
            domain_contract_pack_revision=domain.revision,
            native_runtime_revision="nao-fixture:v1",
            environment_owner_id="nao_fixture.owner",
            attestation_id="environment-attestation:nao:001",
            started_at="2026-09-28T09:00:00Z",
            readiness_evidence_refs=("artifact:readiness:nao:001",),
        )
    )
    normalized_ingress = EnvironmentIngress(
        environment_ingress_id=previous.environment_ingress_id,
        environment_run_id=previous.environment_run_id,
        binding_id="binding:nao.request:v1",
        ingress_type="user_request",
        payload_artifact_id="artifact:request:find-cup:001",
        native_lineage=(("goal_id", previous.task_id),),
        observed_at="2026-09-28T09:00:01Z",
    )
    task_registry = EnvironmentTaskRegistry()
    ingress = TaskIngressPolicy(
        environment_profile_id=environment_run.attestation.environment_profile_id,
        domain_contract_pack=domain,
        task_registry=task_registry,
    ).classify(environment_run, normalized_ingress)
    inputs["domain_contract_pack"] = domain
    inputs["task_registry"] = task_registry
    inputs["task_ingress_decision"] = ingress
    inputs["task_spec"] = replace(
        inputs["task_spec"],
        domain_contract_pack_revision=domain.revision,
    )


def test_task_spec_compiles_one_frozen_projection_and_obligation_set():
    inputs = _compiler_inputs()

    compiled = TaskSpecCompiler().compile(**inputs)

    assert compiled.task_id == inputs["task_spec"].task_id
    assert compiled.trace_id == inputs["task_spec"].trace_id
    assert (
        compiled.environment_run_id
        == inputs["task_ingress_decision"].environment_run_id
    )
    assert compiled.interaction_module.object_ids == frozenset(
        {"find_object", "resolve_target_reference"}
    )
    assert compiled.effect_obligations[0].object_id == "find_object"
    assert compiled.effect_obligations[0].evidence_owner == "object_finder"
    assert compiled.prohibited_effects == ("direct_kb_write", "direct_speech")
    assert compiled.budgets == inputs["task_spec"].budgets
    assert compiled.compiled_task_id == (
        "compiled-task:sha256:"
        "0e16a007b5d533505bded1f44b7125370c8ea3f0084f9b4c57fb8cc9d0c87af1"
    )


def test_domain_rule_cannot_assign_evidence_to_a_non_owner():
    inputs = _compiler_inputs()
    domain = inputs["domain_contract_pack"]
    _use_domain(
        inputs,
        _reissue_domain(
            domain,
            effect_rules=(
                replace(domain.effect_rules[0], evidence_owner="planner_llm"),
            ),
        ),
    )

    with pytest.raises(ValueError, match="evidence owner does not own AB object"):
        TaskSpecCompiler().compile(**inputs)


def test_domain_rule_effect_must_be_declared_as_owner_observable():
    inputs = _compiler_inputs()
    domain = inputs["domain_contract_pack"]
    changed_domain = _reissue_domain(
        domain,
        effect_rules=(
            replace(domain.effect_rules[0], effect_id="unobservable_success"),
        ),
    )
    _use_domain(inputs, changed_domain)
    inputs["task_spec"] = replace(
        inputs["task_spec"],
        requested_effects=(
            replace(
                inputs["task_spec"].requested_effects[0],
                effect_id="unobservable_success",
            ),
        ),
    )

    with pytest.raises(ValueError, match="effect is not an observable of AB object"):
        TaskSpecCompiler().compile(**inputs)


def test_domain_contract_pack_rejects_ambiguous_effect_rules():
    domain = _compiler_inputs()["domain_contract_pack"]

    with pytest.raises(ValueError, match="duplicate domain effect rules"):
        _reissue_domain(
            domain,
            effect_rules=(domain.effect_rules[0], domain.effect_rules[0]),
        )


def test_domain_contract_pack_rejects_rules_hidden_behind_an_old_revision():
    domain = _compiler_inputs()["domain_contract_pack"]

    with pytest.raises(ValueError, match="revision does not match content"):
        replace(
            domain,
            effect_rules=(replace(domain.effect_rules[0], failure_policy="retryable"),),
        )


def test_task_spec_rejects_duplicate_obligation_identity():
    task = _compiler_inputs()["task_spec"]

    with pytest.raises(ValueError, match="duplicate task obligation IDs"):
        replace(
            task,
            requested_effects=(
                task.requested_effects[0],
                task.requested_effects[0],
            ),
        )


def test_compiled_task_artifact_serializes_without_machine_local_registry_path():
    compiled = TaskSpecCompiler().compile(**_compiler_inputs())

    payload = compiled.to_dict()

    assert payload["schema_version"] == "uah.compiled_task/v1"
    assert payload["compiled_task_id"] == compiled.compiled_task_id
    assert payload["task_spec"]["task_id"] == compiled.task_id
    assert payload["interaction_module"]["object_ids"] == (
        "resolve_target_reference",
        "find_object",
    )
    assert "registry_source" not in payload["interaction_module"]


def test_compiled_task_rejects_an_identity_that_does_not_match_its_content():
    compiled = TaskSpecCompiler().compile(**_compiler_inputs())

    with pytest.raises(ValueError, match="compiled task identity does not match"):
        replace(compiled, compiled_task_id="compiled-task:sha256:tampered")


def test_compiler_rejects_domain_revision_not_admitted_at_task_ingress():
    inputs = _compiler_inputs()
    inputs["task_ingress_decision"] = replace(
        inputs["task_ingress_decision"],
        domain_contract_pack_revision="sha256:another-domain-pack",
    )

    with pytest.raises(ValueError, match="ingress domain contract revision"):
        TaskSpecCompiler().compile(**inputs)


def test_compiler_rejects_recompilation_from_resume_ingress():
    inputs = _compiler_inputs()
    inputs["task_ingress_decision"] = replace(
        inputs["task_ingress_decision"],
        action="resume_task",
        reason_code="matched_registered_task",
    )

    with pytest.raises(ValueError, match="requires accepted start_task ingress"):
        TaskSpecCompiler().compile(**inputs)


def test_compiler_rejects_a_matched_decision_without_recorded_start_authority():
    inputs = _compiler_inputs()
    inputs["task_registry"] = EnvironmentTaskRegistry()

    with pytest.raises(ValueError, match="not recorded in lifecycle ledger"):
        TaskSpecCompiler().compile(**inputs)


def test_compiler_rejects_an_effect_that_the_task_also_prohibits():
    inputs = _compiler_inputs()
    task = inputs["task_spec"]
    inputs["task_spec"] = replace(
        task,
        prohibited_effects=task.prohibited_effects
        + (task.requested_effects[0].effect_id,),
    )

    with pytest.raises(ValueError, match="requested effects are prohibited"):
        TaskSpecCompiler().compile(**inputs)


def test_task_spec_rejects_mutable_effect_and_policy_collections():
    task = _compiler_inputs()["task_spec"]

    with pytest.raises(TypeError, match="task spec collections must be tuples"):
        replace(task, requested_effects=list(task.requested_effects))


def test_domain_contract_pack_rejects_mutable_rule_collections():
    domain = _compiler_inputs()["domain_contract_pack"]

    with pytest.raises(TypeError, match="domain contract collections must be tuples"):
        replace(domain, effect_rules=list(domain.effect_rules))


def test_compiled_task_rejects_mutable_compiled_collections():
    compiled = TaskSpecCompiler().compile(**_compiler_inputs())

    with pytest.raises(TypeError, match="compiled task collections must be tuples"):
        replace(compiled, effect_obligations=list(compiled.effect_obligations))


def test_compiler_preserves_required_and_best_effort_effect_requirements():
    inputs = _compiler_inputs()
    domain = inputs["domain_contract_pack"]
    changed_domain = _reissue_domain(
        domain,
        effect_rules=domain.effect_rules
        + (
            DomainEffectRule(
                effect_id="one terminal result event emitted",
                object_id="report_result",
                evidence_owner="dialogue_runtime",
                failure_policy="terminal",
            ),
        ),
    )
    _use_domain(inputs, changed_domain)
    inputs["task_spec"] = replace(
        inputs["task_spec"],
        requested_effects=inputs["task_spec"].requested_effects
        + (
            TaskEffectRequest(
                obligation_id="report_delivered",
                effect_id="one terminal result event emitted",
                requirement="best_effort",
            ),
        ),
    )

    compiled = TaskSpecCompiler().compile(**inputs)

    assert tuple(
        obligation.requirement for obligation in compiled.effect_obligations
    ) == ("required", "best_effort")
