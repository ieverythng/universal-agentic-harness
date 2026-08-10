"""Quarantined, failure-aware trace retrieval for the Neural Workbench seam."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json


@dataclass(frozen=True)
class TraceExperience:
    """One immutable qualification experience available to retrieval."""

    trace_id: str
    task_id: str
    configuration_id: str
    registry_version: str
    object_ids: tuple[str, ...]
    outcome: str
    failure_stage: str | None = None
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.outcome not in {'success', 'failure'}:
            raise ValueError('experience outcome must be success or failure')
        if self.outcome == 'failure' and not self.failure_stage:
            raise ValueError('failed experience must declare a failure stage')
        if self.outcome == 'success' and self.failure_stage:
            raise ValueError('successful experience cannot declare a failure stage')
        if not self.object_ids:
            raise ValueError('experience must reference at least one AB object')


@dataclass(frozen=True)
class WorkbenchContextCandidate:
    """Untrusted retrieval result that cannot promote itself."""

    candidate_id: str
    query_object_ids: tuple[str, ...]
    supporting: tuple[TraceExperience, ...]
    counterexamples: tuple[TraceExperience, ...]
    gaps: tuple[str, ...]
    status: str = field(default='candidate', init=False)

    @property
    def supporting_trace_ids(self) -> tuple[str, ...]:
        return tuple(item.trace_id for item in self.supporting)

    @property
    def counterexample_trace_ids(self) -> tuple[str, ...]:
        return tuple(item.trace_id for item in self.counterexamples)

    @property
    def registry_versions(self) -> tuple[str, ...]:
        return tuple(
            sorted({item.registry_version for item in self._experiences})
        )

    @property
    def configuration_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted({item.configuration_id for item in self._experiences})
        )

    @property
    def _experiences(self) -> tuple[TraceExperience, ...]:
        return self.supporting + self.counterexamples

    def to_context_payload(self) -> dict[str, object]:
        return {
            'candidate_id': self.candidate_id,
            'status': self.status,
            'query_object_ids': list(self.query_object_ids),
            'supporting_traces': [
                _experience_payload(item) for item in self.supporting
            ],
            'counterexamples': [
                _experience_payload(item) for item in self.counterexamples
            ],
            'gaps': list(self.gaps),
            'registry_versions': list(self.registry_versions),
            'configuration_ids': list(self.configuration_ids),
        }


class WorkbenchMemory:
    """Immutable collection that proposes bounded context candidates."""

    def __init__(self, experiences: tuple[TraceExperience, ...]) -> None:
        trace_ids = tuple(item.trace_id for item in experiences)
        if len(trace_ids) != len(set(trace_ids)):
            raise ValueError('duplicate Workbench trace id')
        self._experiences = experiences

    def with_experience(self, experience: TraceExperience) -> 'WorkbenchMemory':
        return WorkbenchMemory(self._experiences + (experience,))

    def propose_context(
        self,
        *,
        query_object_ids: tuple[str, ...],
        per_outcome_limit: int = 2,
    ) -> WorkbenchContextCandidate:
        query = tuple(dict.fromkeys(query_object_ids))
        if not query:
            raise ValueError('at least one query object is required')
        if per_outcome_limit <= 0:
            raise ValueError('per-outcome retrieval limit must be positive')

        supporting = self._ranked(
            query,
            outcome='success',
            limit=per_outcome_limit,
        )
        counterexamples = self._ranked(
            query,
            outcome='failure',
            limit=per_outcome_limit,
        )
        gaps = []
        if not supporting:
            gaps.append('no supporting traces retrieved')
        if not counterexamples:
            gaps.append('no counterexamples retrieved')

        identity = {
            'query_object_ids': query,
            'supporting_trace_ids': tuple(item.trace_id for item in supporting),
            'counterexample_trace_ids': tuple(
                item.trace_id for item in counterexamples
            ),
        }
        digest = hashlib.sha256(
            json.dumps(identity, sort_keys=True).encode('utf-8')
        ).hexdigest()
        return WorkbenchContextCandidate(
            candidate_id='workbench-context:' + digest,
            query_object_ids=query,
            supporting=supporting,
            counterexamples=counterexamples,
            gaps=tuple(gaps),
        )

    def _ranked(
        self,
        query: tuple[str, ...],
        *,
        outcome: str,
        limit: int,
    ) -> tuple[TraceExperience, ...]:
        query_set = frozenset(query)
        matches = []
        for experience in self._experiences:
            if experience.outcome != outcome:
                continue
            object_ids = frozenset(experience.object_ids)
            overlap = len(query_set & object_ids)
            if not overlap:
                continue
            union = len(query_set | object_ids)
            matches.append((overlap, overlap / union, experience))
        matches.sort(key=lambda item: (-item[0], -item[1], item[2].trace_id))
        return tuple(item[2] for item in matches[:limit])


def _experience_payload(experience: TraceExperience) -> dict[str, object]:
    payload: dict[str, object] = {
        'trace_id': experience.trace_id,
        'task_id': experience.task_id,
        'evidence_refs': list(experience.evidence_refs),
    }
    if experience.failure_stage:
        payload['failure_stage'] = experience.failure_stage
    return payload
