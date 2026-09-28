import json

import pytest

from ab_harness import EnvironmentTaskRegistry
from ab_harness import JsonlTaskLifecycleStore
from ab_harness import TaskAcceptance
from ab_harness import TaskLifecycleEvent
from ab_harness import TaskLineage


def _lifecycle_events():
    registry = EnvironmentTaskRegistry()
    lineage = TaskLineage(
        environment_run_id='environment-run:persistence:001',
        task_id='task:persistence:001',
        trace_id='trace:sha256:persistence-001',
        starting_environment_ingress_id='environment-ingress:persistence:start',
    )
    registry.register_start(lineage)
    registry.record_acceptance(
        environment_run_id=lineage.environment_run_id,
        task_id=lineage.task_id,
        acceptance=TaskAcceptance(
            status='accepted',
            satisfied_obligation_ids=('obligation:persistence:required',),
            evidence_refs=('evidence:persistence:required',),
        ),
    )
    return registry.lifecycle_events()


def test_task_lifecycle_event_has_a_strict_versioned_round_trip():
    event = _lifecycle_events()[0]

    payload = event.to_dict()
    restored = TaskLifecycleEvent.from_dict(payload)

    assert payload == {
        'schema_version': 'uah.task_lifecycle_event/v1',
        'event_id': event.event_id,
        'event_type': 'task_started',
        'environment_run_id': 'environment-run:persistence:001',
        'task_id': 'task:persistence:001',
        'trace_id': 'trace:sha256:persistence-001',
        'task_status': 'active',
        'source_ref': 'environment-ingress:persistence:start',
    }
    assert restored == event


def test_jsonl_store_appends_and_loads_lifecycle_events(tmp_path):
    events = _lifecycle_events()
    path = tmp_path / 'task-lifecycle.jsonl'
    store = JsonlTaskLifecycleStore(path)

    for event in events:
        store.append(event)

    lines = path.read_text(encoding='utf-8').splitlines()
    assert tuple(json.loads(line) for line in lines) == tuple(
        event.to_dict() for event in events
    )
    assert store.load_all() == events


def test_store_reconstructs_registry_state_after_process_restart(tmp_path):
    events = _lifecycle_events()
    path = tmp_path / 'restart-task-lifecycle.jsonl'
    writer = JsonlTaskLifecycleStore(path)
    for event in events:
        writer.append(event)

    restarted_registry = JsonlTaskLifecycleStore(path).load_registry()

    assert restarted_registry.lifecycle_events() == events


def test_store_rejects_a_blank_record_inside_the_event_stream(tmp_path):
    events = _lifecycle_events()
    path = tmp_path / 'blank-record.jsonl'
    records = tuple(
        json.dumps(event.to_dict(), sort_keys=True, separators=(',', ':'))
        for event in events
    )
    path.write_text(records[0] + '\n\n' + records[1] + '\n', encoding='utf-8')

    store = JsonlTaskLifecycleStore(path)

    with pytest.raises(
        ValueError, match='invalid task lifecycle event at line 2'
    ):
        store.load_registry()


def test_store_rejects_non_utf8_content_before_replay(tmp_path):
    path = tmp_path / 'invalid-utf8.jsonl'
    path.write_bytes(b'\xff\n')

    with pytest.raises(ValueError, match='not valid UTF-8'):
        JsonlTaskLifecycleStore(path).load_registry()


def test_store_rejects_duplicate_events_as_a_failed_replay(tmp_path):
    event = _lifecycle_events()[0]
    record = json.dumps(event.to_dict(), sort_keys=True, separators=(',', ':'))
    path = tmp_path / 'duplicate-event.jsonl'
    path.write_text(record + '\n' + record + '\n', encoding='utf-8')

    with pytest.raises(ValueError, match='task lifecycle replay failed'):
        JsonlTaskLifecycleStore(path).load_registry()


def test_store_rejects_an_unterminated_final_record(tmp_path):
    event = _lifecycle_events()[0]
    record = json.dumps(event.to_dict(), sort_keys=True, separators=(',', ':'))
    path = tmp_path / 'unterminated-event.jsonl'
    path.write_text(record, encoding='utf-8')

    with pytest.raises(ValueError, match='unterminated final record'):
        JsonlTaskLifecycleStore(path).load_registry()
