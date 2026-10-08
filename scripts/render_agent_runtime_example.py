#!/usr/bin/env python3
"""Render a deterministic, synthetic H1 actor and model-resource O1 example."""

from __future__ import annotations

import argparse
from pathlib import Path

from ab_harness.agent_configuration import (
    AgentRoleConfiguration,
    AgentRoleConfigurationRegistry,
)
from ab_harness.agent_configuration import (
    ModelConfiguration,
    ModelConfigurationRegistry,
)
from ab_harness.agent_identity import (
    AgentHandleRegistry,
    AgentManifest,
    AgentRegistry,
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
from ab_harness.model_invocation import ModelInvocationAuthority
from ab_harness.observatory import ObservatoryDataLabel, render_observatory
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


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/artifacts/observatory/o1_h1_agent_lifecycle.html"
TITLE = "SYNTHETIC H1 Agent Lifecycle: No live provider, hardware qualification, or H2 effect evidence"
RECORDED_AT = "2026-10-04T10:00:00Z"


class SyntheticProvider:
    """Return one fixed proposal without inference or an environment mutation."""

    def invoke(self, request):
        request.verify_identity()
        return {
            "output_type": "operation",
            "object_id": "write_note",
            "arguments": {"text": "Synthetic proposal only. No note was written."},
        }


def example_ledger() -> LifecycleLedger:
    """Use public runtime APIs to record success and startup-failure branches."""

    ledger = LifecycleLedger(clock=lambda: RECORDED_AT)
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
        source="synthetic:notes-registry",
        version="registry:synthetic-notes:v1",
    )
    role = AgentRoleSpec("note_writer", ("operation",), ABControlBand(1, 1, 1))
    frame = AbstractionFrame(
        "synthetic_notes", "workspace", "one verified note mutation", registry.version
    )
    domain = DomainContractPack.issue(
        domain_contract_pack_id="domain:synthetic-notes",
        frame_id=frame.frame_id,
        registry_version=frame.registry_version,
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
            required_model_capabilities=("structured_output",),
            minimum_context_tokens=512,
        )
    )
    model = models.register(
        ModelConfiguration(
            "synthetic",
            "synthetic_local",
            "fixed-proposal-model",
            "fixture:v1",
            ("structured_output",),
            4096,
            (("temperature", 0),),
        )
    )
    pack = PromptPack(
        "uah.protocol/v1",
        "Propose one bounded note operation.",
        "The workspace owner determines whether a note was written.",
    )
    agents = AgentRegistry()
    manifest = agents.register(
        AgentManifest(
            configuration.role_configuration_id,
            model.model_configuration_id,
            pack.prompt_pack_id,
            "build:synthetic-h1-example:v1",
            (),
        )
    )
    handles = AgentHandleRegistry(agents)
    handle = "synthetic.notes.writer.primary"
    handles.register(
        agent_handle_id=handle,
        candidate_agent_id=manifest.agent_id,
        fidelity_evidence_refs=("synthetic:handle-qualification:v1",),
    )
    profile = EnvironmentProfile(
        "profile:synthetic-notes",
        domain.domain_contract_pack_id,
        domain.revision,
        "synthetic-runtime:v1",
        "notes",
        ("request:notes",),
        (handle,),
    )
    profiles = EnvironmentProfileRegistry((profile,))
    environments = EnvironmentRunRegistry(profiles)
    runs = AgentRunRegistry(handles, environments, profiles, ledger=ledger)
    for suffix in ("alpha", "beta"):
        environment = environments.register(
            EnvironmentRunAttestation(
                "environment-run:synthetic-notes:" + suffix,
                profile.environment_profile_id,
                domain.revision,
                profile.native_runtime_revision,
                profile.environment_owner_id,
                "synthetic:attestation:" + suffix,
                RECORDED_AT,
                ("synthetic:environment-ready:" + suffix,),
            )
        )
        runs.attach(
            agent_run_id="agent-run:synthetic-notes:" + suffix,
            environment_run_id=environment.environment_run_id,
            agent_handle_id=handle,
        )
    alpha = environments.get("environment-run:synthetic-notes:alpha")
    ingress = TaskIngressAuthority(
        environment_profile_id=profile.environment_profile_id,
        domain_contract_pack=domain,
        lifecycle_ledger=ledger,
    ).admit(
        alpha,
        EnvironmentIngress(
            "ingress:synthetic-notes:alpha",
            alpha.environment_run_id,
            "request:notes",
            "request",
            "synthetic:request:alpha",
            (("request_id", "task:synthetic-note"),),
            RECORDED_AT,
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
            "Propose a note about this synthetic experiment.",
            (TaskEffectRequest("written", "note_written", "required"),),
            (),
            TaskBudgets(60, 2, 2),
        ),
        role=role,
        frame=frame,
        registry=registry,
        domain_contract_pack=domain,
        task_registry=EnvironmentTaskRegistry(ledger),
    )
    ledger.record(compiled)
    binding = ABImplementationBinding(
        "binding:synthetic-note",
        "write_note",
        "synthetic_notes",
        "notes",
        "python_method",
        "synthetic.notes:write",
        "fixture:v1",
        "schema:note-input",
        "schema:note-result",
        "synthetic:note-evidence",
        ("fake",),
        "approved",
    )
    schema = ObjectArgumentSchema.issue(
        schema_ref=binding.input_schema_ref,
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
        environment_id="synthetic_notes",
        runtime_mode="fake",
    )
    instance = FixedModelInstance(
        "instance:synthetic-notes",
        model.model_configuration_id,
        "host:synthetic",
        4096,
        1,
        0,
        "owner:synthetic-model-runtime",
    )
    allocator = FixedModelAllocator(
        ledger=ledger,
        roles=roles,
        models=models,
        instance=instance,
        clock=lambda: RECORDED_AT,
    )
    resources = ResourceSnapshot(
        "snapshot:synthetic-capacity",
        instance.host_id,
        1024,
        0,
        RECORDED_AT,
        ("synthetic:declared-capacity",),
    )
    alpha_lease = allocator.acquire(
        "agent-run:synthetic-notes:alpha",
        request_id="acquisition:alpha",
        context_tokens=1024,
        duration_seconds=60,
        resources=resources,
    ).lease
    allocator.acquire(
        "agent-run:synthetic-notes:beta",
        request_id="acquisition:beta:busy",
        context_tokens=1024,
        duration_seconds=60,
        resources=resources,
    )
    allocator.preflight(
        alpha_lease,
        readiness_owner_id=instance.readiness_owner_id,
        observed_instance_id=instance.model_instance_id,
        observed_model_configuration_id=model.model_configuration_id,
        observed_at=RECORDED_AT,
        attempts_used=1,
        elapsed_seconds=1,
        succeeded=True,
        evidence_refs=("synthetic:readiness:alpha",),
    )
    ModelInvocationAuthority(
        ledger, SyntheticProvider(), clock=lambda: RECORDED_AT
    ).invoke(alpha_lease, prompt, invocation_id="invocation:synthetic-note:alpha")
    allocator.release(alpha_lease, reason_code="synthetic_invocation_completed")
    beta_lease = allocator.acquire(
        "agent-run:synthetic-notes:beta",
        request_id="acquisition:beta:after-release",
        context_tokens=1024,
        duration_seconds=60,
        resources=resources,
    ).lease
    allocator.preflight(
        beta_lease,
        readiness_owner_id=instance.readiness_owner_id,
        observed_instance_id=instance.model_instance_id,
        observed_model_configuration_id=model.model_configuration_id,
        observed_at=RECORDED_AT,
        attempts_used=1,
        elapsed_seconds=1,
        succeeded=False,
        evidence_refs=("synthetic:readiness-failed:beta",),
    )
    return ledger


def expected_html() -> str:
    return render_observatory(
        example_ledger(), title=TITLE, data_label=ObservatoryDataLabel.SYNTHETIC
    ).html


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="verify the committed synthetic example"
    )
    args = parser.parse_args()
    rendered = expected_html()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("committed synthetic H1 Observatory example is stale")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
