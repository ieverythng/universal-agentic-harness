"""Deterministic NAO adapter canary with no live model or ROS runtime."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace

from ab_harness.bindings import BindingCatalog
from ab_harness.configuration import ConfigurationIdentity
from ab_harness.contracts import ABImplementationBinding, ABObjectView
from ab_harness.contracts import OwnerExecutionResult
from ab_harness.environment import InProcessEnvironmentOwner
from ab_harness.environment_ingress import EnvironmentIngress
from ab_harness.environment_profiles import EnvironmentProfile
from ab_harness.environment_profiles import EnvironmentProfileRegistry
from ab_harness.environment_runs import EnvironmentRunAttestation
from ab_harness.environment_runs import EnvironmentRunRegistry
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.registry import RegistrySnapshot
from ab_harness.task_compiler import TaskBudgets
from ab_harness.task_compiler import TaskEffectRequest
from ab_harness_nao.qualification import NaoQualificationCase
from ab_harness_nao.qualification import RecordedNaoQualificationHarness
from ab_harness_nao.qualification import nao_qualification_domain_contract_pack


CHATBOT_HANDOFF = {
    "route": "execution",
    "verbal_ack": "I will look for the cup.",
    "user_intent": {"type": "find_object", "goal_text": "find the cup"},
}
PLANNER_FIND = {
    "plan": {
        "steps": [
            {
                "id": "step_1",
                "type": "skill",
                "name": "find_object",
                "args": {"label": "cup"},
            }
        ]
    }
}
PLANNER_OUT_OF_SCOPE = {
    "plan": {
        "steps": [{"id": "step_1", "type": "skill", "name": "walk_to", "args": {}}]
    }
}


def run_smoke() -> dict[str, object]:
    registry = _registry()
    binding = ABImplementationBinding(
        binding_id="nao_fake.find_object.v1",
        object_id="find_object",
        environment_id="nao_fake",
        implementation_owner="object_finder",
        interface_kind="python_method",
        locator="ab_harness_nao.smoke:find_object",
        source_revision="uah-smoke-v1",
        input_schema_ref="schema://find_object/input/v1",
        output_schema_ref="schema://find_object/result/v1",
        evidence_adapter="ab_harness_nao.smoke:fresh_detection",
        runtime_modes=("smoke",),
        status="approved",
    )
    catalog = BindingCatalog(registry, (binding,))
    domain_pack = nao_qualification_domain_contract_pack(registry)
    profile = EnvironmentProfile(
        environment_profile_id="environment-profile:nao-smoke:v1",
        domain_contract_pack_id="domain-pack:nao-recorded-qualification:v1",
        domain_contract_pack_revision=domain_pack.revision,
        native_runtime_revision="nao-smoke-runtime:v1",
        environment_owner_id="nao_fake.lifecycle_owner",
        required_interface_ids=("find_object",),
    )
    environment_run = EnvironmentRunRegistry(
        EnvironmentProfileRegistry((profile,))
    ).register(
        EnvironmentRunAttestation(
            environment_run_id="environment-run:nao-smoke:001",
            environment_profile_id=profile.environment_profile_id,
            domain_contract_pack_revision=profile.domain_contract_pack_revision,
            native_runtime_revision=profile.native_runtime_revision,
            environment_owner_id=profile.environment_owner_id,
            attestation_id="environment-attestation:nao-smoke:001",
            started_at="2026-09-28T10:00:00Z",
            readiness_evidence_refs=("artifact:nao-smoke-readiness:001",),
        )
    )
    lifecycle_ledger = LifecycleLedger(clock=lambda: "2026-09-28T10:00:01Z")
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        handlers={binding.locator: _find_object},
        lifecycle_ledger=lifecycle_ledger,
    )
    harness = RecordedNaoQualificationHarness(
        registry,
        catalog,
        environment_run,
        owner,
        lifecycle_ledger,
        domain_pack,
    )
    case = NaoQualificationCase(
        case_id="uah-smoke-find-cup",
        task_id="find_the_cup",
        requested_effects=(
            TaskEffectRequest(
                obligation_id="target_observed",
                effect_id="fresh detector-backed result returned",
                requirement="required",
            ),
        ),
        goal="find the cup",
        budgets=TaskBudgets(wall_time_seconds=60, model_calls=0, tool_calls=4),
    )
    accepted = harness.run(
        case=case,
        ingress=_ingress(environment_run.environment_run_id, case),
        chatbot_payload=CHATBOT_HANDOFF,
        planner_payload=PLANNER_FIND,
        runtime_mode="smoke",
    )
    rejected_case = replace(
        case,
        case_id="uah-smoke-find-cup-rejected",
        task_id="find_the_cup_rejected",
    )
    rejected = harness.run(
        case=rejected_case,
        ingress=_ingress(environment_run.environment_run_id, rejected_case),
        chatbot_payload=CHATBOT_HANDOFF,
        planner_payload=PLANNER_OUT_OF_SCOPE,
        runtime_mode="smoke",
    )
    configuration = _configuration(registry.version)
    accepted_trace_id = next(
        event.trace_id
        for event in lifecycle_ledger.events()
        if event.event_type == "task_started" and event.task_id == case.task_id
    )
    accepted_replay = lifecycle_ledger.replay(accepted_trace_id)
    checks = {
        "accepted_path": accepted.passed,
        "rejected_path": rejected.failure_stage == "semantic_admission",
        "verified_trace_digest": accepted_replay.verified_trace_digest is not None,
    }
    return {
        "status": "passed" if all(checks.values()) else "failed",
        "configuration": configuration.to_dict(),
        "checks": checks,
        "accepted_case": {
            "passed": accepted.passed,
            "evidence_owner": accepted.evidence[0].owner if accepted.evidence else None,
            "closed_observables": list(accepted.closed_observables),
        },
        "rejected_case": {
            "passed": rejected.passed,
            "failure_stage": rejected.failure_stage,
            "reasons": list(rejected.planner_reasons),
        },
        "verified_trace_digest": (
            accepted_replay.verified_trace_digest.digest_id
            if accepted_replay.verified_trace_digest is not None
            else None
        ),
    }


def _registry() -> RegistrySnapshot:
    objects = (
        ABObjectView(
            object_id="resolve_target_reference",
            ab_level=0,
            kind="effect_primitive",
            category="grounding",
            owner_package="scene_grounding",
            observable_success=("canonical target id returned",),
        ),
        ABObjectView(
            object_id="find_object",
            ab_level=1,
            kind="skill",
            category="perception",
            owner_package="object_finder",
            expected_effects=("requested object localized",),
            observable_success=("fresh detector-backed result returned",),
            decomposes_to=("resolve_target_reference",),
            runtime_callable=True,
        ),
    )
    payload = [item.__dict__ for item in objects]
    version = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("utf-8")
        ).hexdigest()
    )
    return RegistrySnapshot(objects, source="builtin:nao-smoke-v1", version=version)


def _configuration(registry_version: str) -> ConfigurationIdentity:
    return ConfigurationIdentity(
        model_id="recorded-fixture",
        model_revision="fixture-v1",
        model_format="recorded-json",
        runtime_id="ab_harness.recorded",
        runtime_revision="0.1.0",
        runtime_parameters=(("mode", "deterministic"),),
        harness_version="0.1.0",
        adapter_version="nao-shadow-v1",
        prompt_hash="sha256:none",
        registry_version=registry_version,
        environment_id="nao_fake",
        environment_revision="uah-smoke-v1",
        task_suite_version="uah-smoke-v1",
        evaluator_version="owner-evidence-v1",
    )


def _find_object(arguments: dict[str, object]) -> OwnerExecutionResult:
    return OwnerExecutionResult(
        evidence_ref="builtin://uah-smoke/detection-001",
        succeeded=arguments.get("label") == "cup",
        observed_effects=("fresh detector-backed result returned",),
        payload={"canonical_target_id": "cup_01"},
    )


def _ingress(environment_run_id: str, case: NaoQualificationCase) -> EnvironmentIngress:
    return EnvironmentIngress(
        environment_ingress_id="ingress:recorded:%s" % case.case_id,
        environment_run_id=environment_run_id,
        binding_id="binding:nao.recorded_qualification:v1",
        ingress_type="recorded_user_request",
        payload_artifact_id="artifact:recorded-request:%s" % case.case_id,
        native_lineage=(("task_id", case.task_id),),
        observed_at="2026-09-28T10:00:01Z",
    )
