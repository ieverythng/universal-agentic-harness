"""Predeclared public-interface ingress review probes (no source inspection)."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier

import ab_harness
from ab_harness.contracts import ABControlBand, AbstractionFrame, AgentRoleSpec
from ab_harness.contracts import TaskAcceptance
from ab_harness.domain_contracts import DomainContractPack, DomainEffectRule, TaskIngressRule
from ab_harness.environment_ingress import EnvironmentIngress, TaskIngressDecision
from ab_harness.environment_profiles import EnvironmentProfile, EnvironmentProfileRegistry
from ab_harness.environment_runs import EnvironmentRunAttestation, EnvironmentRunRegistry
from ab_harness.lifecycle import AcceptanceFact, LifecycleLedger, TaskIngressFact, TaskStartedFact
from ab_harness.registry import RegistrySnapshot
from ab_harness.task_compiler import TaskBudgets, TaskEffectRequest, TaskSpec, TaskSpecCompiler
from ab_harness.task_ingress_authority import TaskIngressAuthority
from ab_harness.task_registry import EnvironmentTaskRegistry

RESULTS = []
STAMP = "2026-10-08T18:00:00+00:00"
ZERO = "sha256:" + "0" * 64


def setup(path=None, run_id="review-run-a"):
    registry = RegistrySnapshot.from_json_file("tests/fixtures/ab_registry.json")
    pack = DomainContractPack.issue(
        domain_contract_pack_id="review-domain",
        frame_id="review-frame",
        registry_version=registry.version,
        allowed_role_ids=("review-role",),
        supported_task_type_ids=("review-tasktype",),
        ingress_rules=tuple(
            TaskIngressRule("review-binding", kind, action, "task_id")
            for kind, action in (("request", "start_task"), ("resume", "resume_task"), ("notify", "notify_task"))
        ),
        effect_rules=(DomainEffectRule("fresh detector-backed result returned", "find_object", "object_finder", "terminal"),),
    )
    profile = EnvironmentProfile("review-profile", pack.domain_contract_pack_id, pack.revision, "review-native", "review-owner", ("review-binding",))
    runs = EnvironmentRunRegistry(EnvironmentProfileRegistry((profile,)))
    run = runs.register(EnvironmentRunAttestation(run_id, "review-profile", pack.revision, "review-native", "review-owner", "review-attestation-" + run_id, STAMP, ("review-readiness",)))
    ledger = LifecycleLedger(path)
    authority = TaskIngressAuthority(environment_profile_id="review-profile", domain_contract_pack=pack, lifecycle_ledger=ledger)
    role = AgentRoleSpec("review-role", ("operation_proposal",), ABControlBand(1, 1, 1))
    frame = AbstractionFrame("review-frame", "review-fixture", "skill is atomic", registry.version)
    return dict(registry=registry, pack=pack, run=run, ledger=ledger, authority=authority, role=role, frame=frame)


def ingress(kind="request", task="review-task-alpha", request="review-request-1", run="review-run-a", lineage=None, binding="review-binding", stamp=STAMP):
    return EnvironmentIngress(request, run, binding, kind, "review-payload", (("task_id", task),) if lineage is None else lineage, stamp)


def spec(ctx, decision):
    return TaskSpec(decision.task_id, decision.trace_id, "review-tasktype", "review-role", "review-frame", ctx["pack"].revision, "localize a requested object", (TaskEffectRequest("review-obligation", "fresh detector-backed result returned", "required"),), (), TaskBudgets(60, 2, 2, 1))


def compile_task(ctx, decision, task_spec=None, ledger=None):
    return TaskSpecCompiler().compile(task_ingress_decision=decision, task_spec=spec(ctx, decision) if task_spec is None else task_spec, role=ctx["role"], frame=ctx["frame"], registry=ctx["registry"], domain_contract_pack=ctx["pack"], task_registry=EnvironmentTaskRegistry(ctx["ledger"] if ledger is None else ledger))


def forged(ctx, item=None):
    item = ingress() if item is None else item
    trace = "trace:sha256:" + sha256(("uah-trace-v1\0" + item.environment_run_id + "\0review-task-alpha").encode()).hexdigest()
    decision = TaskIngressDecision(item.environment_ingress_id, item.ingress_artifact_id, item.environment_run_id, "start_task", "matched_rule", ctx["pack"].revision, "review-task-alpha", trace, "active")
    fact = TaskStartedFact(item.environment_run_id, decision.task_id, trace, item.environment_ingress_id, item.ingress_artifact_id, decision.decision_id, ctx["pack"].revision)
    return decision, fact


def run_case(name, fn):
    try:
        value = fn()
        RESULTS.append(dict(case=name, result="returned", value=value))
    except Exception as exc:
        RESULTS.append(dict(case=name, result="exception", exception=type(exc).__name__, message=str(exc)))


def valid():
    ctx = setup()
    d = ctx["authority"].admit(ctx["run"], ingress())
    c = compile_task(ctx, d)
    return dict(action=d.action, reason=d.reason_code, task=d.task_id, trace=d.trace_id, compiled=c.compiled_task_id, events=len(ctx["ledger"].events()))


def restart():
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        ctx = setup(path)
        d = ctx["authority"].admit(ctx["run"], ingress())
        before = compile_task(ctx, d)
        reloaded = LifecycleLedger(path)
        after = compile_task(ctx, d, ledger=reloaded)
        return dict(equal=before.compiled_task_id == after.compiled_task_id, events=len(reloaded.events()), action=ctx["authority"].admit(ctx["run"], ingress()).action)


def raw(then_compile=False, fact_type="start"):
    ctx = setup()
    d, fact = forged(ctx)
    if fact_type != "start":
        fact = TaskIngressFact(fact.environment_run_id, fact.task_id, fact.trace_id, fact.environment_ingress_id, fact.ingress_artifact_id, fact.decision_id, fact.domain_contract_pack_revision, fact_type)
    ctx["ledger"].record(fact)
    value = dict(events=len(ctx["ledger"].events()), visible=EnvironmentTaskRegistry(ctx["ledger"]).lineage_for_task(environment_run_id="review-run-a", task_id="review-task-alpha") is not None)
    if then_compile:
        value["compiled"] = compile_task(ctx, d).compiled_task_id
    return value


def decision_only():
    ctx = setup()
    d, _ = forged(ctx)
    return compile_task(ctx, d).compiled_task_id


def tamper(field):
    ctx = setup()
    d = ctx["authority"].admit(ctx["run"], ingress())
    changed = "review-run-b" if field == "environment_run_id" else ZERO
    altered = replace(d, **{field: changed})
    return compile_task(ctx, altered).compiled_task_id


def duplicate(reverse=False):
    ctx = setup()
    ids = ["review-request-1", "review-request-2"]
    if reverse:
        ids.reverse()
    output = [ctx["authority"].admit(ctx["run"], ingress(request=request)).to_dict() for request in ids]
    output.append(ctx["authority"].admit(ctx["run"], ingress(request=ids[0])).to_dict())
    return dict(decisions=[(d["action"], d["reason_code"]) for d in output], events=len(ctx["ledger"].events()))


def two_tasks(reverse=False):
    ctx = setup()
    tasks = ["review-task-alpha", "review-task-beta"]
    if reverse:
        tasks.reverse()
    result = [ctx["authority"].admit(ctx["run"], ingress(task=t, request="request-" + t)).to_dict() for t in tasks]
    ctx_b = setup(run_id="review-run-b")
    result.append(ctx_b["authority"].admit(ctx_b["run"], ingress(run="review-run-b")).to_dict())
    return [(d["action"], d["task_id"], d["trace_id"]) for d in result]


def resume(kind, state):
    ctx = setup()
    initial = None
    if state != "absent":
        initial = ctx["authority"].admit(ctx["run"], ingress())
    item = ingress(kind, request="review-request-2", task="foreign-task" if state == "foreign" else "review-task-alpha", run="review-run-b" if state == "wrong-run" else "review-run-a")
    result = ctx["authority"].admit(ctx["run"], item)
    return dict(action=result.action, reason=result.reason_code, same_trace=initial is not None and initial.trace_id == result.trace_id, events=len(ctx["ledger"].events()))


def native_lineage(lineage, stamp=STAMP):
    ctx = setup()
    item = ingress(lineage=lineage, stamp=stamp)
    result = ctx["authority"].admit(ctx["run"], item)
    return dict(action=result.action, reason=result.reason_code, task=result.task_id, events=len(ctx["ledger"].events()))


def wrong_binding(kind="request", binding="unknown-binding"):
    ctx = setup()
    result = ctx["authority"].admit(ctx["run"], ingress(kind=kind, binding=binding))
    return dict(action=result.action, reason=result.reason_code, events=len(ctx["ledger"].events()))


def content_mutation():
    ctx = setup()
    object.__setattr__(ctx["pack"], "ingress_rules", (TaskIngressRule("unknown-binding", "request", "start_task", "task_id"),))
    result = ctx["authority"].admit(ctx["run"], ingress())
    return dict(action=result.action, reason=result.reason_code)


def concurrency():
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        contexts = [setup(path), setup(path)]
        barrier = Barrier(2)
        def worker(ctx):
            barrier.wait()
            try:
                d = ctx["authority"].admit(ctx["run"], ingress())
                return dict(action=d.action, reason=d.reason_code)
            except Exception as exc:
                return dict(exception=type(exc).__name__, message=str(exc))
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(worker, contexts))
        events = LifecycleLedger(path).events()
        return dict(outcomes=outcomes, starts=sum(e.event_type == "task_started" for e in events), sequences=[e.sequence for e in events])


def registry_mutators():
    methods = [n for n in dir(EnvironmentTaskRegistry) if not n.startswith("_") and callable(getattr(EnvironmentTaskRegistry, n))]
    ledger_methods = [n for n in dir(LifecycleLedger) if not n.startswith("_") and callable(getattr(LifecycleLedger, n))]
    return dict(registry=methods, ledger=ledger_methods, alternate_bulk=[n for n in ledger_methods if "many" in n or "batch" in n or "append" in n])


def closure(status, kind):
    ctx = setup()
    d = ctx["authority"].admit(ctx["run"], ingress())
    c = compile_task(ctx, d)
    ctx["ledger"].record(c)
    fields = {"pending_obligation_ids": ("review-obligation",)} if status == "suspended" else {"failed_obligation_ids": ("review-obligation",)}
    ctx["ledger"].record(AcceptanceFact(c, (), TaskAcceptance(status, **fields)))
    value = ctx["authority"].admit(ctx["run"], ingress(kind, request="review-request-2"))
    return dict(action=value.action, reason=value.reason_code)


run_case("01-valid-admit-compile", valid)
run_case("02-restart-compile", restart)
run_case("03-public-raw-start", raw)
run_case("04-alternative-public-append-surface", registry_mutators)
run_case("05-forged-decision-without-start", decision_only)
run_case("06-public-raw-start-then-compile", lambda: raw(True))
for field in ["environment_run_id", "environment_ingress_artifact_id", "environment_ingress_id", "trace_id", "task_id", "domain_contract_pack_revision"]:
    run_case("08-decision-tamper-" + field, lambda field=field: tamper(field))
run_case("09-duplicates-forward", duplicate)
run_case("09-duplicates-reverse", lambda: duplicate(True))
run_case("10-two-tasks-forward", two_tasks)
run_case("10-two-tasks-reverse", lambda: two_tasks(True))
for kind in ["resume", "notify"]:
    for state in ["present", "absent", "wrong-run", "foreign"]:
        run_case("11-12-" + kind + "-" + state, lambda kind=kind, state=state: resume(kind, state))
    for status in ["rejected", "suspended"]:
        run_case("13-" + kind + "-after-" + status, lambda kind=kind, status=status: closure(status, kind))
for label, value in [("omitted", ()), ("null", (("task_id", None),)), ("empty", (("task_id", ""),)), ("whitespace", (("task_id", "   "),)), ("integer", (("task_id", 2),)), ("wrong-key", (("wrong_task_id", "review-task-alpha"),))]:
    run_case("14-lineage-" + label, lambda value=value: native_lineage(value))
run_case("15-unknown-binding", wrong_binding)
run_case("15-unknown-kind", lambda: wrong_binding("unknown-kind", "review-binding"))
run_case("15-domain-content-mutation", content_mutation)
run_case("17-two-writer-contention", concurrency)
run_case("timestamp-equivalent-offset", lambda: native_lineage((("task_id", "review-task-alpha"),), "2026-10-08T20:00:00+02:00"))
for action in ["resume_task", "notify_task", "start_task"]:
    run_case("raw-ingress-fact-" + action, lambda action=action: raw(fact_type=action))
print(json.dumps(dict(import_path=ab_harness.__file__, implementation_not_read=True, probes=RESULTS), indent=2, sort_keys=True))
