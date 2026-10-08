"""Independent public-API probes; run unchanged against both source snapshots."""

import json
import sys
from dataclasses import replace

from ab_harness.agent_configuration import AgentRoleConfiguration
from ab_harness.agent_identity import AgentManifest
from ab_harness.bindings import BindingCatalog
from ab_harness.contracts import (
    ABControlBand,
    ABImplementationBinding,
    ABObjectView,
    AbstractionFrame,
    AgentOutput,
    AgentRoleSpec,
)
from ab_harness.domain_contracts import (
    DomainContractPack,
    DomainEffectRule,
    TaskIngressRule,
)
from ab_harness.environment_ingress import EnvironmentIngress
from ab_harness.environment_runs import EnvironmentRun, EnvironmentRunAttestation
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.prompt_compiler import PromptCompiler, PromptPack
from ab_harness.proposal_admission import ProposalNormalizer, SemanticAdmission
from ab_harness.registry import RegistrySnapshot
from ab_harness.schema_validation import (
    ArgumentField,
    InMemoryArgumentSchemaRegistry,
    ObjectArgumentSchema,
)
from ab_harness.task_compiler import (
    TaskBudgets,
    TaskEffectRequest,
    TaskSpec,
    TaskSpecCompiler,
)
from ab_harness.task_ingress_authority import TaskIngressAuthority
from ab_harness.task_registry import EnvironmentTaskRegistry


def fixture(
    *,
    expected=(),
    observed=(),
    prohibited=(),
    callable=True,
    level=1,
    pair=False,
    reverse=False,
    unrequired=False,
    both_unsafe=False,
    binding_change=None,
    missing_schema=False,
    broad_role=False,
    child_level=1,
    child_callable=True,
):
    a = ABObjectView(
        "alpha",
        level,
        "skill",
        "review",
        "review_owner",
        ("done_alpha",) + tuple(expected),
        ("done_alpha",) + tuple(observed),
        ("beta",) if unrequired else (),
        callable,
    )
    b = ABObjectView(
        "beta",
        child_level,
        "skill",
        "review",
        "review_owner",
        ("done_beta",),
        ("done_beta", "unsafe") if both_unsafe else ("done_beta",),
        (),
        child_callable,
    )
    objects = (a, b) if pair or unrequired else (a,)
    if reverse:
        objects = objects[::-1]
    registry = RegistrySnapshot(
        objects, source="independent:ARCH-01", version="review:v1"
    )
    role = AgentRoleSpec("review_role", ("operation",), ABControlBand(1, 1, 1, 0))
    frame = AbstractionFrame("review_frame", "review", "one mutation", registry.version)
    domain = DomainContractPack.issue(
        domain_contract_pack_id="domain:review",
        frame_id=frame.frame_id,
        registry_version=registry.version,
        allowed_role_ids=(role.role_id,),
        supported_task_type_ids=("review_task",),
        ingress_rules=(
            TaskIngressRule("request:review", "request", "start_task", "request_id"),
        ),
        effect_rules=tuple(
            DomainEffectRule(
                "done_" + item.object_id, item.object_id, "review_owner", "terminal"
            )
            for item in objects
        ),
    )
    ledger = LifecycleLedger()
    environment = EnvironmentRun(
        EnvironmentRunAttestation(
            "environment:review",
            "profile:review",
            domain.revision,
            "runtime:v1",
            "review_owner",
            "attestation:review",
            "2026-10-08T16:00:00Z",
            ("ready:review",),
        )
    )
    ingress = TaskIngressAuthority(
        environment_profile_id="profile:review",
        domain_contract_pack=domain,
        lifecycle_ledger=ledger,
    ).admit(
        environment,
        EnvironmentIngress(
            "ingress:review",
            environment.environment_run_id,
            "request:review",
            "request",
            "raw:review",
            (("request_id", "task:review"),),
            "2026-10-08T16:00:01Z",
        ),
    )
    requested = objects if pair else (a,)
    task = TaskSpecCompiler().compile(
        task_ingress_decision=ingress,
        task_spec=TaskSpec(
            ingress.task_id,
            ingress.trace_id,
            "review_task",
            role.role_id,
            frame.frame_id,
            domain.revision,
            "Review static eligibility",
            tuple(
                TaskEffectRequest(
                    "obligation:" + item.object_id, "done_" + item.object_id, "required"
                )
                for item in requested
            ),
            tuple(prohibited),
            TaskBudgets(30, 1, 2),
        ),
        role=role,
        frame=frame,
        registry=registry,
        domain_contract_pack=domain,
        task_registry=EnvironmentTaskRegistry(ledger),
    )
    configured_role = (
        replace(
            role,
            allowed_output_types=("operation", "answer"),
            control_band=ABControlBand(0, 1, 2),
        )
        if broad_role
        else role
    )
    configuration = AgentRoleConfiguration(
        configured_role,
        frame,
        domain.domain_contract_pack_id,
        domain.revision,
        tuple(x.object_id for x in objects),
    )
    examples = tuple(
        json.dumps(
            {
                "output_type": "operation",
                "object_id": item.object_id,
                "arguments": {"field_" + item.object_id: "EXAMPLE_" + item.object_id},
            }
        )
        for item in objects
    )
    pack = PromptPack(
        "uah.protocol/v1",
        "Propose a bounded operation.",
        "Owner evidence is required.",
        examples,
    )
    manifest = AgentManifest(
        configuration.role_configuration_id,
        "model:recorded",
        pack.prompt_pack_id,
        "build:review",
        (),
    )
    bindings = tuple(
        ABImplementationBinding(
            "binding:" + item.object_id,
            item.object_id,
            "environment:review",
            "review_owner",
            "python_method",
            "PRIVATE_LOCATOR_" + item.object_id,
            "source:v1",
            "schema:" + item.object_id,
            "schema:out",
            "evidence:review",
            ("fake",),
            "approved",
        )
        for item in objects
    )
    if binding_change:
        bindings = tuple(replace(x, **binding_change) for x in bindings)
    schemas = tuple(
        ObjectArgumentSchema.issue(
            schema_ref="schema:" + item.object_id,
            fields=(ArgumentField("field_" + item.object_id, "string"),),
            required=("field_" + item.object_id,),
        )
        for item in objects
    )
    if missing_schema:
        schemas = ()
    return dict(
        compiled_task=task,
        manifest=manifest,
        role_configuration=configuration,
        prompt_pack=pack,
        binding_catalog=BindingCatalog(registry, bindings),
        argument_schemas=schemas,
        environment_id="environment:review",
        runtime_mode="fake",
    )


def probe(
    name,
    inputs,
    *,
    object_id="alpha",
    output_type="operation",
    arguments=None,
    reasons=(),
    choices=("alpha",),
    examples=("alpha",),
):
    arguments = {"field_" + object_id: "valid"} if arguments is None else arguments
    proposal = (
        ProposalNormalizer()
        .normalize(
            compiled_task=inputs["compiled_task"],
            operation_id="operation:review",
            raw_output_artifact_id="raw:review",
            output=AgentOutput(
                output_type,
                {"object_id": object_id, "arguments": arguments},
                (object_id,),
            ),
        )
        .proposal
    )
    assert proposal is not None, name
    decision = SemanticAdmission(
        catalog=inputs["binding_catalog"],
        environment_id=inputs["environment_id"],
        runtime_mode=inputs["runtime_mode"],
        schema_validator=InMemoryArgumentSchemaRegistry(inputs["argument_schemas"]),
    ).admit(inputs["compiled_task"], proposal)
    assert decision.reason_codes == reasons, (name, decision.reason_codes, reasons)
    artifact = decision.admitted_operation or decision.rejection
    artifact.verify_identity()
    record = {
        "name": name,
        "reasons": list(decision.reason_codes),
        "artifact": artifact.to_dict(),
    }
    try:
        prompt = PromptCompiler().compile(**inputs)
        repeated = PromptCompiler().compile(**inputs)
        assert prompt == repeated, name
        schema = json.loads(prompt.output_schema_json)
        actual_choices = tuple(
            item["properties"]["object_id"]["const"] for item in schema["oneOf"]
        )
        assert actual_choices == choices, (name, actual_choices, choices)
        assert tuple(item[0] for item in prompt.source_contracts) == choices
        prompt_examples = json.loads(
            prompt.messages[0].content.split("Task-scoped operation examples:\n")[1]
        )
        actual_examples = tuple(item["object_id"] for item in prompt_examples)
        assert actual_examples == examples, (name, actual_examples, examples)
        assert all(
            item["properties"]["output_type"]["enum"] == ["operation"]
            for item in schema["oneOf"]
        )
        assert all(
            item["properties"]["arguments"]["required"]
            == ["field_" + item["properties"]["object_id"]["const"]]
            for item in schema["oneOf"]
        )
        assert "PRIVATE_LOCATOR" not in json.dumps(prompt.to_dict())
        record.update(
            choices=list(actual_choices),
            examples=list(actual_examples),
            source_contracts=list(prompt.source_contracts),
            output_schema=schema,
            prompt_id=prompt.compiled_prompt_id,
        )
    except (ValueError, LookupError) as exc:
        assert choices is None, (name, str(exc))
        record["prompt_error"] = str(exc)
    return record


def main():
    baseline = sys.argv[1] == "before"
    rows = []

    def run(name, config=None, **options):
        rows.append(probe(name, fixture(**(config or {})), **options))

    run("valid")
    run("broader_configured_role_narrow_task", {"broad_role": True})
    run(
        "unrelated_prohibition",
        {"expected": ("safe",), "observed": ("safe",), "prohibited": ("unsafe",)},
    )
    run("case_distinct_effect_id", {"observed": ("UNSAFE",), "prohibited": ("unsafe",)})
    for form in ("expected", "observed", "both"):
        config = {"prohibited": ("unsafe",)}
        if form in ("expected", "both"):
            config["expected"] = ("unsafe",)
        if form in ("observed", "both"):
            config["observed"] = ("unsafe",)
        admitted_prompt = baseline and form == "observed"
        run(
            "prohibited_" + form,
            config,
            reasons=("object_effect_prohibited",),
            choices=("alpha",) if admitted_prompt else None,
        )
    run(
        "not_callable",
        {"callable": False},
        reasons=("object_not_runtime_callable",),
        choices=None,
    )
    run("inspect_only", {"level": 0}, reasons=("object_inspection_only",), choices=None)
    run(
        "outside_projection",
        object_id="absent",
        reasons=("object_outside_projection", "missing_effect_obligation"),
    )
    run(
        "output_type_forbidden",
        output_type="answer",
        reasons=("role_output_type_forbidden",),
    )
    run(
        "combined_static_reasons",
        {
            "level": 0,
            "callable": False,
            "observed": ("unsafe",),
            "prohibited": ("unsafe",),
        },
        output_type="answer",
        reasons=(
            "role_output_type_forbidden",
            "object_inspection_only",
            "object_not_runtime_callable",
            "object_effect_prohibited",
        ),
        choices=None,
    )
    run(
        "decomposed_missing_obligation",
        {"unrequired": True},
        object_id="beta",
        reasons=("missing_effect_obligation",),
        choices=("alpha", "beta") if baseline else ("alpha",),
        examples=("alpha", "beta") if baseline else ("alpha",),
    )
    run(
        "all_static_reasons_in_order",
        {
            "unrequired": True,
            "child_level": 0,
            "child_callable": False,
            "both_unsafe": True,
            "prohibited": ("unsafe",),
        },
        object_id="beta",
        output_type="answer",
        reasons=(
            "role_output_type_forbidden",
            "object_inspection_only",
            "object_not_runtime_callable",
            "object_effect_prohibited",
            "missing_effect_obligation",
        ),
    )
    for reverse in (False, True):
        suffix = "reverse" if reverse else "forward"
        ordered_examples = ("beta", "alpha") if reverse else ("alpha", "beta")
        run(
            "two_valid_" + suffix,
            {"pair": True, "reverse": reverse},
            choices=("alpha", "beta"),
            examples=ordered_examples,
        )
        run(
            "two_one_observable_forbidden_" + suffix,
            {
                "pair": True,
                "reverse": reverse,
                "observed": ("unsafe",),
                "prohibited": ("unsafe",),
            },
            reasons=("object_effect_prohibited",),
            choices=("alpha", "beta") if baseline else ("beta",),
            examples=ordered_examples if baseline else ("beta",),
        )
        run(
            "two_both_observable_forbidden_" + suffix,
            {
                "pair": True,
                "reverse": reverse,
                "observed": ("unsafe",),
                "prohibited": ("unsafe",),
                "both_unsafe": True,
            },
            reasons=("object_effect_prohibited",),
            choices=("alpha", "beta") if baseline else None,
            examples=ordered_examples,
        )
    for label, arguments in (
        ("missing", {}),
        ("type", {"field_alpha": 1}),
        ("extra", {"field_alpha": "ok", "extra": True}),
    ):
        run(
            "arguments_" + label,
            arguments=arguments,
            reasons=("proposal_arguments_schema_invalid",),
        )
    for label, change, reason in (
        ("candidate", {"status": "candidate"}, "binding_unavailable"),
        ("disabled", {"status": "disabled"}, "binding_unavailable"),
        ("wrong_environment", {"environment_id": "foreign"}, "binding_unavailable"),
        ("wrong_runtime", {"runtime_modes": ("live",)}, "binding_unavailable"),
        ("wrong_owner", {"implementation_owner": "foreign"}, "binding_owner_mismatch"),
    ):
        run(label, {"binding_change": change}, reasons=(reason,), choices=None)
    run(
        "missing_schema",
        {"missing_schema": True},
        reasons=("input_schema_unavailable",),
        choices=None,
    )
    print(
        json.dumps(
            {"variant": sys.argv[1], "count": len(rows), "results": rows},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
