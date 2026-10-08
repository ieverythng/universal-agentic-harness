"""Independent O1 identity probes; run with an isolated tree on PYTHONPATH."""

import hashlib
import json
import tempfile
from pathlib import Path

import ab_harness.observatory as observatory
from ab_harness.lifecycle import LifecycleLedger, TaskStartedFact
from ab_harness.observatory import project_observatory, render_observatory
from scripts.render_agent_runtime_example import example_ledger


def start_ledger(path=None, suffix="one"):
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-08T15:30:00Z")
    ledger.record(
        TaskStartedFact(
            environment_run_id="environment:review",
            task_id="task:" + suffix,
            trace_id="trace:" + suffix,
            environment_ingress_id="ingress:" + suffix,
            ingress_artifact_id="artifact:" + suffix,
            decision_id="decision:" + suffix,
            domain_contract_pack_revision="pack:review",
        )
    )
    return ledger


rows = []


def check(name, expected, operation):
    try:
        actual = operation()
    except Exception as error:
        actual = type(error).__name__ + ": " + str(error)
    rows.append({"case": name, "expected": expected, "actual": actual})


identity_error = "ValueError: trace event identity does not match content"
raw_kind = {"task": lambda: start_ledger().events()[0]}
actor_ledger = example_ledger()
for scope in ("agent", "task"):
    event = next(
        event
        for event in actor_ledger.events()
        if event.schema_version == "uah.trace_event/v2" and event.event_scope == scope
    )
    raw_kind["v2_" + scope] = lambda event=event: type(event).from_dict(event.to_dict())

mutations = {
    "event_type": "terminal_task_accepted",
    "sequence": -999,
    "environment_run_id": "environment:foreign",
    "data_json": '{"forged":true}',
    "recorded_at": "2028-02-29T23:59:59+01:00",
    "artifact_refs": ("artifact:foreign",),
    "parent_event_id": "event:foreign",
    "commit_id": "commit:foreign",
}
for kind, factory in raw_kind.items():
    for field, value in mutations.items():
        for form in ("tuple", "generator"):
            for consumer in (project_observatory, render_observatory):
                def operation(factory=factory, field=field, value=value,
                              form=form, consumer=consumer):
                    event = factory()
                    object.__setattr__(event, field, value)
                    source = (event,) if form == "tuple" else (item for item in (event,))
                    consumer(source)
                    return "accepted"

                check(f"{kind}/{field}/{form}/{consumer.__name__}", identity_error, operation)

for field, value in (("agent_run_id", "agent:forged"), ("event_scope", "agent")):
    for form in ("tuple", "generator"):
        for consumer in (project_observatory, render_observatory):
            def operation(field=field, value=value, form=form, consumer=consumer):
                ledger = start_ledger()
                event = ledger.events()[0]
                object.__setattr__(event, field, value)
                source = (event,) if form == "tuple" else (item for item in (event,))
                result = consumer(source)
                projection = result.projection if hasattr(result, "projection") else result
                return {
                    "accepted": True,
                    "schema": event.schema_version,
                    "traces": projection.trace_ids,
                    "actors": tuple(actor.agent_run_id for actor in projection.agent_runs),
                    "ledger_actors": tuple(actor.agent_run_id for actor in project_observatory(ledger).agent_runs),
                    "ledger_traces": project_observatory(ledger).trace_ids,
                    "serialization_has_actor": "agent_run_id" in event.to_dict(),
                    "graph_actor": json.loads(result.graph_json)["nodes"][0].get("agent_run_id")
                    if hasattr(result, "graph_json") else None,
                }

            check(f"v1-fixed-field/{field}/{form}/{consumer.__name__}", "reject incompatible v1 shape", operation)

for kind in ("v2_agent", "v2_task"):
    for field, value in (("agent_run_id", "agent:foreign"), ("event_scope", "environment")):
        def operation(kind=kind, field=field, value=value):
            event = raw_kind[kind]()
            object.__setattr__(event, field, value)
            project_observatory((event,))
            return "accepted"

        check(f"{kind}/{field}", identity_error, operation)

for reverse in (False, True):
    for foreign in (None, {}, object()):
        def operation(reverse=reverse, foreign=foreign):
            values = [start_ledger().events()[0], foreign]
            project_observatory(reversed(values) if reverse else values)
            return "accepted"

        check(f"foreign/{reverse}/{type(foreign).__name__}", "TypeError: Observatory accepts TraceEvent values only", operation)

    def duplicate(reverse=reverse):
        event = start_ledger().events()[0]
        values = (event, event)
        project_observatory(reversed(values) if reverse else values)
        return "accepted"

    check(f"duplicate/{reverse}", "ValueError: Observatory event identities must be unique", duplicate)

    def valid_multiple(reverse=reverse):
        first = start_ledger(suffix="one").events()[0]
        second = start_ledger(suffix="two").events()[0]
        source = (first, second) if not reverse else (second, first)
        before = tuple(event.to_dict() for event in source)
        document = render_observatory(iter(source), data_label="conceptual")
        return (len(document.projection.traces) == 2
                and len(json.loads(document.graph_json)["nodes"]) == 2
                and before == tuple(event.to_dict() for event in source))

    check(f"valid-incomplete-multiple/{reverse}", True, valid_multiple)

    def stale_multiple(reverse=reverse):
        first = start_ledger(suffix="one").events()[0]
        second = start_ledger(suffix="two").events()[0]
        object.__setattr__(second, "event_type", "terminal_task_accepted")
        source = (first, second) if not reverse else (second, first)
        project_observatory(iter(source))
        return "accepted"

    check(f"stale-multiple/{reverse}", identity_error, stale_multiple)


def iterator_error():
    def broken():
        yield start_ledger().events()[0]
        raise RuntimeError("iterator sentinel")

    render_observatory(broken())
    return "accepted"


check("iterator-error", "RuntimeError: iterator sentinel", iterator_error)
check("empty", True, lambda: not render_observatory(()).projection.events)
check("raw-recorded-label", "ValueError: recorded Observatory data requires a validated ledger",
      lambda: project_observatory(start_ledger().events(), data_label="recorded"))


def ledger_unchanged():
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "ledger.jsonl"
        ledger = start_ledger(path)
        before = path.read_bytes()
        events = ledger.events()
        payloads = tuple(event.to_dict() for event in events)
        recorded = render_observatory(ledger)
        raw = render_observatory(iter(events), data_label="synthetic")
        return (before == path.read_bytes()
                and payloads == tuple(event.to_dict() for event in events)
                and recorded.projection.trace_ids == raw.projection.trace_ids)


check("file-backed-read-only", True, ledger_unchanged)
print(json.dumps({"module": observatory.__file__,
                  "module_sha256": hashlib.sha256(Path(observatory.__file__).read_bytes()).hexdigest(),
                  "results": rows}, indent=2))
