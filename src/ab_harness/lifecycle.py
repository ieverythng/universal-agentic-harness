"""Append-only lifecycle ledger and deterministic trace replay."""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from types import TracebackType
from typing import Callable, TYPE_CHECKING

from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.contracts import EffectEvidence
from ab_harness.contracts import TaskAcceptance

if TYPE_CHECKING:
    from ab_harness.domain_lifecycle import ExecutionLease
    from ab_harness.environment import ExecutionReceipt
    from ab_harness.proposal_admission import AdmittedOperation
    from ab_harness.proposal_admission import TypedProposal
    from ab_harness.task_compiler import CompiledTask


TRACE_EVENT_SCHEMA = "uah.trace_event/v1"
VERIFIED_TRACE_DIGEST_SCHEMA = "uah.verified_trace_digest/v1"


def _canonical_json(payload: object) -> str:
    try:
        return json.dumps(
            payload,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("lifecycle content must contain finite JSON values") from exc


def _content_id(prefix: str, payload: object) -> str:
    return "%s:sha256:%s" % (
        prefix,
        hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest(),
    )


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
class ExecutionFailedFact:
    lease: ExecutionLease
    failure_ref: str
    failure_type: str


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
        | AdmittedOperation
        | ExecutionLease
        | ExecutionStartedFact
        | ExecutionReceipt
        | ExecutionFailedFact
        | AcceptanceFact
    )
else:
    LifecycleFact = object


@dataclass(frozen=True)
class LifecycleCommit:
    events: tuple[TraceEvent, ...]


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
    last_event_id: str | None = None
    event_types: list[str] = field(default_factory=list)
    leased_operation_ids: set[str] = field(default_factory=set)
    started_operation_ids: set[str] = field(default_factory=set)
    terminal_operation_ids: set[str] = field(default_factory=set)
    evidence_artifact_ids: set[str] = field(default_factory=set)
    proposal_by_operation: dict[str, str] = field(default_factory=dict)
    admission_by_operation: dict[str, str] = field(default_factory=dict)
    object_by_operation: dict[str, str] = field(default_factory=dict)
    binding_by_operation: dict[str, str] = field(default_factory=dict)
    owner_by_operation: dict[str, str] = field(default_factory=dict)
    lease_by_operation: dict[str, str] = field(default_factory=dict)
    result_by_operation: dict[str, str] = field(default_factory=dict)


class LifecycleLedger:
    """Single-writer lifecycle authority with replay-derived trace digests."""

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
                raise ValueError("lifecycle ledger sequence conflict")
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
        return self.record(ExecutionStartedFact(lease))

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
        return self.record(
            ExecutionFailedFact(
                lease=lease,
                failure_ref=failure_ref,
                failure_type=failure_type,
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
    from ab_harness.domain_lifecycle import ExecutionLease
    from ab_harness.environment import ExecutionReceipt
    from ab_harness.proposal_admission import AdmittedOperation
    from ab_harness.proposal_admission import TypedProposal
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
                    "ab_level": fact.ab_level,
                    "frame_id": fact.frame_id,
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
    if isinstance(fact, ExecutionFailedFact):
        lease = fact.lease
        lease.verify_identity()
        return (
            _operation_spec(
                lease.admitted_operation.proposal,
                event_type="execution_failed",
                artifact_refs=(lease.execution_lease_id, fact.failure_ref),
                data={
                    "execution_lease_id": lease.execution_lease_id,
                    "failure_ref": fact.failure_ref,
                    "failure_type": fact.failure_type,
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


_SUPPORTED_EVENT_TYPES = {
    "task_started",
    "task_compiled",
    "task_resumed",
    "task_notified",
    "proposal_normalized",
    "semantic_admission_accepted",
    "domain_admission_leased",
    "execution_started",
    "execution_completed",
    "execution_failed",
    "evidence_issued",
    "effect_obligation_satisfied",
    "effect_obligation_failed",
    "effect_obligation_pending",
    "terminal_task_accepted",
    "terminal_task_accepted_with_deficit",
    "terminal_task_rejected",
    "task_suspended",
}
_EVENT_PREREQUISITES = {
    "task_compiled": "task_started",
    "task_resumed": "task_started",
    "task_notified": "task_started",
    "proposal_normalized": "task_compiled",
    "semantic_admission_accepted": "proposal_normalized",
    "domain_admission_leased": "semantic_admission_accepted",
    "execution_started": "domain_admission_leased",
    "execution_completed": "execution_started",
    "execution_failed": "execution_started",
    "evidence_issued": "execution_completed",
    "effect_obligation_satisfied": "evidence_issued",
    "effect_obligation_pending": "task_compiled",
    "terminal_task_accepted": "effect_obligation_satisfied",
    "terminal_task_accepted_with_deficit": "effect_obligation_failed",
    "terminal_task_rejected": "effect_obligation_failed",
    "task_suspended": "effect_obligation_pending",
}
_OPERATION_EVENT_TYPES = {
    "proposal_normalized",
    "semantic_admission_accepted",
    "domain_admission_leased",
    "execution_started",
    "execution_completed",
    "execution_failed",
    "evidence_issued",
}


def _apply_event(state: _TraceState, event: TraceEvent) -> None:
    if event.event_type not in _SUPPORTED_EVENT_TYPES:
        raise ValueError("unsupported lifecycle event type: %s" % event.event_type)
    data = event.data
    _validate_event_prerequisite(state, event.event_type, data)
    operation_id = _event_operation_id(event)
    if event.event_type == "task_compiled":
        _apply_compiled_task(state, data)
    elif event.event_type == "proposal_normalized":
        _apply_proposal(state, operation_id, data)
    elif event.event_type == "semantic_admission_accepted":
        _apply_semantic_admission(state, operation_id, data)
    elif event.event_type == "domain_admission_leased":
        _apply_execution_lease(state, operation_id, data)
    elif event.event_type == "execution_started":
        _apply_execution_start(state, operation_id, data)
    elif event.event_type in {"execution_completed", "execution_failed"}:
        _apply_execution_terminal(state, event.event_type, operation_id, data)
    elif event.event_type == "evidence_issued":
        _apply_evidence(state, operation_id, data)
    if event.event_type.startswith("terminal_task_") or (
        event.event_type == "task_suspended"
    ):
        _apply_task_judgment(state, event.event_type, data)
    state.event_types.append(event.event_type)


def _validate_event_prerequisite(
    state: _TraceState,
    event_type: str,
    data: dict[str, object],
) -> None:
    prerequisite = _EVENT_PREREQUISITES.get(event_type)
    if prerequisite is not None and prerequisite not in state.event_types:
        raise ValueError(
            "lifecycle event %s requires %s" % (event_type, prerequisite)
        )
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


def _event_operation_id(event: TraceEvent) -> str:
    if event.event_type not in _OPERATION_EVENT_TYPES:
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


def _apply_proposal(
    state: _TraceState,
    operation_id: str,
    data: dict[str, object],
) -> None:
    if data["compiled_task_id"] != state.compiled_task_id:
        raise ValueError("proposal does not match recorded compiled task")
    if operation_id in state.proposal_by_operation:
        raise ValueError("operation already has a normalized proposal")
    state.proposal_by_operation[operation_id] = str(data["proposal_id"])


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


def _apply_execution_start(
    state: _TraceState,
    operation_id: str,
    data: dict[str, object],
) -> None:
    if operation_id not in state.leased_operation_ids:
        raise ValueError("execution started without a recorded lease")
    if data["execution_lease_id"] != state.lease_by_operation.get(operation_id):
        raise ValueError("execution start does not match operation lease")
    if operation_id in state.started_operation_ids:
        raise ValueError("execution lease already consumed")
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
    state.evidence_artifact_ids.add(str(data["evidence_artifact_id"]))


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
        "failure_stage": None,
    }
    return VerifiedTraceDigest(
        digest_id=_content_id("verified-trace-digest", fields),
        **fields,
    )
