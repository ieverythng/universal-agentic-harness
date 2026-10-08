from dataclasses import replace
from pathlib import Path
import runpy
import json


ROOT = Path(__file__).resolve().parents[4]

try:
    from ab_harness import TaskSpecCompiler
except ImportError:
    print("BASELINE_UNAVAILABLE: TaskSpecCompiler")
else:
    # Fixture builder constructs fake lineage exclusively through public seams.
    fixtures = runpy.run_path(str(ROOT / "tests/test_task_compiler.py"))
    inputs = fixtures["_compiler_inputs"]()
    domain = inputs["domain_contract_pack"]
    revision = domain.revision
    old_rule = domain.effect_rules[0]
    object.__setattr__(
        domain, "effect_rules", (replace(old_rule, failure_policy="retryable"),)
    )
    try:
        compiled = TaskSpecCompiler().compile(**inputs)
    except Exception as exc:
        print(json.dumps({"result": type(exc).__name__, "message": str(exc)}))
    else:
        print(
            json.dumps(
                {
                    "result": "accepted",
                    "original_policy": old_rule.failure_policy,
                    "compiled_policy": compiled.effect_obligations[0].failure_policy,
                    "revision_unchanged": compiled.domain_contract_pack_revision
                    == revision,
                }
            )
        )
