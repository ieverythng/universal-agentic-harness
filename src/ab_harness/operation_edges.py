"""Frame-relative relationships between recorded UAH operations."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Literal


OPERATION_EDGE_SCHEMA = "uah.operation_edge/v1"
OperationRelation = Literal["decomposes_to", "delegates_to", "continues_with"]


def _edge_payload(
    *,
    environment_run_id: str,
    task_id: str,
    trace_id: str,
    source_operation_id: str,
    target_operation_id: str,
    relation: OperationRelation,
    source_frame_id: str,
    target_frame_id: str,
    artifact_contract_ref: str | None,
) -> dict[str, object]:
    return {
        "schema_version": OPERATION_EDGE_SCHEMA,
        "environment_run_id": environment_run_id,
        "task_id": task_id,
        "trace_id": trace_id,
        "source_operation_id": source_operation_id,
        "target_operation_id": target_operation_id,
        "relation": relation,
        "source_frame_id": source_frame_id,
        "target_frame_id": target_frame_id,
        "artifact_contract_ref": artifact_contract_ref,
    }


def _edge_id(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "operation-edge:sha256:%s" % hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class OperationEdge:
    """One immutable relationship that grants no operation authority."""

    edge_id: str
    environment_run_id: str
    task_id: str
    trace_id: str
    source_operation_id: str
    target_operation_id: str
    relation: OperationRelation
    source_frame_id: str
    target_frame_id: str
    artifact_contract_ref: str | None = None
    schema_version: str = OPERATION_EDGE_SCHEMA

    def __post_init__(self) -> None:
        self.verify_identity()

    @classmethod
    def issue(
        cls,
        *,
        environment_run_id: str,
        task_id: str,
        trace_id: str,
        source_operation_id: str,
        target_operation_id: str,
        relation: OperationRelation,
        source_frame_id: str,
        target_frame_id: str,
        artifact_contract_ref: str | None = None,
    ) -> OperationEdge:
        fields = {
            "environment_run_id": environment_run_id,
            "task_id": task_id,
            "trace_id": trace_id,
            "source_operation_id": source_operation_id,
            "target_operation_id": target_operation_id,
            "relation": relation,
            "source_frame_id": source_frame_id,
            "target_frame_id": target_frame_id,
            "artifact_contract_ref": artifact_contract_ref,
        }
        return cls(edge_id=_edge_id(_edge_payload(**fields)), **fields)

    def verify_identity(self) -> None:
        if self.schema_version != OPERATION_EDGE_SCHEMA:
            raise ValueError("unsupported operation edge schema")
        required = {
            "environment_run_id": self.environment_run_id,
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "source_operation_id": self.source_operation_id,
            "target_operation_id": self.target_operation_id,
            "source_frame_id": self.source_frame_id,
            "target_frame_id": self.target_frame_id,
        }
        missing = tuple(name for name, value in required.items() if not value.strip())
        if missing:
            raise ValueError(
                "operation edge fields must not be empty: %s" % ", ".join(missing)
            )
        if self.source_operation_id == self.target_operation_id:
            raise ValueError("operation edge cannot target itself")
        if self.relation not in {
            "decomposes_to",
            "delegates_to",
            "continues_with",
        }:
            raise ValueError("unsupported operation edge relation")
        if (
            self.relation in {"decomposes_to", "continues_with"}
            and self.source_frame_id != self.target_frame_id
        ):
            raise ValueError("non-delegation edge must remain in one frame")
        if self.relation == "delegates_to":
            if self.source_frame_id == self.target_frame_id:
                raise ValueError("delegation must cross frames")
            if self.artifact_contract_ref is None or not self.artifact_contract_ref.strip():
                raise ValueError("delegation requires an artifact contract")
        elif self.artifact_contract_ref is not None:
            raise ValueError("artifact contract is valid only for delegation")
        payload = _edge_payload(
            environment_run_id=self.environment_run_id,
            task_id=self.task_id,
            trace_id=self.trace_id,
            source_operation_id=self.source_operation_id,
            target_operation_id=self.target_operation_id,
            relation=self.relation,
            source_frame_id=self.source_frame_id,
            target_frame_id=self.target_frame_id,
            artifact_contract_ref=self.artifact_contract_ref,
        )
        if self.edge_id != _edge_id(payload):
            raise ValueError("operation edge identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {
            "edge_id": self.edge_id,
            **_edge_payload(
                environment_run_id=self.environment_run_id,
                task_id=self.task_id,
                trace_id=self.trace_id,
                source_operation_id=self.source_operation_id,
                target_operation_id=self.target_operation_id,
                relation=self.relation,
                source_frame_id=self.source_frame_id,
                target_frame_id=self.target_frame_id,
                artifact_contract_ref=self.artifact_contract_ref,
            ),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> OperationEdge:
        expected = {
            "edge_id",
            "schema_version",
            "environment_run_id",
            "task_id",
            "trace_id",
            "source_operation_id",
            "target_operation_id",
            "relation",
            "source_frame_id",
            "target_frame_id",
            "artifact_contract_ref",
        }
        if set(payload) != expected:
            raise ValueError("invalid operation edge fields")
        nullable = payload["artifact_contract_ref"]
        if nullable is not None and not isinstance(nullable, str):
            raise ValueError("operation edge artifact contract must be a string or null")
        string_fields = expected - {"artifact_contract_ref"}
        if any(not isinstance(payload[name], str) for name in string_fields):
            raise ValueError("operation edge fields must be strings")
        return cls(**payload)  # type: ignore[arg-type]
