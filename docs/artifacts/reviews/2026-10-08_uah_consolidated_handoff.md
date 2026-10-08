# UAH: consolidated review and NAO-first handoff

Date: 2026-10-08, Europe/Madrid. Documentation-only round starts at 20:10:03
and stops by 20:25:03. Initial branch `feat/pre-commit-queue`; initial HEAD
`28fab5e7f2c244d86a64c371f2118017999b2387`. No source/runtime repair, live call
or agent-owned Git mutation is authorized.

The human selected consolidation today, NAO as the first parity/test
environment, and deferral of the synthetic environment. This changes the work
order, not qualification. H0/H1/H2 exits remain open. The existing masterplan's
H0 synthetic lifecycle and H1 synthetic failure-suite acceptance requirements
remain unchanged. Substitution with NAO fixtures requires an explicit
release-contract coverage mapping and agreement in the main architecture grill.

## Reviewed mechanisms, not release closures

Four original reproduced mechanisms have scoped closures. Combined
Standards/Spec labels count as one mechanism, not extra fixes.

| Original mechanism | Scoped result | Evidence |
| --- | --- | --- |
| STD-01 / SPEC-01 | Domain-pack content revalidation at the compiler crossing | [R1](2026-10-08_uah_r1_domain_pack_identity.md) |
| STD-03 / SPEC-04 | Detached ledger exports and stale-content consumer validation | [R3](2026-10-08_uah_r3_ledger_integrity.md) |
| SPEC-03 | Reproduced concrete admission, execution and nested-artifact catalog mechanisms reject, with valid controls | [Nested-owner gate](2026-10-08_uah_r4_nested_owner.md), [original-probe accounting](2026-10-08_uah_arch01_static_eligibility.md) |
| ARCH-01 | Shared pure static eligibility rejects prohibited-observable prompt/admission mismatch | [ARCH-01](2026-10-08_uah_arch01_static_eligibility.md) |

The additional [raw O1 constructor repair](2026-10-08_uah_o1_conformance_fix.md)
has two scoped approvals and integrated checks for shape, identity and
detachment. It does not close ARCH-02 provenance-label policy. No row proves
all-consumer, all-catalog or release-wide conformance. The
[follow-up index](2026-10-08_uah_review_followup_status.md) remains its earlier
dated snapshot; original findings and round verdicts are unchanged.

## Open mechanisms and review debt

| Item | State and owner | Required decision or evidence |
| --- | --- | --- |
| STD-02 | Open, repository tooling owner | Outgoing ref-tip versus all outgoing-commit coverage, actual Git pre-push inputs and tested-tree identity. No cache fix implemented. |
| SPEC-02 | Open, human contract decision then core ingress/ledger owner | Authority-bound command/capability versus authenticated admitted-ingress proof. Both remain alternatives; the main grill owes the explanatory diagram. |
| ARCH-02 | Open, O1 provenance owner | Evidence for measured/reviewed labels; valid event hashes alone do not qualify labels. |
| R1 report provenance | Unresolved | [Historical report-hash discrepancy](2026-10-08_uah_r1_report_provenance_check.md); transformation materiality remains unknown. |
| R4-FIX review record | Historical CHANGES/incomplete | [Interrupted primary record](2026-10-08_uah_r4_fix_primary_partial.md) retains the platform error and reported mismatch. Later fresh nested-owner approvals do not complete that earlier review. |
| Research dashboard | Stopped, CHANGES | [Final gate](2026-10-08_uah_research_dashboard_final.md) preserves heading/fenced-date and duplicate-header format blockers. |
| Synthetic R5 | Deferred unapproved candidate, CHANGES | [R5 handoff](2026-10-08_uah_r5_owner_local_foundation.md) preserves second-owner fence bypass, hardlink effect escape and stale nested compiled-task identity with both complete reviews. No repair or deletion authorized. |

Original review NITs remain tracked. Research on reusable review-agent seams and
commit accounting is a separate proposal, not accepted review policy. No new
ledger/schema, hook, automation or review-rule change follows without agreement.
Ingress A/B remains the sole pending human question in this pass; other choices
above are recorded debt, not additional simultaneous questions.

## Actual next prerequisite sequence

```text
human ingress-provenance decision
  -> reviewed core task-ingress correction
  -> owner-reviewed NAO source/contract/fixture coverage
  -> recorded/fake NAO authority-chain and failure replay
  -> O1 inspection of explicit environment/task/actor lineage
  -> reviewed parity disagreements and release-evidence mapping
```

1. **Main grill and core owner:** explain and select ingress provenance before
   a separately authorized source repair. Preserve the common ledger as writer
   and keep content identity distinct from producer authentication.
2. **NAO adapter/domain owner:** prepare package-owned golden fixtures against
   NAO `v1.0.0` and pinned chatbot revision `a2ecca796...`. Freeze the reviewed
   DomainContractPack, registry/bindings, API schemas, environment profile and
   named chatbot/planner roster. Preserve native goal/request/plan/version/step
   lineage. `report_result` remains planner AB1 with explicit chatbot delegation
   and native communication ownership. Preparation is not container-start or
   endpoint-call authorization.
3. **Core and NAO evidence owners:** map output-schema, stale-evidence,
   false-completion, cancellation, timeout, retry and budget cases to existing
   public compile/admit/lease/execute/evidence/acceptance seams. Required and
   best-effort obligations stay distinct from owner observations and terminal
   judgments. The research coverage proposal cannot waive an exit criterion.
4. **O1 owner:** inspect recorded/fake replay from one ledger through explicit
   environment-run, task/trace, agent-run and operation views. Retain the
   reviewed shape/identity fix; do not infer actors or promote labels from
   discovery. O2 remains later interactive work.
5. **Human release owner with GRILL/RESEARCH:** review disagreements and agree
   the exact NAO-first evidence mapping to unchanged H0/H1 requirements before
   H2 qualification. A later separately authorized provider probe proves
   connectivity only.

Synthetic integration is deferred. Existing source/tests remain for later
review; a human commit records bytes, not R5 approval or production readiness.
H3 Workbench/model pools remain later seams. No live provider, NAO startup,
OptChat, dashboard or additional repair campaign is part of this handoff.

## Skill baseline and deferred iteration

Current uah-guardrails and uah-stack-iteration-loop already require artifact-owned
identity verification, sole-ledger ownership, frame-relative AB coordinates,
read-only O1 and independent evidence gates. Today's failures do not establish
a missing instruction rather than implementation nonconformance. No skill or
REVIEW.md edit is warranted solely for freshness. Any concrete gap identified
by the separate research pass must be proposed as its own SkillOpt iteration:
freeze target/objective/train/independently owned withheld holdout/acceptance
before editing, preserve baseline and candidate, and record acceptance or
rejection. No such iteration is implemented or qualified here.

## Manual review and commit handoff

Start inventory/hashes are retained under
`2026-10-08_uah_consolidation_evidence/start_status.txt` and `start.sha256`.
Its `before/` directory preserves the two pre-edit canonical Markdown sources.
This pass changes only current masterplan/log Markdown and generated HTML,
this handoff and documentation-gate evidence. Old reports and code/hash receipts
remain unchanged; historical end manifests are not regenerated when a current
planning document evolves.

For bulk review, begin with lifecycle.py and task_compiler.py using the
R1/R3/nested-owner receipts; then proposal_admission.py and prompt_compiler.py
under ARCH-01, and observatory.py under the separate O1 receipt. These qualify
only repaired mechanisms. STD-02/SPEC-02/ARCH-02 remain open; NAO adapter changes
need package-owned parity evidence. The original October 5 review covered the
dirty tree and five recent commits; today's narrow gates do not replace it.

The human owns staging, commits and pushes. Concurrent source/dependency edits
require recording the new HEAD/hashes and reassessing affected reviews. Do not
reset or rebase to recover a frozen comparison. Commit state, reviewed-byte
coverage and release qualification are different facts.

## Documentation gate

Pending at author freeze: bounded fresh documentation reviews, canonical render
and synchronization check, hook suite and diff check. Approval covers this
consolidation only, not source or release. If incomplete by 20:25:03, record
pending and stop rather than extend the round.
