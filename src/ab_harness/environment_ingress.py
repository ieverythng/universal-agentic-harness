"""Deterministic classification of normalized environment stimuli."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from ab_harness._content_addressing import content_id
from ab_harness.domain_contracts import IngressAction


ENVIRONMENT_INGRESS_SCHEMA = "uah.environment_ingress/v1"
TASK_INGRESS_DECISION_SCHEMA = "uah.task_ingress_decision/v1"


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
    return content_id("environment-ingress", payload)


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
    return content_id("task-ingress-decision", payload)
