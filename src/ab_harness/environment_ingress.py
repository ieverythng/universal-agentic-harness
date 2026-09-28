"""Deterministic classification of normalized environment stimuli."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Literal

from ab_harness.environment_runs import EnvironmentRun
from ab_harness.task_registry import DuplicateEnvironmentIngressError
from ab_harness.task_registry import EnvironmentTaskRegistry
from ab_harness.task_registry import TaskAlreadyRegisteredError
from ab_harness.task_registry import TaskLineage
from ab_harness.task_registry import TaskTerminalError
from ab_harness.task_registry import UnknownTaskError


IngressAction = Literal[
    'state_update', 'start_task', 'resume_task', 'notify_task', 'reject'
]
_TRACE_ID_DOMAIN = b'uah-trace-v1'


def _trace_id_for(environment_run_id: str, task_id: str) -> str:
    digest = hashlib.sha256(
        b'\0'.join(
            (
                _TRACE_ID_DOMAIN,
                environment_run_id.encode('utf-8'),
                task_id.encode('utf-8'),
            )
        )
    ).hexdigest()
    return 'trace:sha256:%s' % digest


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
        lineage_keys = tuple(key for key, _value in self.native_lineage)
        if len(lineage_keys) != len(set(lineage_keys)):
            raise ValueError('native lineage keys must be unique')
        if any(
            not key.strip() or not value.strip()
            for key, value in self.native_lineage
        ):
            raise ValueError('native lineage fields must not be empty')
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
    task_id_lineage_key: str | None = None

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
        if self.action in {'start_task', 'resume_task', 'notify_task'} and (
            self.task_id_lineage_key is None
            or not self.task_id_lineage_key.strip()
        ):
            raise ValueError('task-bearing rule requires a task identity lineage key')


@dataclass(frozen=True)
class TaskIngressDecision:
    """Deterministic association result produced before model invocation."""

    environment_ingress_id: str
    environment_run_id: str
    action: IngressAction
    reason_code: str
    domain_contract_pack_revision: str | None = None
    task_id: str | None = None
    trace_id: str | None = None
    task_status: str | None = None


class TaskIngressPolicy:
    """Apply frozen domain rules to ingress for one active environment run."""

    def __init__(
        self,
        *,
        environment_profile_id: str,
        domain_contract_pack_revision: str,
        rules: tuple[TaskIngressRule, ...],
        task_registry: EnvironmentTaskRegistry | None = None,
    ) -> None:
        self.environment_profile_id = environment_profile_id
        self.domain_contract_pack_revision = domain_contract_pack_revision
        self._task_registry = task_registry
        self._rules: dict[tuple[str, str], TaskIngressRule] = {}
        for rule in rules:
            if rule.action in {'start_task', 'resume_task', 'notify_task'} and (
                task_registry is None
            ):
                raise ValueError(
                    'task-bearing ingress action requires a task registry: %s'
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
        if rule.action == 'start_task':
            task_id = dict(ingress.native_lineage).get(rule.task_id_lineage_key)
            if task_id is None:
                return TaskIngressDecision(
                    environment_ingress_id=ingress.environment_ingress_id,
                    environment_run_id=environment_run.environment_run_id,
                    action='reject',
                    reason_code='missing_task_identity',
                )
            trace_id = _trace_id_for(environment_run.environment_run_id, task_id)
            lineage = TaskLineage(
                environment_run_id=environment_run.environment_run_id,
                task_id=task_id,
                trace_id=trace_id,
                starting_environment_ingress_id=ingress.environment_ingress_id,
            )
            try:
                self._task_registry.register_start(lineage)
            except DuplicateEnvironmentIngressError as exc:
                return TaskIngressDecision(
                    environment_ingress_id=ingress.environment_ingress_id,
                    environment_run_id=environment_run.environment_run_id,
                    action='reject',
                    reason_code='duplicate_environment_ingress',
                    task_id=exc.lineage.task_id,
                    trace_id=exc.lineage.trace_id,
                )
            except TaskAlreadyRegisteredError as exc:
                return TaskIngressDecision(
                    environment_ingress_id=ingress.environment_ingress_id,
                    environment_run_id=environment_run.environment_run_id,
                    action='reject',
                    reason_code='task_already_registered',
                    task_id=exc.lineage.task_id,
                    trace_id=exc.lineage.trace_id,
                )
            return TaskIngressDecision(
                environment_ingress_id=ingress.environment_ingress_id,
                environment_run_id=environment_run.environment_run_id,
                action=rule.action,
                reason_code='matched_rule',
                domain_contract_pack_revision=(
                    self.domain_contract_pack_revision
                ),
                task_id=task_id,
                trace_id=trace_id,
            )
        if rule.action in {'resume_task', 'notify_task'}:
            task_id = dict(ingress.native_lineage).get(rule.task_id_lineage_key)
            if task_id is None:
                return TaskIngressDecision(
                    environment_ingress_id=ingress.environment_ingress_id,
                    environment_run_id=environment_run.environment_run_id,
                    action='reject',
                    reason_code='missing_task_identity',
                )
            try:
                lineage = self._task_registry.register_existing_ingress(
                    environment_run_id=environment_run.environment_run_id,
                    environment_ingress_id=ingress.environment_ingress_id,
                    task_id=task_id,
                    ingress_action=rule.action,
                )
            except DuplicateEnvironmentIngressError as exc:
                return TaskIngressDecision(
                    environment_ingress_id=ingress.environment_ingress_id,
                    environment_run_id=environment_run.environment_run_id,
                    action='reject',
                    reason_code='duplicate_environment_ingress',
                    task_id=exc.lineage.task_id,
                    trace_id=exc.lineage.trace_id,
                )
            except UnknownTaskError:
                return TaskIngressDecision(
                    environment_ingress_id=ingress.environment_ingress_id,
                    environment_run_id=environment_run.environment_run_id,
                    action='reject',
                    reason_code='unknown_task_identity',
                )
            except TaskTerminalError as exc:
                return TaskIngressDecision(
                    environment_ingress_id=ingress.environment_ingress_id,
                    environment_run_id=environment_run.environment_run_id,
                    action='reject',
                    reason_code='task_terminal',
                    task_id=exc.lineage.task_id,
                    trace_id=exc.lineage.trace_id,
                    task_status=exc.status,
                )
            return TaskIngressDecision(
                environment_ingress_id=ingress.environment_ingress_id,
                environment_run_id=environment_run.environment_run_id,
                action=rule.action,
                reason_code='matched_registered_task',
                task_id=lineage.task_id,
                trace_id=lineage.trace_id,
            )
        return TaskIngressDecision(
            environment_ingress_id=ingress.environment_ingress_id,
            environment_run_id=environment_run.environment_run_id,
            action=rule.action,
            reason_code='matched_rule',
        )
