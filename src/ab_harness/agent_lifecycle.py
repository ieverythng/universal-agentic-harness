"""Closed H1 actor event family and model-free activation replay."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import TYPE_CHECKING

from ab_harness.agent_identity import AgentHandleRevision, AgentManifest, AgentRun
from ab_harness.environment_profiles import (
    EnvironmentProfile,
    EnvironmentProfileRegistry,
)
from ab_harness.environment_runs import (
    EnvironmentRunAttestation,
    EnvironmentRunRegistry,
)

if TYPE_CHECKING:
    from ab_harness.lifecycle import TraceEvent
    from ab_harness.model_allocator import ModelLease, ModelAllocationDecision
    from ab_harness.model_allocator import ModelLeaseRelease, StartupPreflight
    from ab_harness.model_invocation import (
        ModelInvocationRequest,
        RawModelOutput,
        ModelInvocationFailure,
    )


@dataclass(frozen=True)
class AgentRunAttached:
    run: AgentRun
    manifest: AgentManifest
    handle_revision: AgentHandleRevision
    profile: EnvironmentProfile
    attestation: EnvironmentRunAttestation

    def to_dict(self) -> dict[str, object]:
        self.manifest.verify_identity()
        self.handle_revision.verify_identity()
        return {
            "run": asdict(self.run),
            "manifest": self.manifest.to_dict(),
            "handle_revision": self.handle_revision.to_dict(),
            "profile": asdict(self.profile),
            "attestation": asdict(self.attestation),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> AgentRunAttached:
        profile = dict(data["profile"])
        profile["required_interface_ids"] = tuple(profile["required_interface_ids"])
        profile["agent_handle_ids"] = tuple(profile["agent_handle_ids"])
        attestation = dict(data["attestation"])
        attestation["readiness_evidence_refs"] = tuple(
            attestation["readiness_evidence_refs"]
        )
        return cls(
            run=AgentRun(**data["run"]),
            manifest=AgentManifest.from_dict(data["manifest"]),
            handle_revision=AgentHandleRevision.from_dict(data["handle_revision"]),
            profile=EnvironmentProfile(**profile),
            attestation=EnvironmentRunAttestation(**attestation),
        )


@dataclass(frozen=True)
class AgentRunTermination:
    run: AgentRun
    reason_code: str
    terminated_at: str
    lease: ModelLease | None


def termination_specs(fact: AgentRunTermination) -> tuple[dict[str, object], ...]:
    from ab_harness.model_allocator import ModelLeaseRelease, _time

    if not fact.reason_code.strip():
        raise ValueError("agent termination requires a reason")
    _time(fact.terminated_at)
    spec = {
        "event_type": "agent_run_terminated",
        "environment_run_id": fact.run.environment_run_id,
        "event_scope": "agent",
        "agent_run_id": fact.run.agent_run_id,
        "task_id": None,
        "trace_id": None,
        "operation_id": None,
        "artifact_refs": (fact.run.started_from_agent_id,),
        "data": {
            "run": asdict(fact.run),
            "reason_code": fact.reason_code,
            "terminated_at": fact.terminated_at,
        },
    }
    if fact.lease is None:
        return (spec,)
    release = ModelLeaseRelease(fact.lease, "agent_run_terminated", fact.terminated_at)
    return (release_spec(release), spec)


@dataclass(frozen=True)
class AgentRunReplay:
    run: AgentRun
    manifest: AgentManifest
    handle_revision: AgentHandleRevision
    profile: EnvironmentProfile
    attestation: EnvironmentRunAttestation
    events: tuple[TraceEvent, ...]
    model_lease: ModelLease | None = None
    allocation_decisions: tuple[ModelAllocationDecision, ...] = ()
    preflights: tuple[StartupPreflight, ...] = ()
    releases: tuple[ModelLeaseRelease, ...] = ()
    invocations: tuple[ModelInvocationRequest, ...] = ()
    invocation_outcomes: tuple[RawModelOutput | ModelInvocationFailure, ...] = ()

    @property
    def status(self) -> str:
        return self.run.status


def _agent_tail(replay: AgentRunReplay) -> str:
    return next(
        event.event_id
        for event in reversed(replay.events)
        if event.event_scope == "agent"
    )


def attachment_spec(fact: AgentRunAttached) -> dict[str, object]:
    return {
        "event_type": "agent_run_attached",
        "environment_run_id": fact.run.environment_run_id,
        "task_id": None,
        "trace_id": None,
        "operation_id": None,
        "event_scope": "agent",
        "agent_run_id": fact.run.agent_run_id,
        "artifact_refs": (
            fact.manifest.agent_id,
            fact.handle_revision.revision_id,
            fact.attestation.attestation_id,
        ),
        "data": fact.to_dict(),
    }


def apply_agent_event(states: dict[str, AgentRunReplay], event: TraceEvent) -> None:
    from ab_harness.model_allocator import (
        ModelAllocationDecision,
        ModelLease,
        allocation_reasons,
        _time,
    )
    from ab_harness.model_allocator import (
        ModelLeaseRelease,
        StartupPreflight,
        startup_reasons,
    )
    from datetime import timedelta

    if event.event_type == "agent_run_terminated":
        replay = states.get(event.agent_run_id)
        if (
            replay is None
            or replay.status in {"failed", "terminated"}
            or replay.model_lease is not None
        ):
            raise ValueError(
                "termination requires an active agent without a model lease"
            )
        recorded_run = AgentRun(**event.data["run"])
        if (
            recorded_run.agent_run_id,
            recorded_run.environment_run_id,
            recorded_run.agent_handle_id,
            recorded_run.resolved_handle_revision_id,
            recorded_run.started_from_agent_id,
        ) != (
            replay.run.agent_run_id,
            replay.run.environment_run_id,
            replay.run.agent_handle_id,
            replay.run.resolved_handle_revision_id,
            replay.run.started_from_agent_id,
        ):
            raise ValueError("termination identity does not match attached run")
        if (
            event.environment_run_id != replay.run.environment_run_id
            or event.parent_event_id != _agent_tail(replay)
        ):
            raise ValueError("termination lineage or causal tail mismatch")
        if (
            not isinstance(event.data.get("reason_code"), str)
            or not event.data["reason_code"].strip()
        ):
            raise ValueError("termination requires a reason")
        _time(event.data["terminated_at"])
        states[replay.run.agent_run_id] = replace(
            replay,
            run=replace(replay.run, status="terminated"),
            events=(*replay.events, event),
        )
        return

    if event.event_type in {
        "startup_preflight_passed",
        "startup_preflight_failed",
        "model_lease_released",
    }:
        replay = states.get(event.agent_run_id)
        if replay is None:
            raise ValueError("agent transition requires attached run")
        if (
            event.environment_run_id != replay.run.environment_run_id
            or event.parent_event_id != _agent_tail(replay)
        ):
            raise ValueError("agent transition lineage or causal tail mismatch")
        if event.event_type == "model_lease_released":
            result = ModelLeaseRelease.from_dict(event.data)
            if result.lease != replay.model_lease or replay.status == "invoking":
                raise ValueError("release requires the exact active model lease")
            states[replay.run.agent_run_id] = replace(
                replay,
                run=replace(replay.run, status="standby"),
                model_lease=None,
                releases=(*replay.releases, result),
                events=(*replay.events, event),
            )
        else:
            result = StartupPreflight.from_dict(event.data)
            if replay.status != "leased" or result.lease != replay.model_lease:
                raise ValueError("startup requires the exact active model lease")
            allocation = next(
                item
                for item in replay.allocation_decisions
                if item.lease == result.lease
            )
            if result.reason_codes != startup_reasons(result, allocation.instance):
                raise ValueError("startup decision does not match owner readiness")
            expected = (
                "startup_preflight_passed"
                if result.accepted
                else "startup_preflight_failed"
            )
            if event.event_type != expected:
                raise ValueError("startup outcome does not match event")
            states[replay.run.agent_run_id] = replace(
                replay,
                run=replace(replay.run, status="ready")
                if result.accepted
                else replay.run,
                preflights=(*replay.preflights, result),
                events=(*replay.events, event),
            )
        return

    if event.event_type in {"model_lease_acquired", "model_lease_rejected"}:
        decision = ModelAllocationDecision.from_dict(event.data)
        for actor in states.values():
            for prior in actor.allocation_decisions:
                if (
                    prior.instance.model_instance_id
                    == decision.instance.model_instance_id
                    and prior.instance != decision.instance
                ):
                    raise ValueError("model instance identity cannot change content")
                if (
                    prior.resources.snapshot_id == decision.resources.snapshot_id
                    and prior.resources != decision.resources
                ):
                    raise ValueError("resource snapshot identity cannot change content")
        replay = states.get(event.agent_run_id)
        if replay is None:
            raise ValueError("model allocation requires attached agent run")
        if (
            event.environment_run_id != replay.run.environment_run_id
            or decision.agent_run_id != event.agent_run_id
        ):
            raise ValueError("model allocation actor lineage mismatch")
        if event.parent_event_id != _agent_tail(replay):
            raise ValueError("agent parent event does not match causal tail")
        if any(
            item.request_id == decision.request_id
            for item in replay.allocation_decisions
        ):
            raise ValueError("model allocation request already recorded")
        expected_reasons = allocation_reasons(replay, decision, tuple(states.values()))
        if decision.reason_codes != expected_reasons:
            raise ValueError(
                "model allocation decision does not match compatibility or capacity"
            )
        expected_type = (
            "model_lease_acquired" if decision.accepted else "model_lease_rejected"
        )
        if event.event_type != expected_type:
            raise ValueError("model allocation outcome does not match event")
        if decision.lease:
            expected_lease = ModelLease(
                decision.request_id,
                replay.run.agent_run_id,
                replay.run.environment_run_id,
                replay.manifest.agent_id,
                decision.instance.model_instance_id,
                decision.model.model_configuration_id,
                decision.context_tokens,
                decision.requested_at,
                (
                    _time(decision.requested_at)
                    + timedelta(seconds=decision.duration_seconds)
                ).isoformat(),
            )
            if decision.lease != expected_lease:
                raise ValueError("model lease does not match exact allocation")
        states[replay.run.agent_run_id] = replace(
            replay,
            run=replace(replay.run, status="leased")
            if decision.accepted
            else replay.run,
            model_lease=decision.lease if decision.accepted else replay.model_lease,
            allocation_decisions=(*replay.allocation_decisions, decision),
            events=(*replay.events, event),
        )
        return
    if event.event_type != "agent_run_attached":
        raise ValueError("unsupported agent lifecycle event")
    fact = AgentRunAttached.from_dict(event.data)
    run = fact.run
    for existing in states.values():
        if (
            existing.profile.environment_profile_id
            == fact.profile.environment_profile_id
            and existing.profile != fact.profile
        ):
            raise ValueError("environment identity cannot change its profile content")
        if (
            existing.run.environment_run_id == run.environment_run_id
            and existing.attestation != fact.attestation
        ):
            raise ValueError(
                "environment identity cannot change its activation attestation"
            )
    if run.agent_run_id in states:
        raise ValueError("agent run already registered")
    if run.status != "attached_standby":
        raise ValueError("attachment requires standby")
    if any(
        replay.run.environment_run_id == run.environment_run_id
        and replay.run.agent_handle_id == run.agent_handle_id
        and replay.status not in {"failed", "terminated"}
        for replay in states.values()
    ):
        raise ValueError("live agent run already attached for environment and handle")
    if event.parent_event_id is not None:
        raise ValueError("agent attachment cannot have a parent")
    if (
        event.agent_run_id != run.agent_run_id
        or event.environment_run_id != run.environment_run_id
    ):
        raise ValueError("agent attachment envelope does not match run")
    if (
        run.resolved_handle_revision_id != fact.handle_revision.revision_id
        or run.agent_handle_id != fact.handle_revision.agent_handle_id
        or run.started_from_agent_id != fact.manifest.agent_id
        or fact.handle_revision.active_agent_id != fact.manifest.agent_id
        or fact.handle_revision.required_role_configuration_id
        != fact.manifest.role_configuration_id
        or run.environment_run_id != fact.attestation.environment_run_id
        or run.agent_handle_id not in fact.profile.agent_handle_ids
    ):
        raise ValueError("agent attachment identity or roster does not match")
    EnvironmentRunRegistry(EnvironmentProfileRegistry((fact.profile,))).register(
        fact.attestation
    )
    states[run.agent_run_id] = AgentRunReplay(
        run,
        fact.manifest,
        fact.handle_revision,
        fact.profile,
        fact.attestation,
        (event,),
    )


def model_allocation_spec(fact: ModelAllocationDecision) -> dict[str, object]:
    fact.verify_identity()
    return {
        "event_type": "model_lease_acquired"
        if fact.accepted
        else "model_lease_rejected",
        "environment_run_id": fact.environment_run_id,
        "task_id": None,
        "trace_id": None,
        "operation_id": None,
        "event_scope": "agent",
        "agent_run_id": fact.agent_run_id,
        "artifact_refs": (
            fact.decision_id,
            fact.role.role_configuration_id,
            fact.model.model_configuration_id,
            *((fact.lease.model_lease_id,) if fact.lease else ()),
        ),
        "data": fact.to_dict(),
    }


def _model_agent_spec(
    event_type: str, lease: ModelLease, artifact_id: str, data: dict[str, object]
) -> dict[str, object]:
    return {
        "event_type": event_type,
        "environment_run_id": lease.environment_run_id,
        "task_id": None,
        "trace_id": None,
        "operation_id": None,
        "event_scope": "agent",
        "agent_run_id": lease.agent_run_id,
        "artifact_refs": (artifact_id, lease.model_lease_id),
        "data": data,
    }


def release_spec(fact: ModelLeaseRelease) -> dict[str, object]:
    return _model_agent_spec(
        "model_lease_released", fact.lease, fact.release_id, fact.to_dict()
    )


def startup_specs(fact: StartupPreflight) -> tuple[dict[str, object], ...]:
    from ab_harness.model_allocator import ModelLeaseRelease

    specs = (
        _model_agent_spec(
            "startup_preflight_passed" if fact.accepted else "startup_preflight_failed",
            fact.lease,
            fact.preflight_id,
            fact.to_dict(),
        ),
    )
    if fact.accepted:
        return specs
    release = ModelLeaseRelease(
        fact.lease, "startup_preflight_failed", fact.evaluated_at
    )
    return (*specs, release_spec(release))


def replay_agent_runs(events: tuple[TraceEvent, ...]) -> tuple[AgentRunReplay, ...]:
    states: dict[str, AgentRunReplay] = {}
    for event in events:
        if event.event_scope == "agent":
            apply_agent_event(states, event)
        elif event.agent_run_id is not None:
            apply_invocation_event(states, event)
    return tuple(states.values())


def apply_invocation_event(
    states: dict[str, AgentRunReplay], event: TraceEvent
) -> None:
    from ab_harness.model_invocation import (
        ModelInvocationRequest,
        RawModelOutput,
        ModelInvocationFailure,
    )

    replay = states.get(event.agent_run_id)
    if replay is None:
        raise ValueError("model invocation requires a recorded agent activation")
    if event.environment_run_id != replay.run.environment_run_id:
        raise ValueError("model invocation environment does not match actor")
    if event.event_type == "model_invocation_started":
        request = ModelInvocationRequest.from_dict(event.data["request"])
        if request.lease != replay.model_lease or replay.status != "ready":
            raise ValueError("model invocation requires the exact ready model lease")
        if any(
            item.invocation_id == request.invocation_id
            for actor in states.values()
            for item in actor.invocations
        ):
            raise ValueError("model invocation identity already recorded")
        if (
            request.agent_run_id != replay.run.agent_run_id
            or request.compiled_prompt.agent_id != replay.manifest.agent_id
            or request.compiled_prompt.role_configuration_id
            != replay.manifest.role_configuration_id
            or request.compiled_prompt.prompt_pack_id != replay.manifest.prompt_pack_id
            or request.compiled_prompt.task_id != event.task_id
            or request.compiled_prompt.trace_id != event.trace_id
        ):
            raise ValueError("model invocation prompt or actor lineage mismatch")
        states[replay.run.agent_run_id] = replace(
            replay,
            run=replace(replay.run, status="invoking"),
            invocations=(*replay.invocations, request),
            events=(*replay.events, event),
        )
    elif event.event_type in {"model_invocation_completed", "model_invocation_failed"}:
        outcome = (
            RawModelOutput.from_dict(event.data)
            if event.event_type == "model_invocation_completed"
            else ModelInvocationFailure.from_dict(event.data)
        )
        if (
            replay.status != "invoking"
            or not replay.invocations
            or outcome.request != replay.invocations[-1]
        ):
            raise ValueError("model outcome requires its exact in-flight invocation")
        if (outcome.request.trace_id, outcome.request.task_id) != (
            event.trace_id,
            event.task_id,
        ):
            raise ValueError("model outcome task lineage mismatch")
        states[replay.run.agent_run_id] = replace(
            replay,
            run=replace(replay.run, status="ready"),
            invocation_outcomes=(*replay.invocation_outcomes, outcome),
            events=(*replay.events, event),
        )
    else:
        raise ValueError("unsupported actor-bearing task event")
