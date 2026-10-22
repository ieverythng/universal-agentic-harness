import pytest

from ab_harness.workbench import TraceExperience
from ab_harness.workbench import WorkbenchContextCandidate
from ab_harness.workbench import WorkbenchMemory


def _experience(
    trace_id: str,
    *,
    outcome: str,
    object_ids: tuple[str, ...],
    failure_stage: str | None = None,
) -> TraceExperience:
    return TraceExperience(
        trace_id=trace_id,
        task_id="find_the_cup",
        configuration_id="watson-uah-fixture-v1",
        registry_version="sha256:fixture",
        object_ids=object_ids,
        outcome=outcome,
        failure_stage=failure_stage,
        evidence_refs=(f"fixture://{trace_id}",),
    )


def test_experience_requires_failure_stage_for_failed_outcome():
    with pytest.raises(ValueError, match="failure stage"):
        _experience(
            "trace-failure-without-stage",
            outcome="failure",
            object_ids=("find_object",),
        )


def test_workbench_candidate_retrieves_support_and_counterexamples():
    memory = WorkbenchMemory(
        (
            _experience(
                "trace-success-find",
                outcome="success",
                object_ids=("find_object", "resolve_target_reference"),
            ),
            _experience(
                "trace-failure-find",
                outcome="failure",
                object_ids=("find_object",),
                failure_stage="evidence_closure",
            ),
            _experience(
                "trace-unrelated",
                outcome="failure",
                object_ids=("walk_to",),
                failure_stage="environment_owner",
            ),
        )
    )

    candidate = memory.propose_context(
        query_object_ids=("find_object",),
        per_outcome_limit=2,
    )

    assert candidate.status == "candidate"
    assert candidate.supporting_trace_ids == ("trace-success-find",)
    assert candidate.counterexample_trace_ids == ("trace-failure-find",)
    assert candidate.gaps == ()
    assert candidate.registry_versions == ("sha256:fixture",)
    assert candidate.configuration_ids == ("watson-uah-fixture-v1",)


def test_workbench_candidate_identity_is_deterministic_and_query_scoped():
    memory = WorkbenchMemory(
        (
            _experience(
                "trace-success-find",
                outcome="success",
                object_ids=("find_object",),
            ),
        )
    )

    first = memory.propose_context(query_object_ids=("find_object",))
    repeated = memory.propose_context(query_object_ids=("find_object",))
    different = memory.propose_context(query_object_ids=("walk_to",))

    assert first.candidate_id == repeated.candidate_id
    assert first.candidate_id != different.candidate_id
    assert first.gaps == ("no counterexamples retrieved",)
    assert different.gaps == (
        "no supporting traces retrieved",
        "no counterexamples retrieved",
    )


def test_workbench_context_is_structured_and_does_not_claim_promotion():
    experience = _experience(
        "trace-failure-find",
        outcome="failure",
        object_ids=("find_object",),
        failure_stage="planner_gate",
    )
    candidate = WorkbenchMemory((experience,)).propose_context(
        query_object_ids=("find_object",),
    )

    payload = candidate.to_context_payload()

    assert payload["status"] == "candidate"
    assert payload["query_object_ids"] == ["find_object"]
    assert payload["supporting_traces"] == []
    assert payload["counterexamples"] == [
        {
            "trace_id": "trace-failure-find",
            "task_id": "find_the_cup",
            "failure_stage": "planner_gate",
            "evidence_refs": ["fixture://trace-failure-find"],
        }
    ]
    assert "approved" not in payload


def test_workbench_candidate_status_cannot_be_overridden_by_a_caller():
    with pytest.raises(TypeError, match="status"):
        WorkbenchContextCandidate(
            candidate_id="candidate:test",
            query_object_ids=("find_object",),
            supporting=(),
            counterexamples=(),
            gaps=(),
            status="approved",
        )


def test_workbench_rejects_unbounded_or_empty_retrieval_requests():
    memory = WorkbenchMemory(())

    with pytest.raises(ValueError, match="query object"):
        memory.propose_context(query_object_ids=())
    with pytest.raises(ValueError, match="positive"):
        memory.propose_context(
            query_object_ids=("find_object",),
            per_outcome_limit=0,
        )
