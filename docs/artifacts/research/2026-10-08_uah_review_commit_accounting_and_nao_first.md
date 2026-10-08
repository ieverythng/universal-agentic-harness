# UAH review accounting and NAO-first coverage proposal

Date: 2026-10-08. Bounded research pass started 18:10 UTC; stop target 18:30 UTC.
Status: proposal and source coverage, not accepted policy or implementation.
Owners: DEV owns adoption and fresh implementation review; human/GRILL owns
architecture and release-contract decisions. Two read-only research lanes were
used. No broad code review, live call, native mutation, staging or commit ran.

## Outcome and evidence boundary

Use two independent records: review coverage and commit accounting. Keep release
qualification a third decision. An approved repair may be uncommitted; committed
CHANGES bytes remain unapproved. NEED TO CHECK records review debt rather than
proving all committed code unusable.

NAO becomes the first integration/parity environment. Synthetic R5 remains
deferred CHANGES, with three retained mechanisms. H0/H1 synthetic replay and
failure-suite exit obligations remain unchanged until an explicit owner-approved
coverage substitution. H2 planner parity, model qualification and live effects
remain separate claims.

Sources: [REVIEW](../../../REVIEW.md),
[workflow](../../agents/uah_review_workflow.md),
[follow-up](../reviews/2026-10-08_uah_review_followup_status.md),
[consolidation](../reviews/2026-10-08_uah_consolidated_handoff.md),
[masterplan](../../plans/universal_agentic_harness_masterplan.md).
Exact reusable skill targets inspected:
`/home/juanbeck/.agents/skills/code-review/SKILL.md` and
`/home/juanbeck/.codex/skills/.system/review-agent/SKILL.md`.

## Reusable review unit for UAH, iTrader and Terac

The orchestration procedure below is proposed, not installed or a new normative
review framework. Each repository supplies its own standards, spec, owner and
release policy; UAH rules must not be silently imposed on another repository.

1. Declare one owner-local unit, expected behavior, spec, protected paths,
   comparison, authorized probes, deadline and stop conditions. For committed
   reviews resolve the requested base/comparison ref, HEAD and merge-base, and
   retain diff command and commit list. No fixed point was supplied for this
   research pass, so no new broad review was dispatched.
2. For dirty reviews freeze exact-before and candidate content separately from
   index, worktree, untracked and deleted manifests. Include path, type/mode,
   content hash and deletion tombstones. Freeze relevant dependencies as well as
   changed files; a matching edited-file hash alone does not prove contextual
   equivalence.
3. Assign at most two concurrent independent leaf lanes. Standards and Spec
   reports stay independent, with no merging/reranking across axes. Architecture
   coverage is triggered by authority/owner/interface changes, not every
   unrelated diff. Orchestration dispatches; review-agent leaves never delegate.
4. Declare public valid/negative inputs before implementation reading. Exercise
   the public seam in a throwaway environment and compare the exact-before body,
   even if candidate tests pass. An absent baseline seam is unavailable, not
   passing behavioral parity.
5. Review the complete scoped delta and surrounding consumers. Introduced
   actionable demonstrated regressions are findings. Pre-existing seam/release
   debt and heuristic design advice remain separately labeled. Fowler smells
   are judgment calls; repository ownership rules override generic extraction.
6. Apply the repository review contract: every applicable enum/error/boundary
   consumer, reproduction and all five design principles. Reuse a public probe
   matrix where it discriminates the same mechanism; unrelated date/unit
   campaigns do not belong in every review.
7. High-risk changes require a second independently assigned different-model
   review covering the risky seam, within the same concurrency cap. Different
   models on unrelated axes do not automatically supply this coverage.
8. Preserve per-axis findings, severity and verdict. Corroboration may link
   stable mechanism IDs without erasing original IDs or inflating aggregate
   mechanisms. Writer checks and root integration are not independent reviews.
9. Record complete/incomplete/error/timeout, uncovered scope, actual usage and
   deviations. Missing output is not No findings. Incomplete runs supply no
   approval. If the current final-verdict contract requires CHANGES, retain that
   gate plus an explicit incomplete run state rather than inventing approval.
10. Repairs require separate authority and fresh fix review. Stop on the bound,
    new owner/contract choice or unsupported dependency. No autonomous extra
    campaign, tracker setup, provider call or Git mutation follows.

Proposed starting resource envelope: one owner-local unit, two concurrent leaves,
20 minutes total, zero live/provider/native effects by default. Declare file,
changed-line, tool-call and output caps appropriate to the unit before dispatch.
If the full scope cannot fit, split it or record incomplete coverage. These are
proposal limits, not measured reviewer performance or waived review obligations.

Requested model/effort and independently observed backend identity are different
fields. Today's receipts retain gpt-6.1-sol/max and gpt-6-astra/max requests but
do not independently attest execution backend identity.

## Commit accounting and concrete examples

[Example records](2026-10-08_uah_review_commit_examples.json) separate
comparison, reviews, findings, commit events and release status.

The inspected Git HEAD remains
`28fab5e7f2c244d86a64c371f2118017999b2387`, branch
`feat/pre-commit-queue`. Its parent is
`f0159c81ff17ed2333b4a988958c292ebb9fad24`; historical review base and verified
merge-base are `cf90a7e328eb4c80f7fe1418fccb1e60f25a0b77`.
The actual historical commit title is
`feat(lifecycle, task_compile): NEED TO CHECK`.
The October 5 review spans committed and dirty scope; do not assign every
finding to that single commit.

The human expressed intent to commit current changes. No resulting new SHA was
observed. The manual synthetic commit scenario therefore uses null SHA and
requested_human_manual, not a fabricated completed commit. Author/committer
metadata does not authenticate who operated Git.

| Unit | Review state | Observed commit state | Release state |
| --- | --- | --- | --- |
| R4 nested-owner | Two APPROVE reports, exact five-file historical scope | No new commit observed | Not qualified |
| ARCH-01 follow-on | Separate approved static eligibility delta | No new commit observed | Not qualified |
| R5 synthetic native | Two CHANGES reports, three aggregate mechanisms | Human manual commit intended, SHA unknown | Deferred/unapproved |
| Historical 28fab5e | Actual committed bytes, later combined-scope CHANGES review | Existing SHA observed | Review debt, no blanket usability verdict |

Nested-owner frozen proposal_admission.py hash is
`a2a76bf21eb865934d63b5eeece722b4b7827d659421fb7a5bc566bb3161455c`.
Current hash is
`033ba785928c9019b76711ed27c603b6f3f30a2e3110443875bdfea6af019888`.
ARCH-01 exact-before equals the former and its reviewed manifest equals the
latter. This is an explicit later reviewed delta, not unchanged bytes or
unexplained drift. The other four nested-owner scope hashes still match.
Retain both review chains; their composition does not establish release approval.

When a commit is observed, record actual SHA/tree, author/committer metadata,
available actor evidence and per-path reviewed-body equivalence. Extra bytes
remain uncovered. Later dependency/context changes invalidate affected coverage.
Preserve historical verdicts and add focused coverage instead of overwriting
reports or resetting the worktree.

R5 aggregate proposed mechanism labels preserve original report references:

- R5-FENCE: primary Standards finding 1 and second R5-N2-01.
- R5-NESTED-IDENTITY: primary Spec finding 2.
- R5-HARDLINK: second R5-N2-02.

These are three mechanisms, not four because the fence appears in both reports.
The source/test hashes still match the frozen CHANGES candidate.
[Native receipt](../reviews/2026-10-08_uah_r5_owner_local_foundation.md)
retains unavailable isolated baseline, administrative report-link transformation,
passing 532-test shared suite and reproduced failures.

## NAO source coverage

The existing recorded canary composes ingress classification, task compilation,
raw planner hash, proposal/admission, domain lease, fake-owner receipt, acceptance
and digest replay. It declares model_calls=0 and does not compose ready actor,
PromptCompiler or ModelInvocationAuthority. Recorded output is not inference.

| Seam | Actual current source | Missing qualifying evidence |
| --- | --- | --- |
| Ingress | Profile/pack classification, duplicate fencing, ledger start | Raw TaskStartedFact producer bypass remains open |
| Planner envelope | Exact plan.steps and id/type/name/args parser | Native goal/plan/version, dependencies, failure/retry fields rejected |
| AB projection | AB1 find_object plus inspect-only AB0 seam | Native registry/pack owner review; candidate pointers are not approved |
| Owner evidence | Fixture label=cup and literal effect string | Native target/target_kind and target_found/evidence.entity_id mapping |
| Model/actor | Separate fake allocation/invocation tests | Composed NAO readiness/prompt/invocation chain absent |
| Replay | Generic accepted/rejected terminal digests | Retained native source/transform bodies and full lineage |
| O1 | Read-only event/actor/operation views | ARCH-02 provenance labels and native lineage |
| Parity | Narrow recorded/fake generic canary | legacy/shadow/uah disagreement report and wider failure/control cases |

Native fake find_object supplies source=fake_find_object and metadata.fake=True.
It cannot be relabeled detector-backed physical proof. Native normalizers may
generate missing IDs, so fixtures must require supplied IDs before normalization
and retain the original body. Domain-owned replan/supersede transformations need
explicit provenance; timestamps and generated UAH names cannot reconstruct it.

Principal inspected hashes:

- UAH qualification.py: 9d94f9192723bc4e2ed2b7fbab8c49fd1281b77775f63f9330d004ea634fbddb
- UAH contracts.py: a0f8d0e2878b1d3309f24ae039a36c3899d1ef6459aa431ab5cefbba791e338b
- UAH smoke.py: e38ac70b90793c02b2c2d2494908dbbef35ec5e1e66c3615a8e24d82e5fabaab
- Native planner_common/contracts.py: cf9b28199ca959251930eb54204912454c19847be3639ffe681c268560cf4bb9

NAO HEAD: `81b14ef1fa5fc795f46aad90f022e8fbd38e2472`.
Immutable v1.0.0 peeled baseline:
`ebffe93a74be4e013ce0f60fdfc41268dba73fc3`.
Nested chatbot: `a2ecca79600efafeeef75aab4440d18b860b974f`.
Nested Neural-Wokbench:
`5983a6e1f53c47b6980a1f0afdeda398d5b9bb35`.
Nested revisions are recorded separately because the inspected NAO refs do not
bind them as gitlinks. Relevant tracked native contracts show no HEAD/tag delta.
Runtime files stayed stable; UAH masterplan changed concurrently. This is not an
atomic whole-tree freeze or executed qualification.

## Smallest proposed NAO-first proof

1. Freeze one native single-skill find_object request/planner envelope with
   supplied goal_id, request_id, plan_id, plan_version and step_id.
2. Preserve chatbot handoff, native PlannerGate and admitted planner request as
   distinct interfaces. Native gate ownership stays in nao_orchestrator.
3. Add only an owner-reviewed compatibility mapping outside core. Preserve
   dependency/failure semantics; unsupported behavior rejects before dispatch.
4. Execute at most one explicitly fake native-shaped owner call and retain
   result, normalized evidence and acceptance separately.
5. Compare explicit legacy/shadow/uah decisions, zero shadow dispatch and
   owner-accounted authoritative effects; classify every disagreement.
6. Restart and compare lineage, evidence references, terminal result and digest
   without invoking either model or owner again. O1 remains read-only.
7. Follow with a separately bounded ready-actor/fixed-lease/fake-readiness/prompt/
   fake-provider composition, not a live/model qualification claim.

First fixture proposed caps: one environment activation, one AB1 operation,
one tool-call maximum, zero retries and zero model/network/GPU/robot calls,
60-second wall bound. Valid target, malformed/out-of-scope step, unavailable
owner and ambiguous-target clarification are initial comparison families.
Stale evidence, cancellation, timeout, retry exhaustion, false completion,
multi-step/replan/supersede and report_result/no-duplicate-speech remain exits.

Do not casually launch a simulator profile: native launch documentation says
perform_motion defaults to the real adapter. This proposal uses import-light,
recorded in-process fake owners only.

## Instruction-gap decision

No skill mutation recommended. Current uah-guardrails already requires
artifact-owned nested identity checks, separate qualification claims and
quarantine. uah-stack-iteration-loop already requires recording concurrent
commits/content, refreezing affected evidence, independent gates and bounded
stop. Today's defects establish implementation nonconformance, not a measured
missing instruction.

If DEV demonstrates one instruction gap, lock exact skill target, one objective,
train cases, independently withheld holdouts and acceptance before editing.
Use SkillOpt max three edits/about twelve changed lines per file,
baseline→candidate→train→holdout→accept/reject evidence, preserving its reminder.
Different objectives require separate iterations. No promised improvement
without baseline failure and holdout evidence. No instruction or REVIEW edit,
accepted worker interface, second ledger or shared codec is delivered here.

## Validation and bounded handoff

The two lanes performed read-only source/receipt investigation, no new probes.
This pass is not a fresh Standards/Spec implementation review. Canonical document
synchronization and git diff --check pass. Full hooks report 530 passing tests
and two O1 generated-example freshness failures involving blank-line whitespace
in test_agent_runtime_example.py and test_observatory.py. No source/example
repair is made by RESEARCH; this shared-tree result is not blanket green.
DEV owns adoption, scoped implementation, fresh reviews and release evidence.
