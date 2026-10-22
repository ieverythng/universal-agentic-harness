"""Immutable agent, handle, and activation identities for the H1 runtime."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import hashlib
import json
from typing import Literal, Protocol, TYPE_CHECKING

from ab_harness.environment_profiles import EnvironmentProfileRegistry
from ab_harness.environment_runs import EnvironmentRun

if TYPE_CHECKING:
    from ab_harness.lifecycle import LifecycleLedger


@dataclass(frozen=True)
class AgentManifest:
    """One immutable composition of role, model, prompt, and harness build."""

    role_configuration_id: str
    model_configuration_id: str
    prompt_pack_id: str
    harness_build_id: str
    adapter_revisions: tuple[tuple[str, str], ...]
    agent_id: str = field(init=False)

    def __post_init__(self) -> None:
        required = {
            "role_configuration_id": self.role_configuration_id,
            "model_configuration_id": self.model_configuration_id,
            "prompt_pack_id": self.prompt_pack_id,
            "harness_build_id": self.harness_build_id,
        }
        missing = tuple(name for name, value in required.items() if not value.strip())
        if missing:
            raise ValueError(
                "agent manifest fields must not be empty: %s" % ", ".join(missing)
            )
        adapter_names = tuple(name for name, _ in self.adapter_revisions)
        if len(adapter_names) != len(set(adapter_names)):
            raise ValueError("adapter revision names must be unique")
        if any(
            not name.strip() or not revision.strip()
            for name, revision in self.adapter_revisions
        ):
            raise ValueError("adapter revisions must not contain empty values")
        object.__setattr__(
            self, "adapter_revisions", tuple(sorted(self.adapter_revisions))
        )
        object.__setattr__(self, "agent_id", self._content_id())

    def _content_id(self) -> str:
        encoded = json.dumps(
            self._identity_payload(), sort_keys=True, separators=(",", ":")
        ).encode()
        return "agent:sha256:" + hashlib.sha256(encoded).hexdigest()

    def verify_identity(self) -> None:
        if self.agent_id != self._content_id():
            raise ValueError("agent identity does not match manifest content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {"agent_id": self.agent_id, **self._identity_payload()}

    def _identity_payload(self) -> dict[str, object]:
        return {
            "schema_version": "uah.agent_manifest/v1",
            "role_configuration_id": self.role_configuration_id,
            "model_configuration_id": self.model_configuration_id,
            "prompt_pack_id": self.prompt_pack_id,
            "harness_build_id": self.harness_build_id,
            "adapter_revisions": {
                name: revision for name, revision in self.adapter_revisions
            },
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> AgentManifest:
        fields = dict(payload)
        agent_id = fields.pop("agent_id")
        if fields.pop("schema_version") != "uah.agent_manifest/v1":
            raise ValueError("unsupported agent manifest schema")
        revisions = fields.pop("adapter_revisions")
        if not isinstance(revisions, dict):
            raise ValueError("adapter revisions must be an object")
        manifest = cls(adapter_revisions=tuple(revisions.items()), **fields)
        if manifest.agent_id != agent_id:
            raise ValueError("agent identity does not match manifest content")
        return manifest


class AgentRegistry:
    """Register and retrieve immutable agent embodiments."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentManifest] = {}

    def register(self, manifest: AgentManifest) -> AgentManifest:
        manifest.verify_identity()
        if manifest.agent_id in self._agents:
            raise ValueError("agent already registered: %s" % manifest.agent_id)
        self._agents[manifest.agent_id] = manifest
        return manifest

    def get(self, agent_id: str) -> AgentManifest:
        manifest = self._agents[agent_id]
        manifest.verify_identity()
        return manifest


@dataclass(frozen=True)
class AgentHandleRevision:
    """One immutable revision of a stable agent-routing handle."""

    agent_handle_id: str
    active_agent_id: str
    required_role_configuration_id: str
    fidelity_evidence_refs: tuple[str, ...]
    prior_revision_id: str | None = None
    rollback_revision_id: str | None = None
    revision_id: str = field(init=False)

    def __post_init__(self) -> None:
        required = {
            "agent_handle_id": self.agent_handle_id,
            "active_agent_id": self.active_agent_id,
            "required_role_configuration_id": self.required_role_configuration_id,
        }
        missing = tuple(name for name, value in required.items() if not value.strip())
        if missing:
            raise ValueError(
                "agent handle fields must not be empty: %s" % ", ".join(missing)
            )
        if not self.fidelity_evidence_refs or any(
            not reference.strip() for reference in self.fidelity_evidence_refs
        ):
            raise ValueError("agent handle promotion requires fidelity evidence")
        if len(self.fidelity_evidence_refs) != len(set(self.fidelity_evidence_refs)):
            raise ValueError("fidelity evidence references must be unique")
        object.__setattr__(
            self,
            "fidelity_evidence_refs",
            tuple(sorted(self.fidelity_evidence_refs)),
        )
        object.__setattr__(self, "revision_id", self._content_id())

    def _identity_payload(self) -> dict[str, object]:
        return {
            "schema_version": "uah.agent_handle_revision/v1",
            "agent_handle_id": self.agent_handle_id,
            "active_agent_id": self.active_agent_id,
            "required_role_configuration_id": self.required_role_configuration_id,
            "fidelity_evidence_refs": self.fidelity_evidence_refs,
            "prior_revision_id": self.prior_revision_id,
            "rollback_revision_id": self.rollback_revision_id,
        }

    def _content_id(self) -> str:
        encoded = json.dumps(
            self._identity_payload(), sort_keys=True, separators=(",", ":")
        ).encode()
        return "agent-handle-revision:sha256:" + hashlib.sha256(encoded).hexdigest()

    def verify_identity(self) -> None:
        if self.revision_id != self._content_id():
            raise ValueError("agent handle revision identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {"revision_id": self.revision_id, **self._identity_payload()}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> AgentHandleRevision:
        fields = dict(payload)
        revision_id = fields.pop("revision_id")
        if fields.pop("schema_version") != "uah.agent_handle_revision/v1":
            raise ValueError("unsupported agent handle schema")
        fields["fidelity_evidence_refs"] = tuple(fields["fidelity_evidence_refs"])
        revision = cls(**fields)
        if revision.revision_id != revision_id:
            raise ValueError("agent handle revision identity does not match content")
        return revision


class AgentHandleRegistry:
    """Register initial stable-handle bindings without enabling rebinding."""

    def __init__(self, agents: AgentRegistry) -> None:
        self._agents = agents
        self._active_by_handle: dict[str, AgentHandleRevision] = {}
        self._revisions: dict[str, AgentHandleRevision] = {}

    def register(
        self,
        *,
        agent_handle_id: str,
        candidate_agent_id: str,
        fidelity_evidence_refs: tuple[str, ...],
    ) -> AgentHandleRevision:
        candidate = self._agents.get(candidate_agent_id)
        if agent_handle_id in self._active_by_handle:
            raise ValueError("agent handle already registered: %s" % agent_handle_id)

        revision = AgentHandleRevision(
            agent_handle_id=agent_handle_id,
            active_agent_id=candidate.agent_id,
            required_role_configuration_id=candidate.role_configuration_id,
            fidelity_evidence_refs=fidelity_evidence_refs,
        )
        self._revisions[revision.revision_id] = revision
        self._active_by_handle[agent_handle_id] = revision
        return revision

    def resolve(self, agent_handle_id: str) -> AgentHandleRevision:
        revision = self._active_by_handle[agent_handle_id]
        revision.verify_identity()
        return revision

    def get_revision(self, revision_id: str) -> AgentHandleRevision:
        revision = self._revisions[revision_id]
        revision.verify_identity()
        return revision

    def agent_for_revision(self, revision_id: str) -> AgentManifest:
        return self._agents.get(self.get_revision(revision_id).active_agent_id)


@dataclass(frozen=True)
class AgentRun:
    """One logical agent activation pinned to one environment and handle revision."""

    agent_run_id: str
    environment_run_id: str
    agent_handle_id: str
    resolved_handle_revision_id: str
    started_from_agent_id: str
    status: Literal[
        "attached_standby",
        "leased",
        "ready",
        "invoking",
        "standby",
        "failed",
        "terminated",
    ] = "attached_standby"

    def __post_init__(self) -> None:
        required = {
            "agent_run_id": self.agent_run_id,
            "environment_run_id": self.environment_run_id,
            "agent_handle_id": self.agent_handle_id,
            "resolved_handle_revision_id": self.resolved_handle_revision_id,
            "started_from_agent_id": self.started_from_agent_id,
        }
        missing = tuple(name for name, value in required.items() if not value.strip())
        if missing:
            raise ValueError(
                "agent run fields must not be empty: %s" % ", ".join(missing)
            )
        if self.status not in {
            "attached_standby",
            "leased",
            "ready",
            "invoking",
            "standby",
            "failed",
            "terminated",
        }:
            raise ValueError("unsupported agent run status: %s" % self.status)


class EnvironmentRunLookup(Protocol):
    """Read-only environment-run dependency required for agent attachment."""

    def get(self, environment_run_id: str) -> EnvironmentRun: ...


class AgentRunRegistry:
    """Attach logical agents without reserving or invoking model capacity."""

    def __init__(
        self,
        handles: AgentHandleRegistry,
        environment_runs: EnvironmentRunLookup,
        environment_profiles: EnvironmentProfileRegistry,
        *,
        ledger: LifecycleLedger | None = None,
    ) -> None:
        from ab_harness.lifecycle import LifecycleLedger

        self._handles = handles
        self._environment_runs = environment_runs
        self._environment_profiles = environment_profiles
        self._ledger = ledger if ledger is not None else LifecycleLedger()
        self._runs: dict[str, AgentRun] = {}
        self._live_by_environment_handle: dict[tuple[str, str], AgentRun] = {}

    def attach(
        self,
        *,
        agent_run_id: str,
        environment_run_id: str,
        agent_handle_id: str,
    ) -> AgentRun:
        from ab_harness.agent_lifecycle import AgentRunAttached

        self._refresh()
        if agent_run_id in self._runs:
            raise ValueError("agent run already registered: %s" % agent_run_id)

        environment_run = self._environment_runs.get(environment_run_id)
        if environment_run.status != "active":
            raise ValueError("environment run is not active: %s" % environment_run_id)
        profile = self._environment_profiles.get(
            environment_run.attestation.environment_profile_id
        )
        if agent_handle_id not in profile.agent_handle_ids:
            raise ValueError(
                "agent handle is not in environment profile roster: %s"
                % agent_handle_id
            )

        live_key = (environment_run_id, agent_handle_id)
        if live_key in self._live_by_environment_handle:
            raise ValueError(
                "live agent run already attached for environment and handle"
            )

        handle_revision = self._handles.resolve(agent_handle_id)
        agent_run = AgentRun(
            agent_run_id=agent_run_id,
            environment_run_id=environment_run_id,
            agent_handle_id=agent_handle_id,
            resolved_handle_revision_id=handle_revision.revision_id,
            started_from_agent_id=handle_revision.active_agent_id,
        )
        self._ledger.record(
            AgentRunAttached(
                run=agent_run,
                manifest=self._handles.agent_for_revision(handle_revision.revision_id),
                handle_revision=handle_revision,
                profile=profile,
                attestation=environment_run.attestation,
            )
        )
        self._refresh()
        return self._runs[agent_run_id]

    def get(self, agent_run_id: str) -> AgentRun:
        self._refresh()
        return self._runs[agent_run_id]

    def terminate(
        self, agent_run_id: str, *, reason_code: str, terminated_at: str
    ) -> AgentRun:
        from ab_harness.agent_lifecycle import AgentRunTermination

        replay = self._ledger.replay_agent_run(agent_run_id)
        self._ledger.record(
            AgentRunTermination(
                replay.run, reason_code, terminated_at, replay.model_lease
            )
        )
        return self.get(agent_run_id)

    def _refresh(self) -> None:
        live = {}
        for replay in self._ledger.agent_runs():
            run = replay.run
            existing = self._runs.get(run.agent_run_id)
            if existing != run:
                self._runs[run.agent_run_id] = run
            if run.status not in {"failed", "terminated"}:
                live[(run.environment_run_id, run.agent_handle_id)] = self._runs[
                    run.agent_run_id
                ]
        self._live_by_environment_handle = live
