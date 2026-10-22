import math

import pytest

from ab_harness.workbench_protocol import CURRENT_WORKBENCH_PROTOCOL
from ab_harness.workbench_protocol import InProcessWorkbenchAdapter
from ab_harness.workbench_protocol import WorkbenchCandidate
from ab_harness.workbench_protocol import WorkbenchCandidateBatch
from ab_harness.workbench_protocol import WorkbenchObservation
from ab_harness.workbench_protocol import WorkbenchProtocolDescriptor
from ab_harness.workbench_protocol import WorkbenchProtocolMismatch
from ab_harness.workbench_protocol import WorkbenchRequest


class _Engine:
    def __init__(self, *, protocol_version: str = CURRENT_WORKBENCH_PROTOCOL):
        self.protocol_version = protocol_version
        self.observations = []

    def describe(self) -> WorkbenchProtocolDescriptor:
        return WorkbenchProtocolDescriptor(
            protocol_version=self.protocol_version,
            engine_version="0.1.0",
            source_revision="fixture-revision",
            capabilities=("observe", "propose"),
        )

    def propose(self, request: WorkbenchRequest) -> WorkbenchCandidateBatch:
        candidate = WorkbenchCandidate(
            candidate_id="candidate:scan",
            pulse_program={"pulses": [{"operator": "scan"}]},
            verification={"valid": True},
            scores={"energy": 0.25},
            provenance={"source": "fixture"},
        )
        return WorkbenchCandidateBatch(
            protocol_version=self.protocol_version,
            request_id=request.request_id,
            engine_version="0.1.0",
            source_revision="fixture-revision",
            candidates=(candidate,),
            recommended_candidate_id=candidate.candidate_id,
        )

    def observe(self, observation: WorkbenchObservation) -> None:
        self.observations.append(observation)


def _request() -> WorkbenchRequest:
    return WorkbenchRequest(
        protocol_version=CURRENT_WORKBENCH_PROTOCOL,
        request_id="request:scan",
        configuration_id="configuration:bonsai-nao-v1",
        task_id="scan_room",
        frame_id="nao-planner-v1",
        registry_version="sha256:registry",
        projected_object_ids=("scan", "/planner/execution_feedback"),
        current_candidates=({"candidate_id": "model:scan"},),
        constraints={"activation_mode": "shadow"},
        search_budget=3,
    )


def _observation() -> WorkbenchObservation:
    return WorkbenchObservation(
        protocol_version=CURRENT_WORKBENCH_PROTOCOL,
        trace_id="trace:scan",
        configuration_id="configuration:bonsai-nao-v1",
        registry_version="sha256:registry",
        events=({"event_type": "gate.accepted"},),
        outcome="success",
        evidence_refs=("fixture://scan-result",),
    )


def test_workbench_request_is_serializable_and_content_addressed():
    request = _request()

    restored = WorkbenchRequest.from_dict(request.to_dict())

    assert restored == request
    assert restored.content_id == request.content_id
    assert request.content_id.startswith("workbench-request:sha256:")


def test_candidate_batch_recommendation_must_resolve():
    with pytest.raises(ValueError, match="recommended candidate"):
        WorkbenchCandidateBatch(
            protocol_version=CURRENT_WORKBENCH_PROTOCOL,
            request_id="request:scan",
            engine_version="0.1.0",
            source_revision="fixture",
            candidates=(),
            recommended_candidate_id="candidate:missing",
        )


def test_candidate_batch_rejects_duplicate_candidate_ids():
    candidate = WorkbenchCandidate(
        candidate_id="candidate:scan",
        pulse_program={},
        verification={},
        scores={},
        provenance={},
    )

    with pytest.raises(ValueError, match="duplicate candidate"):
        WorkbenchCandidateBatch(
            protocol_version=CURRENT_WORKBENCH_PROTOCOL,
            request_id="request:scan",
            engine_version="0.1.0",
            source_revision="fixture",
            candidates=(candidate, candidate),
        )


def test_transport_payload_rejects_non_finite_numbers():
    with pytest.raises(ValueError, match="JSON-serializable"):
        WorkbenchRequest(
            protocol_version=CURRENT_WORKBENCH_PROTOCOL,
            request_id="request:scan",
            configuration_id="configuration:test",
            task_id="scan_room",
            frame_id="nao-planner-v1",
            registry_version="sha256:registry",
            projected_object_ids=("scan",),
            constraints={"threshold": math.nan},
        )


def test_compatible_in_process_adapter_proposes_and_observes():
    engine = _Engine()
    adapter = InProcessWorkbenchAdapter(engine)

    batch = adapter.propose(_request())
    adapter.observe(_observation())

    assert adapter.compatibility_state == "compatible"
    assert batch.recommended_candidate_id == "candidate:scan"
    assert batch.candidates[0].status == "candidate"
    assert engine.observations[0].trace_id == "trace:scan"


def test_protocol_mismatch_fails_closed_by_default():
    with pytest.raises(WorkbenchProtocolMismatch, match="unsupported"):
        InProcessWorkbenchAdapter(_Engine(protocol_version="workbench.v999"))


def test_proposal_requires_declared_engine_capability():
    engine = _Engine()
    engine.describe = lambda: WorkbenchProtocolDescriptor(
        protocol_version=CURRENT_WORKBENCH_PROTOCOL,
        engine_version="0.1.0",
        source_revision="fixture",
        capabilities=("observe",),
    )
    adapter = InProcessWorkbenchAdapter(engine)

    with pytest.raises(WorkbenchProtocolMismatch, match="proposals"):
        adapter.propose(_request())


def test_candidate_response_must_match_request_id():
    engine = _Engine()
    original_propose = engine.propose

    def mismatched_propose(request):
        batch = original_propose(request)
        return WorkbenchCandidateBatch(
            protocol_version=batch.protocol_version,
            request_id="request:other",
            engine_version=batch.engine_version,
            source_revision=batch.source_revision,
            candidates=batch.candidates,
        )

    engine.propose = mismatched_propose
    adapter = InProcessWorkbenchAdapter(engine)

    with pytest.raises(WorkbenchProtocolMismatch, match="request ID"):
        adapter.propose(_request())


def test_development_override_is_observation_only_and_visible():
    engine = _Engine(protocol_version="workbench.v999")
    adapter = InProcessWorkbenchAdapter(
        engine,
        allow_unsafe_protocol=True,
    )

    adapter.observe(_observation())

    assert adapter.compatibility_state == "degraded_observation_only"
    assert engine.observations
    with pytest.raises(WorkbenchProtocolMismatch, match="observation-only"):
        adapter.propose(_request())
