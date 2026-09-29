"""Domain-owned execution admission for semantically admitted operations."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from ab_harness.environment_runs import EnvironmentRun
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.proposal_admission import AdmittedOperation


EXECUTION_LEASE_SCHEMA = "uah.execution_lease/v1"


def _lease_payload(
    *,
    admitted_operation: AdmittedOperation,
    lease_owner_id: str,
    environment_attestation_id: str,
) -> dict[str, object]:
    return {
        "schema_version": EXECUTION_LEASE_SCHEMA,
        "admitted_operation": admitted_operation.to_dict(),
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
        self.admitted_operation.verify_identity()
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

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
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


@dataclass(frozen=True)
class ExecutionLeaseDecision:
    """Execution lease or deterministic domain lifecycle rejection reasons."""

    execution_lease: ExecutionLease | None = None
    reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if (self.execution_lease is None) == (not self.reason_codes):
            raise ValueError("lease decision must contain lease or reasons")

    @property
    def accepted(self) -> bool:
        return self.execution_lease is not None


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
        admitted_operation.verify_identity()
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
        if self._lifecycle_ledger.has_operation_event(
            trace_id=admitted_operation.trace_id,
            operation_id=admitted_operation.operation_id,
            event_type="domain_admission_leased",
        ):
            reasons.append("operation_already_leased")
        if reasons:
            return ExecutionLeaseDecision(reason_codes=tuple(reasons))

        lease = _new_execution_lease(
            admitted_operation=admitted_operation,
            lease_owner_id=self._environment_run.attestation.environment_owner_id,
            environment_attestation_id=(
                self._environment_run.attestation.attestation_id
            ),
        )
        self._lifecycle_ledger.record(lease)
        return ExecutionLeaseDecision(execution_lease=lease)
