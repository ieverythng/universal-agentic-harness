"""Compile one frozen task contract from admitted ingress and domain rules."""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
import hashlib
import json

from ab_harness.contracts import AbstractionFrame
from ab_harness.contracts import AgentRoleSpec
from ab_harness.contracts import EffectObligation
from ab_harness.contracts import InteractionModuleSpec
from ab_harness.domain_contracts import DomainContractPack
from ab_harness.environment_ingress import TaskIngressDecision
from ab_harness.projection import InteractionProjector
from ab_harness.registry import RegistrySnapshot
from ab_harness.task_registry import EnvironmentTaskRegistry


TASK_SPEC_SCHEMA = "uah.task_spec/v1"
COMPILED_TASK_SCHEMA = "uah.compiled_task/v1"


def _required_strings(values: dict[str, str], contract: str) -> None:
    missing = tuple(name for name, value in values.items() if not value.strip())
    if missing:
        raise ValueError(
            "%s fields must not be empty: %s" % (contract, ", ".join(missing))
        )


def _interaction_module_payload(module: InteractionModuleSpec) -> dict[str, object]:
    return {
        "task_id": module.task_id,
        "role": asdict(module.role),
        "frame": asdict(module.frame),
        "object_ids": tuple(item.object_id for item in module.objects),
        "objects": tuple(asdict(item) for item in module.objects),
    }


def _compiled_task_payload(
    *,
    environment_ingress_id: str,
    environment_run_id: str,
    task_spec: TaskSpec,
    domain_contract_pack_id: str,
    domain_contract_pack_revision: str,
    interaction_module: InteractionModuleSpec,
    effect_obligations: tuple[EffectObligation, ...],
    prohibited_effects: tuple[str, ...],
) -> dict[str, object]:
    return {
        "schema_version": COMPILED_TASK_SCHEMA,
        "environment_ingress_id": environment_ingress_id,
        "environment_run_id": environment_run_id,
        "task_spec": asdict(task_spec),
        "domain_contract_pack_id": domain_contract_pack_id,
        "domain_contract_pack_revision": domain_contract_pack_revision,
        "interaction_module": _interaction_module_payload(interaction_module),
        "effect_obligations": tuple(asdict(item) for item in effect_obligations),
        "prohibited_effects": prohibited_effects,
        "budgets": asdict(task_spec.budgets),
    }


def _compiled_task_id(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "compiled-task:sha256:%s" % hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class TaskBudgets:
    """Finite resource limits copied into one compiled task artifact."""

    wall_time_seconds: int
    model_calls: int
    tool_calls: int

    def __post_init__(self) -> None:
        if self.wall_time_seconds <= 0:
            raise ValueError("task wall-time budget must be positive")
        if self.model_calls < 0 or self.tool_calls < 0:
            raise ValueError("task call budgets must not be negative")


@dataclass(frozen=True)
class TaskEffectRequest:
    """Task-authored effect requirement without domain-owned evidence details."""

    obligation_id: str
    effect_id: str
    requirement: str

    def __post_init__(self) -> None:
        _required_strings(
            {
                "obligation_id": self.obligation_id,
                "effect_id": self.effect_id,
            },
            "task effect request",
        )
        if self.requirement not in {"required", "best_effort"}:
            raise ValueError("invalid task effect requirement: %s" % self.requirement)


@dataclass(frozen=True)
class TaskSpec:
    """Frozen task intent compiled once after successful task-start ingress."""

    task_id: str
    trace_id: str
    task_type_id: str
    role_id: str
    frame_id: str
    domain_contract_pack_revision: str
    goal: str
    requested_effects: tuple[TaskEffectRequest, ...]
    prohibited_effects: tuple[str, ...]
    budgets: TaskBudgets
    schema_version: str = TASK_SPEC_SCHEMA

    def __post_init__(self) -> None:
        if not isinstance(self.requested_effects, tuple) or not isinstance(
            self.prohibited_effects, tuple
        ):
            raise TypeError("task spec collections must be tuples")
        _required_strings(
            {
                "task_id": self.task_id,
                "trace_id": self.trace_id,
                "task_type_id": self.task_type_id,
                "role_id": self.role_id,
                "frame_id": self.frame_id,
                "domain_contract_pack_revision": self.domain_contract_pack_revision,
                "goal": self.goal,
            },
            "task spec",
        )
        if self.schema_version != TASK_SPEC_SCHEMA:
            raise ValueError("unsupported task spec schema: %s" % self.schema_version)
        if not self.requested_effects:
            raise ValueError("task spec requires at least one requested effect")
        obligation_ids = tuple(item.obligation_id for item in self.requested_effects)
        duplicate_obligation_ids = tuple(
            dict.fromkeys(
                obligation_id
                for obligation_id in obligation_ids
                if obligation_ids.count(obligation_id) > 1
            )
        )
        if duplicate_obligation_ids:
            raise ValueError(
                "duplicate task obligation IDs: %s"
                % ", ".join(duplicate_obligation_ids)
            )


@dataclass(frozen=True)
class CompiledTask:
    """Content-addressed task projection and acceptance source of truth."""

    compiled_task_id: str
    environment_ingress_id: str
    environment_run_id: str
    task_spec: TaskSpec
    domain_contract_pack_id: str
    domain_contract_pack_revision: str
    interaction_module: InteractionModuleSpec
    effect_obligations: tuple[EffectObligation, ...]
    prohibited_effects: tuple[str, ...]
    schema_version: str = COMPILED_TASK_SCHEMA

    @property
    def task_id(self) -> str:
        return self.task_spec.task_id

    @property
    def trace_id(self) -> str:
        return self.task_spec.trace_id

    @property
    def task_type_id(self) -> str:
        return self.task_spec.task_type_id

    @property
    def goal(self) -> str:
        return self.task_spec.goal

    @property
    def budgets(self) -> TaskBudgets:
        return self.task_spec.budgets

    def __post_init__(self) -> None:
        self.verify_identity()

    def verify_identity(self) -> None:
        if not isinstance(self.effect_obligations, tuple) or not isinstance(
            self.prohibited_effects, tuple
        ):
            raise TypeError("compiled task collections must be tuples")
        if self.schema_version != COMPILED_TASK_SCHEMA:
            raise ValueError(
                "unsupported compiled task schema: %s" % self.schema_version
            )
        payload = _compiled_task_payload(
            environment_ingress_id=self.environment_ingress_id,
            environment_run_id=self.environment_run_id,
            task_spec=self.task_spec,
            domain_contract_pack_id=self.domain_contract_pack_id,
            domain_contract_pack_revision=self.domain_contract_pack_revision,
            interaction_module=self.interaction_module,
            effect_obligations=self.effect_obligations,
            prohibited_effects=self.prohibited_effects,
        )
        if self.compiled_task_id != _compiled_task_id(payload):
            raise ValueError("compiled task identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {
            "compiled_task_id": self.compiled_task_id,
            **_compiled_task_payload(
                environment_ingress_id=self.environment_ingress_id,
                environment_run_id=self.environment_run_id,
                task_spec=self.task_spec,
                domain_contract_pack_id=self.domain_contract_pack_id,
                domain_contract_pack_revision=self.domain_contract_pack_revision,
                interaction_module=self.interaction_module,
                effect_obligations=self.effect_obligations,
                prohibited_effects=self.prohibited_effects,
            ),
        }


class TaskSpecCompiler:
    """Compile task scope and acceptance once from frozen semantic inputs."""

    def compile(
        self,
        *,
        task_ingress_decision: TaskIngressDecision,
        task_spec: TaskSpec,
        role: AgentRoleSpec,
        frame: AbstractionFrame,
        registry: RegistrySnapshot,
        domain_contract_pack: DomainContractPack,
        task_registry: EnvironmentTaskRegistry,
    ) -> CompiledTask:
        task_ingress_decision.verify_identity()
        if task_ingress_decision.action != "start_task":
            raise ValueError("task compilation requires accepted start_task ingress")
        if task_ingress_decision.reason_code != "matched_rule":
            raise ValueError("task compilation requires accepted start_task ingress")
        if (
            task_ingress_decision.domain_contract_pack_revision
            != domain_contract_pack.revision
        ):
            raise ValueError("ingress domain contract revision does not match")
        if (
            task_ingress_decision.task_id != task_spec.task_id
            or task_ingress_decision.trace_id != task_spec.trace_id
        ):
            raise ValueError("task spec lineage does not match ingress decision")
        task_registry.require_start(
            environment_run_id=task_ingress_decision.environment_run_id,
            environment_ingress_id=task_ingress_decision.environment_ingress_id,
            ingress_artifact_id=(task_ingress_decision.environment_ingress_artifact_id),
            decision_id=task_ingress_decision.decision_id,
            domain_contract_pack_revision=(
                task_ingress_decision.domain_contract_pack_revision
            ),
            task_id=task_spec.task_id,
            trace_id=task_spec.trace_id,
        )
        if task_spec.role_id != role.role_id:
            raise ValueError("task role does not match compiler role")
        if task_spec.frame_id != frame.frame_id:
            raise ValueError("task frame does not match compiler frame")
        if task_spec.domain_contract_pack_revision != domain_contract_pack.revision:
            raise ValueError("task domain contract revision does not match")
        if domain_contract_pack.frame_id != frame.frame_id:
            raise ValueError("domain contract frame does not match compiler frame")
        if domain_contract_pack.registry_version != registry.version:
            raise ValueError("domain contract registry version does not match")
        if frame.registry_version != registry.version:
            raise ValueError("frame registry version does not match")
        if role.role_id not in domain_contract_pack.allowed_role_ids:
            raise ValueError("role is not allowed by domain contract pack")
        if task_spec.task_type_id not in domain_contract_pack.supported_task_type_ids:
            raise ValueError("task type is not supported by domain contract pack")

        rules = {item.effect_id: item for item in domain_contract_pack.effect_rules}
        requested_effect_ids = tuple(
            item.effect_id for item in task_spec.requested_effects
        )
        prohibited_effects = tuple(
            sorted(
                set(domain_contract_pack.prohibited_effects)
                | set(task_spec.prohibited_effects)
            )
        )
        conflicts = tuple(
            effect_id
            for effect_id in requested_effect_ids
            if effect_id in prohibited_effects
        )
        if conflicts:
            raise ValueError(
                "requested effects are prohibited: %s" % ", ".join(conflicts)
            )
        try:
            selected_rules = tuple(
                rules[effect_id] for effect_id in requested_effect_ids
            )
        except KeyError as exc:
            raise ValueError(
                "requested effect has no domain rule: %s" % exc.args[0]
            ) from exc
        for rule in selected_rules:
            object_view = registry.get(rule.object_id)
            if (
                object_view is not None
                and rule.evidence_owner != object_view.owner_package
            ):
                raise ValueError(
                    "domain evidence owner does not own AB object: %s" % rule.object_id
                )
            if (
                object_view is not None
                and rule.effect_id not in object_view.observable_success
            ):
                raise ValueError(
                    "domain effect is not an observable of AB object: %s"
                    % rule.object_id
                )

        interaction_module = InteractionProjector(registry).compile(
            task_id=task_spec.task_id,
            role=role,
            frame=frame,
            requested_object_ids=tuple(rule.object_id for rule in selected_rules),
        )
        obligations = tuple(
            EffectObligation(
                obligation_id=request.obligation_id,
                effect_id=request.effect_id,
                object_id=rule.object_id,
                evidence_owner=rule.evidence_owner,
                requirement=request.requirement,
                failure_policy=rule.failure_policy,
            )
            for request, rule in zip(
                task_spec.requested_effects, selected_rules, strict=True
            )
        )
        identity_payload = _compiled_task_payload(
            environment_ingress_id=task_ingress_decision.environment_ingress_id,
            environment_run_id=task_ingress_decision.environment_run_id,
            task_spec=task_spec,
            domain_contract_pack_id=domain_contract_pack.domain_contract_pack_id,
            domain_contract_pack_revision=domain_contract_pack.revision,
            interaction_module=interaction_module,
            effect_obligations=obligations,
            prohibited_effects=prohibited_effects,
        )
        compiled_task_id = _compiled_task_id(identity_payload)
        return CompiledTask(
            compiled_task_id=compiled_task_id,
            environment_ingress_id=task_ingress_decision.environment_ingress_id,
            environment_run_id=task_ingress_decision.environment_run_id,
            task_spec=task_spec,
            domain_contract_pack_id=domain_contract_pack.domain_contract_pack_id,
            domain_contract_pack_revision=domain_contract_pack.revision,
            interaction_module=interaction_module,
            effect_obligations=obligations,
            prohibited_effects=prohibited_effects,
        )
