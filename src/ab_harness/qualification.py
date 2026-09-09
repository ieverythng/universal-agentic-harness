"""Frozen-output qualification loop"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.contracts import EffectEvidence, EffectObligation, GateDecision
from ab_harness.contracts import TaskAcceptance
from ab_harness.environment import InProcessEnvironmentOwner
from ab_harness.gate import OutputGate
from ab_harness.nao_h0 import CHATBOT_ROLE, PLANNER_ROLE
from ab_harness.nao_h0 import chatbot_output, nao_frame, planner_output
from ab_harness.projection import InteractionProjector
from ab_harness.registry import RegistrySnapshot


@dataclass(frozen=True)
class QualificationCase:
    case_id: str
    task_id: str
    requested_object_ids: tuple[str, ...]
    required_observables: tuple[str, ...] = ()
    effect_obligations: tuple[EffectObligation, ...] = ()
    prohibited_object_ids: tuple[str, ...] = ()
    expected_chatbot_output_type: str = 'planner_handoff'


@dataclass(frozen=True)
class QualificationResult:
    case_id: str
    passed: bool
    failure_stage: str | None
    chatbot_gate: GateDecision
    planner_gate: GateDecision
    evidence: tuple[EffectEvidence, ...] = ()
    closed_observables: tuple[str, ...] = ()
    missing_observables: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    acceptance: TaskAcceptance | None = None


class RecordedNaoQualificationHarness:
    """Replay recorded role outputs through UAH gates and a fake owner."""

    def __init__(
        self,
        registry: RegistrySnapshot,
        environment: InProcessEnvironmentOwner,
    ) -> None:
        self._registry = registry
        self._environment = environment
        self._projector = InteractionProjector(registry)
        self._gate = OutputGate()
        self._acceptance = TaskAcceptanceEvaluator()

    def run(
        self,
        *,
        case: QualificationCase,
        chatbot_payload: dict[str, Any],
        planner_payload: dict[str, Any],
        runtime_mode: str,
    ) -> QualificationResult:
        frame = nao_frame(self._registry)
        chatbot_module = self._projector.compile(
            task_id=case.task_id,
            role=CHATBOT_ROLE,
            frame=frame,
            requested_object_ids=case.requested_object_ids,
        )
        chatbot_proposal = chatbot_output(chatbot_payload)
        chatbot_gate = self._gate.evaluate(chatbot_proposal, chatbot_module)
        if (
            chatbot_gate.accepted
            and chatbot_proposal.output_type != case.expected_chatbot_output_type
        ):
            chatbot_gate = GateDecision(
                False,
                (
                    'qualification case requires chatbot output type: %s'
                    % case.expected_chatbot_output_type,
                ),
            )
        if not chatbot_gate.accepted:
            return QualificationResult(
                case_id=case.case_id,
                passed=False,
                failure_stage='chatbot_gate',
                chatbot_gate=chatbot_gate,
                planner_gate=GateDecision(
                    False,
                    ('not evaluated because chatbot gate rejected the proposal',),
                ),
            )

        planner_module = self._projector.compile(
            task_id=case.task_id,
            role=PLANNER_ROLE,
            frame=frame,
            requested_object_ids=case.requested_object_ids,
        )
        planner_proposal = planner_output(planner_payload)
        planner_gate = self._gate.evaluate(planner_proposal, planner_module)
        prohibited = tuple(
            object_id
            for object_id in planner_proposal.referenced_objects
            if object_id in case.prohibited_object_ids
        )
        if prohibited:
            planner_gate = GateDecision(
                False,
                planner_gate.reasons
                + tuple('prohibited object referenced: %s' % item for item in prohibited),
            )
        if not planner_gate.accepted:
            return QualificationResult(
                case_id=case.case_id,
                passed=False,
                failure_stage='planner_gate',
                chatbot_gate=chatbot_gate,
                planner_gate=planner_gate,
            )

        evidence: list[EffectEvidence] = []
        try:
            for object_id, arguments in _skill_steps(planner_payload):
                evidence.append(
                    self._environment.execute(
                        object_id=object_id,
                        arguments=arguments,
                        runtime_mode=runtime_mode,
                    )
                )
        except (LookupError, TypeError, ValueError) as exc:
            return QualificationResult(
                case_id=case.case_id,
                passed=False,
                failure_stage='environment_owner',
                chatbot_gate=chatbot_gate,
                planner_gate=planner_gate,
                evidence=tuple(evidence),
                errors=(str(exc),),
            )

        closed = tuple(
            dict.fromkeys(
                observable
                for item in evidence
                if item.succeeded
                for observable in item.observed_effects
            )
        )
        missing = tuple(
            observable
            for observable in case.required_observables
            if observable not in closed
        )
        acceptance = (
            self._acceptance.evaluate(case.effect_obligations, evidence)
            if case.effect_obligations
            else None
        )
        passed = (
            acceptance.status in {'accepted', 'accepted_with_deficit'}
            if acceptance is not None
            else not missing
        )
        return QualificationResult(
            case_id=case.case_id,
            passed=passed,
            failure_stage='evidence_closure' if not passed else None,
            chatbot_gate=chatbot_gate,
            planner_gate=planner_gate,
            evidence=tuple(evidence),
            closed_observables=closed,
            missing_observables=missing,
            acceptance=acceptance,
        )


def _skill_steps(payload: dict[str, Any]) -> tuple[tuple[str, dict[str, Any]], ...]:
    plan = payload.get('plan', {}) if isinstance(payload.get('plan'), dict) else {}
    steps: list[tuple[str, dict[str, Any]]] = []
    for step in plan.get('steps', ()):
        if not isinstance(step, dict) or step.get('type') != 'skill':
            continue
        object_id = str(step.get('name', '')).strip()
        arguments = step.get('args', {})
        if object_id:
            steps.append(
                (object_id, dict(arguments) if isinstance(arguments, dict) else {})
            )
    return tuple(steps)
