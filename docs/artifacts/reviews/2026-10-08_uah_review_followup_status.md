# UAH independent review: follow-up status

Date: 2026-10-08, Europe/Madrid. Branch: `feat/pre-commit-queue`.
HEAD: `28fab5e7f2c244d86a64c371f2118017999b2387`.
Status snapshot: 19:05. No H0/H1 exit or H2 qualification is established.

The [original review](2026-10-05_uah_h0_h1_independent_review.md) covers the
captured dirty tree and five recent commits. Its dated findings and verdicts
are retained unchanged. This index records subsequent bounded gates, rather
than rewriting the original results. `REVIEW.md` remains byte-identical to
the iTrader source at SHA-256
`8a1890c212e0f233eeb224d5d11a954d169228c85b949c2f072916f308fa763a`.

| Original mechanism | Current scoped status | Evidence |
| --- | --- | --- |
| STD-01 / SPEC-01, domain-pack content drift | Reproduced compiler crossing closed by R1; not a blanket claim about every domain-pack consumer | [R1 receipt](2026-10-08_uah_r1_domain_pack_identity.md) |
| STD-02, outgoing-tree pre-push cache | Open, untouched | Original review and [R0 rerun](2026-10-08_uah_r0_baseline_and_skill_handoff.md) |
| STD-03 / SPEC-04, ledger export alias and stale content | Ledger mechanisms scoped closed in R3; separate raw O1 identity, versioned-shape and detachment repair has two qualifying approvals and passing current integration checks | [R3 receipt](2026-10-08_uah_r3_ledger_integrity.md), [O1 conformance receipt](2026-10-08_uah_o1_conformance_fix.md) |
| SPEC-02, caller-authored raw task start | Open, untouched | Original review and R0 rerun |
| SPEC-03, catalog semantic drift | Original October 5 admission and R2 post-admission catalog reproductions now reject, with separately executed valid controls; demonstrated finding scoped closed through R2 and nested-owner approvals. Original R4/R4-FIX CHANGES remain historical; no universal all-catalog proof | [R2 receipt](2026-10-08_uah_r2_catalog_semantic_fencing.md), [nested-owner receipt](2026-10-08_uah_r4_nested_owner.md), [exact rerun accounting](2026-10-08_uah_arch01_static_eligibility.md) |
| ARCH-01, static prompt/admission eligibility | Original prohibited-observable mechanism scoped closed: two fresh approvals, unchanged original probe rejection, valid controls and current integration. Complete stateful equivalence is not claimed | [Separate ARCH-01 round](2026-10-08_uah_arch01_static_eligibility.md) |
| ARCH-02, measured/reviewed O1 labels | Open, untouched; distinct from stale-event identity | Original review and R0 rerun |

The original documentation and hook NITs remain tracked in the original review.
Large file size alone did not establish a reason to split `lifecycle.py` or
`task_compiler.py`. Authority, conversion and replay policy must stay with their
owning module. Similar hashing syntax does not justify a shared codec.

## Additional evidence limits

The retained R1 second-review report differs from one historical hash. The
[provenance check](2026-10-08_uah_r1_report_provenance_check.md) records the
unresolved transformation; its materiality is unknown. Runtime hashes do not
establish that the report text was unchanged.

The research dashboard is metadata navigation, separate from runtime O1. Its
[initial review](2026-10-08_uah_research_dashboard_review_closeout.md) and
[first correction review](2026-10-08_uah_research_dashboard_fix.md) returned
CHANGES. The [final bounded correction](2026-10-08_uah_research_dashboard_final.md)
also returns CHANGES for heading and duplicate-header input variants and stops
without another automatic iteration.
Passing renderer tests does not override those findings or promote research.

The [UAH iteration skill](../../../.codex/skills/uah-stack-iteration-loop/SKILL.md)
ports the bounded iTrader method, not its trading metrics. Its instruction-fit
review is recorded in R0. It does not authorize repairs or live calls on its own.
The [synthetic integration plan](../../plans/synthetic_notes_integration_contract.md)
remains an owner-local fixture plan, not executed full-chain qualification.
Its [R5 native foundation](2026-10-08_uah_r5_owner_local_foundation.md) now
performs actual writes and separate closure-content observations outside core.
Both reviewers reproduce a public second-owner closure-fence bypass. Additional
findings concern nested compiled-task identity and hardlink mutation. Its gate
returns CHANGES and stops without another automatic repair. Passing 532 shared-tree tests does not
authenticate ingress, produce UAH receipts or establish terminal acceptance.

## Immediate decision and deferred work

SPEC-02 awaits the human's producer-provenance choice in the main architecture
grill: an authority-bound ledger command/capability, or a complete authenticated
admitted-ingress proof bound to the registered environment and policy. These
are pending alternatives, not selected interfaces. A content hash or issuer
name alone is not authentication. The [current ingress contract](../../../CONTEXT.md)
records the raw-fact gap; no new producer-provenance implementation has begun.

The bounded ARCH-01 gate closes APPROVE. Its reviewer also records the unchanged
incomplete-binding presentation limit outside that static-rule scope. It does
not authorize another correction round. Dashboard and research work
remain stopped. The synthetic native foundation is not approved; full-chain
qualification cannot bypass unresolved authority prerequisites.

No staging, commit, push, branch change or live-provider invocation has occurred
in these rounds. Fresh reviewer configuration requests and backend-observability
limits are recorded separately in each report.
