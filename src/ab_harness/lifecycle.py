"""Append-only lifecycle ledger and deterministic trace replay."""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from types import MappingProxyType
from types import TracebackType
from typing import Callable, TYPE_CHECKING

from ab_harness._content_addressing import canonical_json
from ab_harness._content_addressing import content_id
from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.contracts import EffectEvidence
from ab_harness.contracts import TaskAcceptance

if TYPE_CHECKING:
    from ab_harness.domain_lifecycle import DomainAdmissionRejection
    from ab_harness.domain_lifecycle import ExecutionLease
    from ab_harness.environment import ExecutionReceipt
    from ab_harness.environment import EvidenceRejection
    from ab_harness.operation_edges import OperationEdge
    from ab_harness.proposal_admission import AdmittedOperation
    from ab_harness.proposal_admission import ProposalNormalizationRejection
    from ab_harness.proposal_admission import SemanticAdmissionRejection
    from ab_harness.proposal_admission import TypedProposal
    from ab_harness.runtime_controls import BudgetDecision
    from ab_harness.runtime_controls import ExecutionCancellationDecision
    from ab_harness.runtime_controls import ExecutionFailure
    from ab_harness.runtime_controls import RetryDecision
    from ab_harness.runtime_controls import TaskTimeoutDecision
    from ab_harness.task_compiler import CompiledTask


TRACE_EVENT_SCHEMA = "uah.trace_event/v1"
VERIFIED_TRACE_DIGEST_SCHEMA = "uah.verified_trace_digest/v1"


def _canonical_json(payload: object) -> str:
    try:
        return canonical_json(payload)
    except (TypeError, ValueError) as exc:
        raise ValueError("lifecycle content must contain finite JSON values") from exc


def _content_id(prefix: str, payload: object) -> str:
    try:
        return content_id(prefix, payload)
    except (TypeError, ValueError) as exc:
        raise ValueError("lifecycle content must contain finite JSON values") from exc


def _artifact_id(prefix: str, artifact: object) -> str:
    return _content_id(prefix, asdict(artifact))


@dataclass(frozen=True)
class TraceEvent:
    """One content-addressed fact in the global lifecycle sequence."""

    event_id: str
    sequence: int
    commit_id: str
    commit_index: int
    commit_size: int
    recorded_at: str
    event_type: str
    environment_run_id: str
    task_id: str
    trace_id: str
    operation_id: str | None
    parent_event_id: str | None
    artifact_refs: tuple[str, ...]
    data_json: str
    schema_version: str = TRACE_EVENT_SCHEMA

    def __post_init__(self) -> None:
        if self.schema_version != TRACE_EVENT_SCHEMA:
            raise ValueError("unsupported trace event schema: %s" % self.schema_version)
        if self.sequence < 1:
            raise ValueError("trace event sequence must be positive")
        if not 1 <= self.commit_index <= self.commit_size:
            raise ValueError("trace event commit position is invalid")
        required = {
            "event_id": self.event_id,
            "commit_id": self.commit_id,
            "recorded_at": self.recorded_at,
            "event_type": self.event_type,
            "environment_run_id": self.environment_run_id,
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "data_json": self.data_json,
        }
        missing = tuple(name for name, value in required.items() if not value.strip())
        if missing:
            raise ValueError(
                "trace event fields must not be empty: %s" % ", ".join(missing)
            )
        if not isinstance(self.artifact_refs, tuple) or not self.artifact_refs:
            raise ValueError("trace event requires immutable artifact references")
        if any(not reference.strip() for reference in self.artifact_refs):
            raise ValueError("trace event artifact references must not be empty")
        data = json.loads(self.data_json)
        if not isinstance(data, dict) or self.data_json != _canonical_json(data):
            raise ValueError("trace event data must be a canonical JSON object")
        if self.event_id != _content_id("trace-event", self._identity_payload()):
            raise ValueError("trace event identity does not match content")

    @property
    def data(self) -> dict[str, object]:
        return json.loads(self.data_json)

    def _identity_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "sequence": self.sequence,
            "commit_id": self.commit_id,
            "commit_index": self.commit_index,
            "commit_size": self.commit_size,
            "recorded_at": self.recorded_at,
            "event_type": self.event_type,
            "environment_run_id": self.environment_run_id,
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "operation_id": self.operation_id,
            "parent_event_id": self.parent_event_id,
            "artifact_refs": self.artifact_refs,
            "data_json": self.data_json,
        }

    def to_dict(self) -> dict[str, object]:
        payload = self._identity_payload()
        payload["artifact_refs"] = list(self.artifact_refs)
        return {"event_id": self.event_id, **payload}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> TraceEvent:
        expected = {
            "schema_version",
            "event_id",
            "sequence",
            "commit_id",
            "commit_index",
            "commit_size",
            "recorded_at",
            "event_type",
            "environment_run_id",
            "task_id",
            "trace_id",
            "operation_id",
            "parent_event_id",
            "artifact_refs",
            "data_json",
        }
        if set(payload) != expected:
            raise ValueError("invalid trace event fields")
        if any(
            not isinstance(payload[name], int)
            for name in ("sequence", "commit_index", "commit_size")
        ):
            raise ValueError("trace event sequence fields must be integers")
        nullable = ("operation_id", "parent_event_id")
        if any(
            payload[name] is not None and not isinstance(payload[name], str)
            for name in nullable
        ):
            raise ValueError("trace event optional identities must be strings or null")
        string_fields = expected - {
            "sequence",
            "commit_index",
            "commit_size",
            "operation_id",
            "parent_event_id",
            "artifact_refs",
        }
        if any(not isinstance(payload[name], str) for name in string_fields):
            raise ValueError("trace event fields have invalid types")
        refs = payload["artifact_refs"]
        if not isinstance(refs, list) or any(
            not isinstance(item, str) for item in refs
        ):
            raise ValueError(
                "trace event artifact references must be a list of strings"
            )
        return cls(
            event_id=payload["event_id"],
            sequence=payload["sequence"],
            commit_id=payload["commit_id"],
            commit_index=payload["commit_index"],
            commit_size=payload["commit_size"],
            recorded_at=payload["recorded_at"],
            event_type=payload["event_type"],
            environment_run_id=payload["environment_run_id"],
            task_id=payload["task_id"],
            trace_id=payload["trace_id"],
            operation_id=payload["operation_id"],
            parent_event_id=payload["parent_event_id"],
            artifact_refs=tuple(refs),
            data_json=payload["data_json"],
            schema_version=payload["schema_version"],
        )


@dataclass(frozen=True)
class TaskStartedFact:
    environment_run_id: str
    task_id: str
    trace_id: str
    environment_ingress_id: str
    ingress_artifact_id: str
    decision_id: str
    domain_contract_pack_revision: str


@dataclass(frozen=True)
class TaskIngressFact:
    environment_run_id: str
    task_id: str
    trace_id: str
    environment_ingress_id: str
    ingress_artifact_id: str
    decision_id: str
    domain_contract_pack_revision: str
    action: str


@dataclass(frozen=True)
class ExecutionStartedFact:
    lease: ExecutionLease


@dataclass(frozen=True)
class ExecutionDispatchFact:
    lease: ExecutionLease
    budget_decision: BudgetDecision


@dataclass(frozen=True)
class AcceptanceFact:
    compiled_task: CompiledTask
    evidence_set: tuple[EffectEvidence, ...]
    acceptance: TaskAcceptance


if TYPE_CHECKING:
    LifecycleFact = (
        TaskStartedFact
        | TaskIngressFact
        | CompiledTask
        | TypedProposal
        | ProposalNormalizationRejection
        | SemanticAdmissionRejection
        | AdmittedOperation
        | DomainAdmissionRejection
        | ExecutionLease
        | ExecutionStartedFact
        | ExecutionDispatchFact
        | ExecutionReceipt
        | EvidenceRejection
        | ExecutionFailure
        | BudgetDecision
        | ExecutionCancellationDecision
        | TaskTimeoutDecision
        | RetryDecision
        | OperationEdge
        | AcceptanceFact
    )
else:
    LifecycleFact = object


@dataclass(frozen=True)
class LifecycleCommit:
    events: tuple[TraceEvent, ...]


class LifecycleSequenceConflict(ValueError):
    """Raised when a snapshot-bound append loses its sequence race."""


@dataclass(frozen=True)
class VerifiedTraceDigest:
    digest_id: str
    environment_run_id: str
    task_id: str
    trace_id: str
    environment_ingress_artifact_id: str
    task_ingress_decision_id: str
    first_sequence: int
    last_sequence: int
    event_ids: tuple[str, ...]
    compiled_task_id: str
    domain_contract_pack_revision: str
    role_id: str
    frame_id: str
    registry_version: str
    operation_ids: tuple[str, ...]
    proposal_ids: tuple[str, ...]
    admission_ids: tuple[str, ...]
    execution_lease_ids: tuple[str, ...]
    execution_result_ids: tuple[str, ...]
    evidence_artifact_ids: tuple[str, ...]
    native_evidence_refs: tuple[str, ...]
    satisfied_obligation_ids: tuple[str, ...]
    deficit_obligation_ids: tuple[str, ...]
    pending_obligation_ids: tuple[str, ...]
    failed_obligation_ids: tuple[str, ...]
    terminal_status: str
    failure_stage: str | None = None
    schema_version: str = VERIFIED_TRACE_DIGEST_SCHEMA

    def __post_init__(self) -> None:
        payload = asdict(self)
        payload.pop("digest_id")
        if self.schema_version != VERIFIED_TRACE_DIGEST_SCHEMA:
            raise ValueError(
                "unsupported verified trace digest schema: %s" % self.schema_version
            )
        if self.digest_id != _content_id("verified-trace-digest", payload):
            raise ValueError("verified trace digest identity does not match content")

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        for name in _DIGEST_COLLECTION_FIELDS:
            payload[name] = list(payload[name])
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> VerifiedTraceDigest:
        if set(payload) != _DIGEST_FIELDS:
            raise ValueError("invalid verified trace digest fields")
        if payload["schema_version"] != VERIFIED_TRACE_DIGEST_SCHEMA:
            raise ValueError(
                "unsupported verified trace digest schema: %s"
                % payload["schema_version"]
            )
        if not isinstance(payload["first_sequence"], int) or not isinstance(
            payload["last_sequence"], int
        ):
            raise ValueError("verified trace digest sequences must be integers")
        collections: dict[str, tuple[str, ...]] = {}
        for name in _DIGEST_COLLECTION_FIELDS:
            value = payload[name]
            if not isinstance(value, list) or any(
                not isinstance(item, str) for item in value
            ):
                raise ValueError(
                    "verified trace digest collections must contain strings"
                )
            collections[name] = tuple(value)
        scalar_names = (
            _DIGEST_FIELDS
            - _DIGEST_COLLECTION_FIELDS
            - {
                "first_sequence",
                "last_sequence",
                "failure_stage",
            }
        )
        if any(not isinstance(payload[name], str) for name in scalar_names):
            raise ValueError("verified trace digest fields have invalid types")
        failure_stage = payload["failure_stage"]
        if failure_stage is not None and not isinstance(failure_stage, str):
            raise ValueError("verified trace digest failure stage is invalid")
        return cls(
            digest_id=payload["digest_id"],
            environment_run_id=payload["environment_run_id"],
            task_id=payload["task_id"],
            trace_id=payload["trace_id"],
            environment_ingress_artifact_id=payload["environment_ingress_artifact_id"],
            task_ingress_decision_id=payload["task_ingress_decision_id"],
            first_sequence=payload["first_sequence"],
            last_sequence=payload["last_sequence"],
            compiled_task_id=payload["compiled_task_id"],
            domain_contract_pack_revision=payload["domain_contract_pack_revision"],
            role_id=payload["role_id"],
            frame_id=payload["frame_id"],
            registry_version=payload["registry_version"],
            terminal_status=payload["terminal_status"],
            failure_stage=failure_stage,
            schema_version=payload["schema_version"],
            **collections,
        )


_DIGEST_COLLECTION_FIELDS = {
    "event_ids",
    "operation_ids",
    "proposal_ids",
    "admission_ids",
    "execution_lease_ids",
    "execution_result_ids",
    "evidence_artifact_ids",
    "native_evidence_refs",
    "satisfied_obligation_ids",
    "deficit_obligation_ids",
    "pending_obligation_ids",
    "failed_obligation_ids",
}
_DIGEST_FIELDS = {
    "digest_id",
    "environment_run_id",
    "task_id",
    "trace_id",
    "environment_ingress_artifact_id",
    "task_ingress_decision_id",
    "first_sequence",
    "last_sequence",
    "compiled_task_id",
    "domain_contract_pack_revision",
    "role_id",
    "frame_id",
    "registry_version",
    "terminal_status",
    "failure_stage",
    "schema_version",
    *_DIGEST_COLLECTION_FIELDS,
}


@dataclass(frozen=True)
class LifecycleReplay:
    events: tuple[TraceEvent, ...]
    terminal_status: str | None
    failure_stage: str | None
    verified_trace_digest: VerifiedTraceDigest | None


@dataclass
class _TraceState:
    environment_run_id: str
    task_id: str
    trace_id: str
    environment_ingress_artifact_id: str = ""
    task_ingress_decision_id: str = ""
    compiled_task_id: str | None = None
    domain_contract_pack_revision: str | None = None
    role_id: str | None = None
    frame_id: str | None = None
    registry_version: str | None = None
    terminal_status: str | None = None
    failure_stage: str | None = None
    last_event_id: str | None = None
    event_types: list[str] = field(default_factory=list)
    leased_operation_ids: set[str] = field(default_factory=set)
    started_operation_ids: set[str] = field(default_factory=set)
    terminal_operation_ids: set[str] = field(default_factory=set)
    evidence_artifact_ids: set[str] = field(default_factory=set)
    evidence_issued_operation_ids: set[str] = field(default_factory=set)
    evidence_rejected_operation_ids: set[str] = field(default_factory=set)
    proposal_by_operation: dict[str, str] = field(default_factory=dict)
    rejected_operation_ids: set[str] = field(default_factory=set)
    admission_by_operation: dict[str, str] = field(default_factory=dict)
    object_by_operation: dict[str, str] = field(default_factory=dict)
    binding_by_operation: dict[str, str] = field(default_factory=dict)
    owner_by_operation: dict[str, str] = field(default_factory=dict)
    frame_by_operation: dict[str, str] = field(default_factory=dict)
    lease_by_operation: dict[str, str] = field(default_factory=dict)
    result_by_operation: dict[str, str] = field(default_factory=dict)
    operation_edges: set[tuple[str, str, str]] = field(default_factory=set)
    budget_limits: dict[str, int] = field(default_factory=dict)
    budget_consumed: dict[str, int] = field(default_factory=dict)
    budget_subjects: set[tuple[str, str]] = field(default_factory=set)
    tool_budget_granted_operation_ids: set[str] = field(default_factory=set)
    task_timed_out: bool = False
    failure_by_operation: dict[str, tuple[str, str]] = field(default_factory=dict)
    retry_decided_failure_ids: set[str] = field(default_factory=set)
    retry_target_operation_ids: set[str] = field(default_factory=set)


class LifecycleLedger:
    """Append-only lifecycle authority with coordinated file-backed writers."""

    def __init__(
        self,
        path: str | Path | None = None,
        *,
        clock: Callable[[], str] | None = None,
    ) -> None:
        self.path = Path(path) if path is not None else None
        self._clock = clock or _utc_now
        self._events: list[TraceEvent] = []
        with self._file_lock():
            self._refresh_from_disk()

    @property
    def next_sequence(self) -> int:
        return len(self._events) + 1

    def record(
        self,
        fact: LifecycleFact,
        *,
        expected_sequence: int | None = None,
    ) -> LifecycleCommit:
        with self._file_lock():
            self._refresh_from_disk()
            if (
                expected_sequence is not None
                and expected_sequence != self.next_sequence
            ):
                raise LifecycleSequenceConflict("lifecycle ledger sequence conflict")
            specs = _event_specs(fact)
            if not specs:
                raise ValueError("lifecycle fact produced no events")
            staged: list[TraceEvent] = []
            existing = tuple(self._events)
            recorded_at = self._clock()
            commit_id = _content_id(
                "lifecycle-commit",
                {
                    "first_sequence": len(existing) + 1,
                    "recorded_at": recorded_at,
                    "specs": specs,
                },
            )
            for commit_index, spec in enumerate(specs, start=1):
                trace_events = tuple(
                    event
                    for event in (*existing, *staged)
                    if event.trace_id == spec["trace_id"]
                )
                parent_event_id = trace_events[-1].event_id if trace_events else None
                staged.append(
                    _new_event(
                        sequence=len(existing) + len(staged) + 1,
                        commit_id=commit_id,
                        commit_index=commit_index,
                        commit_size=len(specs),
                        recorded_at=recorded_at,
                        parent_event_id=parent_event_id,
                        **spec,
                    )
                )
            combined = (*existing, *staged)
            _reduce_events(tuple(combined))
            self._append(staged)
            self._events.extend(staged)
            return LifecycleCommit(events=tuple(staged))

    def start_execution(self, lease: ExecutionLease) -> LifecycleCommit:
        from ab_harness.runtime_controls import BudgetExhaustedError
        from ab_harness.runtime_controls import TaskBudgetAuthority

        authority = TaskBudgetAuthority(self)
        for attempt in range(2):
            assessment = authority.assess(
                trace_id=lease.admitted_operation.trace_id,
                resource="tool_call",
                subject_id=lease.operation_id,
            )
            decision = assessment.decision
            if decision.outcome == "exhausted":
                if not assessment.already_recorded:
                    try:
                        self.record(
                            decision,
                            expected_sequence=assessment.expected_sequence,
                        )
                    except LifecycleSequenceConflict:
                        if not attempt:
                            continue
                        raise
                raise BudgetExhaustedError(
                    "tool_call budget exhausted for %s" % lease.operation_id
                )
            fact: LifecycleFact
            if assessment.already_recorded:
                fact = ExecutionStartedFact(lease)
            else:
                fact = ExecutionDispatchFact(lease, decision)
            try:
                return self.record(
                    fact,
                    expected_sequence=assessment.expected_sequence,
                )
            except LifecycleSequenceConflict:
                if not attempt:
                    continue
                raise
        raise RuntimeError("execution dispatch retry exhausted")

    def complete_execution(self, receipt: ExecutionReceipt) -> LifecycleCommit:
        return self.record(receipt)

    def fail_execution(
        self,
        lease: ExecutionLease,
        error: Exception,
    ) -> LifecycleCommit:
        failure_type = type(error).__name__
        failure_ref = _content_id(
            "execution-failure",
            {"failure_type": failure_type, "message": str(error)},
        )
        from ab_harness.runtime_controls import ExecutionFailure

        return self.record(
            ExecutionFailure.issue(
                lease=lease,
                failure_ref=failure_ref,
                failure_code=failure_type,
                failure_stage="native_execution",
                retry_disposition="terminal",
            )
        )

    def events(self) -> tuple[TraceEvent, ...]:
        with self._file_lock():
            self._refresh_from_disk()
            return tuple(self._events)

    def has_operation_event(
        self,
        *,
        trace_id: str,
        operation_id: str,
        event_type: str,
    ) -> bool:
        with self._file_lock():
            self._refresh_from_disk()
            return any(
                event.trace_id == trace_id
                and event.operation_id == operation_id
                and event.event_type == event_type
                for event in self._events
            )

    def replay(self, trace_id: str) -> LifecycleReplay:
        with self._file_lock():
            self._refresh_from_disk()
            events = tuple(
                event for event in self._events if event.trace_id == trace_id
            )
            if not events:
                raise KeyError(trace_id)
            states = _reduce_events(events, require_global_sequence=False)
            state = states[trace_id]
            digest = (
                _digest(events, state) if state.terminal_status is not None else None
            )
            return LifecycleReplay(
                events=events,
                terminal_status=state.terminal_status,
                failure_stage=state.failure_stage,
                verified_trace_digest=digest,
            )

    def _file_lock(self) -> _LedgerFileLock | _NullLedgerLock:
        if self.path is None:
            return _NullLedgerLock()
        return _LedgerFileLock(self.path.with_name(self.path.name + ".lock"))

    def _refresh_from_disk(self) -> None:
        if self.path is None:
            return
        events = self._load_events()
        _reduce_events(events)
        self._events = list(events)

    def _append(self, events: list[TraceEvent]) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            for event in events:
                stream.write(_canonical_json(event.to_dict()) + "\n")
            stream.flush()
            os.fsync(stream.fileno())

    def _load_events(self) -> tuple[TraceEvent, ...]:
        if self.path is None or not self.path.exists():
            return ()
        try:
            content = self.path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("lifecycle ledger is not valid UTF-8") from exc
        if content and not content.endswith("\n"):
            raise ValueError("lifecycle ledger has an unterminated final record")
        events: list[TraceEvent] = []
        for line_number, line in enumerate(content.splitlines(), start=1):
            if not line.strip():
                raise ValueError("invalid lifecycle event at line %d" % line_number)
            try:
                payload = json.loads(line)
                if not isinstance(payload, dict):
                    raise ValueError("event record must be a JSON object")
                events.append(TraceEvent.from_dict(payload))
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                raise ValueError(
                    "invalid lifecycle event at line %d" % line_number
                ) from exc
        return tuple(events)


class _NullLedgerLock:
    def __enter__(self) -> None:
        return None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


class _LedgerFileLock:
    """Cross-process advisory lock for one lifecycle ledger path."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._stream = None

    def __enter__(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._stream = self._path.open("a+b")
        if os.name == "nt":
            import msvcrt

            self._stream.seek(0, os.SEEK_END)
            if self._stream.tell() == 0:
                self._stream.write(b"\0")
                self._stream.flush()
            self._stream.seek(0)
            msvcrt.locking(self._stream.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(self._stream.fileno(), fcntl.LOCK_EX)
        return None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._stream is None:
            return
        try:
            if os.name == "nt":
                import msvcrt

                self._stream.seek(0)
                msvcrt.locking(self._stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._stream.fileno(), fcntl.LOCK_UN)
        finally:
            self._stream.close()
            self._stream = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _new_event(
    *,
    sequence: int,
    commit_id: str,
    commit_index: int,
    commit_size: int,
    recorded_at: str,
    event_type: str,
    environment_run_id: str,
    task_id: str,
    trace_id: str,
    operation_id: str | None,
    parent_event_id: str | None,
    artifact_refs: tuple[str, ...],
    data: dict[str, object],
) -> TraceEvent:
    fields = {
        "schema_version": TRACE_EVENT_SCHEMA,
        "sequence": sequence,
        "commit_id": commit_id,
        "commit_index": commit_index,
        "commit_size": commit_size,
        "recorded_at": recorded_at,
        "event_type": event_type,
        "environment_run_id": environment_run_id,
        "task_id": task_id,
        "trace_id": trace_id,
        "operation_id": operation_id,
        "parent_event_id": parent_event_id,
        "artifact_refs": artifact_refs,
        "data_json": _canonical_json(data),
    }
    return TraceEvent(
        event_id=_content_id("trace-event", fields),
        **fields,
    )


def _event_specs(fact: LifecycleFact) -> tuple[dict[str, object], ...]:
    from ab_harness.domain_lifecycle import DomainAdmissionRejection
    from ab_harness.domain_lifecycle import ExecutionLease
    from ab_harness.environment import ExecutionReceipt
    from ab_harness.environment import EvidenceRejection
    from ab_harness.operation_edges import OperationEdge
    from ab_harness.proposal_admission import AdmittedOperation
    from ab_harness.proposal_admission import ProposalNormalizationRejection
    from ab_harness.proposal_admission import SemanticAdmissionRejection
    from ab_harness.proposal_admission import TypedProposal
    from ab_harness.runtime_controls import BudgetDecision
    from ab_harness.runtime_controls import ExecutionCancellationDecision
    from ab_harness.runtime_controls import ExecutionFailure
    from ab_harness.runtime_controls import RetryDecision
    from ab_harness.runtime_controls import TaskTimeoutDecision
    from ab_harness.task_compiler import CompiledTask

    if isinstance(fact, TaskStartedFact):
        return (
            _spec(
                event_type="task_started",
                environment_run_id=fact.environment_run_id,
                task_id=fact.task_id,
                trace_id=fact.trace_id,
                artifact_refs=(
                    fact.ingress_artifact_id,
                    fact.decision_id,
                    fact.domain_contract_pack_revision,
                ),
                data={
                    "environment_ingress_id": fact.environment_ingress_id,
                    "ingress_artifact_id": fact.ingress_artifact_id,
                    "decision_id": fact.decision_id,
                    "domain_contract_pack_revision": (
                        fact.domain_contract_pack_revision
                    ),
                },
            ),
        )
    if isinstance(fact, TaskIngressFact):
        if fact.action not in {"resume_task", "notify_task"}:
            raise ValueError("unsupported existing-task ingress action")
        return (
            _spec(
                event_type={
                    "resume_task": "task_resumed",
                    "notify_task": "task_notified",
                }[fact.action],
                environment_run_id=fact.environment_run_id,
                task_id=fact.task_id,
                trace_id=fact.trace_id,
                artifact_refs=(
                    fact.ingress_artifact_id,
                    fact.decision_id,
                    fact.domain_contract_pack_revision,
                ),
                data={
                    "environment_ingress_id": fact.environment_ingress_id,
                    "ingress_artifact_id": fact.ingress_artifact_id,
                    "decision_id": fact.decision_id,
                    "domain_contract_pack_revision": (
                        fact.domain_contract_pack_revision
                    ),
                },
            ),
        )
    if isinstance(fact, ExecutionDispatchFact):
        if (
            fact.budget_decision.resource != "tool_call"
            or fact.budget_decision.subject_id != fact.lease.operation_id
            or fact.budget_decision.outcome != "granted"
        ):
            raise ValueError("execution dispatch requires its granted tool-call budget")
        return (
            *_event_specs(fact.budget_decision),
            *_event_specs(ExecutionStartedFact(fact.lease)),
        )
    if isinstance(fact, CompiledTask):
        fact.verify_identity()
        return (
            _spec(
                event_type="task_compiled",
                environment_run_id=fact.environment_run_id,
                task_id=fact.task_id,
                trace_id=fact.trace_id,
                artifact_refs=(fact.compiled_task_id,),
                data={
                    "compiled_task_id": fact.compiled_task_id,
                    "domain_contract_pack_revision": fact.domain_contract_pack_revision,
                    "role_id": fact.interaction_module.role.role_id,
                    "frame_id": fact.interaction_module.frame.frame_id,
                    "registry_version": fact.interaction_module.frame.registry_version,
                    "budgets": asdict(fact.budgets),
                },
            ),
        )
    if isinstance(fact, TypedProposal):
        fact.verify_identity()
        return (
            _operation_spec(
                fact,
                event_type="proposal_normalized",
                artifact_refs=(
                    fact.proposal_id,
                    fact.compiled_task_id,
                    fact.raw_output_artifact_id,
                ),
                data={
                    "proposal_id": fact.proposal_id,
                    "compiled_task_id": fact.compiled_task_id,
                    "object_id": fact.object_id,
                },
            ),
        )
    if isinstance(fact, ProposalNormalizationRejection):
        fact.verify_identity()
        artifact_refs = (fact.rejection_id, fact.compiled_task_id)
        if fact.raw_output_artifact_id is not None:
            artifact_refs = (*artifact_refs, fact.raw_output_artifact_id)
        return (
            _spec(
                event_type="proposal_rejected",
                environment_run_id=fact.environment_run_id,
                task_id=fact.task_id,
                trace_id=fact.trace_id,
                operation_id=fact.operation_id,
                artifact_refs=artifact_refs,
                data=fact.to_dict(),
            ),
        )
    if isinstance(fact, SemanticAdmissionRejection):
        fact.verify_identity()
        return (
            _operation_spec(
                fact.proposal,
                event_type="semantic_admission_rejected",
                artifact_refs=(
                    fact.rejection_id,
                    fact.proposal.proposal_id,
                    fact.compiled_task_id,
                ),
                data={
                    "rejection_id": fact.rejection_id,
                    "proposal_id": fact.proposal.proposal_id,
                    "compiled_task_id": fact.compiled_task_id,
                    "reason_codes": fact.reason_codes,
                },
            ),
        )
    if isinstance(fact, AdmittedOperation):
        fact.verify_identity()
        return (
            _operation_spec(
                fact.proposal,
                event_type="semantic_admission_accepted",
                artifact_refs=(fact.admission_id, fact.proposal_id),
                data={
                    "admission_id": fact.admission_id,
                    "proposal_id": fact.proposal_id,
                    "object_id": fact.object_id,
                    "binding_id": fact.binding_id,
                    "binding_owner": fact.binding_owner,
                    "input_schema_id": fact.input_schema_id,
                    "ab_level": fact.ab_level,
                    "frame_id": fact.frame_id,
                },
            ),
        )
    if isinstance(fact, DomainAdmissionRejection):
        fact.verify_identity()
        admitted = fact.admitted_operation
        return (
            _operation_spec(
                admitted.proposal,
                event_type="domain_admission_rejected",
                artifact_refs=(
                    fact.rejection_id,
                    admitted.admission_id,
                    fact.environment_attestation_id,
                ),
                data={
                    "rejection_id": fact.rejection_id,
                    "admission_id": admitted.admission_id,
                    "environment_attestation_id": fact.environment_attestation_id,
                    "environment_id": fact.environment_id,
                    "reason_codes": fact.reason_codes,
                },
            ),
        )
    if isinstance(fact, ExecutionLease):
        fact.verify_identity()
        admitted = fact.admitted_operation
        return (
            _operation_spec(
                admitted.proposal,
                event_type="domain_admission_leased",
                artifact_refs=(
                    fact.execution_lease_id,
                    fact.admission_id,
                    fact.environment_attestation_id,
                ),
                data={
                    "execution_lease_id": fact.execution_lease_id,
                    "admission_id": fact.admission_id,
                    "lease_owner_id": fact.lease_owner_id,
                    "object_id": fact.object_id,
                    "binding_id": fact.binding_id,
                },
            ),
        )
    if isinstance(fact, ExecutionStartedFact):
        lease = fact.lease
        lease.verify_identity()
        return (
            _operation_spec(
                lease.admitted_operation.proposal,
                event_type="execution_started",
                artifact_refs=(lease.execution_lease_id,),
                data={"execution_lease_id": lease.execution_lease_id},
            ),
        )
    if isinstance(fact, ExecutionReceipt):
        fact.verify_identity()
        evidence_id = _artifact_id("effect-evidence", fact.evidence)
        common = {
            "environment_run_id": fact.environment_run_id,
            "task_id": fact.task_id,
            "trace_id": fact.trace_id,
            "operation_id": fact.operation_id,
        }
        completed = _spec(
            event_type="execution_completed",
            artifact_refs=(fact.execution_result_id, fact.execution_lease_id),
            data={
                "execution_result_id": fact.execution_result_id,
                "execution_lease_id": fact.execution_lease_id,
                "admission_id": fact.admission_id,
                "object_id": fact.evidence.object_id,
                "binding_id": fact.evidence.binding_id,
                "owner": fact.evidence.owner,
                "succeeded": fact.owner_result.succeeded,
            },
            **common,
        )
        evidence = _spec(
            event_type="evidence_issued",
            artifact_refs=(evidence_id, fact.execution_result_id),
            data={
                "evidence_artifact_id": evidence_id,
                "native_evidence_ref": fact.evidence.evidence_ref,
                "execution_result_id": fact.execution_result_id,
                "execution_lease_id": fact.execution_lease_id,
                "object_id": fact.evidence.object_id,
                "binding_id": fact.evidence.binding_id,
                "owner": fact.evidence.owner,
                "succeeded": fact.evidence.succeeded,
                "observed_effects": fact.evidence.observed_effects,
            },
            **common,
        )
        return completed, evidence
    if isinstance(fact, EvidenceRejection):
        fact.verify_identity()
        lease = fact.lease
        common = {
            "environment_run_id": fact.environment_run_id,
            "task_id": fact.task_id,
            "trace_id": fact.trace_id,
            "operation_id": fact.operation_id,
        }
        completed = _spec(
            event_type="execution_completed",
            artifact_refs=(fact.execution_result_id, lease.execution_lease_id),
            data={
                "execution_result_id": fact.execution_result_id,
                "execution_lease_id": lease.execution_lease_id,
                "admission_id": lease.admission_id,
                "object_id": lease.object_id,
                "binding_id": lease.binding_id,
                "owner": lease.admitted_operation.binding_owner,
                "succeeded": fact.owner_result.succeeded,
            },
            **common,
        )
        rejected = _spec(
            event_type="evidence_rejected",
            artifact_refs=(fact.rejection_id, fact.execution_result_id),
            data={
                "rejection_id": fact.rejection_id,
                "execution_result_id": fact.execution_result_id,
                "execution_lease_id": lease.execution_lease_id,
                "object_id": lease.object_id,
                "binding_id": lease.binding_id,
                "owner": lease.admitted_operation.binding_owner,
                "native_evidence_ref": fact.owner_result.evidence_ref,
                "reason_codes": fact.reason_codes,
            },
            **common,
        )
        return completed, rejected
    if isinstance(fact, ExecutionFailure):
        fact.verify_identity()
        lease = fact.lease
        return (
            _operation_spec(
                lease.admitted_operation.proposal,
                event_type="execution_failed",
                artifact_refs=(
                    lease.execution_lease_id,
                    fact.failure_id,
                    fact.failure_ref,
                ),
                data={
                    "execution_lease_id": lease.execution_lease_id,
                    "failure_id": fact.failure_id,
                    "failure_ref": fact.failure_ref,
                    "failure_code": fact.failure_code,
                    "failure_stage": fact.failure_stage,
                    "retry_disposition": fact.retry_disposition,
                },
            ),
        )
    if isinstance(fact, OperationEdge):
        fact.verify_identity()
        artifact_refs = (fact.edge_id,)
        if fact.artifact_contract_ref is not None:
            artifact_refs = (*artifact_refs, fact.artifact_contract_ref)
        return (
            _spec(
                event_type="operation_edge_recorded",
                environment_run_id=fact.environment_run_id,
                task_id=fact.task_id,
                trace_id=fact.trace_id,
                operation_id=fact.source_operation_id,
                artifact_refs=artifact_refs,
                data=fact.to_dict(),
            ),
        )
    if isinstance(fact, BudgetDecision):
        fact.verify_identity()
        return (
            _spec(
                event_type="budget_%s" % fact.outcome,
                environment_run_id=fact.environment_run_id,
                task_id=fact.task_id,
                trace_id=fact.trace_id,
                operation_id=(
                    fact.subject_id
                    if fact.resource == "tool_call"
                    else None
                ),
                artifact_refs=(fact.decision_id, fact.compiled_task_id),
                data=fact.to_dict(),
            ),
        )
    if isinstance(fact, ExecutionCancellationDecision):
        fact.verify_identity()
        lease = fact.lease
        return (
            _operation_spec(
                lease.admitted_operation.proposal,
                event_type="execution_cancelled",
                artifact_refs=(
                    fact.decision_id,
                    lease.execution_lease_id,
                    fact.request_artifact_id,
                ),
                data={
                    "decision_id": fact.decision_id,
                    "execution_lease_id": lease.execution_lease_id,
                    "requester_id": fact.requester_id,
                    "request_artifact_id": fact.request_artifact_id,
                    "deciding_owner_id": fact.deciding_owner_id,
                    "phase": fact.phase,
                    "outcome": fact.outcome,
                    "reason_code": fact.reason_code,
                },
            ),
        )
    if isinstance(fact, TaskTimeoutDecision):
        fact.verify_identity()
        compiled = fact.compiled_task
        return (
            _spec(
                event_type="task_timeout_recorded",
                environment_run_id=compiled.environment_run_id,
                task_id=compiled.task_id,
                trace_id=compiled.trace_id,
                artifact_refs=(fact.decision_id, compiled.compiled_task_id),
                data={
                    "decision_id": fact.decision_id,
                    "compiled_task_id": compiled.compiled_task_id,
                    "task_started_at": fact.task_started_at,
                    "deadline_at": fact.deadline_at,
                    "observed_at": fact.observed_at,
                    "policy_revision": fact.policy_revision,
                    "outcome": fact.outcome,
                },
            ),
        )
    if isinstance(fact, RetryDecision):
        fact.verify_identity()
        return (
            _spec(
                event_type="retry_%s" % fact.outcome,
                environment_run_id=fact.environment_run_id,
                task_id=fact.task_id,
                trace_id=fact.trace_id,
                operation_id=fact.source_operation_id,
                artifact_refs=(
                    fact.decision_id,
                    fact.source_failure_id,
                    fact.compiled_task_id,
                ),
                data={
                    "decision_id": fact.decision_id,
                    "compiled_task_id": fact.compiled_task_id,
                    "source_failure_id": fact.source_failure_id,
                    "source_operation_id": fact.source_operation_id,
                    "target_operation_id": fact.target_operation_id,
                    "attempt_ordinal": fact.attempt_ordinal,
                    "retry_limit": fact.retry_limit,
                    "policy_revision": fact.policy_revision,
                    "outcome": fact.outcome,
                },
            ),
        )
    if isinstance(fact, AcceptanceFact):
        fact.compiled_task.verify_identity()
        return _acceptance_specs(fact)
    raise TypeError("unsupported lifecycle fact: %s" % type(fact).__name__)


def _spec(
    *,
    event_type: str,
    environment_run_id: str,
    task_id: str,
    trace_id: str,
    artifact_refs: tuple[str, ...],
    data: dict[str, object],
    operation_id: str | None = None,
) -> dict[str, object]:
    return {
        "event_type": event_type,
        "environment_run_id": environment_run_id,
        "task_id": task_id,
        "trace_id": trace_id,
        "operation_id": operation_id,
        "artifact_refs": artifact_refs,
        "data": data,
    }


def _operation_spec(
    proposal: TypedProposal,
    *,
    event_type: str,
    artifact_refs: tuple[str, ...],
    data: dict[str, object],
) -> dict[str, object]:
    return _spec(
        event_type=event_type,
        environment_run_id=proposal.environment_run_id,
        task_id=proposal.task_id,
        trace_id=proposal.trace_id,
        operation_id=proposal.operation_id,
        artifact_refs=artifact_refs,
        data=data,
    )


def _acceptance_specs(fact: AcceptanceFact) -> tuple[dict[str, object], ...]:
    computed = TaskAcceptanceEvaluator().evaluate(
        fact.compiled_task.effect_obligations,
        fact.evidence_set,
    )
    if computed != fact.acceptance:
        raise ValueError("task acceptance does not match obligations and evidence")
    acceptance_id = _artifact_id("task-acceptance", fact.acceptance)
    evidence_artifact_ids = tuple(
        _artifact_id("effect-evidence", evidence) for evidence in fact.evidence_set
    )
    outcome_by_id = {
        **{item: "satisfied" for item in fact.acceptance.satisfied_obligation_ids},
        **{item: "deficit" for item in fact.acceptance.deficit_obligation_ids},
        **{item: "pending" for item in fact.acceptance.pending_obligation_ids},
        **{item: "failed" for item in fact.acceptance.failed_obligation_ids},
    }
    specs: list[dict[str, object]] = []
    for obligation in fact.compiled_task.effect_obligations:
        outcome = outcome_by_id[obligation.obligation_id]
        event_outcome = "failed" if outcome in {"failed", "deficit"} else outcome
        specs.append(
            _spec(
                event_type="effect_obligation_%s" % event_outcome,
                environment_run_id=fact.compiled_task.environment_run_id,
                task_id=fact.compiled_task.task_id,
                trace_id=fact.compiled_task.trace_id,
                artifact_refs=(acceptance_id,),
                data={
                    "obligation_id": obligation.obligation_id,
                    "effect_id": obligation.effect_id,
                    "requirement": obligation.requirement,
                    "outcome": outcome,
                },
            )
        )
    terminal_type = {
        "accepted": "terminal_task_accepted",
        "accepted_with_deficit": "terminal_task_accepted_with_deficit",
        "rejected": "terminal_task_rejected",
        "suspended": "task_suspended",
    }[fact.acceptance.status]
    specs.append(
        _spec(
            event_type=terminal_type,
            environment_run_id=fact.compiled_task.environment_run_id,
            task_id=fact.compiled_task.task_id,
            trace_id=fact.compiled_task.trace_id,
            artifact_refs=(
                acceptance_id,
                fact.compiled_task.compiled_task_id,
                *evidence_artifact_ids,
            ),
            data={
                "acceptance_id": acceptance_id,
                "compiled_task_id": fact.compiled_task.compiled_task_id,
                "evidence_artifact_ids": evidence_artifact_ids,
                "status": fact.acceptance.status,
                "evidence_refs": fact.acceptance.evidence_refs,
                "satisfied_obligation_ids": fact.acceptance.satisfied_obligation_ids,
                "deficit_obligation_ids": fact.acceptance.deficit_obligation_ids,
                "pending_obligation_ids": fact.acceptance.pending_obligation_ids,
                "failed_obligation_ids": fact.acceptance.failed_obligation_ids,
            },
        )
    )
    return tuple(specs)


def _reduce_events(
    events: tuple[TraceEvent, ...],
    *,
    require_global_sequence: bool = True,
) -> dict[str, _TraceState]:
    _validate_commit_frames(events)
    states: dict[str, _TraceState] = {}
    known_event_ids: set[str] = set()
    known_task_ingress: set[tuple[str, str]] = set()
    for index, event in enumerate(events, start=1):
        if require_global_sequence and event.sequence != index:
            raise ValueError("lifecycle event sequence is not contiguous")
        if event.event_id in known_event_ids:
            raise ValueError("duplicate lifecycle event identity")
        if (
            event.parent_event_id is not None
            and event.parent_event_id not in known_event_ids
        ):
            raise ValueError("lifecycle parent event is not available")
        if event.event_type in {"task_started", "task_resumed", "task_notified"}:
            ingress_id = event.data.get("environment_ingress_id")
            if not isinstance(ingress_id, str) or not ingress_id.strip():
                raise ValueError("task ingress event requires an ingress id")
            ingress_key = (event.environment_run_id, ingress_id)
            if ingress_key in known_task_ingress:
                raise ValueError("duplicate task ingress in lifecycle ledger")
            known_task_ingress.add(ingress_key)
        state = states.get(event.trace_id)
        if state is None:
            if event.event_type != "task_started":
                raise ValueError("trace lifecycle must begin with task_started")
            if event.parent_event_id is not None:
                raise ValueError("task_started cannot have a parent event")
            state = _TraceState(
                environment_run_id=event.environment_run_id,
                task_id=event.task_id,
                trace_id=event.trace_id,
                environment_ingress_artifact_id=str(event.data["ingress_artifact_id"]),
                task_ingress_decision_id=str(event.data["decision_id"]),
                domain_contract_pack_revision=str(
                    event.data["domain_contract_pack_revision"]
                ),
            )
            states[event.trace_id] = state
        else:
            if (
                event.environment_run_id != state.environment_run_id
                or event.task_id != state.task_id
            ):
                raise ValueError("lifecycle event lineage does not match trace")
            if event.event_type == "task_started":
                raise ValueError("trace already has a task start")
            if event.parent_event_id != state.last_event_id:
                raise ValueError("trace parent event does not match causal tail")
            if state.terminal_status is not None:
                raise ValueError("lifecycle event occurs after terminal task judgment")
        _apply_event(state, event)
        state.last_event_id = event.event_id
        known_event_ids.add(event.event_id)
    return states


def _validate_commit_frames(events: tuple[TraceEvent, ...]) -> None:
    offset = 0
    while offset < len(events):
        first = events[offset]
        if first.commit_index != 1:
            raise ValueError("lifecycle commit does not begin at index one")
        end = offset + first.commit_size
        if end > len(events):
            raise ValueError("lifecycle ledger ends with an incomplete commit")
        commit = events[offset:end]
        if any(
            event.commit_id != first.commit_id
            or event.commit_size != first.commit_size
            or event.commit_index != index
            for index, event in enumerate(commit, start=1)
        ):
            raise ValueError("lifecycle commit frame is inconsistent")
        offset = end


@dataclass(frozen=True)
class _EventRule:
    prerequisite: str | None = None
    operation_scoped: bool = False


_EVENT_RULES = MappingProxyType(
    {
        "task_started": _EventRule(),
        "task_compiled": _EventRule("task_started"),
        "task_resumed": _EventRule("task_started"),
        "task_notified": _EventRule("task_started"),
        "proposal_normalized": _EventRule("task_compiled", True),
        "proposal_rejected": _EventRule("task_compiled"),
        "semantic_admission_accepted": _EventRule("proposal_normalized", True),
        "semantic_admission_rejected": _EventRule("proposal_normalized", True),
        "domain_admission_leased": _EventRule("semantic_admission_accepted", True),
        "domain_admission_rejected": _EventRule(
            "semantic_admission_accepted", True
        ),
        "execution_started": _EventRule("domain_admission_leased", True),
        "execution_completed": _EventRule("execution_started", True),
        "execution_failed": _EventRule("execution_started", True),
        "execution_cancelled": _EventRule("domain_admission_leased", True),
        "evidence_issued": _EventRule("execution_completed", True),
        "evidence_rejected": _EventRule("execution_completed", True),
        "operation_edge_recorded": _EventRule("proposal_normalized", True),
        "budget_granted": _EventRule("task_compiled"),
        "budget_exhausted": _EventRule("task_compiled"),
        "task_timeout_recorded": _EventRule("task_compiled"),
        "retry_approved": _EventRule("execution_failed", True),
        "retry_not_retryable": _EventRule("execution_failed", True),
        "retry_exhausted": _EventRule("execution_failed", True),
        "effect_obligation_satisfied": _EventRule("evidence_issued"),
        "effect_obligation_failed": _EventRule(),
        "effect_obligation_pending": _EventRule("task_compiled"),
        "terminal_task_accepted": _EventRule("effect_obligation_satisfied"),
        "terminal_task_accepted_with_deficit": _EventRule(
            "effect_obligation_failed"
        ),
        "terminal_task_rejected": _EventRule("effect_obligation_failed"),
        "task_suspended": _EventRule("effect_obligation_pending"),
    }
)


def _apply_event(state: _TraceState, event: TraceEvent) -> None:
    rule = _EVENT_RULES.get(event.event_type)
    if rule is None:
        raise ValueError("unsupported lifecycle event type: %s" % event.event_type)
    data = event.data
    _validate_event_prerequisite(state, event.event_type, data, rule)
    operation_id = _event_operation_id(event, rule)
    if event.event_type == "task_compiled":
        _apply_compiled_task(state, data)
    elif event.event_type == "proposal_normalized":
        _apply_proposal(state, operation_id, data)
    elif event.event_type == "proposal_rejected":
        _apply_normalization_rejection(state, event.operation_id, data)
    elif event.event_type == "semantic_admission_accepted":
        _apply_semantic_admission(state, operation_id, data)
    elif event.event_type == "semantic_admission_rejected":
        _apply_semantic_rejection(state, operation_id, data)
    elif event.event_type == "domain_admission_leased":
        _apply_execution_lease(state, operation_id, data)
    elif event.event_type == "domain_admission_rejected":
        _apply_domain_rejection(state, operation_id, data)
    elif event.event_type == "execution_started":
        _apply_execution_start(state, operation_id, data)
    elif event.event_type in {"execution_completed", "execution_failed"}:
        _apply_execution_terminal(state, event.event_type, operation_id, data)
    elif event.event_type == "execution_cancelled":
        _apply_execution_cancellation(state, operation_id, data)
    elif event.event_type == "evidence_issued":
        _apply_evidence(state, operation_id, data)
    elif event.event_type == "evidence_rejected":
        _apply_evidence_rejection(state, operation_id, data)
    elif event.event_type == "operation_edge_recorded":
        _apply_operation_edge(state, operation_id, data)
    elif event.event_type in {"budget_granted", "budget_exhausted"}:
        _apply_budget_decision(state, event.event_type, data)
    elif event.event_type == "task_timeout_recorded":
        _apply_timeout_decision(state, data)
    elif event.event_type.startswith("retry_"):
        _apply_retry_decision(state, event.event_type, operation_id, data)
    if event.event_type.startswith("terminal_task_") or (
        event.event_type == "task_suspended"
    ):
        _apply_task_judgment(state, event.event_type, data)
    state.event_types.append(event.event_type)


def _validate_event_prerequisite(
    state: _TraceState,
    event_type: str,
    data: dict[str, object],
    rule: _EventRule,
) -> None:
    prerequisite = rule.prerequisite
    if prerequisite is not None and prerequisite not in state.event_types:
        raise ValueError("lifecycle event %s requires %s" % (event_type, prerequisite))
    if event_type == "effect_obligation_failed":
        failure_prerequisite = {
            "deficit": "task_compiled",
            "failed": "evidence_issued",
        }.get(data.get("outcome"))
        if failure_prerequisite is None:
            raise ValueError("effect obligation failure outcome is invalid")
        if failure_prerequisite not in state.event_types:
            raise ValueError(
                "lifecycle event effect_obligation_failed requires %s"
                % failure_prerequisite
            )


def _event_operation_id(event: TraceEvent, rule: _EventRule) -> str:
    if not rule.operation_scoped:
        return ""
    if event.operation_id is None or not event.operation_id.strip():
        raise ValueError("operation lifecycle event requires an operation id")
    return event.operation_id


def _apply_compiled_task(state: _TraceState, data: dict[str, object]) -> None:
    if state.compiled_task_id is not None:
        raise ValueError("trace already has a compiled task")
    state.compiled_task_id = str(data["compiled_task_id"])
    if data["domain_contract_pack_revision"] != state.domain_contract_pack_revision:
        raise ValueError("compiled task contract does not match admitted ingress")
    state.role_id = str(data["role_id"])
    state.frame_id = str(data["frame_id"])
    state.registry_version = str(data["registry_version"])
    budgets = data.get("budgets")
    if not isinstance(budgets, dict):
        raise ValueError("compiled task requires budget limits")
    expected_budget_keys = {
        "wall_time_seconds",
        "model_calls",
        "tool_calls",
        "retry_attempts",
    }
    if set(budgets) != expected_budget_keys or any(
        not isinstance(value, int) for value in budgets.values()
    ):
        raise ValueError("compiled task budget limits are invalid")
    state.budget_limits = {str(name): value for name, value in budgets.items()}
    state.budget_consumed = {
        "model_call": 0,
        "tool_call": 0,
    }


def _apply_proposal(
    state: _TraceState,
    operation_id: str,
    data: dict[str, object],
) -> None:
    if data["compiled_task_id"] != state.compiled_task_id:
        raise ValueError("proposal does not match recorded compiled task")
    if operation_id in state.proposal_by_operation:
        raise ValueError("operation already has a normalized proposal")
    if operation_id in state.rejected_operation_ids:
        raise ValueError("rejected operation id cannot be normalized")
    state.proposal_by_operation[operation_id] = str(data["proposal_id"])


def _apply_normalization_rejection(
    state: _TraceState,
    operation_id: str | None,
    data: dict[str, object],
) -> None:
    from ab_harness.proposal_admission import ProposalNormalizationRejection

    rejection = ProposalNormalizationRejection.from_dict(data)
    if rejection.compiled_task_id != state.compiled_task_id:
        raise ValueError("proposal rejection does not match compiled task")
    if operation_id != rejection.operation_id:
        raise ValueError("proposal rejection event operation does not match artifact")
    if operation_id is not None:
        if operation_id in state.proposal_by_operation:
            raise ValueError("normalized operation cannot later be rejected")
        if operation_id in state.rejected_operation_ids:
            raise ValueError("operation already has a proposal rejection")
        state.rejected_operation_ids.add(operation_id)
    state.failure_stage = "proposal_normalization"


def _apply_semantic_admission(
    state: _TraceState,
    operation_id: str,
    data: dict[str, object],
) -> None:
    if data["proposal_id"] != state.proposal_by_operation.get(operation_id):
        raise ValueError("semantic admission does not match operation proposal")
    if operation_id in state.admission_by_operation:
        raise ValueError("operation already has a semantic admission")
    state.admission_by_operation[operation_id] = str(data["admission_id"])
    state.object_by_operation[operation_id] = str(data["object_id"])
    state.binding_by_operation[operation_id] = str(data["binding_id"])
    state.owner_by_operation[operation_id] = str(data["binding_owner"])
    state.frame_by_operation[operation_id] = str(data["frame_id"])


def _apply_semantic_rejection(
    state: _TraceState,
    operation_id: str,
    data: dict[str, object],
) -> None:
    if data["compiled_task_id"] != state.compiled_task_id:
        raise ValueError("semantic rejection does not match compiled task")
    if data["proposal_id"] != state.proposal_by_operation.get(operation_id):
        raise ValueError("semantic rejection does not match operation proposal")
    reason_codes = data["reason_codes"]
    if not isinstance(reason_codes, list) or not reason_codes:
        raise ValueError("semantic rejection requires reason codes")
    if operation_id in state.admission_by_operation:
        raise ValueError("accepted operation cannot be semantically rejected")
    state.failure_stage = "semantic_admission"


def _apply_execution_lease(
    state: _TraceState,
    operation_id: str,
    data: dict[str, object],
) -> None:
    if data["admission_id"] != state.admission_by_operation.get(operation_id):
        raise ValueError("execution lease does not match semantic admission")
    if operation_id in state.leased_operation_ids:
        raise ValueError("operation already has an execution lease")
    state.leased_operation_ids.add(operation_id)
    state.lease_by_operation[operation_id] = str(data["execution_lease_id"])


def _apply_domain_rejection(
    state: _TraceState,
    operation_id: str,
    data: dict[str, object],
) -> None:
    if data["admission_id"] != state.admission_by_operation.get(operation_id):
        raise ValueError("domain rejection does not match semantic admission")
    reason_codes = data["reason_codes"]
    if not isinstance(reason_codes, list) or not reason_codes:
        raise ValueError("domain rejection requires reason codes")
    if operation_id in state.leased_operation_ids:
        raise ValueError("leased operation cannot later be domain rejected")
    state.failure_stage = "domain_admission"


def _apply_execution_start(
    state: _TraceState,
    operation_id: str,
    data: dict[str, object],
) -> None:
    if operation_id not in state.leased_operation_ids:
        raise ValueError("execution started without a recorded lease")
    if data["execution_lease_id"] != state.lease_by_operation.get(operation_id):
        raise ValueError("execution start does not match operation lease")
    if state.task_timed_out:
        raise ValueError("execution cannot start after task timeout")
    if operation_id not in state.tool_budget_granted_operation_ids:
        raise ValueError("execution start requires a granted tool-call budget")
    if operation_id in state.started_operation_ids:
        raise ValueError("execution lease already consumed")
    if operation_id in state.terminal_operation_ids:
        raise ValueError("cancelled operation cannot start execution")
    state.started_operation_ids.add(operation_id)


def _apply_execution_terminal(
    state: _TraceState,
    event_type: str,
    operation_id: str,
    data: dict[str, object],
) -> None:
    if operation_id not in state.started_operation_ids:
        raise ValueError("execution terminated before it started")
    if data["execution_lease_id"] != state.lease_by_operation.get(operation_id):
        raise ValueError("execution result does not match operation lease")
    if operation_id in state.terminal_operation_ids:
        raise ValueError("execution already has a terminal result")
    if event_type == "execution_completed":
        expected = (
            state.admission_by_operation.get(operation_id),
            state.object_by_operation.get(operation_id),
            state.binding_by_operation.get(operation_id),
            state.owner_by_operation.get(operation_id),
        )
        observed = (
            data["admission_id"],
            data["object_id"],
            data["binding_id"],
            data["owner"],
        )
        if observed != expected:
            raise ValueError("execution receipt does not match admitted operation")
        state.result_by_operation[operation_id] = str(data["execution_result_id"])
    else:
        failure_id = data.get("failure_id")
        retry_disposition = data.get("retry_disposition")
        if not isinstance(failure_id, str) or not isinstance(
            retry_disposition, str
        ):
            raise ValueError("execution failure contract is incomplete")
        state.failure_by_operation[operation_id] = (
            failure_id,
            retry_disposition,
        )
        state.failure_stage = "execution"
    state.terminal_operation_ids.add(operation_id)


def _apply_evidence(
    state: _TraceState,
    operation_id: str,
    data: dict[str, object],
) -> None:
    if operation_id not in state.terminal_operation_ids:
        raise ValueError("evidence issued before execution terminated")
    if data["execution_lease_id"] != state.lease_by_operation.get(operation_id):
        raise ValueError("evidence does not match operation lease")
    if data["execution_result_id"] != state.result_by_operation.get(operation_id):
        raise ValueError("evidence does not match execution result")
    expected_lineage = (
        state.object_by_operation.get(operation_id),
        state.binding_by_operation.get(operation_id),
        state.owner_by_operation.get(operation_id),
    )
    observed_lineage = (data["object_id"], data["binding_id"], data["owner"])
    if observed_lineage != expected_lineage:
        raise ValueError("effect evidence does not match admitted operation")
    if operation_id in state.evidence_rejected_operation_ids:
        raise ValueError("rejected evidence cannot later be issued")
    if operation_id in state.evidence_issued_operation_ids:
        raise ValueError("operation already has issued evidence")
    state.evidence_artifact_ids.add(str(data["evidence_artifact_id"]))
    state.evidence_issued_operation_ids.add(operation_id)


def _apply_evidence_rejection(
    state: _TraceState,
    operation_id: str,
    data: dict[str, object],
) -> None:
    if operation_id not in state.terminal_operation_ids:
        raise ValueError("evidence rejected before execution completed")
    if data["execution_lease_id"] != state.lease_by_operation.get(operation_id):
        raise ValueError("evidence rejection does not match operation lease")
    if data["execution_result_id"] != state.result_by_operation.get(operation_id):
        raise ValueError("evidence rejection does not match execution result")
    expected_lineage = (
        state.object_by_operation.get(operation_id),
        state.binding_by_operation.get(operation_id),
        state.owner_by_operation.get(operation_id),
    )
    observed_lineage = (data["object_id"], data["binding_id"], data["owner"])
    if observed_lineage != expected_lineage:
        raise ValueError("evidence rejection does not match admitted operation")
    reasons = data["reason_codes"]
    if not isinstance(reasons, list) or not reasons:
        raise ValueError("evidence rejection requires reason codes")
    if operation_id in state.evidence_issued_operation_ids:
        raise ValueError("issued evidence cannot later be rejected")
    if operation_id in state.evidence_rejected_operation_ids:
        raise ValueError("operation already has rejected evidence")
    state.evidence_rejected_operation_ids.add(operation_id)
    state.failure_stage = "evidence"


def _apply_budget_decision(
    state: _TraceState,
    event_type: str,
    data: dict[str, object],
) -> None:
    if data["compiled_task_id"] != state.compiled_task_id:
        raise ValueError("budget decision does not match compiled task")
    resource = data["resource"]
    if resource not in {"model_call", "tool_call"}:
        raise ValueError("budget decision resource is invalid")
    subject_id = data["subject_id"]
    if not isinstance(subject_id, str) or not subject_id.strip():
        raise ValueError("budget decision subject is invalid")
    subject_key = (str(resource), subject_id)
    if subject_key in state.budget_subjects:
        raise ValueError("budget subject already has a decision")
    limit_key = {
        "model_call": "model_calls",
        "tool_call": "tool_calls",
    }[str(resource)]
    if data["limit"] != state.budget_limits.get(limit_key):
        raise ValueError("budget decision limit does not match compiled task")
    consumed = state.budget_consumed[str(resource)]
    if data["consumed_before"] != consumed:
        raise ValueError("budget decision consumption is stale")
    units = data["units"]
    if not isinstance(units, int) or units <= 0:
        raise ValueError("budget decision units are invalid")
    outcome = data.get("outcome")
    reason_code = data.get("reason_code")
    if event_type != "budget_%s" % outcome:
        raise ValueError("budget event does not match decision outcome")
    if event_type == "budget_granted":
        if reason_code != "within_budget" or consumed + units > data["limit"]:
            raise ValueError("budget grant outcome is inconsistent")
        if resource == "tool_call":
            if subject_id not in state.leased_operation_ids:
                raise ValueError("tool-call budget requires a recorded lease")
            if state.task_timed_out:
                raise ValueError("timed-out task cannot consume tool-call budget")
            if (
                subject_id in state.terminal_operation_ids
                and subject_id not in state.started_operation_ids
            ):
                raise ValueError("cancelled operation cannot consume tool-call budget")
        if data["consumed_after"] != consumed + units:
            raise ValueError("budget grant consumption is invalid")
        state.budget_consumed[str(resource)] = consumed + units
        if resource == "tool_call":
            state.tool_budget_granted_operation_ids.add(subject_id)
    else:
        if reason_code != "budget_exhausted" or consumed + units <= data["limit"]:
            raise ValueError("budget exhaustion outcome is inconsistent")
        if data["consumed_after"] != consumed:
            raise ValueError("exhausted budget cannot consume units")
        state.failure_stage = "budget"
    state.budget_subjects.add(subject_key)


def _apply_execution_cancellation(
    state: _TraceState,
    operation_id: str,
    data: dict[str, object],
) -> None:
    if data["execution_lease_id"] != state.lease_by_operation.get(operation_id):
        raise ValueError("cancellation does not match operation lease")
    if operation_id in state.started_operation_ids:
        raise ValueError("pre-dispatch cancellation cannot follow execution start")
    if operation_id in state.terminal_operation_ids:
        raise ValueError("operation already has a terminal result")
    if data["phase"] != "pre_dispatch" or data["outcome"] != "accepted":
        raise ValueError("unsupported cancellation decision")
    state.terminal_operation_ids.add(operation_id)
    state.failure_stage = "cancellation"


def _apply_timeout_decision(
    state: _TraceState,
    data: dict[str, object],
) -> None:
    if data["compiled_task_id"] != state.compiled_task_id:
        raise ValueError("timeout decision does not match compiled task")
    if state.task_timed_out:
        raise ValueError("task already has a terminal timeout decision")
    outcome = data["outcome"]
    if outcome not in {"within_budget", "timed_out"}:
        raise ValueError("timeout decision outcome is invalid")
    if outcome == "timed_out":
        state.task_timed_out = True
        state.failure_stage = "timeout"


def _apply_retry_decision(
    state: _TraceState,
    event_type: str,
    operation_id: str,
    data: dict[str, object],
) -> None:
    if data["compiled_task_id"] != state.compiled_task_id:
        raise ValueError("retry decision does not match compiled task")
    failure = state.failure_by_operation.get(operation_id)
    if failure is None or data["source_failure_id"] != failure[0]:
        raise ValueError("retry decision does not match execution failure")
    if data["source_operation_id"] != operation_id:
        raise ValueError("retry decision source operation is invalid")
    if failure[0] in state.retry_decided_failure_ids:
        raise ValueError("execution failure already has a retry decision")
    target_operation_id = data["target_operation_id"]
    if (
        not isinstance(target_operation_id, str)
        or not target_operation_id.strip()
        or target_operation_id in state.retry_target_operation_ids
    ):
        raise ValueError("retry target operation is invalid or already reserved")
    outcome = str(data["outcome"])
    if event_type != "retry_%s" % outcome:
        raise ValueError("retry event does not match decision outcome")
    retry_limit = state.budget_limits["retry_attempts"]
    if data["retry_limit"] != retry_limit:
        raise ValueError("retry decision limit does not match compiled task")
    prior_approved = sum(
        event == "retry_approved" for event in state.event_types
    )
    expected_ordinal = prior_approved + 1
    if data["attempt_ordinal"] != expected_ordinal:
        raise ValueError("retry decision ordinal is invalid")
    expected_outcome = (
        "not_retryable"
        if failure[1] != "retryable"
        else "approved" if expected_ordinal <= retry_limit else "exhausted"
    )
    if outcome != expected_outcome:
        raise ValueError("retry decision outcome is inconsistent")
    if outcome in {"exhausted", "not_retryable"}:
        state.failure_stage = "retry"
    state.retry_decided_failure_ids.add(failure[0])
    state.retry_target_operation_ids.add(target_operation_id)


def _apply_operation_edge(
    state: _TraceState,
    operation_id: str,
    data: dict[str, object],
) -> None:
    from ab_harness.operation_edges import OperationEdge

    edge = OperationEdge.from_dict(data)
    if operation_id != edge.source_operation_id:
        raise ValueError("operation edge event does not match source operation")
    if (
        edge.environment_run_id != state.environment_run_id
        or edge.task_id != state.task_id
        or edge.trace_id != state.trace_id
    ):
        raise ValueError("operation edge lineage does not match trace")
    if edge.source_operation_id not in state.proposal_by_operation:
        raise ValueError("edge source operation is not recorded")
    if edge.target_operation_id not in state.proposal_by_operation:
        raise ValueError("edge target operation is not recorded")
    source_frame = state.frame_by_operation.get(edge.source_operation_id)
    target_frame = state.frame_by_operation.get(edge.target_operation_id)
    if source_frame is None or target_frame is None:
        raise ValueError("operation edge requires semantically admitted operations")
    if source_frame != edge.source_frame_id or target_frame != edge.target_frame_id:
        raise ValueError("operation edge frame does not match admitted operations")
    if edge.relation == "delegates_to":
        raise ValueError(
            "cross-frame delegation requires a separately compiled target projection"
        )
    pair = (edge.source_operation_id, edge.target_operation_id)
    if any(existing[:2] == pair for existing in state.operation_edges):
        raise ValueError("operation edge pair already recorded")
    if edge.relation == "decomposes_to" and any(
        target == edge.target_operation_id
        and relation in {"decomposes_to", "delegates_to"}
        for _source, target, relation in state.operation_edges
    ):
        raise ValueError("operation already has a structural parent")
    if _operation_path_exists(
        state.operation_edges,
        edge.target_operation_id,
        edge.source_operation_id,
    ):
        raise ValueError("operation edge would create a cycle")
    if edge.target_operation_id in state.leased_operation_ids:
        raise ValueError("operation edge cannot be added after target lease")
    state.operation_edges.add(
        (edge.source_operation_id, edge.target_operation_id, edge.relation)
    )


def _operation_path_exists(
    edges: set[tuple[str, str, str]],
    source: str,
    target: str,
) -> bool:
    adjacency: dict[str, set[str]] = {}
    for edge_source, edge_target, _relation in edges:
        adjacency.setdefault(edge_source, set()).add(edge_target)
    pending = [source]
    visited: set[str] = set()
    while pending:
        current = pending.pop()
        if current == target:
            return True
        if current in visited:
            continue
        visited.add(current)
        pending.extend(adjacency.get(current, ()))
    return False


def _apply_task_judgment(
    state: _TraceState,
    event_type: str,
    data: dict[str, object],
) -> None:
    if data["compiled_task_id"] != state.compiled_task_id:
        raise ValueError("task acceptance does not match compiled task")
    acceptance_evidence = set(data["evidence_artifact_ids"])
    if acceptance_evidence != state.evidence_artifact_ids:
        raise ValueError("task acceptance evidence set is incomplete or unrecorded")
    if event_type.startswith("terminal_task_"):
        state.terminal_status = str(data["status"])
        if event_type == "terminal_task_rejected":
            state.failure_stage = "task_acceptance"


def _digest(events: tuple[TraceEvent, ...], state: _TraceState) -> VerifiedTraceDigest:
    terminal = events[-1].data
    event_data = tuple((event.event_type, event.data) for event in events)

    def values(event_type: str, field: str) -> tuple[str, ...]:
        return tuple(
            str(data[field])
            for item_type, data in event_data
            if item_type == event_type and field in data
        )

    evidence_events = tuple(
        data for event_type, data in event_data if event_type == "evidence_issued"
    )
    fields = {
        "schema_version": VERIFIED_TRACE_DIGEST_SCHEMA,
        "environment_run_id": state.environment_run_id,
        "task_id": state.task_id,
        "trace_id": state.trace_id,
        "environment_ingress_artifact_id": (state.environment_ingress_artifact_id),
        "task_ingress_decision_id": state.task_ingress_decision_id,
        "first_sequence": events[0].sequence,
        "last_sequence": events[-1].sequence,
        "event_ids": tuple(event.event_id for event in events),
        "compiled_task_id": state.compiled_task_id or "",
        "domain_contract_pack_revision": state.domain_contract_pack_revision or "",
        "role_id": state.role_id or "",
        "frame_id": state.frame_id or "",
        "registry_version": state.registry_version or "",
        "operation_ids": tuple(
            dict.fromkeys(
                event.operation_id for event in events if event.operation_id is not None
            )
        ),
        "proposal_ids": values("proposal_normalized", "proposal_id"),
        "admission_ids": values("semantic_admission_accepted", "admission_id"),
        "execution_lease_ids": values("domain_admission_leased", "execution_lease_id"),
        "execution_result_ids": values("execution_completed", "execution_result_id"),
        "evidence_artifact_ids": tuple(
            str(data["evidence_artifact_id"]) for data in evidence_events
        ),
        "native_evidence_refs": tuple(
            str(data["native_evidence_ref"]) for data in evidence_events
        ),
        "satisfied_obligation_ids": tuple(terminal["satisfied_obligation_ids"]),
        "deficit_obligation_ids": tuple(terminal["deficit_obligation_ids"]),
        "pending_obligation_ids": tuple(terminal["pending_obligation_ids"]),
        "failed_obligation_ids": tuple(terminal["failed_obligation_ids"]),
        "terminal_status": state.terminal_status or "",
        "failure_stage": state.failure_stage,
    }
    return VerifiedTraceDigest(
        digest_id=_content_id("verified-trace-digest", fields),
        **fields,
    )
