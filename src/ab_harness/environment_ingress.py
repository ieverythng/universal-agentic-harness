"""Deterministic classification of normalized environment stimuli."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ab_harness.environment_runs import EnvironmentRun


IngressAction = Literal[
    'state_update', 'start_task', 'resume_task', 'notify_task', 'reject'
]


@dataclass(frozen=True)
class EnvironmentIngress:
    """Immutable normalized input received through an environment binding."""

    environment_ingress_id: str
    environment_run_id: str
    binding_id: str
    ingress_type: str
    payload_artifact_id: str
    native_lineage: tuple[tuple[str, str], ...]
    observed_at: str

    def __post_init__(self) -> None:
        if not isinstance(self.native_lineage, tuple) or any(
            not isinstance(item, tuple) for item in self.native_lineage
        ):
            raise TypeError('native lineage must be an immutable tuple')
        required = {
            'environment_ingress_id': self.environment_ingress_id,
            'environment_run_id': self.environment_run_id,
            'binding_id': self.binding_id,
            'ingress_type': self.ingress_type,
            'payload_artifact_id': self.payload_artifact_id,
            'observed_at': self.observed_at,
        }
        missing = tuple(name for name, value in required.items() if not value.strip())
        if missing:
            raise ValueError(
                'environment ingress fields must not be empty: %s'
                % ', '.join(missing)
            )


@dataclass(frozen=True)
class TaskIngressRule:
    """Domain-pack rule mapping one normalized ingress type to an action."""

    binding_id: str
    ingress_type: str
    action: IngressAction

    def __post_init__(self) -> None:
        if not self.binding_id.strip() or not self.ingress_type.strip():
            raise ValueError('ingress rule fields must not be empty')
        if self.action not in {
            'state_update',
            'start_task',
            'resume_task',
            'notify_task',
            'reject',
        }:
            raise ValueError('invalid ingress action: %s' % self.action)


@dataclass(frozen=True)
class TaskIngressDecision:
    """Deterministic association result produced before model invocation."""

    environment_ingress_id: str
    environment_run_id: str
    action: IngressAction
    reason_code: str
    task_id: str | None = None
    trace_id: str | None = None


class TaskIngressPolicy:
    """Apply frozen domain rules to ingress for one active environment run."""

    def __init__(
        self,
        *,
        environment_profile_id: str,
        domain_contract_pack_revision: str,
        rules: tuple[TaskIngressRule, ...],
    ) -> None:
        self.environment_profile_id = environment_profile_id
        self.domain_contract_pack_revision = domain_contract_pack_revision
        self._rules: dict[tuple[str, str], TaskIngressRule] = {}
        for rule in rules:
            if rule.action in {'start_task', 'resume_task', 'notify_task'}:
                raise ValueError(
                    'task-bearing ingress action requires task lineage: %s'
                    % rule.action
                )
            key = (rule.binding_id, rule.ingress_type)
            if key in self._rules:
                raise ValueError(
                    'ingress rule already registered: %s / %s'
                    % (rule.binding_id, rule.ingress_type)
                )
            self._rules[key] = rule

    def classify(
        self,
        environment_run: EnvironmentRun,
        ingress: EnvironmentIngress,
    ) -> TaskIngressDecision:
        if (
            self.environment_profile_id
            != environment_run.attestation.environment_profile_id
        ):
            return TaskIngressDecision(
                environment_ingress_id=ingress.environment_ingress_id,
                environment_run_id=environment_run.environment_run_id,
                action='reject',
                reason_code='policy_environment_profile_mismatch',
            )
        if (
            self.domain_contract_pack_revision
            != environment_run.attestation.domain_contract_pack_revision
        ):
            return TaskIngressDecision(
                environment_ingress_id=ingress.environment_ingress_id,
                environment_run_id=environment_run.environment_run_id,
                action='reject',
                reason_code='policy_contract_revision_mismatch',
            )
        if ingress.environment_run_id != environment_run.environment_run_id:
            return TaskIngressDecision(
                environment_ingress_id=ingress.environment_ingress_id,
                environment_run_id=environment_run.environment_run_id,
                action='reject',
                reason_code='environment_run_mismatch',
            )
        known_bindings = {binding_id for binding_id, _ingress_type in self._rules}
        if ingress.binding_id not in known_bindings:
            return TaskIngressDecision(
                environment_ingress_id=ingress.environment_ingress_id,
                environment_run_id=environment_run.environment_run_id,
                action='reject',
                reason_code='unsupported_ingress_binding',
            )
        rule = self._rules.get((ingress.binding_id, ingress.ingress_type))
        if rule is None:
            return TaskIngressDecision(
                environment_ingress_id=ingress.environment_ingress_id,
                environment_run_id=environment_run.environment_run_id,
                action='reject',
                reason_code='unsupported_ingress_type',
            )
        return TaskIngressDecision(
            environment_ingress_id=ingress.environment_ingress_id,
            environment_run_id=environment_run.environment_run_id,
            action=rule.action,
            reason_code='matched_rule',
        )
