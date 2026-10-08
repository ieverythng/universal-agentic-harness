"""Independent public-seam probes. Run once per isolated implementation."""

from dataclasses import asdict
import hashlib
import itertools
import json

from ab_harness.lifecycle import TraceEvent
from ab_harness.observatory import project_observatory, render_observatory


def content_id(fields):
    fields = dict(fields)
    fields.pop("event_id", None)
    if fields["schema_version"] == "uah.trace_event/v1":
        fields.pop("event_scope", None)
        fields.pop("agent_run_id", None)
    encoded = json.dumps(fields, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return "trace-event:sha256:" + hashlib.sha256(encoded.encode()).hexdigest()


def event(sequence=1, version=1, scope="task", actor=None, **changes):
    fields = {
        "schema_version": "uah.trace_event/v%d" % version,
        "sequence": sequence,
        "commit_id": "commit:independent:%s" % sequence,
        "commit_index": 1,
        "commit_size": 1,
        "recorded_at": "2026-10-08T15:30:00Z",
        "event_type": "terminal_task_accepted",
        "environment_run_id": "environment:independent",
        "task_id": "task:independent" if scope == "task" else None,
        "trace_id": "trace:independent" if scope == "task" else None,
        "operation_id": None,
        "parent_event_id": None,
        "artifact_refs": ("artifact:independent",),
        "data_json": '{"nested":{"items":[1,2]}}',
        "event_scope": scope,
        "agent_run_id": actor,
    }
    fields.update(changes)
    return TraceEvent(event_id=content_id(fields), **fields)


def mutate(value, changes, fresh_identity=False):
    for key, changed in changes.items():
        object.__setattr__(value, key, changed)
    if fresh_identity:
        object.__setattr__(value, "event_id", content_id(asdict(value)))
    return value


def snapshot(projection):
    return {
        "events": [value.event_id for value in projection.events],
        "actors": [value.agent_run_id for value in projection.agent_runs],
        "traces": [(value.trace_id, value.status.value) for value in projection.traces],
        "environments": list(projection.environment_run_ids),
        "label": projection.data_label.value,
    }


results = []


def probe(name, values, expected, use_generator=False, consumer="project"):
    source = (value for value in values) if use_generator else tuple(values)
    try:
        result = (project_observatory if consumer == "project" else render_observatory)(source)
        projection = result if consumer == "project" else result.projection
        actual = snapshot(projection)
        if consumer == "render":
            graph = json.loads(result.graph_json)
            nodes = [node for node in graph["nodes"] if node["kind"] == "lifecycle_event"]
            assert [node["id"] for node in nodes] == actual["events"]
            assert all(value.event_id in result.html for value in projection.events)
            actual["graph_html_agree"] = True
        accepted = True
    except Exception as error:
        actual = {"error_type": type(error).__name__, "message": str(error)}
        accepted = False
    results.append({"case": name, "consumer": consumer, "generator": use_generator,
                    "expected": expected, "actual": actual, "matches": accepted == (expected == "accept")})


# Valid forms, both consumers, both iterable representations, all mixed-history orders.
for version, scope, actor in ((1, "task", None), (2, "task", "actor:one"), (2, "agent", "actor:one")):
    for consumer, generator in itertools.product(("project", "render"), (False, True)):
        probe("valid-v%d-%s" % (version, scope), [event(version=version, scope=scope, actor=actor)],
              "accept", generator, consumer)
for index, order in enumerate(itertools.permutations((1, 2, 3))):
    mixed = {1: event(1), 2: event(2, 2, "agent", "actor:one"),
             3: event(3, 2, "task", "actor:two", event_type="model_invocation_failed")}
    probe("mixed-order-%d" % index, [mixed[number] for number in order], "accept", True, "render")
for consumer in ("project", "render"):
    probe("empty", [], "accept", True, consumer)
for terminal in ("terminal_task_accepted", "terminal_task_accepted_with_deficit",
                 "terminal_task_rejected", "execution_failed", "semantic_admission_rejected",
                 "budget_exhausted", "retry_exhausted"):
    value = event(event_type=terminal)
    document = render_observatory((value,))
    expected_status = ("accepted" if terminal in {"terminal_task_accepted", "terminal_task_accepted_with_deficit"}
                       else "rejected" if terminal == "terminal_task_rejected" else "open")
    actual_status = document.projection.traces[0].status.value
    results.append({"case": "explicit-status-" + terminal, "expected": expected_status,
                    "actual": actual_status, "matches": actual_status == expected_status})

# v1 fields excluded from content identity must still respect owner shape.
for changes in ({"agent_run_id": "actor:forged"}, {"event_scope": "agent"},
                {"event_scope": "agent", "agent_run_id": "actor:forged"},
                {"event_scope": "unknown"}, {"event_scope": None}, {"agent_run_id": 7}):
    for consumer, generator in itertools.product(("project", "render"), (False, True)):
        changed = mutate(event(), changes)
        changed.verify_identity()
        probe("v1-excluded-" + repr(changes), [changed], "reject", generator, consumer)

# Retaining old content identity after changing covered fields is rejected.
stale = {"event_type": "terminal_task_rejected", "environment_run_id": "environment:foreign",
         "task_id": "task:foreign", "trace_id": "trace:foreign", "sequence": 999,
         "commit_id": "commit:foreign", "commit_index": 2, "commit_size": 2,
         "recorded_at": "2026-10-09T00:00:00Z", "operation_id": "operation:foreign",
         "parent_event_id": "trace-event:foreign", "artifact_refs": ("artifact:foreign",),
         "data_json": '{"changed":true}', "event_id": "trace-event:stale"}
for key, changed in stale.items():
    for consumer in ("project", "render"):
        probe("stale-" + key, [mutate(event(), {key: changed})], "reject", True, consumer)
for key, changed in (("agent_run_id", "actor:foreign"), ("event_scope", "agent")):
    probe("stale-v2-" + key, [mutate(event(version=2, actor="actor:one"), {key: changed})],
          "reject", True, "render")

# Shape-invalid values with fresh identities distinguish owner shape from hashing alone.
invalid = ({"schema_version": "uah.trace_event/v9"}, {"event_scope": "bogus"},
           {"artifact_refs": ["artifact:independent"]}, {"artifact_refs": ()},
           {"artifact_refs": ("",)}, {"sequence": 0}, {"sequence": -1},
           {"commit_index": 0}, {"commit_index": 2}, {"task_id": None},
           {"trace_id": ""}, {"data_json": "[]"}, {"data_json": '{"a": 1}'},
           {"environment_run_id": ""}, {"event_type": ""}, {"recorded_at": ""})
for changes in invalid:
    for consumer in ("project", "render"):
        probe("shape-" + repr(changes), [mutate(event(), changes, True)], "reject", True, consumer)
for version, changes in ((1, {"sequence": "one"}), (1, {"artifact_refs": (1,)}),
                         (1, {"environment_run_id": 1}), (1, {"data_json": None}),
                         (2, {"agent_run_id": None}), (2, {"agent_run_id": ""}),
                         (2, {"event_scope": "agent"}), (2, {"event_scope": "bogus"})):
    probe("invalid-type-v%d-" % version + repr(changes),
          [mutate(event(version=version, actor="actor:one" if version == 2 else None), changes, True)],
          "reject", True, "project")

for foreign in (object(), {}, {"schema_version": "foreign/v1"}, "foreign", 7, None):
    probe("foreign-" + repr(foreign), [foreign], "reject", True, "project")
duplicate = event()
probe("duplicate-identity", [duplicate, duplicate], "reject", False, "render")
probe("duplicate-sequence-distinct-ids", [event(), event(event_type="terminal_task_rejected")], "accept")

# Existing lineage consistency belongs to the projection; raw causality remains unconstrained.
probe("mixed-trace-lineage", [event(), event(2, task_id="task:foreign")], "reject")
probe("mixed-actor-environments", [event(version=2, scope="agent", actor="actor:one"),
      event(2, 2, "agent", "actor:one", environment_run_id="environment:foreign")], "reject")
probe("missing-parent-synthetic", [event(parent_event_id="trace-event:missing")], "accept", True, "render")
probe("incomplete-commit-synthetic", [event(commit_size=2)], "accept", True, "render")

original = event(version=2, actor="actor:one")
projection = project_observatory((original,))
before = snapshot(projection)
retained_fields = asdict(projection.events[0])
shared_detached_views = (projection.events[0] is projection.traces[0].events[0]
                         and projection.events[0] is projection.agent_runs[0].events[0]
                         and projection.events[0] is not original)
payload = original.data
payload["nested"]["items"].append(3)
payload_stable = original.data == {"nested": {"items": [1, 2]}}
mutate(original, {"event_type": "terminal_task_rejected", "agent_run_id": "actor:later",
                  "environment_run_id": "environment:later", "trace_id": "trace:later",
                  "data_json": '{"mutated":true}'})
after = snapshot(projection)
results.append({"case": "later-input-alias-mutation", "expected": before,
                "actual": after, "matches": before == after and payload_stable
                and retained_fields == asdict(projection.events[0]) and shared_detached_views,
                "payload_getter_detached": payload_stable,
                "all_retained_fields_stable": retained_fields == asdict(projection.events[0]),
                "shared_detached_views": shared_detached_views})

print(json.dumps({"total": len(results), "mismatches": sum(not result["matches"] for result in results),
                  "results": results}, sort_keys=True, indent=2))
