import json
import runpy
from dataclasses import replace
from pathlib import Path

from ab_harness.contracts import AgentOutput
from ab_harness.prompt_compiler import PromptCompiler
from ab_harness.proposal_admission import ProposalNormalizer, SemanticAdmission
from ab_harness.schema_validation import InMemoryArgumentSchemaRegistry


namespace = runpy.run_path(str(Path.cwd() / "tests/test_prompt_compiler.py"))
globals_ = namespace["_inputs"].__globals__
original_object = globals_["ABObjectView"]
original_task = globals_["TaskSpec"]
globals_["ABObjectView"] = lambda *args, **kwargs: replace(
    original_object(*args, **kwargs),
    observable_success=("note_written", "prohibited_observable"),
)
globals_["TaskSpec"] = lambda *args, **kwargs: replace(
    original_task(*args, **kwargs),
    prohibited_effects=("prohibited_observable",),
)

# The repository fixture constructs this task through public ingress and compilation.
inputs = namespace["_inputs"]()
prompt = PromptCompiler().compile(**inputs)
print("Task identity verifies", inputs["compiled_task"].verify_identity() is None)
print(
    "Prompt exposed operations",
    [
        choice["properties"]["object_id"]["const"]
        for choice in json.loads(prompt.output_schema_json)["oneOf"]
    ],
)
normalized = ProposalNormalizer().normalize(
    compiled_task=inputs["compiled_task"],
    output=AgentOutput(
        "operation",
        {"object_id": "write_note", "arguments": {"text": "bounded note"}},
        ("write_note",),
    ),
    operation_id="operation:independent-prohibited-observable",
    raw_output_artifact_id="raw-output:independent",
)
print("Normalization", normalized)
admission = SemanticAdmission(
    catalog=inputs["binding_catalog"],
    environment_id=inputs["environment_id"],
    runtime_mode=inputs["runtime_mode"],
    schema_validator=InMemoryArgumentSchemaRegistry(inputs["argument_schemas"]),
).admit(inputs["compiled_task"], normalized.proposal)
print("Semantic admission", admission.accepted, admission.reason_codes)
