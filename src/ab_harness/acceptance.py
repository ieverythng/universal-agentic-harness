"""Deterministic task acceptance over normalized owner evidence."""

from __future__ import annotations

from collections.abc import Iterable

from ab_harness.contracts import EffectEvidence
from ab_harness.contracts import EffectObligation
from ab_harness.contracts import TaskAcceptance


class TaskAcceptanceEvaluator:
    """Compare frozen effect obligations with normalized environment evidence."""

    def evaluate(
        self,
        effect_obligations: Iterable[EffectObligation],
        evidence_set: Iterable[EffectEvidence],
    ) -> TaskAcceptance:
        obligations = tuple(effect_obligations)
        evidence = tuple(evidence_set)
        if not obligations:
            raise ValueError('task acceptance requires at least one effect obligation')
        obligation_ids = tuple(item.obligation_id for item in obligations)
        duplicate_ids = tuple(
            dict.fromkeys(
                obligation_id
                for obligation_id in obligation_ids
                if obligation_ids.count(obligation_id) > 1
            )
        )
        if duplicate_ids:
            raise ValueError(
                'duplicate effect obligation IDs: %s' % ', '.join(duplicate_ids)
            )
        satisfied: list[str] = []
        deficits: list[str] = []
        pending: list[str] = []
        failed: list[str] = []
        considered_evidence_refs: set[str] = set()

        for obligation in obligations:
            matching_evidence = tuple(
                item
                for item in evidence
                if item.object_id == obligation.object_id
                and item.owner == obligation.evidence_owner
            )
            considered_evidence_refs.update(
                item.evidence_ref for item in matching_evidence
            )
            if any(
                item.succeeded and obligation.effect_id in item.observed_effects
                for item in matching_evidence
            ):
                satisfied.append(obligation.obligation_id)
            elif obligation.requirement == 'best_effort':
                deficits.append(obligation.obligation_id)
            elif obligation.failure_policy == 'terminal' and any(
                not item.succeeded for item in matching_evidence
            ):
                failed.append(obligation.obligation_id)
            else:
                pending.append(obligation.obligation_id)

        if failed:
            status = 'rejected'
        elif pending:
            status = 'suspended'
        elif deficits:
            status = 'accepted_with_deficit'
        else:
            status = 'accepted'
        return TaskAcceptance(
            status=status,
            satisfied_obligation_ids=tuple(satisfied),
            deficit_obligation_ids=tuple(deficits),
            pending_obligation_ids=tuple(pending),
            failed_obligation_ids=tuple(failed),
            evidence_refs=tuple(sorted(considered_evidence_refs)),
        )
