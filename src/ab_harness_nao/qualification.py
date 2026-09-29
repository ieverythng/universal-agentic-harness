"""Frozen-output qualification loop"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.bindings import BindingCatalog
from ab_harness.contracts import AgentOutput
from ab_harness.contracts import EffectEvidence, GateDecision
from ab_harness.contracts import TaskAcceptance
from ab_harness.domain_lifecycle import DomainLifecycleAdmission
from ab_harness.environment import InProcessEnvironmentOwner
from ab_harness.environment_ingress import EnvironmentIngress
from ab_harness.environment_ingress import TaskIngressDecision
from ab_harness.environment_ingress import TaskIngressPolicy
from ab_harness.environment_runs import EnvironmentRun
from ab_harness.gate import OutputGate
from ab_harness.lifecycle import AcceptanceFact
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.proposal_admission import ProposalNormalizer
from ab_harness.proposal_admission import SemanticAdmission
from ab_harness_nao.contracts import CHATBOT_ROLE, PLANNER_ROLE
from ab_harness_nao.contracts import chatbot_output, nao_frame
from ab_harness.projection import InteractionProjector
from ab_harness.registry import RegistrySnapshot
from ab_harness.domain_contracts import DomainContractPack
from ab_harness.domain_contracts import DomainEffectRule
from ab_harness.domain_contracts import TaskIngressRule
from ab_harness.task_compiler import TaskBudgets
from ab_harness.task_compiler import TaskEffectRequest
from ab_harness.task_compiler import TaskSpec
from ab_harness.task_compiler import TaskSpecCompiler
from ab_harness.task_registry import EnvironmentTaskRegistry


_QUALIFICATION_TASK_TYPE = "recorded_nao_qualification"


@dataclass(frozen=True)
class NaoQualificationCase:
    case_id: str
    task_id: str
    requested_effects: tuple[TaskEffectRequest, ...]
    goal: str
    budgets: TaskBudgets
    prohibited_effects: tuple[str, ...] = ()
    expected_chatbot_output_type: str = "planner_handoff"


@dataclass(frozen=True)
class NaoPlanStep:
    step_id: str
    object_id: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class NaoQualificationResult:
    case_id: str
    passed: bool
    failure_stage: str | None
    chatbot_gate: GateDecision
    planner_admitted: bool
    planner_reasons: tuple[str, ...] = ()
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
        catalog: BindingCatalog,
        environment_run: EnvironmentRun,
        environment: InProcessEnvironmentOwner,
        lifecycle_ledger: LifecycleLedger,
        domain_contract_pack: DomainContractPack,
    ) -> None:
        self._registry = registry
        self._catalog = catalog
        self._environment_run = environment_run
        self._environment = environment
        self._lifecycle_ledger = lifecycle_ledger
        self._domain_contract_pack = domain_contract_pack
        if domain_contract_pack.registry_version != registry.version:
            raise ValueError("qualification domain pack registry does not match")
        if domain_contract_pack.frame_id != nao_frame(registry).frame_id:
            raise ValueError("qualification domain pack frame does not match")
        if (
            domain_contract_pack.revision
            != environment_run.attestation.domain_contract_pack_revision
        ):
            raise ValueError("qualification domain pack revision does not match run")
        self._task_registry = EnvironmentTaskRegistry(lifecycle_ledger)
        self._ingress_policy = TaskIngressPolicy(
            environment_profile_id=(environment_run.attestation.environment_profile_id),
            domain_contract_pack=domain_contract_pack,
            task_registry=self._task_registry,
        )
        self._projector = InteractionProjector(registry)
        self._gate = OutputGate()
        self._acceptance = TaskAcceptanceEvaluator()

    def run(
        self,
        *,
        case: NaoQualificationCase,
        ingress: EnvironmentIngress,
        chatbot_payload: dict[str, Any],
        planner_payload: dict[str, Any],
        runtime_mode: str,
    ) -> NaoQualificationResult:
        frame = nao_frame(self._registry)
        ingress_decision = self._ingress_policy.classify(
            self._environment_run,
            ingress,
        )
        if ingress_decision.action != "start_task":
            return NaoQualificationResult(
                case_id=case.case_id,
                passed=False,
                failure_stage="task_ingress",
                chatbot_gate=GateDecision(False, ("task ingress was rejected",)),
                planner_admitted=False,
                planner_reasons=(ingress_decision.reason_code,),
            )
        object_by_effect = {
            rule.effect_id: rule.object_id
            for rule in self._domain_contract_pack.effect_rules
        }
        try:
            requested_object_ids = tuple(
                object_by_effect[request.effect_id]
                for request in case.requested_effects
            )
        except KeyError as exc:
            return NaoQualificationResult(
                case_id=case.case_id,
                passed=False,
                failure_stage="task_compilation",
                chatbot_gate=GateDecision(False, ("task effect has no domain rule",)),
                planner_admitted=False,
                errors=("requested effect has no domain rule: %s" % exc.args[0],),
            )
        chatbot_module = self._projector.compile(
            task_id=case.task_id,
            role=CHATBOT_ROLE,
            frame=frame,
            requested_object_ids=requested_object_ids,
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
                    "qualification case requires chatbot output type: %s"
                    % case.expected_chatbot_output_type,
                ),
            )
        if not chatbot_gate.accepted:
            return NaoQualificationResult(
                case_id=case.case_id,
                passed=False,
                failure_stage="chatbot_gate",
                chatbot_gate=chatbot_gate,
                planner_admitted=False,
                planner_reasons=(
                    "not evaluated because chatbot gate rejected the proposal",
                ),
            )

        try:
            compiled_task = _compile_qualification_task(
                case=case,
                registry=self._registry,
                ingress_decision=ingress_decision,
                domain_contract_pack=self._domain_contract_pack,
                task_registry=self._task_registry,
            )
        except ValueError as exc:
            return NaoQualificationResult(
                case_id=case.case_id,
                passed=False,
                failure_stage="task_compilation",
                chatbot_gate=chatbot_gate,
                planner_admitted=False,
                errors=(str(exc),),
            )
        self._lifecycle_ledger.record(compiled_task)

        try:
            raw_output_artifact_id = _model_output_artifact_id(planner_payload)
            steps = _strict_skill_steps(planner_payload)
        except (TypeError, ValueError) as exc:
            return NaoQualificationResult(
                case_id=case.case_id,
                passed=False,
                failure_stage="proposal_normalization",
                chatbot_gate=chatbot_gate,
                planner_admitted=False,
                planner_reasons=(str(exc),),
            )

        admitted_operations = []
        for step in steps:
            normalized = ProposalNormalizer().normalize(
                compiled_task=compiled_task,
                operation_id="%s:operation:%s" % (case.case_id, step.step_id),
                raw_output_artifact_id=raw_output_artifact_id,
                output=AgentOutput(
                    output_type="executable_plan",
                    payload={
                        "object_id": step.object_id,
                        "arguments": step.arguments,
                    },
                    referenced_objects=(step.object_id,),
                ),
            )
            if normalized.proposal is None:
                return NaoQualificationResult(
                    case_id=case.case_id,
                    passed=False,
                    failure_stage="proposal_normalization",
                    chatbot_gate=chatbot_gate,
                    planner_admitted=False,
                    planner_reasons=normalized.reason_codes,
                )
            self._lifecycle_ledger.record(normalized.proposal)
            admitted = SemanticAdmission(
                catalog=self._catalog,
                environment_id=self._environment.environment_id,
                runtime_mode=runtime_mode,
            ).admit(compiled_task, normalized.proposal)
            if admitted.admitted_operation is None:
                return NaoQualificationResult(
                    case_id=case.case_id,
                    passed=False,
                    failure_stage="semantic_admission",
                    chatbot_gate=chatbot_gate,
                    planner_admitted=False,
                    planner_reasons=admitted.reason_codes,
                )
            self._lifecycle_ledger.record(admitted.admitted_operation)
            admitted_operations.append(admitted.admitted_operation)

        lifecycle = DomainLifecycleAdmission(
            environment_run=self._environment_run,
            environment_id=self._environment.environment_id,
            lifecycle_ledger=self._lifecycle_ledger,
        )
        leases = []
        for admitted_operation in admitted_operations:
            lease = lifecycle.request_execution(admitted_operation)
            if lease.execution_lease is None:
                return NaoQualificationResult(
                    case_id=case.case_id,
                    passed=False,
                    failure_stage="domain_admission",
                    chatbot_gate=chatbot_gate,
                    planner_admitted=False,
                    planner_reasons=lease.reason_codes,
                )
            leases.append(lease.execution_lease)

        evidence: list[EffectEvidence] = []
        for lease in leases:
            try:
                receipt = self._environment.execute(lease)
            except Exception as exc:
                if not self._lifecycle_ledger.has_operation_event(
                    trace_id=compiled_task.trace_id,
                    operation_id=lease.operation_id,
                    event_type="execution_failed",
                ):
                    raise
                return NaoQualificationResult(
                    case_id=case.case_id,
                    passed=False,
                    failure_stage="environment_owner",
                    chatbot_gate=chatbot_gate,
                    planner_admitted=True,
                    evidence=tuple(evidence),
                    errors=(str(exc),),
                )
            evidence.append(receipt.evidence)

        closed = tuple(
            dict.fromkeys(
                observable
                for item in evidence
                if item.succeeded
                for observable in item.observed_effects
            )
        )
        missing = tuple(
            obligation.effect_id
            for obligation in compiled_task.effect_obligations
            for observable in (obligation.effect_id,)
            if observable not in closed
        )
        acceptance = self._acceptance.evaluate(
            compiled_task.effect_obligations,
            evidence,
        )
        self._lifecycle_ledger.record(
            AcceptanceFact(
                compiled_task=compiled_task,
                evidence_set=tuple(evidence),
                acceptance=acceptance,
            )
        )
        passed = acceptance.status in {"accepted", "accepted_with_deficit"}
        return NaoQualificationResult(
            case_id=case.case_id,
            passed=passed,
            failure_stage="evidence_closure" if not passed else None,
            chatbot_gate=chatbot_gate,
            planner_admitted=True,
            evidence=tuple(evidence),
            closed_observables=closed,
            missing_observables=missing,
            acceptance=acceptance,
        )


def _model_output_artifact_id(payload: dict[str, Any]) -> str:
    try:
        encoded = json.dumps(
            payload,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("planner output must contain finite JSON values") from exc
    return "model-output:sha256:%s" % hashlib.sha256(encoded).hexdigest()


def _strict_skill_steps(payload: dict[str, Any]) -> tuple[NaoPlanStep, ...]:
    if set(payload) != {"plan"}:
        raise ValueError("planner output contains unsupported top-level fields")
    plan = payload.get("plan")
    if not isinstance(plan, dict):
        raise ValueError("planner output requires a plan object")
    if set(plan) != {"steps"}:
        raise ValueError("planner plan contains unsupported fields")
    raw_steps = plan.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise ValueError("planner output requires a non-empty steps list")
    steps = []
    seen_ids: set[str] = set()
    for index, raw_step in enumerate(raw_steps):
        if not isinstance(raw_step, dict):
            raise ValueError("planner step %d must be an object" % index)
        if set(raw_step) != {"id", "type", "name", "args"}:
            raise ValueError("planner step %d contains unsupported fields" % index)
        step_id = raw_step.get("id")
        object_id = raw_step.get("name")
        arguments = raw_step.get("args")
        if raw_step.get("type") != "skill":
            raise ValueError("planner step %d is not a skill operation" % index)
        if not isinstance(step_id, str) or not step_id.strip():
            raise ValueError("planner step %d requires a string ID" % index)
        if step_id in seen_ids:
            raise ValueError("planner step ID is duplicated: %s" % step_id)
        if not isinstance(object_id, str) or not object_id.strip():
            raise ValueError("planner step %s requires a string skill name" % step_id)
        if not isinstance(arguments, dict):
            raise ValueError("planner step %s args must be an object" % step_id)
        seen_ids.add(step_id)
        steps.append(
            NaoPlanStep(
                step_id=step_id,
                object_id=object_id,
                arguments=dict(arguments),
            )
        )
    return tuple(steps)


def _compile_qualification_task(
    *,
    case: NaoQualificationCase,
    registry: RegistrySnapshot,
    ingress_decision: TaskIngressDecision,
    domain_contract_pack: DomainContractPack,
    task_registry: EnvironmentTaskRegistry,
):
    frame = nao_frame(registry)
    task = TaskSpec(
        task_id=case.task_id,
        trace_id=ingress_decision.trace_id,
        task_type_id=_QUALIFICATION_TASK_TYPE,
        role_id=PLANNER_ROLE.role_id,
        frame_id=frame.frame_id,
        domain_contract_pack_revision=domain_contract_pack.revision,
        goal=case.goal,
        requested_effects=case.requested_effects,
        prohibited_effects=case.prohibited_effects,
        budgets=case.budgets,
    )
    return TaskSpecCompiler().compile(
        task_ingress_decision=ingress_decision,
        task_spec=task,
        role=PLANNER_ROLE,
        frame=frame,
        registry=registry,
        domain_contract_pack=domain_contract_pack,
        task_registry=task_registry,
    )


def nao_qualification_domain_contract_pack(
    registry: RegistrySnapshot,
) -> DomainContractPack:
    frame = nao_frame(registry)
    return DomainContractPack.issue(
        domain_contract_pack_id="domain-pack:nao-recorded-qualification:v1",
        frame_id=frame.frame_id,
        registry_version=registry.version,
        allowed_role_ids=(PLANNER_ROLE.role_id,),
        supported_task_type_ids=(_QUALIFICATION_TASK_TYPE,),
        ingress_rules=(
            TaskIngressRule(
                binding_id="binding:nao.recorded_qualification:v1",
                ingress_type="recorded_user_request",
                action="start_task",
                task_id_lineage_key="task_id",
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
    )
