# SPR-01-REFRESH — current-main planning refresh

**Date:** 2026-11-10 (Europe/Madrid). **State:** planning-only, unstaged;
implementation unauthorized. **Owner:** DEV under GRILL. Writer: gpt-6.1-sol;
actual reasoning effort is not exposed. Original scope started 03:46:33+01;
its 04:31:33+01 deadline expired during a credits outage, not continuous work.
The human explicitly requested continuation, routed by GRILL. Actual resumed
start: 10:22:39+01; new bounded closeout deadline: 10:47:39+01, inclusive of
review/transfer/handoff. No automatic successor or expanded implementation scope.
[Resume custody record](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/resume-20261110.json>).

This note supplements, never rewrites, the retained [implementation scaffold](IMPLEMENTATION.md),
[reviewed brief](.planning/SPR-01.reviewed.md) and [planning receipt](PLANNING-RECEIPT.json).
Their bytes, stale HEAD and index are frozen in the [custody baseline](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/sprint-baseline.json>).
The planning checkout remains `eddfa6d28ebcc6f2967c0568a6ed2d29eccf665e`;
it is not the integration base. No rebase, checkout, index or implementation
change is part of this refresh.

## Entry gate and actual base

Verified actual main: `d9eb84a04099431d774f459792bcd16524ab54ce`;
read-only remote confirmation at 2026-11-10 03:52:48+01. PR1 is merged.
PR2 remains a separate branch at `d97fadd4b84f1dee1d5b2434eb88030ec6146e31`,
not merged main. **PR2 independently approved and human-merged on actual main
remains the implementation entry gate.** Planning completion does not waive it.
After that prerequisite, GRILL must issue a finite new implementation dispatch
and provision/refreeze a dedicated base. Predecessor completion is not dispatch.

Release seam: H0 historical lifecycle/ingress, protecting H1 authority and later
H2 replay. The deterministic ingress issuer and common ledger remain owners;
the registry and Observatory are read-only projections. No H0/H1/O1/H2 closure
is asserted. No new runtime coordinator or second task store is proposed.

## Assumption crosswalk

| Old planning assumption | Actual-main observation | Planning consequence |
| --- | --- | --- |
| PR1 repair source missing from stale checkout | PR1 is merged on the fixed main above. | Do not redo PR1 repair or integrate old dirty runtime bytes. |
| Old inspected `0fd0917` plus selected dirty bytes are the source reference | Use [current-main source hashes](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/sprint-main-source.json>), not those historical hashes. | Refreeze again against post-PR2 main before implementation. |
| Resume/notify need a new ingress system | [TaskIngressAuthority.admit](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/control-main/src/ab_harness/task_ingress_authority.py#L135-L190>) already classifies both; [existing behavior/restart tests](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/control-main/tests/test_environment_ingress.py#L606-L803>) pass. | Preserve lineage, reasons and behavior; do not rebuild these features. |
| Resume/notify issuer-bound write hardening is automatically required | [Existing-task write](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/control-main/src/ab_harness/task_ingress_authority.py#L271-L339>) still records a raw task ingress fact; [start crossing](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/control-main/src/ab_harness/lifecycle.py#L627-L703>) uses an issuer-bound command. | This is source evidence, not a newly demonstrated exploit. Select hardening only after a public current-main rejection red and untouched accepted control. No repair is selected here. |
| Legacy replay failures may already have disappeared | Exact original two-event and accepted A/B fixtures all fail the public constructor with `compiled task requires budget limits` on actual main. | Historical replay gap is freshly reproduced; no compatibility implementation in this scope. |
| Referenced old briefs exist in product main | The original October 9 brief is absent from the coordination checkout/current main; retained copy exists in quarantine. | Link authenticated custody evidence, not nonexistent product paths or an invented merge. |

## Executed evidence (read-only, not qualification)

An archive of fixed main was used with the independently installed private
Python environment and copy-local `PYTHONPATH=src`. Existing ledger/ingress suites:
**89 passed**, [exact log](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/sprint-current-main-controls.log>).
This retains genuine resume/notify, duplicate, restart, cross-run and stale-writer
controls; it is not proof of an untested issuer-authentication boundary.

The [read-only fixture probe](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/probe-historical-fixtures.py>)
used unchanged original bytes in throwaway files, never current constructors
to manufacture history. [Fresh outcomes](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/sprint-fixture-probe-final.json>):
three historical inputs reject at missing budget limits; the eleven-event
retained current control opens, reopens and replays accepted. Its digest is
`verified-trace-digest:sha256:c26202fdaa0218e3fcb85fade644a386596fad117b0282c8f0088544a12fec27`.
Every probed file remains byte-identical. No fresh-use exploit, concurrent
resume/notify race or historical failed-execution qualification was executed.

## Authentic fixture inventory and explicit gaps

[Full archive/member custody and SHA-256 inventory](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/sprint-fixture-inventory.json>)
was recomputed this scope. Retained quarantine is evidence, not an integration base.

| Fixture | Exact SHA-256 | Custody / current observation |
| --- | --- | --- |
| Original start/compile, two events | `3fa6f142bc300f87b9653f8db7fadbdcae73223e7e29cd48e6880316ce91b5e5` | [Original JSONL](</home/juanbeck/uah-experiments/checkpoint-20261103/grill/quarantine/working-tree/docs/artifacts/reviews/2026-10-08_uah_no_mistakes_pilot_evidence/baseline-public-ledger.jsonl>); rejects missing budgets. |
| Accepted trace A, ten events | `4c0b970c1d2d0687745e9f2acf84b028b885f82bfd29f51b12218e7ddfb4f0b9` | Member `base-accepted.jsonl` of [Standards archive](</home/juanbeck/uah-experiments/checkpoint-20261103/grill/quarantine/working-tree/docs/artifacts/reviews/2026-10-09_uah_checkpoint_audit_evidence/standards-original.tar.gz>); rejects missing budgets. |
| Accepted trace B, ten events | `1994743080033c29ec7e93f5714e30da83373c52d32e8e4d2fe509261c609de7` | Member `base-nao-ledger.jsonl` of [Spec archive](</home/juanbeck/uah-experiments/checkpoint-20261103/grill/quarantine/working-tree/docs/artifacts/reviews/2026-10-09_uah_checkpoint_audit_evidence/spec-original.tar.gz>); rejects missing budgets. |
| Retained current control, eleven events | `dfef58c0a4827e2f584e9b23184ed4c458f717a0215ae68ec591e1b33baf43b3` | Member `current-nao-ledger.jsonl` of the [Spec archive](</home/juanbeck/uah-experiments/checkpoint-20261103/grill/quarantine/working-tree/docs/artifacts/reviews/2026-10-09_uah_checkpoint_audit_evidence/spec-original.tar.gz>); accepted with unchanged bytes. |

Trace A historical expected digest remains
`verified-trace-digest:sha256:c10fb8218a46f99184db39d0dd99dbb26c350a339a64836e57165f72ce501a3d`;
it was **not** newly achieved. Missing authentic historical failed-execution
fixture remains a gap. Do not synthesize old events with current constructors.
Locating one, or separately authorized pinned-historical-producer fake-owner
production, must route through GRILL. No producer was run here.

## Future discriminating tests before any selected repair

1. On the newly frozen main, re-run all four exact fixtures; compare original
   dictionaries, IDs, `data_json`, framing, causal parents, lineage, counts,
   statuses and original digest inputs. Historical absence means unavailable
   budget/failure policy, never zero/unlimited policy or invented actors/grants.
2. Preserve strict fresh-use rejection: unmarked legacy starts cannot authorize
   fresh compile, budget grant/consumption, dispatch, provider call, effect proof
   or retries. Reopening and O1 inspection must preserve original bytes.
3. Attack downgrade: stripped current budgets, unbudgeted new execution,
   incomplete current failure, counterfeit current markers, mixed legacy/current
   provenance, invalid hash/commit/framing. Reject without append or legacy downgrade.
   A shared v1 envelope alone is not sufficient legacy authentication.
4. Before considering issuer-bound resume/notify writes, test caller-created raw
   facts versus genuine `admit()` for both actions. Forged facts must append
   nothing; valid controls must retain exact task/trace/profile/pack/ingress and
   `matched_registered_task`. A green positive control is not a public red.
5. Test both actions across restart, duplicate ingress, two synchronized issuers,
   terminal acceptance interleavings, cross-run/profile/pack mismatch and unknown
   tasks. Exactly one duplicate winner; no post-terminal append. Suspended remains
   nonterminal. Do not newly prohibit issuer-admitted notifications on historical
   unmarked lineage: continuation-policy changes require GRILL decision.
6. Revalidate the decision inside the same lock/reload/reduce/append/flush/fsync
   critical section. Preserve stale sequence conflict behavior. Avoid recursive
   file-backed registry reads while locked. Registry stays a projection.
7. Resume/notify do not recompile, reset budgets, invoke providers or prove effects.
   Keep typed reasons and schemas; never infer missing identity from model output.

## Conditional future allowlist, gates and finite stop

Only after human prerequisites and a finite new GRILL dispatch, potential paths:
[ledger](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/control-main/src/ab_harness/lifecycle.py>),
[ingress issuer](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/control-main/src/ab_harness/task_ingress_authority.py>),
[ledger tests](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/control-main/tests/test_lifecycle_ledger.py>),
[ingress tests](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/control-main/tests/test_environment_ingress.py>),
exact authenticated fixture copies and minimal owning documentation.
[Registry](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/control-main/src/ab_harness/task_registry.py>)
changes require an evidenced lock-local need; no new writer interface.
Paths refer to inspected main snapshots, not permission to edit those copies.

One PR-sized repair only, chosen from reproduced current-main failures, with an
unchanged accepted control. Run focused public seams, package-boundary checks,
full deterministic tests, both O1 example checks, generated-doc synchronization,
whitespace and mandatory hooks in independent metadata. Freeze complete bytes
and obtain fresh independent reviews under [REVIEW.md](</home/juanbeck/uah-experiments/dsh-pilot-20261110/dev/control-main/REVIEW.md>).
Authority/gate work needs a second **different-model** reviewer. Only
gpt-6.1-sol/max is exposed now; two new contexts do not meet that requirement.
Stop for that limitation rather than relaxing review.

Stop after one bounded approved unit or report the concrete unresolved blocker.
At most one authorized correction batch and one changed-byte re-review; a new
unrelated blocker returns upward. No automatic repair/review loop or successor.
Exclude schema redesign, generic compatibility frameworks, ledger splitting,
crash/exactly-once claims, live providers, native adapters, H3/H4 work and broad
style churn. Preserve H0 synthetic replay and the eight H1 families (success,
invalid proposal, unavailable tool, timeout, cancellation, retry exhaustion,
stale evidence, false completion); NAO-first did not waive them. O1 preparation
can precede H2 parity, but final O1 closure consumes the parity run, not vice versa.

## Rollback and custody

Before transfer, withdraw only the private candidate and preserve evidence.
After any future human merge, rollback requires a human-authorized revert of
exact merged paths. Never rewrite old ledgers, shared history or another
writer’s work. This refresh preserves all existing drafts and index bytes.
Its only stale-worktree addition is this unstaged Markdown note.

## Reserved: GRILL-routed FPV considerations

Await bounded research synthesis routed by GRILL; no RESEARCH child was contacted.
Record any later proposal here only with its source/evidence limits. This section
adds no prerequisite, implementation permission or unsupported FPV-H2 claim.
The present SPR-01 gate remains replay/ingress evidence, not FPV expansion.

**GRILL-routed addition, 2026-11-10 (supersedes the awaiting status above): proposal
only.** Preserve NAO-first Python H2 and SPR-01→07 prerequisites. FPV is a
separately selected **post-NAO fake-goal cross-domain pilot**, not a new SPR-01/H2
gate, flight qualification or current implementation scope. Reuse replay, ingress
and identity discipline; later freeze `fpv_flight` frame/registry/DomainContractPack,
explicit authority mode, deterministic fake owner/reset/clock, outcome/evidence/
parity evaluator and lineage, budgets/cancel/late settlement, exact source/config/
license/rollback and **zero hardware authority**. A started operation followed by
cancel acknowledgement and late success must not dispatch its successor before
truthful owner settlement; deduplicate this future case against existing SPR-05/06
rows rather than expanding SPR-01. P1a readiness, P1b fake authority/evidence and
P2 SITL are distinct evidence gates; no runtime receipts are claimed here.

Sources: GRILL-routed [unreviewed FPV/NAO memo](</home/juanbeck/uah-experiments/dsh-pilot-20261110/research/fpv-nao-memo.md>);
FPV proposed-head `dc69e344e7a604c9efe687591310072e4bea0070` pinned primary
[ownership and phase plan:11–49](</home/juanbeck/uah-experiments/dsh-pilot-20261110/research/fpv-docs--plans--p0-p2-implementation.md#L11-L49>),
[public verification/version gates:53–67](</home/juanbeck/uah-experiments/dsh-pilot-20261110/research/fpv-docs--plans--p0-p2-implementation.md#L53-L67>),
[G0 subgates:23–29](</home/juanbeck/uah-experiments/dsh-pilot-20261110/research/fpv-docs--plans--g0-flight-freeze.md#L23-L29>)
and [freeze/evidence ownership:42–58](</home/juanbeck/uah-experiments/dsh-pilot-20261110/research/fpv-docs--plans--g0-flight-freeze.md#L42-L58>).
These are private source/proposal records, not permission to vendor/publish them
or proof of executed UAH/flight behavior. PR2 reviewed product bytes are unchanged.
