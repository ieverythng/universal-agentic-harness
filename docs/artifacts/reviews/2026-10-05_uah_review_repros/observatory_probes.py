import dataclasses
import hashlib
import inspect
import json
import tempfile
from pathlib import Path

from ab_harness import LifecycleLedger, TraceEvent
from ab_harness.observatory import render_observatory


def show(label, call):
    try:
        value = call()
        print(label, repr(value))
    except Exception as error:
        print(label, type(error).__name__, str(error))


def event(
    kind,
    *,
    sequence=1,
    parent=None,
    data=None,
    schema="uah.trace_event/v1",
    scope="task",
    actor=None,
    task="task-independent",
    trace="trace-independent",
):
    fields = dict(
        sequence=sequence,
        commit_id="lifecycle-commit:sha256:" + str(sequence) * 64,
        commit_index=1,
        commit_size=1,
        recorded_at="2026-10-05T10:00:00+00:00",
        event_type=kind,
        environment_run_id="environment-independent",
        task_id=task,
        trace_id=trace,
        operation_id=None,
        parent_event_id=parent,
        artifact_refs=("artifact:independent",),
        data_json=json.dumps(data or {}, sort_keys=True, separators=(",", ":")),
        schema_version=schema,
        event_scope=scope,
        agent_run_id=actor,
    )
    payload = dict(fields)
    if schema == "uah.trace_event/v1":
        payload.pop("event_scope")
        payload.pop("agent_run_id")
    digest = hashlib.sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()
    return TraceEvent(event_id="trace-event:sha256:" + digest, **fields)


show("TraceEvent.from_dict", lambda: str(inspect.signature(TraceEvent.from_dict)))
show(
    "ObservatoryDocument fields",
    lambda: tuple(field.name for field in dataclasses.fields(render_observatory(()))),
)
for source_name, source in (
    ("empty iterable", ()),
    ("empty ledger", LifecycleLedger()),
):
    for label in (None, "recorded", "synthetic", "conceptual", "measured", "reviewed"):
        show(
            f"{source_name} label={label}",
            lambda s=source, selected_label=label: tuple(
                (
                    field.name,
                    getattr(
                        render_observatory(s, data_label=selected_label), field.name
                    ),
                )
                for field in dataclasses.fields(
                    render_observatory(s, data_label=selected_label)
                )
                if field.name not in ("html", "graph_json")
            ),
        )

accepted = event("terminal_task_accepted", data={"status": "accepted"})
rejected = event(
    "terminal_task_rejected",
    sequence=2,
    parent=accepted.event_id,
    data={"status": "rejected"},
)
show(
    "terminal only hash round-trip",
    lambda: TraceEvent.from_dict(accepted.to_dict()) == accepted,
)
for label in ("measured", "reviewed"):
    show(
        "terminal only label=" + label,
        lambda selected_label=label: (
            render_observatory(
                (accepted,), data_label=selected_label
            ).projection.data_label.value,
            render_observatory((accepted,), data_label=selected_label)
            .projection.traces[0]
            .status.value,
            json.loads(
                render_observatory((accepted,), data_label=selected_label).graph_json
            )["data_label"],
        ),
    )

for name, source in (
    ("terminal only", (accepted,)),
    ("conflicting terminal", (accepted, rejected)),
):
    show(
        name + " iterable projection",
        lambda s=source: render_observatory(s).projection.traces,
    )
    with tempfile.TemporaryDirectory(prefix="uah-o1-grammar-") as directory:
        path = Path(directory) / "events.jsonl"
        path.write_text(
            "".join(
                json.dumps(item.to_dict(), sort_keys=True, separators=(",", ":")) + "\n"
                for item in source
            )
        )
        show(name + " ledger reload", lambda p=path: len(LifecycleLedger(p).events))

actor = event(
    "agent_run_attached",
    schema="uah.trace_event/v2",
    scope="agent",
    actor="actor-independent",
    task=None,
    trace=None,
)
show(
    "actor without task",
    lambda: (
        render_observatory((actor,)).projection.environment_run_ids,
        render_observatory((actor,)).projection.traces,
    ),
)
show(
    "HTML title escaped",
    lambda: (
        "<script>alert(1)</script>"
        in render_observatory((), title="<script>alert(1)</script>").html
    ),
)
