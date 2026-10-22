"""Portable environment-owner adapter used by the synthetic H1 runtime."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import replace
import hashlib
import json
import math
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
    from ab_harness.proposal_admission import AdmittedOperation
    from ab_harness.runtime_controls import ExecutionCancellationDecision


Handler = Callable[[dict[str, Any]], OwnerExecutionResult]
EXECUTION_RECEIPT_SCHEMA = "uah.execution_receipt/v1"
EVIDENCE_REJECTION_SCHEMA = "uah.evidence_rejection/v1"


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
        "owner_result": _owner_result_payload(owner_result),
        "evidence": _effect_evidence_payload(evidence),
    }


def _owner_result_payload(owner_result: OwnerExecutionResult) -> dict[str, object]:
    return {
        "evidence_ref": owner_result.evidence_ref,
        "succeeded": owner_result.succeeded,
        "observed_effects": list(owner_result.observed_effects),
        "payload": owner_result.payload,
    }


def _effect_evidence_payload(evidence: EffectEvidence) -> dict[str, object]:
    return {
        "evidence_ref": evidence.evidence_ref,
        "object_id": evidence.object_id,
        "binding_id": evidence.binding_id,
        "environment_id": evidence.environment_id,
        "owner": evidence.owner,
        "succeeded": evidence.succeeded,
        "observed_effects": list(evidence.observed_effects),
        "payload": evidence.payload,
    }


def _validate_json_value(value: object, *, path: str) -> None:
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float:
        if math.isfinite(value):
            return
        raise ValueError("execution result must contain finite JSON values")
    if type(value) is list:
        for index, item in enumerate(value):
            _validate_json_value(item, path="%s[%s]" % (path, index))
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("execution result mapping keys must be strings")
            _validate_json_value(item, path="%s.%s" % (path, key))
        return
    raise ValueError("execution result must contain JSON values")


def _validate_json_object(value: object, *, field_name: str) -> None:
    if type(value) is not dict:
        raise ValueError("execution receipt %s must be JSON objects" % field_name)
    _validate_json_value(value, path=field_name)


def _validate_owner_result(owner_result: OwnerExecutionResult) -> None:
    if type(owner_result) is not OwnerExecutionResult:
        raise ValueError("execution owner result has an invalid type")
    if type(owner_result.evidence_ref) is not str:
        raise ValueError("execution receipt evidence references must be strings")
    if type(owner_result.succeeded) is not bool:
        raise ValueError("execution receipt success values must be booleans")
    if type(owner_result.observed_effects) is not tuple or any(
        type(effect) is not str for effect in owner_result.observed_effects
    ):
        raise ValueError("execution receipt effects must be tuples of strings")
    _validate_json_object(owner_result.payload, field_name="owner payloads")


def _validate_effect_evidence(evidence: EffectEvidence) -> None:
    if type(evidence) is not EffectEvidence:
        raise ValueError("normalized effect evidence has an invalid type")
    if any(
        type(value) is not str
        for value in (
            evidence.evidence_ref,
            evidence.object_id,
            evidence.binding_id,
            evidence.environment_id,
            evidence.owner,
        )
    ):
        raise ValueError("execution receipt evidence fields must be strings")
    if type(evidence.succeeded) is not bool:
        raise ValueError("execution receipt success values must be booleans")
    if type(evidence.observed_effects) is not tuple or any(
        type(effect) is not str for effect in evidence.observed_effects
    ):
        raise ValueError("execution receipt effects must be tuples of strings")
    _validate_json_object(evidence.payload, field_name="evidence payloads")


def _canonical_json_bytes(value: object) -> bytes:
    _validate_json_value(value, path="execution result")
    try:
        encoded = json.dumps(
            value,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("execution result must contain finite JSON values") from exc
    return encoded


def _same_json_value(left: object, right: object) -> bool:
    return _canonical_json_bytes(left) == _canonical_json_bytes(right)


def _receipt_id(payload: dict[str, object]) -> str:
    encoded = _canonical_json_bytes(payload)
    return "execution-receipt:sha256:%s" % hashlib.sha256(encoded).hexdigest()


def _evidence_rejection_id(payload: dict[str, object]) -> str:
    try:
        encoded = json.dumps(
            payload,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("evidence rejection must contain finite JSON values") from exc
    return "evidence-rejection:sha256:%s" % hashlib.sha256(encoded).hexdigest()


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
            "owner_result": _owner_result_payload(self.owner_result),
            "evidence": _effect_evidence_payload(self.evidence),
        }

    def verify_identity(self) -> None:
        if type(self) is not ExecutionReceipt:
            raise ValueError("execution receipt must use the concrete receipt type")
        if any(
            type(getattr(self, name)) is not str
            for name in (
                "execution_result_id",
                "execution_lease_id",
                "admission_id",
                "environment_run_id",
                "task_id",
                "trace_id",
                "operation_id",
            )
        ):
            raise ValueError("execution receipt fields must be strings")
        _validate_owner_result(self.owner_result)
        _validate_effect_evidence(self.evidence)
        if self.execution_result_id != _receipt_id(
            ExecutionReceipt._identity_payload(self)
        ):
            raise ValueError("execution receipt identity does not match content")
        mismatched_owner_result_fields = []
        for name in ("evidence_ref", "succeeded", "observed_effects"):
            if getattr(self.owner_result, name) != getattr(self.evidence, name):
                mismatched_owner_result_fields.append(name)
        if not _same_json_value(self.owner_result.payload, self.evidence.payload):
            mismatched_owner_result_fields.append("payload")
        if mismatched_owner_result_fields:
            raise ValueError(
                "execution evidence does not match owner result: %s"
                % ", ".join(mismatched_owner_result_fields)
            )

    @classmethod
    def verified_copy(cls, receipt: ExecutionReceipt) -> ExecutionReceipt:
        """Validate and detach a receipt before a trusted ledger consumes it."""
        if cls is not ExecutionReceipt or type(receipt) is not ExecutionReceipt:
            raise ValueError("execution receipt must use the concrete receipt type")

        owner_result = object.__getattribute__(receipt, "owner_result")
        evidence = object.__getattribute__(receipt, "evidence")
        _validate_owner_result(owner_result)
        _validate_effect_evidence(evidence)

        owner_result_copy = OwnerExecutionResult(
            evidence_ref=object.__getattribute__(owner_result, "evidence_ref"),
            succeeded=object.__getattribute__(owner_result, "succeeded"),
            observed_effects=object.__getattribute__(owner_result, "observed_effects"),
            payload=json.loads(
                _canonical_json_bytes(object.__getattribute__(owner_result, "payload"))
            ),
        )
        evidence_copy = EffectEvidence(
            evidence_ref=object.__getattribute__(evidence, "evidence_ref"),
            object_id=object.__getattribute__(evidence, "object_id"),
            binding_id=object.__getattribute__(evidence, "binding_id"),
            environment_id=object.__getattribute__(evidence, "environment_id"),
            owner=object.__getattribute__(evidence, "owner"),
            succeeded=object.__getattribute__(evidence, "succeeded"),
            observed_effects=object.__getattribute__(evidence, "observed_effects"),
            payload=json.loads(
                _canonical_json_bytes(object.__getattribute__(evidence, "payload"))
            ),
        )
        verified = cls(
            execution_result_id=object.__getattribute__(
                receipt, "execution_result_id"
            ),
            execution_lease_id=object.__getattribute__(receipt, "execution_lease_id"),
            admission_id=object.__getattribute__(receipt, "admission_id"),
            environment_run_id=object.__getattribute__(receipt, "environment_run_id"),
            task_id=object.__getattribute__(receipt, "task_id"),
            trace_id=object.__getattribute__(receipt, "trace_id"),
            operation_id=object.__getattribute__(receipt, "operation_id"),
            owner_result=owner_result_copy,
            evidence=evidence_copy,
            schema_version=object.__getattribute__(receipt, "schema_version"),
        )
        ExecutionReceipt.verify_identity(verified)
        return verified

    @classmethod
    def issue(
        cls,
        *,
        lease: ExecutionLease,
        owner_result: OwnerExecutionResult,
        evidence: EffectEvidence,
    ) -> ExecutionReceipt:
        _validate_owner_result(owner_result)
        _validate_effect_evidence(evidence)
        lease = ExecutionLease.verified_copy(lease)
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
        if not _same_json_value(evidence.payload, owner_result.payload):
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
        return {
            "execution_result_id": self.execution_result_id,
            **self._identity_payload(),
        }

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
        if type(owner_result["succeeded"]) is not bool or type(
            evidence["succeeded"]
        ) is not bool:
            raise ValueError("execution receipt success values must be booleans")
        if type(owner_result["payload"]) is not dict or type(
            evidence["payload"]
        ) is not dict:
            raise ValueError("execution receipt payloads must be JSON objects")
        _validate_json_object(owner_result["payload"], field_name="owner payloads")
        _validate_json_object(evidence["payload"], field_name="evidence payloads")
        for item in (owner_result, evidence):
            observed = item["observed_effects"]
            if type(observed) is not list or any(
                type(value) is not str for value in observed
            ):
                raise ValueError("execution receipt effects must be strings")
        if type(owner_result["evidence_ref"]) is not str or any(
            type(evidence[name]) is not str
            for name in (
                "evidence_ref",
                "object_id",
                "binding_id",
                "environment_id",
                "owner",
            )
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


def _evidence_rejection_payload(
    *,
    lease: ExecutionLease,
    owner_result: OwnerExecutionResult,
    reason_codes: tuple[str, ...],
) -> dict[str, object]:
    return {
        "schema_version": EVIDENCE_REJECTION_SCHEMA,
        "lease": lease.to_dict(),
        "owner_result": asdict(owner_result),
        "reason_codes": reason_codes,
    }


@dataclass(frozen=True)
class EvidenceRejection:
    """Owner result retained without accepting it as effect evidence."""

    rejection_id: str
    lease: ExecutionLease
    owner_result: OwnerExecutionResult
    reason_codes: tuple[str, ...]
    schema_version: str = EVIDENCE_REJECTION_SCHEMA

    def __post_init__(self) -> None:
        self.verify_identity()

    @classmethod
    def issue(
        cls,
        *,
        lease: ExecutionLease,
        owner_result: OwnerExecutionResult,
        reason_codes: tuple[str, ...],
    ) -> EvidenceRejection:
        lease = ExecutionLease.verified_copy(lease)
        _validate_owner_result(owner_result)
        if not isinstance(reason_codes, tuple) or not reason_codes or any(
            type(reason) is not str or not reason.strip() for reason in reason_codes
        ):
            raise ValueError("evidence rejection requires reason codes")
        fields = {
            "lease": lease,
            "owner_result": owner_result,
            "reason_codes": reason_codes,
        }
        return cls(
            rejection_id=_evidence_rejection_id(
                _evidence_rejection_payload(**fields)
            ),
            **fields,
        )

    def verify_identity(self) -> None:
        ExecutionLease.verify_identity(self.lease)
        if self.schema_version != EVIDENCE_REJECTION_SCHEMA:
            raise ValueError("unsupported evidence rejection schema")
        _validate_owner_result(self.owner_result)
        if not isinstance(self.reason_codes, tuple) or not self.reason_codes or any(
            type(reason) is not str or not reason.strip()
            for reason in self.reason_codes
        ):
            raise ValueError("evidence rejection requires reason codes")
        expected = _evidence_rejection_id(
            _evidence_rejection_payload(
                lease=self.lease,
                owner_result=self.owner_result,
                reason_codes=self.reason_codes,
            )
        )
        if self.rejection_id != expected:
            raise ValueError("evidence rejection identity does not match content")

    @property
    def execution_result_id(self) -> str:
        return self.rejection_id

    @property
    def environment_run_id(self) -> str:
        return self.lease.environment_run_id

    @property
    def task_id(self) -> str:
        return self.lease.admitted_operation.task_id

    @property
    def trace_id(self) -> str:
        return self.lease.admitted_operation.trace_id

    @property
    def operation_id(self) -> str:
        return self.lease.operation_id

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        payload = _evidence_rejection_payload(
            lease=self.lease,
            owner_result=self.owner_result,
            reason_codes=self.reason_codes,
        )
        result = dict(payload["owner_result"])
        result["observed_effects"] = list(self.owner_result.observed_effects)
        payload["owner_result"] = result
        payload["reason_codes"] = list(self.reason_codes)
        return {"rejection_id": self.rejection_id, **payload}


@dataclass(frozen=True)
class EvidenceDecision:
    """Accepted execution receipt or typed evidence-contract rejection."""

    receipt: ExecutionReceipt | None = None
    rejection: EvidenceRejection | None = None

    def __post_init__(self) -> None:
        if (self.receipt is None) == (self.rejection is None):
            raise ValueError("evidence decision requires receipt or rejection")

    @property
    def accepted(self) -> bool:
        return self.receipt is not None


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
    if item.runtime_callable is not True:
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
) -> tuple[OwnerExecutionResult, EffectEvidence, tuple[str, ...]]:
    result = handler(dict(arguments))
    if type(result) is not OwnerExecutionResult:
        raise TypeError("environment handler must return OwnerExecutionResult")
    if type(result.succeeded) is not bool:
        raise TypeError("environment handler succeeded must be a boolean")
    _validate_owner_result(result)
    reasons: list[str] = []
    if not result.evidence_ref.strip():
        reasons.append("missing_evidence_reference")
    undeclared = tuple(
        effect
        for effect in result.observed_effects
        if effect not in item.observable_success
    )
    if undeclared:
        reasons.append("undeclared_observed_effect")
    if result.succeeded and item.observable_success and not result.observed_effects:
        reasons.append("successful_result_without_observable")

    evidence = EffectEvidence(
        evidence_ref=result.evidence_ref,
        object_id=item.object_id,
        binding_id=binding.binding_id,
        environment_id=environment_id,
        owner=item.owner_package,
        succeeded=result.succeeded,
        observed_effects=result.observed_effects,
        payload=result.payload,
    )
    return result, evidence, tuple(reasons)


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

    def execute(self, lease: ExecutionLease) -> EvidenceDecision:
        lease = ExecutionLease.verified_copy(lease)
        admitted = self._validate_lease(lease)
        if self._catalog.object_for(admitted.object_id) != admitted.object_snapshot:
            raise ValueError("execution lease object semantics no longer match the catalog")

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
            owner_result, evidence, rejection_reasons = _execute_handler(
                environment_id=self.environment_id,
                item=replace(admitted.object_snapshot),
                binding=binding,
                handler=handler,
                arguments=admitted.arguments,
            )
            if rejection_reasons:
                rejection = EvidenceRejection.issue(
                    lease=lease,
                    owner_result=owner_result,
                    reason_codes=rejection_reasons,
                )
                self._lifecycle_ledger.record(rejection)
                return EvidenceDecision(rejection=rejection)
            receipt = ExecutionReceipt.issue(
                lease=lease,
                owner_result=owner_result,
                evidence=evidence,
            )
        except Exception as exc:
            self._lifecycle_ledger.fail_execution(lease, exc)
            raise
        self._lifecycle_ledger.complete_execution(receipt)
        return EvidenceDecision(receipt=receipt)

    def cancel(
        self,
        lease: ExecutionLease,
        *,
        requester_id: str,
        request_artifact_id: str,
        reason_code: str,
    ) -> ExecutionCancellationDecision:
        self._validate_lease(lease)
        from ab_harness.runtime_controls import ExecutionCancellationDecision

        decision = ExecutionCancellationDecision.issue(
            lease=lease,
            requester_id=requester_id,
            request_artifact_id=request_artifact_id,
            deciding_owner_id=self.environment_run.attestation.environment_owner_id,
            reason_code=reason_code,
        )
        self._lifecycle_ledger.record(decision)
        return decision

    def _validate_lease(self, lease: ExecutionLease) -> AdmittedOperation:
        if not isinstance(lease, ExecutionLease):
            raise TypeError("lease-bound owner requires an ExecutionLease")
        ExecutionLease.verify_identity(lease)
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
        self._lifecycle_ledger.require_current_admission(admitted)
        return admitted
