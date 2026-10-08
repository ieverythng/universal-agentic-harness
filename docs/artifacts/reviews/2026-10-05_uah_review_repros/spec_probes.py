"""Read-only review probes. All persistent state lives under a temporary path."""

import json
import runpy
import tempfile
from dataclasses import replace
from pathlib import Path

from ab_harness import TaskSpecCompiler, EnvironmentTaskRegistry, LifecycleLedger
from ab_harness.environment_ingress import TaskIngressDecision
from ab_harness.lifecycle import TaskStartedFact

ROOT = Path(__file__).resolve().parents[4]
_compiler_inputs = runpy.run_path(str(ROOT / "tests/test_task_compiler.py"))[
    "_compiler_inputs"
]


def nested_domain_tamper():
    inputs = _compiler_inputs()
    domain = inputs["domain_contract_pack"]
    original = domain.revision
    object.__setattr__(domain.effect_rules[0], "failure_policy", "retryable")
    compiled = TaskSpecCompiler().compile(**inputs)
    print(
        "nested_domain_tamper:",
        json.dumps(
            {
                "revision_preserved": compiled.domain_contract_pack_revision
                == original,
                "issued_policy": "terminal",
                "compiled_policy": compiled.effect_obligations[0].failure_policy,
            }
        ),
    )


def caller_started_fact():
    inputs = _compiler_inputs()
    original = inputs["task_ingress_decision"]
    decision = TaskIngressDecision(
        action="start_task",
        reason_code="matched_rule",
        environment_run_id="unregistered-environment",
        environment_ingress_id="never-observed-ingress",
        domain_contract_pack_revision=original.domain_contract_pack_revision,
        environment_ingress_artifact_id="never-issued-artifact",
        task_id="caller-authored-task",
        trace_id="caller-authored-trace",
    )
    with tempfile.TemporaryDirectory(prefix="uah-spec-forged-start-") as tmp:
        path = Path(tmp) / "ledger.jsonl"
        ledger = LifecycleLedger(path)
        ledger.record(
            TaskStartedFact(
                environment_run_id=decision.environment_run_id,
                environment_ingress_id=decision.environment_ingress_id,
                ingress_artifact_id=decision.environment_ingress_artifact_id,
                decision_id=decision.decision_id,
                domain_contract_pack_revision=decision.domain_contract_pack_revision,
                task_id=decision.task_id,
                trace_id=decision.trace_id,
            )
        )
        inputs["task_ingress_decision"] = decision
        inputs["task_spec"] = replace(
            inputs["task_spec"], task_id=decision.task_id, trace_id=decision.trace_id
        )
        inputs["task_registry"] = EnvironmentTaskRegistry(LifecycleLedger(path))
        compiled = TaskSpecCompiler().compile(**inputs)
        ledger.record(compiled)
        reloaded = LifecycleLedger(path)
        print(
            "caller_started_fact:",
            json.dumps(
                {
                    "event_types": [event.event_type for event in reloaded.events()],
                    "environment": compiled.environment_run_id,
                    "task": compiled.task_id,
                    "trace": compiled.trace_id,
                }
            ),
        )


def semantic_catalog_drift():
    from ab_harness import BindingCatalog, RegistrySnapshot, DomainLifecycleAdmission
    from ab_harness import EnvironmentIngress, TaskIngressAuthority
    from ab_harness.environment import InProcessEnvironmentOwner
    from ab_harness.contracts import OwnerExecutionResult
    from ab_harness.acceptance import TaskAcceptanceEvaluator
    from ab_harness.lifecycle import AcceptanceFact

    fixtures = runpy.run_path(str(ROOT / "tests/test_two_stage_admission.py"))
    _admission_fixture = fixtures["_admission_fixture"]
    _proposal = fixtures["_proposal"]
    _semantic_admission = fixtures["_semantic_admission"]
    _domain_pack_for_compiled = fixtures["_domain_pack_for_compiled"]

    compiled, original_catalog, environment = _admission_fixture()
    original = original_catalog.object_for("find_object")
    drifted_object = replace(
        original,
        expected_effects=(*original.expected_effects, "direct_speech"),
        observable_success=(*original.observable_success, "direct_speech"),
    )
    drifted_catalog = BindingCatalog(
        RegistrySnapshot(
            (drifted_object,),
            source="synthetic:other-registry",
            version="different-registry",
        ),
        original_catalog.bindings_for("find_object"),
    )
    proposal = _proposal(compiled)
    admitted = (
        _semantic_admission(drifted_catalog)
        .admit(compiled, proposal)
        .admitted_operation
    )
    with tempfile.TemporaryDirectory(prefix="uah-spec-catalog-drift-") as tmp:
        path = Path(tmp) / "ledger.jsonl"
        ledger = LifecycleLedger(path)
        domain = _domain_pack_for_compiled(compiled)
        TaskIngressAuthority(
            environment_profile_id=environment.attestation.environment_profile_id,
            domain_contract_pack=domain,
            lifecycle_ledger=ledger,
        ).admit(
            environment,
            EnvironmentIngress(
                environment_ingress_id=compiled.environment_ingress_id,
                environment_run_id=compiled.environment_run_id,
                binding_id="binding:nao.request:v1",
                ingress_type="user_request",
                payload_artifact_id="artifact:request:admission-001",
                native_lineage=(("goal_id", compiled.task_id),),
                observed_at="2026-09-28T09:00:01Z",
            ),
        )
        ledger.record(compiled)
        ledger.record(proposal)
        ledger.record(admitted)
        lease = (
            DomainLifecycleAdmission(
                environment_run=environment,
                environment_id="nao_fake",
                lifecycle_ledger=ledger,
            )
            .request_execution(admitted)
            .execution_lease
        )
        owner = InProcessEnvironmentOwner(
            environment_id="nao_fake",
            environment_run=environment,
            catalog=drifted_catalog,
            lifecycle_ledger=ledger,
            handlers={
                "fake_nao.skills:find_object": lambda args: OwnerExecutionResult(
                    evidence_ref="synthetic:prohibited-effect",
                    succeeded=True,
                    observed_effects=(
                        "fresh detector-backed result returned",
                        "direct_speech",
                    ),
                )
            },
        )
        receipt = owner.execute(lease).receipt
        acceptance = TaskAcceptanceEvaluator().evaluate(
            compiled.effect_obligations, (receipt.evidence,)
        )
        ledger.record(AcceptanceFact(compiled, (receipt.evidence,), acceptance))
        print(
            "semantic_catalog_drift:",
            json.dumps(
                {
                    "prohibited": compiled.prohibited_effects,
                    "observed": receipt.evidence.observed_effects,
                    "terminal_after_restart": LifecycleLedger(path)
                    .replay(compiled.trace_id)
                    .terminal_status,
                }
            ),
        )


def exposed_event_tamper():
    from ab_harness.runtime_controls import TaskBudgetAuthority
    from ab_harness.lifecycle import TraceEvent

    inputs = _compiler_inputs()
    compiled = TaskSpecCompiler().compile(**inputs)
    # Fixture setup retrieves its ledger; the tamper targets the public event.
    ledger = inputs["task_registry"]._ledger
    ledger.record(compiled)
    event = ledger.events()[-1]
    data = event.data
    data["budgets"]["model_calls"] = 1000
    object.__setattr__(
        event, "data_json", json.dumps(data, sort_keys=True, separators=(",", ":"))
    )
    decision = TaskBudgetAuthority(ledger).consume(
        trace_id=compiled.trace_id,
        resource="model_call",
        subject_id="over-budget",
        units=4,
    )
    try:
        TraceEvent.from_dict(event.to_dict())
        serialized_valid = True
    except ValueError:
        serialized_valid = False
    print(
        "exposed_event_tamper:",
        json.dumps(
            {
                "original_model_call_limit": compiled.budgets.model_calls,
                "granted_units": decision.units,
                "outcome": decision.outcome,
                "event_hash_valid": serialized_valid,
            }
        ),
    )


if __name__ == "__main__":
    nested_domain_tamper()
    caller_started_fact()
    semantic_catalog_drift()
    exposed_event_tamper()
