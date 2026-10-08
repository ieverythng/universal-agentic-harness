# ARCH-01 independent primary review

Date: 2026-10-08. Scope: the exact-before/current changes to
`src/ab_harness/proposal_admission.py`, `src/ab_harness/prompt_compiler.py`, and
`tests/test_prompt_compiler.py`. No implementation edits or Git mutations were
made. No writer receipts, other reviews, or writer rationale were used.

## Authority and method

Governing sources: `REVIEW.md`, root `AGENTS.md` and `CONTEXT.md`, the foundation's
two-stage admission and prompt-compilation sections, ADR 0001, the masterplan's
current H0 implementation and H1/H2 boundaries, and the development log's frozen
invariant and existing fake-provider prompt checkpoint. The applicable skills
were `code-review` (separate Standards and Spec axes) and `uah-guardrails`.
The orchestrator owns review coordination and repository hooks; this fresh
reviewer performed both axes independently against the supplied exact snapshots.

Affected gate: H0/H1 semantic admission and deterministic prompt presentation.
`SemanticAdmission` owns static object eligibility. `PromptCompiler` consumes
that decision without admission or execution authority. Domain lifecycle and
the environment owner retain execution and effect-evidence authority. This
review does not qualify H2 or close other release-wide findings.

`REVIEW.md` requests `gpt-6.1-sol` at `max` reasoning. The exposed runtime does
not independently identify this agent's actual model/effort, so that pairing is
unverified. The separate different-model review remains the orchestrator's gate.

Inputs were written in [the input manifest](2026-10-08_uah_arch01_primary_inputs.md)
before reading implementation, diff, or changed test source. The public initial
control ran first in isolated current and exact-before copies. Both used the same
current tests and unaffected source/resources/dependencies. Read-only recursive
comparisons found no differences outside the two substituted modules. Independent
probes reported the exact imported temporary source paths and used a separate
bytecode prefix, preventing reuse of checkout bytecode.

Frozen current SHA-256 values were checked at initial execution and again after
the probes, with no drift:

```text
033ba785928c9019b76711ed27c603b6f3f30a2e3110443875bdfea6af019888 proposal_admission.py
9caaf597a1d08983f53f27672e425ba7971cc2b47e9ce0b099f0fa9ba5121ae1 prompt_compiler.py
c04db4be3abc125e43ace67d4416a412f18c2288da8a30362ae85c199c63774b test_prompt_compiler.py
```

Exact-before module hashes were `a2a76bf21eb865934d63b5eeece722b4b7827d659421fb7a5bc566bb3161455c`
and `c76d829b9e6b9e04c6856fcb35ce6f61e26953f881a27cdd3ef79e1016a34b82`.
The supplied exact-before test hash is
`53b19f5e5d9d8c05d5b328034b54874d58e6e35924aa7b543e672d55f47eb183`;
both executable variants deliberately used the current tests instead.

## Standards

0 BLOCKING findings. 0 NIT findings.

| Principle | Result | Evidence in current source |
| --- | --- | --- |
| Separation of concerns | OK | `proposal_admission.py:866` owns the pure static query; `prompt_compiler.py:358` consumes it. Stateful admission remains at `proposal_admission.py:910` and `:947`. |
| Programming by intention | OK | `static_object_rejection_reasons` returns named, ordered reasons; both callers use that decision directly (`proposal_admission.py:935`, `prompt_compiler.py:358`). |
| Encapsulation | OK | The query uses the compiled projection and obligations and returns an immutable tuple (`proposal_admission.py:870`). It exposes no catalog state or execution grant. |
| High cohesion | OK | Projection, direct band, callability, prohibited effects and obligation presence are one task-local rule (`proposal_admission.py:871`). Binding/schema and lineage policy were not moved into it. |
| Low coupling | OK | The added dependency is a one-way portable query from prompt compilation to semantic admission (`prompt_compiler.py:17`). No provider SDK, ROS/NAO import, framework, schema, or domain-owner dependency was added. |

The duplicated static predicate was removed from prompt compilation. No second
policy owner or business rule in rendered templates was introduced. The Fowler
smell baseline disclosed by `code-review` produced no additional change-scoped
finding; formatting rules enforced by tooling were not reported as judgement
findings.

## Spec

0 BLOCKING findings. 0 NIT findings.

The shared rule now includes the existing admission union of `expected_effects`
and `observable_success`, as well as the existing obligation-presence check.
Semantic admission results, ordered reason codes, and emitted admission/rejection
IDs were identical across all 50 before/current probe rows. Prompt choices,
filtered examples, and binding/schema source metadata now omit statically
ineligible objects. Permitted single-object controls retain the same prompt IDs.

| Input / expected behavior | Exact-before | Current |
| --- | --- | --- |
| Expected-only prohibited effect: reject and offer no operation | Admission rejects; prompt refuses | Same |
| Observable-only prohibited effect: reject and offer no operation | Admission rejects; prompt offers the object | Admission rejects; prompt refuses |
| Both effect forms, different prohibited effect names, and reversed effect-list order | Reject | Same rejection and artifact ID |
| Unrelated prohibition or no prohibition | Accept and offer permitted operation | Same result, prompt ID, schema and binding fingerprint |
| Missing compiled obligation | Admission rejects; prompt offers the object | Admission rejects; prompt refuses |
| Two permitted objects in either order | Both offered | Both offered with matching per-object contracts |
| Permitted plus observable-forbidden or obligation-free object, either order | Both offered | Only permitted object offered, exampled and fingerprinted |
| Empty projection, inspect-only/above-band, non-callable | No admissible operation | Same |
| Foreign output type plus all static violations | Ordered role/static reasons | Same ordered reasons and rejection ID |
| Foreign lineage or tampered compiled identity | Reject before decision | Same |
| Candidate/disabled/ambiguous/foreign-environment/foreign-runtime binding, foreign owner, catalog drift, missing schema, invalid arguments | Stateful admission rejects | Same reasons and artifact IDs |

The legitimate ingress/ledger/`TaskSpecCompiler` holdout confirms this is not
limited to rehashed consumer fixtures: a callable same-level decomposition child
without a task obligation was formerly offered alongside its obligated parent.
Current offers only the parent; admission still returns `missing_effect_obligation`
for the child. Adding a prohibited child observable yields the unchanged ordered
reasons `object_effect_prohibited`, `missing_effect_obligation`.

The full inspectable projection still contains excluded objects and describes
their registry callability. That descriptor is not a task authorization label;
the operation schema, examples and source contracts consistently exclude them.
Output enums remain task-owned. No new enum/schema consumer or authority owner
was introduced.

## Executed evidence and limitations

- [Initial execute-before-read control](2026-10-08_uah_arch01_primary_control.md):
  current prompt tests, 26 passed; exact-before under identical current tests,
  24 passed and 2 failed. Both failures are the former observable-only widening.
- [Independent public probe](2026-10-08_uah_arch01_primary_probe.py) and
  [complete results](2026-10-08_uah_arch01_primary_probe_final.json): 50 rows per
  variant, including four real-ingress/task-compiler holdouts. All semantic
  outcomes/IDs match; current has zero choice/metadata, example, per-object
  binding/schema, or private-locator mismatches in those probes.
- [Stateful controls](2026-10-08_uah_arch01_primary_stateful_tests.md): the same
  113 admission/schema/invocation/nested-owner/provenance tests pass in each
  variant. `git diff --check` and the documentation renderer's `--check` passed
  (12 metadata records). Full hooks remain the orchestrator's work.

The first independent harness invocation stopped at a keyword-only fixture
constructor before producing behavior evidence; the harness was corrected,
without editing implementation. An initial positional contract-order check was
stricter than the existing sorted `source_contracts` contract. Its
[raw capture](2026-10-08_uah_arch01_primary_probe_results.json) is retained; the
final check compares object keys and fingerprints. No failed review verdict was
retried or discarded.

Several synthetic consumer variants intentionally bypass task-compiler semantic
consistency (empty object/effect lists and an above-band projected object). Their
results qualify the consumer's rejection behavior, not task-start provenance or
producer validity. Real compiled decomposition cases supply the obligation
holdout. No live provider or native environment was used.

An empty binding output-schema reference or evidence adapter still allows prompt
presentation but causes stateful admission to return `binding_contract_incomplete`
in both versions. That unchanged stateful boundary is outside this static-rule
repair and must not be described as full prompt/admission equivalence. This
review approves only the specified static eligibility contract.

Standards: 0 findings. Spec: 0 findings. No worst issue within either axis.

VERDICT: APPROVE
