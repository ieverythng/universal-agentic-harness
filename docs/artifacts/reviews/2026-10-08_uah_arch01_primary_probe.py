"""Independent ARCH-01 consumer probes. Run with PYTHONPATH=<variant>/src."""

from dataclasses import asdict, replace
import hashlib
import json

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
    EffectObligation,
    InteractionModuleSpec,
)
from ab_harness.domain_contracts import DomainContractPack, DomainEffectRule, TaskIngressRule
from ab_harness.environment_ingress import EnvironmentIngress
from ab_harness.environment_runs import EnvironmentRun, EnvironmentRunAttestation
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.prompt_compiler import PromptCompiler, PromptPack
import ab_harness.prompt_compiler as prompt_module
from ab_harness.proposal_admission import ProposalNormalizer, SemanticAdmission
import ab_harness.proposal_admission as admission_module
from ab_harness.registry import RegistrySnapshot
from ab_harness.schema_validation import (
    ArgumentField,
    InMemoryArgumentSchemaRegistry,
    ObjectArgumentSchema,
)
from ab_harness.task_compiler import CompiledTask, TaskBudgets, TaskEffectRequest, TaskSpec, TaskSpecCompiler
from ab_harness.task_ingress_authority import TaskIngressAuthority
from ab_harness.task_registry import EnvironmentTaskRegistry


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def ab_object(name="a", *, expected=("done",), observed=("done",), level=1, callable=True):
    return ABObjectView(name, level, "skill", "fixture", "owner", expected, observed, (), callable)


def fixture(objects, *, prohibited=(), obligations=None, output_types=("operation",), task_id="task:review"):
    """Issue a synthetic content-addressed consumer fixture, not task-start authority."""
    role = AgentRoleSpec("role:review", output_types, ABControlBand(1, 1, 1))
    frame = AbstractionFrame("frame:review", "fixture", "one fixture action", "registry:review")
    module = InteractionModuleSpec(task_id, role, frame, objects, "synthetic:independent-review")
    requested = (TaskEffectRequest("request:review", "done", "required"),)
    spec = TaskSpec(task_id, "trace:review", "type:review", role.role_id, frame.frame_id,
                    "domain:revision", "Independent static eligibility probe", requested,
                    prohibited, TaskBudgets(10, 1, 2))
    obligated = tuple(item.object_id for item in objects) if obligations is None else obligations
    effects = tuple(EffectObligation("obligation:" + name, "done", name, "owner", "required", "terminal")
                    for name in obligated)
    payload = {
        "schema_version": "uah.compiled_task/v2",
        "environment_ingress_id": "ingress:review",
        "environment_run_id": "run:review",
        "task_spec": asdict(spec),
        "domain_contract_pack_id": "domain:review",
        "domain_contract_pack_revision": "domain:revision",
        "interaction_module": {
            "task_id": task_id,
            "role": asdict(role),
            "frame": asdict(frame),
            "object_ids": tuple(item.object_id for item in objects),
            "objects": tuple(asdict(item) for item in objects),
        },
        "effect_obligations": tuple(asdict(item) for item in effects),
        "prohibited_effects": prohibited,
    }
    identity = "compiled-task:sha256:" + hashlib.sha256(canonical(payload).encode()).hexdigest()
    compiled = CompiledTask(identity, "ingress:review", "run:review", spec, "domain:review",
                            "domain:revision", module, effects, prohibited)
    configuration = AgentRoleConfiguration(role, frame, "domain:review", "domain:revision",
                                            tuple(item.object_id for item in objects))
    examples = tuple(canonical({"output_type": "operation", "object_id": item.object_id,
                                "arguments": {"value": "example:" + item.object_id}})
                     for item in objects)
    pack = PromptPack("uah.protocol/v1", "Propose a scoped operation.", "Fixture owner verifies effects.", examples)
    manifest = AgentManifest(configuration.role_configuration_id, "model:fake", pack.prompt_pack_id,
                             "build:review", (("synthetic", "review:v1"),))
    bindings = tuple(ABImplementationBinding("binding:" + item.object_id, item.object_id, "environment:review",
                                            "owner", "python_method", "PRIVATE:" + item.object_id,
                                            "revision:review", "schema:review", "schema:result", "adapter:review",
                                            ("fake",), "approved") for item in objects)
    schema = ObjectArgumentSchema.issue(schema_ref="schema:review", fields=(ArgumentField("value", "string"),),
                                        required=("value",))
    registry = RegistrySnapshot(objects, source="synthetic:independent-review", version="registry:review")
    return {
        "compiled_task": compiled, "manifest": manifest, "role_configuration": configuration,
        "prompt_pack": pack, "binding_catalog": BindingCatalog(registry, bindings),
        "argument_schemas": (schema,), "environment_id": "environment:review", "runtime_mode": "fake",
    }, registry, bindings


def probe(label, inputs, *, object_id="a", output_type="operation", arguments=None, foreign=None):
    compiled = inputs["compiled_task"]
    normalized = ProposalNormalizer().normalize(
        compiled_task=foreign or compiled, operation_id="operation:" + label, raw_output_artifact_id="raw:" + label,
        output=AgentOutput(output_type, {"object_id": object_id, "arguments": arguments or {"value": "valid"}},
                           (object_id,)),
    )
    row = {"label": label, "object": object_id, "output_type": output_type}
    if normalized.proposal is None:
        row["normalization_reasons"] = normalized.reason_codes
    else:
        try:
            decision = SemanticAdmission(catalog=inputs["binding_catalog"], environment_id=inputs["environment_id"],
                                         runtime_mode=inputs["runtime_mode"],
                                         schema_validator=InMemoryArgumentSchemaRegistry(inputs["argument_schemas"])).admit(
                                             compiled, normalized.proposal)
            row["accepted"] = decision.accepted
            row["reasons"] = decision.reason_codes
            artifact = decision.admitted_operation or decision.rejection
            row["admission_artifact_id"] = (artifact.admission_id if decision.accepted else artifact.rejection_id)
            if decision.accepted:
                row["admitted_binding"] = artifact.binding_fingerprint
                row["admitted_schema"] = artifact.input_schema_id
                row["execution_authority"] = hasattr(artifact, "lease_id")
        except (ValueError, LookupError) as error:
            row["admission_error"] = str(error)
    try:
        prompt = PromptCompiler().compile(**inputs)
        choices = json.loads(prompt.output_schema_json)["oneOf"]
        row["choices"] = tuple(choice["properties"]["object_id"]["const"] for choice in choices)
        row["output_enums"] = tuple(choice["properties"]["output_type"]["enum"] for choice in choices)
        row["contracts"] = prompt.source_contracts
        row["prompt_id"] = prompt.compiled_prompt_id
        projection = prompt.messages[0].content.split("Task-scoped AB projection:\n", 1)[1].split("\n\n", 1)[0]
        row["projection"] = tuple(item["object_id"] for item in json.loads(projection)["objects"])
        examples = prompt.messages[0].content.split("Task-scoped operation examples:\n", 1)[1]
        row["examples"] = tuple(item["object_id"] for item in json.loads(examples))
        row["private_locator_leaked"] = "PRIVATE:" in canonical(prompt.to_dict())
        row["metadata_coherent"] = (set(row["choices"]) == {item[0] for item in prompt.source_contracts}
                                    and set(row["examples"]).issubset(row["choices"]))
        if row.get("accepted"):
            source = next((item for item in prompt.source_contracts if item[0] == object_id), None)
            row["admission_prompt_source_agreement"] = bool(source and source[1:] == (
                row["admitted_binding"], row["admitted_schema"]))
    except (ValueError, LookupError) as error:
        row["prompt_error"] = str(error)
    return row


rows = []
effect_cases = (
    ("permitted", ("done",), ("done",), ()),
    ("expected_only", ("done", "unsafe"), ("done",), ("unsafe",)),
    ("observable_only", ("done",), ("done", "unsafe"), ("unsafe",)),
    ("both", ("done", "unsafe"), ("unsafe", "done"), ("unsafe",)),
    ("separate_both", ("unsafe_expected", "done"), ("done", "unsafe_observed"), ("unsafe_observed", "unsafe_expected")),
    ("separate_both_reverse", ("done", "unsafe_expected"), ("unsafe_observed", "done"), ("unsafe_expected", "unsafe_observed")),
    ("unrelated_prohibition", ("done", "safe"), ("safe", "done"), ("unsafe",)),
    ("empty_effect_lists", (), (), ()),
)
for label, expected, observed, prohibited in effect_cases:
    inputs, _, _ = fixture((ab_object(expected=expected, observed=observed),), prohibited=prohibited)
    rows.append(probe(label, inputs))

for label, objects, obligated in (
    ("empty_projection", (), ()),
    ("missing_obligation", (ab_object(),), ()),
    ("inspect_only", (ab_object(level=0),), None),
    ("above_direct_band", (ab_object(level=2),), None),
    ("not_callable", (ab_object(callable=False),), None),
    ("two_permitted_ab", (ab_object(), ab_object("b")), None),
    ("two_permitted_ba", (ab_object("b"), ab_object()), None),
    ("mixed_ab", (ab_object(), ab_object("b", observed=("done", "unsafe"))), None),
    ("mixed_ba", (ab_object("b", observed=("done", "unsafe")), ab_object()), None),
    ("missing_second_ab", (ab_object(), ab_object("b")), ("a",)),
    ("missing_second_ba", (ab_object("b"), ab_object()), ("a",)),
    ("all_static_reasons", (ab_object(level=0, callable=False, observed=("done", "unsafe")),), ()),
):
    inputs, _, _ = fixture(objects, obligations=obligated,
                            prohibited=("unsafe",) if label.startswith(("mixed", "all_static")) else ())
    rows.append(probe(label, inputs))
    if len(objects) == 2:
        rows.append(probe(label + "_b", inputs, object_id="b"))
    if label == "all_static_reasons":
        rows.append(probe(label + "_bad_output", inputs, output_type="foreign"))

inputs, registry, bindings = fixture((ab_object(),))
rows.append(probe("outside_projection", inputs, object_id="unknown"))
rows.append(probe("outside_and_output", inputs, object_id="unknown", output_type="foreign"))
for output in ("foreign", " operation", "", 17):
    rows.append(probe("output_" + repr(output), inputs, output_type=output))
rows.append(probe("bad_argument", inputs, arguments={"value": 42}))
other, _, _ = fixture((ab_object(),), task_id="task:foreign")
rows.append(probe("foreign_lineage", inputs, foreign=other["compiled_task"]))

for label, changes in (
    ("candidate_binding", {"status": "candidate"}),
    ("disabled_binding", {"status": "disabled"}),
    ("owner_mismatch", {"implementation_owner": "foreign_owner"}),
    ("missing_output_schema", {"output_schema_ref": ""}),
    ("missing_evidence_adapter", {"evidence_adapter": ""}),
    ("binding_environment", {"environment_id": "foreign_environment"}),
    ("binding_runtime", {"runtime_modes": ("live",)}),
):
    changed = dict(inputs, binding_catalog=BindingCatalog(registry, (replace(bindings[0], **changes),)))
    rows.append(probe(label, changed))
rows.append(probe("ambiguous_binding", dict(inputs, binding_catalog=BindingCatalog(registry,
    (bindings[0], replace(bindings[0], binding_id="binding:second"))))))
rows.append(probe("missing_schema", dict(inputs, argument_schemas=())))
drift = RegistrySnapshot((ab_object(expected=("done", "catalog_drift")),), source=registry.source, version=registry.version)
rows.append(probe("catalog_drift", dict(inputs, binding_catalog=BindingCatalog(drift, bindings))))
tampered, _, _ = fixture((ab_object(),))
object.__setattr__(tampered["compiled_task"], "compiled_task_id", "compiled-task:tampered")
try:
    rows.append(probe("tampered_compiled_identity", tampered))
except ValueError as error:
    rows.append({"label": "tampered_compiled_identity", "early_error": str(error)})


def compiler_fixture(objects, *, prohibited=()):
    """Produce the projection through real ingress, ledger and task compilation."""
    inputs, registry, _ = fixture(objects, prohibited=prohibited, obligations=("a",))
    role = inputs["role_configuration"].role
    frame = inputs["role_configuration"].primary_frame
    domain = DomainContractPack.issue(
        domain_contract_pack_id="domain:review", frame_id=frame.frame_id, registry_version=registry.version,
        allowed_role_ids=(role.role_id,), supported_task_type_ids=("type:review",),
        ingress_rules=(TaskIngressRule("request:review", "request", "start_task", "request_id"),),
        effect_rules=(DomainEffectRule("done", "a", "owner", "terminal"),),
    )
    ledger = LifecycleLedger(clock=lambda: "2026-10-08T16:00:00Z")
    run = EnvironmentRun(EnvironmentRunAttestation(
        environment_run_id="run:review", environment_profile_id="profile:review",
        domain_contract_pack_revision=domain.revision, native_runtime_revision="runtime:review",
        environment_owner_id="owner", attestation_id="attestation:review", started_at="2026-10-08T15:59:00Z",
        readiness_evidence_refs=("readiness:review",),
    ))
    decision = TaskIngressAuthority(environment_profile_id="profile:review", domain_contract_pack=domain,
                                    lifecycle_ledger=ledger).admit(
        run, EnvironmentIngress("ingress:review", run.environment_run_id, "request:review", "request",
                                "payload:review", (("request_id", "task:review"),), "2026-10-08T16:00:00Z"),
    )
    spec = replace(inputs["compiled_task"].task_spec, trace_id=decision.trace_id,
                   domain_contract_pack_revision=domain.revision)
    compiled = TaskSpecCompiler().compile(task_ingress_decision=decision, task_spec=spec, role=role, frame=frame,
                                          registry=registry, domain_contract_pack=domain,
                                          task_registry=EnvironmentTaskRegistry(ledger))
    configuration = replace(inputs["role_configuration"], domain_contract_pack_revision=domain.revision)
    manifest = replace(inputs["manifest"], role_configuration_id=configuration.role_configuration_id)
    return dict(inputs, compiled_task=compiled, role_configuration=configuration, manifest=manifest)


for label, child in (
    ("compiler_missing_child_obligation", ab_object("b")),
    ("compiler_missing_child_and_forbidden_observable", ab_object("b", observed=("done", "unsafe"))),
):
    parent = replace(ab_object(), decomposes_to=("b",))
    compiled_inputs = compiler_fixture((parent, child), prohibited=("unsafe",))
    rows.append(probe(label + "_parent", compiled_inputs))
    rows.append(probe(label + "_child", compiled_inputs, object_id="b"))

print(canonical({"imported_prompt": prompt_module.__file__, "imported_admission": admission_module.__file__,
                 "rows": rows, "row_count": len(rows)}))
