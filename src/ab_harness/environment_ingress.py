"""Deterministic classification of normalized environment stimuli."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
import hashlib
import json

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

    @classmethod
    def verified_copy(cls, value: object) -> EnvironmentIngress:
        """Return a detached owner-verified copy of one ingress artifact."""
        if cls is not EnvironmentIngress:
            raise TypeError("environment ingress requires its concrete owner type")
        values = _stored_ingress_fields(value, EnvironmentIngress)
        lineage = values["native_lineage"]
        if type(lineage) is not tuple or any(
            type(item) is not tuple
            or len(item) != 2
            or any(type(part) is not str for part in item)
            for item in lineage
        ):
            raise TypeError("environment ingress lineage must contain plain pairs")
        string_fields = tuple(
            name
            for name in values
            if name not in {"native_lineage", "ingress_artifact_id"}
        )
        if any(type(values[name]) is not str for name in string_fields):
            raise TypeError("environment ingress fields must be plain strings")
        if type(values["ingress_artifact_id"]) is not str:
            raise TypeError("environment ingress identity must be a plain string")
        snapshot = EnvironmentIngress(
            **{name: values[name] for name in string_fields},
            native_lineage=tuple(tuple(item) for item in lineage),
        )
        if snapshot.ingress_artifact_id != values["ingress_artifact_id"]:
            raise ValueError("environment ingress identity does not match content")
        return snapshot

    def __post_init__(self) -> None:
        if type(self.native_lineage) is not tuple or any(
            type(item) is not tuple
            or len(item) != 2
            or any(type(part) is not str for part in item)
            for item in self.native_lineage
        ):
            raise TypeError("native lineage must be an immutable tuple of string pairs")
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
        if any(type(value) is not str for value in required.values()):
            raise TypeError("environment ingress fields must be plain strings")
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
            _ingress_artifact_id(EnvironmentIngress._identity_payload(self)),
        )

    def _identity_payload(self) -> dict[str, object]:
        if type(self) is not EnvironmentIngress:
            raise TypeError("environment ingress requires its concrete owner type")
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
        if type(self) is not EnvironmentIngress:
            raise TypeError("environment ingress requires its concrete owner type")
        if self.ingress_artifact_id != _ingress_artifact_id(
            EnvironmentIngress._identity_payload(self)
        ):
            raise ValueError("environment ingress identity does not match content")

    def to_dict(self) -> dict[str, object]:
        snapshot = EnvironmentIngress.verified_copy(self)
        payload = EnvironmentIngress._identity_payload(snapshot)
        payload["native_lineage"] = [list(item) for item in snapshot.native_lineage]
        return {"ingress_artifact_id": snapshot.ingress_artifact_id, **payload}


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

    @classmethod
    def verified_copy(cls, value: object) -> TaskIngressDecision:
        """Return a detached owner-verified copy of one ingress decision."""
        if cls is not TaskIngressDecision:
            raise TypeError("task ingress decision requires its concrete owner type")
        values = _stored_ingress_fields(value, TaskIngressDecision)
        for name, item in values.items():
            if name in {"action", "decision_id"}:
                continue
            if item is not None and type(item) is not str:
                raise TypeError("task ingress decision fields must be plain strings")
        if type(values["action"]) is not str:
            raise TypeError("task ingress decision action must be a plain string")
        if type(values["decision_id"]) is not str:
            raise TypeError("task ingress decision identity must be a plain string")
        snapshot = TaskIngressDecision(
            **{
                name: item
                for name, item in values.items()
                if name not in {"decision_id"}
            }
        )
        if snapshot.decision_id != values["decision_id"]:
            raise ValueError("task ingress decision identity does not match content")
        return snapshot

    def __post_init__(self) -> None:
        required = {
            "environment_ingress_id": self.environment_ingress_id,
            "environment_ingress_artifact_id": self.environment_ingress_artifact_id,
            "environment_run_id": self.environment_run_id,
            "reason_code": self.reason_code,
        }
        if any(type(value) is not str for value in required.values()):
            raise TypeError("task ingress decision fields must be plain strings")
        for value in (
            self.domain_contract_pack_revision,
            self.task_id,
            self.trace_id,
            self.task_status,
        ):
            if value is not None and type(value) is not str:
                raise TypeError("task ingress decision fields must be plain strings")
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
        if type(self.action) is not str or self.action not in {
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
        payload = TaskIngressDecision._identity_payload(self)
        object.__setattr__(self, "decision_id", _decision_id(payload))

    def _identity_payload(self) -> dict[str, object]:
        if type(self) is not TaskIngressDecision:
            raise TypeError("task ingress decision requires its concrete owner type")
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
        if type(self) is not TaskIngressDecision:
            raise TypeError("task ingress decision requires its concrete owner type")
        if self.decision_id != _decision_id(
            TaskIngressDecision._identity_payload(self)
        ):
            raise ValueError("task ingress decision identity does not match content")

    def to_dict(self) -> dict[str, object]:
        snapshot = TaskIngressDecision.verified_copy(self)
        return {
            "decision_id": snapshot.decision_id,
            **TaskIngressDecision._identity_payload(snapshot),
        }


def _stored_ingress_fields(value: object, expected_type: type) -> dict[str, object]:
    if type(value) is not expected_type:
        raise TypeError("ingress artifacts require their concrete owner type")
    stored = object.__getattribute__(value, "__dict__")
    names = tuple(item.name for item in fields(expected_type))
    if type(stored) is not dict or set(stored) != set(names):
        raise ValueError("ingress artifact identity does not match content")
    return {name: stored[name] for name in names}


def _decision_id(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "task-ingress-decision:sha256:%s" % hashlib.sha256(encoded).hexdigest()
