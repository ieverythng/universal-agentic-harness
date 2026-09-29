"""Portable environment-owner adapter used by the synthetic H1 runtime."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import asdict
from dataclasses import dataclass
import hashlib
import json
from typing import Any, TYPE_CHECKING

from ab_harness.bindings import BindingCatalog
from ab_harness.bindings import binding_fingerprint
from ab_harness.contracts import ABImplementationBinding
from ab_harness.contracts import ABObjectView
from ab_harness.contracts import EffectEvidence, OwnerExecutionResult
from ab_harness.domain_lifecycle import ExecutionLease
from ab_harness.environment_runs import EnvironmentRun

if TYPE_CHECKING:
    from ab_harness.lifecycle import LifecycleLedger


Handler = Callable[[dict[str, Any]], OwnerExecutionResult]
EXECUTION_RECEIPT_SCHEMA = "uah.execution_receipt/v1"


def _receipt_payload(
    *,
    lease: ExecutionLease,
    owner_result: OwnerExecutionResult,
    evidence: EffectEvidence,
) -> dict[str, object]:
    return {
        "schema_version": EXECUTION_RECEIPT_SCHEMA,
        "execution_lease_id": lease.execution_lease_id,
        "admission_id": lease.admission_id,
        "environment_run_id": lease.environment_run_id,
        "task_id": lease.admitted_operation.task_id,
        "trace_id": lease.admitted_operation.trace_id,
        "operation_id": lease.operation_id,
        "owner_result": asdict(owner_result),
        "evidence": asdict(evidence),
    }


def _receipt_id(payload: dict[str, object]) -> str:
    try:
        encoded = json.dumps(
            payload,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("execution result must contain finite JSON values") from exc
    return "execution-receipt:sha256:%s" % hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ExecutionReceipt:
    """Content-addressed native result and normalized owner evidence."""

    execution_result_id: str
    execution_lease_id: str
    admission_id: str
    environment_run_id: str
    task_id: str
    trace_id: str
    operation_id: str
    owner_result: OwnerExecutionResult
    evidence: EffectEvidence
    schema_version: str = EXECUTION_RECEIPT_SCHEMA

    def __post_init__(self) -> None:
        if self.schema_version != EXECUTION_RECEIPT_SCHEMA:
            raise ValueError(
                "unsupported execution receipt schema: %s" % self.schema_version
            )
        self.verify_identity()

    def _identity_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "execution_lease_id": self.execution_lease_id,
            "admission_id": self.admission_id,
            "environment_run_id": self.environment_run_id,
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "operation_id": self.operation_id,
            "owner_result": asdict(self.owner_result),
            "evidence": asdict(self.evidence),
        }

    def verify_identity(self) -> None:
        if self.execution_result_id != _receipt_id(self._identity_payload()):
            raise ValueError("execution receipt identity does not match content")

    @classmethod
    def issue(
        cls,
        *,
        lease: ExecutionLease,
        owner_result: OwnerExecutionResult,
        evidence: EffectEvidence,
    ) -> ExecutionReceipt:
        lease.verify_identity()
        admitted = lease.admitted_operation
        mismatched = []
        if evidence.object_id != admitted.object_id:
            mismatched.append("object_id")
        if evidence.binding_id != admitted.binding_id:
            mismatched.append("binding_id")
        if evidence.environment_id != admitted.environment_id:
            mismatched.append("environment_id")
        if evidence.owner != admitted.binding_owner:
            mismatched.append("owner")
        if evidence.evidence_ref != owner_result.evidence_ref:
            mismatched.append("evidence_ref")
        if evidence.succeeded != owner_result.succeeded:
            mismatched.append("succeeded")
        if evidence.observed_effects != owner_result.observed_effects:
            mismatched.append("observed_effects")
        if evidence.payload != owner_result.payload:
            mismatched.append("payload")
        if mismatched:
            raise ValueError(
                "execution evidence does not match lease and owner result: %s"
                % ", ".join(mismatched)
            )
        payload = _receipt_payload(
            lease=lease,
            owner_result=owner_result,
            evidence=evidence,
        )
        return cls(
            execution_result_id=_receipt_id(payload),
            execution_lease_id=lease.execution_lease_id,
            admission_id=lease.admission_id,
            environment_run_id=lease.environment_run_id,
            task_id=lease.admitted_operation.task_id,
            trace_id=lease.admitted_operation.trace_id,
            operation_id=lease.operation_id,
            owner_result=owner_result,
            evidence=evidence,
        )

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        payload = self._identity_payload()
        owner_result = dict(payload["owner_result"])
        owner_result["observed_effects"] = list(self.owner_result.observed_effects)
        evidence = dict(payload["evidence"])
        evidence["observed_effects"] = list(self.evidence.observed_effects)
        payload["owner_result"] = owner_result
        payload["evidence"] = evidence
        return {"execution_result_id": self.execution_result_id, **payload}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> ExecutionReceipt:
        expected = {
            "execution_result_id",
            "schema_version",
            "execution_lease_id",
            "admission_id",
            "environment_run_id",
            "task_id",
            "trace_id",
            "operation_id",
            "owner_result",
            "evidence",
        }
        if set(payload) != expected:
            raise ValueError("invalid execution receipt fields")
        scalar_names = expected - {"owner_result", "evidence"}
        if any(not isinstance(payload[name], str) for name in scalar_names):
            raise ValueError("execution receipt fields have invalid types")
        owner_result = payload["owner_result"]
        evidence = payload["evidence"]
        if not isinstance(owner_result, dict) or set(owner_result) != {
            "evidence_ref",
            "succeeded",
            "observed_effects",
            "payload",
        }:
            raise ValueError("invalid execution owner result")
        if not isinstance(evidence, dict) or set(evidence) != {
            "evidence_ref",
            "object_id",
            "binding_id",
            "environment_id",
            "owner",
            "succeeded",
            "observed_effects",
            "payload",
        }:
            raise ValueError("invalid normalized effect evidence")
        if not isinstance(owner_result["succeeded"], bool) or not isinstance(
            evidence["succeeded"], bool
        ):
            raise ValueError("execution receipt success values must be booleans")
        if not isinstance(owner_result["payload"], dict) or not isinstance(
            evidence["payload"], dict
        ):
            raise ValueError("execution receipt payloads must be JSON objects")
        for item in (owner_result, evidence):
            observed = item["observed_effects"]
            if not isinstance(observed, list) or any(
                not isinstance(value, str) for value in observed
            ):
                raise ValueError("execution receipt effects must be strings")
        evidence_strings = (
            "evidence_ref",
            "object_id",
            "binding_id",
            "environment_id",
            "owner",
        )
        if not isinstance(owner_result["evidence_ref"], str) or any(
            not isinstance(evidence[name], str) for name in evidence_strings
        ):
            raise ValueError("execution receipt evidence fields must be strings")
        return cls(
            execution_result_id=payload["execution_result_id"],
            execution_lease_id=payload["execution_lease_id"],
            admission_id=payload["admission_id"],
            environment_run_id=payload["environment_run_id"],
            task_id=payload["task_id"],
            trace_id=payload["trace_id"],
            operation_id=payload["operation_id"],
            owner_result=OwnerExecutionResult(
                evidence_ref=owner_result["evidence_ref"],
                succeeded=owner_result["succeeded"],
                observed_effects=tuple(owner_result["observed_effects"]),
                payload=dict(owner_result["payload"]),
            ),
            evidence=EffectEvidence(
                evidence_ref=evidence["evidence_ref"],
                object_id=evidence["object_id"],
                binding_id=evidence["binding_id"],
                environment_id=evidence["environment_id"],
                owner=evidence["owner"],
                succeeded=evidence["succeeded"],
                observed_effects=tuple(evidence["observed_effects"]),
                payload=dict(evidence["payload"]),
            ),
            schema_version=payload["schema_version"],
        )


def _resolve_handler(
    *,
    environment_id: str,
    catalog: BindingCatalog,
    handlers: Mapping[str, Handler],
    object_id: str,
    runtime_mode: str,
) -> tuple[ABObjectView, ABImplementationBinding, Handler]:
    item = catalog.object_for(object_id)
    if item is None:
        raise ValueError("unknown AB object: %s" % object_id)
    if not item.runtime_callable:
        raise ValueError("AB object is not runtime callable: %s" % object_id)

    binding = catalog.resolve(
        object_id,
        runtime_mode=runtime_mode,
        environment_id=environment_id,
    )
    if binding.implementation_owner != item.owner_package:
        raise ValueError(
            "binding implementation owner does not own executable AB object: %s"
            % binding.binding_id
        )
    if binding.interface_kind != "python_method":
        raise ValueError(
            "binding is not an in-process Python method: %s" % binding.binding_id
        )

    handler = handlers.get(binding.locator)
    if handler is None:
        raise LookupError("binding locator is not mounted: %s" % binding.locator)
    return item, binding, handler


def _execute_handler(
    *,
    environment_id: str,
    item: ABObjectView,
    binding: ABImplementationBinding,
    handler: Handler,
    arguments: dict[str, Any],
) -> tuple[OwnerExecutionResult, EffectEvidence]:
    result = handler(dict(arguments))
    if not isinstance(result, OwnerExecutionResult):
        raise TypeError("environment handler must return OwnerExecutionResult")
    if not result.evidence_ref.strip():
        raise ValueError("environment owner returned evidence without a reference")

    undeclared = tuple(
        effect
        for effect in result.observed_effects
        if effect not in item.observable_success
    )
    if undeclared:
        raise ValueError(
            "environment owner returned undeclared observables: %s"
            % ", ".join(undeclared)
        )
    if result.succeeded and item.observable_success and not result.observed_effects:
        raise ValueError("successful execution requires declared effect evidence")

    result = OwnerExecutionResult(
        evidence_ref=result.evidence_ref,
        succeeded=result.succeeded,
        observed_effects=tuple(result.observed_effects),
        payload=dict(result.payload),
    )
    evidence = EffectEvidence(
        evidence_ref=result.evidence_ref,
        object_id=item.object_id,
        binding_id=binding.binding_id,
        environment_id=environment_id,
        owner=item.owner_package,
        succeeded=result.succeeded,
        observed_effects=result.observed_effects,
        payload=dict(result.payload),
    )
    return result, evidence


class InProcessEnvironmentOwner:
    """Execute an admitted operation only through its domain-issued lease."""

    def __init__(
        self,
        *,
        environment_id: str,
        environment_run: EnvironmentRun,
        catalog: BindingCatalog,
        handlers: Mapping[str, Handler],
        lifecycle_ledger: LifecycleLedger,
    ) -> None:
        if not environment_id.strip():
            raise ValueError("lease-bound owner environment must not be empty")
        if environment_run.status != "active":
            raise ValueError("lease-bound owner requires an active environment run")
        self.environment_id = environment_id
        self.environment_run = environment_run
        self._catalog = catalog
        self._handlers = dict(handlers)
        self._lifecycle_ledger = lifecycle_ledger

    def execute(self, lease: ExecutionLease) -> ExecutionReceipt:
        if not isinstance(lease, ExecutionLease):
            raise TypeError("lease-bound owner requires an ExecutionLease")
        lease.verify_identity()
        if lease.environment_run_id != self.environment_run.environment_run_id:
            raise ValueError("execution lease belongs to another environment run")
        if (
            lease.environment_attestation_id
            != self.environment_run.attestation.attestation_id
        ):
            raise ValueError("execution lease has a stale environment attestation")
        if (
            lease.lease_owner_id
            != self.environment_run.attestation.environment_owner_id
        ):
            raise ValueError("execution lease belongs to another environment owner")
        admitted = lease.admitted_operation
        if admitted.environment_id != self.environment_id:
            raise ValueError("execution lease belongs to another environment")

        item, binding, handler = _resolve_handler(
            environment_id=self.environment_id,
            catalog=self._catalog,
            handlers=self._handlers,
            object_id=admitted.object_id,
            runtime_mode=admitted.runtime_mode,
        )
        if (
            binding.binding_id != admitted.binding_id
            or binding.source_revision != admitted.binding_source_revision
            or binding_fingerprint(binding) != admitted.binding_fingerprint
        ):
            raise ValueError("execution lease binding no longer matches the catalog")

        self._lifecycle_ledger.start_execution(lease)
        try:
            owner_result, evidence = _execute_handler(
                environment_id=self.environment_id,
                item=item,
                binding=binding,
                handler=handler,
                arguments=admitted.arguments,
            )
        except Exception as exc:
            self._lifecycle_ledger.fail_execution(lease, exc)
            raise
        receipt = ExecutionReceipt.issue(
            lease=lease,
            owner_result=owner_result,
            evidence=evidence,
        )
        self._lifecycle_ledger.complete_execution(receipt)
        return receipt
