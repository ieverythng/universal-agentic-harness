"""Authoritative admission of environment ingress into task lineage."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from types import MappingProxyType

from ab_harness.domain_contracts import DomainContractPack
from ab_harness.domain_contracts import IngressAction
from ab_harness.domain_contracts import TaskIngressRule
from ab_harness.environment_ingress import EnvironmentIngress
from ab_harness.environment_ingress import TaskIngressDecision
from ab_harness.environment_runs import EnvironmentRun
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.lifecycle import TaskIngressFact
from ab_harness.lifecycle import TaskStartedFact
from ab_harness.task_registry import EnvironmentTaskRegistry
from ab_harness.task_registry import TaskLineage


_TRACE_ID_DOMAIN = b"uah-trace-v1"


@dataclass(frozen=True)
class _TaskStartCommand:
    authority: TaskIngressAuthority
    capability: object
    environment_run: EnvironmentRun
    ingress: EnvironmentIngress
    decision: TaskIngressDecision

    def require_fact(self, ledger: LifecycleLedger) -> TaskStartedFact:
        authority = self.authority
        if (
            type(authority) is not TaskIngressAuthority
            or authority._ledger is not ledger
            or self.capability is not authority._start_capability
        ):
            raise ValueError("invalid authority-bound task-start command")
        self.ingress.verify_identity()
        self.decision.verify_identity()
        expected = authority._start_decision(self.environment_run, self.ingress)
        if expected != self.decision:
            raise ValueError("task-start command does not match admitted ingress")
        return TaskStartedFact(
            environment_run_id=expected.environment_run_id,
            task_id=expected.task_id,
            trace_id=expected.trace_id,
            environment_ingress_id=expected.environment_ingress_id,
            ingress_artifact_id=expected.environment_ingress_artifact_id,
            decision_id=expected.decision_id,
            domain_contract_pack_revision=expected.domain_contract_pack_revision,
        )


@dataclass(frozen=True)
class _FrozenIngressRule:
    binding_id: str
    ingress_type: str
    action: IngressAction
    task_id_lineage_key: str | None

    @classmethod
    def from_rule(cls, rule: TaskIngressRule) -> _FrozenIngressRule:
        return cls(
            binding_id=rule.binding_id,
            ingress_type=rule.ingress_type,
            action=rule.action,
            task_id_lineage_key=rule.task_id_lineage_key,
        )


def _trace_id_for(environment_run_id: str, task_id: str) -> str:
    digest = hashlib.sha256(
        b"\0".join(
            (
                _TRACE_ID_DOMAIN,
                environment_run_id.encode("utf-8"),
                task_id.encode("utf-8"),
            )
        )
    ).hexdigest()
    return "trace:sha256:%s" % digest


class TaskIngressAuthority:
    """Classify and durably admit ingress under one frozen domain policy."""

    def __init__(
        self,
        *,
        environment_profile_id: str,
        domain_contract_pack: DomainContractPack,
        lifecycle_ledger: LifecycleLedger | None = None,
    ) -> None:
        domain_contract_pack.verify_identity()
        self._environment_profile_id = environment_profile_id
        self._domain_contract_pack_revision = domain_contract_pack.revision
        self._ledger = lifecycle_ledger or LifecycleLedger()
        self._task_registry = EnvironmentTaskRegistry(self._ledger)
        self._start_capability = object()
        self._rules = MappingProxyType(
            {
                (rule.binding_id, rule.ingress_type): _FrozenIngressRule.from_rule(rule)
                for rule in domain_contract_pack.ingress_rules
            }
        )

    def _start_decision(
        self, environment_run: EnvironmentRun, ingress: EnvironmentIngress
    ) -> TaskIngressDecision:
        """Recheck the issuer's frozen policy at the ledger trust crossing."""
        rule = self._rules.get((ingress.binding_id, ingress.ingress_type))
        if (
            self._environment_profile_id
            != environment_run.attestation.environment_profile_id
            or self._domain_contract_pack_revision
            != environment_run.attestation.domain_contract_pack_revision
            or ingress.environment_run_id != environment_run.environment_run_id
            or rule is None
            or rule.action != "start_task"
        ):
            raise ValueError("task-start command does not match admitted ingress")
        task_id = dict(ingress.native_lineage).get(rule.task_id_lineage_key or "")
        if task_id is None:
            raise ValueError("task-start command does not match admitted ingress")
        return self._decision(
            environment_run, ingress, "start_task", "matched_rule",
            domain_contract_pack_revision=self._domain_contract_pack_revision,
            task_id=task_id,
            trace_id=_trace_id_for(environment_run.environment_run_id, task_id),
        )

    def admit(
        self,
        environment_run: EnvironmentRun,
        ingress: EnvironmentIngress,
    ) -> TaskIngressDecision:
        """Decide ingress and record accepted task-bearing lineage in the ledger."""

        ingress.verify_identity()
        if (
            self._environment_profile_id
            != environment_run.attestation.environment_profile_id
        ):
            return self._decision(
                environment_run,
                ingress,
                "reject",
                "policy_environment_profile_mismatch",
            )
        if (
            self._domain_contract_pack_revision
            != environment_run.attestation.domain_contract_pack_revision
        ):
            return self._decision(
                environment_run,
                ingress,
                "reject",
                "policy_contract_revision_mismatch",
            )
        if ingress.environment_run_id != environment_run.environment_run_id:
            return self._decision(
                environment_run,
                ingress,
                "reject",
                "environment_run_mismatch",
            )
        known_bindings = {binding_id for binding_id, _ingress_type in self._rules}
        if ingress.binding_id not in known_bindings:
            return self._decision(
                environment_run,
                ingress,
                "reject",
                "unsupported_ingress_binding",
            )
        rule = self._rules.get((ingress.binding_id, ingress.ingress_type))
        if rule is None:
            return self._decision(
                environment_run,
                ingress,
                "reject",
                "unsupported_ingress_type",
            )
        if rule.action == "start_task":
            return self._admit_start(environment_run, ingress, rule)
        if rule.action in {"resume_task", "notify_task"}:
            return self._admit_existing(environment_run, ingress, rule)
        return self._decision(environment_run, ingress, rule.action, "matched_rule")

    def _admit_start(
        self,
        environment_run: EnvironmentRun,
        ingress: EnvironmentIngress,
        rule: _FrozenIngressRule,
    ) -> TaskIngressDecision:
        task_id = dict(ingress.native_lineage).get(rule.task_id_lineage_key or "")
        if task_id is None:
            return self._decision(
                environment_run,
                ingress,
                "reject",
                "missing_task_identity",
            )
        duplicate = self._task_registry.lineage_for_ingress(
            environment_run_id=environment_run.environment_run_id,
            environment_ingress_id=ingress.environment_ingress_id,
        )
        if duplicate is not None:
            return self._lineage_rejection(
                environment_run,
                ingress,
                "duplicate_environment_ingress",
                duplicate,
            )
        registered = self._task_registry.lineage_for_task(
            environment_run_id=environment_run.environment_run_id,
            task_id=task_id,
        )
        if registered is not None:
            return self._lineage_rejection(
                environment_run,
                ingress,
                "task_already_registered",
                registered,
            )
        decision = self._start_decision(environment_run, ingress)
        try:
            self._ledger.record(
                _TaskStartCommand(
                    authority=self,
                    capability=self._start_capability,
                    environment_run=environment_run,
                    ingress=ingress,
                    decision=decision,
                )
            )
        except ValueError:
            duplicate = self._task_registry.lineage_for_ingress(
                environment_run_id=environment_run.environment_run_id,
                environment_ingress_id=ingress.environment_ingress_id,
            )
            if duplicate is not None:
                return self._lineage_rejection(
                    environment_run,
                    ingress,
                    "duplicate_environment_ingress",
                    duplicate,
                )
            registered = self._task_registry.lineage_for_task(
                environment_run_id=environment_run.environment_run_id,
                task_id=task_id,
            )
            if registered is not None:
                return self._lineage_rejection(
                    environment_run,
                    ingress,
                    "task_already_registered",
                    registered,
                )
            raise
        recorded = self._task_registry.lineage_for_ingress(
            environment_run_id=environment_run.environment_run_id,
            environment_ingress_id=ingress.environment_ingress_id,
        )
        if recorded is None or recorded.starting_decision_id != decision.decision_id:
            raise RuntimeError("recorded task start is absent from task projection")
        return decision

    def _admit_existing(
        self,
        environment_run: EnvironmentRun,
        ingress: EnvironmentIngress,
        rule: _FrozenIngressRule,
    ) -> TaskIngressDecision:
        task_id = dict(ingress.native_lineage).get(rule.task_id_lineage_key or "")
        if task_id is None:
            return self._decision(
                environment_run,
                ingress,
                "reject",
                "missing_task_identity",
            )
        duplicate = self._task_registry.lineage_for_ingress(
            environment_run_id=environment_run.environment_run_id,
            environment_ingress_id=ingress.environment_ingress_id,
        )
        if duplicate is not None:
            return self._lineage_rejection(
                environment_run,
                ingress,
                "duplicate_environment_ingress",
                duplicate,
            )
        lineage = self._task_registry.lineage_for_task(
            environment_run_id=environment_run.environment_run_id,
            task_id=task_id,
        )
        if lineage is None:
            return self._decision(
                environment_run,
                ingress,
                "reject",
                "unknown_task_identity",
            )
        terminal_status = self._task_registry.terminal_status(lineage)
        if terminal_status is not None:
            return self._lineage_rejection(
                environment_run,
                ingress,
                "task_terminal",
                lineage,
                task_status=terminal_status,
            )
        if lineage.domain_contract_pack_revision != self._domain_contract_pack_revision:
            raise ValueError("existing-task ingress contract revision does not match")
        decision = self._decision(
            environment_run,
            ingress,
            rule.action,
            "matched_registered_task",
            domain_contract_pack_revision=self._domain_contract_pack_revision,
            task_id=lineage.task_id,
            trace_id=lineage.trace_id,
        )
        try:
            self._ledger.record(
                TaskIngressFact(
                    environment_run_id=environment_run.environment_run_id,
                    task_id=lineage.task_id,
                    trace_id=lineage.trace_id,
                    environment_ingress_id=ingress.environment_ingress_id,
                    ingress_artifact_id=ingress.ingress_artifact_id,
                    decision_id=decision.decision_id,
                    domain_contract_pack_revision=self._domain_contract_pack_revision,
                    action=rule.action,
                )
            )
        except ValueError:
            duplicate = self._task_registry.lineage_for_ingress(
                environment_run_id=environment_run.environment_run_id,
                environment_ingress_id=ingress.environment_ingress_id,
            )
            if duplicate is not None:
                return self._lineage_rejection(
                    environment_run,
                    ingress,
                    "duplicate_environment_ingress",
                    duplicate,
                )
            current = self._task_registry.lineage_for_task(
                environment_run_id=environment_run.environment_run_id,
                task_id=task_id,
            )
            if current is not None:
                terminal_status = self._task_registry.terminal_status(current)
                if terminal_status is not None:
                    return self._lineage_rejection(
                        environment_run,
                        ingress,
                        "task_terminal",
                        current,
                        task_status=terminal_status,
                    )
            raise
        recorded = self._task_registry.lineage_for_ingress(
            environment_run_id=environment_run.environment_run_id,
            environment_ingress_id=ingress.environment_ingress_id,
        )
        if recorded != lineage:
            raise RuntimeError("recorded task ingress is absent from task projection")
        return decision

    @staticmethod
    def _decision(
        environment_run: EnvironmentRun,
        ingress: EnvironmentIngress,
        action: IngressAction,
        reason_code: str,
        *,
        domain_contract_pack_revision: str | None = None,
        task_id: str | None = None,
        trace_id: str | None = None,
        task_status: str | None = None,
    ) -> TaskIngressDecision:
        return TaskIngressDecision(
            environment_ingress_id=ingress.environment_ingress_id,
            environment_ingress_artifact_id=ingress.ingress_artifact_id,
            environment_run_id=environment_run.environment_run_id,
            action=action,
            reason_code=reason_code,
            domain_contract_pack_revision=domain_contract_pack_revision,
            task_id=task_id,
            trace_id=trace_id,
            task_status=task_status,
        )

    def _lineage_rejection(
        self,
        environment_run: EnvironmentRun,
        ingress: EnvironmentIngress,
        reason_code: str,
        lineage: TaskLineage,
        *,
        task_status: str | None = None,
    ) -> TaskIngressDecision:
        return self._decision(
            environment_run,
            ingress,
            "reject",
            reason_code,
            task_id=lineage.task_id,
            trace_id=lineage.trace_id,
            task_status=task_status,
        )
