"""Replay-stable runtime controls derived from frozen task policy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json
from typing import Literal

from ab_harness.domain_lifecycle import ExecutionLease
from ab_harness.lifecycle import LifecycleSequenceConflict
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.task_compiler import CompiledTask


BUDGET_DECISION_SCHEMA = "uah.budget_decision/v1"
CANCELLATION_DECISION_SCHEMA = "uah.execution_cancellation_decision/v1"
EXECUTION_FAILURE_SCHEMA = "uah.execution_failure/v1"
TASK_TIMEOUT_DECISION_SCHEMA = "uah.task_timeout_decision/v1"
RETRY_DECISION_SCHEMA = "uah.retry_decision/v1"

BudgetResource = Literal["model_call", "tool_call"]


def _content_id(prefix: str, payload: object) -> str:
    try:
        encoded = json.dumps(
            payload,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("runtime control content must contain finite JSON") from exc
    return "%s:sha256:%s" % (prefix, hashlib.sha256(encoded).hexdigest())


def _budget_payload(
    *,
    compiled_task_id: str,
    environment_run_id: str,
    task_id: str,
    trace_id: str,
    resource: BudgetResource,
    subject_id: str,
    units: int,
    limit: int,
    consumed_before: int,
    consumed_after: int,
    outcome: str,
    reason_code: str,
) -> dict[str, object]:
    return {
        "schema_version": BUDGET_DECISION_SCHEMA,
        "compiled_task_id": compiled_task_id,
        "environment_run_id": environment_run_id,
        "task_id": task_id,
        "trace_id": trace_id,
        "resource": resource,
        "subject_id": subject_id,
        "units": units,
        "limit": limit,
        "consumed_before": consumed_before,
        "consumed_after": consumed_after,
        "outcome": outcome,
        "reason_code": reason_code,
    }


@dataclass(frozen=True)
class BudgetDecision:
    """One idempotent resource debit against a compiled task limit."""

    decision_id: str
    compiled_task_id: str
    environment_run_id: str
    task_id: str
    trace_id: str
    resource: BudgetResource
    subject_id: str
    units: int
    limit: int
    consumed_before: int
    consumed_after: int
    outcome: Literal["granted", "exhausted"]
    reason_code: str
    schema_version: str = BUDGET_DECISION_SCHEMA

    def __post_init__(self) -> None:
        self.verify_identity()

    @classmethod
    def issue(cls, **fields: object) -> BudgetDecision:
        payload = _budget_payload(**fields)  # type: ignore[arg-type]
        return cls(
            decision_id=_content_id("budget-decision", payload),
            **fields,  # type: ignore[arg-type]
        )

    def verify_identity(self) -> None:
        required = (
            self.compiled_task_id,
            self.environment_run_id,
            self.task_id,
            self.trace_id,
            self.subject_id,
            self.reason_code,
        )
        if any(not value.strip() for value in required):
            raise ValueError("budget decision fields must not be empty")
        if self.schema_version != BUDGET_DECISION_SCHEMA:
            raise ValueError("unsupported budget decision schema")
        if self.resource not in {"model_call", "tool_call"}:
            raise ValueError("unsupported budget resource")
        if self.outcome not in {"granted", "exhausted"}:
            raise ValueError("unsupported budget outcome")
        if any(
            type(value) is not int
            for value in (
                self.units,
                self.limit,
                self.consumed_before,
                self.consumed_after,
            )
        ):
            raise ValueError("budget quantities must be finite integers")
        if (
            self.units <= 0
            or min(self.limit, self.consumed_before, self.consumed_after) < 0
        ):
            raise ValueError("budget quantities are invalid")
        if self.outcome == "granted":
            if self.consumed_after != self.consumed_before + self.units:
                raise ValueError("granted budget decision has invalid consumption")
            if self.consumed_after > self.limit:
                raise ValueError("granted budget decision exceeds limit")
        elif self.consumed_after != self.consumed_before:
            raise ValueError("exhausted budget decision cannot consume units")
        payload = _budget_payload(
            compiled_task_id=self.compiled_task_id,
            environment_run_id=self.environment_run_id,
            task_id=self.task_id,
            trace_id=self.trace_id,
            resource=self.resource,
            subject_id=self.subject_id,
            units=self.units,
            limit=self.limit,
            consumed_before=self.consumed_before,
            consumed_after=self.consumed_after,
            outcome=self.outcome,
            reason_code=self.reason_code,
        )
        if self.decision_id != _content_id("budget-decision", payload):
            raise ValueError("budget decision identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {
            "decision_id": self.decision_id,
            **_budget_payload(
                compiled_task_id=self.compiled_task_id,
                environment_run_id=self.environment_run_id,
                task_id=self.task_id,
                trace_id=self.trace_id,
                resource=self.resource,
                subject_id=self.subject_id,
                units=self.units,
                limit=self.limit,
                consumed_before=self.consumed_before,
                consumed_after=self.consumed_after,
                outcome=self.outcome,
                reason_code=self.reason_code,
            ),
        }


class BudgetExhaustedError(RuntimeError):
    """Raised after a typed exhausted budget decision has been recorded."""


class TaskBudgetAuthority:
    """Compute idempotent budget decisions from compiled ledger policy."""

    _LIMIT_KEYS = {
        "model_call": "model_calls",
        "tool_call": "tool_calls",
    }

    def __init__(self, ledger: LifecycleLedger) -> None:
        self._ledger = ledger

    def consume(
        self,
        *,
        trace_id: str,
        resource: BudgetResource,
        subject_id: str,
        units: int = 1,
    ) -> BudgetDecision:
        for _attempt in range(2):
            assessment = self.assess(
                trace_id=trace_id,
                resource=resource,
                subject_id=subject_id,
                units=units,
            )
            if assessment.already_recorded:
                return assessment.decision
            try:
                self._ledger.record(
                    assessment.decision,
                    expected_sequence=assessment.expected_sequence,
                )
                return assessment.decision
            except LifecycleSequenceConflict:
                if _attempt:
                    raise
        raise RuntimeError("budget decision retry exhausted")

    def assess(
        self,
        *,
        trace_id: str,
        resource: BudgetResource,
        subject_id: str,
        units: int = 1,
    ) -> BudgetAssessment:
        events = self._ledger.events()
        compiled = next(
            (
                event
                for event in events
                if event.trace_id == trace_id and event.event_type == "task_compiled"
            ),
            None,
        )
        if compiled is None:
            raise ValueError("budget authority requires a compiled task")
        prior = tuple(
            event
            for event in events
            if event.trace_id == trace_id
            and event.event_type in {"budget_granted", "budget_exhausted"}
            and event.data["resource"] == resource
        )
        existing = next(
            (event for event in prior if event.data["subject_id"] == subject_id),
            None,
        )
        if existing is not None:
            if existing.data["units"] != units:
                raise ValueError("budget subject cannot change requested units")
            return BudgetAssessment(
                decision=_budget_decision_from_event(existing.data),
                already_recorded=True,
                expected_sequence=len(events) + 1,
            )
        budgets = compiled.data["budgets"]
        if not isinstance(budgets, dict):
            raise ValueError("compiled task budget projection is invalid")
        limit = budgets[self._LIMIT_KEYS[resource]]
        if type(limit) is not int:
            raise ValueError("compiled task budget limit is invalid")
        consumed = sum(
            int(event.data["units"])
            for event in prior
            if event.event_type == "budget_granted"
        )
        granted = consumed + units <= limit
        decision = BudgetDecision.issue(
            compiled_task_id=str(compiled.data["compiled_task_id"]),
            environment_run_id=compiled.environment_run_id,
            task_id=compiled.task_id,
            trace_id=compiled.trace_id,
            resource=resource,
            subject_id=subject_id,
            units=units,
            limit=limit,
            consumed_before=consumed,
            consumed_after=consumed + units if granted else consumed,
            outcome="granted" if granted else "exhausted",
            reason_code="within_budget" if granted else "budget_exhausted",
        )
        return BudgetAssessment(
            decision=decision,
            already_recorded=False,
            expected_sequence=len(events) + 1,
        )


@dataclass(frozen=True)
class BudgetAssessment:
    """One snapshot-bound budget result before ledger commitment."""

    decision: BudgetDecision
    already_recorded: bool
    expected_sequence: int


def _budget_decision_from_event(data: dict[str, object]) -> BudgetDecision:
    values = dict(data)
    values.pop("schema_version", None)
    return BudgetDecision(**values)  # type: ignore[arg-type]


def _cancellation_payload(
    *,
    lease: ExecutionLease,
    requester_id: str,
    request_artifact_id: str,
    deciding_owner_id: str,
    reason_code: str,
) -> dict[str, object]:
    return {
        "schema_version": CANCELLATION_DECISION_SCHEMA,
        "lease": lease.to_dict(),
        "requester_id": requester_id,
        "request_artifact_id": request_artifact_id,
        "deciding_owner_id": deciding_owner_id,
        "phase": "pre_dispatch",
        "outcome": "accepted",
        "reason_code": reason_code,
    }


@dataclass(frozen=True)
class ExecutionCancellationDecision:
    """Owner-authorized cancellation before native dispatch."""

    decision_id: str
    lease: ExecutionLease
    requester_id: str
    request_artifact_id: str
    deciding_owner_id: str
    reason_code: str
    phase: str = "pre_dispatch"
    outcome: str = "accepted"
    schema_version: str = CANCELLATION_DECISION_SCHEMA

    def __post_init__(self) -> None:
        self.verify_identity()

    @classmethod
    def issue(cls, **fields: object) -> ExecutionCancellationDecision:
        payload = _cancellation_payload(**fields)  # type: ignore[arg-type]
        return cls(
            decision_id=_content_id("cancellation-decision", payload),
            **fields,  # type: ignore[arg-type]
        )

    def verify_identity(self) -> None:
        self.lease.verify_identity()
        if self.schema_version != CANCELLATION_DECISION_SCHEMA:
            raise ValueError("unsupported cancellation decision schema")
        if self.phase != "pre_dispatch" or self.outcome != "accepted":
            raise ValueError("only accepted pre-dispatch cancellation is supported")
        required = (
            self.requester_id,
            self.request_artifact_id,
            self.deciding_owner_id,
            self.reason_code,
        )
        if any(not value.strip() for value in required):
            raise ValueError("cancellation decision fields must not be empty")
        if self.deciding_owner_id != self.lease.lease_owner_id:
            raise ValueError("cancellation decision owner does not own lease")
        expected = _content_id(
            "cancellation-decision",
            _cancellation_payload(
                lease=self.lease,
                requester_id=self.requester_id,
                request_artifact_id=self.request_artifact_id,
                deciding_owner_id=self.deciding_owner_id,
                reason_code=self.reason_code,
            ),
        )
        if self.decision_id != expected:
            raise ValueError("cancellation decision identity does not match content")


def _failure_payload(
    *,
    lease: ExecutionLease,
    failure_ref: str,
    failure_code: str,
    failure_stage: str,
    retry_disposition: str,
) -> dict[str, object]:
    return {
        "schema_version": EXECUTION_FAILURE_SCHEMA,
        "lease": lease.to_dict(),
        "failure_ref": failure_ref,
        "failure_code": failure_code,
        "failure_stage": failure_stage,
        "retry_disposition": retry_disposition,
    }


@dataclass(frozen=True)
class ExecutionFailure:
    """Content-addressed terminal operation failure."""

    failure_id: str
    lease: ExecutionLease
    failure_ref: str
    failure_code: str
    failure_stage: str
    retry_disposition: Literal["retryable", "terminal"]
    schema_version: str = EXECUTION_FAILURE_SCHEMA

    def __post_init__(self) -> None:
        self.verify_identity()

    @classmethod
    def issue(cls, **fields: object) -> ExecutionFailure:
        payload = _failure_payload(**fields)  # type: ignore[arg-type]
        return cls(
            failure_id=_content_id("execution-failure", payload),
            **fields,  # type: ignore[arg-type]
        )

    def verify_identity(self) -> None:
        self.lease.verify_identity()
        if self.schema_version != EXECUTION_FAILURE_SCHEMA:
            raise ValueError("unsupported execution failure schema")
        required = (self.failure_ref, self.failure_code, self.failure_stage)
        if any(not value.strip() for value in required):
            raise ValueError("execution failure fields must not be empty")
        if self.retry_disposition not in {"retryable", "terminal"}:
            raise ValueError("invalid retry disposition")
        expected = _content_id(
            "execution-failure",
            _failure_payload(
                lease=self.lease,
                failure_ref=self.failure_ref,
                failure_code=self.failure_code,
                failure_stage=self.failure_stage,
                retry_disposition=self.retry_disposition,
            ),
        )
        if self.failure_id != expected:
            raise ValueError("execution failure identity does not match content")


def _timeout_payload(
    *,
    compiled_task: CompiledTask,
    task_started_at: str,
    deadline_at: str,
    observed_at: str,
    policy_revision: str,
    outcome: str,
) -> dict[str, object]:
    return {
        "schema_version": TASK_TIMEOUT_DECISION_SCHEMA,
        "compiled_task_id": compiled_task.compiled_task_id,
        "environment_run_id": compiled_task.environment_run_id,
        "task_id": compiled_task.task_id,
        "trace_id": compiled_task.trace_id,
        "task_started_at": task_started_at,
        "deadline_at": deadline_at,
        "observed_at": observed_at,
        "policy_revision": policy_revision,
        "outcome": outcome,
    }


@dataclass(frozen=True)
class TaskTimeoutDecision:
    """Recorded wall-time decision that never consults replay time."""

    decision_id: str
    compiled_task: CompiledTask
    task_started_at: str
    deadline_at: str
    observed_at: str
    policy_revision: str
    outcome: Literal["within_budget", "timed_out"]
    schema_version: str = TASK_TIMEOUT_DECISION_SCHEMA

    def __post_init__(self) -> None:
        self.verify_identity()

    @classmethod
    def issue(cls, **fields: object) -> TaskTimeoutDecision:
        payload = _timeout_payload(**fields)  # type: ignore[arg-type]
        return cls(
            decision_id=_content_id("timeout-decision", payload),
            **fields,  # type: ignore[arg-type]
        )

    def verify_identity(self) -> None:
        self.compiled_task.verify_identity()
        if self.schema_version != TASK_TIMEOUT_DECISION_SCHEMA:
            raise ValueError("unsupported timeout decision schema")
        if self.outcome not in {"within_budget", "timed_out"}:
            raise ValueError("invalid timeout outcome")
        if not self.policy_revision.strip():
            raise ValueError("timeout policy revision must not be empty")
        started = _parse_time(self.task_started_at)
        deadline = _parse_time(self.deadline_at)
        observed = _parse_time(self.observed_at)
        expected_deadline = started + timedelta(
            seconds=self.compiled_task.budgets.wall_time_seconds
        )
        if deadline != expected_deadline:
            raise ValueError(
                "timeout deadline does not match compiled wall-time budget"
            )
        expected_outcome = "timed_out" if observed > deadline else "within_budget"
        if self.outcome != expected_outcome:
            raise ValueError("timeout outcome does not match recorded timestamps")
        expected = _content_id(
            "timeout-decision",
            _timeout_payload(
                compiled_task=self.compiled_task,
                task_started_at=self.task_started_at,
                deadline_at=self.deadline_at,
                observed_at=self.observed_at,
                policy_revision=self.policy_revision,
                outcome=self.outcome,
            ),
        )
        if self.decision_id != expected:
            raise ValueError("timeout decision identity does not match content")


class TaskRuntimeControlAuthority:
    """Issue replay-stable wall-time decisions from compiled limits."""

    def __init__(self, ledger: LifecycleLedger) -> None:
        self._ledger = ledger

    def evaluate_timeout(
        self,
        *,
        compiled_task: CompiledTask,
        observed_at: str,
        policy_revision: str,
    ) -> TaskTimeoutDecision:
        events = self._ledger.events()
        started_event = next(
            (
                event
                for event in events
                if event.trace_id == compiled_task.trace_id
                and event.event_type == "task_started"
            ),
            None,
        )
        compiled_event = next(
            (
                event
                for event in events
                if event.trace_id == compiled_task.trace_id
                and event.event_type == "task_compiled"
                and event.data.get("compiled_task_id") == compiled_task.compiled_task_id
            ),
            None,
        )
        if started_event is None or compiled_event is None:
            raise ValueError("timeout authority requires the recorded compiled task")
        task_started_at = started_event.recorded_at
        started = _parse_time(task_started_at)
        observed = _parse_time(observed_at)
        deadline = started + timedelta(seconds=compiled_task.budgets.wall_time_seconds)
        decision = TaskTimeoutDecision.issue(
            compiled_task=compiled_task,
            task_started_at=task_started_at,
            deadline_at=deadline.isoformat().replace("+00:00", "Z"),
            observed_at=observed_at,
            policy_revision=policy_revision,
            outcome="timed_out" if observed > deadline else "within_budget",
        )
        self._ledger.record(decision)
        return decision


def _parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("runtime control timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError("runtime control timestamp must include timezone")
    return parsed


def _retry_payload(
    *,
    compiled_task_id: str,
    environment_run_id: str,
    task_id: str,
    trace_id: str,
    source_failure_id: str,
    source_operation_id: str,
    target_operation_id: str,
    attempt_ordinal: int,
    retry_limit: int,
    policy_revision: str,
    outcome: str,
) -> dict[str, object]:
    return {
        "schema_version": RETRY_DECISION_SCHEMA,
        "compiled_task_id": compiled_task_id,
        "environment_run_id": environment_run_id,
        "task_id": task_id,
        "trace_id": trace_id,
        "source_failure_id": source_failure_id,
        "source_operation_id": source_operation_id,
        "target_operation_id": target_operation_id,
        "attempt_ordinal": attempt_ordinal,
        "retry_limit": retry_limit,
        "policy_revision": policy_revision,
        "outcome": outcome,
    }


@dataclass(frozen=True)
class RetryDecision:
    """Retry policy result that grants no proposal or execution authority."""

    decision_id: str
    compiled_task_id: str
    environment_run_id: str
    task_id: str
    trace_id: str
    source_failure_id: str
    source_operation_id: str
    target_operation_id: str
    attempt_ordinal: int
    retry_limit: int
    policy_revision: str
    outcome: Literal["approved", "not_retryable", "exhausted"]
    schema_version: str = RETRY_DECISION_SCHEMA

    def __post_init__(self) -> None:
        self.verify_identity()

    @classmethod
    def issue(cls, **fields: object) -> RetryDecision:
        payload = _retry_payload(**fields)  # type: ignore[arg-type]
        return cls(
            decision_id=_content_id("retry-decision", payload),
            **fields,  # type: ignore[arg-type]
        )

    def verify_identity(self) -> None:
        required = (
            self.compiled_task_id,
            self.environment_run_id,
            self.task_id,
            self.trace_id,
            self.source_failure_id,
            self.source_operation_id,
            self.target_operation_id,
            self.policy_revision,
        )
        if any(not value.strip() for value in required):
            raise ValueError("retry decision fields must not be empty")
        if self.source_operation_id == self.target_operation_id:
            raise ValueError("retry requires a fresh target operation id")
        if self.outcome not in {"approved", "not_retryable", "exhausted"}:
            raise ValueError("invalid retry outcome")
        if self.attempt_ordinal < 1 or self.retry_limit < 0:
            raise ValueError("retry quantities are invalid")
        expected = _content_id(
            "retry-decision",
            _retry_payload(
                compiled_task_id=self.compiled_task_id,
                environment_run_id=self.environment_run_id,
                task_id=self.task_id,
                trace_id=self.trace_id,
                source_failure_id=self.source_failure_id,
                source_operation_id=self.source_operation_id,
                target_operation_id=self.target_operation_id,
                attempt_ordinal=self.attempt_ordinal,
                retry_limit=self.retry_limit,
                policy_revision=self.policy_revision,
                outcome=self.outcome,
            ),
        )
        if self.decision_id != expected:
            raise ValueError("retry decision identity does not match content")


class RetryAuthority:
    """Decide bounded retries from a typed failure and compiled task budget."""

    def __init__(self, ledger: LifecycleLedger) -> None:
        self._ledger = ledger

    def decide(
        self,
        *,
        compiled_task: CompiledTask,
        source_failure: ExecutionFailure,
        target_operation_id: str,
        policy_revision: str,
    ) -> RetryDecision:
        source_failure.verify_identity()
        if (
            source_failure.lease.admitted_operation.compiled_task_id
            != compiled_task.compiled_task_id
        ):
            raise ValueError("retry failure does not belong to compiled task")
        events = self._ledger.events()
        if not any(
            event.trace_id == compiled_task.trace_id
            and event.event_type == "execution_failed"
            and event.data.get("failure_id") == source_failure.failure_id
            for event in events
        ):
            raise ValueError("retry requires a recorded execution failure")
        prior_approved = sum(
            event.trace_id == compiled_task.trace_id
            and event.event_type == "retry_approved"
            for event in events
        )
        ordinal = prior_approved + 1
        if source_failure.retry_disposition != "retryable":
            outcome = "not_retryable"
        elif ordinal > compiled_task.budgets.retry_attempts:
            outcome = "exhausted"
        else:
            outcome = "approved"
        decision = RetryDecision.issue(
            compiled_task_id=compiled_task.compiled_task_id,
            environment_run_id=compiled_task.environment_run_id,
            task_id=compiled_task.task_id,
            trace_id=compiled_task.trace_id,
            source_failure_id=source_failure.failure_id,
            source_operation_id=source_failure.lease.operation_id,
            target_operation_id=target_operation_id,
            attempt_ordinal=ordinal,
            retry_limit=compiled_task.budgets.retry_attempts,
            policy_revision=policy_revision,
            outcome=outcome,
        )
        self._ledger.record(decision)
        return decision
