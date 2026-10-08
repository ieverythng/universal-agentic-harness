import inspect
import json
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

import ab_harness as a
from ab_harness.lifecycle import TaskIngressFact, TaskStartedFact


def result(name, fn):
    try:
        value = fn()
        print(json.dumps({"case": name, "accepted": True, "value": str(value)}, sort_keys=True))
    except Exception as error:
        print(json.dumps({"case": name, "accepted": False, "type": type(error).__name__, "message": str(error)}, sort_keys=True))


def setup(path=None, *, tool_calls=2, additional=False):
    item = a.ABObjectView("write", 1, "skill", "test", "owner", observable_success=("written",), runtime_callable=True)
    registry = a.RegistrySnapshot((item,), source="review:fixture", version="registry:review")
    role = a.AgentRoleSpec("writer", ("operation",), a.ABControlBand(1, 1, 1))
    frame = a.AbstractionFrame("review", "notes", "one write", registry.version)
    domain = a.DomainContractPack.issue(domain_contract_pack_id="domain:review", frame_id=frame.frame_id, registry_version=registry.version, allowed_role_ids=(role.role_id,), supported_task_type_ids=("write",), ingress_rules=(a.TaskIngressRule("request", "request", "start_task", "task_id"), a.TaskIngressRule("resume", "request", "resume_task", "task_id")), effect_rules=(a.DomainEffectRule("written", "write", "owner", "terminal"),))
    run = a.EnvironmentRun(a.EnvironmentRunAttestation("environment:review", "profile:review", domain.revision, "runtime:review", "owner", "attestation:review", "2024-02-29T23:59:00Z", ("ready:review",)))
    ledger = a.LifecycleLedger(path, clock=lambda: "2024-02-29T23:59:00Z")
    task_registry = a.EnvironmentTaskRegistry(ledger)
    ingress = a.EnvironmentIngress("ingress:review", run.environment_run_id, "request", "request", "artifact:review", (("task_id", "task:review"),), "2024-02-29T23:59:00Z")
    if hasattr(a, "TaskIngressAuthority"):
        authority = a.TaskIngressAuthority(environment_profile_id="profile:review", domain_contract_pack=domain, lifecycle_ledger=ledger)
        decision = authority.admit(run, ingress)
    else:
        authority = a.TaskIngressPolicy(environment_profile_id="profile:review", domain_contract_pack=domain, task_registry=task_registry)
        decision = authority.classify(run, ingress)
    compiled = a.TaskSpecCompiler().compile(task_ingress_decision=decision, task_spec=a.TaskSpec(decision.task_id, decision.trace_id, "write", role.role_id, frame.frame_id, domain.revision, "Write", (a.TaskEffectRequest("written", "written", "required"),), (), a.TaskBudgets(60, 2, tool_calls)), role=role, frame=frame, registry=registry, domain_contract_pack=domain, task_registry=task_registry)
    ledger.record(compiled)
    binding = a.ABImplementationBinding("binding:review", "write", "review", "owner", "python_method", "review.write", "v1", "schema:review", "schema:result", "evidence:review", ("fake",), "approved")
    catalog = a.BindingCatalog(registry, (binding,))
    kwargs = dict(catalog=catalog, environment_id="review", runtime_mode="fake")
    if hasattr(a, "ObjectArgumentSchema"):
        schema = a.ObjectArgumentSchema.issue(schema_ref="schema:review", fields=(a.ArgumentField("text", "string"),), required=("text",), allow_additional_properties=additional)
        kwargs["schema_validator"] = a.InMemoryArgumentSchemaRegistry((schema,))
    admission = a.SemanticAdmission(**kwargs)
    return ledger, run, compiled, catalog, admission, authority, ingress, domain


def proposal(compiled, admission, operation="op:1", arguments=None):
    normalized = a.ProposalNormalizer().normalize(compiled_task=compiled, operation_id=operation, raw_output_artifact_id="artifact:raw", output=a.AgentOutput("operation", {"object_id": "write", "arguments": arguments or {"text": "hello"}}, ("write",)))
    if normalized.proposal is None:
        return normalized, None
    return normalized.proposal, admission.admit(compiled, normalized.proposal)


def raw_ingress(action):
    ledger, run, compiled, *_ = setup()
    fact = TaskIngressFact(environment_run_id=run.environment_run_id, task_id=compiled.task_id, trace_id=compiled.trace_id, environment_ingress_id="forged:" + action, ingress_artifact_id="forged:artifact", decision_id="forged:decision", domain_contract_pack_revision=compiled.domain_contract_pack_revision, action=action)
    ledger.record(fact)
    registry = a.EnvironmentTaskRegistry(ledger)
    lineage = registry.lineage_for_ingress(environment_run_id=run.environment_run_id, environment_ingress_id="forged:" + action) if hasattr(registry, "lineage_for_ingress") else "baseline projection API differs"
    return {"event": ledger.events()[-1].event_type, "registry_accepts": lineage is not None, "source_ingress_supplied": False}


def schema_extra(policy):
    ledger, run, compiled, catalog, admission, *_ = setup(additional=policy)
    prop, decision = proposal(compiled, admission, arguments={"text": "hello", "not_reviewed": "payload"})
    if not decision.accepted:
        return {"semantic_admitted": False, "reasons": decision.reason_codes}
    ledger.record(prop)
    ledger.record(decision.admitted_operation)
    lease = a.DomainLifecycleAdmission(environment_run=run, environment_id="review", lifecycle_ledger=ledger).request_execution(decision.admitted_operation).execution_lease
    seen = []
    def handler(arguments):
        seen.append(arguments)
        return a.OwnerExecutionResult("evidence:review", True, ("written",), {})
    owner = a.InProcessEnvironmentOwner(environment_id="review", environment_run=run, catalog=catalog, handlers={"review.write": handler}, lifecycle_ledger=ledger)
    output = owner.execute(lease)
    return {"semantic_admitted": True, "handler_arguments": seen, "return_type": type(output).__name__}


def control(which):
    with TemporaryDirectory() as directory:
        ledger, run, compiled, catalog, admission, authority, ingress, domain = setup(Path(directory) / "ledger.jsonl", tool_calls=1)
        prop, decision = proposal(compiled, admission)
        ledger.record(prop)
        ledger.record(decision.admitted_operation)
        lease = a.DomainLifecycleAdmission(environment_run=run, environment_id="review", lifecycle_ledger=ledger).request_execution(decision.admitted_operation).execution_lease
        seen = []
        def handler(arguments):
            seen.append(arguments)
            return a.OwnerExecutionResult("evidence:review", True, ("written",), {})
        owner = a.InProcessEnvironmentOwner(environment_id="review", environment_run=run, catalog=catalog, handlers={"review.write": handler}, lifecycle_ledger=ledger)
        if which == "cancel":
            owner.cancel(lease, requester_id="review", request_artifact_id="cancel:review", reason_code="cancelled")
        elif which == "timeout":
            a.TaskRuntimeControlAuthority(ledger).evaluate_timeout(compiled_task=compiled, observed_at="2024-03-01T00:00:01Z", policy_revision="timeout:review")
        elif which == "nested_tamper":
            object.__setattr__(lease.admitted_operation.proposal, "arguments_json", '{"text":"tampered"}')
        elif which == "duplicate":
            owner.execute(lease)
            ledger = a.LifecycleLedger(ledger.path)
            owner = a.InProcessEnvironmentOwner(environment_id="review", environment_run=run, catalog=catalog, handlers={"review.write": handler}, lifecycle_ledger=ledger)
        elif which == "wrong_owner":
            object.__setattr__(lease, "lease_owner_id", "intruder")
        caught = None
        try:
            owner.execute(lease)
        except Exception as error:
            caught = type(error).__name__ + ": " + str(error)
        reloaded = a.LifecycleLedger(ledger.path)
        return {"handler_calls": len(seen), "error": caught, "events": [event.event_type for event in reloaded.events()]}


def budget_existing_type(value):
    ledger, run, compiled, *_ = setup()
    authority = a.TaskBudgetAuthority(ledger)
    authority.consume(trace_id=compiled.trace_id, resource="model_call", subject_id="call:review", units=1)
    return authority.consume(trace_id=compiled.trace_id, resource="model_call", subject_id="call:review", units=value).to_dict()


for field in ("wall_time_seconds", "model_calls", "tool_calls"):
    for value in (True, 1.5, float("nan"), float("inf"), 0, 1):
        kwargs = dict(wall_time_seconds=1, model_calls=1, tool_calls=1)
        kwargs[field] = value
        result(f"compatible-budgets/{field}/{value!r}", lambda kwargs=kwargs: a.TaskBudgets(**kwargs))
for action in ("resume_task", "notify_task"):
    result("raw-ingress/" + action, lambda action=action: raw_ingress(action))
for policy in (False, True, "false", 1, None):
    result("additional-policy/" + repr(policy), lambda policy=policy: schema_extra(policy))
for case in ("cancel", "timeout", "nested_tamper", "duplicate", "wrong_owner"):
    result("dispatch/" + case, lambda case=case: control(case))
for value in (True, 1.0, 1, 2):
    result("budget-idempotent-units/" + repr(value), lambda value=value: budget_existing_type(value))
