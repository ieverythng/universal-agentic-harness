import pytest

from ab_harness.lifecycle import LifecycleLedger
from ab_harness.observatory import (
    ObservatoryDataLabel,
    ObservatoryTraceStatus,
    project_observatory,
    render_observatory,
)


def raw_events():
    from test_two_stage_admission import _admission_fixture, _record_task_start

    ledger = LifecycleLedger(clock=lambda: "2026-10-08T15:30:00Z")
    compiled, _, _ = _admission_fixture()
    _record_task_start(ledger, compiled)
    return ledger, ledger.events()


def test_raw_stale_terminal_kind_rejects_before_deriving_accepted_status():
    ledger, events = raw_events()
    assert project_observatory(events).traces[0].status is ObservatoryTraceStatus.OPEN
    original_id = events[0].event_id
    object.__setattr__(events[0], "event_type", "terminal_task_accepted")

    with pytest.raises(ValueError, match="identity does not match"):
        project_observatory(events)

    assert events[0].event_id == original_id
    assert project_observatory(ledger).traces[0].status is ObservatoryTraceStatus.OPEN
    assert project_observatory(ledger).data_label is ObservatoryDataLabel.RECORDED


@pytest.mark.parametrize(
    "field,value",
    (
        ("environment_run_id", "environment-run:foreign"),
        ("trace_id", "trace:foreign"),
        ("sequence", 999),
        ("recorded_at", "2026-10-09T00:00:00Z"),
        ("artifact_refs", ("artifact:foreign",)),
    ),
)
def test_raw_identity_validation_precedes_grouping_and_ordering(field, value):
    _, events = raw_events()
    object.__setattr__(events[0], field, value)
    with pytest.raises(ValueError, match="identity does not match"):
        project_observatory(iter(events))


def test_valid_generator_and_ledger_views_preserve_the_same_read_only_lineage():
    ledger, events = raw_events()
    raw = project_observatory(event for event in events)
    recorded = project_observatory(ledger)
    assert raw.data_label is ObservatoryDataLabel.SYNTHETIC
    assert raw.traces[0].status is recorded.traces[0].status is ObservatoryTraceStatus.OPEN
    assert raw.traces[0].events == recorded.traces[0].events == events
    assert ledger.events() == events


def test_duplicate_valid_events_and_foreign_values_remain_rejected():
    _, events = raw_events()
    with pytest.raises(ValueError, match="identities must be unique"):
        project_observatory((*events, *events))
    with pytest.raises(TypeError, match="TraceEvent values only"):
        project_observatory((object(),))


def test_v1_actor_field_excluded_from_its_hash_cannot_invent_an_actor_view():
    _, events = raw_events()
    object.__setattr__(events[0], "agent_run_id", "agent-run:forged")
    events[0].verify_identity()
    with pytest.raises(ValueError, match="v1 events require task scope without actor identity"):
        project_observatory(events)


@pytest.mark.parametrize("actor", (None, "agent-run:forged"))
def test_v1_scope_mutation_cannot_hide_a_task_trace_in_projection_or_render(actor):
    _, events = raw_events()
    object.__setattr__(events[0], "event_scope", "agent")
    object.__setattr__(events[0], "agent_run_id", actor)
    events[0].verify_identity()
    for project in (project_observatory, render_observatory):
        with pytest.raises(ValueError, match="v1 events require task scope without actor identity"):
            project(event for event in events)


def test_projection_detaches_raw_values_from_later_input_mutation():
    _, events = raw_events()
    projected = project_observatory(events)
    object.__setattr__(events[0], "agent_run_id", "agent-run:later-mutation")
    assert projected.events[0].agent_run_id is None
    assert projected.traces[0].status is ObservatoryTraceStatus.OPEN
    assert not projected.agent_runs


def test_valid_mixed_v1_and_v2_history_preserves_explicit_actor_membership(tmp_path):
    from tests.test_observatory import _attached_actor_ledger

    _, task_events = raw_events()
    actor_ledger, attached = _attached_actor_ledger(tmp_path / "actors.jsonl")
    combined = (*task_events, *actor_ledger.events())
    projected = project_observatory(iter(combined))
    assert projected.traces[0].trace_id == task_events[0].trace_id
    assert projected.agent_run(attached.agent_run_id).events == actor_ledger.events()
    assert projected.events != ()
    assert project_observatory(actor_ledger).agent_runs == project_observatory(
        actor_ledger.events()
    ).agent_runs


def test_valid_incomplete_terminal_illustration_keeps_its_synthetic_label():
    from tests.test_observatory import _event

    event = _event(1, "terminal_task_accepted", trace_id="trace:illustrative")
    projected = project_observatory((event,))
    assert projected.data_label is ObservatoryDataLabel.SYNTHETIC
    assert projected.traces[0].status is ObservatoryTraceStatus.ACCEPTED
    assert render_observatory((event,)).projection.data_label is ObservatoryDataLabel.SYNTHETIC
