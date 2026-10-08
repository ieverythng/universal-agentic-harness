# UAH H0/H1 independent review

**Date:** 2026-10-05  
**Decision:** Changes required; no runtime repairs in this round  
**Scope:** [Pinned commits, dirty files, hashes and deletions](2026-10-05_uah_h0_h1_review_scope.md)  
**Contract:** [REVIEW.md](../../../REVIEW.md)  
**Reproductions:** [Executable probes and commands](2026-10-05_uah_review_repros/README.md)  
**Follow-up workflow:** [UAH review and trace iteration](../../agents/uah_review_workflow.md)

The review does not establish H0 closure. Executed counterexamples show authority
and evidence failures in the compiler, admission, ingress and in-memory ledger.
H1 has bounded registry, allocation, prompt and invocation implementations, but
their successful synthetic tests do not resolve those failures or qualify H2.
O1 renders useful environment/task/trace and actor views; its evidence labels
need correction before they can support an exit decision.

## Review method and evidence scope

Three fresh agents reviewed the last five commits plus the entire captured
tracked and untracked dirty scope. They did not inherit the writer's
conversation or change runtime code. Standards and Spec remain separate axes;
cross-references identify corroboration without merging their findings.

| Axis | Reviewer | Model and reasoning | Result |
|---|---|---|---|
| Standards | `review_standards_20261005` | `gpt-6.1-sol`, `max` | 3 BLOCKING, 1 NIT |
| Spec | `review_spec_20261005` | `gpt-6-astra`, `max` | 4 BLOCKING |
| Architecture/O1 | `review_architecture_20261005` | `gpt-6.1-sol`, `max` | 2 BLOCKING, 2 NIT |

The second model supplies independent coverage of high-risk authority gates.
No model fallback occurred. Before implementation reading, reviewers declared
probes for forged lineage, nested authority mutation, replay/restart, numeric
budget boundaries, admission and prompt scope, O1 provenance, HTML escaping,
hook evasion and package portability. The PromptCompiler observable-effect
counterexample was an explicitly identified source-directed follow-up.

The parent executed the saved counterexamples and reran the adapted repository
copies. The findings below are open at the captured hashes. The parent was a
previous writer, so these reruns corroborate the independent reviews rather
than replacing them.

## Standards

### Independent summary

1 of the 4 found so far. **BLOCKING, STD-01:** `TaskSpecCompiler` trusts the
domain revision without reverifying its covered content. A changed failure
policy produces obligations under the original revision.

2 of the 4 found so far. **BLOCKING, STD-02:** The pre-push success cache checks
working-tree bytes, allowing a broken outgoing commit to pass when valid
unstaged bytes match the cached state.

3 of the 4 found so far. **BLOCKING, STD-03:** In-memory ledger events escape
without revalidation. O1 displays altered events as recorded acceptance while
ledger replay rejects them.

4 of the 4 found so far. **NIT, STD-04:** Dated August checkpoints were rewritten
with the later NAO package path and lease/replay behavior.

Design principles: separation of concerns **OK**; programming by intention
**violation STD-02**; encapsulation **violations STD-01/03**; high cohesion
**OK**; low coupling **OK**. The reviewer found no justification for splitting
files by length or extracting artifact codecs solely because SHA syntax recurs.

### Findings and reproductions

#### STD-01: Domain revision does not constrain the consumed policy

- **Owner/release:** Task compilation, H0 authority gate. **Status:** OPEN.
- **Source:** `src/ab_harness/task_compiler.py:265-303`.
- **Rule:** UAH guardrails lines 65-66 require content and nested-content
  revalidation at authority trust crossings.
- **Input:** Replace an issued pack's effect rule with a retryable rule while
  retaining its original revision after admitted task start.
- **Expected:** Reject the stale pack before compiling obligations.
- **Actual:** Compilation succeeds with `compiled_policy=retryable` and
  `revision_unchanged=true`.
- **Probe:** `standards_domain_tamper.py`. SPEC-01 corroborates with nested
  mutation rather than replacement.
- **Base:** No equivalent compiler interface exists at `cf90a7e`.

#### STD-02: Untested outgoing content can pass the push cache

- **Owner/release:** Git pre-push cache, development gate. **Status:** OPEN.
- **Source:** `scripts/precommit_cache.py:75-84`.
- **Rule:** REVIEW.md section 6 requires gates to reject evasive inputs.
- **Input:** In an isolated Git repository, cache tested `RESULT = 42`, commit
  `RESULT = (` while restoring the valid bytes as an unstaged working-tree edit.
- **Expected:** Reject the outgoing committed tree that was not tested.
- **Actual:** Committed content raises `SyntaxError`; cache check exits `0`
  because the worktree matches its signature.
- **Probe:** `standards_push_cache.py "$PWD"`; all commits occur inside a
  temporary synthetic repository, never this repository.
- **Base:** Cache interface absent. This is not a demonstrated bypass of CI.

#### STD-03: O1 trusts a changed in-memory event

- **Owner/release:** Common ledger and O1 evidence projection, H0/O1.
  **Status:** OPEN.
- **Source:** `src/ab_harness/lifecycle.py:698-701`, `:787-789`;
  `src/ab_harness/observatory.py:231-233`.
- **Rules:** Guardrails lines 65-66 and REVIEW.md section 4, truthful labels.
- **Input:** Alter the event type of a returned resume event to
  `terminal_task_accepted` without updating its content ID.
- **Expected:** Reject invalid content before projecting recorded status.
- **Actual:** O1 displays `accepted/recorded`; replay raises the missing
  `effect_obligation_satisfied` prerequisite.
- **Probe:** `standards_event_tamper.py`. SPEC-04 demonstrates a budget
  consequence of the same in-memory exposure.
- **Scope:** Default in-memory ledger mode. File-backed refresh reloads and
  validates stored records. Base ledger/O1 interfaces absent.

#### STD-04: Historical records were retroactively migrated

- **Owner/release:** Dated development history, documentation. **Status:** OPEN.
- **Source:** `docs/plans/universal_agentic_harness_development_log.md:184-185`;
  `docs/plans/universal_agentic_harness_masterplan.md:312-314`.
- **Rule:** REVIEW.md section 7 preserves historical paths and facts.
- **Input:** Compare the August checkpoint against the pinned base and the
  later package extraction entry.
- **Expected:** Preserve the historical command, adding a dated migration note.
- **Actual:** August text now uses `python -m ab_harness_nao` and later
  lease/replay claims. The base checkpoint uses `python -m ab_harness smoke`;
  the separate adapter package is absent there.
- **Reproduction:** `git show cf90a7e:docs/plans/universal_agentic_harness_development_log.md`.

**Independent Standards verdict:**

```text
VERDICT: CHANGES
```

## Spec

### Independent summary

1 of the 4 found so far. **BLOCKING, SPEC-01:** DomainContractPack nested content
can change compiled failure semantics under its original revision.

2 of the 4 found so far. **BLOCKING, SPEC-02:** Caller-authored raw task-start
facts can establish fabricated lineage that authorizes compilation after restart.

3 of the 4 found so far. **BLOCKING, SPEC-03:** Admission does not bind the
catalog's semantic object to the compiled projection. A different registry can
add a prohibited effect and still produce accepted execution and task closure.

4 of the 4 found so far. **BLOCKING, SPEC-04:** In-memory event reduction does
not reverify content IDs. Changed event budgets become authoritative despite
an invalid hash.

Design principles: separation of concerns **violation SPEC-02**; programming
by intention **OK**; encapsulation **violations SPEC-01/04**; high cohesion
**OK**; low coupling **OK**. No confirmed scope creep. Deferred stale-evidence,
live-provider, context/failure coverage, O1 comparison and H2 parity requirements
remain qualification gaps rather than additional implemented defects.

### Findings and reproductions

All four probes run through `spec_probes.py`.

#### SPEC-01: Nested policy mutation survives compilation

- **Owner/release:** Domain pack verification and task compilation, H0.
  **Status:** OPEN.
- **Source:** `src/ab_harness/task_compiler.py:259-324`;
  `src/ab_harness/domain_contracts.py:288-302`.
- **Rule:** Guardrails lines 65-66, nested authority revalidation.
- **Input:** Change an issued rule's `failure_policy` from terminal to retryable
  with `object.__setattr__`, leaving the revision unchanged.
- **Expected:** Reject stale identity.
- **Actual:** `revision_preserved=true`, `issued_policy=terminal`,
  `compiled_policy=retryable`.
- **Probe:** `nested_domain_tamper`. Corroborates STD-01.
- **Base:** Equivalent interfaces absent.

#### SPEC-02: Public raw facts bypass task ingress ownership

- **Owner/release:** TaskIngressAuthority and common ledger, H0 ingress gate.
  **Status:** OPEN.
- **Source:** `src/ab_harness/lifecycle.py:992-1014`.
- **Rule:** CONTEXT.md lines 273-282 says the decision's fields alone do not
  authorize compilation and callers cannot register raw lineage as authority.
- **Input:** Construct `TaskStartedFact` for an unregistered environment,
  never-observed ingress and caller-authored task/trace; submit with
  `LifecycleLedger.record(...)`, reload the registry, then compile.
- **Expected:** Reject the start lacking admitted ingress provenance.
- **Actual:** `task_started` and `task_compiled` survive file-backed reload for
  `unregistered-environment` and `caller-authored-trace`.
- **Probe:** `caller_started_fact`. No private ledger write or hash forgery.
- **Base:** Equivalent ingress/common-ledger/compiler interfaces absent.

#### SPEC-03: The execution catalog can contradict the compiled semantics

- **Owner/release:** Semantic admission and binding/object identity, H0.
  **Status:** OPEN.
- **Source:** `src/ab_harness/proposal_admission.py:803-839`.
- **Rules:** ADR 0001 lines 22-37 preserves stable semantic objects separately
  from bindings; foundation lines 490-494 claims projected prohibited-effect
  checks before admission.
- **Input:** Create a different registry with the same object ID and owner,
  preserve the approved binding, and add prohibited `direct_speech` to the
  catalog object's expected and observable effects.
- **Expected:** Reject catalog semantic drift before dispatch.
- **Actual:** Admission succeeds, owner evidence includes `direct_speech`,
  and restarted terminal status is `accepted` despite the compiled prohibition.
- **Probe:** `semantic_catalog_drift`. Uses real public task-ingress admission
  for setup; no authority artifact mutation or private API bypass.
- **Base:** Equivalent two-stage/compiled-task interface absent.

#### SPEC-04: Invalid in-memory events change enforced budgets

- **Owner/release:** Common ledger replay and runtime budget accounting,
  H0/H1. **Status:** OPEN.
- **Source:** `src/ab_harness/lifecycle.py:698-701`, `:787-789`, `:1514-1530`.
- **Rule:** Guardrails lines 65-68, revalidated authority and immutable lineage.
- **Input:** Change a returned task-compiled event's model-call limit from
  `3` to `1000`, preserving its stale ID; request four model-call units.
- **Expected:** Reject the invalid event before budget consumption.
- **Actual:** Four units are granted. `TraceEvent.from_dict(event.to_dict())`
  rejects the very same event's content identity.
- **Probe:** `exposed_event_tamper`; fixture bookkeeping retrieves the original
  ledger, while the altered event comes from the public `events()` interface.
- **Scope:** In-memory mode. File-backed reload validates stored records.
  Corroborates STD-03 with a distinct consequence. Base interfaces absent.

**Independent Spec verdict:**

```text
VERDICT: CHANGES
```

## Architecture and O1

### Independent summary

1 of the 4 found so far. **BLOCKING, ARCH-01:** Static callable eligibility
differs between PromptCompiler and semantic admission, producing an offered
operation that the kernel deterministically rejects.

2 of the 4 found so far. **BLOCKING, ARCH-02:** O1 accepts measured/reviewed
labels for raw events without evaluation, frozen-configuration or review evidence.

3 of the 4 found so far. **NIT, ARCH-03:** The generated-doc hook skips HTML-only
changes. All-files checks and CI retain protection.

4 of the 4 found so far. **NIT, ARCH-04:** README's current-status text denies
runtime budget consumption, contrary to implemented tool/model accounting.

Design principles: separation of concerns and programming by intention
**violations ARCH-01**; encapsulation **OK for the inspected paths**; high
cohesion **OK**; low coupling **OK**. This axis did not inspect or negate the
in-memory mutation defects found on the other axes. Governance supplement:
no confirmed defect in the copied contract, captured scope or proposed local
workflow.

### Findings and reproductions

#### ARCH-01: The advertised prompt contract includes a forbidden operation

- **Owner/release:** Static semantic eligibility consumed by prompts, H1.
  **Status:** OPEN.
- **Source:** `src/ab_harness/prompt_compiler.py:361-364` versus
  `src/ab_harness/proposal_admission.py:812-816`.
- **Rule:** REVIEW.md section 5 disallows duplicated policy; the agreed bounded
  prompt projection must respect semantic admission.
- **Input:** Valid compiled `write_note` object: expected effect `note_written`,
  observable effects `note_written` and `prohibited_observable`; the task
  prohibits `prohibited_observable`.
- **Expected:** Do not offer the statically forbidden operation to the model.
- **Actual:** Compiled identity verifies; prompt schema offers `write_note`;
  schema-valid normalization succeeds; admission rejects
  `object_effect_prohibited`.
- **Probe:** `prompt_scope_probe.py`, a source-directed follow-up.
- **Base:** Prompt compiler absent.

#### ARCH-02: Evidence labels can be escalated by caller metadata

- **Owner/release:** Observatory evidence provenance, O1. **Status:** OPEN.
- **Source:** `src/ab_harness/observatory.py:231-238`, propagation at `:325`,
  `:362`, `:485`.
- **Rules:** Observatory contract lines 383-384 defines measured as an evaluator
  result under frozen configuration and reviewed as gate-accepted measurement;
  REVIEW.md section 4 requires truthful labels.
- **Input:** A content-valid fabricated terminal event without task start,
  obligations, evaluator configuration or review decision; request measured
  and reviewed labels on the iterable.
- **Expected:** Reject unsupported provenance or retain an explicit synthetic label.
- **Actual:** Projection and graph say measured/reviewed and accepted. Loading
  the same event as a ledger rejects missing `task_started`.
- **Probe:** `observatory_probes.py`, terminal hash round-trip and label cases.
- **Scope:** This finding is provenance escalation. Permitting incomplete
  explicitly synthetic illustrations alone is not classified as a runtime
  authority failure. O1 interface absent at base.

#### ARCH-03: Generated HTML is outside the hook trigger

- **Owner/release:** Generated-doc pre-commit trigger, development tooling.
  **Status:** OPEN.
- **Source:** `.pre-commit-config.yaml:39`.
- **Rule:** AGENTS.md requires synchronized generated HTML/Markdown.
- **Input:** Select `docs/architecture/observatory_contract.html` alone for
  the synchronization hook; the independent reviewer also changed its HTML
  in a temporary repository copy.
- **Expected:** Execute the freshness check for the generated path.
- **Actual:** `pre_commit run generated-docs --files ...html` exits successfully
  with `Skipped`; direct renderer `--check` rejects the modified copy.
- **Reproduction:** `.venv/bin/python -m pre_commit run generated-docs --files docs/architecture/observatory_contract.html`.
- **Scope:** Manual all-files check and CI still protect synchronization. Hook
  absent at base. No claim that CI approves stale HTML.

#### ARCH-04: Current README does not match implemented budget accounting

- **Owner/release:** Current-status documentation, H0/H1. **Status:** OPEN.
- **Source:** `README.md:40-41`.
- **Input:** Compare its unenforced-budget claim with runtime budget tests and
  recorded canary tool-budget grant events.
- **Expected:** Distinguish implemented tool/model accounting from deferred
  token/cost accounting.
- **Actual:** README says consumption is not enforced while those grants and
  enforcement tests execute.
- **Reproduction:** `.venv/bin/python -m pytest -q tests/test_runtime_budget_contracts.py tests/test_two_stage_admission.py tests/test_model_invocation.py`.
- **Base:** No runtime-budget accounting seam; its historical claim was not
  tested as a current implementation claim.

**Independent Architecture/O1 verdict:**

```text
VERDICT: CHANGES
```

## Executed validation and limits

| Executor | Executed evidence |
|---|---|
| Parent | Base full suite 50 passed; current full suite 344 passed |
| Standards | 125 focused plus 93 admission/runtime/invocation/schema tests passed; Ruff, config validation, diff and three render checks passed |
| Spec | 179 primary plus 111 additional focused tests passed; numeric budget alternatives exercised; 16 base contract/NAO tests passed |
| Architecture/O1 | 34 O1/package/cache/Markdown plus 60 prompt/compiler/runtime-budget tests passed; 3 base renderer tests passed; base/current offline wheel builds passed |
| Parent final checks | Full pre-commit passed; Ruff on source, tests, scripts and saved probes passed; canonical docs and both O1 examples fresh; diff check passed; copied REVIEW matches iTrader |

Reviewer suites overlap. Do not add their counts or treat the base/current count
difference as parity. The new compiler, ledger, O1, prompt and cache interfaces
do not exist at the base. Missing top-level packages were checked with
`python -S` and base-only `PYTHONPATH` to prevent editable-install fallback.
The parent compared all 107 captured file hashes and found no content changes.
HEAD and branch remain unchanged, with no staged changes.

Additional passing observations: actor-only environment views do not fabricate
tasks; HTML title escaping works; core portability tests pass; the current wheel
contains the separate NAO adapter rather than removed core adapter modules.
Those observations do not invalidate the counterexamples.

Not scored: live providers, native NAO/container parity, model quality,
hardware behavior under real load, Windows locking, full timestamp permutations,
hook-install migration, and visual layout of binary design reports. O1 source,
labels and generated examples were checked, but this round does not claim
browser pixel-level visual QA. No complete cross-domain conformance claim is made.
The computer-use browser rejected the local `file:` report URL under its
protocol policy. No alternate browser surface or localhost workaround was
attempted. The optional before/after report is available for manual inspection
at `/tmp/architecture-review-20261005-120335.html`.

## Optional architecture exploration

These candidates are not fixes or approved interface designs. The seven
distinct blocking counterexamples reported across the three axes need owning
corrections and fresh focused reviews before release claims advance.

### Semantic-owned static operation eligibility (Strong)

Files: `prompt_compiler.py`, `proposal_admission.py`.

```text
Before: CompiledTask -> prompt eligibility -> offered operation
                    -> admission eligibility -> rejection
After:  CompiledTask -> one semantic-owned static eligibility module
                       -> prompt presentation
                       -> semantic admission, with trust-crossing rechecks
```

ARCH-01 demonstrates caller friction and duplicated policy. Locality places
static effect/scope policy under one owner; leverage keeps prompt and admission
tests consistent. The deletion test is meaningful only if removing the module
redistributes policy, rather than deleting a pass-through. Domain lifecycle
admission and live evidence checks retain separate ownership.

### Invocation lifecycle-family locality (Worth exploring)

Files: `model_invocation.py`, `agent_lifecycle.py`, `lifecycle.py`.

```text
Before: Invocation fact -> conversion -> actor reduction -> task checks
                         grammar distributed across three modules
After:  Invocation lifecycle family -> local conversion and replay rules
                                      inside LifecycleLedger ownership
```

Related grammar spans `invocation_spec`, `apply_invocation_event`, atomic budget
checks and `_validate_model_task_event`. A cohesive internal family may improve
locality while public ledger tests remain the test surface. No second writer,
generic dispatcher or event-codec framework is proposed. File length alone
does not pass the deletion test.

## iTrader iteration loop adaptation

The iTrader loop makes independent review mandatory after evidence-browser and
decision-gate changes. The bounded UAH mapping is documented in the linked
workflow: freeze failure/control and loadout, public-seam red test, authorized
owner correction, focused retest, wider checks plus trace/digest comparison,
then fresh independent fix review. Implementation approval and domain/provider
qualification remain separate decisions.

No reusable UAH iteration skill was installed in this round. The workflow is a
reviewable proposal, not a measured SkillOpt improvement. An actual skill should
be finalized with locked training/holdout cases and bounded mutation evidence.
Spawning reviewers through UAH requires a reviewed read-only role and tool
projection; the existing provider port does not implement that worker capability.

Each review-rule or workflow change requires independent review. Closing a
finding requires an authorized TDD correction, a protected valid control,
updated implementation evidence and a fresh reviewer. No runtime fix, staging,
commit or push occurred in this round.

VERDICT: CHANGES
