"""Independent public-boundary probes for the bounded O1 conformance fix."""

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import tempfile

from ab_harness.lifecycle import LifecycleLedger, TaskStartedFact, TraceEvent
from ab_harness.observatory import project_observatory, render_observatory
from tests.test_observatory import _event


def altered(event, **changes):
    for field, value in changes.items():
        object.__setattr__(event, field, value)
    return event


def valid(sequence=1, *, version=1, scope="task", actor=None):
    values = asdict(_event(sequence, "task_started", trace_id="trace:independent"))
    values.pop("event_id")
    values.update(schema_version=f"uah.trace_event/v{version}")
    values.update(event_scope=scope, agent_run_id=actor)
    if scope == "agent":
        values.update(task_id=None, trace_id=None, operation_id=None,
                      event_type="agent_run_attached")
    identity = dict(values)
    if version == 1:
        identity.pop("event_scope")
        identity.pop("agent_run_id")
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":"),
                         allow_nan=False).encode()
    return TraceEvent(event_id="trace-event:sha256:" + hashlib.sha256(encoded).hexdigest(),
                      **values)


def rehash(event):
    values = asdict(event)
    values.pop("event_id")
    if event.schema_version != "uah.trace_event/v2":
        values.pop("event_scope")
        values.pop("agent_run_id")
    encoded = json.dumps(values, sort_keys=True, separators=(",", ":"),
                         allow_nan=False).encode()
    return altered(event, event_id="trace-event:sha256:" + hashlib.sha256(encoded).hexdigest())


cases = {
    "empty": lambda: [],
    "v1": lambda: [valid()],
    "v2-actor": lambda: [valid(version=2, scope="agent", actor="actor:one")],
    "v2-task": lambda: [valid(version=2, actor="actor:one")],
    "mixed-forward": lambda: [valid(), valid(2, version=2, scope="agent", actor="actor:one"),
                              valid(3, version=2, actor="actor:one")],
    "mixed-reverse": lambda: [valid(3, version=2, actor="actor:one"),
                              valid(2, version=2, scope="agent", actor="actor:one"), valid()],
    "v1-actor-only": lambda: [altered(valid(), agent_run_id="actor:forged")],
    "v1-scope-only": lambda: [altered(valid(), event_scope="agent")],
    "v1-actor-scope": lambda: [altered(valid(), agent_run_id="actor:forged", event_scope="agent")],
    "foreign-member": lambda: [valid(), object()],
    "duplicate": lambda: [valid(), valid()],
    "unknown-schema-stale": lambda: [altered(valid(), schema_version="uah.trace_event/v99")],
    "unknown-schema-rehashed": lambda: [rehash(altered(valid(), schema_version="uah.trace_event/v99"))],
    "noncanonical-json-rehashed": lambda: [rehash(altered(valid(), data_json='{"b": 2, "a": 1}'))],
    "array-json-rehashed": lambda: [rehash(altered(valid(), data_json='[1]'))],
    "mutable-reference-list": lambda: [altered(valid(), artifact_refs=["artifact:observatory:001"])],
    "v2-missing-actor-rehashed": lambda: [rehash(altered(valid(version=2, actor="actor:one"), agent_run_id=None))],
    "v2-invalid-scope-rehashed": lambda: [rehash(altered(valid(version=2, actor="actor:one"), event_scope="elsewhere"))],
    "v2-agent-with-task-rehashed": lambda: [rehash(altered(valid(version=2, actor="actor:one"), event_scope="agent"))],
    "v2-task-missing-trace-rehashed": lambda: [rehash(altered(valid(version=2, actor="actor:one"), trace_id=None))],
}
for field, value in {
    "event_type": "terminal_task_accepted",
    "environment_run_id": "environment:changed",
    "task_id": "task:changed", "trace_id": "trace:changed", "sequence": 99,
    "recorded_at": "2028-02-29T23:59:59Z", "artifact_refs": ("artifact:changed",),
    "operation_id": "operation:changed", "parent_event_id": "event:changed",
    "commit_id": "commit:changed", "commit_index": 2, "commit_size": 2,
    "data_json": '{"unexpected":true}',
}.items():
    cases["stale-" + field] = lambda f=field, v=value: [altered(valid(), **{f: v})]

rows = []
for name, make in cases.items():
    for form in ("tuple", "generator"):
        for api in (project_observatory, render_observatory):
            items = make()
            source = tuple(items) if form == "tuple" else (item for item in items)
            row = {"case": name, "form": form, "api": api.__name__}
            try:
                result = api(source)
                projected = result if api is project_observatory else result.projection
                row.update(outcome="accepted", label=projected.data_label.value,
                           traces=list(projected.trace_ids),
                           actors=[actor.agent_run_id for actor in projected.agent_runs],
                           event_ids=[event.event_id for event in projected.events])
                if api is render_observatory:
                    row["graph_nodes"] = len(json.loads(result.graph_json)["nodes"])
            except Exception as exc:
                row.update(outcome="rejected", error=type(exc).__name__, message=str(exc))
            rows.append(row)

for api in (project_observatory, render_observatory):
    for label in ("synthetic", "conceptual"):
        result = api((_event(1, "terminal_task_accepted", trace_id="trace:incomplete"),),
                     data_label=label)
        projected = result if api is project_observatory else result.projection
        rows.append({"case": "incomplete-illustration", "api": api.__name__,
                     "label": projected.data_label.value, "status": projected.traces[0].status.value})

source = valid()
projected = project_observatory((source,))
document = render_observatory((source,))
altered(source, agent_run_id="actor:late", event_type="terminal_task_accepted",
        environment_run_id="environment:late")
rows.append({"case": "post-projection-input-alias", "projection_detached":
             projected.events[0].agent_run_id is None and
             projected.events[0].event_type == "task_started" and
             projected.events[0].environment_run_id == "environment-run:observatory:001",
             "document_detached": document.projection.events[0].agent_run_id is None,
             "trace_event_same_owned_copy": projected.events[0] is projected.traces[0].events[0]})

with tempfile.TemporaryDirectory() as temporary:
    path = Path(temporary) / "ledger.jsonl"
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-08T15:30:00Z")
    ledger.record(TaskStartedFact(environment_run_id="environment:one", task_id="task:one",
                                 trace_id="trace:one", environment_ingress_id="ingress:one",
                                 ingress_artifact_id="artifact:one", decision_id="decision:one",
                                 domain_contract_pack_revision="pack:one"))
    before = path.read_bytes()
    events = ledger.events()
    doc = render_observatory(ledger)
    rows.append({"case": "ledger-read-only", "unchanged": path.read_bytes() == before,
                 "events_unchanged": ledger.events() == events,
                 "label": doc.projection.data_label.value})

print(json.dumps(rows, indent=2))
