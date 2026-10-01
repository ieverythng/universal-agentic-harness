from pathlib import Path

from ab_harness import ABImplementationBinding
from ab_harness import BindingCatalog
from ab_harness import EnvironmentIngress
from ab_harness import EnvironmentProfile
from ab_harness import EnvironmentProfileRegistry
from ab_harness import EnvironmentRunAttestation
from ab_harness import EnvironmentRunRegistry
from ab_harness import InProcessEnvironmentOwner
from ab_harness import OwnerExecutionResult
from ab_harness import RegistrySnapshot
from ab_harness import TaskBudgets
from ab_harness import TaskEffectRequest
from ab_harness.lifecycle import LifecycleLedger
from ab_harness_nao.qualification import NaoQualificationCase
from ab_harness_nao.qualification import RecordedNaoQualificationHarness
from ab_harness_nao.qualification import nao_qualification_domain_contract_pack


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "tests" / "fixtures" / "ab_registry.json"


def _environment(handler):
    registry = RegistrySnapshot.from_json_file(REGISTRY)
    binding = ABImplementationBinding(
        binding_id="nao_fake.find_object.v1",
        object_id="find_object",
        environment_id="nao_fake",
        implementation_owner="object_finder",
        interface_kind="python_method",
        locator="fake_nao.skills:find_object",
        source_revision="fixture-rev-1",
        input_schema_ref="schema://find_object/input/v1",
        output_schema_ref="schema://find_object/result/v1",
        evidence_adapter="fake_nao.evidence:fresh_detection",
        runtime_modes=("fake",),
        status="approved",
    )
    catalog = BindingCatalog(registry, (binding,))
    domain_pack = nao_qualification_domain_contract_pack(registry)
    profile = EnvironmentProfile(
        environment_profile_id="environment-profile:nao-recorded:v1",
        domain_contract_pack_id="domain-pack:nao-recorded-qualification:v1",
        domain_contract_pack_revision=domain_pack.revision,
        native_runtime_revision="nao-recorded-runtime:v1",
        environment_owner_id="nao_fake.lifecycle_owner",
        required_interface_ids=("find_object",),
    )
    environment_run = EnvironmentRunRegistry(
        EnvironmentProfileRegistry((profile,))
    ).register(
        EnvironmentRunAttestation(
            environment_run_id="environment-run:nao-recorded:001",
            environment_profile_id=profile.environment_profile_id,
            domain_contract_pack_revision=profile.domain_contract_pack_revision,
            native_runtime_revision=profile.native_runtime_revision,
            environment_owner_id=profile.environment_owner_id,
            attestation_id="environment-attestation:nao-recorded:001",
            started_at="2026-09-28T10:00:00Z",
            readiness_evidence_refs=("artifact:nao-recorded-readiness:001",),
        )
    )
    lifecycle_ledger = LifecycleLedger(clock=lambda: "2026-09-28T10:00:01Z")
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        environment_run=environment_run,
        catalog=catalog,
        handlers={binding.locator: handler},
        lifecycle_ledger=lifecycle_ledger,
    )
    return registry, catalog, environment_run, owner, lifecycle_ledger, domain_pack


def _case() -> NaoQualificationCase:
    return NaoQualificationCase(
        case_id="nao-find-cup-001",
        task_id="find_the_cup",
        requested_effects=(
            TaskEffectRequest(
                obligation_id="target_observed",
                effect_id="fresh detector-backed result returned",
                requirement="required",
            ),
        ),
        goal="find the cup",
        budgets=TaskBudgets(wall_time_seconds=60, model_calls=0, tool_calls=4),
    )


def _ingress(environment_run, case):
    return EnvironmentIngress(
        environment_ingress_id="ingress:recorded:%s" % case.case_id,
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:nao.recorded_qualification:v1",
        ingress_type="recorded_user_request",
        payload_artifact_id="artifact:recorded-request:%s" % case.case_id,
        native_lineage=(("task_id", case.task_id),),
        observed_at="2026-09-28T10:00:01Z",
    )


CHATBOT_HANDOFF = {
    "route": "execution",
    "verbal_ack": "I will look for the cup.",
    "user_intent": {"type": "find_object", "goal_text": "find the cup"},
}
PLANNER_FIND = {
    "plan": {
        "steps": [
            {
                "id": "step_1",
                "type": "skill",
                "name": "find_object",
                "args": {"label": "cup"},
            }
        ]
    }
}


def test_recorded_nao_case_closes_chatbot_planner_gate_and_owner_evidence():
    def find_object(arguments):
        return OwnerExecutionResult(
            evidence_ref="fake-nao://evidence/detection-001",
            succeeded=True,
            observed_effects=("fresh detector-backed result returned",),
            payload={"canonical_target_id": "cup_01", "arguments": arguments},
        )

    registry, catalog, environment_run, environment, ledger, domain_pack = _environment(
        find_object
    )
    harness = RecordedNaoQualificationHarness(
        registry,
        catalog,
        environment_run,
        environment,
        ledger,
        domain_pack,
    )
    case = _case()

    result = harness.run(
        case=case,
        ingress=_ingress(environment_run, case),
        chatbot_payload=CHATBOT_HANDOFF,
        planner_payload=PLANNER_FIND,
        runtime_mode="fake",
    )

    assert result.passed is True
    assert result.failure_stage is None
    assert result.chatbot_gate.accepted is True
    assert result.planner_admitted is True
    assert result.closed_observables == ("fresh detector-backed result returned",)
    assert result.evidence[0].owner == "object_finder"


def test_rejected_planner_proposal_never_reaches_environment_owner():
    calls = []

    def find_object(arguments):
        calls.append(arguments)
        raise AssertionError("rejected proposal must not dispatch")

    registry, catalog, environment_run, environment, ledger, domain_pack = _environment(
        find_object
    )
    harness = RecordedNaoQualificationHarness(
        registry,
        catalog,
        environment_run,
        environment,
        ledger,
        domain_pack,
    )
    planner_payload = {
        "plan": {
            "steps": [{"id": "step_1", "type": "skill", "name": "walk_to", "args": {}}]
        }
    }

    case = _case()
    result = harness.run(
        case=case,
        ingress=_ingress(environment_run, case),
        chatbot_payload=CHATBOT_HANDOFF,
        planner_payload=planner_payload,
        runtime_mode="fake",
    )

    assert result.passed is False
    assert result.failure_stage == "semantic_admission"
    assert result.planner_admitted is False
    assert result.planner_reasons == (
        "object_outside_projection",
        "missing_effect_obligation",
    )
    assert result.evidence == ()
    assert calls == []


def test_failed_owner_result_does_not_close_terminal_observable():
    def find_object(_arguments):
        return OwnerExecutionResult(
            evidence_ref="fake-nao://evidence/detection-failed-001",
            succeeded=False,
            observed_effects=(),
            payload={"reason": "detector timeout"},
        )

    registry, catalog, environment_run, environment, ledger, domain_pack = _environment(
        find_object
    )
    harness = RecordedNaoQualificationHarness(
        registry,
        catalog,
        environment_run,
        environment,
        ledger,
        domain_pack,
    )

    case = _case()
    result = harness.run(
        case=case,
        ingress=_ingress(environment_run, case),
        chatbot_payload=CHATBOT_HANDOFF,
        planner_payload=PLANNER_FIND,
        runtime_mode="fake",
    )

    assert result.passed is False
    assert result.failure_stage == "evidence_closure"
    assert result.missing_observables == ("fresh detector-backed result returned",)


def test_recorded_owner_evidence_produces_explicit_task_acceptance():
    def find_object(_arguments):
        return OwnerExecutionResult(
            evidence_ref="fake-nao://evidence/detection-acceptance-001",
            succeeded=True,
            observed_effects=("fresh detector-backed result returned",),
        )

    registry, catalog, environment_run, environment, ledger, domain_pack = _environment(
        find_object
    )
    harness = RecordedNaoQualificationHarness(
        registry,
        catalog,
        environment_run,
        environment,
        ledger,
        domain_pack,
    )
    case = NaoQualificationCase(
        case_id="nao-find-cup-acceptance-001",
        task_id="find_the_cup",
        requested_effects=(
            TaskEffectRequest(
                obligation_id="target_observed",
                effect_id="fresh detector-backed result returned",
                requirement="required",
            ),
        ),
        goal="find the cup",
        budgets=TaskBudgets(wall_time_seconds=60, model_calls=0, tool_calls=4),
    )

    result = harness.run(
        case=case,
        ingress=_ingress(environment_run, case),
        chatbot_payload=CHATBOT_HANDOFF,
        planner_payload=PLANNER_FIND,
        runtime_mode="fake",
    )

    assert result.acceptance is not None
    assert result.acceptance.status == "accepted"


def test_malformed_planner_step_rejects_the_whole_plan_before_dispatch():
    calls = []

    def find_object(arguments):
        calls.append(arguments)
        raise AssertionError("malformed plan must not dispatch")

    registry, catalog, environment_run, environment, ledger, domain_pack = _environment(
        find_object
    )
    harness = RecordedNaoQualificationHarness(
        registry,
        catalog,
        environment_run,
        environment,
        ledger,
        domain_pack,
    )
    case = _case()
    malformed = {
        "plan": {
            "steps": [
                PLANNER_FIND["plan"]["steps"][0],
                {"id": "step_2", "type": "skill", "name": 42, "args": {}},
            ]
        }
    }

    result = harness.run(
        case=case,
        ingress=_ingress(environment_run, case),
        chatbot_payload=CHATBOT_HANDOFF,
        planner_payload=malformed,
        runtime_mode="fake",
    )

    assert result.failure_stage == "proposal_normalization"
    assert result.planner_reasons == (
        "planner step step_2 requires a string skill name",
    )
    assert calls == []


def test_all_operations_are_semantically_admitted_before_any_dispatch():
    calls = []

    def find_object(arguments):
        calls.append(arguments)
        raise AssertionError("partially admitted plan must not dispatch")

    registry, catalog, environment_run, environment, ledger, domain_pack = _environment(
        find_object
    )
    harness = RecordedNaoQualificationHarness(
        registry,
        catalog,
        environment_run,
        environment,
        ledger,
        domain_pack,
    )
    case = _case()
    partially_valid = {
        "plan": {
            "steps": [
                PLANNER_FIND["plan"]["steps"][0],
                {
                    "id": "step_2",
                    "type": "skill",
                    "name": "walk_to",
                    "args": {"location": "kitchen"},
                },
            ]
        }
    }

    result = harness.run(
        case=case,
        ingress=_ingress(environment_run, case),
        chatbot_payload=CHATBOT_HANDOFF,
        planner_payload=partially_valid,
        runtime_mode="fake",
    )

    assert result.failure_stage == "semantic_admission"
    assert result.planner_admitted is False
    assert calls == []


def test_unsupported_step_semantics_are_not_silently_flattened():
    calls = []

    def find_object(arguments):
        calls.append(arguments)
        raise AssertionError("unsupported step semantics must not dispatch")

    registry, catalog, environment_run, environment, ledger, domain_pack = _environment(
        find_object
    )
    harness = RecordedNaoQualificationHarness(
        registry,
        catalog,
        environment_run,
        environment,
        ledger,
        domain_pack,
    )
    case = _case()
    step_with_hidden_dependency = {
        "plan": {
            "steps": [
                {
                    **PLANNER_FIND["plan"]["steps"][0],
                    "requires": ["step_0"],
                }
            ]
        }
    }

    result = harness.run(
        case=case,
        ingress=_ingress(environment_run, case),
        chatbot_payload=CHATBOT_HANDOFF,
        planner_payload=step_with_hidden_dependency,
        runtime_mode="fake",
    )

    assert result.failure_stage == "proposal_normalization"
    assert result.planner_reasons == ("planner step 0 contains unsupported fields",)
    assert calls == []
