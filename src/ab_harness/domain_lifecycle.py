"""Domain-owned execution admission for semantically admitted operations."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json

from ab_harness.environment_runs import EnvironmentRun
from ab_harness.lifecycle import LifecycleSequenceConflict
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.proposal_admission import AdmittedOperation


EXECUTION_LEASE_SCHEMA = "uah.execution_lease/v1"
DOMAIN_ADMISSION_REJECTION_SCHEMA = "uah.domain_admission_rejection/v1"


def _lease_payload(
    *,
    admitted_operation: AdmittedOperation,
    lease_owner_id: str,
    environment_attestation_id: str,
) -> dict[str, object]:
    return {
        "schema_version": EXECUTION_LEASE_SCHEMA,
        "admitted_operation": AdmittedOperation.to_dict(admitted_operation),
        "lease_owner_id": lease_owner_id,
        "environment_attestation_id": environment_attestation_id,
        "scope": "operation",
    }


def _lease_id(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "execution-lease:sha256:%s" % hashlib.sha256(encoded).hexdigest()


def _domain_rejection_id(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "domain-rejection:sha256:%s" % hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ExecutionLease:
    """Domain-issued authority for exactly one admitted operation."""

    execution_lease_id: str
    admitted_operation: AdmittedOperation
    lease_owner_id: str
    environment_attestation_id: str
    scope: str = "operation"
    schema_version: str = EXECUTION_LEASE_SCHEMA

    def __post_init__(self) -> None:
        self.verify_identity()

    def verify_identity(self) -> None:
        if type(self) is not ExecutionLease:
            raise ValueError("current execution requires the supported concrete lease")
        AdmittedOperation.verify_identity(self.admitted_operation)
        if self.schema_version != EXECUTION_LEASE_SCHEMA:
            raise ValueError(
                "unsupported execution lease schema: %s" % self.schema_version
            )
        if not self.lease_owner_id.strip():
            raise ValueError("execution lease owner must not be empty")
        if not self.environment_attestation_id.strip():
            raise ValueError("execution lease attestation must not be empty")
        if self.scope != "operation":
            raise ValueError("execution lease scope must be operation")
        payload = _lease_payload(
            admitted_operation=self.admitted_operation,
            lease_owner_id=self.lease_owner_id,
            environment_attestation_id=self.environment_attestation_id,
        )
        if self.execution_lease_id != _lease_id(payload):
            raise ValueError("execution lease identity does not match content")

    @property
    def admission_id(self) -> str:
        return self.admitted_operation.admission_id

    @property
    def environment_run_id(self) -> str:
        return self.admitted_operation.environment_run_id

    @property
    def operation_id(self) -> str:
        return self.admitted_operation.operation_id

    @property
    def object_id(self) -> str:
        return self.admitted_operation.object_id

    @property
    def binding_id(self) -> str:
        return self.admitted_operation.binding_id

    @property
    def runtime_mode(self) -> str:
        return self.admitted_operation.runtime_mode

    def verified_copy(self) -> ExecutionLease:
        if type(self) is not ExecutionLease:
            raise ValueError("current execution requires the supported concrete lease")
        return replace(
            self,
            admitted_operation=AdmittedOperation.verified_copy(self.admitted_operation),
        )

    def to_dict(self) -> dict[str, object]:
        ExecutionLease.verify_identity(self)
        return {
            "execution_lease_id": self.execution_lease_id,
            **_lease_payload(
                admitted_operation=self.admitted_operation,
                lease_owner_id=self.lease_owner_id,
                environment_attestation_id=self.environment_attestation_id,
            ),
        }


def _new_execution_lease(
    *,
    admitted_operation: AdmittedOperation,
    lease_owner_id: str,
    environment_attestation_id: str,
) -> ExecutionLease:
    payload = _lease_payload(
        admitted_operation=admitted_operation,
        lease_owner_id=lease_owner_id,
        environment_attestation_id=environment_attestation_id,
    )
    return ExecutionLease(
        execution_lease_id=_lease_id(payload),
        admitted_operation=admitted_operation,
        lease_owner_id=lease_owner_id,
        environment_attestation_id=environment_attestation_id,
    )


def _domain_rejection_payload(
    *,
    admitted_operation: AdmittedOperation,
    environment_run_id: str,
    environment_id: str,
    environment_attestation_id: str,
    reason_codes: tuple[str, ...],
) -> dict[str, object]:
    return {
        "schema_version": DOMAIN_ADMISSION_REJECTION_SCHEMA,
        "admitted_operation": AdmittedOperation.to_dict(admitted_operation),
        "environment_run_id": environment_run_id,
        "environment_id": environment_id,
        "environment_attestation_id": environment_attestation_id,
        "reason_codes": reason_codes,
    }


@dataclass(frozen=True)
class DomainAdmissionRejection:
    """Content-addressed domain-owner refusal to issue an execution lease."""

    rejection_id: str
    admitted_operation: AdmittedOperation
    environment_run_id: str
    environment_id: str
    environment_attestation_id: str
    reason_codes: tuple[str, ...]
    schema_version: str = DOMAIN_ADMISSION_REJECTION_SCHEMA

    def __post_init__(self) -> None:
        self.verify_identity()

    def verify_identity(self) -> None:
        AdmittedOperation.verify_identity(self.admitted_operation)
        if self.schema_version != DOMAIN_ADMISSION_REJECTION_SCHEMA:
            raise ValueError(
                "unsupported domain rejection schema: %s" % self.schema_version
            )
        required = (
            self.environment_run_id,
            self.environment_id,
            self.environment_attestation_id,
        )
        if any(not value.strip() for value in required):
            raise ValueError("domain rejection identities must not be empty")
        if not isinstance(self.reason_codes, tuple) or not self.reason_codes:
            raise ValueError("domain rejection requires ordered reason codes")
        if any(not reason.strip() for reason in self.reason_codes):
            raise ValueError("domain rejection reason codes must not be empty")
        payload = _domain_rejection_payload(
            admitted_operation=self.admitted_operation,
            environment_run_id=self.environment_run_id,
            environment_id=self.environment_id,
            environment_attestation_id=self.environment_attestation_id,
            reason_codes=self.reason_codes,
        )
        if self.rejection_id != _domain_rejection_id(payload):
            raise ValueError("domain rejection identity does not match content")

    @property
    def task_id(self) -> str:
        return self.admitted_operation.task_id

    @property
    def trace_id(self) -> str:
        return self.admitted_operation.trace_id

    @property
    def operation_id(self) -> str:
        return self.admitted_operation.operation_id

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {
            "rejection_id": self.rejection_id,
            **_domain_rejection_payload(
                admitted_operation=self.admitted_operation,
                environment_run_id=self.environment_run_id,
                environment_id=self.environment_id,
                environment_attestation_id=self.environment_attestation_id,
                reason_codes=self.reason_codes,
            ),
        }


def _new_domain_rejection(
    *,
    admitted_operation: AdmittedOperation,
    environment_run: EnvironmentRun,
    environment_id: str,
    reason_codes: tuple[str, ...],
) -> DomainAdmissionRejection:
    fields = {
        "admitted_operation": admitted_operation,
        "environment_run_id": environment_run.environment_run_id,
        "environment_id": environment_id,
        "environment_attestation_id": environment_run.attestation.attestation_id,
        "reason_codes": reason_codes,
    }
    rejection_id = _domain_rejection_id(_domain_rejection_payload(**fields))
    return DomainAdmissionRejection(rejection_id=rejection_id, **fields)


@dataclass(frozen=True)
class ExecutionLeaseDecision:
    """Execution lease or deterministic domain lifecycle rejection reasons."""

    execution_lease: ExecutionLease | None = None
    rejection: DomainAdmissionRejection | None = None

    def __post_init__(self) -> None:
        if (self.execution_lease is None) == (self.rejection is None):
            raise ValueError("lease decision must contain lease or rejection")

    @property
    def accepted(self) -> bool:
        return self.execution_lease is not None

    @property
    def reason_codes(self) -> tuple[str, ...]:
        return self.rejection.reason_codes if self.rejection is not None else ()


class DomainLifecycleAdmission:
    """Issue operation leases under one attested environment activation."""

    def __init__(
        self,
        *,
        environment_run: EnvironmentRun,
        environment_id: str,
        lifecycle_ledger: LifecycleLedger,
    ) -> None:
        if not environment_id.strip():
            raise ValueError("domain lifecycle environment id must not be empty")
        self._environment_run = environment_run
        self._environment_id = environment_id
        self._lifecycle_ledger = lifecycle_ledger

    def request_execution(
        self,
        admitted_operation: AdmittedOperation,
    ) -> ExecutionLeaseDecision:
        AdmittedOperation.verify_identity(admitted_operation)
        self._lifecycle_ledger.require_current_admission(admitted_operation)
        recorded_lease = self._lifecycle_ledger.execution_lease_identity(
            trace_id=admitted_operation.trace_id,
            operation_id=admitted_operation.operation_id,
        )
        if recorded_lease is not None:
            if (
                self._environment_run.status != "active"
                or admitted_operation.environment_run_id
                != self._environment_run.environment_run_id
                or admitted_operation.environment_id != self._environment_id
                or admitted_operation.domain_contract_pack_revision
                != self._environment_run.attestation.domain_contract_pack_revision
            ):
                raise ValueError(
                    "leased operation cannot be reconsidered under changed domain context"
                )
            lease = self._new_lease(admitted_operation)
            self._require_exact_recorded_lease(
                lease,
                recorded_lease=recorded_lease,
            )
            return ExecutionLeaseDecision(execution_lease=lease)

        reasons: list[str] = []
        if self._environment_run.status != "active":
            reasons.append("environment_run_not_active")
        if (
            admitted_operation.environment_run_id
            != self._environment_run.environment_run_id
        ):
            reasons.append("environment_run_mismatch")
        if admitted_operation.environment_id != self._environment_id:
            reasons.append("binding_environment_mismatch")
        if (
            admitted_operation.domain_contract_pack_revision
            != self._environment_run.attestation.domain_contract_pack_revision
        ):
            reasons.append("domain_contract_revision_mismatch")
        if reasons:
            rejection = _new_domain_rejection(
                admitted_operation=admitted_operation,
                environment_run=self._environment_run,
                environment_id=self._environment_id,
                reason_codes=tuple(reasons),
            )
            self._lifecycle_ledger.record(rejection)
            return ExecutionLeaseDecision(rejection=rejection)

        lease = self._new_lease(admitted_operation)
        expected_sequence = len(self._lifecycle_ledger.events()) + 1
        try:
            self._lifecycle_ledger.record(
                lease,
                expected_sequence=expected_sequence,
            )
        except LifecycleSequenceConflict:
            recorded_lease = self._lifecycle_ledger.execution_lease_identity(
                trace_id=admitted_operation.trace_id,
                operation_id=admitted_operation.operation_id,
            )
            if recorded_lease is None:
                raise
            self._require_exact_recorded_lease(
                lease,
                recorded_lease=recorded_lease,
            )
            return ExecutionLeaseDecision(execution_lease=lease)
        return ExecutionLeaseDecision(execution_lease=lease)

    def _new_lease(self, admitted_operation: AdmittedOperation) -> ExecutionLease:
        return _new_execution_lease(
            admitted_operation=admitted_operation,
            lease_owner_id=self._environment_run.attestation.environment_owner_id,
            environment_attestation_id=(
                self._environment_run.attestation.attestation_id
            ),
        )

    @staticmethod
    def _require_exact_recorded_lease(
        lease: ExecutionLease,
        *,
        recorded_lease: tuple[str, str],
    ) -> None:
        if recorded_lease != (lease.admission_id, lease.execution_lease_id):
            raise ValueError("leased operation requires the exact admitted operation")
