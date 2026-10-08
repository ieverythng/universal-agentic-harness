import pytest
from dataclasses import replace

from ab_harness.agent_configuration import (
    AgentRoleConfiguration,
    AgentRoleConfigurationRegistry,
)
from ab_harness.agent_configuration import (
    ModelConfiguration,
    ModelConfigurationRegistry,
)
from ab_harness.agent_identity import AgentManifest, AgentRegistry, AgentHandleRegistry
from ab_harness.contracts import AgentRoleSpec, AbstractionFrame, ABControlBand
from ab_harness.environment_profiles import EnvironmentProfileRegistry
from ab_harness.environment_runs import EnvironmentRunRegistry

from ab_harness.agent_identity import AgentRunRegistry
from ab_harness.lifecycle import LifecycleLedger
from tests.test_agent_identity import _environment_attestation
from tests.test_agent_identity import _run_registries
from tests.test_agent_identity import _environment_profile


def _runtime_fixture(tmp_path):
    from ab_harness.model_allocator import (
        FixedModelAllocator,
        FixedModelInstance,
        ResourceSnapshot,
    )

    roles, models = AgentRoleConfigurationRegistry(), ModelConfigurationRegistry()
    role = roles.register(
        AgentRoleConfiguration(
            role=AgentRoleSpec("worker", ("operation",), ABControlBand(1, 1, 1)),
            primary_frame=AbstractionFrame(
                "synthetic", "workspace", "AB1 transforms", "registry:v1"
            ),
            domain_contract_pack_id="domain-pack:synthetic:v1",
            domain_contract_pack_revision="sha256:domain-pack-revision",
            projected_object_ids=("transform",),
            required_model_capabilities=("json_schema",),
            minimum_context_tokens=100,
        )
    )
    model = models.register(
        ModelConfiguration(
            provider_kind="fake",
            endpoint_ref="fake_local",
            model_artifact="test-model",
            model_revision="v1",
            capabilities=("json_schema",),
            max_context_tokens=4096,
        )
    )
    manifest = AgentManifest(
        role.role_configuration_id,
        model.model_configuration_id,
        "prompt:v1",
        "harness:v1",
        (),
    )
    agents = AgentRegistry()
    agents.register(manifest)
    handles = AgentHandleRegistry(agents)
    handles.register(
        agent_handle_id="handle:synthetic.worker.primary",
        candidate_agent_id=manifest.agent_id,
        fidelity_evidence_refs=("qualification:v1",),
    )
    profiles = EnvironmentProfileRegistry((_environment_profile(),))
    environments = EnvironmentRunRegistry(profiles)
    attestation = _environment_attestation(
        "environment-run:synthetic:001", "environment-profile:synthetic:v1"
    )
    environments.register(attestation)
    ledger = LifecycleLedger(
        tmp_path / "runtime.jsonl", clock=lambda: "2026-10-04T10:00:00Z"
    )
    runs = AgentRunRegistry(handles, environments, profiles, ledger=ledger)
    run = runs.attach(
        agent_run_id="agent-run:synthetic:001",
        environment_run_id=attestation.environment_run_id,
        agent_handle_id="handle:synthetic.worker.primary",
    )
    instance = FixedModelInstance(
        "instance:local:001",
        model.model_configuration_id,
        "host:local",
        4096,
        8192,
        4096,
        "runtime:fake",
    )
    snapshot = ResourceSnapshot(
        "snapshot:001",
        "host:local",
        16384,
        8192,
        "2026-10-04T10:00:00Z",
        ("capacity:fixture",),
    )
    allocator = FixedModelAllocator(
        ledger=ledger,
        roles=roles,
        models=models,
        instance=instance,
        clock=lambda: "2026-10-04T10:00:00Z",
    )
    return allocator, runs, ledger, run, snapshot


def test_fixed_lease_is_exact_idempotent_and_recorded_without_provider_work(tmp_path):
    allocator, runs, ledger, run, snapshot = _runtime_fixture(tmp_path)
    assert len(ledger.events()) == 1
    decision = allocator.acquire(
        run.agent_run_id,
        request_id="request:001",
        context_tokens=1024,
        duration_seconds=60,
        resources=snapshot,
    )
    assert decision.accepted
    assert decision.lease.agent_run_id == run.agent_run_id
    assert runs.get(run.agent_run_id).status == "leased"
    assert (
        allocator.acquire(
            run.agent_run_id,
            request_id="request:001",
            context_tokens=1024,
            duration_seconds=60,
            resources=snapshot,
        )
        == decision
    )
    with pytest.raises(ValueError, match="request identity"):
        allocator.acquire(
            run.agent_run_id,
            request_id="request:001",
            context_tokens=2048,
            duration_seconds=60,
            resources=snapshot,
        )
    assert [event.event_type for event in ledger.events()] == [
        "agent_run_attached",
        "model_lease_acquired",
    ]
    reopened = LifecycleLedger(ledger.path)
    assert reopened.replay_agent_run(run.agent_run_id).model_lease == decision.lease


@pytest.mark.parametrize("changed_artifact", ("instance", "snapshot"))
def test_allocation_cannot_reuse_an_owner_identity_with_changed_content(
    tmp_path, changed_artifact
):
    allocator, _, ledger, run, snapshot = _runtime_fixture(tmp_path)
    lease = allocator.acquire(
        run.agent_run_id,
        request_id="request:001",
        context_tokens=1024,
        duration_seconds=60,
        resources=snapshot,
    ).lease
    allocator.release(lease, reason_code="operator_release")
    before = ledger.events()
    if changed_artifact == "instance":
        allocator.instance = replace(allocator.instance, required_ram_mib=1024)
    else:
        snapshot = replace(snapshot, available_ram_mib=32768)
    with pytest.raises(ValueError, match="identity cannot change"):
        allocator.acquire(
            run.agent_run_id,
            request_id="request:002",
            context_tokens=1024,
            duration_seconds=60,
            resources=snapshot,
        )
    assert ledger.events() == before


def test_readiness_and_release_preserve_logical_activation_and_fence_old_lease(
    tmp_path,
):
    allocator, runs, ledger, run, snapshot = _runtime_fixture(tmp_path)
    lease = allocator.acquire(
        run.agent_run_id,
        request_id="request:001",
        context_tokens=1024,
        duration_seconds=60,
        resources=snapshot,
    ).lease
    assert lease is not None
    readiness = allocator.preflight(
        lease,
        readiness_owner_id="runtime:fake",
        observed_instance_id="instance:local:001",
        observed_model_configuration_id=lease.model_configuration_id,
        observed_at="2026-10-04T10:00:00Z",
        attempts_used=1,
        elapsed_seconds=1,
        succeeded=True,
        evidence_refs=("probe:001",),
    )
    assert readiness.accepted
    assert runs.get(run.agent_run_id).status == "ready"
    released = allocator.release(lease, reason_code="inference_complete")
    assert runs.get(run.agent_run_id).status == "standby"
    assert runs.get(run.agent_run_id).started_from_agent_id == run.started_from_agent_id
    assert allocator.release(lease, reason_code="inference_complete") == released
    with pytest.raises(ValueError, match="active model lease"):
        allocator.preflight(
            lease,
            readiness_owner_id="runtime:fake",
            observed_instance_id="instance:local:001",
            observed_model_configuration_id=lease.model_configuration_id,
            observed_at="2026-10-04T10:00:00Z",
            attempts_used=1,
            elapsed_seconds=1,
            succeeded=True,
            evidence_refs=("probe:late",),
        )
    renewed = allocator.acquire(
        run.agent_run_id,
        request_id="request:002",
        context_tokens=1024,
        duration_seconds=60,
        resources=snapshot,
    ).lease
    assert renewed.model_lease_id != lease.model_lease_id
    assert (
        LifecycleLedger(ledger.path).replay_agent_run(run.agent_run_id).model_lease
        == renewed
    )


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("available_ram_mib", 1024, "insufficient_ram"),
        ("available_vram_mib", 1024, "insufficient_vram"),
        ("host_id", "host:other", "resource_host_mismatch"),
        ("observed_at", "2026-10-04T09:59:00Z", "resource_snapshot_not_fresh"),
    ),
)
def test_capacity_rejection_is_recorded_without_lease_or_run_activation(
    tmp_path, field, value, reason
):
    allocator, runs, ledger, run, snapshot = _runtime_fixture(tmp_path)
    decision = allocator.acquire(
        run.agent_run_id,
        request_id="request:rejected",
        context_tokens=1024,
        duration_seconds=60,
        resources=replace(snapshot, **{field: value}),
    )
    assert not decision.accepted
    assert decision.reason_codes == (reason,)
    assert runs.get(run.agent_run_id).status == "attached_standby"
    assert (
        LifecycleLedger(ledger.path).replay_agent_run(run.agent_run_id).model_lease
        is None
    )


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("readiness_owner_id", "runtime:other", "startup_owner_mismatch"),
        ("observed_instance_id", "instance:other", "startup_instance_mismatch"),
        ("observed_model_configuration_id", "model:other", "startup_model_mismatch"),
        ("attempts_used", 3, "startup_probe_budget_exhausted"),
        ("succeeded", False, "startup_probe_failed"),
    ),
)
def test_failed_startup_atomically_releases_capacity_and_returns_to_standby(
    tmp_path, field, value, reason
):
    allocator, runs, ledger, run, snapshot = _runtime_fixture(tmp_path)
    lease = allocator.acquire(
        run.agent_run_id,
        request_id="request:001",
        context_tokens=1024,
        duration_seconds=60,
        resources=snapshot,
    ).lease
    inputs = dict(
        readiness_owner_id="runtime:fake",
        observed_instance_id="instance:local:001",
        observed_model_configuration_id=lease.model_configuration_id,
        observed_at="2026-10-04T10:00:00Z",
        attempts_used=1,
        elapsed_seconds=1,
        succeeded=True,
        evidence_refs=("probe:001",),
    )
    inputs[field] = value
    decision = allocator.preflight(lease, **inputs)
    assert decision.reason_codes == (reason,)
    assert runs.get(run.agent_run_id).status == "standby"
    failed, released = ledger.events()[-2:]
    assert failed.event_type == "startup_preflight_failed"
    assert released.event_type == "model_lease_released"
    assert failed.commit_id == released.commit_id
    assert (
        LifecycleLedger(ledger.path).replay_agent_run(run.agent_run_id).model_lease
        is None
    )


def test_two_open_ledgers_cannot_lease_the_same_fixed_instance(tmp_path):
    from ab_harness.agent_lifecycle import AgentRunAttached
    from ab_harness.model_allocator import FixedModelAllocator

    allocator, _, ledger, run, snapshot = _runtime_fixture(tmp_path)
    replay = ledger.replay_agent_run(run.agent_run_id)
    ledger.record(
        AgentRunAttached(
            run=replace(
                run,
                agent_run_id="agent-run:synthetic:002",
                environment_run_id="environment-run:synthetic:002",
            ),
            manifest=replay.manifest,
            handle_revision=replay.handle_revision,
            profile=replay.profile,
            attestation=replace(
                replay.attestation,
                environment_run_id="environment-run:synthetic:002",
                attestation_id="attestation:002",
            ),
        )
    )
    second_ledger = LifecycleLedger(ledger.path)
    second = FixedModelAllocator(
        ledger=second_ledger,
        roles=allocator.roles,
        models=allocator.models,
        instance=allocator.instance,
        clock=allocator.clock,
    )
    allocator.acquire(
        run.agent_run_id,
        request_id="request:001",
        context_tokens=1024,
        duration_seconds=60,
        resources=snapshot,
    )
    rejected = second.acquire(
        "agent-run:synthetic:002",
        request_id="request:001",
        context_tokens=1024,
        duration_seconds=60,
        resources=snapshot,
    )
    assert rejected.reason_codes == ("model_instance_busy",)
    assert (
        second_ledger.replay_agent_run("agent-run:synthetic:002").status
        == "attached_standby"
    )


def test_fixed_allocators_cannot_double_reserve_a_host_under_distinct_instance_ids(
    tmp_path,
):
    from ab_harness.agent_lifecycle import AgentRunAttached
    from ab_harness.model_allocator import FixedModelAllocator

    allocator, _, ledger, run, snapshot = _runtime_fixture(tmp_path)
    replay = ledger.replay_agent_run(run.agent_run_id)
    ledger.record(
        AgentRunAttached(
            replace(
                run,
                agent_run_id="agent-run:second",
                environment_run_id="environment-run:second",
            ),
            replay.manifest,
            replay.handle_revision,
            replay.profile,
            replace(
                replay.attestation,
                environment_run_id="environment-run:second",
                attestation_id="attestation:second",
            ),
        )
    )
    allocator.acquire(
        run.agent_run_id,
        request_id="request:001",
        context_tokens=1024,
        duration_seconds=60,
        resources=snapshot,
    )
    second = FixedModelAllocator(
        ledger=LifecycleLedger(ledger.path),
        roles=allocator.roles,
        models=allocator.models,
        instance=replace(allocator.instance, model_instance_id="instance:other"),
        clock=allocator.clock,
    )
    rejected = second.acquire(
        "agent-run:second",
        request_id="request:001",
        context_tokens=1024,
        duration_seconds=60,
        resources=snapshot,
    )
    assert rejected.reason_codes == ("fixed_host_busy",)


@pytest.mark.parametrize("invalid", (True, 1.5, float("nan"), float("inf")))
def test_invalid_lease_limits_fail_before_any_allocation_event(tmp_path, invalid):
    allocator, _, ledger, run, snapshot = _runtime_fixture(tmp_path)
    with pytest.raises(ValueError, match="finite integer"):
        allocator.acquire(
            run.agent_run_id,
            request_id="request:001",
            context_tokens=invalid,
            duration_seconds=60,
            resources=snapshot,
        )
    with pytest.raises(ValueError, match="finite integer"):
        allocator.acquire(
            run.agent_run_id,
            request_id="request:001",
            context_tokens=1024,
            duration_seconds=invalid,
            resources=snapshot,
        )
    assert len(ledger.events()) == 1


def test_released_acquisition_request_cannot_return_apparent_new_authority(tmp_path):
    allocator, _, ledger, run, snapshot = _runtime_fixture(tmp_path)
    lease = allocator.acquire(
        run.agent_run_id,
        request_id="request:001",
        context_tokens=1024,
        duration_seconds=60,
        resources=snapshot,
    ).lease
    allocator.release(lease, reason_code="done")
    from ab_harness.model_allocator import FixedModelAllocator

    restarted = FixedModelAllocator(
        ledger=LifecycleLedger(ledger.path),
        roles=allocator.roles,
        models=allocator.models,
        instance=allocator.instance,
        clock=allocator.clock,
    )
    with pytest.raises(ValueError, match="released acquisition request"):
        restarted.acquire(
            run.agent_run_id,
            request_id="request:001",
            context_tokens=1024,
            duration_seconds=60,
            resources=snapshot,
        )


def test_direct_attachment_cannot_redefine_an_existing_environment_activation(tmp_path):
    from ab_harness.agent_identity import AgentRun, AgentHandleRevision
    from ab_harness.agent_lifecycle import AgentRunAttached

    _, _, ledger, run, _ = _runtime_fixture(tmp_path)
    replay = ledger.replay_agent_run(run.agent_run_id)
    handle = AgentHandleRevision(
        "handle:second.primary",
        replay.manifest.agent_id,
        replay.manifest.role_configuration_id,
        ("fidelity:second",),
    )
    profile = replace(
        replay.profile,
        agent_handle_ids=(*replay.profile.agent_handle_ids, handle.agent_handle_id),
        native_runtime_revision="runtime:changed",
    )
    changed = AgentRunAttached(
        AgentRun(
            "agent-run:second",
            run.environment_run_id,
            handle.agent_handle_id,
            handle.revision_id,
            replay.manifest.agent_id,
        ),
        replay.manifest,
        handle,
        profile,
        replace(
            replay.attestation, native_runtime_revision=profile.native_runtime_revision
        ),
    )
    with pytest.raises(ValueError, match="environment identity"):
        ledger.record(changed)


def test_terminated_run_releases_model_and_allows_a_new_activation(tmp_path):
    allocator, runs, ledger, run, snapshot = _runtime_fixture(tmp_path)
    allocator.acquire(
        run.agent_run_id,
        request_id="request:001",
        context_tokens=1024,
        duration_seconds=60,
        resources=snapshot,
    )
    ended = runs.terminate(
        run.agent_run_id,
        reason_code="operator_shutdown",
        terminated_at="2026-10-04T10:00:01Z",
    )
    assert ended.status == "terminated"
    assert ledger.replay_agent_run(run.agent_run_id).model_lease is None
    assert runs.get(run.agent_run_id).status == "terminated"
    restarted = runs.attach(
        agent_run_id="agent-run:synthetic:restart",
        environment_run_id=run.environment_run_id,
        agent_handle_id=run.agent_handle_id,
    )
    assert restarted.started_from_agent_id == run.started_from_agent_id
    assert restarted.agent_run_id != run.agent_run_id


def test_attachment_is_an_agent_scoped_fact_and_survives_registry_restart(tmp_path):
    _, handles, profiles, environments, _ = _run_registries()
    attestation = _environment_attestation(
        "environment-run:synthetic:001", "environment-profile:synthetic:v1"
    )
    environments.register(attestation)
    path = tmp_path / "lifecycle.jsonl"
    ledger = LifecycleLedger(path, clock=lambda: "2026-10-04T10:00:00Z")
    runs = AgentRunRegistry(handles, environments, profiles, ledger=ledger)

    attached = runs.attach(
        agent_run_id="agent-run:synthetic:001",
        environment_run_id=attestation.environment_run_id,
        agent_handle_id="handle:synthetic.worker.primary",
    )

    (event,) = ledger.events()
    assert event.event_type == "agent_run_attached"
    assert event.schema_version == "uah.trace_event/v2"
    assert event.event_scope == "agent"
    assert event.agent_run_id == attached.agent_run_id
    assert event.task_id is None
    assert event.trace_id is None
    reopened = LifecycleLedger(path)
    restarted = AgentRunRegistry(handles, environments, profiles, ledger=reopened)
    assert restarted.get(attached.agent_run_id) == attached
    assert reopened.replay_agent_run(attached.agent_run_id).status == "attached_standby"
    with pytest.raises(ValueError, match="already registered"):
        restarted.attach(
            agent_run_id=attached.agent_run_id,
            environment_run_id=attestation.environment_run_id,
            agent_handle_id=attached.agent_handle_id,
        )
