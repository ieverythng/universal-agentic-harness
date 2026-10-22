from dataclasses import FrozenInstanceError, fields, replace
import hashlib
import json
from pathlib import Path

import pytest

from ab_harness.model_allocator import ModelLease
from ab_harness.model_invocation import (
    ModelInvocationAuthority,
    ModelInvocationRequest,
    RawModelOutput,
)
from ab_harness.model_invocation import ModelInvocationFailure
from ab_harness.model_invocation import ModelInvocationStarted
from ab_harness.prompt_compiler import CompiledPrompt, PromptMessage


LEGACY_V1_FIXTURES = Path(__file__).parent / "fixtures" / "model_invocation_legacy_v1"


def _request():
    lease = ModelLease(
        "acquisition:1",
        "actor:1",
        "environment:1",
        "agent:1",
        "instance:1",
        "model:1",
        1024,
        "2026-10-04T10:00:00Z",
        "2026-10-04T10:01:00Z",
    )
    prompt = CompiledPrompt(
        compiled_task_id="compiled-task:1",
        agent_id="agent:1",
        role_configuration_id="role:1",
        prompt_pack_id="pack:1",
        environment_id="workspace:1",
        runtime_mode="fake",
        messages=(
            PromptMessage("system", "Propose one operation."),
            PromptMessage("user", "Write a note."),
        ),
        output_schema_json='{"type":"object"}',
        source_contracts=(),
        environment_run_id="environment:1",
        task_id="task:1",
        trace_id="trace:1",
        role_id="worker",
        frame_id="workspace",
        registry_version="registry:1",
        domain_contract_pack_revision="domain:revision:1",
    )
    return ModelInvocationRequest(
        invocation_id="invocation:1",
        lease=lease,
        compiled_prompt=prompt,
        requested_at="2026-10-04T10:00:01Z",
        task_id="task:1",
        trace_id="trace:1",
    )


@pytest.mark.parametrize("spoofed", (False, True))
def test_invocation_rejects_prompt_verification_overrides_before_provider_or_ledger_changes(
    tmp_path, spoofed
):
    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    original_events = ledger.events()
    authentic_payload = json.loads(json.dumps(prompt.to_dict()))

    class SpoofedPrompt(CompiledPrompt):
        def verify_identity(self):
            pass

        def to_dict(self):
            return authentic_payload

    if spoofed:
        prompt = SpoofedPrompt(
            **{
                item.name: getattr(prompt, item.name)
                for item in fields(prompt)
                if item.init
            }
        )
        object.__setattr__(
            prompt,
            "messages",
            (
                PromptMessage(
                    "system", "An instruction absent from the recorded prompt."
                ),
                PromptMessage("user", "An unrecorded task."),
            ),
        )

    delivered = []
    delivered_prompts = []

    class Provider:
        def invoke(self, request):
            delivered_prompts.append(request.compiled_prompt.to_dict())
            delivered.append(
                [
                    {"role": message.role, "content": message.content}
                    for message in request.compiled_prompt.messages
                ]
            )
            return {
                "output_type": "operation",
                "object_id": "write_note",
                "arguments": {"text": "hello"},
            }

    authority = _authority(
        ledger, Provider(), clock=lambda: "2026-10-04T10:00:02Z"
    )
    if spoofed:
        with pytest.raises(TypeError, match="concrete CompiledPrompt"):
            authority.invoke(lease, prompt, invocation_id="invocation:prompt-integrity")
        assert delivered == []
        assert ledger.events() == original_events
    else:
        output = authority.invoke(
            lease, prompt, invocation_id="invocation:prompt-integrity"
        )
        assert isinstance(output, RawModelOutput)
        assert delivered == [authentic_payload["messages"]]
        assert json.loads(json.dumps(delivered_prompts[0])) == authentic_payload
        started = next(
            event
            for event in ledger.events()
            if event.event_type == "model_invocation_started"
        )
        assert started.data["request"]["compiled_prompt"] == authentic_payload


def test_invocation_rejects_shadowed_prompt_methods_before_provider_or_ledger_changes(
    tmp_path,
):
    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    original_events = ledger.events()
    recorded_prompt = json.loads(json.dumps(prompt.to_dict()))
    object.__setattr__(
        prompt,
        "messages",
        (
            PromptMessage("system", "Unrecorded system instruction."),
            PromptMessage("user", "Unrecorded request."),
        ),
    )
    object.__setattr__(prompt, "verify_identity", lambda: None)
    object.__setattr__(prompt, "to_dict", lambda: recorded_prompt)

    class Provider:
        calls = 0

        def invoke(self, request):
            self.calls += 1
            return {"output_type": "operation", "object_id": "write_note"}

    provider = Provider()
    authority = _authority(
        ledger, provider, clock=lambda: "2026-10-04T10:00:02Z"
    )

    with pytest.raises(ValueError, match="compiled prompt identity"):
        authority.invoke(lease, prompt, invocation_id="invocation:shadowed-prompt")

    assert provider.calls == 0
    assert ledger.events() == original_events


def test_raw_model_output_is_immutable_untrusted_json_with_verified_request_lineage():
    request = _request()
    output = RawModelOutput.capture(
        request,
        {"object_id": "write_note", "arguments": {"text": "hello"}},
        completed_at="2026-10-04T10:00:02Z",
    )

    assert output.invocation_id == "invocation:1"
    assert output.output == {"object_id": "write_note", "arguments": {"text": "hello"}}
    assert "execution_lease_id" not in output.to_dict()
    assert RawModelOutput.from_dict(output.to_dict()) == output
    with pytest.raises(FrozenInstanceError):
        output.output_json = "{}"
    serialized = output.to_dict()
    serialized["output_json"] = '{"object_id":"delete_all"}'
    with pytest.raises(ValueError, match="identity"):
        RawModelOutput.from_dict(serialized)


def test_provider_failure_records_type_and_hashed_reference_without_sensitive_exception_text():
    failure = ModelInvocationFailure.capture(
        _request(),
        RuntimeError("Authorization: Bearer secret-provider-key"),
        failed_at="2026-10-04T10:00:02Z",
    )
    assert failure.failure_code == "RuntimeError"
    assert failure.diagnostic_ref.startswith("invocation-diagnostic:sha256:")
    assert "secret-provider-key" not in json.dumps(failure.to_dict())
    assert ModelInvocationFailure.from_dict(failure.to_dict()) == failure


def test_failure_diagnostic_reference_cannot_embed_plaintext_under_a_hash_prefix():
    with pytest.raises(ValueError, match="hashed reference"):
        ModelInvocationFailure(
            _request(),
            "RuntimeError",
            "invocation-diagnostic:sha256:secret-provider-key",
            "2026-10-04T10:00:02Z",
        )


@pytest.mark.parametrize("units", (2,))
def test_invocation_start_requires_exactly_one_integer_model_call(units):
    from ab_harness.runtime_controls import BudgetDecision

    request = _request()
    budget = BudgetDecision.issue(
        compiled_task_id=request.compiled_task_id,
        environment_run_id=request.environment_run_id,
        task_id=request.task_id,
        trace_id=request.trace_id,
        resource="model_call",
        subject_id=request.invocation_id,
        units=units,
        limit=2,
        consumed_before=0,
        consumed_after=units,
        outcome="granted",
        reason_code="within_budget",
    )
    with pytest.raises(ValueError, match="exact granted model-call budget"):
        ModelInvocationStarted(request, budget)


def test_invocation_start_cannot_charge_another_invocation_budget():
    from ab_harness.runtime_controls import BudgetDecision

    request = _request()
    budget = BudgetDecision.issue(
        compiled_task_id=request.compiled_task_id,
        environment_run_id=request.environment_run_id,
        task_id=request.task_id,
        trace_id=request.trace_id,
        resource="model_call",
        subject_id="invocation:different",
        units=1,
        limit=2,
        consumed_before=0,
        consumed_after=1,
        outcome="granted",
        reason_code="within_budget",
    )
    with pytest.raises(ValueError, match="exact granted model-call budget"):
        ModelInvocationStarted(request, budget)


def _invocation_fixture(tmp_path, *, model_calls=2, return_compiled=False):
    from ab_harness.agent_configuration import (
        AgentRoleConfiguration,
        AgentRoleConfigurationRegistry,
    )
    from ab_harness.agent_configuration import (
        ModelConfiguration,
        ModelConfigurationRegistry,
    )
    from ab_harness.agent_identity import (
        AgentManifest,
        AgentRegistry,
        AgentHandleRegistry,
        AgentRunRegistry,
    )
    from ab_harness.bindings import BindingCatalog
    from ab_harness.contracts import (
        ABControlBand,
        ABImplementationBinding,
        ABObjectView,
        AbstractionFrame,
        AgentRoleSpec,
    )
    from ab_harness.domain_contracts import (
        DomainContractPack,
        DomainEffectRule,
        TaskIngressRule,
    )
    from ab_harness.environment_ingress import EnvironmentIngress
    from ab_harness.environment_profiles import (
        EnvironmentProfile,
        EnvironmentProfileRegistry,
    )
    from ab_harness.environment_runs import (
        EnvironmentRunAttestation,
        EnvironmentRunRegistry,
    )
    from ab_harness.lifecycle import LifecycleLedger
    from ab_harness.model_allocator import (
        FixedModelAllocator,
        FixedModelInstance,
        ResourceSnapshot,
    )
    from ab_harness.prompt_compiler import (
        ConfiguredPromptSourceOwner,
        PromptCompiler,
        PromptPack,
        PromptSourceSet,
    )
    from ab_harness.registry import RegistrySnapshot
    from ab_harness.schema_validation import ArgumentField, ObjectArgumentSchema
    from ab_harness.task_compiler import (
        TaskBudgets,
        TaskEffectRequest,
        TaskSpec,
        TaskSpecCompiler,
    )
    from ab_harness.task_ingress_authority import TaskIngressAuthority
    from ab_harness.task_registry import EnvironmentTaskRegistry

    now = "2026-10-04T10:00:00Z"
    registry = RegistrySnapshot(
        (
            ABObjectView(
                "write_note",
                1,
                "skill",
                "workspace",
                "notes",
                expected_effects=("note_written",),
                observable_success=("note_written",),
                runtime_callable=True,
            ),
        ),
        source="synthetic:registry",
        version="registry:notes:v1",
    )
    role = AgentRoleSpec("note_writer", ("operation",), ABControlBand(1, 1, 1))
    frame = AbstractionFrame(
        "notes", "workspace", "one note mutation", registry.version
    )
    domain = DomainContractPack.issue(
        domain_contract_pack_id="domain:notes",
        frame_id=frame.frame_id,
        registry_version=registry.version,
        allowed_role_ids=(role.role_id,),
        supported_task_type_ids=("write_note",),
        ingress_rules=(
            TaskIngressRule("request:notes", "request", "start_task", "request_id"),
        ),
        effect_rules=(
            DomainEffectRule("note_written", "write_note", "notes", "terminal"),
        ),
    )
    roles, models = AgentRoleConfigurationRegistry(), ModelConfigurationRegistry()
    configuration = roles.register(
        AgentRoleConfiguration(
            role,
            frame,
            domain.domain_contract_pack_id,
            domain.revision,
            ("write_note",),
        )
    )
    model = models.register(
        ModelConfiguration("fake", "fake_local", "test-model", "v1", (), 4096)
    )
    pack = PromptPack(
        "uah.protocol/v1",
        "Propose one note operation.",
        "The workspace owns note evidence.",
    )
    manifest = AgentManifest(
        configuration.role_configuration_id,
        model.model_configuration_id,
        pack.prompt_pack_id,
        "build:v1",
        (),
    )
    agents = AgentRegistry()
    agents.register(manifest)
    handles = AgentHandleRegistry(agents)
    handle = "notes.writer.primary"
    handles.register(
        agent_handle_id=handle,
        candidate_agent_id=manifest.agent_id,
        fidelity_evidence_refs=("qualification:1",),
    )
    profile = EnvironmentProfile(
        "profile:notes",
        domain.domain_contract_pack_id,
        domain.revision,
        "runtime:v1",
        "notes",
        ("request:notes",),
        (handle,),
    )
    profiles = EnvironmentProfileRegistry((profile,))
    environments = EnvironmentRunRegistry(profiles)
    environment = environments.register(
        EnvironmentRunAttestation(
            "environment:notes",
            profile.environment_profile_id,
            domain.revision,
            "runtime:v1",
            "notes",
            "attestation:notes",
            now,
            ("ready:1",),
        )
    )
    ledger = LifecycleLedger(tmp_path / "invocation.jsonl", clock=lambda: now)
    runs = AgentRunRegistry(handles, environments, profiles, ledger=ledger)
    run = runs.attach(
        agent_run_id="actor:notes",
        environment_run_id=environment.environment_run_id,
        agent_handle_id=handle,
    )
    ingress = TaskIngressAuthority(
        environment_profile_id=profile.environment_profile_id,
        domain_contract_pack=domain,
        lifecycle_ledger=ledger,
    ).admit(
        environment,
        EnvironmentIngress(
            "ingress:notes",
            environment.environment_run_id,
            "request:notes",
            "request",
            "artifact:request",
            (("request_id", "task:note"),),
            now,
        ),
    )
    task_spec = TaskSpec(
        ingress.task_id,
        ingress.trace_id,
        "write_note",
        role.role_id,
        frame.frame_id,
        domain.revision,
        "Write a note",
        (TaskEffectRequest("written", "note_written", "required"),),
        (),
        TaskBudgets(60, model_calls, 2),
    )
    compiled = TaskSpecCompiler().compile(
        task_ingress_decision=ingress,
        task_spec=task_spec,
        role=role,
        frame=frame,
        registry=registry,
        domain_contract_pack=domain,
        task_registry=EnvironmentTaskRegistry(ledger),
    )
    ledger.record(compiled)
    binding = ABImplementationBinding(
        "binding:write",
        "write_note",
        "notes_environment",
        "notes",
        "python_method",
        "notes.write",
        "binding:v1",
        "schema:write",
        "schema:result",
        "evidence:notes",
        ("fake",),
        "approved",
    )
    schema = ObjectArgumentSchema.issue(
        schema_ref="schema:write",
        fields=(ArgumentField("text", "string"),),
        required=("text",),
    )
    prompt = PromptCompiler().compile(
        compiled_task=compiled,
        manifest=manifest,
        role_configuration=configuration,
        prompt_pack=pack,
        binding_catalog=BindingCatalog(registry, (binding,)),
        argument_schemas=(schema,),
        environment_id="notes_environment",
        runtime_mode="fake",
    )
    source_owner = ConfiguredPromptSourceOwner(
        (
            PromptSourceSet(
                task_spec,
                compiled,
                manifest,
                configuration,
                pack,
                registry,
                (binding,),
                (schema,),
                "notes_environment",
                "fake",
            ),
        )
    )
    instance = FixedModelInstance(
        "instance:notes",
        model.model_configuration_id,
        "host:local",
        4096,
        1,
        1,
        "runtime:notes",
    )
    allocator = FixedModelAllocator(
        ledger=ledger, roles=roles, models=models, instance=instance, clock=lambda: now
    )
    snapshot = ResourceSnapshot(
        "snapshot:notes", "host:local", 1024, 1024, now, ("capacity:1",)
    )
    lease = allocator.acquire(
        run.agent_run_id,
        request_id="acquisition:notes",
        context_tokens=1024,
        duration_seconds=60,
        resources=snapshot,
    ).lease
    allocator.preflight(
        lease,
        readiness_owner_id="runtime:notes",
        observed_instance_id=instance.model_instance_id,
        observed_model_configuration_id=model.model_configuration_id,
        observed_at=now,
        attempts_used=1,
        elapsed_seconds=1,
        succeeded=True,
        evidence_refs=("probe:1",),
    )
    result = ledger, allocator, lease, prompt
    ledger._test_prompt_source_owner = source_owner
    return (*result, compiled) if return_compiled else result


class _RecordedProvider:
    def __init__(self, ledger):
        self.ledger = ledger
        self.calls = 0
        self.requests = []

    def invoke(self, request):
        self.calls += 1
        self.requests.append(request)
        events = self.ledger.events()
        assert events[-1].event_type == "model_invocation_started"
        assert events[-2].event_type == "budget_granted"
        assert events[-1].commit_id == events[-2].commit_id
        assert self.ledger.replay_agent_run(request.agent_run_id).status == "invoking"
        return {
            "output_type": "operation",
            "object_id": "write_note",
            "arguments": {"text": "hello"},
        }


def _authority(ledger, provider, *, clock=None, source_owner=None):
    return ModelInvocationAuthority(
        ledger,
        provider,
        prompt_source_owner=(
            source_owner
            if source_owner is not None
            else ledger._test_prompt_source_owner
        ),
        clock=clock,
    )


def test_provider_call_records_budget_and_start_before_untrusted_output_and_is_idempotent(
    tmp_path,
):
    from ab_harness.lifecycle import LifecycleLedger

    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    provider = _RecordedProvider(ledger)
    authority = _authority(
        ledger, provider, clock=lambda: "2026-10-04T10:00:02Z"
    )
    output = authority.invoke(lease, prompt, invocation_id="invocation:1")

    assert isinstance(output, RawModelOutput)
    assert output.output["arguments"] == {"text": "hello"}
    started = next(
        event for event in ledger.events() if event.event_type == "model_invocation_started"
    )
    source_refs = started.data["request"]["source_references"]
    assert any(reference.startswith("task-spec:sha256:") for reference in source_refs)
    assert "task-projection:" + prompt.compiled_task_id in source_refs
    assert "prompt-pack:" + prompt.prompt_pack_id in source_refs
    assert any(reference.startswith("binding:sha256:") for reference in source_refs)
    assert any(reference.startswith("input-schema:sha256:") for reference in source_refs)
    configured_sources = ledger._test_prompt_source_owner.resolve(
        prompt.compiled_task_id, lease.agent_id, prompt.frame_id
    )
    assert provider.requests[0].compiled_prompt == configured_sources.compile()
    assert provider.requests[0].source_references == configured_sources.references(
        prompt
    )
    assert (
        ModelInvocationRequest.from_dict(started.data["request"]).compiled_prompt
        == configured_sources.compile()
    )
    assert ledger.replay_agent_run(lease.agent_run_id).status == "ready"
    assert ledger.replay(prompt.trace_id).terminal_status is None
    assert not any(
        event.event_type
        in {"proposal_normalized", "domain_admission_leased", "evidence_issued"}
        for event in ledger.events()
    )
    reopened = LifecycleLedger(ledger.path)
    from ab_harness.prompt_compiler import ConfiguredPromptSourceOwner

    replayed = _authority(
        reopened,
        provider,
        source_owner=ConfiguredPromptSourceOwner((), frame_id=prompt.frame_id),
    ).invoke(
        lease, prompt, invocation_id="invocation:1"
    )
    assert replayed == output
    assert provider.calls == 1


def test_completed_call_can_release_capacity_and_return_the_same_actor_to_standby(
    tmp_path,
):
    ledger, allocator, lease, prompt = _invocation_fixture(tmp_path)
    _authority(
        ledger, _RecordedProvider(ledger), clock=lambda: "2026-10-04T10:00:02Z"
    ).invoke(
        lease,
        prompt,
        invocation_id="invocation:1",
    )
    allocator.clock = lambda: "2026-10-04T10:00:03Z"
    allocator.release(lease, reason_code="inference_complete")
    assert ledger.replay_agent_run(lease.agent_run_id).status == "standby"


def test_exhausted_model_budget_never_starts_provider_work_and_replays_idempotently(
    tmp_path,
):
    from ab_harness.runtime_controls import BudgetExhaustedError

    ledger, _, lease, prompt = _invocation_fixture(tmp_path, model_calls=0)
    provider = _RecordedProvider(ledger)
    authority = _authority(
        ledger, provider, clock=lambda: "2026-10-04T10:00:02Z"
    )
    for _ in range(2):
        with pytest.raises(BudgetExhaustedError, match="model_call"):
            authority.invoke(lease, prompt, invocation_id="invocation:over-budget")
    assert provider.calls == 0
    assert [event.event_type for event in ledger.events()].count(
        "budget_exhausted"
    ) == 1
    assert ledger.replay_agent_run(lease.agent_run_id).status == "ready"


@pytest.mark.parametrize("response", ("exception", "nonfinite"))
def test_provider_failure_is_replayable_without_secret_text_or_refunding_a_model_call(
    tmp_path, response
):
    from ab_harness.lifecycle import LifecycleLedger

    ledger, _, lease, prompt = _invocation_fixture(tmp_path)

    class FailingProvider:
        calls = 0

        def invoke(self, request):
            self.calls += 1
            if response == "exception":
                raise RuntimeError("Bearer secret-provider-key")
            return {"output": float("nan")}

    provider = FailingProvider()
    authority = _authority(
        ledger, provider, clock=lambda: "2026-10-04T10:00:02Z"
    )
    failure = authority.invoke(lease, prompt, invocation_id="invocation:failed")
    assert isinstance(failure, ModelInvocationFailure)
    assert "secret-provider-key" not in ledger.path.read_text()
    assert ledger.replay_agent_run(lease.agent_run_id).status == "ready"
    replay = LifecycleLedger(ledger.path).replay(prompt.trace_id)
    assert replay.failure_stage == "model_invocation"
    assert replay.terminal_status is None
    budgets = [event for event in replay.events if event.event_type == "budget_granted"]
    assert len(budgets) == 1
    assert budgets[0].data["consumed_after"] == 1
    assert authority.invoke(lease, prompt, invocation_id="invocation:failed") == failure
    assert provider.calls == 1


def test_expired_lease_does_not_authorize_provider_work_or_consume_task_budget(
    tmp_path,
):
    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    provider = _RecordedProvider(ledger)
    before = ledger.events()
    authority = _authority(
        ledger, provider, clock=lambda: "2026-10-04T10:01:00Z"
    )
    with pytest.raises(ValueError, match="unexpired model lease"):
        authority.invoke(lease, prompt, invocation_id="invocation:expired")
    assert ledger.events() == before
    assert provider.calls == 0


def test_inflight_provider_call_cannot_release_its_model_reservation(tmp_path):
    ledger, allocator, lease, prompt = _invocation_fixture(tmp_path)

    class InflightProvider:
        def invoke(self, request):
            with pytest.raises(ValueError, match="during invocation"):
                allocator.release(request.lease, reason_code="premature_release")
            return {
                "output_type": "operation",
                "object_id": "write_note",
                "arguments": {"text": "safe"},
            }

    result = _authority(
        ledger, InflightProvider(), clock=lambda: "2026-10-04T10:00:02Z"
    ).invoke(
        lease,
        prompt,
        invocation_id="invocation:inflight",
    )
    assert isinstance(result, RawModelOutput)
    assert ledger.replay_agent_run(lease.agent_run_id).model_lease == lease


def test_restart_does_not_repeat_provider_work_for_an_unfinished_invocation(tmp_path):
    from ab_harness.lifecycle import LifecycleLedger

    ledger, _, lease, prompt = _invocation_fixture(tmp_path)

    class InterruptedProvider:
        calls = 0

        def invoke(self, request):
            self.calls += 1
            raise KeyboardInterrupt()

    provider = InterruptedProvider()
    with pytest.raises(KeyboardInterrupt):
        _authority(
            ledger, provider, clock=lambda: "2026-10-04T10:00:02Z"
        ).invoke(
            lease,
            prompt,
            invocation_id="invocation:unfinished",
        )
    reopened = LifecycleLedger(ledger.path)
    assert reopened.replay_agent_run(lease.agent_run_id).status == "invoking"
    with pytest.raises(ValueError, match="automatic retry is forbidden"):
        from ab_harness.prompt_compiler import ConfiguredPromptSourceOwner

        _authority(
            reopened,
            provider,
            source_owner=ConfiguredPromptSourceOwner((), frame_id=prompt.frame_id),
        ).invoke(
            lease, prompt, invocation_id="invocation:unfinished"
        )
    assert provider.calls == 1
    assert [event.event_type for event in reopened.events()].count(
        "budget_granted"
    ) == 1


def test_completed_invocation_identity_cannot_be_reused_for_a_changed_prompt(tmp_path):
    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    provider = _RecordedProvider(ledger)
    authority = _authority(
        ledger, provider, clock=lambda: "2026-10-04T10:00:02Z"
    )
    authority.invoke(lease, prompt, invocation_id="invocation:1")
    changed = replace(
        prompt,
        messages=(prompt.messages[0], PromptMessage("user", "Changed task context")),
    )
    with pytest.raises(ValueError, match="identity cannot change request content"):
        authority.invoke(lease, changed, invocation_id="invocation:1")
    assert provider.calls == 1


@pytest.mark.parametrize("mutation", ("messages", "schema", "source_contract"))
def test_fresh_invocation_rejects_caller_prompt_replacement_before_budget_or_dispatch(
    tmp_path, mutation
):
    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    provider = _RecordedProvider(ledger)
    authority = _authority(
        ledger, provider, clock=lambda: "2026-10-04T10:00:02Z"
    )
    if mutation == "messages":
        changed = replace(
            prompt,
            messages=(prompt.messages[0], PromptMessage("user", "Caller-owned task")),
        )
    elif mutation == "schema":
        changed = replace(prompt, output_schema_json='{"oneOf":[]}')
    else:
        changed = replace(
            prompt,
            source_contracts=(("write_note", "binding:sha256:changed", "schema:changed"),),
        )
    before = ledger.events()

    with pytest.raises(ValueError, match="trusted source revisions"):
        authority.invoke(lease, changed, invocation_id="invocation:caller-replaced")

    assert ledger.events() == before
    assert provider.calls == 0
    assert ledger.replay_agent_run(lease.agent_run_id).status == "ready"


def test_missing_exact_prompt_source_fails_before_budget_or_dispatch(tmp_path):
    from ab_harness.prompt_compiler import ConfiguredPromptSourceOwner

    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    provider = _RecordedProvider(ledger)
    authority = _authority(
        ledger,
        provider,
        source_owner=ConfiguredPromptSourceOwner((), frame_id=prompt.frame_id),
        clock=lambda: "2026-10-04T10:00:02Z",
    )
    before = ledger.events()

    with pytest.raises(LookupError, match="exact prompt source revision is unavailable"):
        authority.invoke(lease, prompt, invocation_id="invocation:source-missing")

    assert ledger.events() == before
    assert provider.calls == 0
    assert ledger.replay_agent_run(lease.agent_run_id).status == "ready"


def test_changed_prompt_source_revision_fails_before_budget_or_dispatch(tmp_path):
    from ab_harness.prompt_compiler import ConfiguredPromptSourceOwner

    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    configured = ledger._test_prompt_source_owner.resolve(
        prompt.compiled_task_id, lease.agent_id, prompt.frame_id
    )
    changed_binding = replace(configured.bindings[0], source_revision="binding:v2")
    changed_sources = replace(configured, bindings=(changed_binding,))
    provider = _RecordedProvider(ledger)
    authority = _authority(
        ledger,
        provider,
        source_owner=ConfiguredPromptSourceOwner((changed_sources,)),
        clock=lambda: "2026-10-04T10:00:02Z",
    )
    before = ledger.events()

    with pytest.raises(ValueError, match="trusted source revisions"):
        authority.invoke(lease, prompt, invocation_id="invocation:changed-source")

    assert ledger.events() == before
    assert provider.calls == 0
    assert ledger.replay_agent_run(lease.agent_run_id).status == "ready"


def test_caller_authored_prompt_with_matching_actor_and_task_is_rejected(tmp_path):
    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    provider = _RecordedProvider(ledger)
    authority = _authority(
        ledger,
        provider,
        clock=lambda: "2026-10-04T10:00:02Z",
    )
    caller_prompt = replace(
        prompt,
        messages=(prompt.messages[0], PromptMessage("user", "caller-authored")),
    )
    before = ledger.events()

    with pytest.raises(ValueError, match="trusted source revisions"):
        authority.invoke(
            lease, caller_prompt, invocation_id="invocation:caller-authored-prompt"
        )

    assert ledger.events() == before
    assert provider.calls == 0
    assert ledger.replay_agent_run(lease.agent_run_id).status == "ready"


def test_shadowed_prompt_pack_source_is_rejected_before_budget_or_dispatch(tmp_path):
    from ab_harness.prompt_compiler import ConfiguredPromptSourceOwner

    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    configured = ledger._test_prompt_source_owner.resolve(
        prompt.compiled_task_id, lease.agent_id, prompt.frame_id
    )
    pack = configured.prompt_pack
    authentic_export = pack.to_dict()
    object.__setattr__(
        pack, "role_instructions", "changed source wording under original ID"
    )
    object.__setattr__(pack, "verify_identity", lambda: None)
    object.__setattr__(pack, "to_dict", lambda: authentic_export)
    provider = _RecordedProvider(ledger)
    before = ledger.events()

    with pytest.raises(ValueError, match="prompt pack identity does not match content"):
        changed_sources = replace(configured, prompt_pack=pack)
        changed_owner = ConfiguredPromptSourceOwner((changed_sources,))
        changed_prompt = changed_owner.resolve(
            prompt.compiled_task_id, lease.agent_id, prompt.frame_id
        ).compile()
        _authority(
            ledger,
            provider,
            clock=lambda: "2026-10-04T10:00:02Z",
            source_owner=changed_owner,
        ).invoke(lease, changed_prompt, invocation_id="invocation:shadowed-source")

    assert ledger.events() == before
    assert provider.calls == 0
    assert ledger.replay_agent_run(lease.agent_run_id).status == "ready"


def test_shadowed_nested_manifest_identity_methods_are_rejected(tmp_path):
    from ab_harness.prompt_compiler import PromptSourceSet

    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    configured = ledger._test_prompt_source_owner.resolve(
        prompt.compiled_task_id, lease.agent_id, prompt.frame_id
    )
    manifest = configured.manifest
    authentic_export = manifest.to_dict()
    object.__setattr__(manifest, "harness_build_id", "changed-build")
    object.__setattr__(manifest, "verify_identity", lambda: None)
    object.__setattr__(manifest, "to_dict", lambda: authentic_export)
    provider = _RecordedProvider(ledger)
    before = ledger.events()

    with pytest.raises(ValueError, match="prompt source identity does not match stored fields"):
        PromptSourceSet(
            task_spec=configured.task_spec,
            compiled_task=configured.compiled_task,
            manifest=manifest,
            role_configuration=configured.role_configuration,
            prompt_pack=configured.prompt_pack,
            registry=configured.registry,
            bindings=configured.bindings,
            argument_schemas=configured.argument_schemas,
            environment_id=configured.environment_id,
            runtime_mode=configured.runtime_mode,
        )

    assert ledger.events() == before
    assert provider.calls == 0
    assert ledger.replay_agent_run(lease.agent_run_id).status == "ready"


@pytest.mark.parametrize("attack", ("substituted_prompt", "fabricated_references"))
def test_raw_model_invocation_start_cannot_claim_source_owner_issuance(
    tmp_path, attack
):
    from ab_harness.runtime_controls import TaskBudgetAuthority

    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    owner = ledger._test_prompt_source_owner
    configured = owner.resolve(prompt.compiled_task_id, lease.agent_id, prompt.frame_id)
    if attack == "substituted_prompt":
        unissued_prompt = replace(
            prompt,
            messages=(prompt.messages[0], PromptMessage("user", "Caller-supplied intent")),
        )
        references = configured.references(prompt)
    else:
        unissued_prompt = prompt
        references = tuple(
            "task-spec:sha256:not-a-digest"
            if item.startswith("task-spec:sha256:")
            else "registry-content:sha256:forged"
            if item.startswith("registry-content:sha256:")
            else item
            for item in configured.references(prompt)
        )
    request = ModelInvocationRequest(
        "invocation:forged-owner-claim",
        lease,
        unissued_prompt,
        "2026-10-04T10:00:02Z",
        unissued_prompt.task_id,
        unissued_prompt.trace_id,
        references,
    )
    assessment = TaskBudgetAuthority(ledger).assess(
        trace_id=request.trace_id,
        resource="model_call",
        subject_id=request.invocation_id,
    )
    before = ledger.events()

    with pytest.raises(ValueError, match="authority-bound"):
        ledger.record(
            ModelInvocationStarted(request, assessment.decision),
            expected_sequence=assessment.expected_sequence,
        )

    assert ledger.events() == before
    forged_output = RawModelOutput.capture(
        request,
        {"output_type": "operation", "object_id": "write_note"},
        completed_at="2026-10-04T10:00:03Z",
    )
    with pytest.raises(ValueError, match="exact in-flight invocation"):
        ledger.record(forged_output)
    assert ledger.events() == before
    assert ledger.replay_agent_run(lease.agent_run_id).status == "ready"
    provider = _RecordedProvider(ledger)
    trusted = _authority(
        ledger, provider, clock=lambda: "2026-10-04T10:00:02Z"
    ).invoke(lease, prompt, invocation_id="invocation:valid-owner-control")
    assert isinstance(trusted, RawModelOutput)
    assert provider.calls == 1


@pytest.mark.parametrize(
    ("fixture_name", "expected_sha256", "expected_event_count", "expected_status"),
    (
        (
            "completed.jsonl",
            "d2ba19b9a4a7ab43d5c170c3cb4dd1c62d7f2bb8e7901a1ab2c97738e7a03fc0",
            8,
            "ready",
        ),
        (
            "unfinished.jsonl",
            "9f8f250acd43a818ebdf9c3be31b0c3539a72f7555fd0fd6d34eaf38b86283c2",
            7,
            "invoking",
        ),
    ),
)
def test_legacy_model_invocation_events_remain_inspectable_and_replay_safely(
    tmp_path, fixture_name, expected_sha256, expected_event_count, expected_status
):
    from ab_harness.lifecycle import LifecycleLedger
    from ab_harness.prompt_compiler import ConfiguredPromptSourceOwner

    original = (LEGACY_V1_FIXTURES / fixture_name).read_bytes()
    assert hashlib.sha256(original).hexdigest() == expected_sha256
    path = tmp_path / fixture_name
    path.write_bytes(original)
    ledger = LifecycleLedger(path)
    events = ledger.events()
    assert len(events) == expected_event_count
    assert events[-1].event_type == (
        "model_invocation_completed" if expected_status == "ready" else "model_invocation_started"
    )
    assert all(
        "source_references" not in event.data["request"]
        for event in events
        if event.event_type in {"model_invocation_started", "model_invocation_completed"}
    )
    request_event = next(
        event
        for event in events
        if event.event_type == (
            "model_invocation_completed" if expected_status == "ready" else "model_invocation_started"
        )
    )
    request = ModelInvocationRequest.from_dict(request_event.data["request"])
    assert ledger.replay_agent_run(request.agent_run_id).status == expected_status
    provider = _RecordedProvider(ledger)
    authority = _authority(
        ledger,
        provider,
        source_owner=ConfiguredPromptSourceOwner((), frame_id=request.compiled_prompt.frame_id),
    )
    if expected_status == "ready":
        completed = next(
            event for event in events if event.event_type == "model_invocation_completed"
        )
        replayed = authority.invoke(
            request.lease, request.compiled_prompt, invocation_id=request.invocation_id
        )
        assert replayed == RawModelOutput.from_dict(completed.data)
    else:
        with pytest.raises(ValueError, match="automatic retry is forbidden"):
            authority.invoke(
                request.lease, request.compiled_prompt, invocation_id=request.invocation_id
            )
    assert provider.calls == 0
    assert ledger.replay_agent_run(request.agent_run_id).status == expected_status
    assert len(ledger.events()) == expected_event_count
    assert path.read_bytes() == original


def test_prompt_source_resolution_returns_detached_pinned_values(tmp_path):
    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    owner = ledger._test_prompt_source_owner
    with pytest.raises(LookupError, match="frame is unavailable"):
        owner.resolve(prompt.compiled_task_id, lease.agent_id, "another_frame")
    resolved = owner.resolve(prompt.compiled_task_id, lease.agent_id, prompt.frame_id)
    object.__setattr__(resolved.prompt_pack, "role_instructions", "mutated bytes")

    with pytest.raises(ValueError, match="identity does not match content"):
        resolved.verify_source_integrity()

    fresh = owner.resolve(prompt.compiled_task_id, lease.agent_id, prompt.frame_id)
    assert fresh.prompt_pack.role_instructions == "Propose one note operation."


def test_late_provider_output_is_recorded_but_does_not_authorize_another_expired_call(
    tmp_path,
):
    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    provider = _RecordedProvider(ledger)
    times = iter(("2026-10-04T10:00:02Z", "2026-10-04T10:02:00Z"))
    result = _authority(
        ledger, provider, clock=lambda: next(times)
    ).invoke(
        lease,
        prompt,
        invocation_id="invocation:late-response",
    )
    assert isinstance(result, RawModelOutput)
    assert result.completed_at == "2026-10-04T10:02:00Z"
    with pytest.raises(ValueError, match="unexpired model lease"):
        _authority(
            ledger, provider, clock=lambda: "2026-10-04T10:02:01Z"
        ).invoke(
            lease,
            prompt,
            invocation_id="invocation:next",
        )
    assert provider.calls == 1


def test_task_suspension_cannot_close_an_inflight_invocation_and_rolls_back_its_entire_commit(
    tmp_path,
):
    from ab_harness.acceptance import TaskAcceptanceEvaluator
    from ab_harness.lifecycle import AcceptanceFact

    ledger, _, lease, prompt, compiled = _invocation_fixture(
        tmp_path, return_compiled=True
    )
    judgment = TaskAcceptanceEvaluator().evaluate(compiled.effect_obligations, ())
    assert judgment.status == "suspended"

    class SuspendingProvider:
        def invoke(self, request):
            before = ledger.events()
            with pytest.raises(ValueError, match="settled model invocations"):
                ledger.record(AcceptanceFact(compiled, (), judgment))
            assert ledger.events() == before
            return {
                "output_type": "operation",
                "object_id": "write_note",
                "arguments": {"text": "hello"},
            }

    result = _authority(
        ledger, SuspendingProvider(), clock=lambda: "2026-10-04T10:00:02Z"
    ).invoke(
        lease,
        prompt,
        invocation_id="invocation:protected",
    )
    assert isinstance(result, RawModelOutput)
    assert ledger.replay_agent_run(lease.agent_run_id).status == "ready"
    assert ledger.replay(prompt.trace_id).terminal_status is None
    assert not any(event.event_type == "task_suspended" for event in ledger.events())


def test_bare_invocation_request_cannot_bypass_atomic_model_budget_authorization(
    tmp_path,
):
    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    request = ModelInvocationRequest(
        "invocation:bare",
        lease,
        prompt,
        "2026-10-04T10:00:02Z",
        prompt.task_id,
        prompt.trace_id,
    )
    before = ledger.events()
    with pytest.raises(TypeError, match="unsupported lifecycle fact"):
        ledger.record(request)
    assert ledger.events() == before
