"""Deterministic UAH v0 smoke qualification with no live model or ROS runtime."""

from __future__ import annotations

import hashlib
import json

from ab_harness.bindings import BindingCatalog
from ab_harness.configuration import ConfigurationIdentity
from ab_harness.contracts import ABImplementationBinding, ABObjectView
from ab_harness.contracts import OwnerExecutionResult
from ab_harness.environment import InProcessEnvironmentOwner
from ab_harness.qualification import QualificationCase
from ab_harness.qualification import RecordedNaoQualificationHarness
from ab_harness.registry import RegistrySnapshot
from ab_harness.workbench import TraceExperience, WorkbenchMemory


CHATBOT_HANDOFF = {
    'route': 'execution',
    'verbal_ack': 'I will look for the cup.',
    'user_intent': {'type': 'find_object', 'goal_text': 'find the cup'},
}
PLANNER_FIND = {
    'plan': {
        'steps': [
            {
                'id': 'step_1',
                'type': 'skill',
                'name': 'find_object',
                'args': {'label': 'cup'},
            }
        ]
    }
}
PLANNER_OUT_OF_SCOPE = {
    'plan': {
        'steps': [
            {'id': 'step_1', 'type': 'skill', 'name': 'walk_to', 'args': {}}
        ]
    }
}


def run_smoke() -> dict[str, object]:
    registry = _registry()
    binding = ABImplementationBinding(
        binding_id='nao_fake.find_object.v1',
        object_id='find_object',
        environment_id='nao_fake',
        implementation_owner='object_finder',
        interface_kind='python_method',
        locator='ab_harness.smoke:find_object',
        source_revision='uah-smoke-v1',
        input_schema_ref='schema://find_object/input/v1',
        output_schema_ref='schema://find_object/result/v1',
        evidence_adapter='ab_harness.smoke:fresh_detection',
        runtime_modes=('smoke',),
        status='approved',
    )
    owner = InProcessEnvironmentOwner(
        environment_id='nao_fake',
        catalog=BindingCatalog(registry, (binding,)),
        handlers={binding.locator: _find_object},
    )
    harness = RecordedNaoQualificationHarness(registry, owner)
    case = QualificationCase(
        case_id='uah-smoke-find-cup',
        task_id='find_the_cup',
        requested_object_ids=('find_object',),
        required_observables=('fresh detector-backed result returned',),
    )
    accepted = harness.run(
        case=case,
        chatbot_payload=CHATBOT_HANDOFF,
        planner_payload=PLANNER_FIND,
        runtime_mode='smoke',
    )
    rejected = harness.run(
        case=case,
        chatbot_payload=CHATBOT_HANDOFF,
        planner_payload=PLANNER_OUT_OF_SCOPE,
        runtime_mode='smoke',
    )
    configuration = _configuration(registry.version)
    memory = WorkbenchMemory(
        (
            _experience(
                trace_id='smoke-accepted',
                result=accepted,
                case=case,
                configuration=configuration,
                registry=registry,
            ),
            _experience(
                trace_id='smoke-rejected',
                result=rejected,
                case=case,
                configuration=configuration,
                registry=registry,
            ),
        )
    )
    candidate = memory.propose_context(query_object_ids=('find_object',))
    checks = {
        'accepted_path': accepted.passed,
        'rejected_path': rejected.failure_stage == 'planner_gate',
        'workbench_support_retrieved': bool(candidate.supporting),
        'workbench_counterexample_retrieved': bool(candidate.counterexamples),
    }
    return {
        'status': 'passed' if all(checks.values()) else 'failed',
        'configuration': configuration.to_dict(),
        'checks': checks,
        'accepted_case': {
            'passed': accepted.passed,
            'evidence_owner': accepted.evidence[0].owner if accepted.evidence else None,
            'closed_observables': list(accepted.closed_observables),
        },
        'rejected_case': {
            'passed': rejected.passed,
            'failure_stage': rejected.failure_stage,
            'reasons': list(rejected.planner_gate.reasons),
        },
        'workbench_candidate': candidate.to_context_payload(),
    }


def _registry() -> RegistrySnapshot:
    objects = (
        ABObjectView(
            object_id='resolve_target_reference',
            ab_level=0,
            kind='effect_primitive',
            category='grounding',
            owner_package='scene_grounding',
            observable_success=('canonical target id returned',),
        ),
        ABObjectView(
            object_id='find_object',
            ab_level=1,
            kind='skill',
            category='perception',
            owner_package='object_finder',
            expected_effects=('requested object localized',),
            observable_success=('fresh detector-backed result returned',),
            decomposes_to=('resolve_target_reference',),
            runtime_callable=True,
        ),
    )
    payload = [item.__dict__ for item in objects]
    version = 'sha256:' + hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode('utf-8')
    ).hexdigest()
    return RegistrySnapshot(objects, source='builtin:nao-smoke-v1', version=version)


def _configuration(registry_version: str) -> ConfigurationIdentity:
    return ConfigurationIdentity(
        model_id='recorded-fixture',
        model_revision='fixture-v1',
        model_format='recorded-json',
        runtime_id='ab_harness.recorded',
        runtime_revision='0.1.0',
        runtime_parameters=(('mode', 'deterministic'),),
        harness_version='0.1.0',
        adapter_version='nao-shadow-v1',
        prompt_hash='sha256:none',
        registry_version=registry_version,
        environment_id='nao_fake',
        environment_revision='uah-smoke-v1',
        task_suite_version='uah-smoke-v1',
        evaluator_version='owner-evidence-v1',
    )


def _find_object(arguments: dict[str, object]) -> OwnerExecutionResult:
    return OwnerExecutionResult(
        evidence_ref='builtin://uah-smoke/detection-001',
        succeeded=arguments.get('label') == 'cup',
        observed_effects=('fresh detector-backed result returned',),
        payload={'canonical_target_id': 'cup_01'},
    )


def _experience(
    *,
    trace_id: str,
    result,
    case: QualificationCase,
    configuration: ConfigurationIdentity,
    registry: RegistrySnapshot,
) -> TraceExperience:
    return TraceExperience(
        trace_id=trace_id,
        task_id=case.task_id,
        configuration_id=configuration.configuration_id,
        registry_version=registry.version,
        object_ids=case.requested_object_ids,
        outcome='success' if result.passed else 'failure',
        failure_stage=result.failure_stage,
        evidence_refs=tuple(item.evidence_ref for item in result.evidence),
    )
