from pathlib import Path

from ab_harness import ABImplementationBinding
from ab_harness import BindingCatalog
from ab_harness import InProcessEnvironmentOwner
from ab_harness import OwnerExecutionResult
from ab_harness import RegistrySnapshot
from ab_harness.qualification import QualificationCase
from ab_harness.qualification import RecordedNaoQualificationHarness


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
    owner = InProcessEnvironmentOwner(
        environment_id="nao_fake",
        catalog=BindingCatalog(registry, (binding,)),
        handlers={binding.locator: handler},
    )
    return registry, owner


def _case() -> QualificationCase:
    return QualificationCase(
        case_id="nao-find-cup-001",
        task_id="find_the_cup",
        requested_object_ids=("find_object",),
        required_observables=("fresh detector-backed result returned",),
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

    registry, environment = _environment(find_object)
    harness = RecordedNaoQualificationHarness(registry, environment)

    result = harness.run(
        case=_case(),
        chatbot_payload=CHATBOT_HANDOFF,
        planner_payload=PLANNER_FIND,
        runtime_mode="fake",
    )

    assert result.passed is True
    assert result.failure_stage is None
    assert result.chatbot_gate.accepted is True
    assert result.planner_gate.accepted is True
    assert result.closed_observables == (
        "fresh detector-backed result returned",
    )
    assert result.evidence[0].owner == "object_finder"


def test_rejected_planner_proposal_never_reaches_environment_owner():
    calls = []

    def find_object(arguments):
        calls.append(arguments)
        raise AssertionError("rejected proposal must not dispatch")

    registry, environment = _environment(find_object)
    harness = RecordedNaoQualificationHarness(registry, environment)
    planner_payload = {
        "plan": {
            "steps": [
                {"id": "step_1", "type": "skill", "name": "walk_to", "args": {}}
            ]
        }
    }

    result = harness.run(
        case=_case(),
        chatbot_payload=CHATBOT_HANDOFF,
        planner_payload=planner_payload,
        runtime_mode="fake",
    )

    assert result.passed is False
    assert result.failure_stage == "planner_gate"
    assert result.planner_gate.accepted is False
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

    registry, environment = _environment(find_object)
    harness = RecordedNaoQualificationHarness(registry, environment)

    result = harness.run(
        case=_case(),
        chatbot_payload=CHATBOT_HANDOFF,
        planner_payload=PLANNER_FIND,
        runtime_mode="fake",
    )

    assert result.passed is False
    assert result.failure_stage == "evidence_closure"
    assert result.missing_observables == (
        "fresh detector-backed result returned",
    )
