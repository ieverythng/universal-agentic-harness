import hashlib
import json

import pytest

from scripts.render_observatory_example import OUTPUT
from scripts.render_observatory_example import expected_html

from ab_harness.lifecycle import LifecycleLedger
from ab_harness.lifecycle import TaskStartedFact
from ab_harness.lifecycle import TraceEvent
from ab_harness.observatory import ObservatoryDataLabel
from ab_harness.observatory import ObservatoryTraceStatus
from ab_harness.observatory import project_observatory
from ab_harness.observatory import render_observatory
from ab_harness.operation_edges import OperationEdge


def _event(
    sequence: int,
    event_type: str,
    *,
    trace_id: str,
    task_id: str = "task:observatory:001",
    environment_run_id: str = "environment-run:observatory:001",
    parent_event_id: str | None = None,
    data: dict[str, object] | None = None,
    operation_id: str | None = None,
) -> TraceEvent:
    data_json = json.dumps(
        data or {"event_type": event_type},
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    identity = {
        "schema_version": "uah.trace_event/v1",
        "sequence": sequence,
        "commit_id": "commit:observatory:%03d" % sequence,
        "commit_index": 1,
        "commit_size": 1,
        "recorded_at": "2026-10-01T09:00:%02dZ" % sequence,
        "event_type": event_type,
        "environment_run_id": environment_run_id,
        "task_id": task_id,
        "trace_id": trace_id,
        "operation_id": operation_id,
        "parent_event_id": parent_event_id,
        "artifact_refs": ("artifact:observatory:%03d" % sequence,),
        "data_json": data_json,
    }
    encoded = json.dumps(
        identity,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return TraceEvent(
        event_id="trace-event:sha256:%s" % hashlib.sha256(encoded).hexdigest(),
        **identity,
    )


def test_projection_uses_only_terminal_facts_for_trace_status():
    accepted_start = _event(1, "task_started", trace_id="trace:accepted")
    accepted = _event(
        4,
        "terminal_task_accepted",
        trace_id="trace:accepted",
        parent_event_id=accepted_start.event_id,
    )
    rejected_operation = _event(
        2,
        "semantic_admission_rejected",
        trace_id="trace:recoverable-rejection",
        data={"reason_code": "role_not_allowed"},
    )
    open_event = _event(3, "task_compiled", trace_id="trace:open")
    rejected_trace = _event(
        5,
        "terminal_task_rejected",
        trace_id="trace:rejected",
        data={"status": "rejected"},
    )

    projection = project_observatory(
        (
            accepted,
            open_event,
            rejected_operation,
            accepted_start,
            rejected_trace,
        ),
        data_label=ObservatoryDataLabel.SYNTHETIC,
    )

    assert [trace.trace_id for trace in projection.traces] == [
        "trace:accepted",
        "trace:recoverable-rejection",
        "trace:open",
        "trace:rejected",
    ]
    assert [trace.trace_id for trace in projection.accepted_traces] == [
        "trace:accepted"
    ]
    assert [trace.trace_id for trace in projection.rejected_traces] == [
        "trace:rejected"
    ]
    assert projection.trace("trace:open").status is ObservatoryTraceStatus.OPEN
    recoverable = projection.trace("trace:recoverable-rejection")
    assert recoverable.status is ObservatoryTraceStatus.OPEN
    assert recoverable.failure_stage == "semantic_admission"
    assert projection.trace("trace:accepted").events == (
        accepted_start,
        accepted,
    )


@pytest.mark.parametrize(
    "label",
    [
        ObservatoryDataLabel.SYNTHETIC,
        ObservatoryDataLabel.CONCEPTUAL,
    ],
)
def test_projection_preserves_the_declared_data_label(label):
    projection = project_observatory(
        (_event(1, "task_started", trace_id="trace:label"),),
        data_label=label,
    )

    assert projection.data_label is label
    assert projection.traces[0].data_label is label


def test_recorded_label_requires_a_validated_lifecycle_ledger():
    with pytest.raises(ValueError, match="requires a validated ledger"):
        project_observatory(
            (_event(1, "task_started", trace_id="trace:not-ledger-validated"),),
            data_label=ObservatoryDataLabel.RECORDED,
        )


def test_projection_rejects_conflicting_trace_lineage():
    events = (
        _event(1, "task_started", trace_id="trace:mixed", task_id="task:one"),
        _event(2, "task_compiled", trace_id="trace:mixed", task_id="task:two"),
    )

    with pytest.raises(ValueError, match="mixes task or environment lineage"):
        project_observatory(events)


def test_execution_failure_is_visible_without_inventing_a_terminal_rejection():
    projection = project_observatory(
        (_event(1, "execution_failed", trace_id="trace:failed-operation"),)
    )

    trace = projection.trace("trace:failed-operation")
    assert trace.status is ObservatoryTraceStatus.OPEN
    assert trace.failure_stage == "execution"
    assert projection.rejected_traces == ()


@pytest.mark.parametrize(
    ("event_type", "data", "expected_stage"),
    [
        ("execution_cancelled", {}, "cancellation"),
        ("budget_exhausted", {}, "budget"),
        ("retry_not_retryable", {}, "retry"),
        ("retry_exhausted", {}, "retry"),
        ("task_timeout_recorded", {"outcome": "timed_out"}, "timeout"),
    ],
)
def test_runtime_control_failures_are_visible_without_becoming_terminal(
    event_type,
    data,
    expected_stage,
):
    projection = project_observatory(
        (_event(1, event_type, trace_id="trace:control", data=data),)
    )

    trace = projection.trace("trace:control")
    assert trace.status is ObservatoryTraceStatus.OPEN
    assert trace.failure_stage == expected_stage


def test_within_budget_timeout_check_is_not_a_failure_stage():
    projection = project_observatory(
        (
            _event(
                1,
                "task_timeout_recorded",
                trace_id="trace:within-time",
                data={"outcome": "within_budget"},
            ),
        )
    )

    assert projection.trace("trace:within-time").failure_stage is None


def test_static_html_escapes_title_and_raw_payload_and_embeds_inert_graph_json():
    attack = '<img src=x onerror="alert(1)"> </script><script>alert(2)</script>'
    event = _event(
        1,
        "semantic_admission_rejected",
        trace_id="trace:escape",
        data={"untrusted": attack},
    )

    document = render_observatory(
        (event,),
        title="<Unsafe Observatory>",
        data_label=ObservatoryDataLabel.SYNTHETIC,
    )

    assert "&lt;Unsafe Observatory&gt;" in document.html
    assert "&lt;img src=x onerror=" in document.html
    assert "&lt;/script&gt;" in document.html
    assert attack not in document.html
    assert '<script type="application/json" id="observatory-graph">' in document.html
    assert "\\u003c/script\\u003e" in document.html
    assert (
        document.projection.trace("trace:escape").status is ObservatoryTraceStatus.OPEN
    )
    assert not hasattr(document, "write")


def test_observatory_consumes_events_from_the_lifecycle_ledger():
    ledger = LifecycleLedger(clock=lambda: "2026-10-01T09:00:00Z")
    ledger.record(
        TaskStartedFact(
            environment_run_id="environment-run:observatory:ledger",
            task_id="task:observatory:ledger",
            trace_id="trace:observatory:ledger",
            environment_ingress_id="ingress:observatory:ledger",
            ingress_artifact_id="environment-ingress:sha256:observatory-ledger",
            decision_id="task-ingress-decision:sha256:observatory-ledger",
            domain_contract_pack_revision="sha256:observatory-domain-pack",
        )
    )

    document = render_observatory(ledger)

    assert document.projection.trace_ids == ("trace:observatory:ledger",)
    assert document.projection.data_label is ObservatoryDataLabel.RECORDED
    assert "task_started" in document.html
    assert "task:observatory:ledger" in document.html


def test_observatory_renders_explicit_operation_edges_without_inference():
    edge = OperationEdge.issue(
        environment_run_id="environment-run:observatory:graph",
        task_id="task:observatory:graph",
        trace_id="trace:observatory:graph",
        source_operation_id="operation:parent",
        target_operation_id="operation:child",
        relation="decomposes_to",
        source_frame_id="nao_runtime",
        target_frame_id="nao_runtime",
    )
    start = _event(
        1,
        "task_started",
        trace_id=edge.trace_id,
        task_id=edge.task_id,
        environment_run_id=edge.environment_run_id,
    )
    recorded_edge = _event(
        2,
        "operation_edge_recorded",
        trace_id=edge.trace_id,
        task_id=edge.task_id,
        environment_run_id=edge.environment_run_id,
        parent_event_id=start.event_id,
        operation_id=edge.source_operation_id,
        data=edge.to_dict(),
    )

    document = render_observatory((start, recorded_edge))
    graph = json.loads(document.graph_json)

    assert "Operation graph" in document.html
    assert "decomposes_to" in document.html
    assert any(node["kind"] == "operation" for node in graph["nodes"])
    assert any(item["relation"] == "decomposes_to" for item in graph["edges"])
    plain_graph = json.loads(render_observatory((start,)).graph_json)
    assert not any(
        item["relation"] == "decomposes_to" for item in plain_graph["edges"]
    )


def test_committed_o1_example_matches_recorded_nao_canary():
    rendered = expected_html()

    assert OUTPUT.read_text(encoding="utf-8") == rendered
    assert "Label: <strong>recorded</strong>" in rendered
    assert "Accepted: 1 · Rejected: 1 · Open: 1" in rendered
    assert "semantic_admission" in rendered
    assert "task_acceptance" in rendered
