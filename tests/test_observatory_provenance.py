"""Public O1 provenance labels cannot claim unsupported evaluation evidence."""

import json

import pytest

from ab_harness.lifecycle import LifecycleLedger
from ab_harness.observatory import ObservatoryDataLabel
from ab_harness.observatory import project_observatory
from ab_harness.observatory import render_observatory
from tests.test_observatory import _event
from tests.test_two_stage_admission import _admission_fixture, _record_task_start


def test_raw_events_cannot_claim_measured_provenance():
    events = (_event(1, "task_started", trace_id="trace:provenance"),)
    with pytest.raises(ValueError, match="does not support measured or reviewed"):
        project_observatory(events, data_label="measured")


def _inputs(tmp_path, source_kind, nonempty):
    ledger = LifecycleLedger(tmp_path / "provenance.jsonl")
    if nonempty:
        compiled, _, _ = _admission_fixture()
        _record_task_start(ledger, compiled)
    events = ledger.events()
    source = {
        "ledger": ledger,
        "tuple": events,
        "generator": (event for event in events),
    }[source_kind]
    return source, ledger, events


def _file_state(ledger):
    return ledger.path.read_bytes() if ledger.path.exists() else None


def _projection(consumer, source, label):
    result = consumer(source, data_label=label)
    return result.projection if consumer is render_observatory else result


@pytest.mark.parametrize("label", ("measured", "reviewed"))
@pytest.mark.parametrize("label_form", ("string", "enum"))
@pytest.mark.parametrize("source_kind", ("ledger", "tuple", "generator"))
@pytest.mark.parametrize("nonempty", (False, True))
@pytest.mark.parametrize("consumer", (project_observatory, render_observatory))
def test_unsupported_provenance_rejects_every_public_route_without_writing(
    tmp_path, label, label_form, source_kind, nonempty, consumer
):
    source, ledger, events = _inputs(tmp_path, source_kind, nonempty)
    before = _file_state(ledger)
    requested = ObservatoryDataLabel(label) if label_form == "enum" else label

    with pytest.raises(ValueError, match="does not support measured or reviewed"):
        consumer(source, data_label=requested)

    assert _file_state(ledger) == before
    assert ledger.events() == events
    if nonempty:
        assert ledger.replay(events[0].trace_id).events == events


@pytest.mark.parametrize("label", (
    "conceptual", "synthetic", ObservatoryDataLabel.CONCEPTUAL,
    ObservatoryDataLabel.SYNTHETIC,
))
@pytest.mark.parametrize("source_kind", ("ledger", "tuple", "generator"))
@pytest.mark.parametrize("nonempty", (False, True))
@pytest.mark.parametrize("consumer", (project_observatory, render_observatory))
def test_supported_explicit_labels_preserve_read_only_lineage(
    tmp_path, label, source_kind, nonempty, consumer
):
    source, ledger, events = _inputs(tmp_path, source_kind, nonempty)
    before = _file_state(ledger)
    projection = _projection(consumer, source, label)

    assert projection.data_label == ObservatoryDataLabel(label)
    assert all(trace.data_label == ObservatoryDataLabel(label) for trace in projection.traces)
    assert projection.events == events
    assert ledger.events() == events
    assert _file_state(ledger) == before


@pytest.mark.parametrize("label", (None, "", False, 0))
@pytest.mark.parametrize("source_kind", ("ledger", "tuple", "generator"))
@pytest.mark.parametrize("nonempty", (False, True))
@pytest.mark.parametrize("consumer", (project_observatory, render_observatory))
def test_existing_falsey_requests_keep_the_source_default(
    tmp_path, label, source_kind, nonempty, consumer
):
    source, ledger, events = _inputs(tmp_path, source_kind, nonempty)
    before = _file_state(ledger)
    projection = _projection(consumer, source, label)

    assert projection.data_label is (
        ObservatoryDataLabel.RECORDED if source_kind == "ledger"
        else ObservatoryDataLabel.SYNTHETIC
    )
    assert projection.events == events
    assert _file_state(ledger) == before


@pytest.mark.parametrize("label", ("recorded", ObservatoryDataLabel.RECORDED))
@pytest.mark.parametrize("source_kind", ("tuple", "generator"))
@pytest.mark.parametrize("nonempty", (False, True))
@pytest.mark.parametrize("consumer", (project_observatory, render_observatory))
def test_raw_recorded_request_remains_rejected(
    tmp_path, label, source_kind, nonempty, consumer
):
    source, ledger, events = _inputs(tmp_path, source_kind, nonempty)
    before = _file_state(ledger)
    with pytest.raises(ValueError, match="requires a validated ledger"):
        consumer(source, data_label=label)
    assert ledger.events() == events
    assert _file_state(ledger) == before


@pytest.mark.parametrize("source_kind", ("ledger", "tuple", "generator"))
@pytest.mark.parametrize("consumer", (project_observatory, render_observatory))
def test_unknown_label_keeps_the_enum_validation_error(tmp_path, source_kind, consumer):
    source, ledger, events = _inputs(tmp_path, source_kind, True)
    with pytest.raises(ValueError, match="is not a valid ObservatoryDataLabel"):
        consumer(source, data_label="unsupported-label")
    assert ledger.events() == events


@pytest.mark.parametrize("label", ("recorded", ObservatoryDataLabel.RECORDED))
@pytest.mark.parametrize("nonempty", (False, True))
@pytest.mark.parametrize("consumer", (project_observatory, render_observatory))
def test_explicit_recorded_ledger_replay_keeps_projection_graph_and_file_bytes(
    tmp_path, label, nonempty, consumer
):
    source, ledger, events = _inputs(tmp_path, "ledger", nonempty)
    before = _file_state(ledger)
    default = consumer(source)
    explicit = consumer(LifecycleLedger(ledger.path), data_label=label)

    assert explicit == default
    projection = explicit.projection if consumer is render_observatory else explicit
    assert projection.data_label is ObservatoryDataLabel.RECORDED
    assert projection.events == events
    if consumer is render_observatory:
        graph = json.loads(explicit.graph_json)
        assert graph["data_label"] == "recorded"
    assert _file_state(ledger) == before
