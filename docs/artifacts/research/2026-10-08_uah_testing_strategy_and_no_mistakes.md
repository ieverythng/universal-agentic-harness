# UAH testing strategy and No-Mistakes evaluation

Date: 2026-10-08. Status: decision-ready research and unchanged-vendor skill installation, not an adopted testing policy or independent release review.

## Recommendation

Prefer public-contract integration scenarios for new behavior and scoped local iteration. Keep focused deterministic contract tests and adversarial matrices where they distinguish separate authority crossings. Do not delete tests to meet a numerical target or replace them with a small happy-path end-to-end suite.

The current snapshot has 342 test functions expanding to 549 cases, not 549 implementation-coupled unit tests. All 549 passed in 12.02 seconds. This does not contradict the user's concern about token cost: repeated fixture generation, agent rereading, repair loops and review may dominate development expense even when execution is cheap. Those token costs were not measured.

Use No-Mistakes' independent-oracle guidance as an experiment input. The unchanged upstream skill is installed locally, but the binary, daemon and automatic publication workflow are not installed or enabled. Its default workflow cannot replace UAH's deterministic gates or required independent review. Its automatic repairs and broad invocation triggers require separate bounded adaptation before use on this dirty checkout.

AgentLint is complementary: local deterministic rules can flag forbidden imports or sensitive paths without model calls, whereas No-Mistakes orchestrates probabilistic review and scenario evidence. Neither establishes environment-owner truth, proves model obedience, or waives admission/replay tests. See the separate [AgentLint mapping](/home/juanbeck/universal-agentic-harness/docs/artifacts/research/2026-10-08_uah_agentlint_guardrail_review_mapping.md).

## Scope, authority and provenance

The user authorized parallel upstream/testing research and installing the No-Mistakes skill. No source/test deletion, hook narrowing, canonical policy edit, runtime initialization, upstream agent/model execution, commit, push, PR or branch protection change occurred in this pass. Higher-priority UAH instructions remain authoritative. Broad instructions inside a vendored skill do not grant new publication or credential authority.

The user subsequently clarified the commit boundary: commits on current working branches remain human-controlled. A separately enabled full No-Mistakes experiment may make its own commits only in its own isolated worktree and dedicated branch. This conditional permission does not enable that workflow now, authorize commits on existing working branches, or grant push/PR authority. Any adapted setup must preserve that separation explicitly.

The testing audit examined the frozen dirty-worktree copy at `/tmp/uah-agentlint-measure-epv03i`. Links in its detailed section deliberately retain that frozen path and line pins. It includes staged, unstaged and untracked files, including deferred synthetic-owner work; inspecting or passing those files is not qualification or promotion. The 34 test hashes are recorded below, and the companion AgentLint handoff records the 39-source-file manifest.

The validation clone is `/tmp/uah-agentlint-validation-20261008`, with isolated Git metadata and the same source/test snapshot. Its environment uses the existing repository virtualenv, without new provider/runtime dependency installation. Validation is not certification of DEV's selected staged commit. Historical shared HEAD `864c6d3` was corrected to `06f5a29` during this work; the research snapshot did not silently become the corrected staged selection.

Research publication was held during that correction, then explicitly released for dated research artifacts and this exact vendor skill only. Shared Git/index state was not changed. Coordination goes through GRILL, with no direct DEV messaging. The AgentLint pass had its own 19:22 UTC bound; this separately authorized test/No-Mistakes pass has a 19:40 UTC bound. No continuing campaign or autonomous follow-up is implied.

## Measured suite execution

Command, executed against the isolated snapshot:

```sh
/home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest -q --durations=10 --junitxml=/tmp/uah-testing-audit-20261008.xml
```

Result: **549 passed in 12.02 seconds**. JUnit suite time was 11.873 seconds, a different timing boundary from pytest's displayed duration. Collection with isolated Git metadata took 0.22 seconds.

| Test module | Cases | Aggregate case time, seconds |
| --- | ---: | ---: |
| Research dashboard | 52 | 4.252 |
| Admitted object snapshot | 32 | 1.262 |
| Nested admission owner | 25 | 1.078 |
| Package boundaries | 2 | 1.050 |
| Model invocation | 17 | 0.889 |
| Two-stage admission | 48 | 0.744 |
| Active admission provenance | 16 | 0.632 |
| Agent runtime | 23 | 0.547 |
| Lifecycle ledger | 27 | 0.285 |
| Observatory | 23 | 0.172 |

The slowest individual case was the stale-build wheel test at approximately 0.94 seconds. Dashboard subprocess scenarios account for roughly a third of suite time. These are timing observations from one machine/snapshot, not universal benchmarks. No live model/robot/backend call, coverage or mutation score, actual authoring/review token count, provider charge, or before/after savings experiment was measured.

JUnit evidence SHA-256: `e142fbfabc22e9007470507af0b4ebb0cf6e1c0ce14065c605a164abab3adfcc`.

## Installation record

Installed with the standard skill-installer helper at the user's request:

- Source: [kunchenguid/no-mistakes](https://github.com/kunchenguid/no-mistakes/tree/420adfd317e29e31bf6b5cd5d770529580084610).
- Pinned revision: `420adfd317e29e31bf6b5cd5d770529580084610`, source version 1.91.0.
- Installed skill: [SKILL.md](/home/juanbeck/universal-agentic-harness/.codex/skills/no-mistakes/SKILL.md).
- Preserved exact upstream notice: [LICENSE](/home/juanbeck/universal-agentic-harness/.codex/skills/no-mistakes/LICENSE).
- Skill SHA-256: `313374bcd2ba43da08f0ac7e179244f2804a9088b8cf44549f862e6bc9a122c5`.
- License SHA-256: `945016bd37e1ba7211622ef60ee1d23ab727896ba7710edd21e8fbe983863969`.

Both hashes matched the pinned upstream files. The skill text was not adapted and no wrapper or replacement policy was added. It becomes available on the next turn, not retroactively as the active governing skill for this audit. Existing AGENTS/REVIEW/skills remain unchanged. The installation is unstaged.

The upstream Go binary, installer, `init`, proxy remote, hooks, daemon, telemetry-enabled workflow and native-agent execution were not run. Installation is not evidence that this desktop runtime can drive the upstream native agent or that a provider/model/cost profile is configured.

## Proposed adoption sequence, for GRILL decision

1. Agree a public scenario inventory by selecting existing tests, approximately 15 to 25 scenarios across the nine families below. Count follows distinct failure modes, not a quota. Run the relevant seam and attack cases during local red/green iteration; preserve the current full hooks before commit.
2. Pilot advisory test-quality review on one small, frozen accepted diff. Record each test's public behavior, independent oracle, plausible incorrect behavior, and demonstrated before/after failure where feasible. Report findings, not automatic changes or deletion.
3. If authorized, consolidate public-contract builders and rewrite the four tooling tests identified below. Remove a predecessor only after an explicit coverage map and old-defect/controlled-mutation evidence. Do not hide authority setup in magic fixtures.
4. Consider a UAH-specific bounded workflow adaptation in a separate change. First resolve publication authority, hook preservation, reviewer-model independence, high-risk repair revalidation, sandbox/credential scope and aggregate spending limits. Adaptation requires its own review; this audit does not edit the vendor skill.
5. Only then consider a disposable runtime trial: explicit model and sandbox posture, isolated HOME/credentials, no writable production remote/forge credentials, disabled telemetry/update checks, one initial review plus at most one repair/rereview, total wall-time/token/provider-budget caps set by the user, and independent UAH hooks. These are proposed experiment bounds, not runtime defaults.

Measure accepted defects found, false positives, preserved failure modes, test-writing/repair tokens, review tokens, human review time and total provider spend. Include rule-maintenance/review overhead. Fewer tests or fewer model calls alone is not the acceptance criterion.

The user wants REVIEW and No-Mistakes explored side by side. Keep the existing REVIEW process as the qualification authority, including its independent high-risk review requirements. The proposed No-Mistakes lane produces advisory changed-file findings and executable scenario evidence, with a frozen diff identity and explicit limits. Do not equate its model verdict with formal REVIEW completion, or duplicate full review passes by default. GRILL should decide which low-risk changes can benefit from that lane and which sensitive seams still require the existing deeper review. This is a proposed allocation of work, not a new review policy or an automatic waiver.

The named TDD skill influenced this recommendation by preferring public seams, independent expectations and vertical red/green behavior slices. UAH guardrails preserved authority/replay boundaries; deslop-refactor guidance treats complexity as a review signal rather than permission to fragment cohesive domain owners. No code refactor was performed.

## UAH testing strategy audit

Date: 2026-10-08. Scope: read-only inspection of `/tmp/uah-agentlint-measure-epv03i`, the frozen source copy supplied by the parent audit. Collection also used `/tmp/uah-agentlint-validation-20261008`, whose source, tests, scripts, documentation, and skill files were overlaid from that same copy and which has isolated Git metadata. No source, test, hook, release contract, or review rule was changed. This is a strategy audit, not a qualifying independent review of a change.

### Decision

Prefer public-contract integration tests for new behavior, with a small named scenario inventory and independent oracles. Do not replace the current suite with a few happy-path end-to-end tests. The premise that the repository has 500-plus implementation-coupled unit tests is not supported: the snapshot contains 342 test functions expanding to 549 cases, and substantial existing coverage already crosses public admission, ledger, owner, provider-port, and command seams.

The concrete efficiency opportunities are fixture consolidation, a few internal tooling mocks, clearer separation of freshness from correctness checks, and scenario-based selection during local iteration. Test deletion requires replacement evidence for the same failure mode. Runtime expense and model-token expense are different questions; neither is established by the case count.

### Governing contracts and method

Read the root `AGENTS.md`, `CONTEXT.md`, `REVIEW.md`, named TDD skill and its complete `tests.md` and `mocking.md`, UAH guardrails, research skill, current masterplan sections, foundation ownership contract, ADR 0001, Observatory contract, adaptive extension boundary, and current development-log entries. The TDD skill makes public seams and independent expectations the criterion, not whether pytest executes a function. Its new-test seam confirmation requirement remains applicable to future implementation; no new test was written here.

Affected release scope: H0 contract/replay and H1 runtime prerequisites to H2 NAO parity. The portable kernel owns deterministic admission and lifecycle serialization; environment owners own native execution and effect evidence. Observatory is read-only, providers supply untrusted output, and Workbench remains candidate-only. The current masterplan retains synthetic replay/failure-suite exit requirements despite NAO-first ordering. The development log explicitly records incomplete H0/H1 qualification and deferred, unapproved R5 source. See [masterplan queue](/tmp/uah-agentlint-measure-epv03i/docs/plans/universal_agentic_harness_masterplan.md:1620), [current development state](/tmp/uah-agentlint-measure-epv03i/docs/plans/universal_agentic_harness_development_log.md:18), [ADR 0001](/tmp/uah-agentlint-measure-epv03i/docs/architecture/decisions/0001-semantic-objects-and-shadow-first-bindings.md:25), and [Observatory ownership](/tmp/uah-agentlint-measure-epv03i/docs/architecture/observatory_contract.md:16).

Inspection used AST counts, collection, lexical searches, and representative real test bodies. Lexical counts identify candidates, not proof that a test is bad. No full suite, provider/model call, network request, or native environment action was performed by this sub-audit. The main audit separately timed the full deterministic suite and validated the delivered artifacts in an isolated clone; see the execution record above.

### Inventory and measured cost

| Measure | Frozen snapshot |
| --- | ---: |
| Test Python files | 34 |
| Test functions | 342 |
| Functions with parameterization | 47 |
| Collected cases with isolated Git metadata | 549 |
| Additional cases from parameterization | 207 |
| Test-file lines, including fixtures and setup | 10,257 |
| Portable core Python files / lines | 31 / 12,168 |
| All source Python files / lines | 39 / 13,433 |
| Cross-test-module imports / importing files | 22 / 9 |

Test source is approximately 76% of all source lines, or 84% of portable-core lines. This is a maintenance signal, not evidence of waste. `test_two_stage_admission.py` alone has 2,046 lines and 48 functions; much of its size is reusable public-contract setup.

The original snapshot lacks `.git`. Collection there produced 546 cases and one import error because [precommit cache import](/tmp/uah-agentlint-measure-epv03i/scripts/precommit_cache.py:27) eagerly resolves the Git directory. Ignoring that file collected 546 cases in 0.21 seconds. Collection in the isolated validation clone succeeded with 549 cases in 0.22 seconds, adding exactly three cache tests. This is collection time, not suite time. No authoring-token, repair-token, review-token, or test-maintenance cost was measured, so token savings cannot be quantified here.

The 52 research-dashboard cases are public-command subprocess tests, not 52 mocked helper tests. The wheel test invokes an actual isolated package build with `--no-deps --no-build-isolation`. The main audit measured their durations above. Public subprocess and package-build coverage has distinct value; its execution cost does not establish test-authoring waste. See [dashboard command seam](/tmp/uah-agentlint-measure-epv03i/tests/test_research_dashboard.py:49) and [wheel build](/tmp/uah-agentlint-measure-epv03i/tests/test_package_boundaries.py:41).

### Existing behavior coverage worth keeping

- Full accepted authority chain persists, reloads, derives a verified digest, and rejects post-terminal resume: [test_two_stage_admission.py:1388](/tmp/uah-agentlint-measure-epv03i/tests/test_two_stage_admission.py:1388). Required-effect failure and accepted best-effort deficit have separate restart cases at [1465](/tmp/uah-agentlint-measure-epv03i/tests/test_two_stage_admission.py:1465) and [1524](/tmp/uah-agentlint-measure-epv03i/tests/test_two_stage_admission.py:1524). These are multi-component integration tests, even though no live robot participates.
- A restarted/stale owner cannot consume a lease twice: [test_two_stage_admission.py:1155](/tmp/uah-agentlint-measure-epv03i/tests/test_two_stage_admission.py:1155). The one native call assertion is contractual exactly-once protection, not incidental collaborator choreography.
- Model invocation uses real actor/lease/prompt/ledger machinery with an injected provider boundary. Completed invocation replay avoids a second call at [test_model_invocation.py:422](/tmp/uah-agentlint-measure-epv03i/tests/test_model_invocation.py:422); interrupted invocation replay forbids automatic retry at [561](/tmp/uah-agentlint-measure-epv03i/tests/test_model_invocation.py:561). Atomic budget/start observations in the fake provider are part of the declared resource and persistence contract.
- Recorded NAO input passes actual normalization, semantic admission, domain leasing, fake-owner execution, and evidence closure at [test_recorded_nao_qualification.py:124](/tmp/uah-agentlint-measure-epv03i/tests/test_recorded_nao_qualification.py:124). Rejected proposals assert no dispatch and preserve nonterminal failure attribution at [163](/tmp/uah-agentlint-measure-epv03i/tests/test_recorded_nao_qualification.py:163). These qualify harness mechanics, not H2 planner parity or model capability.
- Competing task-start requests synchronize two independent authorities and ledger instances using a barrier and two threads at [test_environment_ingress.py:360](/tmp/uah-agentlint-measure-epv03i/tests/test_environment_ingress.py:360). This is actual thread contention. Sequential stale-writer/owner tests remain valuable, but neither is a subprocess crash or multi-process contention test; that distinction must survive reporting.
- Snapshot, historical-artifact, nested-method, and exported-event adversarial matrices exercise independent trust crossings. The 20 snapshot attack/crossing combinations at [test_admitted_object_snapshot.py:157](/tmp/uah-agentlint-measure-epv03i/tests/test_admitted_object_snapshot.py:157) and 18 serializer/verifier/crossing combinations at [test_nested_admission_owner.py:80](/tmp/uah-agentlint-measure-epv03i/tests/test_nested_admission_owner.py:80) cannot be replaced by one bad-input flow: an earlier rejecting gate would leave later public consumers untested.
- Public acceptance evaluation at [test_task_acceptance.py:27](/tmp/uah-agentlint-measure-epv03i/tests/test_task_acceptance.py:27) is a small deterministic contract test. Unit-sized does not mean implementation-coupled.

Direct private attribute access inside test bodies appears in one cache test by AST. `monkeypatch` appears in three cache tests and one renderer test. Many other tests intentionally mutate public artifact fields or methods to attack the trust boundary, or inject provider/native-handler doubles. Those are not ordinary mocks of internal collaborators.

### Scoped consolidation and rewrite candidates

| Candidate and exact pin | Recommended treatment | Failure behavior that must survive |
| --- | --- | --- |
| [Cache tests:6](/tmp/uah-agentlint-measure-epv03i/tests/test_precommit_cache.py:6), [17](/tmp/uah-agentlint-measure-epv03i/tests/test_precommit_cache.py:17), [28](/tmp/uah-agentlint-measure-epv03i/tests/test_precommit_cache.py:28) patch `_git` / `_repo_signature`, and the third invokes the private helper | Rewrite in a later authorized slice through `record/check` or CLI against a disposable Git fixture. Keep existing tests until the replacement detects the old defect and uses no shared Git state. | Valid cache acceptance; tracked/untracked content invalidation; staging/listing-order invariance. Add no broader cache guarantees without a contract. |
| [Renderer drift test:59](/tmp/uah-agentlint-measure-epv03i/tests/test_markdown_renderer.py:59) patches owned `rendered_html` | Prefer a tiny real Markdown source and generated companion under a temp root, invoking public `--check`; configuration/root injection can remain filesystem-boundary setup. | Check fails on drift, reports the path, and does not rewrite the stale file. |
| 22 imports from other test modules across 9 files, including [ledger setup:23](/tmp/uah-agentlint-measure-epv03i/tests/test_lifecycle_ledger.py:23), [snapshot setup:17](/tmp/uah-agentlint-measure-epv03i/tests/test_admitted_object_snapshot.py:17), and [synthetic note setup:6](/tmp/uah-agentlint-measure-epv03i/tests/test_synthetic_notes_owner.py:6) | Consolidate shared public-contract builders in a small neutral test-support module only after seams are agreed. This is fixture coupling, not product-private API coupling. Do not add a test framework or hidden bypass fixture. | Authentic ingress/start provenance, explicit owner/revision identity, real ledger writes, valid controls, and isolated mutations. |
| Exact API parameter spelling in [test_two_stage_admission.py:1216](/tmp/uah-agentlint-measure-epv03i/tests/test_two_stage_admission.py:1216) | The no-direct-dispatch negative call is contractual. Exact `inspect.signature` equality is narrower than behavior; candidate for removing only that assertion if public negative/positive calls cover the same contract. | Object/arguments cannot bypass the exact recorded lease; lease-only valid dispatch still works. |
| Freshness equality in [test_observatory.py:487](/tmp/uah-agentlint-measure-epv03i/tests/test_observatory.py:487) and [runtime example:36](/tmp/uah-agentlint-measure-epv03i/tests/test_agent_runtime_example.py:36) | Keep as synchronization checks; group under documentation/artifact tests for navigation. Do not count them as independent correctness oracles. | Committed output matches canonical generation and retains explicit recorded/synthetic qualification labels. |

No whole-test deletion is justified by the inspected evidence. A single-value parameter decorator at [test_model_invocation.py:102](/tmp/uah-agentlint-measure-epv03i/tests/test_model_invocation.py:102) can be simplified without reducing coverage, but this is low priority compared with contract-level consolidation.

### Oracle assessment

No unambiguous tautological assertion was established in the sampled bodies. There are narrower guarantees that can be mistaken for correctness:

- Compiling before and after restart and comparing equality at [test_task_compiler.py:381](/tmp/uah-agentlint-measure-epv03i/tests/test_task_compiler.py:381) proves replay stability, not that the projection is semantically right. It is legitimate metamorphic coverage. Keep the independently specified object/obligation expectations at [186](/tmp/uah-agentlint-measure-epv03i/tests/test_task_compiler.py:186).
- Round-trip identities and generated HTML equality can preserve a defect across both sides. Literal compatibility digests at [test_content_identity_compatibility.py:8](/tmp/uah-agentlint-measure-epv03i/tests/test_content_identity_compatibility.py:8) are independent regression expectations. Their scope is byte compatibility, not authority truth.
- Manually rehashing altered event/proposal bytes, for example [test_lifecycle_ledger.py:256](/tmp/uah-agentlint-measure-epv03i/tests/test_lifecycle_ledger.py:256), constructs a self-consistent hostile input so validation cannot stop at a stale outer hash. This is attack construction, not a duplicate implementation oracle.
- The note-owner literal `expected_text` is an independent oracle only when obtained from the reviewed task contract before provider/native action. Positive tests alone could echo the same wrong value. Existing wrong-content alternatives at [test_synthetic_notes_owner.py:40](/tmp/uah-agentlint-measure-epv03i/tests/test_synthetic_notes_owner.py:40) distinguish occurrence from exact content. Nevertheless, the development log records second-owner/hardlink and retained-task gaps; local owner tests do not establish full-chain effect closure. Do not promote R5 on their basis.

### Proposed small contract scenario inventory

Agree these seams with the user before writing or relocating tests. Start by selecting existing cases, not generating a parallel suite. Nine families should produce approximately 15 to 25 named scenarios, with a count determined by distinct failure behavior rather than a numerical quota:

1. Accepted ingress to exact owner evidence to accepted restart digest, with post-terminal resume rejected.
2. Required failure and best-effort deficit retain different terminal decisions after restart.
3. Semantic and domain rejection stop before native work and remain nonterminal unless a task acceptance fact says otherwise.
4. Duplicate task starts, cross-environment lineage, and concurrent cooperating writers do not create additional authority.
5. Exact lease fencing, one consumption across restart/stale owners, and start recorded before native work.
6. One representative attack per independent public authority crossing in the local selector; retain the complete hostile-representation matrices in full regression.
7. Prompt/admission eligibility agrees for allowed and prohibited observables.
8. Fake-provider success, settled replay, outstanding-call restart, and exhausted/expired resource rejection remain distinct from execution/effect truth.
9. O1 accepts valid ledger projections, rejects stale raw identity, preserves explicit actor/environment lineage, and never labels operation rejection as terminal task rejection.

This is a deterministic public-contract integration selector, not a substitute for release evidence. H2 still needs owner-reviewed NAO golden fixtures and `legacy/shadow/uah` parity. A real two-process race/crash probe and exact note full-chain test are future discriminating probes, not implied by existing test names or by this audit.

### Execution and review tiers

Local red/green iteration can run the selected public seam plus the relevant adversarial matrix. The declared changed-seam selector is an iteration convenience, never full-regression qualification. Use static test names and requirement IDs rather than a second generated test taxonomy.

Before commit or release, retain the current all-files hooks and full regression. [.pre-commit-config.yaml:27](/tmp/uah-agentlint-measure-epv03i/.pre-commit-config.yaml:27) runs pytest without filenames; [run_precommit.sh:12](/tmp/uah-agentlint-measure-epv03i/scripts/run_precommit.sh:12) runs all hooks before recording a fresh repository signature. Do not narrow or bypass these gates without an explicit human-approved policy change.

CI should run the full deterministic suite, packaging, artifact freshness, and architecture checks. This audit does not assert a new CI system exists or authorize adding one. Independent high-risk review must follow the existing `REVIEW.md`, including different-model second review where required, fresh input selection, and base comparison. Suite green is insufficient; the development log records defects found independently after large green runs.

For a later consolidation, establish a frozen baseline, name each preserved failure mode, demonstrate the replacement fails on the old defect or a controlled relevant mutation, passes on the corrected behavior, and preserves valid/restart controls. Remove a predecessor only when the coverage mapping is approved. Measure test durations and authoring/review tokens separately before claiming savings.

### Residual limits

Body inspection was representative, not an exhaustive semantic classification of every assertion. AST signals cannot establish absence of all internal coupling. No suite runtime, coverage/mutation score, token usage, or live capability result was measured by this sub-audit. No tests, release claims, hooks, or review rules should change solely on the basis of the count. The next decision is the human-approved public seam inventory and replacement-evidence policy.

## no-mistakes primary-source audit for UAH

Date: 2026-10-08. Scope: source-only inspection at `420adfd317e29e31bf6b5cd5d770529580084610` (release 1.91.0). The source was fetched into `/tmp/no-mistakes-primary-audit-420adfd`. No upstream installer, build, tests, daemon, provider, model, or pipeline was executed. The upstream sub-audit itself edited no shared repository file; the main audit subsequently installed the pinned unchanged skill and published this combined research handoff.

### Decision

Use its testing-quality guidance as an advisory checklist. Do not adopt the default runtime as UAH's validation or publication authority. It is a Go Git-proxy and agent-driven publication pipeline, not a static skill-only linter and not a replacement for tests. A pinned project-local skill can be installed as a reference/manual invocation, provided a higher-priority UAH boundary explicitly denies initialization, automatic repair, hook bypass, provider execution, or publication absent separate user authorization. Skill installation must not be represented as installing or enabling the binary or pipeline. [README](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/README.md#L39-L83), [skill](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/skills/no-mistakes/SKILL.md#L1-L64).

The exact upstream skill is `skills/no-mistakes/SKILL.md`, 436 lines, SHA-256 `313374bcd2ba43da08f0ac7e179244f2804a9088b8cf44549f862e6bc9a122c5`. It is generated from the upstream `internal/skill` source; upstream `make skill-check` checks drift. [Makefile](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/Makefile#L93-L103).

### What it does to testing

It invokes more checks and reviews; it does not replace them. The Test step runs an optional configured `commands.test` baseline, then invokes a model-driven evidence agent whether that baseline passes, fails, or is absent. The agent derives named end-user scenarios and attempts to exercise the real running product, using disposable fixtures or local instances. It can write tests and repair tests or code. Failures can enter automatic repair followed by another baseline/evidence pass. [Test implementation](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/internal/pipeline/steps/test.go#L52-L100), [baseline implementation](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/internal/pipeline/steps/test.go#L136-L178), [evidence prompt](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/internal/pipeline/steps/test.go#L228-L280).

Its product boundary is targeted local checks plus broad remote CI, not full local regression. Both the initial evidence prompt and repair prompt forbid running the complete repository suite. The repair prompt additionally says a generic driver or user request for broad/full-suite confirmation does not override this boundary. That upstream product rule must not supersede UAH's user instructions or mandatory `./scripts/run_precommit.sh`. Running the UAH hook suite independently remains required; no-mistakes' targeted result is additional evidence only. [Source restriction](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/internal/pipeline/steps/test.go#L78-L92), [reference](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/reference/pipeline-steps.md#L159-L189).

Useful test-quality rules are explicit and nuanced:

- Prefer executable public interfaces and observable behavior over implementation-source substring, AST-shape, or incidental-snapshot assertions.
- Require an independent oracle from a specification, external contract, worked example, or justified property. Name a plausible wrong behavior the test rejects.
- Regressions should fail before the fix and pass afterward when feasible.
- Owned text/byte contracts, serialized state, generated public output, and intentional emitted-prompt interfaces remain legitimate test subjects. A prompt containing a sentence does not establish model obedience.
- Review cleanup is limited to same-pattern tests encountered in the accepted change, not an automatic repository-wide deletion campaign.

These are prompt instructions, not proof that the model follows them. Their narrow owned-contract exception matters for UAH's source-aware and generated-document tests: classify each test's actual claim before removing it. [Shared guidance implementation](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/internal/testguidance/guidance.go#L1-L55).

Live scenario evidence is model-reported with a validated schema. A scenario marked untested does not independently park the gate; the overall verdict controls whether insufficient evidence is blocking. Structurally valid evidence and a model's `go` verdict are not independently verified correctness. The docs explicitly call Review probabilistic evidence and deny security/compliance certification or replacement of deterministic authorization/privacy tests. [Review and Test reference](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/reference/pipeline-steps.md#L92-L189).

For UAH, the useful advisory audit questions are: which public operation or lifecycle transition is exercised; which authority owns the expected result; what unauthorized operation, fabricated effect, stale frame, missing context, or rollback failure is rejected; and whether the assertion merely restates a fixture or implementation rule. Preserve deterministic owner/admission/replay tests and existing documentation synchronization checks. This paragraph is an application recommendation, not an upstream implementation claim.

### Authority and security findings

1. **Skill invocation is expansive.** Its description triggers on generic validation/shipping requests. Task-first mode commits on a feature branch, then drives `intent → rebase → review → test → document → lint → push → pr → ci`. It tells the driver to run `init` when absent and act on remediation hints. Installing or inspecting this skill does not authorize these later mutations. [Skill preconditions and task mode](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/skills/no-mistakes/SKILL.md#L1-L133).
2. **Runtime setup changes persistent local state.** `init` adds the local gate remote, installs bare-repository hooks, creates state, refreshes user-level skills in `~/.claude/skills` and `~/.agents/skills`, and starts the daemon. It leaves `origin` intact; this is an explicit alternate remote, not interception of every ordinary push. The stock installer restarts a background service, and release/source builds embed telemetry defaults. Most CLI invocations perform background update checks unless disabled. [Gate model](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/concepts/gate-model.md#L32-L80), [installation](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/start-here/installation.md#L6-L157).
3. **Disposable worktrees are not security sandboxes.** Codex defaults to `--dangerously-bypass-approvals-and-sandbox`; Claude defaults to `--dangerously-skip-permissions` unless machine-local overrides select another mode. ACP uses approve-all. Worktree containment is prompt steering; normal HOME credentials/settings are available. `protected_paths` is only a staging guard and does not inspect already committed changes. [Codex source](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/internal/agent/codex.go#L178-L209), [Claude source](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/internal/agent/claude.go#L170-L205), [agent reference](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/guides/agents.md#L266-L348), [protected paths](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/reference/repo-config.md#L593-L618).
4. **Repair is enabled beyond Review.** Default follow-up limits are rebase/test/lint/CI 3, Review 0. Document attempts modifications on its initial pass, and an unconfigured lint command is folded into that housekeeping pass. Setting all `auto_fix` entries to zero is therefore not read-only. Ordinary ask-user findings are escalated, but explicit unattended `--yes` treats them as consent to fix. Test approval may override failures without a mandatory operator reason, with the exception recorded rather than a clean pass; required attestation enforcement is separate. [Default config](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/reference/global-config.md#L858-L879), [skill consent and overrides](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/skills/no-mistakes/SKILL.md#L239-L374).
5. **Generated correction commits bypass local hooks.** The shared correction commit helper creates an empty temporary `core.hooksPath` and uses `--no-verify`; it suppresses the full commit-hook family for that invocation. This does not establish UAH's required hook suite ran. [Commit implementation](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/internal/pipeline/steps/common_fix.go#L295-L350).
6. **Publication occurs automatically after gates.** Push has no separate approval gate. Existing-branch rewrites use an explicit-SHA force-with-lease, live remote checks, patch preservation, review-approved-head continuity, and post-push verification. These are valuable data-loss guards, not human authorization for the initial push or substantive correctness of later commits. CI's default `revalidate_repairs: false` permits publishing descendant repairs without another complete Review/Test/Document/Lint pass; merge-conflict/non-descendant repairs return through Review. [Publication implementation](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/internal/pipeline/steps/push.go#L92-L206), [CI default](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/internal/config/config.go#L88-L102).

There are useful runtime protections: nested validation agents cannot launch/control another gate, trusted default-branch configuration owns executable commands and agent selection unless explicitly opted in, missing analyzer output fails closed, and review coverage must name the trusted changed-file set. None elevates model findings into UAH authorization or environment-owner evidence. [Pipeline and configuration references](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/reference/pipeline-steps.md#L12-L33), [trusted configuration](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/reference/repo-config.md#L152-L185).

### Reviewer independence, boundedness, and cost

Full reviews/rereviews use fresh, session-free invocations; fixes may reuse a fixer session. Optional global-only `review_agents` selects separate reviewer/fixer harnesses or models. By default omitted roles inherit the same ordinary agent chain; a cold session does not guarantee model/provider diversity or statistically independent errors. Coverage is a self-reported record validated against known paths, not a proof those paths were correctly understood. [Review reference](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/reference/pipeline-steps.md#L98-L149), [role configuration](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/reference/global-config.md#L349-L420).

Default per-invocation Review/Test/other-agent timeout is 30 minutes, with optional still-working extensions. Automatic fix limits bound particular loops, but the Review reference explicitly imposes no limit on review fix rounds. Each fixer and independent rereviewer gets a fresh timeout. CI monitoring defaults to a seven-day idle timeout rearmed by base-branch movement. No aggregate monetary/token/entire-run hard cap was found in the inspected configuration; token stats are measurement, not authorization to spend. A safe trial would need its own total rounds, wall time, provider quota, and cost cap. [Budget source](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/internal/config/config.go#L28-L75), [Review rounds](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/reference/pipeline-steps.md#L131-L149).

### Dependencies, license, and evaluation limits

MIT license, copyright 2026 Kun Chen; preserve its notice with copied substantial skill material. The source module requires Go 1.25.0. Runtime needs Git and an installed/authenticated supported native agent or ACP runner; the current AXI driver is not automatically that runner. PR/CI additionally depend on the forge CLI/plugin and its existing credentials. `agent: auto` picks the first available runner, so source-only installation does not establish a model, provider, credential, or cost profile. [License](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/LICENSE), [module](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/go.mod#L1-L19), [runner requirements](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/guides/agents.md#L39-L71), [forge prerequisites](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/start-here/installation.md#L93-L112).

The evaluation toolkit replays Review only, excluding Test, fix loops, publication, and CI. Its local-only label refers to corpus storage and added transport, not provider traffic: replay uses normal signed-in agent settings and can read/write ordinary HOME files. Gold labels are operational proxies (human Fix, shipped-unfixed, merged auto-fix, curated/CI misses), not comprehensive independent defect truth. Unmatched findings remain pending; reports correctly withhold F1 without false-positive gold. [Eval reference](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/docs/src/content/docs/reference/eval.md#L5-L175).

The inspected current schema benchmark reports 30/30 schema-valid Review runs per arm across three historical workloads, with no demonstrated reliability improvement and explicitly no finding-accuracy/recall evaluation. Its smaller pilot is likewise schema-only. Historical Jev experiments are retired and explicitly deny established token savings; they must not be cited as current functionality or UAH benefit. No inspected benchmark establishes fewer UAH regressions, test replacement, security certification, or net development cost savings. [Current schema benchmark](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/benchmarks/issue-1284/results.md#L12-L74), [retired experiment](https://github.com/kunchenguid/no-mistakes/blob/420adfd317e29e31bf6b5cd5d770529580084610/benchmarks/issue-1125/results.md#L1-L12).

### Safe local-only subset

Immediate safe subset: pinned text extraction, source inspection, and advisory UAH test-oracle/scenario review with no upstream runtime. Keep UAH's deterministic validation and architecture authority unchanged. Record model review findings as proposals requiring independently reproduced behavior before fixes.

There is no demonstrated read-only mode for the full pipeline: skipping publication still leaves rebase, test generation, document edits, repairs, provider traffic, and configuration/daemon state in scope. A future experiment should use a disposable non-production clone, isolated HOME/credentials, explicit agent/model and sandbox posture, no writable real remote/forge credentials, disabled telemetry/update checks, separate cost/round caps, and UAH-owned deterministic acceptance checks. It requires separate user authorization and must not be enabled merely by installing the skill.

## Reproducibility manifest

SHA-256 hashes below are relative to the frozen audit snapshot's root. They pin inspected tests, not a release or selected commit.

```text
ad585953067804b3f30b184c57520d7646428fc84fca17797cdd4afdb716540e  tests/test_admission_active_provenance.py
cbff9c50f69659f2497b9b1a63f7d6088166589f726ff8be4bfeb466da696b5b  tests/test_admitted_object_snapshot.py
3308e7e626c69283d0f68150b0b2246a6fc1df0b14cd47e88e0577f77b5d3824  tests/test_agent_configuration.py
a61667255c037e04b93d38e46f47e9c9b807778962dad141f8147e3468b8ebb7  tests/test_agent_identity.py
63ed2ce4d4244abed4f88b7f7843329998f5b561c1db2196f8701264d736b757  tests/test_agent_runtime.py
973e39f172588f0ef79ee58a880c42cd6bf610ce5a4cefaa90538801f8740fcb  tests/test_agent_runtime_example.py
cb182dab1fa9e7fca371fc1e36a972a974e53c29cb844b10a82a5f40cf0e4bb6  tests/test_argument_schema_validation.py
f4e2d87f92c1356d5ce746b12cd1f816667118a6eb7ab4d3d27474425244087e  tests/test_cli_smoke.py
1f61ffdefdec42ff6546744f3324b87613d929621d85a7f3412e76ecbea5fbdf  tests/test_configuration_identity.py
eb2a6ced57624d500943e9bbf781db6f08098fe7ce2bd1d61e438aa59a40a3ab  tests/test_content_identity_compatibility.py
b68ee492878bff41ec97a80a8de69c4feb67ea332ed8e4ed8a159279bf0c8f44  tests/test_core_contracts.py
33c152c1a914a7b6e07bf681ad75007d7bbd71025da2a21c374968520f931fd9  tests/test_environment_ingress.py
65eb3cc1e8d98d59916eacc38fb541dc6d5d5024c50d6e295fed16489b0ee764  tests/test_environment_runs.py
d115c4b9c265ed3439e01e33dee69e979150c0bb71bc86c2c4f5f210b6ceccd5  tests/test_h0_nao_harness.py
3db785f7efce387202a83b8aa05280d8e3085cbc5346e536587743be771466f8  tests/test_implementation_bindings.py
96818685de39c6cf715516b77d3e3a7de27e71ce56d5d5d62f59bbd3f180e5ae  tests/test_lifecycle_ledger.py
356693df67ccaf7b97676bed83a6dfc9bbcce58cc4134d1e630b38fd642fc824  tests/test_markdown_renderer.py
554c5ff8177ea41d6ba9f3603740c90efd7ece273b25c15b5ec76692fb63da71  tests/test_model_invocation.py
4175dc62a23955924ff10dd6653d6a5f23cc8305f87579e058ae368363fcc8c0  tests/test_nested_admission_owner.py
87dcb0e7892e6a8affb4253bf9f69dcde7db105e16ca5bc8ccda4b454b4929ea  tests/test_observatory.py
b7088e4b167cc8f643827c9e4770054ce7699757bde65952ce2c4c2d8fc9772d  tests/test_observatory_format.py
62a67d8db16788542ef730b5f5f913e0602a2ce8a01060b90173bd0f96db01c5  tests/test_observatory_raw_identity.py
00d3396dd615911cb34b29b8754a9dd7ef58749b96a0fd66daee6cf2ed81b931  tests/test_package_boundaries.py
9bef810c4e3fd8bd0b5528f03d4f76712888b6cc97e8e2738d4cd863b070bcc1  tests/test_precommit_cache.py
c04db4be3abc125e43ace67d4416a412f18c2288da8a30362ae85c199c63774b  tests/test_prompt_compiler.py
3d20bafc274761b9fe7e976841218f07c625740961a1cb1c9ee880353f81a42e  tests/test_recorded_nao_qualification.py
0a086b3f98255dfe34eacf01ec1801b7427ff935961b3beb3d0c5a2a0f0d91ef  tests/test_research_dashboard.py
8f8cd3011e15aec9cd7e36d3373ac74f8fb5616f17655ab0a1cc6ac095e33098  tests/test_runtime_budget_contracts.py
2391e2273d9c97cf43871025fbcee4e0b1c2df35ec460e0453a005cbe6391e36  tests/test_synthetic_notes_owner.py
7da46209cd5e93f0db479aea127b7a09906a369dfe86f41bdbf58e2658af1c02  tests/test_task_acceptance.py
c343f064b69ea47809880c5d7ecab5415d5dbcd25df67d395ceea4381f0dabb5  tests/test_task_compiler.py
ded076b966093c009fc26989070d2dc9864f9f91a1df78a059e9644c4e73d0b2  tests/test_two_stage_admission.py
7dfd4b1319d648c86ae8c8506adec9e6ddbf2b7685441821670684c0d37f0146  tests/test_workbench_memory.py
74ab4dde576ba13a1f361807cab6d7738e360abe4bebbbfb51ecb7a8d3c709b4  tests/test_workbench_protocol.py
```

## Delivered-change validation

Only this dated handoff and the vendor skill/license are new deliverables from this pass. The full repository pre-commit suite passed in the isolated clone, including Ruff, source-aware pytest and generated-document synchronization. Explicit end-of-file and trailing-whitespace hooks passed for the three new files, including the otherwise untracked research artifact and vendor files. Vendor skill and license hashes remained identical to upstream. Shared `git diff --check` passed as a read-only diagnostic. No shared hook execution or Git/index modification was used. Passing snapshot checks does not close ARCH02, H0/H1 qualification, R5 promotion, independent review, or the pending selected-commit dependency gap.
