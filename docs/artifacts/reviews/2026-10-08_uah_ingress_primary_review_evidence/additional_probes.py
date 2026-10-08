"""Supplementary post-read bindings for predeclared export/replay cases."""

from contextlib import redirect_stdout
from dataclasses import replace
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory

with redirect_stdout(StringIO()):
    helpers = runpy.run_path(str(Path(__file__).with_name("public_probes.py")))

setup = helpers["setup"]
ingress = helpers["ingress"]
compile_task = helpers["compile_task"]
RESULTS = []
LifecycleLedger = helpers["LifecycleLedger"]
EnvironmentTaskRegistry = helpers["EnvironmentTaskRegistry"]


def run_case(name, fn):
    try:
        RESULTS.append(dict(case=name, result="returned", value=fn()))
    except Exception as exc:
        RESULTS.append(dict(case=name, result="exception", exception=type(exc).__name__, message=str(exc)))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def legacy_start():
    ctx = setup()
    decision = ctx["authority"].admit(ctx["run"], ingress())
    compiled = compile_task(ctx, decision)
    event = ctx["ledger"].events()[0].to_dict()
    data = json.loads(event["data_json"])
    data.pop("task_start_authority", None)
    event["data_json"] = canonical(data)
    event.pop("event_id")
    event["event_id"] = "trace-event:sha256:" + sha256(canonical(event).encode()).hexdigest()
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "legacy-start.jsonl"
        path.write_text(canonical(event) + "\n", encoding="utf-8")
        ledger = LifecycleLedger(path)
        visible = EnvironmentTaskRegistry(ledger).lineage_for_task(environment_run_id="review-run-a", task_id="review-task-alpha") is not None
        outcome = dict(readable=True, visible=visible, terminal=ledger.replay(decision.trace_id).terminal_status)
        for name, operation in [("compiler", lambda: compile_task(ctx, decision, ledger=ledger)), ("record_compiled", lambda: ledger.record(compiled))]:
            try:
                value = operation()
                outcome[name] = dict(result="returned", identity=getattr(value, "compiled_task_id", None))
            except Exception as exc:
                outcome[name] = dict(result="exception", exception=type(exc).__name__, message=str(exc))
        outcome["event_count"] = len(ledger.events())
        return outcome


def exported(form):
    ctx = setup()
    decision = ctx["authority"].admit(ctx["run"], ingress())
    event = ctx["ledger"].events()[0]
    value = {"event": event, "mapping": event.to_dict(), "iterable": iter(ctx["ledger"].events()), "replay": ctx["ledger"].replay(decision.trace_id)}[form]
    target = LifecycleLedger()
    try:
        target.record(value)
        return dict(events=len(target.events()), accepted=True)
    except Exception as exc:
        return dict(events=len(target.events()), accepted=False, exception=type(exc).__name__, message=str(exc))


def stale_policy_at_construction():
    ctx = setup()
    object.__setattr__(ctx["pack"].ingress_rules[0], "binding_id", "unknown-binding")
    helpers["TaskIngressAuthority"](environment_profile_id="review-profile", domain_contract_pack=ctx["pack"])
    return "constructed"


def spec_tamper(field):
    ctx = setup()
    decision = ctx["authority"].admit(ctx["run"], ingress())
    original = helpers["spec"](ctx, decision)
    return compile_task(ctx, decision, task_spec=replace(original, **{field: "sha256:" + "0" * 64})).compiled_task_id


def genuine_record_restart():
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "genuine.jsonl"
        ctx = setup(path)
        decision = ctx["authority"].admit(ctx["run"], ingress())
        compiled = compile_task(ctx, decision)
        ctx["ledger"].record(compiled)
        reloaded = LifecycleLedger(path)
        return dict(events=[e.event_type for e in reloaded.events()], same_lineage=EnvironmentTaskRegistry(reloaded).lineage_for_task(environment_run_id="review-run-a", task_id="review-task-alpha").trace_id == compiled.trace_id)


run_case("18-legacy-unmarked-start", legacy_start)
for form in ["event", "mapping", "iterable", "replay"]:
    run_case("18-exported-" + form, lambda form=form: exported(form))
run_case("15-stale-domain-rule-before-authority-construction", stale_policy_at_construction)
for field in ["task_id", "trace_id", "domain_contract_pack_revision"]:
    run_case("08-task-spec-tamper-" + field, lambda field=field: spec_tamper(field))
run_case("02-genuine-start-compile-record-reload", genuine_record_restart)
print(json.dumps(dict(import_path=helpers["ab_harness"].__file__, execution_stage="post-read supplementary", probes=RESULTS), indent=2, sort_keys=True))
