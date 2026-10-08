from dataclasses import FrozenInstanceError, replace
import json

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
    from ab_harness.prompt_compiler import PromptCompiler, PromptPack
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
    compiled = TaskSpecCompiler().compile(
        task_ingress_decision=ingress,
        task_spec=TaskSpec(
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
        ),
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
    return (*result, compiled) if return_compiled else result


class _RecordedProvider:
    def __init__(self, ledger):
        self.ledger = ledger
        self.calls = 0

    def invoke(self, request):
        self.calls += 1
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


def test_provider_call_records_budget_and_start_before_untrusted_output_and_is_idempotent(
    tmp_path,
):
    from ab_harness.lifecycle import LifecycleLedger

    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    provider = _RecordedProvider(ledger)
    authority = ModelInvocationAuthority(
        ledger, provider, clock=lambda: "2026-10-04T10:00:02Z"
    )
    output = authority.invoke(lease, prompt, invocation_id="invocation:1")

    assert isinstance(output, RawModelOutput)
    assert output.output["arguments"] == {"text": "hello"}
    assert ledger.replay_agent_run(lease.agent_run_id).status == "ready"
    assert ledger.replay(prompt.trace_id).terminal_status is None
    assert not any(
        event.event_type
        in {"proposal_normalized", "domain_admission_leased", "evidence_issued"}
        for event in ledger.events()
    )
    reopened = LifecycleLedger(ledger.path)
    replayed = ModelInvocationAuthority(reopened, provider).invoke(
        lease, prompt, invocation_id="invocation:1"
    )
    assert replayed == output
    assert provider.calls == 1


def test_completed_call_can_release_capacity_and_return_the_same_actor_to_standby(
    tmp_path,
):
    ledger, allocator, lease, prompt = _invocation_fixture(tmp_path)
    ModelInvocationAuthority(
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
    authority = ModelInvocationAuthority(
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
    authority = ModelInvocationAuthority(
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
    authority = ModelInvocationAuthority(
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

    result = ModelInvocationAuthority(
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
        ModelInvocationAuthority(
            ledger, provider, clock=lambda: "2026-10-04T10:00:02Z"
        ).invoke(
            lease,
            prompt,
            invocation_id="invocation:unfinished",
        )
    reopened = LifecycleLedger(ledger.path)
    assert reopened.replay_agent_run(lease.agent_run_id).status == "invoking"
    with pytest.raises(ValueError, match="automatic retry is forbidden"):
        ModelInvocationAuthority(reopened, provider).invoke(
            lease, prompt, invocation_id="invocation:unfinished"
        )
    assert provider.calls == 1
    assert [event.event_type for event in reopened.events()].count(
        "budget_granted"
    ) == 1


def test_completed_invocation_identity_cannot_be_reused_for_a_changed_prompt(tmp_path):
    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    provider = _RecordedProvider(ledger)
    authority = ModelInvocationAuthority(
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


def test_late_provider_output_is_recorded_but_does_not_authorize_another_expired_call(
    tmp_path,
):
    ledger, _, lease, prompt = _invocation_fixture(tmp_path)
    provider = _RecordedProvider(ledger)
    times = iter(("2026-10-04T10:00:02Z", "2026-10-04T10:02:00Z"))
    result = ModelInvocationAuthority(
        ledger, provider, clock=lambda: next(times)
    ).invoke(
        lease,
        prompt,
        invocation_id="invocation:late-response",
    )
    assert isinstance(result, RawModelOutput)
    assert result.completed_at == "2026-10-04T10:02:00Z"
    with pytest.raises(ValueError, match="unexpired model lease"):
        ModelInvocationAuthority(
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

    result = ModelInvocationAuthority(
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
