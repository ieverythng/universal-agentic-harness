import hashlib
import json

import pytest

from scripts.render_observatory_example import OUTPUT
from scripts.render_observatory_example import expected_html

from ab_harness.lifecycle import LifecycleLedger
from ab_harness.lifecycle import TraceEvent
from ab_harness.observatory import ObservatoryDataLabel
from ab_harness.observatory import ObservatoryTraceStatus
from ab_harness.observatory import project_observatory
from ab_harness.observatory import render_observatory
from ab_harness.operation_edges import OperationEdge
from ab_harness.agent_identity import AgentRunRegistry
from tests.test_agent_identity import _environment_attestation
from tests.test_agent_identity import _run_registries


def test_explicit_task_invocation_is_visible_in_actor_and_task_views(tmp_path):
    from ab_harness.model_invocation import ModelInvocationAuthority
    from tests.test_model_invocation import _invocation_fixture, _RecordedProvider

    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    ModelInvocationAuthority(
        ledger, _RecordedProvider(ledger), clock=lambda: "2026-10-04T10:00:02Z"
    ).invoke(lease, prompt, invocation_id="invocation:o1")
    projection = project_observatory(
        ledger.events(), data_label=ObservatoryDataLabel.SYNTHETIC
    )
    actor = projection.agent_run(lease.agent_run_id)
    invocation_events = tuple(
        event
        for event in actor.events
        if event.event_type.startswith("model_invocation_")
    )
    assert tuple(event.event_type for event in invocation_events) == (
        "model_invocation_started",
        "model_invocation_completed",
    )
    assert all(
        event.trace_id == prompt.trace_id and event.task_id == prompt.task_id
        for event in invocation_events
    )
    assert all(event in projection.traces[0].events for event in invocation_events)
    rendered = render_observatory(
        ledger,
        title="Synthetic H1 invocation",
        data_label=ObservatoryDataLabel.SYNTHETIC,
    )
    assert lease.agent_run_id in rendered.html
    assert all(event.event_id in rendered.html for event in invocation_events)
    graph = json.loads(rendered.graph_json)
    invocation_ids = {event.event_id for event in invocation_events}
    assert all(
        node["agent_run_id"] == lease.agent_run_id and node["event_scope"] == "task"
        for node in graph["nodes"]
        if node["id"] in invocation_ids
    )


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


def _attached_actor_ledger(path, *, environment_run_id="environment-run:synthetic:001"):
    _, handles, profiles, environments, _ = _run_registries()
    attestation = _environment_attestation(
        environment_run_id, "environment-profile:synthetic:v1"
    )
    environments.register(attestation)
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-04T10:00:00Z")
    runs = AgentRunRegistry(handles, environments, profiles, ledger=ledger)
    attached = runs.attach(
        agent_run_id="agent-run:synthetic:001",
        environment_run_id=attestation.environment_run_id,
        agent_handle_id="handle:synthetic.worker.primary",
    )
    return ledger, attached


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


def test_projection_indexes_tasks_and_traces_within_their_environment_run():
    first_trace = _event(
        1,
        "task_started",
        trace_id="trace:first",
        task_id="task:shared",
        environment_run_id="environment-run:first",
    )
    second_trace = _event(
        2,
        "task_started",
        trace_id="trace:second",
        task_id="task:shared",
        environment_run_id="environment-run:second",
    )
    continuation = _event(
        3,
        "task_compiled",
        trace_id="trace:continuation",
        task_id="task:shared",
        environment_run_id="environment-run:first",
    )
    other_task = _event(
        4,
        "task_started",
        trace_id="trace:other",
        task_id="task:other",
        environment_run_id="environment-run:first",
    )

    projection = project_observatory(
        (other_task, continuation, second_trace, first_trace)
    )

    assert projection.environment_run_ids == (
        "environment-run:first",
        "environment-run:second",
    )
    first_run = projection.environment_run("environment-run:first")
    assert first_run.task_ids == ("task:shared", "task:other")
    assert first_run.task("task:shared").trace_ids == (
        "trace:first",
        "trace:continuation",
    )
    assert projection.environment_run("environment-run:second").task(
        "task:shared"
    ).trace_ids == ("trace:second",)
    assert first_run.task("task:shared").traces[0] is projection.trace("trace:first")
    with pytest.raises(KeyError):
        projection.environment_run("environment-run:missing")
    with pytest.raises(KeyError):
        projection.environment_run("environment-run:second").task("task:other")


def test_projection_keeps_agent_attachment_without_inventing_a_task_or_trace(tmp_path):
    path = tmp_path / "actor.jsonl"
    ledger, attached = _attached_actor_ledger(path)

    projection = project_observatory(LifecycleLedger(path))

    assert projection.trace_ids == ()
    environment = projection.environment_run(attached.environment_run_id)
    assert environment.task_ids == ()
    assert environment.agent_run_ids == (attached.agent_run_id,)
    actor = environment.agent_run(attached.agent_run_id)
    assert actor.events == ledger.events()
    assert projection.agent_run(attached.agent_run_id) is actor
    assert projection.events == ledger.events()
    with pytest.raises(KeyError):
        environment.agent_run("agent-run:missing")


def test_actor_rendering_retains_scoped_facts_in_cards_and_graph(tmp_path):
    ledger, attached = _attached_actor_ledger(tmp_path / "actor.jsonl")

    document = render_observatory(ledger)
    graph = json.loads(document.graph_json)

    assert 'class="agent-run"' in document.html
    assert "Agent run <code>%s</code>" % attached.agent_run_id in document.html
    assert "agent_run_attached" in document.html
    assert 'href="#actor-%s"' % ledger.events()[0].event_id in document.html
    assert graph["nodes"][0]["event_scope"] == "agent"
    assert graph["nodes"][0]["agent_run_id"] == attached.agent_run_id
    assert graph["nodes"][0]["task_id"] is None
    assert graph["nodes"][0]["trace_id"] is None
    assert "trace-None" not in document.html


def test_actor_lifecycle_events_are_exposed_in_static_search_and_event_filters(
    tmp_path,
):
    ledger, _ = _attached_actor_ledger(tmp_path / "actor.jsonl")

    rendered = render_observatory(ledger).html

    assert '<option value="agent_run_attached">agent_run_attached</option>' in rendered
    assert 'class="agent-run"' in rendered
    assert 'data-event-types="agent_run_attached"' in rendered
    assert "document.querySelectorAll('.trace,.agent-run')" in rendered


def test_projection_rejects_agent_run_identity_mixed_across_environment_activations(
    tmp_path,
):
    first, _ = _attached_actor_ledger(tmp_path / "first.jsonl")
    second, _ = _attached_actor_ledger(
        tmp_path / "second.jsonl", environment_run_id="environment-run:synthetic:002"
    )

    with pytest.raises(ValueError, match="agent run mixes environment lineage"):
        project_observatory(first.events() + second.events())


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


def test_static_html_navigates_recorded_environment_task_and_trace_hierarchy():
    first = _event(
        1,
        "task_started",
        trace_id="trace:first",
        task_id="task:shared",
        environment_run_id="environment-run:first",
    )
    second = _event(
        2,
        "task_started",
        trace_id="trace:second",
        task_id="task:shared",
        environment_run_id="environment-run:second",
    )

    rendered = render_observatory((first, second)).html

    assert '<nav aria-label="Environment run, task and trace index">' in rendered
    assert "Environment run <code>environment-run:first</code>" in rendered
    assert "Task <code>task:shared</code>" in rendered
    assert 'href="#trace-%s"' % first.event_id in rendered
    assert 'id="trace-%s"' % first.event_id in rendered
    assert 'href="#trace-%s"' % second.event_id in rendered
    assert rendered.count('class="environment-index"') == 2


def test_observatory_consumes_events_from_the_lifecycle_ledger():
    from test_two_stage_admission import _admission_fixture, _record_task_start

    ledger = LifecycleLedger(clock=lambda: "2026-10-01T09:00:00Z")
    compiled, _, _ = _admission_fixture()
    _record_task_start(ledger, compiled)

    document = render_observatory(ledger)

    assert document.projection.trace_ids == (compiled.trace_id,)
    assert document.projection.data_label is ObservatoryDataLabel.RECORDED
    assert "task_started" in document.html
    assert compiled.task_id in document.html


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
    assert not any(item["relation"] == "decomposes_to" for item in plain_graph["edges"])


def test_committed_o1_example_matches_recorded_nao_canary():
    rendered = expected_html()

    assert OUTPUT.read_text(encoding="utf-8") == rendered
    assert "Label: <strong>recorded</strong>" in rendered
    assert "Accepted: 1 · Rejected: 1 · Open: 1" in rendered
    assert "semantic_admission" in rendered
    assert "task_acceptance" in rendered
