"""Append-only persistence for validated task lifecycle events."""

from __future__ import annotations

import json
import os
from pathlib import Path

from ab_harness.task_registry import EnvironmentTaskRegistry
from ab_harness.task_registry import TaskLifecycleEvent


class JsonlTaskLifecycleStore:
    """Persist one canonical task lifecycle event per durable JSONL record."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, event: TaskLifecycleEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        record = json.dumps(
            event.to_dict(),
            sort_keys=True,
            separators=(',', ':'),
        )
        with self.path.open('a', encoding='utf-8') as stream:
            stream.write(record + '\n')
            stream.flush()
            os.fsync(stream.fileno())

    def load_all(self) -> tuple[TaskLifecycleEvent, ...]:
        if not self.path.exists():
            return ()
        try:
            content = self.path.read_text(encoding='utf-8')
        except UnicodeDecodeError as exc:
            raise ValueError('task lifecycle store is not valid UTF-8') from exc
        if content and not content.endswith('\n'):
            raise ValueError('task lifecycle store has an unterminated final record')
        events: list[TaskLifecycleEvent] = []
        for line_number, line in enumerate(
            content.splitlines(),
            start=1,
        ):
            if not line.strip():
                raise ValueError(
                    'invalid task lifecycle event at line %d' % line_number
                )
            try:
                payload = json.loads(line)
                if not isinstance(payload, dict):
                    raise ValueError('event record must be a JSON object')
                events.append(TaskLifecycleEvent.from_dict(payload))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    'invalid task lifecycle event at line %d' % line_number
                ) from exc
        return tuple(events)

    def load_registry(self) -> EnvironmentTaskRegistry:
        events = self.load_all()
        try:
            return EnvironmentTaskRegistry.replay(events)
        except (KeyError, ValueError) as exc:
            raise ValueError('task lifecycle replay failed') from exc
