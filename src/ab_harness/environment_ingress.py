"""Deterministic classification of normalized environment stimuli."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import hashlib
import json

from ab_harness.domain_contracts import DomainContractPack
from ab_harness.domain_contracts import IngressAction
from ab_harness.domain_contracts import TaskIngressRule
from ab_harness.environment_runs import EnvironmentRun
from ab_harness.task_registry import DuplicateEnvironmentIngressError
from ab_harness.task_registry import EnvironmentTaskRegistry
from ab_harness.task_registry import TaskAlreadyRegisteredError
from ab_harness.task_registry import TaskLineage
from ab_harness.task_registry import TaskTerminalError
from ab_harness.task_registry import UnknownTaskError


_TRACE_ID_DOMAIN = b"uah-trace-v1"
ENVIRONMENT_INGRESS_SCHEMA = "uah.environment_ingress/v1"
TASK_INGRESS_DECISION_SCHEMA = "uah.task_ingress_decision/v1"


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
    schema_version: str = ENVIRONMENT_INGRESS_SCHEMA
    ingress_artifact_id: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.native_lineage, tuple) or any(
            not isinstance(item, tuple) for item in self.native_lineage
        ):
            raise TypeError("native lineage must be an immutable tuple")
        lineage_keys = tuple(key for key, _value in self.native_lineage)
        if len(lineage_keys) != len(set(lineage_keys)):
            raise ValueError("native lineage keys must be unique")
        if any(
            not key.strip() or not value.strip() for key, value in self.native_lineage
        ):
            raise ValueError("native lineage fields must not be empty")
        required = {
            "environment_ingress_id": self.environment_ingress_id,
            "environment_run_id": self.environment_run_id,
            "binding_id": self.binding_id,
            "ingress_type": self.ingress_type,
            "payload_artifact_id": self.payload_artifact_id,
            "observed_at": self.observed_at,
        }
        missing = tuple(name for name, value in required.items() if not value.strip())
        if missing:
            raise ValueError(
                "environment ingress fields must not be empty: %s" % ", ".join(missing)
            )
        if self.schema_version != ENVIRONMENT_INGRESS_SCHEMA:
            raise ValueError(
                "unsupported environment ingress schema: %s" % self.schema_version
            )
        object.__setattr__(
            self,
            "ingress_artifact_id",
            _ingress_artifact_id(self._identity_payload()),
        )

    def _identity_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "environment_ingress_id": self.environment_ingress_id,
            "environment_run_id": self.environment_run_id,
            "binding_id": self.binding_id,
            "ingress_type": self.ingress_type,
            "payload_artifact_id": self.payload_artifact_id,
            "native_lineage": self.native_lineage,
            "observed_at": self.observed_at,
        }

    def verify_identity(self) -> None:
        if self.ingress_artifact_id != _ingress_artifact_id(self._identity_payload()):
            raise ValueError("environment ingress identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        payload = self._identity_payload()
        payload["native_lineage"] = [list(item) for item in self.native_lineage]
        return {"ingress_artifact_id": self.ingress_artifact_id, **payload}


def _ingress_artifact_id(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "environment-ingress:sha256:%s" % hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class TaskIngressDecision:
    """Deterministic association result produced before model invocation."""

    environment_ingress_id: str
    environment_ingress_artifact_id: str
    environment_run_id: str
    action: IngressAction
    reason_code: str
    domain_contract_pack_revision: str | None = None
    task_id: str | None = None
    trace_id: str | None = None
    task_status: str | None = None
    schema_version: str = TASK_INGRESS_DECISION_SCHEMA
    decision_id: str = field(init=False)

    def __post_init__(self) -> None:
        required = {
            "environment_ingress_id": self.environment_ingress_id,
            "environment_ingress_artifact_id": self.environment_ingress_artifact_id,
            "environment_run_id": self.environment_run_id,
            "reason_code": self.reason_code,
        }
        missing = tuple(name for name, value in required.items() if not value.strip())
        if missing:
            raise ValueError(
                "task ingress decision fields must not be empty: %s"
                % ", ".join(missing)
            )
        if self.schema_version != TASK_INGRESS_DECISION_SCHEMA:
            raise ValueError(
                "unsupported task ingress decision schema: %s" % self.schema_version
            )
        if self.action not in {
            "state_update",
            "start_task",
            "resume_task",
            "notify_task",
            "reject",
        }:
            raise ValueError("invalid task ingress decision action: %s" % self.action)
        if (self.task_id is None) != (self.trace_id is None):
            raise ValueError(
                "task ingress decision task and trace must appear together"
            )
        if self.action in {"start_task", "resume_task", "notify_task"} and (
            self.reason_code in {"matched_rule", "matched_registered_task"}
        ):
            if (
                self.domain_contract_pack_revision is None
                or self.task_id is None
                or self.trace_id is None
            ):
                raise ValueError(
                    "accepted task start requires contract revision and lineage"
                )
        payload = self._identity_payload()
        object.__setattr__(self, "decision_id", _decision_id(payload))

    def _identity_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "environment_ingress_id": self.environment_ingress_id,
            "environment_ingress_artifact_id": self.environment_ingress_artifact_id,
            "environment_run_id": self.environment_run_id,
            "action": self.action,
            "reason_code": self.reason_code,
            "domain_contract_pack_revision": self.domain_contract_pack_revision,
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "task_status": self.task_status,
        }

    def verify_identity(self) -> None:
        if self.decision_id != _decision_id(self._identity_payload()):
            raise ValueError("task ingress decision identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {"decision_id": self.decision_id, **self._identity_payload()}


def _decision_id(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "task-ingress-decision:sha256:%s" % hashlib.sha256(encoded).hexdigest()


class TaskIngressPolicy:
    """Apply frozen domain rules to ingress for one active environment run."""

    def __init__(
        self,
        *,
        environment_profile_id: str,
        domain_contract_pack: DomainContractPack,
        task_registry: EnvironmentTaskRegistry | None = None,
    ) -> None:
        self.environment_profile_id = environment_profile_id
        self.domain_contract_pack = domain_contract_pack
        self._task_registry = task_registry
        self._rules: dict[tuple[str, str], TaskIngressRule] = {}
        for rule in domain_contract_pack.ingress_rules:
            if rule.action in {"start_task", "resume_task", "notify_task"} and (
                task_registry is None
            ):
                raise ValueError(
                    "task-bearing ingress action requires a task registry: %s"
                    % rule.action
                )
            key = (rule.binding_id, rule.ingress_type)
            if key in self._rules:
                raise ValueError(
                    "ingress rule already registered: %s / %s"
                    % (rule.binding_id, rule.ingress_type)
                )
            self._rules[key] = rule

    def classify(
        self,
        environment_run: EnvironmentRun,
        ingress: EnvironmentIngress,
    ) -> TaskIngressDecision:
        ingress.verify_identity()
        if (
            self.environment_profile_id
            != environment_run.attestation.environment_profile_id
        ):
            return self._decision(
                environment_run,
                ingress,
                "reject",
                "policy_environment_profile_mismatch",
            )
        if (
            self.domain_contract_pack.revision
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
            return self._classify_start(environment_run, ingress, rule)
        if rule.action in {"resume_task", "notify_task"}:
            return self._classify_existing(environment_run, ingress, rule)
        return self._decision(environment_run, ingress, rule.action, "matched_rule")

    def _classify_start(
        self,
        environment_run: EnvironmentRun,
        ingress: EnvironmentIngress,
        rule: TaskIngressRule,
    ) -> TaskIngressDecision:
        task_id = dict(ingress.native_lineage).get(rule.task_id_lineage_key)
        if task_id is None:
            return self._decision(
                environment_run,
                ingress,
                "reject",
                "missing_task_identity",
            )
        trace_id = _trace_id_for(environment_run.environment_run_id, task_id)
        accepted = self._decision(
            environment_run,
            ingress,
            rule.action,
            "matched_rule",
            domain_contract_pack_revision=self.domain_contract_pack.revision,
            task_id=task_id,
            trace_id=trace_id,
        )
        lineage = TaskLineage(
            environment_run_id=environment_run.environment_run_id,
            task_id=task_id,
            trace_id=trace_id,
            starting_environment_ingress_id=ingress.environment_ingress_id,
            starting_ingress_artifact_id=ingress.ingress_artifact_id,
            starting_decision_id=accepted.decision_id,
            domain_contract_pack_revision=self.domain_contract_pack.revision,
        )
        if self._task_registry is None:
            raise RuntimeError("task-bearing ingress requires a task registry")
        try:
            self._task_registry._record_policy_start(lineage)
        except DuplicateEnvironmentIngressError as exc:
            return self._lineage_rejection(
                environment_run,
                ingress,
                "duplicate_environment_ingress",
                exc.lineage,
            )
        except TaskAlreadyRegisteredError as exc:
            return self._lineage_rejection(
                environment_run,
                ingress,
                "task_already_registered",
                exc.lineage,
            )
        return accepted

    def _classify_existing(
        self,
        environment_run: EnvironmentRun,
        ingress: EnvironmentIngress,
        rule: TaskIngressRule,
    ) -> TaskIngressDecision:
        task_id = dict(ingress.native_lineage).get(rule.task_id_lineage_key)
        if task_id is None:
            return self._decision(
                environment_run,
                ingress,
                "reject",
                "missing_task_identity",
            )
        accepted = self._decision(
            environment_run,
            ingress,
            rule.action,
            "matched_registered_task",
            domain_contract_pack_revision=self.domain_contract_pack.revision,
            task_id=task_id,
            trace_id=_trace_id_for(environment_run.environment_run_id, task_id),
        )
        if self._task_registry is None:
            raise RuntimeError("task-bearing ingress requires a task registry")
        try:
            lineage = self._task_registry.register_existing_ingress(
                environment_run_id=environment_run.environment_run_id,
                environment_ingress_id=ingress.environment_ingress_id,
                ingress_artifact_id=ingress.ingress_artifact_id,
                decision_id=accepted.decision_id,
                domain_contract_pack_revision=self.domain_contract_pack.revision,
                task_id=task_id,
                trace_id=accepted.trace_id,
                ingress_action=rule.action,
            )
        except DuplicateEnvironmentIngressError as exc:
            return self._lineage_rejection(
                environment_run,
                ingress,
                "duplicate_environment_ingress",
                exc.lineage,
            )
        except UnknownTaskError:
            return self._decision(
                environment_run,
                ingress,
                "reject",
                "unknown_task_identity",
            )
        except TaskTerminalError as exc:
            return self._lineage_rejection(
                environment_run,
                ingress,
                "task_terminal",
                exc.lineage,
                task_status=exc.status,
            )
        if accepted.task_id != lineage.task_id or accepted.trace_id != lineage.trace_id:
            raise ValueError("existing-task decision does not match lineage")
        return accepted

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
