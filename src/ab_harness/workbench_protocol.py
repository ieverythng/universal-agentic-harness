"""Transport-neutral contracts for the optional Neural Workbench engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from typing import Protocol


CURRENT_WORKBENCH_PROTOCOL = 'uah.workbench.v1'


class WorkbenchProtocolMismatch(RuntimeError):
    """Raised when an engine cannot safely participate in the configured mode."""


@dataclass(frozen=True)
class WorkbenchProtocolDescriptor:
    protocol_version: str
    engine_version: str
    source_revision: str
    capabilities: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text(
            protocol_version=self.protocol_version,
            engine_version=self.engine_version,
            source_revision=self.source_revision,
        )


@dataclass(frozen=True)
class WorkbenchRequest:
    """One bounded candidate-search request issued by a harness host."""

    protocol_version: str
    request_id: str
    configuration_id: str
    task_id: str
    frame_id: str
    registry_version: str
    projected_object_ids: tuple[str, ...]
    current_candidates: tuple[dict, ...] = ()
    constraints: dict = field(default_factory=dict)
    search_budget: int = 1

    def __post_init__(self) -> None:
        _require_text(
            protocol_version=self.protocol_version,
            request_id=self.request_id,
            configuration_id=self.configuration_id,
            task_id=self.task_id,
            frame_id=self.frame_id,
            registry_version=self.registry_version,
        )
        if not self.projected_object_ids:
            raise ValueError('Workbench request requires projected AB objects')
        if self.search_budget <= 0:
            raise ValueError('Workbench search budget must be positive')
        _require_json(self.to_dict())

    @property
    def content_id(self) -> str:
        payload = json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(',', ':'),
        ).encode('utf-8')
        return 'workbench-request:sha256:' + hashlib.sha256(payload).hexdigest()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict) -> 'WorkbenchRequest':
        return cls(
            protocol_version=str(payload.get('protocol_version', '')),
            request_id=str(payload.get('request_id', '')),
            configuration_id=str(payload.get('configuration_id', '')),
            task_id=str(payload.get('task_id', '')),
            frame_id=str(payload.get('frame_id', '')),
            registry_version=str(payload.get('registry_version', '')),
            projected_object_ids=tuple(payload.get('projected_object_ids', ())),
            current_candidates=tuple(
                dict(item) for item in payload.get('current_candidates', ())
            ),
            constraints=dict(payload.get('constraints', {})),
            search_budget=int(payload.get('search_budget', 1)),
        )


@dataclass(frozen=True)
class WorkbenchCandidate:
    """Untrusted pulse candidate returned by a Workbench engine."""

    candidate_id: str
    pulse_program: dict
    verification: dict
    scores: dict
    provenance: dict
    status: str = field(default='candidate', init=False)

    def __post_init__(self) -> None:
        _require_text(candidate_id=self.candidate_id)
        _require_json(self.to_dict())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict) -> 'WorkbenchCandidate':
        return cls(
            candidate_id=str(payload.get('candidate_id', '')),
            pulse_program=dict(payload.get('pulse_program', {})),
            verification=dict(payload.get('verification', {})),
            scores=dict(payload.get('scores', {})),
            provenance=dict(payload.get('provenance', {})),
        )


@dataclass(frozen=True)
class WorkbenchCandidateBatch:
    """Versioned candidate response; its recommendation has no execution authority."""

    protocol_version: str
    request_id: str
    engine_version: str
    source_revision: str
    candidates: tuple[WorkbenchCandidate, ...]
    recommended_candidate_id: str = ''
    activation_mode: str = 'shadow'

    def __post_init__(self) -> None:
        _require_text(
            protocol_version=self.protocol_version,
            request_id=self.request_id,
            engine_version=self.engine_version,
            source_revision=self.source_revision,
        )
        if self.activation_mode not in {'shadow', 'gated'}:
            raise ValueError('invalid Workbench activation mode')
        candidate_ids = {item.candidate_id for item in self.candidates}
        if len(candidate_ids) != len(self.candidates):
            raise ValueError('candidate batch contains a duplicate candidate ID')
        if self.recommended_candidate_id not in candidate_ids and self.recommended_candidate_id:
            raise ValueError('recommended candidate does not resolve in candidate batch')
        _require_json(self.to_dict())

    def to_dict(self) -> dict:
        return {
            'protocol_version': self.protocol_version,
            'request_id': self.request_id,
            'engine_version': self.engine_version,
            'source_revision': self.source_revision,
            'candidates': [item.to_dict() for item in self.candidates],
            'recommended_candidate_id': self.recommended_candidate_id,
            'activation_mode': self.activation_mode,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> 'WorkbenchCandidateBatch':
        return cls(
            protocol_version=str(payload.get('protocol_version', '')),
            request_id=str(payload.get('request_id', '')),
            engine_version=str(payload.get('engine_version', '')),
            source_revision=str(payload.get('source_revision', '')),
            candidates=tuple(
                WorkbenchCandidate.from_dict(item)
                for item in payload.get('candidates', ())
            ),
            recommended_candidate_id=str(
                payload.get('recommended_candidate_id', '')
            ),
            activation_mode=str(payload.get('activation_mode', 'shadow')),
        )


@dataclass(frozen=True)
class WorkbenchObservation:
    """Immutable UAH evidence supplied to the Workbench after a lifecycle run."""

    protocol_version: str
    trace_id: str
    configuration_id: str
    registry_version: str
    events: tuple[dict, ...]
    outcome: str
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_text(
            protocol_version=self.protocol_version,
            trace_id=self.trace_id,
            configuration_id=self.configuration_id,
            registry_version=self.registry_version,
            outcome=self.outcome,
        )
        if not self.events:
            raise ValueError('Workbench observation requires lifecycle events')
        _require_json(self.to_dict())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict) -> 'WorkbenchObservation':
        return cls(
            protocol_version=str(payload.get('protocol_version', '')),
            trace_id=str(payload.get('trace_id', '')),
            configuration_id=str(payload.get('configuration_id', '')),
            registry_version=str(payload.get('registry_version', '')),
            events=tuple(dict(item) for item in payload.get('events', ())),
            outcome=str(payload.get('outcome', '')),
            evidence_refs=tuple(payload.get('evidence_refs', ())),
        )


class WorkbenchEnginePort(Protocol):
    """Host-independent interface implemented by Neural Workbench engines."""

    def describe(self) -> WorkbenchProtocolDescriptor: ...

    def propose(self, request: WorkbenchRequest) -> WorkbenchCandidateBatch: ...

    def observe(self, observation: WorkbenchObservation) -> None: ...


class InProcessWorkbenchAdapter:
    """Reference in-process transport with a fail-closed version handshake."""

    def __init__(
        self,
        engine: WorkbenchEnginePort,
        *,
        supported_protocols: tuple[str, ...] = (CURRENT_WORKBENCH_PROTOCOL,),
        allow_unsafe_protocol: bool = False,
    ) -> None:
        self._engine = engine
        self.descriptor = engine.describe()
        if self.descriptor.protocol_version in supported_protocols:
            self.compatibility_state = 'compatible'
            return
        if not allow_unsafe_protocol:
            raise WorkbenchProtocolMismatch(
                'unsupported Neural Workbench protocol: '
                + self.descriptor.protocol_version
            )
        self.compatibility_state = 'degraded_observation_only'

    def propose(self, request: WorkbenchRequest) -> WorkbenchCandidateBatch:
        if self.compatibility_state != 'compatible':
            raise WorkbenchProtocolMismatch(
                'protocol override is observation-only; proposal is disabled'
            )
        if 'propose' not in self.descriptor.capabilities:
            raise WorkbenchProtocolMismatch(
                'attached Neural Workbench does not support proposals'
            )
        if request.protocol_version != self.descriptor.protocol_version:
            raise WorkbenchProtocolMismatch(
                'request protocol does not match attached Neural Workbench'
            )
        batch = self._engine.propose(request)
        if batch.protocol_version != self.descriptor.protocol_version:
            raise WorkbenchProtocolMismatch(
                'candidate response protocol does not match attached Neural Workbench'
            )
        if batch.request_id != request.request_id:
            raise WorkbenchProtocolMismatch(
                'candidate response request ID does not match the request'
            )
        return batch

    def observe(self, observation: WorkbenchObservation) -> None:
        if 'observe' not in self.descriptor.capabilities:
            raise WorkbenchProtocolMismatch(
                'attached Neural Workbench does not support observations'
            )
        self._engine.observe(observation)


def _require_text(**values: str) -> None:
    missing = [name for name, value in values.items() if not str(value).strip()]
    if missing:
        raise ValueError('Workbench fields must not be empty: ' + ', '.join(missing))


def _require_json(payload: dict) -> None:
    try:
        json.dumps(payload, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError('Workbench payload must be JSON-serializable') from error
