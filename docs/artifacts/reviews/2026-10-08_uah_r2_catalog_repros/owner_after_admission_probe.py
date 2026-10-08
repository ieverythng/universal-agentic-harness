"""Public owner controls for catalog replacement after valid admission."""

from dataclasses import replace
import json
from pathlib import Path
import runpy
import tempfile

from ab_harness import BindingCatalog, DomainLifecycleAdmission
from ab_harness import EnvironmentIngress, LifecycleLedger
from ab_harness import RegistrySnapshot, TaskIngressAuthority
from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.contracts import OwnerExecutionResult
from ab_harness.environment import InProcessEnvironmentOwner
from ab_harness.lifecycle import AcceptanceFact


fixtures = runpy.run_path("tests/test_two_stage_admission.py")
FRESH_EFFECT = "fresh detector-backed result returned"


def run_case(directory, name, *, replace_catalog, observed_effects):
    compiled, catalog, environment = fixtures["_admission_fixture"]()
    proposal = fixtures["_proposal"](compiled)
    admitted = fixtures["_semantic_admission"](catalog).admit(
        compiled, proposal
    ).admitted_operation
    assert admitted is not None
    owner_catalog = catalog
    if replace_catalog:
        original = catalog.object_for("find_object")
        changed = replace(
            original,
            expected_effects=(*original.expected_effects, "direct_speech"),
            observable_success=(*original.observable_success, "direct_speech"),
        )
        owner_catalog = BindingCatalog(
            RegistrySnapshot(
                (changed,), source="synthetic:post-admission", version="changed"
            ),
            catalog.bindings_for("find_object"),
        )
    path = Path(directory) / (name + ".jsonl")
    ledger = LifecycleLedger(path)
    TaskIngressAuthority(
        environment_profile_id=environment.attestation.environment_profile_id,
        domain_contract_pack=fixtures["_domain_pack_for_compiled"](compiled),
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
    lease = DomainLifecycleAdmission(
        environment_run=environment,
        environment_id="nao_fake",
        lifecycle_ledger=ledger,
    ).request_execution(admitted).execution_lease
    assert lease is not None
    result = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment,
        catalog=owner_catalog,
        lifecycle_ledger=ledger,
        handlers={
            "fake_nao.skills:find_object": lambda _arguments: OwnerExecutionResult(
                evidence_ref="synthetic:" + name,
                succeeded=True,
                observed_effects=observed_effects,
            )
        },
    ).execute(lease)
    if result.receipt is not None:
        acceptance = TaskAcceptanceEvaluator().evaluate(
            compiled.effect_obligations, (result.receipt.evidence,)
        )
        ledger.record(AcceptanceFact(compiled, (result.receipt.evidence,), acceptance))
    replay = LifecycleLedger(path).replay(compiled.trace_id)
    print(json.dumps({
        "scenario": name,
        "binding_unchanged": owner_catalog.bindings_for("find_object")
        == catalog.bindings_for("find_object"),
        "prohibited": compiled.prohibited_effects,
        "observed": observed_effects,
        "evidence_accepted": result.accepted,
        "evidence_rejection": result.rejection.reason_codes if result.rejection else [],
        "terminal_after_restart": replay.terminal_status,
        "failure_stage_after_restart": replay.failure_stage,
    }))


with tempfile.TemporaryDirectory(prefix="uah-r2-post-admission-") as directory:
    run_case(
        directory, "catalog_replaced_after_valid_admission",
        replace_catalog=True, observed_effects=(FRESH_EFFECT, "direct_speech"),
    )
    run_case(
        directory, "original_catalog_undeclared_effect_control",
        replace_catalog=False, observed_effects=(FRESH_EFFECT, "direct_speech"),
    )
    run_case(
        directory, "untouched_success_control",
        replace_catalog=False, observed_effects=(FRESH_EFFECT,),
    )
