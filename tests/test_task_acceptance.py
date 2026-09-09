from ab_harness import EffectEvidence
from ab_harness import EffectObligation
from ab_harness import TaskAcceptanceEvaluator


def _evidence(
    *,
    evidence_ref: str,
    object_id: str,
    owner: str,
    succeeded: bool,
    observed_effects: tuple[str, ...] = (),
) -> EffectEvidence:
    return EffectEvidence(
        evidence_ref=evidence_ref,
        object_id=object_id,
        binding_id=f"nao_fake.{object_id}.v1",
        environment_id="nao_fake",
        owner=owner,
        succeeded=succeeded,
        observed_effects=observed_effects,
    )


def test_best_effort_failure_preserves_required_effect_acceptance():
    obligations = (
        EffectObligation(
            obligation_id="target_observed",
            effect_id="fresh detector-backed result returned",
            object_id="find_object",
            evidence_owner="object_finder",
            requirement="required",
            failure_policy="terminal",
        ),
        EffectObligation(
            obligation_id="report_spoken",
            effect_id="speech action completed",
            object_id="report_result",
            evidence_owner="communication_skills",
            requirement="best_effort",
            failure_policy="terminal",
        ),
    )
    evidence = (
        _evidence(
            evidence_ref="fake-nao://evidence/detection-001",
            object_id="find_object",
            owner="object_finder",
            succeeded=True,
            observed_effects=("fresh detector-backed result returned",),
        ),
        _evidence(
            evidence_ref="fake-nao://evidence/report-failed-001",
            object_id="report_result",
            owner="communication_skills",
            succeeded=False,
        ),
    )

    acceptance = TaskAcceptanceEvaluator().evaluate(obligations, evidence)

    assert acceptance.status == "accepted_with_deficit"
    assert acceptance.satisfied_obligation_ids == ("target_observed",)
    assert acceptance.deficit_obligation_ids == ("report_spoken",)
