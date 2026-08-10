"""Read-only NAO H0 role contracts and output adapters."""

from __future__ import annotations

from ab_harness.contracts import ABControlBand
from ab_harness.contracts import ABImplementationBinding
from ab_harness.contracts import AbstractionFrame
from ab_harness.contracts import AgentOutput
from ab_harness.contracts import AgentRoleSpec
from ab_harness.registry import RegistrySnapshot


CHATBOT_ROLE = AgentRoleSpec(
    role_id='chatbot_llm',
    allowed_output_types=('dialogue_response', 'knowledge_query', 'planner_handoff'),
    control_band=ABControlBand(1, 1, 2, inspect_down_to_level=0),
    may_claim_effects=False,
)
PLANNER_ROLE = AgentRoleSpec(
    role_id='planner_llm',
    allowed_output_types=('executable_plan', 'supervision_decision', 'planner_dialogue_act'),
    control_band=ABControlBand(1, 1, 2, inspect_down_to_level=0),
    may_claim_effects=False,
)


def nao_contract_bindings(
    *,
    chatbot_revision: str,
    stack_revision: str,
) -> tuple[ABImplementationBinding, ...]:
    """Declare inspected NAO API seams as quarantined AB0 binding candidates."""

    shared = {
        'environment_id': 'nao_ros4hri',
        'runtime_modes': ('shadow', 'cooperative'),
        'status': 'candidate',
    }
    return (
        ABImplementationBinding(
            binding_id='nao.chatbot.planner_gate_request.publisher.v1',
            object_id='/nao_orchestrator/planner_request',
            implementation_owner='chatbot_llm',
            interface_kind='python_function',
            locator=(
                'chatbot_llm.planner_request_adapter:'
                'build_planner_request_payload'
            ),
            source_revision=chatbot_revision,
            input_schema_ref='python://chatbot_llm/turn',
            output_schema_ref='python://planner_common/PlannerRequest',
            evidence_adapter='shadow://planner_gate_request/publication',
            **shared,
        ),
        ABImplementationBinding(
            binding_id='nao.planner_gate.admission.v1',
            object_id='/planner/request',
            implementation_owner='nao_orchestrator',
            interface_kind='python_method',
            locator='nao_orchestrator.planner_gate:PlannerGate.decide',
            source_revision=stack_revision,
            input_schema_ref='python://planner_common/PlannerRequest',
            output_schema_ref='python://nao_orchestrator/PlannerGateDecision',
            evidence_adapter='shadow://planner_gate/decision',
            **shared,
        ),
        ABImplementationBinding(
            binding_id='nao.planner_request.contract.v1',
            object_id='/planner/request',
            implementation_owner='planner_common',
            interface_kind='python_type',
            locator='planner_common.contracts:PlannerRequest',
            source_revision=stack_revision,
            input_schema_ref='ros://hri_actions_msgs/msg/Intent',
            output_schema_ref='python://planner_common/PlannerRequest',
            evidence_adapter='shadow://planner_request/normalization',
            **shared,
        ),
        ABImplementationBinding(
            binding_id='nao.planner_output.publisher.v1',
            object_id='/intents',
            implementation_owner='planner_llm',
            interface_kind='python_method',
            locator='planner_llm.planner_node:PlannerNode._publish_decision',
            source_revision=stack_revision,
            input_schema_ref='python://planner_llm/PlannerDecision',
            output_schema_ref='ros://hri_actions_msgs/msg/Intent',
            evidence_adapter='shadow://planner_output/publication',
            **shared,
        ),
        ABImplementationBinding(
            binding_id='nao.execution_feedback.contract.v1',
            object_id='/planner/execution_feedback',
            implementation_owner='planner_common',
            interface_kind='python_type',
            locator='planner_common.contracts:ExecutionFeedback',
            source_revision=stack_revision,
            input_schema_ref='ros://std_msgs/msg/String',
            output_schema_ref='python://planner_common/ExecutionFeedback',
            evidence_adapter='shadow://execution_feedback/normalization',
            **shared,
        ),
        ABImplementationBinding(
            binding_id='nao.planner_dialogue_act.contract.v1',
            object_id='/planner/dialogue_act',
            implementation_owner='planner_common',
            interface_kind='python_type',
            locator='planner_common.contracts:PlannerDialogueAct',
            source_revision=stack_revision,
            input_schema_ref='python://planner_common/PlannerDialogueAct',
            output_schema_ref='ros://std_msgs/msg/String',
            evidence_adapter='shadow://planner_dialogue_act/normalization',
            **shared,
        ),
        ABImplementationBinding(
            binding_id='nao.scene_summary.contract.v1',
            object_id='/scene/summary',
            implementation_owner='planner_common',
            interface_kind='python_type',
            locator='planner_common.contracts:SceneSummary',
            source_revision=stack_revision,
            input_schema_ref='ros://std_msgs/msg/String',
            output_schema_ref='python://planner_common/SceneSummary',
            evidence_adapter='shadow://scene_summary/normalization',
            **shared,
        ),
    )


def nao_frame(registry: RegistrySnapshot) -> AbstractionFrame:
    return AbstractionFrame(
        frame_id='nao_ros4hri',
        substrate='ROS4HRI planner and deterministic skill runtime',
        atomicity_rule='AB1 is planner-callable skill; AB0 is inspectable effect decomposition',
        registry_version=registry.version,
    )


def planner_output(payload: dict) -> AgentOutput:
    plan = payload.get('plan', {}) if isinstance(payload.get('plan'), dict) else {}
    references = []
    for step in plan.get('steps', ()):
        if isinstance(step, dict) and step.get('type') == 'skill':
            name = str(step.get('name', '')).strip()
            if name:
                references.append(name)
    return AgentOutput('executable_plan', dict(payload), tuple(references))


def chatbot_output(payload: dict) -> AgentOutput:
    route = str(payload.get('route', '')).strip()
    output_type = {
        'dialogue': 'dialogue_response',
        'knowledge_query': 'knowledge_query',
        'execution': 'planner_handoff',
    }.get(route, 'dialogue_response')
    user_intent = payload.get('user_intent', {})
    references = ()
    if isinstance(user_intent, dict):
        skill_name = str(user_intent.get('type', '')).strip()
        if skill_name:
            references = (skill_name,)
    return AgentOutput(output_type, dict(payload), references)
