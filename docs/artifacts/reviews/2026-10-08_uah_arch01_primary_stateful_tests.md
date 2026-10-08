# ARCH-01 independent stateful controls

Executed once per isolated variant on 2026-10-08, after the public initial control
and source inspection. Same current tests and unaffected dependencies in both.

Command, from `/tmp/uah-arch01-primary.qXMxdY/<variant>`:

```bash
PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/uah-arch01-primary.qXMxdY/test-bytecode-<variant> /home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest -q tests/test_two_stage_admission.py tests/test_argument_schema_validation.py tests/test_model_invocation.py tests/test_nested_admission_owner.py tests/test_admission_active_provenance.py
```

Current: exit 0, `113 passed in 4.06s`.
Exact-before: exit 0, `113 passed in 4.06s`.

These controls include semantic rejection replay and nonterminal labels, ordered
static reasons, input-schema validation, approved/candidate and owner bindings,
catalog drift, proposal/task identity and lineage, independent domain leasing,
lease-only execution, budget/cancellation/timeout/retry controls, nested-owner
consumption, and model invocation against fake providers. They do not prove live
provider readiness, release-wide H0/H1 closure, or H2 qualification.

Recursive read-only comparisons excluding the two changed modules and bytecode
reported no differences between the variants' unaffected source trees or tests.
`git diff --check` returned exit 0.
`python scripts/render_agentic_harness_docs.py --check` returned exit 0 and
`Checked 12 metadata records`. The orchestrator owns the full hook suite.
