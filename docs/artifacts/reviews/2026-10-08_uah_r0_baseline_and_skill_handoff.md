# UAH R0 baseline and iteration-skill handoff

**Date:** 2026-10-08 (Europe/Madrid)  
**Round:** R0, bounded to a target of 20 minutes; no automatic continuation  
**Runtime decision:** No repairs authorized in this round; original blockers remain open  
**Skill decision:** ACCEPT instruction fit; two independent APPROVE verdicts, one optional NIT retained  
**Round stopped:** 2026-10-08 at 16:02 Europe/Madrid; subsequent repairs require a separate freeze  
**Branch:** `feat/pre-commit-queue`  
**HEAD:** `28fab5e7f2c244d86a64c371f2118017999b2387`  
**Original review base:** `cf90a7e328eb4c80f7fe1418fccb1e60f25a0b77`

## Target contract

R0-A reruns the [October 5 saved counterexamples](2026-10-05_uah_h0_h1_independent_review.md)
against current bytes, preserving finding IDs. R0-B ports the iTrader iteration
workflow into one UAH-native skill. Runtime repairs, release closure, provider
setup, staging, commits, pushes and branch manipulation are excluded.
GRILL/DEV/RESEARCH describe the user's chat coordination, not UAH architecture.

The [start manifest](2026-10-08_uah_r0_start.sha256) records 73 dirty/untracked
file contents before R0 additions. The original review's 107 captured hashes
all match at the baseline helper's start and end. R0 additions are outside
that initial manifest. Concurrent user commits or byte changes must be recorded
and invalidate affected frozen results; no user work may be reset or overwritten.

## Locked skill experiment, before candidate drafting

- **Target artifact:** `.codex/skills/uah-stack-iteration-loop/SKILL.md` only.
- **Objective:** Make the bounded trace/public-test/owner-correction/replay/review
  loop usable for UAH without moving authority or importing trading semantics.
- **Train set:** T1 compiler policy-identity failure with an untouched valid
  compilation control; T2 successful provider connectivity without complete
  operation/effect acceptance; T3 concurrent user commits or source changes
  during a frozen repair round.
- **Holdout set:** Three independently authored workflow requests, withheld
  from the writer until the initial draft is frozen. Locked before drafting:
  `/tmp/uah-skill-forward-review-20261008-28fab5e-holdouts.json`, SHA256
  `2f7c0be9206f0fe20ec8a89ddecaa86ecdcab559fb650cf211b52c9b9a0e8319`.
- **Acceptance gate:** Valid metadata and references; UAH owners and release
  distinctions preserved; no trading/ROS-only requirements or REVIEW policy
  duplication; no unauthorized mutations, invented evidence or indefinite
  continuation; train cases improve applicability and holdouts do not regress;
  fresh independent review under REVIEW.md, including a distinct second model
  for decision-gate instructions. This is workflow evaluation, not a model benchmark.
- **Mutation budget:** One justified initial foreign-to-UAH adaptation, followed
  by at most one refinement of up to three edits and 12 changed lines. A failed
  final gate returns a bounded handoff, not repeated wording mutations.

The foreign skill is not a UAH baseline implementation. It targets iTrader
training/PBT and directs its comparable run to that stack. Baseline evaluation
therefore concerns workflow applicability and decisions, not UAH runtime or
measured model performance. The target has no pre-existing version.

## R0-A: Current counterexample results

The fresh `r0_saved_probe_baseline` helper read the saved scripts before running
them. All six scripts exited zero; that proves diagnostic execution only.

| Mechanism | Original IDs | Expected | Actual on current bytes |
| --- | --- | --- | --- |
| Domain policy identity | STD-01, SPEC-01 | Reject stale content before compilation | Replacement and nested mutation compile retryable policy under unchanged revision |
| Outgoing-tree cache | STD-02 | Reject untested committed tree | Outgoing SyntaxError, valid restored worktree, cache check exit 0 |
| In-memory event integrity | STD-03, SPEC-04 | Reject invalid event before projection/reduction | O1 accepted/recorded; replay prerequisite ValueError; budget grants 4 against original 3 despite invalid hash |
| Raw-start authority | SPEC-02 | Require admitted ingress provenance | Fabricated start and compiled task survive restart |
| Catalog semantic drift | SPEC-03 | Reject semantics outside frozen projection | Prohibited direct_speech in owner evidence; restarted task accepted |
| Prompt/admission scope | ARCH-01 | Omit forbidden operation | Prompt offers write_note; normalization succeeds; admission rejects object_effect_prohibited |
| O1 label escalation | ARCH-02 | Require evidence for measured/reviewed labels | Fabricated terminal renders accepted with both labels; ledger rejects missing task_started |

Errors observed by the saved diagnostics:

```text
ValueError: lifecycle event terminal_task_accepted requires effect_obligation_satisfied
ValueError: trace lifecycle must begin with task_started
SyntaxError in the cache probe's temporary outgoing commit
```

The exceptions above are evidence inside the diagnostics, not failed script
launches. No unexpected command error prevented scoring a saved mechanism.
In-memory mutation consequences are scoped to in-memory mode; file-backed
reload provides the recorded validation control. Incomplete explicitly synthetic
illustrations alone are not counted as an authority defect.

### Exact diagnostic commands

```bash
PYTHONPATH=src .venv/bin/python docs/artifacts/reviews/2026-10-05_uah_review_repros/standards_domain_tamper.py
PYTHONPATH=src .venv/bin/python docs/artifacts/reviews/2026-10-05_uah_review_repros/standards_push_cache.py "$PWD"
PYTHONPATH=src .venv/bin/python docs/artifacts/reviews/2026-10-05_uah_review_repros/standards_event_tamper.py
PYTHONPATH=src .venv/bin/python docs/artifacts/reviews/2026-10-05_uah_review_repros/spec_probes.py
PYTHONPATH=src .venv/bin/python docs/artifacts/reviews/2026-10-05_uah_review_repros/observatory_probes.py
PYTHONPATH=src .venv/bin/python docs/artifacts/reviews/2026-10-05_uah_review_repros/prompt_scope_probe.py
rg '^[a-f0-9]{64}  ' docs/artifacts/reviews/2026-10-05_uah_h0_h1_review_scope.md | sha256sum --quiet -c -
```

The cache probe commits only inside its temporary synthetic Git repository.
The base lacks equivalent compiler, common-ledger, prompt, Observatory and
cache modules, so interface parity remains unavailable, not passed.

### Three NITs, unchanged

- **STD-04:** The August checkpoint still names the later NAO adapter command
  and replay behavior. Base history uses `python -m ab_harness smoke`.
- **ARCH-03:** HTML-only generated-doc hook invocation exits zero with
  `(no files to check)Skipped`. R0 did not mutate a temporary stale HTML file;
  the original review's fuller counterexample remains historical evidence.
- **ARCH-04:** README still denies runtime budget consumption. Its referenced
  runtime-budget/admission/invocation suite passes 71 tests, with implemented
  tool/model accounting. No NIT was fixed.

```bash
.venv/bin/python -m pre_commit run generated-docs --files docs/architecture/observatory_contract.html
.venv/bin/python -m pytest -q tests/test_runtime_budget_contracts.py tests/test_two_stage_admission.py tests/test_model_invocation.py
git show cf90a7e:docs/plans/universal_agentic_harness_development_log.md
```

### Protected controls

The following exact command passed 10 tests (counts overlap the 71-test suite):

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_task_compiler.py::test_task_spec_compiles_one_frozen_projection_and_obligation_set tests/test_environment_ingress.py::test_new_task_preserves_domain_identity_and_receives_a_uah_trace tests/test_two_stage_admission.py::test_common_ledger_replays_the_full_accepted_authority_chain tests/test_two_stage_admission.py::test_tool_budget_exhaustion_is_recorded_before_second_dispatch tests/test_lifecycle_ledger.py::test_common_ledger_round_trips_strict_events_and_registry_projection tests/test_prompt_compiler.py::test_prompt_compiler_preserves_task_narrowing_and_matches_semantic_admission tests/test_observatory.py::test_projection_keeps_agent_attachment_without_inventing_a_task_or_trace tests/test_observatory.py::test_static_html_escapes_title_and_raw_payload_and_embeds_inert_graph_json tests/test_precommit_cache.py::test_recorded_precommit_signature_is_accepted tests/test_precommit_cache.py::test_changed_repository_state_invalidates_precommit_cache
```

## Approach registry and repair handoff

| Route | Owner and settled invariant | Next discriminating probe | Status / exact gap |
| --- | --- | --- | --- |
| Frozen domain policy | Domain pack/compiler, nested content revalidated at trust crossing | Both mutations plus untouched pack through public compile; no artifact issued for stale input | Authorized separately as R1; no repair occurred in R0 |
| Frozen catalog semantics | Semantic admission, bindings cannot replace compiled object semantics | Changed registry/object plus unchanged approved binding; no lease/dispatch after rejection | Candidate settled-invariant repair, not adapter redesign |
| Ledger integrity | Common ledger, immutable verified authority events | Returned-event mutation versus strict file reload; budget and O1 agree | Candidate settled-invariant repair; preserve sole write/replay owner |
| Static operation scope | Semantic owner, prompts cannot widen admissible capability | Prohibited observable effect versus eligible control | Candidate correction; shared ownership location does not justify a generic framework |
| Ingress provenance | TaskIngressAuthority remains sole ingress authority | Raw start versus admitted start across restart | Blocked on approved issuer/provenance interface shape, not on who owns ingress |
| O1 evidence classes | Read-only Observatory cannot certify unproven measurement/review | Unsupported labels versus provenance-backed evidence | Blocked on fail-closed response and future provenance representation |
| Outgoing Git coverage | Development hook must bind tested content to outgoing trees | Worktree differs from pushed tree; multiple outgoing refs | Blocked on explicit outgoing-ref coverage policy; no CI bypass claim |

The smallest first batch is **STD-01/SPEC-01 only**: public compiler regressions
for replacement and nested policy mutation, the valid frozen-projection control,
and local content verification before consuming rules. This enforces an accepted
invariant without shared codec extraction or a new architecture decision.
Follow with catalog semantics and in-memory ledger integrity, each as a separate
reviewed batch. Static scope then follows its semantic owner. Exact ingress
issuer/provenance, O1 label behavior and outgoing-ref coverage go back to GRILL
before adding new contracts. All seven runtime/tooling mechanisms remain open.

## Provider and release boundary

Provider choice does not block the first repair. Existing synthetic environment,
agent-run, prompt and invocation fixtures can support troubleshooting of current
contracts without NAO hardware. The renderer's `synthetic_notes` example and
synthetic workspace runtime tests are reuse candidates, not evidence of a new
complete acceptance path. The [RESEARCH handoff](../../research/2026-10-08_uah_r0_exit_contracts_and_provider_routes.md)
confirms that the current actor example stops after raw invocation and does not
establish semantic admission, owner effects or terminal acceptance.

The human approved two later targets under the same provider-neutral contract:
a local Ollama server using a cloud model, and the personal Watson model reached
through ZeroTier. Neither target was called, and no main-PC startup was requested.
Cloud structured-schema capability is not assumed. Synthetic environments/runs
are approved, with the existing `synthetic_notes` frame preferred. The next
composed proposal must cover ingress, actor/lease/readiness, frozen prompt/raw
invocation, normalization, both admission gates, owner evidence, acceptance and
restart/digest. Evidence/freshness representation remains unapproved and belongs
to the separate RESEARCH/GRILL decision. Connectivity alone does not qualify H0/H1/H2.
Live transport, model performance, full H1 failure-suite closure, native NAO
parity and hardware behavior remain `not_scored` in R0.

## R0-B evaluation record

The initial adaptation is permitted to exceed a 12-line refinement budget because
it replaces foreign owners and stack probes rather than tuning an existing UAH skill.
No historical review, canonical release contract or runtime implementation is rewritten.

### Objective and mutation batch

One initial adaptation added `.codex/skills/uah-stack-iteration-loop/SKILL.md`
at SHA256 `3011cad0dd069cb488217a708e5f8bd78f2641658de4302f3ffaa569381fc37e`.
It preserves the bounded freeze/red/owner/replay/review/decision sequence while
substituting UAH contracts and comparable probes for trading owners and PBT.
No UI metadata, helper scripts, runtime adapter or review-policy fork was added.
The skill-creator validator reports `Skill is valid!`.

### Train results (writer's workflow inspection)

| Case | Foreign baseline instruction support | UAH candidate decision support | Result |
| --- | --- | --- | --- |
| T1 policy identity | Bounded loop/control principle present, but owners and official probe point to trading stack | Red public compiler seam, untouched control, UAH owner correction, fresh REVIEW required | UAH applicability improved; no runtime fix evaluated |
| T2 connectivity only | Separates trading evidence classes, without UAH proposal/effect chain | Explicitly separates connectivity from admission/lease/evidence/acceptance and release gates | Claim distinction specialized; no endpoint tested |
| T3 concurrent changes | Dirty boundary frozen; no explicit invalidation on concurrent commits/content changes | Record concurrent change and refreeze affected evidence without reset/overwrite | Handling made explicit; no concurrent edit manufactured |

These are inspected workflow decisions against locked cases, not independent
prompt-run transcripts or measured model benchmark outcomes. The candidate
contains the intended rules; the independent results below determine instruction
fit only. No refinement has occurred.

### Holdout results and decision

The forward reviewer accepted all three locked walkthroughs: nonterminal O1
operation rejection, frame-relative incomparable probes, and quarantined retrieval
candidates. The foreign baseline's mandatory trading-stack probe was inapplicable
to those UAH requests. These were independent source-grounded workflow decisions,
not isolated model rollouts or runtime experiments.

| Fresh reviewer | Requested model/effort | Findings | Verdict |
| --- | --- | --- | --- |
| `r0_skill_forward_review` | `gpt-6.1-sol/max` | 0 BLOCKING; 1 NIT | APPROVE |
| `r0_skill_independent_gate_review` | `gpt-6-astra/max` | 0 BLOCKING; 0 NIT | APPROVE |

No fallback was reported; deployment identity was not independently observable.
Both reviewers addressed all five REVIEW.md design principles. The optional NIT
concerns the unconditional document-edit sentence at skill line 60. The diagnosis-only
boundary and linked guardrails remain authoritative; the wording is retained in
this frozen candidate rather than starting an unreviewed refinement. The forward
decision artifact is `/tmp/uah-skill-forward-review-20261008-28fab5e-candidate-walkthrough.md`.
Its independent review is `/tmp/uah-skill-forward-review-20261008-28fab5e-independent-review.md`,
SHA256 `ea6b006a3749c7edbe23dabca13564111e103d3779a6255dfb6178181e1d764f`.
The full [primary review](2026-10-08_uah_r0_skill_review/primary_review.md),
[distinct-model review](2026-10-08_uah_r0_skill_review/second_model_review.md),
[locked holdouts](2026-10-08_uah_r0_skill_review/locked_holdouts.json),
[foreign baseline walkthrough](2026-10-08_uah_r0_skill_review/baseline_walkthrough.md),
[candidate walkthrough](2026-10-08_uah_r0_skill_review/candidate_walkthrough.md)
and [static checks](2026-10-08_uah_r0_skill_review/static_checks.json) are retained
beside this receipt without changing their content or original verdict.

R0-B accepts instruction fit at the frozen candidate hash. This does not establish
improved agent performance, runtime correctness or release closure. R0-A's seven
mechanisms and three NITs remain open. **Runtime verdict: CHANGES.**

### Exact metadata and repository checks

```bash
.venv/bin/python /home/juanbeck/.codex/skills/.system/skill-creator/scripts/quick_validate.py .codex/skills/uah-stack-iteration-loop
./scripts/run_precommit.sh
.venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python scripts/render_observatory_example.py --check
PYTHONPATH=src .venv/bin/python scripts/render_agent_runtime_example.py --check
.venv/bin/python scripts/render_agentic_harness_docs.py --check
git diff --check
sha256sum --quiet -c docs/artifacts/reviews/2026-10-08_uah_r0_start.sha256
```

The initial parent executions of pre-commit and pytest failed with missing
`pre_commit` and `pytest` modules; the forward reviewer also found missing PyYAML.
RESEARCH coordinated `./scripts/setup_dev_tools.sh` in the shared checkout. DEV
did not run a competing installation. After dependencies became available, the
commands above passed: metadata valid, all pre-commit gates passed, 344 tests
passed, both O1 examples and generated documents current, whitespace clean, and
the 73 start hashes unchanged. These checks do not repair the saved counterexamples.
No source repair, staging, commit, push or branch change occurred in R0.
