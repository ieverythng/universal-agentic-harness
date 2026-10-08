from dataclasses import FrozenInstanceError

import pytest

from ab_harness.agent_identity import AgentManifest
from ab_harness.agent_identity import AgentHandleRegistry
from ab_harness.agent_identity import AgentRegistry
from ab_harness.agent_identity import AgentRun
from ab_harness.agent_identity import AgentRunRegistry
from ab_harness.environment_profiles import EnvironmentProfile
from ab_harness.environment_profiles import EnvironmentProfileRegistry
from ab_harness.environment_runs import EnvironmentRun
from ab_harness.environment_runs import EnvironmentRunAttestation
from ab_harness.environment_runs import EnvironmentRunRegistry


def _manifest(
    *,
    role_configuration_id: str = "role:synthetic.worker:v1",
    model_configuration_id: str = "model:synthetic.worker:v1",
) -> AgentManifest:
    return AgentManifest(
        role_configuration_id=role_configuration_id,
        model_configuration_id=model_configuration_id,
        prompt_pack_id="prompt:synthetic.worker:v1",
        harness_build_id="git:0123456789abcdef",
        adapter_revisions=(
            ("provider", "openai-compatible:v1"),
            ("synthetic", "git:fedcba9876543210"),
        ),
    )


def test_agent_registry_registers_one_content_addressed_immutable_manifest():
    registry = AgentRegistry()
    manifest = _manifest()

    registered = registry.register(manifest)

    assert registered.agent_id.startswith("agent:sha256:")
    assert registry.get(registered.agent_id) is registered
    with pytest.raises(FrozenInstanceError):
        registered.prompt_pack_id = "prompt:replacement:v1"  # type: ignore[misc]


def test_agent_identity_canonicalizes_adapter_revision_order():
    manifest = _manifest()
    reordered = AgentManifest(
        role_configuration_id=manifest.role_configuration_id,
        model_configuration_id=manifest.model_configuration_id,
        prompt_pack_id=manifest.prompt_pack_id,
        harness_build_id=manifest.harness_build_id,
        adapter_revisions=tuple(reversed(manifest.adapter_revisions)),
    )

    assert reordered.agent_id == manifest.agent_id
    assert reordered.adapter_revisions == manifest.adapter_revisions


@pytest.mark.parametrize(
    "field_name,replacement",
    (
        ("role_configuration_id", "role:synthetic.reviewer:v1"),
        ("model_configuration_id", "model:synthetic.worker:v2"),
        ("prompt_pack_id", "prompt:synthetic.worker:v2"),
        ("harness_build_id", "git:fedcba9876543210"),
        ("adapter_revisions", (("provider", "openai-compatible:v2"),)),
    ),
)
def test_every_manifest_member_contributes_to_agent_identity(field_name, replacement):
    manifest = _manifest()
    fields = {
        "role_configuration_id": manifest.role_configuration_id,
        "model_configuration_id": manifest.model_configuration_id,
        "prompt_pack_id": manifest.prompt_pack_id,
        "harness_build_id": manifest.harness_build_id,
        "adapter_revisions": manifest.adapter_revisions,
    }
    fields[field_name] = replacement

    changed = AgentManifest(**fields)

    assert changed.agent_id != manifest.agent_id


def test_agent_and_handle_registries_reverify_content_addressed_identity():
    agents, original, _candidate = _registered_agents()
    handles = AgentHandleRegistry(agents)
    revision = handles.register(
        agent_handle_id="handle:synthetic.worker.primary",
        candidate_agent_id=original.agent_id,
        fidelity_evidence_refs=("fidelity-report:synthetic:v1",),
    )

    object.__setattr__(original, "prompt_pack_id", "prompt:tampered")
    with pytest.raises(ValueError, match="agent identity does not match"):
        agents.get(original.agent_id)

    object.__setattr__(revision, "active_agent_id", "agent:tampered")
    with pytest.raises(ValueError, match="handle revision identity"):
        handles.resolve(revision.agent_handle_id)


def test_agent_manifest_rejects_duplicate_adapter_names():
    with pytest.raises(ValueError, match="adapter revision names must be unique"):
        AgentManifest(
            role_configuration_id="role:synthetic.worker:v1",
            model_configuration_id="model:synthetic.worker:v1",
            prompt_pack_id="prompt:synthetic.worker:v1",
            harness_build_id="git:0123456789abcdef",
            adapter_revisions=(("synthetic", "v1"), ("synthetic", "v2")),
        )


def test_agent_registry_rejects_duplicate_manifest_without_replacing_it():
    registry = AgentRegistry()
    manifest = registry.register(_manifest())

    with pytest.raises(ValueError, match="agent already registered"):
        registry.register(_manifest())

    assert registry.get(manifest.agent_id) is manifest


def _registered_agents() -> tuple[AgentRegistry, AgentManifest, AgentManifest]:
    agents = AgentRegistry()
    original = agents.register(_manifest())
    candidate = agents.register(
        _manifest(model_configuration_id="model:synthetic.worker:v2")
    )
    return agents, original, candidate


def test_handle_registration_creates_an_immutable_resolvable_revision():
    agents, original, _ = _registered_agents()
    handles = AgentHandleRegistry(agents)

    revision = handles.register(
        agent_handle_id="handle:synthetic.worker.primary",
        candidate_agent_id=original.agent_id,
        fidelity_evidence_refs=("fidelity-report:synthetic:v1",),
    )

    assert revision.revision_id.startswith("agent-handle-revision:sha256:")
    assert revision.required_role_configuration_id == original.role_configuration_id
    assert revision.prior_revision_id is None
    assert revision.rollback_revision_id is None
    assert handles.resolve(revision.agent_handle_id) is revision
    with pytest.raises(FrozenInstanceError):
        revision.active_agent_id = "agent:replacement"  # type: ignore[misc]


def test_handle_registration_rejects_rebinding_until_fidelity_gate_exists():
    agents, original, candidate = _registered_agents()
    handles = AgentHandleRegistry(agents)
    first = handles.register(
        agent_handle_id="handle:synthetic.worker.primary",
        candidate_agent_id=original.agent_id,
        fidelity_evidence_refs=("fidelity-report:synthetic:v1",),
    )

    with pytest.raises(ValueError, match="handle already registered"):
        handles.register(
            agent_handle_id=first.agent_handle_id,
            candidate_agent_id=candidate.agent_id,
            fidelity_evidence_refs=("fidelity-report:synthetic:v2",),
        )

    assert handles.resolve(first.agent_handle_id) is first
    assert handles.get_revision(first.revision_id) is first


def test_handle_registration_does_not_expose_role_changing_rebind():
    agents, original, _ = _registered_agents()
    other_role = agents.register(
        _manifest(
            role_configuration_id="role:synthetic.reviewer:v1",
            model_configuration_id="model:synthetic.reviewer:v1",
        )
    )
    handles = AgentHandleRegistry(agents)
    first = handles.register(
        agent_handle_id="handle:synthetic.worker.primary",
        candidate_agent_id=original.agent_id,
        fidelity_evidence_refs=("fidelity-report:synthetic:v1",),
    )

    with pytest.raises(ValueError, match="handle already registered"):
        handles.register(
            agent_handle_id=first.agent_handle_id,
            candidate_agent_id=other_role.agent_id,
            fidelity_evidence_refs=("fidelity-report:other-role:v1",),
        )

    assert handles.resolve(first.agent_handle_id) is first


def test_handle_registration_requires_fidelity_evidence_reference():
    agents, original, _ = _registered_agents()
    handles = AgentHandleRegistry(agents)

    with pytest.raises(ValueError, match="fidelity evidence"):
        handles.register(
            agent_handle_id="handle:synthetic.worker.primary",
            candidate_agent_id=original.agent_id,
            fidelity_evidence_refs=(),
        )


def _environment_profile(
    *,
    environment_profile_id: str = "environment-profile:synthetic:v1",
    agent_handle_ids: tuple[str, ...] = ("handle:synthetic.worker.primary",),
) -> EnvironmentProfile:
    return EnvironmentProfile(
        environment_profile_id=environment_profile_id,
        domain_contract_pack_id="domain-pack:synthetic:v1",
        domain_contract_pack_revision="sha256:domain-pack-revision",
        native_runtime_revision="synthetic-runtime:v1",
        environment_owner_id="synthetic.runtime.owner",
        required_interface_ids=("synthetic.request",),
        agent_handle_ids=agent_handle_ids,
    )


def _environment_attestation(
    environment_run_id: str,
    environment_profile_id: str,
) -> EnvironmentRunAttestation:
    return EnvironmentRunAttestation(
        environment_run_id=environment_run_id,
        environment_profile_id=environment_profile_id,
        domain_contract_pack_revision="sha256:domain-pack-revision",
        native_runtime_revision="synthetic-runtime:v1",
        environment_owner_id="synthetic.runtime.owner",
        attestation_id="environment-attestation:" + environment_run_id,
        started_at="2026-10-01T12:00:00Z",
        readiness_evidence_refs=("artifact:readiness:" + environment_run_id,),
    )


def _run_registries(
    *,
    profiles: tuple[EnvironmentProfile, ...] | None = None,
) -> tuple[
    AgentRegistry,
    AgentHandleRegistry,
    EnvironmentProfileRegistry,
    EnvironmentRunRegistry,
    AgentRunRegistry,
]:
    agents, original, _ = _registered_agents()
    handles = AgentHandleRegistry(agents)
    handles.register(
        agent_handle_id="handle:synthetic.worker.primary",
        candidate_agent_id=original.agent_id,
        fidelity_evidence_refs=("fidelity-report:synthetic:v1",),
    )
    profile_registry = EnvironmentProfileRegistry(profiles or (_environment_profile(),))
    environment_runs = EnvironmentRunRegistry(profile_registry)
    agent_runs = AgentRunRegistry(handles, environment_runs, profile_registry)
    return agents, handles, profile_registry, environment_runs, agent_runs


def test_agent_run_attaches_to_an_active_rostered_environment_in_standby():
    _, handles, _, environment_runs, agent_runs = _run_registries()
    attestation = _environment_attestation(
        "environment-run:synthetic:001",
        "environment-profile:synthetic:v1",
    )
    environment_runs.register(attestation)
    handle_revision = handles.resolve("handle:synthetic.worker.primary")

    run = agent_runs.attach(
        agent_run_id="agent-run:synthetic:001",
        environment_run_id=attestation.environment_run_id,
        agent_handle_id=handle_revision.agent_handle_id,
    )

    assert run.status == "attached_standby"
    assert run.started_from_agent_id == handle_revision.active_agent_id
    assert run.resolved_handle_revision_id == handle_revision.revision_id
    assert agent_runs.get(run.agent_run_id) is run


def test_agent_run_rejects_an_unimplemented_lifecycle_status():
    with pytest.raises(ValueError, match="unsupported agent run status"):
        AgentRun(
            agent_run_id="agent-run:synthetic:unsupported",
            environment_run_id="environment-run:synthetic:001",
            agent_handle_id="handle:synthetic.worker.primary",
            resolved_handle_revision_id="agent-handle-revision:synthetic:v1",
            started_from_agent_id="agent:synthetic:v1",
            status="running",  # type: ignore[arg-type]
        )


def test_registered_agent_run_pins_the_resolved_handle_revision():
    _, handles, _, environment_runs, agent_runs = _run_registries()
    attestation = _environment_attestation(
        "environment-run:synthetic:001",
        "environment-profile:synthetic:v1",
    )
    environment_runs.register(attestation)
    run = agent_runs.attach(
        agent_run_id="agent-run:synthetic:001",
        environment_run_id=attestation.environment_run_id,
        agent_handle_id="handle:synthetic.worker.primary",
    )
    assert agent_runs.get(run.agent_run_id) is run
    resolved = handles.resolve("handle:synthetic.worker.primary")
    assert run.started_from_agent_id == resolved.active_agent_id
    assert run.resolved_handle_revision_id == resolved.revision_id


def test_agent_run_rejects_duplicate_identity_and_second_live_handle_run():
    _, _, _, environment_runs, agent_runs = _run_registries()
    attestation = _environment_attestation(
        "environment-run:synthetic:001",
        "environment-profile:synthetic:v1",
    )
    environment_runs.register(attestation)
    agent_runs.attach(
        agent_run_id="agent-run:synthetic:001",
        environment_run_id=attestation.environment_run_id,
        agent_handle_id="handle:synthetic.worker.primary",
    )

    with pytest.raises(ValueError, match="agent run already registered"):
        agent_runs.attach(
            agent_run_id="agent-run:synthetic:001",
            environment_run_id=attestation.environment_run_id,
            agent_handle_id="handle:synthetic.worker.primary",
        )
    with pytest.raises(ValueError, match="live agent run already attached"):
        agent_runs.attach(
            agent_run_id="agent-run:synthetic:002",
            environment_run_id=attestation.environment_run_id,
            agent_handle_id="handle:synthetic.worker.primary",
        )


def test_same_handle_can_attach_to_distinct_environment_runs():
    _, _, _, environment_runs, agent_runs = _run_registries()
    first_attestation = _environment_attestation(
        "environment-run:synthetic:001",
        "environment-profile:synthetic:v1",
    )
    second_attestation = _environment_attestation(
        "environment-run:synthetic:002",
        "environment-profile:synthetic:v1",
    )
    environment_runs.register(first_attestation)
    environment_runs.register(second_attestation)

    first = agent_runs.attach(
        agent_run_id="agent-run:synthetic:001",
        environment_run_id=first_attestation.environment_run_id,
        agent_handle_id="handle:synthetic.worker.primary",
    )
    second = agent_runs.attach(
        agent_run_id="agent-run:synthetic:002",
        environment_run_id=second_attestation.environment_run_id,
        agent_handle_id="handle:synthetic.worker.primary",
    )

    assert first.environment_run_id != second.environment_run_id
    assert first.started_from_agent_id == second.started_from_agent_id


def test_agent_run_requires_handle_membership_in_the_environment_roster():
    profile = _environment_profile(agent_handle_ids=("handle:other.primary",))
    _, _, _, environment_runs, agent_runs = _run_registries(profiles=(profile,))
    attestation = _environment_attestation(
        "environment-run:synthetic:001",
        profile.environment_profile_id,
    )
    environment_runs.register(attestation)

    with pytest.raises(ValueError, match="not in environment profile roster"):
        agent_runs.attach(
            agent_run_id="agent-run:synthetic:001",
            environment_run_id=attestation.environment_run_id,
            agent_handle_id="handle:synthetic.worker.primary",
        )


class _InactiveEnvironmentRuns:
    def __init__(self, environment_run: EnvironmentRun) -> None:
        self._environment_run = environment_run

    def get(self, environment_run_id: str) -> EnvironmentRun:
        assert environment_run_id == self._environment_run.environment_run_id
        return self._environment_run


def test_agent_run_requires_an_active_environment_run():
    _, handles, profiles, _, _ = _run_registries()
    attestation = _environment_attestation(
        "environment-run:synthetic:closed",
        "environment-profile:synthetic:v1",
    )
    inactive = EnvironmentRun(attestation=attestation, status="closed")  # type: ignore[arg-type]
    agent_runs = AgentRunRegistry(
        handles,
        _InactiveEnvironmentRuns(inactive),  # type: ignore[arg-type]
        profiles,
    )

    with pytest.raises(ValueError, match="environment run is not active"):
        agent_runs.attach(
            agent_run_id="agent-run:synthetic:001",
            environment_run_id=attestation.environment_run_id,
            agent_handle_id="handle:synthetic.worker.primary",
        )
