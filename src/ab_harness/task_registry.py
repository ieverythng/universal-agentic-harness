"""Environment-scoped task lineage registered before agent work begins."""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
import hashlib
import json

from ab_harness.contracts import TaskAcceptance


_TASK_LIFECYCLE_EVENT_DOMAIN = 'uah-task-lifecycle-event-v1'
TASK_LIFECYCLE_EVENT_SCHEMA = 'uah.task_lifecycle_event/v1'
_TASK_LIFECYCLE_EVENT_FIELDS = {
    'schema_version',
    'event_id',
    'event_type',
    'environment_run_id',
    'task_id',
    'trace_id',
    'task_status',
    'source_ref',
}


def _event_id(
    *,
    event_type: str,
    environment_run_id: str,
    task_id: str,
    trace_id: str,
    task_status: str,
    source_ref: str,
) -> str:
    digest = hashlib.sha256(
        b'\0'.join(
            item.encode('utf-8')
            for item in (
                _TASK_LIFECYCLE_EVENT_DOMAIN,
                event_type,
                environment_run_id,
                task_id,
                trace_id,
                task_status,
                source_ref,
            )
        )
    ).hexdigest()
    return 'task-lifecycle-event:sha256:%s' % digest


def _acceptance_ref(acceptance: TaskAcceptance) -> str:
    payload = json.dumps(
        asdict(acceptance),
        sort_keys=True,
        separators=(',', ':'),
    ).encode('utf-8')
    return 'task-acceptance:sha256:%s' % hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class TaskLifecycleEvent:
    """Replayable task registration or acceptance transition."""

    event_id: str
    event_type: str
    environment_run_id: str
    task_id: str
    trace_id: str
    task_status: str
    source_ref: str

    def __post_init__(self) -> None:
        allowed = {
            'task_started': 'active',
            'task_resumed': 'active',
            'task_notified': 'active',
            'task_suspended': 'suspended',
            'terminal_task_accepted': 'accepted',
            'terminal_task_accepted_with_deficit': 'accepted_with_deficit',
            'terminal_task_rejected': 'rejected',
        }
        if allowed.get(self.event_type) != self.task_status:
            raise ValueError('invalid task lifecycle event type or status')
        expected = _event_id(
            event_type=self.event_type,
            environment_run_id=self.environment_run_id,
            task_id=self.task_id,
            trace_id=self.trace_id,
            task_status=self.task_status,
            source_ref=self.source_ref,
        )
        if self.event_id != expected:
            raise ValueError('task lifecycle event identity does not match content')

    def to_dict(self) -> dict[str, str]:
        return {
            'schema_version': TASK_LIFECYCLE_EVENT_SCHEMA,
            'event_id': self.event_id,
            'event_type': self.event_type,
            'environment_run_id': self.environment_run_id,
            'task_id': self.task_id,
            'trace_id': self.trace_id,
            'task_status': self.task_status,
            'source_ref': self.source_ref,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> TaskLifecycleEvent:
        keys = set(payload)
        if keys != _TASK_LIFECYCLE_EVENT_FIELDS:
            missing = sorted(_TASK_LIFECYCLE_EVENT_FIELDS - keys)
            unknown = sorted(keys - _TASK_LIFECYCLE_EVENT_FIELDS)
            raise ValueError(
                'invalid task lifecycle event fields; missing=%s unknown=%s'
                % (missing, unknown)
            )
        if payload['schema_version'] != TASK_LIFECYCLE_EVENT_SCHEMA:
            raise ValueError(
                'unsupported task lifecycle event schema: %s'
                % payload['schema_version']
            )
        event_fields = {
            name: payload[name]
            for name in _TASK_LIFECYCLE_EVENT_FIELDS
            if name != 'schema_version'
        }
        invalid = tuple(
            name
            for name, value in event_fields.items()
            if not isinstance(value, str) or not value
        )
        if invalid:
            raise ValueError(
                'task lifecycle event fields must be non-empty strings: %s'
                % ', '.join(sorted(invalid))
            )
        return cls(**event_fields)


@dataclass(frozen=True)
class TaskLineage:
    """Immutable identity assigned to one domain task in an environment run."""

    environment_run_id: str
    task_id: str
    trace_id: str
    starting_environment_ingress_id: str

    def __post_init__(self) -> None:
        required = {
            'environment_run_id': self.environment_run_id,
            'task_id': self.task_id,
            'trace_id': self.trace_id,
            'starting_environment_ingress_id': (
                self.starting_environment_ingress_id
            ),
        }
        missing = tuple(name for name, value in required.items() if not value.strip())
        if missing:
            raise ValueError(
                'task lineage fields must not be empty: %s' % ', '.join(missing)
            )


def _lifecycle_event(
    *,
    event_type: str,
    lineage: TaskLineage,
    task_status: str,
    source_ref: str,
) -> TaskLifecycleEvent:
    return TaskLifecycleEvent(
        event_id=_event_id(
            event_type=event_type,
            environment_run_id=lineage.environment_run_id,
            task_id=lineage.task_id,
            trace_id=lineage.trace_id,
            task_status=task_status,
            source_ref=source_ref,
        ),
        event_type=event_type,
        environment_run_id=lineage.environment_run_id,
        task_id=lineage.task_id,
        trace_id=lineage.trace_id,
        task_status=task_status,
        source_ref=source_ref,
    )


class DuplicateEnvironmentIngressError(ValueError):
    """Raised when task-bearing ingress has already been registered."""

    def __init__(self, lineage: TaskLineage) -> None:
        super().__init__(lineage.starting_environment_ingress_id)
        self.lineage = lineage


class TaskAlreadyRegisteredError(ValueError):
    """Raised when another ingress tries to start an existing domain task."""

    def __init__(self, lineage: TaskLineage) -> None:
        super().__init__(lineage.task_id)
        self.lineage = lineage


class UnknownTaskError(KeyError):
    """Raised when existing-task ingress has no registered lineage."""


class TaskTerminalError(ValueError):
    """Raised when ingress targets a task with a terminal judgment."""

    def __init__(self, lineage: TaskLineage, status: str) -> None:
        super().__init__(status)
        self.lineage = lineage
        self.status = status


class EnvironmentTaskRegistry:
    """Register task lineage beneath its exact environment activation."""

    def __init__(self) -> None:
        self._lineage_by_ingress: dict[tuple[str, str], TaskLineage] = {}
        self._lineage_by_task: dict[tuple[str, str], TaskLineage] = {}
        self._terminal_status_by_task: dict[tuple[str, str], str] = {}
        self._lifecycle_events: list[TaskLifecycleEvent] = []
        self._lifecycle_event_ids: set[str] = set()

    def register_start(self, lineage: TaskLineage) -> None:
        ingress_key = (
            lineage.environment_run_id,
            lineage.starting_environment_ingress_id,
        )
        existing = self._lineage_by_ingress.get(ingress_key)
        if existing is not None:
            raise DuplicateEnvironmentIngressError(existing)
        task_key = (lineage.environment_run_id, lineage.task_id)
        existing = self._lineage_by_task.get(task_key)
        if existing is not None:
            raise TaskAlreadyRegisteredError(existing)
        self._lineage_by_ingress[ingress_key] = lineage
        self._lineage_by_task[task_key] = lineage
        self._append_event(
            _lifecycle_event(
                event_type='task_started',
                lineage=lineage,
                task_status='active',
                source_ref=lineage.starting_environment_ingress_id,
            )
        )

    def register_existing_ingress(
        self,
        *,
        environment_run_id: str,
        environment_ingress_id: str,
        task_id: str,
        ingress_action: str,
    ) -> TaskLineage:
        ingress_key = (environment_run_id, environment_ingress_id)
        existing = self._lineage_by_ingress.get(ingress_key)
        if existing is not None:
            raise DuplicateEnvironmentIngressError(existing)
        task_key = (environment_run_id, task_id)
        try:
            lineage = self._lineage_by_task[task_key]
        except KeyError as exc:
            raise UnknownTaskError(task_id) from exc
        terminal_status = self._terminal_status_by_task.get(task_key)
        if terminal_status is not None:
            raise TaskTerminalError(lineage, terminal_status)
        self._lineage_by_ingress[ingress_key] = lineage
        event_type = {
            'resume_task': 'task_resumed',
            'notify_task': 'task_notified',
        }[ingress_action]
        self._append_event(
            _lifecycle_event(
                event_type=event_type,
                lineage=lineage,
                task_status='active',
                source_ref=environment_ingress_id,
            )
        )
        return lineage

    def record_acceptance(
        self,
        *,
        environment_run_id: str,
        task_id: str,
        acceptance: TaskAcceptance,
    ) -> None:
        task_key = (environment_run_id, task_id)
        if task_key not in self._lineage_by_task:
            raise UnknownTaskError(task_id)
        terminal_status = self._terminal_status_by_task.get(task_key)
        if terminal_status is not None:
            raise ValueError('task already terminal: %s' % terminal_status)
        if acceptance.status not in {
            'accepted',
            'accepted_with_deficit',
            'rejected',
            'suspended',
        }:
            raise ValueError(
                'invalid task acceptance status: %s' % acceptance.status
            )
        lineage = self._lineage_by_task[task_key]
        self._record_acceptance_status(
            lineage=lineage,
            status=acceptance.status,
            source_ref=_acceptance_ref(acceptance),
        )

    def lifecycle_events(self) -> tuple[TaskLifecycleEvent, ...]:
        return tuple(self._lifecycle_events)

    @classmethod
    def replay(
        cls,
        events: tuple[TaskLifecycleEvent, ...],
    ) -> EnvironmentTaskRegistry:
        registry = cls()
        for event in events:
            if event.event_type == 'task_started':
                registry.register_start(
                    TaskLineage(
                        environment_run_id=event.environment_run_id,
                        task_id=event.task_id,
                        trace_id=event.trace_id,
                        starting_environment_ingress_id=event.source_ref,
                    )
                )
                if registry._lifecycle_events[-1] != event:
                    raise ValueError('replayed task-start event does not match')
                continue
            if event.event_type in {
                'task_suspended',
                'terminal_task_accepted',
                'terminal_task_accepted_with_deficit',
                'terminal_task_rejected',
            }:
                task_key = (event.environment_run_id, event.task_id)
                try:
                    lineage = registry._lineage_by_task[task_key]
                except KeyError as exc:
                    raise ValueError(
                        'task acceptance event precedes task start: %s'
                        % event.task_id
                    ) from exc
                if lineage.trace_id != event.trace_id:
                    raise ValueError('task acceptance trace does not match lineage')
                registry._record_acceptance_status(
                    lineage=lineage,
                    status=event.task_status,
                    source_ref=event.source_ref,
                )
                if registry._lifecycle_events[-1] != event:
                    raise ValueError('replayed task-acceptance event does not match')
                continue
            if event.event_type in {'task_resumed', 'task_notified'}:
                ingress_action = {
                    'task_resumed': 'resume_task',
                    'task_notified': 'notify_task',
                }[event.event_type]
                registry.register_existing_ingress(
                    environment_run_id=event.environment_run_id,
                    environment_ingress_id=event.source_ref,
                    task_id=event.task_id,
                    ingress_action=ingress_action,
                )
                if registry._lifecycle_events[-1] != event:
                    raise ValueError(
                        'replayed existing-task event does not match'
                    )
                continue
            raise ValueError('unsupported task lifecycle event: %s' % event.event_type)
        return registry

    def _record_acceptance_status(
        self,
        *,
        lineage: TaskLineage,
        status: str,
        source_ref: str,
    ) -> None:
        task_key = (lineage.environment_run_id, lineage.task_id)
        terminal_status = self._terminal_status_by_task.get(task_key)
        if terminal_status is not None:
            raise ValueError('task already terminal: %s' % terminal_status)
        if status != 'suspended':
            self._terminal_status_by_task[task_key] = status
        event_type = {
            'accepted': 'terminal_task_accepted',
            'accepted_with_deficit': 'terminal_task_accepted_with_deficit',
            'rejected': 'terminal_task_rejected',
            'suspended': 'task_suspended',
        }[status]
        self._append_event(
            _lifecycle_event(
                event_type=event_type,
                lineage=lineage,
                task_status=status,
                source_ref=source_ref,
            )
        )

    def _append_event(self, event: TaskLifecycleEvent) -> None:
        if event.event_id in self._lifecycle_event_ids:
            raise ValueError(
                'task lifecycle event already registered: %s' % event.event_id
            )
        self._lifecycle_events.append(event)
        self._lifecycle_event_ids.add(event.event_id)
