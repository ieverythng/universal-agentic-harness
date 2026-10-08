# Independent Spec review: frozen unchecked-support pilot

## Bounded summary (under 400 words)

The 14-source/22-test target is not approved. Two target-contract defects, one dependency regression, and one optional API consistency issue were demonstrated. No supported scope-creep finding was established.

1. **BLOCKING, SPEC-PILOT-01 (1 of the 4 found so far): malformed additional-property policy fails open.** `ObjectArgumentSchema.issue(allow_additional_properties='false')` accepts a string, semantic admission accepts an extra argument, and the leased owner receives it. Boolean `False` correctly rejects. This is a partial implementation of the newly introduced reviewed-schema gate, not a regression from a baseline that had no schema gate.
2. **BLOCKING, SPEC-PILOT-02 (2 of the 4 found so far): sole-writer ingress contract remains incomplete.** Public `LifecycleLedger.record(TaskIngressFact(...))` accepts fabricated resume and notify facts without any `EnvironmentIngress` or authority decision. Both baseline and candidate accept them. This is retained historical debt in the current sole-writer requirement, not an introduced regression.
3. **BLOCKING dependency, SPEC-PILOT-03 (3 of the 4 found so far): genuine historical task replay regresses.** A two-event ledger produced through baseline public start/compile APIs reloads in baseline but candidate rejects it with `compiled task requires budget limits`. The failing reducer is in context-only `lifecycle.py`; this finding does not claim a review of the selected 13 files.
4. **NIT, SPEC-PILOT-04 (4 of the 4 found so far): idempotent budget requests bypass input-type validation.** After a one-unit debit, `units=True` or `1.0` returns the prior grant; a fresh request rejects those types. No extra debit or demonstrated authority increase occurs.

Executed: four standalone adversarial scripts on both copies, genuine baseline-ledger replay on both versions, 458 candidate tests across all 22 target test files, and 93 baseline tests across its six existing target test files. Portable import scan passed. Wheel checks fail identically because the available Python lacks `setuptools`; the initial broad baseline collection also lacked `.git` context.

Separation of concerns and encapsulation have the violations above. Programming by intention, high cohesion, and low coupling are OK within inspected target seams. Coverage is bounded: not every test hunk or every reason-code/UI consumer received manual inspection; independent competing-process and exhaustive actor interleavings remain incomplete. Missing coverage is not a proven defect and no unreviewed bytes are approved.

## Identity, scope, independence, and timing

- Requested reviewer: `gpt-6-astra` at `max`, fresh context. Actual backend model/effort attestation: **unverifiable** from observable tools. No claim of exact backend attestation is made.
- REVIEW.md was read first. The immutable predeclaration was created before any implementation, test, or diff inspection: `/tmp/uah-spec-review.B9Og0tph/PREDECLARATION.md`, SHA-256 `c3b1902b94d09ce298f386487be53e4707325a843a58152034477ed8f3c1b116`.
- Execution GO received separately. First execution clock: `2026-10-08 19:42:32 UTC`; hard stop: `19:58:17 UTC`.
- Base: `06f5a29daef9bb877fb08b6c6ee47d870df94d71`, supplied pure snapshot `/tmp/uah-pilot-review-before`.
- Candidate: supplied `/tmp/uah-pilot-review-candidate`; exact target list `/tmp/uah-pilot-preparation/review36.paths`.
- Executed only on disposable `/tmp/uah-pilot-spec-result/before` and `/tmp/uah-pilot-spec-result/candidate`. No implementation or test files were modified. No hooks, no-mistakes, staging, commit, push, or external-chat actions were performed.
- All 51 frozen candidate file hashes were checked before and after execution against `candidate51.sha256`; every hash matched. This establishes copied-byte identity, not approval of context-only files. Full final check: `final-manifest-check.log`.
- Selected 13 index-context files and two generated O1 outputs were dependencies/context only. ARCH-02 label/provenance changes and R5 synthetic work were excluded. Existing review receipt contents and writer findings were not used.
- Governing contract: frozen AGENTS, CONTEXT, foundation current H0/H1 seams, masterplan current implemented/deferred and H0/H1 gates, Observatory contract, accepted September 8 grill, and relevant dated development-log checkpoints. Source status assertions in those contracts were not treated as test evidence.
- Release gates affected: H0 portable admission/lineage grammar and H1 deterministic runtime. Owners: TaskIngressAuthority for task-bearing ingress, semantic admission for operation eligibility/schema, domain owner for leasing/execution/evidence, common ledger for append/replay. Dynamic memory/scheduling and live H2 parity remain deferred.

## Finding evidence

### SPEC-PILOT-01: malformed schema policy permits unreviewed arguments

**BLOCKING. 1 of the 4 found so far.** Introduced gate is incomplete; not a baseline regression.

Governing spec: `2026-09-08_uah_identity_environment_and_memory_grill.md:574-576`: “Semantic admission now validates canonical arguments through a reviewed, content-addressed portable object-schema subset. The subset covers required fields, top-level JSON types, and additional-property policy.” Foundation `:478-480` requires input arguments to be validated against the reviewed schema before semantic admission. The public schema contract declares `allow_additional_properties: bool` in `schema_validation.py:102` and `:121`.

Source: `src/ab_harness/schema_validation.py:139-169` verifies identity without validating this policy's boolean type; `:205-209` uses Python truthiness. The later admission and owner path accepts the resulting schema identity.

Reproduction: `probe_authority.py`, cases `additional-policy/False`, `additional-policy/'false'`, and `additional-policy/1`. The self-contained fixture uses public APIs to create one task, normalize `{'text':'hello','not_reviewed':'payload'}`, admit, lease, and execute it.

Expected: invalid policy representations are rejected at schema construction/verification, before a schema identity can authorize argument acceptance. This is not a request to coerce the string `'false'` into a boolean.

Actual candidate: `False` returns semantic rejection `proposal_arguments_schema_invalid`; `'false'` and `1` pass and the owner sees `{'not_reviewed': 'payload', 'text': 'hello'}`. Baseline has no `ObjectArgumentSchema` and accepted extra fields with no schema gate. Logs: `candidate-authority.log`, `before-authority.log`.

### SPEC-PILOT-02: public raw existing-task facts bypass ingress authority

**BLOCKING. 2 of the 4 found so far.** Retained historical contract debt, not a new regression.

Governing spec: accepted grill `:106-111`: TaskIngressAuthority classifies/admit items and “is the only public writer for accepted task-bearing ingress”; CONTEXT `:256-269` gives it rule matching, ledger append, and registered resume/notify lineage. Foundation `:389-394` also reserves task-bearing writes to that authority.

Target source: `src/ab_harness/task_ingress_authority.py:328-343` emits ordinary `TaskIngressFact` values for resume/notify. Dependency: `src/ab_harness/lifecycle.py:596-602` reserves only starts, while `:1066-1091` accepts caller-created existing-task facts. `task_registry.py:137-148` then projects them as admitted ingress.

Reproduction: `probe_authority.py` cases `raw-ingress/resume_task` and `raw-ingress/notify_task`. After a genuine task start/compile, call `ledger.record(TaskIngressFact(..., ingress_artifact_id='forged:artifact', decision_id='forged:decision', action=...))`. No ingress artifact or classifier invocation is supplied for that fact. The notify case is accepted even though the fixture pack contains no notify rule.

Expected: direct caller-authored task-bearing ingress cannot be appended as an accepted authority fact; legitimate resume/notify should use the classifier-owned command boundary.

Actual: both versions append `task_resumed` / `task_notified`. Candidate's public registry resolves the fabricated ingress to the task. Baseline projection API differs, but append success is directly established from its emitted events. Logs: `candidate-authority.log`, `before-authority.log`. Start-command hardening itself is not alleged to be broken.

### SPEC-PILOT-03: baseline-created ledger is no longer readable

**BLOCKING dependency. 3 of the 4 found so far.** Introduced baseline-to-candidate regression in context-only lifecycle dependency.

Governing spec: CONTEXT `:284-285` and Observatory `:253` preserve historical unmarked starts for read-only use; CONTEXT `:315-319` and accepted grill `:682-688` preserve earlier v1 task events and their identity. Foundation `:499-505` distinguishes historical metadata reading from active authority. Read-only replay must not manufacture budget authority, but rejecting the entire genuine historical trace is not read-only preservation.

Failing source: `src/ab_harness/lifecycle.py:1883-1895`, reached by the unchanged v1 event loader. Target `task_compiler.py:21-22` introduces v2 task artifacts; this report does not propose treating historical v1 tasks as active v2 authority.

Reproduction: `probe_historical.py create <new-path>` under the pure baseline calls public TaskIngressPolicy, TaskSpecCompiler, and LifecycleLedger.record. It emits genuine `task_started` and `task_compiled` v1 envelopes. Run `probe_historical.py load <same-path>` under each package.

Expected: baseline history remains inspectable/replayable without granting fresh execution or compilation authority.

Actual baseline: `loaded=true`, two events, terminal status `null`. Candidate: `loaded=false`, `ValueError: compiled task requires budget limits`. The old public `task_compiled` projection has no `budgets` field at all; this is not just a missing retry default. No JSON was manually forged or rehashed.

Frozen evidence: `baseline-public-ledger.jsonl`, SHA-256 `3fa6f142bc300f87b9653f8db7fadbdcae73223e7e29cd48e6880316ce91b5e5`; logs `historical-create.log`, `historical-before.log`, `historical-candidate.log`.

### SPEC-PILOT-04: idempotent units accept otherwise invalid types

**NIT. 4 of the 4 found so far.** New public API consistency issue, no demonstrated budget increase.

Governing spec: accepted grill `:628-634` requires idempotent subjects whose units cannot change; development log `:1120-1122` requires integer budget quantities. Source: `src/ab_harness/runtime_controls.py:251-257` returns an existing decision before new-input type validation, using equality (`True == 1 == 1.0`).

Reproduction: `probe_authority.py` cases `budget-idempotent-units/True` and `/1.0`: consume one model-call unit, then repeat that subject with either malformed type.

Expected: input validity is consistent on first and repeated requests. Actual candidate: returns the existing one-unit grant; a distinct `units=2` rejects. Baseline API is absent. Existing recorded decision remains unchanged and no second grant is written; this is optional hardening rather than an authority bypass.

## Execution appendix

All probes were reviewer-authored and use public package contracts. They do not import candidate test fixtures or internal implementation helpers. Their fixture inputs derive from the predeclaration and accepted contracts. The first probe was executed on both versions before reading implementation/test/diff contents; public API signature discovery preceded it. Later scripts elaborate the predeclared identity, malformed-type, multi-entity, time, replay, and secret-sentinel cases after source inspection.

For each disposable tree, the common invocation is:

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python /tmp/uah-pilot-spec-result/probe_initial.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python /tmp/uah-pilot-spec-result/probe_authority.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python /tmp/uah-pilot-spec-result/probe_matrix.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python /tmp/uah-pilot-spec-result/probe_invocation.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python /tmp/uah-pilot-spec-result/probe_historical.py load /tmp/uah-pilot-spec-result/baseline-public-ledger.jsonl
```

Evidence logs are `{before,candidate}-{initial,authority,matrix,invocation}.log`. The initial four-field budget cases cannot run meaningfully in baseline because `retry_attempts` did not exist; `probe_authority.py` reruns compatible three-field cases and establishes the before/after difference. Initial edge calls intentionally carry an invalid supplied identity, so valid edge issuance/graph behavior is covered separately in `probe_matrix.py`.

Candidate test command: `python -m pytest -q -p no:cacheprovider` with all 22 test paths from `review36.paths`; `PYTHONPATH=src`, `PYTHONDONTWRITEBYTECODE=1`. Result: **458 passed in 11.11s** (`candidate-tests.log`). Baseline runs the six existing target files with the same flags: **93 passed in 0.57s** (`before-target-tests.log`). Missing newly introduced test files were not fabricated or copied into the baseline.

Additional `tests/test_package_boundaries.py` on both copies: one import-boundary test passed, wheel test failed because the available interpreter lacks `setuptools`, not because of candidate code. See `{before,candidate}-boundaries.log`. No install was attempted. Initial broad baseline pytest collection also failed because the disposable snapshot has no `.git`; the targeted comparison avoids that unrelated precommit-cache fixture (`before-tests.log`). Shell pipelines preserve diagnostic output; quoted pytest counts/status come from pytest's own report, not the pipeline's final exit status.

An independent AST import scan found only standard-library and `ab_harness` import roots and no ROS, NAO, OpenAI, Anthropic, or NAOqi imports in portable core (`candidate-import-audit.log`).

## Full target coverage matrix

“Exercised” is bounded evidence, not an exhaustive proof. “Test coverage” identifies supplemental repository tests that were actually executed. All 14 target source modules were inspected at their affected public/trust boundaries. Not all 7,436 lines of test delta were manually read.

| Target source | Independent public evidence | Supplemental exercised tests / residual limit |
| --- | --- | --- |
| domain_lifecycle.py | schema-approved dispatch chain, wrong lease owner, exact lease reuse | two-stage admission and nested/snapshot/current-provenance tests; all concurrent domain races not independently enumerated |
| environment.py | cancelled/timed-out/tampered dispatch does not call handler; restart duplicate executes once | two-stage owner/evidence tests; malformed-result combinations not exhaustively independently replayed |
| environment_ingress.py | scalar/nested tampering, duplicate/mutable/empty lineage, leap/year timestamps | environment ingress tests; timestamp string acceptance is historical, not filed as a new defect |
| model_invocation.py | normal, restart duplicate, wrong actor, recorded timeout, nonfinite output, redacted failure, release to standby | all invocation tests; arbitrary provider request mutation leaves an outstanding call, recorded as adversarial fault behavior, not classified as an authority defect |
| operation_edges.py | three operations in both orders, decomposition/continuation, duplicate, cycle, second parent, target lease, cross-frame refusal | two-stage operation-edge tests; cross-frame implementation intentionally deferred |
| prompt_compiler.py | independent public compilation followed by exact invocation; wrong-actor prompt rejected | prompt compiler suite exercises scope/schema/manifest mutations; all wording/example combinations not independently enumerated |
| proposal_admission.py | empty/ambiguous payload, claimed effects, two references both orders, unknown object, wrong output, malformed argument, schema policy fail-open | admission/schema/snapshot/nested suites |
| runtime_controls.py | cancellation, recorded timeout, leap-day threshold and equivalent zone, model-call idempotent types | runtime budget/two-stage tests; independent retry and writer-interleaving matrix incomplete |
| schema_validation.py | correct False versus string/number policy; missing/null type rejection | argument schema tests; SPEC-PILOT-01 |
| task_compiler.py | public valid task build in both trees; strict numeric changes; genuine baseline event generation | task compiler suite incl start provenance; historical reducer compatibility fails in context dependency |
| task_ingress_authority.py | genuine public start, fabricated resume/notify bypass | ingress/start concurrency/terminal tests; historical SPEC-PILOT-02 |
| task_registry.py | public projected forged ingress, exact task lineage from real starts | ingress/lifecycle/compiler tests; registry remains structurally read-only |
| ab_harness_nao/qualification.py | public CLI accepted, rejected, required-effect counterexample; portable dispatch fixture | recorded NAO suite; no live NAO parity claim |
| ab_harness_nao/smoke.py | public CLI in both versions; candidate terminal counterexample added honestly | CLI and recorded NAO suites; actual ROS/provider excluded |

| Target test file | Executed candidate | Baseline availability |
| --- | --- | --- |
| test_admission_active_provenance.py | yes | absent |
| test_admitted_object_snapshot.py | yes | absent |
| test_agent_configuration.py | yes | absent |
| test_agent_identity.py | yes | absent |
| test_agent_runtime.py | yes | absent |
| test_agent_runtime_example.py | yes | absent |
| test_argument_schema_validation.py | yes | absent |
| test_cli_smoke.py | yes | yes |
| test_content_identity_compatibility.py | yes | absent |
| test_environment_ingress.py | yes | yes |
| test_lifecycle_ledger.py | yes | yes |
| test_model_invocation.py | yes | absent |
| test_nested_admission_owner.py | yes | absent |
| test_observatory.py | yes | absent |
| test_observatory_format.py | yes | absent |
| test_observatory_raw_identity.py | yes | absent |
| test_prompt_compiler.py | yes | absent |
| test_recorded_nao_qualification.py | yes | yes |
| test_research_dashboard.py | yes | absent |
| test_runtime_budget_contracts.py | yes | absent |
| test_task_compiler.py | yes | yes |
| test_two_stage_admission.py | yes | yes |

## All five design principles

1. **Separation of concerns: violation.** SPEC-PILOT-02, `task_ingress_authority.py:328` and dependency `lifecycle.py:1066`, leaves an additional producer of accepted ingress facts outside the named authority. The environment owner, semantic gate, and ledger otherwise retain separate responsibilities in exercised paths.
2. **Programming by intention: OK within inspected scope.** Public compile, normalize, admit, lease, execute, and evaluate methods expose the intended stages; fake NAO qualification follows those stages without a direct-dispatch fallback.
3. **Encapsulation: violation.** SPEC-PILOT-01, `schema_validation.py:139`, admits a malformed authority-policy value instead of enforcing its owning contract. Nested operation/lease identity mutation otherwise fails closed in independent probes.
4. **High cohesion: OK within inspected scope.** Schema validation, ingress association, invocation, and domain execution have coherent responsibilities; no new second memory/task store was found.
5. **Low coupling: OK within inspected scope.** Portable core imports remain standard-library/portable-package only. NAO consumes portable contracts. Shared static eligibility remains owned by semantic admission rather than duplicated in prompt generation.

## Residual coverage and release limits

- Complete independent competing-process/actor interleaving coverage, every rejection code's ultimate UI text, every persistence consumer, and line-by-line manual review of every target test hunk were not completed in this pilot. Those are coverage gaps, not evidence that those paths are defective. No smaller split is implicitly approved.
- Agent configuration/identity/allocation and O1 implementations were context dependencies, not selected source targets. Their tests ran, and the invocation setup exercised registration/allocation/release, but they receive no independent source approval here.
- Memory retrieval/context, stale-effect-evidence policy, false-completion policy, dynamic scheduling, native readiness signatures, and H2 live parity remain declared deferred seams. They were not mislabeled as missing deliverables of this finite batch.
- The package's fail-closed handling of a provider mutating its frozen request via `object.__setattr__` leaves an outstanding invocation. Whether arbitrary in-process provider mutation belongs to the supported provider threat model needs an owner decision; no new recovery or broad authority requirement is inferred here.
- Tests, probes, and this REVIEW do not replace no-mistakes or authorize any commit/push. Fixes require a new frozen candidate and fresh independent review.

VERDICT: CHANGES
