"""Portable contracts for an AB-grounded agent interaction."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class AbstractionFrame:
    frame_id: str
    substrate: str
    atomicity_rule: str
    registry_version: str


@dataclass(frozen=True)
class ABControlBand:
    min_direct_level: int
    preferred_level: int
    max_direct_level: int
    inspect_down_to_level: int = 0

    def __post_init__(self) -> None:
        if not (
            self.inspect_down_to_level
            <= self.min_direct_level
            <= self.preferred_level
            <= self.max_direct_level
        ):
            raise ValueError('invalid AB control band ordering')

    def admits_direct(self, level: int) -> bool:
        return self.min_direct_level <= level <= self.max_direct_level

    def admits_inspection(self, level: int) -> bool:
        return self.inspect_down_to_level <= level <= self.max_direct_level


@dataclass(frozen=True)
class AgentRoleSpec:
    role_id: str
    allowed_output_types: tuple[str, ...]
    control_band: ABControlBand
    may_claim_effects: bool = False


@dataclass(frozen=True)
class ABObjectView:
    object_id: str
    ab_level: int
    kind: str
    category: str
    owner_package: str
    expected_effects: tuple[str, ...] = ()
    observable_success: tuple[str, ...] = ()
    decomposes_to: tuple[str, ...] = ()
    runtime_callable: bool = False


@dataclass(frozen=True)
class ABImplementationBinding:
    """Versioned pointer from one semantic AB object to an environment API."""

    binding_id: str
    object_id: str
    environment_id: str
    implementation_owner: str
    interface_kind: str
    locator: str
    source_revision: str
    input_schema_ref: str
    output_schema_ref: str
    evidence_adapter: str
    runtime_modes: tuple[str, ...]
    status: str = 'candidate'

    def __post_init__(self) -> None:
        required = {
            'binding_id': self.binding_id,
            'object_id': self.object_id,
            'environment_id': self.environment_id,
            'implementation_owner': self.implementation_owner,
            'interface_kind': self.interface_kind,
            'locator': self.locator,
            'source_revision': self.source_revision,
        }
        missing = tuple(name for name, value in required.items() if not value.strip())
        if missing:
            raise ValueError('binding fields must not be empty: %s' % ', '.join(missing))
        if self.status not in {'candidate', 'approved', 'disabled'}:
            raise ValueError('invalid binding status: %s' % self.status)
        if not self.runtime_modes:
            raise ValueError('binding must declare at least one runtime mode')


@dataclass(frozen=True)
class InteractionModuleSpec:
    task_id: str
    role: AgentRoleSpec
    frame: AbstractionFrame
    objects: tuple[ABObjectView, ...]
    registry_source: str

    @property
    def object_ids(self) -> frozenset[str]:
        return frozenset(item.object_id for item in self.objects)

    def object_for(self, object_id: str) -> ABObjectView | None:
        return next((item for item in self.objects if item.object_id == object_id), None)


@dataclass(frozen=True)
class AgentOutput:
    output_type: str
    payload: dict[str, Any]
    referenced_objects: tuple[str, ...] = ()
    claimed_effects: tuple[str, ...] = ()


@dataclass(frozen=True)
class GateDecision:
    accepted: bool
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OwnerExecutionResult:
    """Raw result issued by the environment component that owns an effect."""

    evidence_ref: str
    succeeded: bool
    observed_effects: tuple[str, ...]
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EffectEvidence:
    """Normalized evidence linked to the binding that produced it."""

    evidence_ref: str
    object_id: str
    binding_id: str
    environment_id: str
    owner: str
    succeeded: bool
    observed_effects: tuple[str, ...]
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EffectObligation:
    """One task effect that must be judged from owner-issued evidence."""

    obligation_id: str
    effect_id: str
    object_id: str
    evidence_owner: str
    requirement: str
    failure_policy: str

    def __post_init__(self) -> None:
        required = {
            'obligation_id': self.obligation_id,
            'effect_id': self.effect_id,
            'object_id': self.object_id,
            'evidence_owner': self.evidence_owner,
        }
        missing = tuple(name for name, value in required.items() if not value.strip())
        if missing:
            raise ValueError(
                'effect obligation fields must not be empty: %s' % ', '.join(missing)
            )
        if self.requirement not in {'required', 'best_effort'}:
            raise ValueError('invalid effect obligation requirement: %s' % self.requirement)
        if self.failure_policy not in {'terminal', 'retryable'}:
            raise ValueError(
                'invalid effect obligation failure policy: %s' % self.failure_policy
            )


@dataclass(frozen=True)
class TaskAcceptance:
    """Deterministic task judgment over a frozen obligation set."""

    status: str
    satisfied_obligation_ids: tuple[str, ...] = ()
    deficit_obligation_ids: tuple[str, ...] = ()
    pending_obligation_ids: tuple[str, ...] = ()
    failed_obligation_ids: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class HarnessTrace:
    trace_id: str
    task_id: str
    role_id: str
    frame_id: str
    registry_version: str
    projected_object_ids: tuple[str, ...]
    output_type: str
    referenced_objects: tuple[str, ...]
    gate: GateDecision
    evidence_refs: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> 'HarnessTrace':
        gate = payload.get('gate', {})
        return cls(
            trace_id=str(payload['trace_id']),
            task_id=str(payload['task_id']),
            role_id=str(payload['role_id']),
            frame_id=str(payload['frame_id']),
            registry_version=str(payload['registry_version']),
            projected_object_ids=tuple(payload.get('projected_object_ids', ())),
            output_type=str(payload['output_type']),
            referenced_objects=tuple(payload.get('referenced_objects', ())),
            gate=GateDecision(bool(gate.get('accepted')), tuple(gate.get('reasons', ()))),
            evidence_refs=tuple(payload.get('evidence_refs', ())),
            metadata=dict(payload.get('metadata', {})),
        )
