"""Read-only lifecycle projections and static rendering for Observatory O1."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from dataclasses import dataclass
from enum import Enum
import html
import json
from typing import Iterable

from ab_harness.lifecycle import LifecycleLedger
from ab_harness.lifecycle import TraceEvent
from ab_harness.operation_edges import OperationEdge


OBSERVATORY_PROJECTION_SCHEMA = "uah.observatory_projection/v1"
OBSERVATORY_GRAPH_SCHEMA = "uah.observatory_graph/v1"


class ObservatoryDataLabel(str, Enum):
    """Provenance label applied to every value in one projection."""

    CONCEPTUAL = "conceptual"
    SYNTHETIC = "synthetic"
    RECORDED = "recorded"
    MEASURED = "measured"
    REVIEWED = "reviewed"


class ObservatoryTraceStatus(str, Enum):
    """Status derived only from explicit lifecycle facts."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    OPEN = "open"


@dataclass(frozen=True)
class ObservatoryTraceProjection:
    """One immutable trace view over ordered ledger events."""

    trace_id: str
    environment_run_id: str
    task_id: str
    status: ObservatoryTraceStatus
    data_label: ObservatoryDataLabel
    failure_stages: tuple[str, ...]
    events: tuple[TraceEvent, ...]

    @property
    def failure_stage(self) -> str | None:
        return self.failure_stages[-1] if self.failure_stages else None


@dataclass(frozen=True)
class ObservatoryTaskProjection:
    """Recorded traces for one task inside an environment activation."""

    environment_run_id: str
    task_id: str
    traces: tuple[ObservatoryTraceProjection, ...]

    @property
    def trace_ids(self) -> tuple[str, ...]:
        return tuple(trace.trace_id for trace in self.traces)


@dataclass(frozen=True)
class ObservatoryAgentRunProjection:
    """Ordered actor facts without inferred task or trace membership."""

    environment_run_id: str
    agent_run_id: str
    events: tuple[TraceEvent, ...]


@dataclass(frozen=True)
class ObservatoryEnvironmentRunProjection:
    """Recorded task hierarchy for one environment activation."""

    environment_run_id: str
    tasks: tuple[ObservatoryTaskProjection, ...]
    agent_runs: tuple[ObservatoryAgentRunProjection, ...] = ()

    @property
    def agent_run_ids(self) -> tuple[str, ...]:
        return tuple(actor.agent_run_id for actor in self.agent_runs)

    def agent_run(self, agent_run_id: str) -> ObservatoryAgentRunProjection:
        for actor in self.agent_runs:
            if actor.agent_run_id == agent_run_id:
                return actor
        raise KeyError(agent_run_id)

    @property
    def task_ids(self) -> tuple[str, ...]:
        return tuple(task.task_id for task in self.tasks)

    def task(self, task_id: str) -> ObservatoryTaskProjection:
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        raise KeyError(task_id)


@dataclass(frozen=True)
class ObservatoryProjection:
    """Read-only O1 projection over one immutable event collection."""

    traces: tuple[ObservatoryTraceProjection, ...]
    data_label: ObservatoryDataLabel
    schema_version: str = OBSERVATORY_PROJECTION_SCHEMA
    events: tuple[TraceEvent, ...] = ()
    agent_runs: tuple[ObservatoryAgentRunProjection, ...] = ()

    @property
    def environment_runs(self) -> tuple[ObservatoryEnvironmentRunProjection, ...]:
        grouped: dict[str, dict[str, list[ObservatoryTraceProjection]]] = {
            event.environment_run_id: {} for event in self.events
        }
        for trace in self.traces:
            tasks = grouped.setdefault(trace.environment_run_id, {})
            tasks.setdefault(trace.task_id, []).append(trace)
        return tuple(
            ObservatoryEnvironmentRunProjection(
                environment_run_id=run_id,
                tasks=tuple(
                    ObservatoryTaskProjection(run_id, task_id, tuple(traces))
                    for task_id, traces in tasks.items()
                ),
                agent_runs=tuple(
                    actor
                    for actor in self.agent_runs
                    if actor.environment_run_id == run_id
                ),
            )
            for run_id, tasks in grouped.items()
        )

    @property
    def environment_run_ids(self) -> tuple[str, ...]:
        return tuple(run.environment_run_id for run in self.environment_runs)

    def environment_run(
        self, environment_run_id: str
    ) -> ObservatoryEnvironmentRunProjection:
        for run in self.environment_runs:
            if run.environment_run_id == environment_run_id:
                return run
        raise KeyError(environment_run_id)

    def agent_run(self, agent_run_id: str) -> ObservatoryAgentRunProjection:
        for actor in self.agent_runs:
            if actor.agent_run_id == agent_run_id:
                return actor
        raise KeyError(agent_run_id)

    @property
    def trace_ids(self) -> tuple[str, ...]:
        return tuple(trace.trace_id for trace in self.traces)

    @property
    def accepted_traces(self) -> tuple[ObservatoryTraceProjection, ...]:
        return tuple(
            trace
            for trace in self.traces
            if trace.status is ObservatoryTraceStatus.ACCEPTED
        )

    @property
    def rejected_traces(self) -> tuple[ObservatoryTraceProjection, ...]:
        return tuple(
            trace
            for trace in self.traces
            if trace.status is ObservatoryTraceStatus.REJECTED
        )

    def trace(self, trace_id: str) -> ObservatoryTraceProjection:
        for trace in self.traces:
            if trace.trace_id == trace_id:
                return trace
        raise KeyError(trace_id)


@dataclass(frozen=True)
class ObservatoryDocument:
    """Self-contained static document backed by its exact projection."""

    html: str
    graph_json: str
    projection: ObservatoryProjection


_ACCEPTED_EVENTS = {
    "terminal_task_accepted",
    "terminal_task_accepted_with_deficit",
}

_FAILURE_STAGES = {
    "registration_preflight_failed": "registration_preflight",
    "environment_run_failed": "environment_run",
    "environment_ingress_rejected": "environment_ingress",
    "agent_run_startup_failed": "agent_run_startup",
    "model_lease_rejected": "model_allocation",
    "startup_preflight_failed": "startup_preflight",
    "model_invocation_failed": "model_invocation",
    "proposal_rejected": "proposal_normalization",
    "semantic_admission_rejected": "semantic_admission",
    "domain_admission_rejected": "domain_admission",
    "execution_failed": "execution",
    "execution_cancelled": "cancellation",
    "budget_exhausted": "budget",
    "evidence_rejected": "evidence",
    "effect_obligation_failed": "effect_obligation",
    "terminal_task_rejected": "task_acceptance",
    "retry_not_retryable": "retry",
    "retry_exhausted": "retry",
}

_REJECTED_EVENTS = {"terminal_task_rejected"}


def project_observatory(
    source: LifecycleLedger | Iterable[TraceEvent],
    *,
    data_label: ObservatoryDataLabel | str | None = None,
) -> ObservatoryProjection:
    """Project immutable ledger events without reconstructing missing facts."""

    if isinstance(source, LifecycleLedger):
        events = source.events()
        label = ObservatoryDataLabel(data_label or ObservatoryDataLabel.RECORDED)
    else:
        events = tuple(source)
        label = ObservatoryDataLabel(data_label or ObservatoryDataLabel.SYNTHETIC)
        if label is ObservatoryDataLabel.RECORDED:
            raise ValueError("recorded Observatory data requires a validated ledger")
    if label in {ObservatoryDataLabel.MEASURED, ObservatoryDataLabel.REVIEWED}:
        raise ValueError("Observatory O1 does not support measured or reviewed data labels")
    if any(not isinstance(event, TraceEvent) for event in events):
        raise TypeError("Observatory accepts TraceEvent values only")
    events = tuple(TraceEvent(**asdict(event)) for event in events)
    event_ids = [event.event_id for event in events]
    if len(event_ids) != len(set(event_ids)):
        raise ValueError("Observatory event identities must be unique")

    ordered_events = tuple(sorted(events, key=lambda event: event.sequence))
    grouped: dict[str, list[TraceEvent]] = {}
    actors: dict[str, list[TraceEvent]] = {}
    for event in ordered_events:
        if event.agent_run_id is not None:
            actors.setdefault(event.agent_run_id, []).append(event)
        if event.event_scope == "task":
            grouped.setdefault(event.trace_id, []).append(event)

    traces = tuple(
        _project_trace(tuple(trace_events), label) for trace_events in grouped.values()
    )
    if any(
        event.environment_run_id != actor_events[0].environment_run_id
        for actor_events in actors.values()
        for event in actor_events
    ):
        raise ValueError("agent run mixes environment lineage")
    return ObservatoryProjection(
        traces=traces,
        data_label=label,
        events=ordered_events,
        agent_runs=tuple(
            ObservatoryAgentRunProjection(
                environment_run_id=actor_events[0].environment_run_id,
                agent_run_id=agent_run_id,
                events=tuple(actor_events),
            )
            for agent_run_id, actor_events in actors.items()
        ),
    )


def render_observatory(
    source: LifecycleLedger | Iterable[TraceEvent],
    *,
    title: str = "UAH Observatory O1",
    data_label: ObservatoryDataLabel | str | None = None,
) -> ObservatoryDocument:
    """Return a static read-only report; persistence remains caller-owned."""

    projection = project_observatory(source, data_label=data_label)
    graph_json = _safe_json_for_html(_graph_payload(projection))
    html_payload = _render_html(projection, graph_json=graph_json, title=title)
    return ObservatoryDocument(
        html=html_payload,
        graph_json=graph_json,
        projection=projection,
    )


def _project_trace(
    events: tuple[TraceEvent, ...],
    data_label: ObservatoryDataLabel,
) -> ObservatoryTraceProjection:
    first = events[0]
    if any(
        event.task_id != first.task_id
        or event.environment_run_id != first.environment_run_id
        for event in events
    ):
        raise ValueError("trace mixes task or environment lineage")

    decisive_events = [
        event
        for event in events
        if event.event_type in _ACCEPTED_EVENTS or event.event_type in _REJECTED_EVENTS
    ]
    if not decisive_events:
        status = ObservatoryTraceStatus.OPEN
    elif decisive_events[-1].event_type in _ACCEPTED_EVENTS:
        status = ObservatoryTraceStatus.ACCEPTED
    else:
        status = ObservatoryTraceStatus.REJECTED

    return ObservatoryTraceProjection(
        trace_id=first.trace_id,
        environment_run_id=first.environment_run_id,
        task_id=first.task_id,
        status=status,
        data_label=data_label,
        failure_stages=tuple(
            stage for event in events if (stage := _failure_stage(event)) is not None
        ),
        events=events,
    )


def _failure_stage(event: TraceEvent) -> str | None:
    if (
        event.event_type == "task_timeout_recorded"
        and event.data.get("outcome") == "timed_out"
    ):
        return "timeout"
    return _FAILURE_STAGES.get(event.event_type)


def _graph_payload(projection: ObservatoryProjection) -> dict[str, object]:
    events = projection.events
    event_ids = {event.event_id for event in events}
    operation_edges = tuple(
        OperationEdge.from_dict(event.data)
        for event in events
        if event.event_type == "operation_edge_recorded"
    )
    operation_keys = {
        (event.trace_id, event.operation_id)
        for event in events
        if event.operation_id is not None
    }
    operation_keys.update(
        (edge.trace_id, operation_id)
        for edge in operation_edges
        for operation_id in (edge.source_operation_id, edge.target_operation_id)
    )
    return {
        "schema_version": OBSERVATORY_GRAPH_SCHEMA,
        "data_label": projection.data_label.value,
        "nodes": [
            {
                "id": event.event_id,
                "kind": "lifecycle_event",
                "event_type": event.event_type,
                "environment_run_id": event.environment_run_id,
                "trace_id": event.trace_id,
                "task_id": event.task_id,
                "operation_id": event.operation_id,
                "sequence": event.sequence,
                "data": event.data,
                **(
                    {
                        "event_scope": event.event_scope,
                        "agent_run_id": event.agent_run_id,
                    }
                    if event.agent_run_id is not None
                    else {}
                ),
            }
            for event in events
        ]
        + [
            {
                "id": _operation_node_id(trace_id, operation_id),
                "kind": "operation",
                "trace_id": trace_id,
                "operation_id": operation_id,
            }
            for trace_id, operation_id in sorted(operation_keys)
        ],
        "edges": [
            {
                "source": event.parent_event_id,
                "target": event.event_id,
                "relation": "ledger_parent_event",
            }
            for event in events
            if event.parent_event_id in event_ids
        ]
        + [
            {
                "id": edge.edge_id,
                "source": _operation_node_id(edge.trace_id, edge.source_operation_id),
                "target": _operation_node_id(edge.trace_id, edge.target_operation_id),
                "relation": edge.relation,
                "source_frame_id": edge.source_frame_id,
                "target_frame_id": edge.target_frame_id,
                "artifact_contract_ref": edge.artifact_contract_ref,
            }
            for edge in operation_edges
        ],
    }


def _operation_node_id(trace_id: str, operation_id: str) -> str:
    return "operation-node:%s:%s" % (trace_id, operation_id)


def _render_html(
    projection: ObservatoryProjection,
    *,
    graph_json: str,
    title: str,
) -> str:
    event_types = sorted({event.event_type for event in projection.events})
    status_counts = Counter(trace.status.value for trace in projection.traces)
    trace_sections = "\n".join(_render_trace(trace) for trace in projection.traces)
    actor_sections = "\n".join(_render_actor(actor) for actor in projection.agent_runs)
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ --bg:#f4f7fb; --ink:#182536; --muted:#5d6d7e; --line:#cbd6e2;
      --panel:#fff; --accepted:#147d64; --rejected:#b33b45; --open:#75632c; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--ink);
      font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }}
    main {{ max-width:1180px; margin:0 auto; padding:28px 18px 56px; }}
    h1 {{ margin:0 0 8px; }}
    .summary {{ color:var(--muted); margin:0 0 18px; }}
    .controls {{ display:grid; grid-template-columns:2fr 1fr 1fr; gap:10px;
      padding:12px; border:1px solid var(--line); border-radius:12px;
      background:var(--panel); position:sticky; top:0; z-index:1; }}
    label {{ display:flex; flex-direction:column; gap:4px; font-size:.85rem; }}
    input,select {{ font:inherit; border:1px solid var(--line); border-radius:7px;
      padding:7px 9px; background:#fff; color:var(--ink); }}
    .trace,.agent-run {{ margin-top:16px; padding:14px; border:1px solid var(--line);
      border-radius:12px; background:var(--panel); }}
    .trace > header {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; }}
    .trace h2 {{ margin:0 auto 0 0; font-size:1.05rem; }}
    .badge {{ border-radius:999px; padding:3px 8px; color:#fff; font-size:.75rem; }}
    .accepted {{ background:var(--accepted); }} .rejected {{ background:var(--rejected); }}
    .open {{ background:var(--open); }}
    .event {{ border-top:1px solid var(--line); margin-top:12px; padding-top:12px; }}
    .event header {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; }}
    .event p {{ color:var(--muted); margin:6px 0; }}
    code {{ background:#e8eef5; border-radius:4px; padding:.1rem .25rem; }}
    pre {{ margin:8px 0 0; padding:10px; overflow:auto; border-radius:8px;
      background:#142033; color:#ecf3fb; }}
    details > summary {{ cursor:pointer; }} .hidden {{ display:none; }}
    .operation-graph {{ margin:12px 0; padding:10px; border-radius:8px;
      background:#edf3f8; }}
    .operation-edge {{ display:grid; grid-template-columns:1fr auto 1fr; gap:8px;
      align-items:center; padding:7px 0; border-top:1px solid var(--line); }}
    nav {{ margin:18px 0; padding:12px; border:1px solid var(--line);
      border-radius:12px; background:var(--panel); }}
    nav h2 {{ margin:0 0 10px; font-size:1.05rem; }}
    .environment-index + .environment-index {{ border-top:1px solid var(--line);
      margin-top:12px; padding-top:12px; }}
    nav ul {{ margin:8px 0; padding-left:24px; }}
    nav li {{ margin:6px 0; }} nav a {{ color:#235d91; }}
    .trace {{ scroll-margin-top:110px; }}
    @media (max-width:700px) {{ .controls {{ grid-template-columns:1fr; position:static; }} }}
  </style>
</head>
<body>
  <main>
    <h1>{title}</h1>
    <p class="summary">Label: <strong>{label}</strong> · Traces: {trace_count} ·
      Accepted: {accepted_count} · Rejected: {rejected_count} · Open: {open_count}</p>
    <section class="controls" aria-label="Trace filters">
      <label>Search<input id="query" type="search" placeholder="task, trace, event, payload"></label>
      <label>Status<select id="status"><option value="">All</option>
        <option value="accepted">Accepted</option><option value="rejected">Rejected</option>
        <option value="open">Open</option></select></label>
      <label>Event type<select id="event-type"><option value="">All</option>{event_options}</select></label>
    </section>
    {hierarchy_index}
    <section id="agent-runs">{actor_sections}</section>
    <section id="traces">{trace_sections}</section>
    <script type="application/json" id="observatory-graph">{graph_json}</script>
  </main>
  <script>
    (() => {{
      const traces = Array.from(document.querySelectorAll('.trace,.agent-run'));
      const query = document.getElementById('query');
      const status = document.getElementById('status');
      const eventType = document.getElementById('event-type');
      const apply = () => {{
        const q = query.value.trim().toLowerCase();
        for (const trace of traces) {{
          const matchesQuery = !q || trace.dataset.searchable.includes(q);
          const matchesStatus = !status.value || trace.dataset.status === status.value;
          const matchesType = !eventType.value || trace.dataset.eventTypes.split(' ').includes(eventType.value);
          trace.classList.toggle('hidden', !(matchesQuery && matchesStatus && matchesType));
        }}
      }};
      query.addEventListener('input', apply);
      status.addEventListener('change', apply);
      eventType.addEventListener('change', apply);
    }})();
  </script>
</body>
</html>
""".format(
        title=html.escape(title),
        label=html.escape(projection.data_label.value),
        trace_count=len(projection.traces),
        accepted_count=status_counts[ObservatoryTraceStatus.ACCEPTED.value],
        rejected_count=status_counts[ObservatoryTraceStatus.REJECTED.value],
        open_count=status_counts[ObservatoryTraceStatus.OPEN.value],
        event_options="".join(
            '<option value="{0}">{0}</option>'.format(html.escape(event_type))
            for event_type in event_types
        ),
        trace_sections=trace_sections,
        actor_sections=actor_sections,
        hierarchy_index=_render_hierarchy_index(projection),
        graph_json=graph_json,
    )


def _render_hierarchy_index(projection: ObservatoryProjection) -> str:
    runs = []
    for run in projection.environment_runs:
        tasks = []
        for task in run.tasks:
            traces = "".join(
                '<li><a href="#trace-{anchor}">{trace_id}</a> '
                '<span class="badge {status}">{status}</span></li>'.format(
                    anchor=html.escape(trace.events[0].event_id, quote=True),
                    trace_id=html.escape(trace.trace_id),
                    status=html.escape(trace.status.value),
                )
                for trace in task.traces
            )
            tasks.append(
                "<li>Task <code>{task_id}</code><ul>{traces}</ul></li>".format(
                    task_id=html.escape(task.task_id),
                    traces=traces,
                )
            )
        actors = "".join(
            '<li><a href="#actor-{anchor}">Agent run <code>{actor_id}</code></a></li>'.format(
                anchor=html.escape(actor.events[0].event_id, quote=True),
                actor_id=html.escape(actor.agent_run_id),
            )
            for actor in run.agent_runs
        )
        runs.append(
            '<section class="environment-index">Environment run '
            "<code>{run_id}</code><ul>{actors}{tasks}</ul></section>".format(
                run_id=html.escape(run.environment_run_id),
                tasks="".join(tasks),
                actors=actors,
            )
        )
    return (
        '<nav aria-label="Environment run, task and trace index">'
        "<h2>Environment runs</h2>%s</nav>" % "".join(runs)
    )


def _render_actor(actor: ObservatoryAgentRunProjection) -> str:
    raw_events = tuple(
        json.dumps(event.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)
        for event in actor.events
    )
    cards = "\n".join(
        _render_event(event, raw_payload)
        for event, raw_payload in zip(actor.events, raw_events, strict=True)
    )
    searchable = " ".join(
        (actor.agent_run_id, actor.environment_run_id, *raw_events)
    ).lower()
    event_types = " ".join(sorted({event.event_type for event in actor.events}))
    return (
        '<article class="agent-run" id="actor-{anchor}" '
        'data-event-types="{event_types}" data-searchable="{searchable}">'
        "<h2>Agent run <code>{actor_id}</code></h2>"
        "<p>Environment run <code>{run_id}</code></p>{cards}</article>"
    ).format(
        anchor=html.escape(actor.events[0].event_id, quote=True),
        actor_id=html.escape(actor.agent_run_id),
        run_id=html.escape(actor.environment_run_id),
        cards=cards,
        event_types=html.escape(event_types, quote=True),
        searchable=html.escape(searchable, quote=True),
    )


def _render_trace(trace: ObservatoryTraceProjection) -> str:
    raw_events = [
        json.dumps(event.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)
        for event in trace.events
    ]
    searchable = " ".join(
        [
            trace.trace_id,
            trace.task_id,
            trace.environment_run_id,
            *(event.event_type for event in trace.events),
            *raw_events,
        ]
    ).lower()
    event_cards = "\n".join(
        _render_event(event, raw_payload)
        for event, raw_payload in zip(trace.events, raw_events, strict=True)
    )
    event_types = " ".join(sorted({event.event_type for event in trace.events}))
    failure = (
        " · Failure stage: <code>%s</code>" % html.escape(trace.failure_stage)
        if trace.failure_stage
        else ""
    )
    operation_graph = _render_operation_graph(trace.events)
    return """<article class="trace" id="trace-{anchor}" data-status="{status}" data-event-types="{event_types}"
      data-searchable="{searchable}">
      <header><h2>{trace_id}</h2><span class="badge {status}">{status}</span>
        <span class="badge open">{label}</span></header>
      <p>Task <code>{task_id}</code> · Environment <code>{environment_run_id}</code>{failure}</p>
{operation_graph}
      {event_cards}
    </article>""".format(
        status=html.escape(trace.status.value),
        anchor=html.escape(trace.events[0].event_id, quote=True),
        event_types=html.escape(event_types),
        searchable=html.escape(searchable, quote=True),
        trace_id=html.escape(trace.trace_id),
        label=html.escape(trace.data_label.value),
        task_id=html.escape(trace.task_id),
        environment_run_id=html.escape(trace.environment_run_id),
        failure=failure,
        operation_graph=operation_graph,
        event_cards=event_cards,
    )


def _render_operation_graph(events: tuple[TraceEvent, ...]) -> str:
    edges = tuple(
        OperationEdge.from_dict(event.data)
        for event in events
        if event.event_type == "operation_edge_recorded"
    )
    if not edges:
        return ""
    rows = "".join(
        """<div class="operation-edge"><code>{source}</code>
          <strong>{relation}</strong><code>{target}</code></div>""".format(
            source=html.escape(edge.source_operation_id),
            relation=html.escape(edge.relation),
            target=html.escape(edge.target_operation_id),
        )
        for edge in edges
    )
    return (
        '<section class="operation-graph"><strong>Operation graph</strong>%s</section>'
        % rows
    )


def _render_event(event: TraceEvent, raw_payload: str) -> str:
    operation = (
        " · Operation <code>%s</code>" % html.escape(event.operation_id)
        if event.operation_id
        else ""
    )
    return """<section class="event">
      <header><strong>{event_type}</strong><code>#{sequence}</code></header>
      <p>Recorded {recorded_at}{operation}</p>
      <details><summary>Raw immutable event</summary><pre>{raw_payload}</pre></details>
    </section>""".format(
        event_type=html.escape(event.event_type),
        sequence=event.sequence,
        recorded_at=html.escape(event.recorded_at),
        operation=operation,
        raw_payload=html.escape(raw_payload),
    )


def _safe_json_for_html(payload: object) -> str:
    return (
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
