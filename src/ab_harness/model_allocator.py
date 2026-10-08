"""Exclusive fixed-instance reservation contracts for the initial H1 runtime."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timedelta, timezone
import hashlib
import json
from typing import Callable, TYPE_CHECKING

from ab_harness.agent_configuration import AgentRoleConfiguration, ModelConfiguration

if TYPE_CHECKING:
    from ab_harness.agent_configuration import (
        AgentRoleConfigurationRegistry,
        ModelConfigurationRegistry,
    )
    from ab_harness.agent_lifecycle import AgentRunReplay
    from ab_harness.lifecycle import LifecycleLedger


def _identity(prefix: str, payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    return prefix + ":sha256:" + hashlib.sha256(encoded).hexdigest()


def _text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name + " must be a nonempty string")


def _integer(value: object, name: str, *, positive: bool = False) -> None:
    if type(value) is not int or value < (1 if positive else 0):
        raise ValueError(name + " must be a finite integer within its limit")


def _time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ValueError("runtime timestamp must be an aware ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError("runtime timestamp must be an aware ISO timestamp")
    return parsed


@dataclass(frozen=True)
class FixedModelInstance:
    """One declared runtime resource with an exclusive reservation policy."""

    model_instance_id: str
    model_configuration_id: str
    host_id: str
    max_context_tokens: int
    required_ram_mib: int
    required_vram_mib: int
    readiness_owner_id: str

    def __post_init__(self) -> None:
        for name in (
            "model_instance_id",
            "model_configuration_id",
            "host_id",
            "readiness_owner_id",
        ):
            _text(getattr(self, name), name)
        _integer(self.max_context_tokens, "max_context_tokens", positive=True)
        _integer(self.required_ram_mib, "required_ram_mib")
        _integer(self.required_vram_mib, "required_vram_mib")


@dataclass(frozen=True)
class ResourceSnapshot:
    """Owner-supplied available capacity; no automatic hardware discovery."""

    snapshot_id: str
    host_id: str
    available_ram_mib: int
    available_vram_mib: int
    observed_at: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("snapshot_id", "host_id"):
            _text(getattr(self, name), name)
        _integer(self.available_ram_mib, "available_ram_mib")
        _integer(self.available_vram_mib, "available_vram_mib")
        _time(self.observed_at)
        if not isinstance(self.evidence_refs, tuple) or not self.evidence_refs:
            raise ValueError("resource snapshot requires immutable evidence references")
        for reference in self.evidence_refs:
            _text(reference, "resource evidence")


@dataclass(frozen=True)
class ModelLease:
    """A bounded exclusive reservation, distinct from domain execution authority."""

    request_id: str
    agent_run_id: str
    environment_run_id: str
    agent_id: str
    model_instance_id: str
    model_configuration_id: str
    context_tokens: int
    acquired_at: str
    expires_at: str
    model_lease_id: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "agent_run_id",
            "environment_run_id",
            "agent_id",
            "model_instance_id",
            "model_configuration_id",
        ):
            _text(getattr(self, name), name)
        _integer(self.context_tokens, "context_tokens", positive=True)
        if _time(self.expires_at) <= _time(self.acquired_at):
            raise ValueError("model lease must have a positive bounded duration")
        object.__setattr__(
            self, "model_lease_id", _identity("model-lease", self._payload())
        )

    def _payload(self) -> dict[str, object]:
        return {
            "schema_version": "uah.model_lease/v1",
            **{
                item.name: getattr(self, item.name)
                for item in fields(self)
                if item.name != "model_lease_id"
            },
        }

    def verify_identity(self) -> None:
        if self.model_lease_id != _identity("model-lease", self._payload()):
            raise ValueError("model lease identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {"model_lease_id": self.model_lease_id, **self._payload()}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> ModelLease:
        data = dict(payload)
        identity = data.pop("model_lease_id")
        if data.pop("schema_version") != "uah.model_lease/v1":
            raise ValueError("unsupported model lease schema")
        lease = cls(**data)
        if identity != lease.model_lease_id:
            raise ValueError("model lease identity does not match content")
        return lease


@dataclass(frozen=True)
class ModelAllocationDecision:
    request_id: str
    agent_run_id: str
    environment_run_id: str
    requested_at: str
    duration_seconds: int
    context_tokens: int
    instance: FixedModelInstance
    resources: ResourceSnapshot
    role: AgentRoleConfiguration
    model: ModelConfiguration
    lease: ModelLease | None
    reason_codes: tuple[str, ...]
    decision_id: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("request_id", "agent_run_id", "environment_run_id"):
            _text(getattr(self, name), name)
        _time(self.requested_at)
        _integer(self.duration_seconds, "duration_seconds", positive=True)
        _integer(self.context_tokens, "context_tokens", positive=True)
        if not isinstance(self.reason_codes, tuple):
            raise ValueError("allocation reasons must be immutable")
        if (self.lease is None) != bool(self.reason_codes):
            raise ValueError("allocation requires a lease or rejection reasons")
        object.__setattr__(
            self, "decision_id", _identity("model-allocation", self._payload())
        )

    @property
    def accepted(self) -> bool:
        return self.lease is not None

    def _payload(self) -> dict[str, object]:
        return {
            "schema_version": "uah.model_allocation_decision/v1",
            "request_id": self.request_id,
            "agent_run_id": self.agent_run_id,
            "environment_run_id": self.environment_run_id,
            "requested_at": self.requested_at,
            "duration_seconds": self.duration_seconds,
            "context_tokens": self.context_tokens,
            "instance": asdict(self.instance),
            "resources": asdict(self.resources),
            "role": self.role.to_dict(),
            "model": self.model.to_dict(),
            "lease": self.lease.to_dict() if self.lease else None,
            "reason_codes": self.reason_codes,
        }

    def verify_identity(self) -> None:
        if self.decision_id != _identity("model-allocation", self._payload()):
            raise ValueError("allocation identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {"decision_id": self.decision_id, **self._payload()}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> ModelAllocationDecision:
        data = dict(payload)
        identity = data.pop("decision_id")
        if data.pop("schema_version") != "uah.model_allocation_decision/v1":
            raise ValueError("unsupported model allocation schema")
        data["instance"] = FixedModelInstance(**data["instance"])
        resources = dict(data["resources"])
        resources["evidence_refs"] = tuple(resources["evidence_refs"])
        data["resources"] = ResourceSnapshot(**resources)
        data["role"] = AgentRoleConfiguration.from_dict(data["role"])
        data["model"] = ModelConfiguration.from_dict(data["model"])
        data["lease"] = ModelLease.from_dict(data["lease"]) if data["lease"] else None
        data["reason_codes"] = tuple(data["reason_codes"])
        decision = cls(**data)
        if identity != decision.decision_id:
            raise ValueError("allocation identity does not match content")
        return decision


@dataclass(frozen=True)
class StartupPreflight:
    """Recorded evaluation of a bounded, owner-issued readiness observation."""

    lease: ModelLease
    readiness_owner_id: str
    observed_instance_id: str
    observed_model_configuration_id: str
    observed_at: str
    evaluated_at: str
    attempts_used: int
    elapsed_seconds: int
    succeeded: bool
    evidence_refs: tuple[str, ...]
    reason_codes: tuple[str, ...]
    preflight_id: str = field(init=False)

    def __post_init__(self) -> None:
        self.lease.verify_identity()
        for name in (
            "readiness_owner_id",
            "observed_instance_id",
            "observed_model_configuration_id",
        ):
            _text(getattr(self, name), name)
        _time(self.observed_at)
        _time(self.evaluated_at)
        _integer(self.attempts_used, "attempts_used", positive=True)
        _integer(self.elapsed_seconds, "elapsed_seconds")
        if type(self.succeeded) is not bool:
            raise ValueError("startup probe success must be boolean")
        if not isinstance(self.evidence_refs, tuple) or not self.evidence_refs:
            raise ValueError("startup preflight requires immutable owner evidence")
        for reference in self.evidence_refs:
            _text(reference, "startup evidence")
        if not isinstance(self.reason_codes, tuple):
            raise ValueError("startup reasons must be immutable")
        object.__setattr__(
            self, "preflight_id", _identity("startup-preflight", self._payload())
        )

    @property
    def accepted(self) -> bool:
        return not self.reason_codes

    def _payload(self) -> dict[str, object]:
        payload = {
            item.name: getattr(self, item.name)
            for item in fields(self)
            if item.name != "preflight_id"
        }
        payload["lease"] = self.lease.to_dict()
        return {"schema_version": "uah.startup_preflight/v1", **payload}

    def verify_identity(self) -> None:
        if self.preflight_id != _identity("startup-preflight", self._payload()):
            raise ValueError("startup preflight identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {"preflight_id": self.preflight_id, **self._payload()}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> StartupPreflight:
        data = dict(payload)
        identity = data.pop("preflight_id")
        if data.pop("schema_version") != "uah.startup_preflight/v1":
            raise ValueError("unsupported startup preflight schema")
        data["lease"] = ModelLease.from_dict(data["lease"])
        for name in ("evidence_refs", "reason_codes"):
            data[name] = tuple(data[name])
        result = cls(**data)
        if result.preflight_id != identity:
            raise ValueError("startup preflight identity does not match content")
        return result


def startup_reasons(
    result: StartupPreflight, instance: FixedModelInstance
) -> tuple[str, ...]:
    reasons = []
    if result.readiness_owner_id != instance.readiness_owner_id:
        reasons.append("startup_owner_mismatch")
    if result.observed_instance_id != result.lease.model_instance_id:
        reasons.append("startup_instance_mismatch")
    if result.observed_model_configuration_id != result.lease.model_configuration_id:
        reasons.append("startup_model_mismatch")
    if (
        not _time(result.lease.acquired_at)
        <= _time(result.observed_at)
        <= _time(result.evaluated_at)
        < _time(result.lease.expires_at)
    ):
        reasons.append("startup_observation_outside_lease")
    if (_time(result.evaluated_at) - _time(result.observed_at)).total_seconds() > 30:
        reasons.append("startup_observation_stale")
    if result.attempts_used > 2 or result.elapsed_seconds > 10:
        reasons.append("startup_probe_budget_exhausted")
    if not result.succeeded:
        reasons.append("startup_probe_failed")
    return tuple(reasons)


@dataclass(frozen=True)
class ModelLeaseRelease:
    lease: ModelLease
    reason_code: str
    released_at: str
    release_id: str = field(init=False)

    def __post_init__(self) -> None:
        self.lease.verify_identity()
        _text(self.reason_code, "release reason")
        if _time(self.released_at) < _time(self.lease.acquired_at):
            raise ValueError("model lease release predates acquisition")
        object.__setattr__(
            self, "release_id", _identity("model-lease-release", self._payload())
        )

    def _payload(self) -> dict[str, object]:
        return {
            "schema_version": "uah.model_lease_release/v1",
            "lease": self.lease.to_dict(),
            "reason_code": self.reason_code,
            "released_at": self.released_at,
        }

    def verify_identity(self) -> None:
        if self.release_id != _identity("model-lease-release", self._payload()):
            raise ValueError("model lease release identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {"release_id": self.release_id, **self._payload()}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> ModelLeaseRelease:
        data = dict(payload)
        identity = data.pop("release_id")
        if data.pop("schema_version") != "uah.model_lease_release/v1":
            raise ValueError("unsupported model release schema")
        data["lease"] = ModelLease.from_dict(data["lease"])
        result = cls(**data)
        if identity != result.release_id:
            raise ValueError("model lease release identity does not match content")
        return result


def allocation_reasons(
    replay: AgentRunReplay,
    decision: ModelAllocationDecision,
    actors: tuple[AgentRunReplay, ...],
) -> tuple[str, ...]:
    from ab_harness.agent_configuration import (
        AgentRoleConfigurationRegistry,
        ModelConfigurationRegistry,
        RegistrationPreflight,
    )

    roles, models = AgentRoleConfigurationRegistry(), ModelConfigurationRegistry()
    roles.register(decision.role)
    models.register(decision.model)
    registration = RegistrationPreflight(roles, models).evaluate(replay.manifest)
    reasons = list(registration.reasons)
    if replay.status not in {"attached_standby", "standby"}:
        reasons.append("agent_run_not_in_standby")
    if decision.environment_run_id != replay.run.environment_run_id:
        reasons.append("environment_run_mismatch")
    if (
        decision.role.domain_contract_pack_id != replay.profile.domain_contract_pack_id
        or decision.role.domain_contract_pack_revision
        != replay.profile.domain_contract_pack_revision
    ):
        reasons.append("role_domain_mismatch")
    if (
        decision.instance.model_configuration_id
        != replay.manifest.model_configuration_id
    ):
        reasons.append("model_instance_configuration_mismatch")
    if decision.resources.host_id != decision.instance.host_id:
        reasons.append("resource_host_mismatch")
    age = (
        _time(decision.requested_at) - _time(decision.resources.observed_at)
    ).total_seconds()
    if age < 0 or age > 30:
        reasons.append("resource_snapshot_not_fresh")
    if (
        not decision.role.minimum_context_tokens
        <= decision.context_tokens
        <= min(decision.model.max_context_tokens, decision.instance.max_context_tokens)
    ):
        reasons.append("context_capacity_mismatch")
    if decision.resources.available_ram_mib < decision.instance.required_ram_mib:
        reasons.append("insufficient_ram")
    if decision.resources.available_vram_mib < decision.instance.required_vram_mib:
        reasons.append("insufficient_vram")
    if any(
        actor.model_lease
        and actor.model_lease.model_instance_id == decision.instance.model_instance_id
        for actor in actors
    ):
        reasons.append("model_instance_busy")
    elif any(
        actor.model_lease
        and any(
            prior.lease == actor.model_lease
            and prior.instance.host_id == decision.instance.host_id
            for prior in actor.allocation_decisions
        )
        for actor in actors
    ):
        reasons.append("fixed_host_busy")
    return tuple(reasons)


class FixedModelAllocator:
    """Reserve one configured instance using the common ledger as authority."""

    def __init__(
        self,
        *,
        ledger: LifecycleLedger,
        roles: AgentRoleConfigurationRegistry,
        models: ModelConfigurationRegistry,
        instance: FixedModelInstance,
        clock: Callable[[], str] | None = None,
    ) -> None:
        self.ledger, self.roles, self.models, self.instance = (
            ledger,
            roles,
            models,
            instance,
        )
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat())

    def acquire(
        self,
        agent_run_id: str,
        *,
        request_id: str,
        context_tokens: int,
        duration_seconds: int,
        resources: ResourceSnapshot,
    ) -> ModelAllocationDecision:
        from ab_harness.lifecycle import LifecycleSequenceConflict

        _integer(context_tokens, "context_tokens", positive=True)
        _integer(duration_seconds, "duration_seconds", positive=True)

        for attempt in range(2):
            expected_sequence = len(self.ledger.events()) + 1
            actors = self.ledger.agent_runs()
            replay = next(
                actor for actor in actors if actor.run.agent_run_id == agent_run_id
            )
            role = self.roles.get(replay.manifest.role_configuration_id)
            model = self.models.get(replay.manifest.model_configuration_id)
            prior = next(
                (
                    item
                    for item in replay.allocation_decisions
                    if item.request_id == request_id
                ),
                None,
            )
            if prior:
                if (
                    context_tokens,
                    duration_seconds,
                    resources,
                    self.instance,
                    role,
                    model,
                ) != (
                    prior.context_tokens,
                    prior.duration_seconds,
                    prior.resources,
                    prior.instance,
                    prior.role,
                    prior.model,
                ):
                    raise ValueError("lease request identity cannot change content")
                if prior.lease is not None and replay.model_lease != prior.lease:
                    raise ValueError(
                        "released acquisition request requires a new request identity"
                    )
                return prior
            requested_at = self.clock()
            candidate = ModelLease(
                request_id,
                agent_run_id,
                replay.run.environment_run_id,
                replay.manifest.agent_id,
                self.instance.model_instance_id,
                model.model_configuration_id,
                context_tokens,
                requested_at,
                (_time(requested_at) + timedelta(seconds=duration_seconds)).isoformat(),
            )
            decision = ModelAllocationDecision(
                request_id,
                agent_run_id,
                replay.run.environment_run_id,
                requested_at,
                duration_seconds,
                context_tokens,
                self.instance,
                resources,
                role,
                model,
                candidate,
                (),
            )
            reasons = allocation_reasons(replay, decision, actors)
            if reasons:
                decision = ModelAllocationDecision(
                    request_id,
                    agent_run_id,
                    replay.run.environment_run_id,
                    requested_at,
                    duration_seconds,
                    context_tokens,
                    self.instance,
                    resources,
                    role,
                    model,
                    None,
                    reasons,
                )
            try:
                self.ledger.record(decision, expected_sequence=expected_sequence)
                return decision
            except LifecycleSequenceConflict:
                if attempt:
                    raise
        raise RuntimeError("model allocation sequence retry exhausted")

    def preflight(
        self,
        lease: ModelLease,
        *,
        readiness_owner_id: str,
        observed_instance_id: str,
        observed_model_configuration_id: str,
        observed_at: str,
        attempts_used: int,
        elapsed_seconds: int,
        succeeded: bool,
        evidence_refs: tuple[str, ...],
    ) -> StartupPreflight:
        from dataclasses import replace

        lease.verify_identity()
        replay = self.ledger.replay_agent_run(lease.agent_run_id)
        if replay.model_lease != lease or replay.status != "leased":
            raise ValueError("startup requires the exact active model lease")
        result = StartupPreflight(
            lease,
            readiness_owner_id,
            observed_instance_id,
            observed_model_configuration_id,
            observed_at,
            self.clock(),
            attempts_used,
            elapsed_seconds,
            succeeded,
            evidence_refs,
            (),
        )
        result = replace(result, reason_codes=startup_reasons(result, self.instance))
        self.ledger.record(result)
        return result

    def release(self, lease: ModelLease, *, reason_code: str) -> ModelLeaseRelease:
        lease.verify_identity()
        replay = self.ledger.replay_agent_run(lease.agent_run_id)
        prior = next((item for item in replay.releases if item.lease == lease), None)
        if prior is not None:
            if prior.reason_code != reason_code:
                raise ValueError("release request cannot change its reason")
            return prior
        if replay.model_lease != lease:
            raise ValueError("release requires the exact active model lease")
        if replay.status == "invoking":
            raise ValueError("model lease cannot be released during invocation")
        result = ModelLeaseRelease(lease, reason_code, self.clock())
        self.ledger.record(result)
        return result
