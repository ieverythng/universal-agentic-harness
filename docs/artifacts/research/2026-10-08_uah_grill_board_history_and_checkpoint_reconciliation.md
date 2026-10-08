# GRILL board history and checkpoint reconciliation proposal

Date: 2026-10-08. Dispatch: GRILL-BOARD-DESIGN-01. Started 19:55:51 UTC; hard stop 20:07:51 UTC (21:55–22:07 Europe/Madrid), including handoff. Source/document-only; one scoped child mapped canonical checkpoints. Proposal, not adopted review policy, runtime implementation or release closure.

## Decision-ready recommendation

Use the existing [grill.md](/home/juanbeck/universal-agentic-harness/docs/coordination/grill.md) as a plain, scrollable Markdown decision journal. Its 19:58 UTC update already includes a decision-history table. Enrich that existing history with rationale, source references and explicit supersession where missing; do not create a competing record. Keep current scope and pending questions compact at the top. Do not build a dashboard, service, new protocol, acknowledgment engine or UAH lifecycle component.

GRILL alone owns that file's continuing writes. DEV and RESEARCH retain their own current-status files and link completed evidence. The existing [board contract](/home/juanbeck/universal-agentic-harness/docs/coordination/README.md) is adopted; the history layout below is proposed. Single-writer ownership is a convention, not authenticated runtime authority or filesystem isolation. File writes do not wake GRILL; no new polling or monitoring is proposed.

## Smallest durable history shape

Top sections: current finite scope, one actionable pending question when blocked, links to the last accepted decisions, then a short queue. Beneath them, chronological decision headings retain the scrollable history. Ordinary progress and transcripts stay out.

A plain Markdown entry, not a machine schema:

```text
### D-YYYYMMDD-NN: Decision topic
Question: exact choice and scope.
Decision: accepted/rejected/deferred; distinguish a pending proposal.
Source: human message/reference or explicit GRILL dispatch and known time.
Rationale: constraint or evidence that determined the choice.
Owner and next action: one finite task, permitted paths, bound and stop condition.
Evidence: links to owning contracts, proposals and exact review receipts.
Applicability: proposal; reviewed snapshot; staged/commit state; release status.
Supersedes: earlier decision ID, only when explicitly changed.
```

Only record acceptance when the human or authorized dispatch actually supplies it. A researcher recommendation, passing tests, peer urgency or lack of reply is not acceptance. If no stable message link exists, preserve a short exact human statement and known date, explicitly noting the missing durable reference; do not invent a timestamp or identity proof.

Retain old accepted entries when superseded. Add the new decision and a link to the prior one rather than rewriting it as though the earlier choice never existed. Link from current status to the effective decision. This is organizational history, not an append-only tamper-resistant log or release evidence. The retained incident [coordination analysis](/home/juanbeck/universal-agentic-harness/docs/artifacts/research/2026-10-08_uah_hugging_face_incident_and_coordination_board.md) already states these limits; it is not researched again here.

No additional acknowledgment machinery is warranted by this pass. A stale status is not proof that a request was lost. GRILL reads at active gates and new turns; a blocked owner stops dependent work and records the exact decision needed on its own file.

Keep three distinct records: editable current status names the effective scope and next gate; retained decision entries preserve accepted choices and explicit supersession; dated evidence artifacts preserve completed observations against their inspected bytes. Neither current status nor the journal establishes lossless history or automatic delivery. GRILL's final scoped refinement adopts stable decision IDs in its own journal, without an acknowledgment engine; the four-path DEV documentation slice remains proposed and queued.

Proposed reader/writer tightening: read the effective GRILL dispatch and own board at task start, resume and final gate; update the owned board at scope changes, actionable gates and final handoff. Preserve pending requests by task/request ID until explicit disposition, and link durable completed evidence before replacing current status. GRILL reports post-switch compliance with board-only routing by both parents, but an older DEV board than a later private-clone/setup milestone. This is owner-reported freshness evidence, not an independently audited loss, enforcement proof or pilot result. No board contract or AGENTS amendment is made here.

## Authoritative document inventory

| Fact being reconciled | Exact owning document | Preserve |
| --- | --- | --- |
| Chat routing and permission limits | [AGENTS.md](/home/juanbeck/universal-agentic-harness/AGENTS.md:24), [coordination README](/home/juanbeck/universal-agentic-harness/docs/coordination/README.md:28) | Parent ownership, no unsolicited inbound messages, human Git permission; board is not runtime authority |
| H0–H6 requirements and release exits | [Masterplan](/home/juanbeck/universal-agentic-harness/docs/plans/universal_agentic_harness_masterplan.md:3), H0 at [825](/home/juanbeck/universal-agentic-harness/docs/plans/universal_agentic_harness_masterplan.md:825), H1 at [878](/home/juanbeck/universal-agentic-harness/docs/plans/universal_agentic_harness_masterplan.md:878) | Complete replay/failure evidence; NAO-first changes order, not exits |
| Current implementation and later checkpoint navigation | [Development log](/home/juanbeck/universal-agentic-harness/docs/plans/universal_agentic_harness_development_log.md:16), sole-source topology at [207](/home/juanbeck/universal-agentic-harness/docs/plans/universal_agentic_harness_development_log.md:207) | Canonical Markdown with generated HTML; historical checkpoint facts remain dated |
| Vocabulary and architecture authority | [CONTEXT.md](/home/juanbeck/universal-agentic-harness/CONTEXT.md:271), [foundation](/home/juanbeck/universal-agentic-harness/docs/architecture/universal_agentic_harness_foundation.md:11), [ADR 0001](/home/juanbeck/universal-agentic-harness/docs/architecture/decisions/0001-semantic-objects-and-shadow-first-bindings.md:22) | Target versus implemented terms; foundation defers release status to masterplan |
| O1 labels and deferred producer evidence | [Observatory contract](/home/juanbeck/universal-agentic-harness/docs/architecture/observatory_contract.md:404) | Human-selected label restriction, stopped implementation gate and not-implemented evaluator/reviewer interface are separate |
| Independent review requirements and method | [REVIEW.md](/home/juanbeck/universal-agentic-harness/REVIEW.md:1), [review workflow](/home/juanbeck/universal-agentic-harness/docs/agents/uah_review_workflow.md:25) | Fresh reviewer, predeclared inputs, base comparison, all five principles, per-fix review, required different-model coverage |
| Original findings and scoped follow-ups | [October 5 review](/home/juanbeck/universal-agentic-harness/docs/artifacts/reviews/2026-10-05_uah_h0_h1_independent_review.md), [October 8 historical follow-up](/home/juanbeck/universal-agentic-harness/docs/artifacts/reviews/2026-10-08_uah_review_followup_status.md:3), later individual receipts | Original IDs/verdicts/hashes; historical index is not current HEAD status |
| Review/commit accounting proposal | [Prior accounting handoff](/home/juanbeck/universal-agentic-harness/docs/artifacts/research/2026-10-08_uah_review_commit_accounting_and_nao_first.md:31), [existing examples](/home/juanbeck/universal-agentic-harness/docs/artifacts/research/2026-10-08_uah_review_commit_examples.json) | Examples remain proposals; no new record schema or reviewer runtime is needed |
| Current implementation/review/pilot evidence | [DEV-owned board](/home/juanbeck/universal-agentic-harness/docs/coordination/dev.md) and its receipts | DEV alone owns the live No-Mistakes pilot; temporary evidence is not durable release/commit approval |

Historical accepted decisions also live in [September 8 identity/environment grill](/home/juanbeck/universal-agentic-harness/docs/artifacts/decisions/2026-09-08_uah_identity_environment_and_memory_grill.md) and [August 4 H2 grill](/home/juanbeck/universal-agentic-harness/docs/artifacts/decisions/2026-08-04_uah_h2_neural_workbench_grill.md). Link them; do not copy their full transcripts into the board or make a second delivery-status spine.

## Concrete drift and double-counting risks

1. Masterplan [section 13](/home/juanbeck/universal-agentic-harness/docs/plans/universal_agentic_harness_masterplan.md:1513) has undated observations saying seven tests pass and task/provider/environment specs are absent. Its current H1 section and log's [TaskSpec v2 row](/home/juanbeck/universal-agentic-harness/docs/plans/universal_agentic_harness_development_log.md:175) describe newer implemented artifacts. Label supported historical context and point to current status; do not pretend those old probes ran now or invent their original dates.
2. Log's [H2 table header](/home/juanbeck/universal-agentic-harness/docs/plans/universal_agentic_harness_development_log.md:1372) says September 23 while rows include later actor, fixed-lease and TaskSpec v2 work. Give the current table an honestly supported update date, or separate historical rows. This does not change acceptance criteria.
3. Log's [Repository guardrails Green row](/home/juanbeck/universal-agentic-harness/docs/plans/universal_agentic_harness_development_log.md:187) omits the still-open STD-02 outgoing-commit coverage limitation. Narrow it to implemented worktree checks and retain the unresolved finding. A new tooling audit or fix is outside this documentation scope.
4. Historical follow-up still calls SPEC-02 untouched, while later [ingress receipt](/home/juanbeck/universal-agentic-harness/docs/artifacts/reviews/2026-10-08_uah_ingress_authority_repair.md) and log record selection/scoped approval. The old index explicitly names its snapshot and [consolidation](/home/juanbeck/universal-agentic-harness/docs/artifacts/reviews/2026-10-08_uah_consolidated_handoff.md:31) preserves it. This is a navigation hazard, not a reason to overwrite history.
5. The earlier captured GRILL snapshot (updated 19:48 UTC, hash below) retained a blocked-pilot decision; DEV subsequently recorded the finite 19:56:41 NM-PILOT-01 dispatch. GRILL's 19:58 UTC board, inspected at 20:03:02 UTC, already records explicit supersession and a decision-history table. The earlier navigation mismatch is resolved in that later board, not an outstanding defect. Preserve both historical decisions. Neither dispatch nor supersession proves a completed AXI run; no pilot controls were re-audited.

No inspected owner document equates a scoped APPROVE with H0/H1 closure. The [workflow](/home/juanbeck/universal-agentic-harness/docs/agents/uah_review_workflow.md:19) explicitly separates them. Existing caveats should be retained rather than reported as new defects.

STD-01/SPEC-01 and STD-03/SPEC-04 are paired labels for two mechanisms, not four closures. Two reviewers approving one frozen seam are not two fixes. Raw O1 identity/shape repair does not close ARCH-02 label provenance. R2/R4/nested-owner/ARCH-01 follow-ons do not each create another original SPEC-03 closure. Do not add overlapping test-suite totals. These controls are already reflected in the [consolidation](/home/juanbeck/universal-agentic-harness/docs/artifacts/reviews/2026-10-08_uah_consolidated_handoff.md:17).

Keep separate facts for accepted design, implemented candidate, exact independently reviewed bytes/dependencies, selected/staged bytes, observed commit SHA/tree, and release exit. An approved-but-uncommitted repair and committed-CHANGES candidate are legitimate distinct states; unknown stays unknown.

## Complementary review roles without duplicate campaigns

This is a proposed allocation of existing methods, not an amendment to REVIEW or installed skills.

- REVIEW remains the binding qualification contract. Its scope, model/deviation record, all five design principles, base comparison and final verdict cannot be replaced by an informal result.
- The [code-review skill](/home/juanbeck/.agents/skills/code-review/SKILL.md) organizes Standards and Spec separately over one frozen comparison and explicit spec. Reuse those axes within the existing review round, not as a second whole-branch campaign. Architecture/O1 becomes affected-seam coverage, not an automatic third full reread. Existing local workflow has no external tracker; no tracker setup was performed.
- The inspected [review-agent leaf skill](/home/juanbeck/.codex/skills/.system/review-agent/SKILL.md) is read-only and defect-first, reviews the whole assigned delta, and forbids delegation or publishing. Supply a frozen scope and the governing repository contract. Its generic instruction reads code first and uses P0–P3/No findings; UAH's higher-priority execute-before-read, BLOCKING/NIT, principle reporting and terminal verdict rules still apply. Preserve priority as extra detail if useful. Separate introduced defects from inherited debt and heuristic advice; inherited debt can still block release. No findings is not complete approval when coverage is incomplete.
- High-risk seams still need a second independent different-model review of that risky seam. Different models on unrelated Standards/Spec axes do not automatically satisfy it. Every fix needs fresh focused review; no automatic campaign extension.
- No-Mistakes may supply scenario/test-oracle and changed-file evidence under DEV's already scoped pilot. Reuse its relevant reproduced evidence where applicable, but do not count its model verdict as independent REVIEW or repeat both full workflows by default. Pilot outcome, tool-owned commit, selective human integration and release qualification remain separate. This pass changes no pilot controls or vendor instructions.

The prior [review accounting proposal](/home/juanbeck/universal-agentic-harness/docs/artifacts/research/2026-10-08_uah_review_commit_accounting_and_nao_first.md:31) already covers this orchestration. Any adoption in the review-workflow document is a later separately reviewed instructional scope, not part of checkpoint cleanup or a new schema.

## Small next DEV documentation scope

Propose only these four existing paths:

1. `docs/plans/universal_agentic_harness_masterplan.md`: mark the old section 13 observations as historical with only supported provenance; point to current checkpoint status. Preserve H0/H1 exit contracts and explicit NAO coverage-mapping decision.
2. `docs/plans/universal_agentic_harness_development_log.md`: correct the H2 table date, qualify the guardrails row, and make existing Current state links the latest checkpoint navigation. Link only finalized owner-supplied review receipts; preserve historical IDs, CHANGES, stopped/incomplete reviews and uncovered dependencies.
3. Their generated `.html` companions, generated from canonical Markdown using the existing [renderer manifest](/home/juanbeck/universal-agentic-harness/scripts/render_agentic_harness_docs.py:16).

GRILL maintains its own proposed history layout separately if accepted; DEV does not write GRILL's continuing file. Do not touch REVIEW, skills, workflow policy, CONTEXT/architecture semantics, old reports/indexes, source/tests or shared Git/index in this reconciliation slice.

Acceptance: supported dates and links; no duplicate mechanism closures; exact reviewed-versus-staged/committed distinctions; no release upgrade; synchronized Markdown/HTML; frozen before/candidate documentation with independent REVIEW and applicable link/format/claim checks, hooks and diff check. A later review-workflow integration is a separate scope, including bounded SkillOpt where its instructions require it.

## Evidence limits and validation

Inspected shared HEAD was `06f5a29daef9bb877fb08b6c6ee47d870df94d71` on dirty `feat/pre-commit-queue`; the selected13 index was only read, never modified. Below are document hashes at inspection, not an atomic whole-tree snapshot or reviewed commit manifest. Final unchecked-dependency review and live pilot outcomes belong to DEV, and durable final receipts/coverage may still be missing. Original dates for the section 13 observations were not reconstructed. NAO replacement of synthetic exits remains an unaccepted release-contract mapping. No H0/H1/O1/H2 release closes here.

```text
be7fc663d94170575013c2c79c1e597956bb5204e0f700d13cc7043d2b4e0d2c  AGENTS.md
8a1890c212e0f233eeb224d5d11a954d169228c85b949c2f072916f308fa763a  REVIEW.md
8c053aee9841996ae602f272b40f0d93f17b2e5123d4a13d342942049658506a  CONTEXT.md
8ff54631a1b37f9385eaeadc59fd8e4384dd6c93ab5f38fbb7460dbe0f2d4829  docs/coordination/README.md
db648d342df6c4b7a46057cc885746dc335def6c9e9646d22e2338d507640392  docs/coordination/grill.md
20038ec85d98fa1ad2c1cf33122c12ca4f1c38db80bbb1f658385fed5c50a661  docs/agents/uah_review_workflow.md
a8d004a9d250d0291d8be9bd958a2ffc02bccd68be2a4fea968e1772d9dd4bf4  docs/plans/universal_agentic_harness_masterplan.md
ec487894559266fb736bdee1b0623e6155c0d039ac15305f5e90c3deb661d1a8  docs/plans/universal_agentic_harness_development_log.md
6ebc8d0dd25d557712029e5a79edfe07fe4d59846bf80352c54bccdb43f410b9  docs/architecture/universal_agentic_harness_foundation.md
7914b2d07ef6443824108bde8eaefbef9ff6df725d8dca686c6970fa404a7920  docs/architecture/observatory_contract.md
907ca4c925d2e8a359bc725e4b46c60b81ecf2151c2967840e3634334a8219a0  docs/artifacts/reviews/2026-10-08_uah_review_followup_status.md
a860e754ca51b1dac67e3739b6f648a4daad4bbe266d8177c340e43bc7838a58  docs/artifacts/reviews/2026-10-08_uah_consolidated_handoff.md
```

This pass writes only this dated handoff and the RESEARCH-owned board. The full pre-commit suite passed in an isolated validation copy; explicit new-file hygiene checks and shared read-only diff checks passed. All 35 local links exist and cited line numbers are in bounds. The isolated copy uses an older frozen source/test snapshot, so these checks validate documentation hygiene, not current dirty source, the live pilot or release readiness. The research skill required the source-mapping child and cited artifact; UAH guardrails kept release/effect authority distinct. No continuation follows this pass.
