# ARCH-01: shared static operation eligibility

**Scoped gate closed 2026-10-08 at 18:39 Europe/Madrid: APPROVE.**

Start 2026-10-08 at 18:23:15 Europe/Madrid; hard stop 18:43:15.
Source freeze target 18:29:15; review target 18:39:15.
HEAD `28fab5e7f2c244d86a64c371f2118017999b2387`, branch `feat/pre-commit-queue`.
Root is the writer. Existing semantic admission owns static operation policy;
PromptCompiler consumes it without acquiring admission or execution authority.

This separately authorized H1 correction addresses original ARCH-01 only.
Frozen public seams are PromptCompiler.compile and SemanticAdmission.admit.
The own public red uses an otherwise valid task whose object has an additional
forbidden observable, while its expected effect remains permitted. Prompt
offers no operation that static semantic policy rejects. Valid expected and
observable effects, inspect-only/non-callable objects, projection membership,
obligation presence and effect combinations are protected controls. Binding,
argument-schema and stateful domain checks remain with existing owners.

Owned files: proposal_admission.py, prompt_compiler.py and
tests/test_prompt_compiler.py. Exact-before copies and complete pre-edit dirty
hash inventory are retained in the evidence directory. Lifecycle, compiled
task, nested artifact-copy mechanisms, O1, dashboard and historical reports
are protected. No new schema, framework, producer-provenance policy, provider
call or Git mutation. One actual public red then the minimal owning rule;
fresh primary and distinct-model review compare exact-before and current bytes.
Full hooks, source tests, canonical docs and both O1 examples follow source
freeze. Stop at the bound or an outside-scope decision, without another round.

SPEC-03 finding accounting must distinguish replay of the original cases from
a universal authority claim. Original probes remain unchanged; an uncaught
rejection is evidence of its first rejected crossing, not execution of later
controls. R5 and raw-ingress provenance remain prerequisite-gated.

## Source freeze

Frozen at 18:26:32, before the 18:29:15 target. Three files are covered by
the evidence directory's `source_frozen.sha256`. SemanticAdmission owns one
pure `static_object_rejection_reasons` method. PromptCompiler consumes that
method when building operation choices. Admission preserves role-output checks,
reason order and subsequent catalog, binding and argument-schema authority.
No lifecycle, artifact-copy, effect-owner or execution-lease implementation
changed in this round.

The own public red returned DID NOT RAISE while semantic admission already
returned `object_effect_prohibited`. The first implementation run exposed a
missing SemanticAdmission import in PromptCompiler, producing NameError; this
was an implementation error, not the intended red, and was fixed before freeze.
The intended case then passed. Five additional fixed expected/observable
effect combinations preserve permitted choices and reject prohibited ones.
Focused prompt, admission, invocation and protected nested-owner tests: 116
passed. Scoped Ruff and whitespace checks pass. Two fresh independent reviews
and full integration are pending at freeze; no release gate is claimed.

## Original finding replay and current integration

Root's full shared-tree suite passes: 510 tests in 10.85s. Both O1 example
freshness checks pass. This is integration evidence, not independent approval.

The unchanged October 5 ARCH-01 probe now raises `compiled task exposes no
direct proposal operations`. Its later normalization/admission statements do
not execute in that run. The own public regression independently checks the
semantic rejection and prompt exclusion for the same prohibited-observable
mechanism. Its exact log is retained, not rewritten to return a green exit.

Original SPEC-03 accounting is supported by additional read-only reruns:

- The unchanged October 5 catalog function no longer obtains an admission. Its
  later ledger call fails on NoneType. A separate public companion reconstructs
  the original catalog input and reports `catalog_object_mismatch`; the
  unchanged catalog control reports accepted. This separates intended
  rejection from the old probe's assumption that admission always succeeds.
- The unchanged R2 post-admission owner probe rejects with `execution lease
  object semantics no longer match the catalog` before dispatch. Subsequent
  control calls in that original script do not execute.
- The unchanged original R4 control probe separately records valid dispatch
  (one call and receipt), pre-dispatch drift (zero calls), mid-handler drift
  (one call, no receipt, `undeclared_observed_effect`), reviewed binding
  replacement, old read-only history and active metadata downgrade rejection.

Those exact reproductions and the previously approved nested-owner controls
close the original demonstrated SPEC-03 catalog mechanism within their scope.
They do not establish universal all-catalog security, authentic ingress
production, freshness, output validation or H0/H1 release exit. Original
CHANGES receipts remain intact. Replay logs and the companion command are
retained in this round's evidence directory; no original probe was edited.

## Independent gate and final integration

The [fresh primary](2026-10-08_uah_arch01_primary_review.md) and
[fresh second](2026-10-08_uah_arch01_second_review.md) both return APPROVE,
zero blocking and zero nit findings, and report all five design principles.
Both finish before the 18:39:15 soft target and 18:43:15 hard stop. Each
predeclares inputs and executes the initial public control before source/diff
inspection. Exact-before and current trees share unaffected dependencies and
the same candidate tests.

Orchestration requested `gpt-6.1-sol/max` for the primary and
`gpt-6-astra/max` for the second using distinct fresh agents. The accepted tool
requests preserve that configuration provenance; independent backend/model
identity is unavailable and is not attested by either reviewer or root.

The primary executes 50 before/current public rows, including real-ingress
decomposition holdouts, plus 113 unchanged stateful controls in both trees.
The second executes 29 independent public cases and 135 candidate tests
against 133 passes and two intended before failures. Semantic admission and
rejection artifacts and reason ordering are identical in every paired row.
Permitted prompt controls retain their identities; prohibited-observable and
obligation-free operation choices, examples and binding references are removed.
Reviewer fixture/setup corrections are retained in their reports and are not
counted as code defects or discarded review verdicts.

Root confirms frozen source/test hashes, 510 full tests, all-files hooks,
canonical-doc synchronization, both O1 example checks and whitespace checks.
No code changed after source freeze. ARCH-01's original demonstrated mechanism
is closed at these reviewed bytes. Source-specific approval does not imply
H0/H1 exit, H2 parity or complete prompt/admission equivalence.

The primary records an unchanged additional limit: incomplete binding output
schema/evidence-adapter references can still be presented by PromptCompiler
and rejected later as `binding_contract_incomplete`. Binding completeness and
other stateful checks are outside this pure task-object eligibility correction.
No additional repair is authorized here. Original STD-02, SPEC-02 and ARCH-02
remain open; synthetic full-chain work is not executed and producer provenance
still awaits the human's choice. Dashboard remains stopped. No Git mutation,
provider invocation or automatic follow-on round occurred.
