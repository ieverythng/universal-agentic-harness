<!-- Local planning scaffold; not a published product change. -->

Planning checkout: `codex/sprint-01-replay-ingress` at `eddfa6d28ebcc6f2967c0568a6ed2d29eccf665e` (main).
Predecessors must be reviewed, human-merged and this branch rebased/refrozen
before implementation. This checkout does not contain unmerged PR1 source.
Reviewed brief: [SPR-01](/home/juanbeck/universal-agentic-harness/docs/plans/pr-sprints/SPR-01-historical-replay-and-ingress.md); documentation approval and exact
source identity are recorded in `PLANNING-RECEIPT.json`.

# SPR-01: historical replay and authority-bound ingress

Status: `planning-only`; readiness: `blocked_predecessors`.
Target repository: Universal Agentic Harness (UAH).
Proposed branch: `codex/sprint-01-replay-ingress`.
Future worktree key: `sprint-01-replay-ingress`.
Gate: H0 lifecycle/ingress, protecting H1 execution controls. Target H0 v0.2;
H1/O1 v0.3-v0.4, complete Python H2 v0.5, native H2.1 v0.6 and H3 v0.7-v1.0.
Controlling D-20261017-07 targets H4 v1.5; H5+ versions remain unassigned.
These are human-approved delivery targets, not qualification, tags or completion.

## Entry and custody

PR1 must receive independent approval and be human-merged into verified main.
PR2 documentation must be present on actual main; this does not require source
to be dirtied. No additional sprint dependency applies. The parent provisions
the future worktree from that verified main and records its exact revision.
This private planning snapshot is not an implementation starting point or a
claim that unmerged source is runnable. PR1's reported three blocking bugs and
the resumed PR1-REPAIR-02 candidate remain predecessor work, not this sprint.

DEV owns implementation and independent-review coordination. GRILL owns new
policy decisions; lifecycle and ingress retain runtime ownership below.
The human owns shared staging, commits and pushes. This brief authorizes none.

## Frozen evidence and inspected bytes

Inspected HEAD: `0fd09174e95c536b44bcc22bace8f462cf5b58de` plus selected dirty
bytes, not accepted main. Historical producer: `06f5a29daef9bb877fb08b6c6ee47d870df94d71`.
Reuse the [October 9 replay/ingress brief](/home/juanbeck/universal-agentic-harness/docs/artifacts/research/2026-10-09_uah_historical_replay_and_resume_notify_seam_briefs.md),
[October 11 design](/home/juanbeck/universal-agentic-harness/docs/artifacts/decisions/2026-10-11_uah_mechanical_seam_design.md)
and [approved October 17 dossier](/home/juanbeck/universal-agentic-harness/docs/artifacts/research/2026-10-17_uah_history_recovery_workbench_evaluation_and_nao_seams.md).
Their respective SHA-256 values are `ba9cd1e6e2c762034d1b72a2f59a040d489a82e83ca6987051887b5ab4445e91`,
`582d4bf854ed4924bafc49a97789135782634c5b590eec190a8d13bdf319abf1`,
and `71507e55c42f045fa50dcc35f6318c42e864a19f18fc7e23590b369b616cf796`.

| Source path / owner | Inspected SHA-256 |
| --- | --- |
| `src/ab_harness/lifecycle.py`, ledger/reducer (selected dirty) | `c6876a51762a194c7cdc69b223a5cc57e8e2ca014f7601817749c90860b62b97` |
| `src/ab_harness/task_ingress_authority.py`, ingress issuer | `d38a56709c6b93b61750abb717dedfa72dcabeab94c3cc0039d48dc2fd48dc7a` |
| `src/ab_harness/task_registry.py`, read-only lineage | `e0cd048a2752387846477f18eb26ae3f2b3a23d81e11b8e36acb6aaa230800ef` |

The October 17 selected-byte manifest pins governing dirty documents and settled
prompt-source implementation. Preserve SOURCE-PACK-01; do not reopen issuance.
Recheck actual-main bytes before implementation and report changed assumptions.

## Interface and finite TODOs

1. Freeze failing public tests through `LifecycleLedger(path)`, `events()` and
   `replay(trace_id)`. Copy exact retained historical JSONL, verify its hashes,
   and retain a current accepted control. There is no public `load()` method.
2. Deepen historical reduction only for evidenced old `task_compiled`,
   `execution_started` and, when authenticated fixture evidence exists,
   `execution_failed` shapes. Missing budgets/failure policy stay unavailable.
   Preserve event dictionaries, IDs, `data_json`, framing, causal lineage,
   lease ordering and recorded digest inputs. Never synthesize grants or actors.
3. Preserve strict active-write reduction (`active_from_sequence`) and reject
   mixed current-provenance/legacy projections. Historical unmarked starts stay
   readable but cannot authorize fresh compilation, dispatch or provider work.
4. Extend the existing private authority-bound start-command mechanism to
   resume/notify, binding issuer capability, exact ledger, ingress, decision,
   action, environment/profile, frozen rule/pack and registered task/trace.
   Reject caller-created raw `TaskIngressFact` at the write crossing.
5. Revalidate duplicate/terminal state under the ledger's existing single
   lock/reload/reduce/append/flush/fsync critical section. Avoid recursive
   file-backed registry reads while locked. Keep the registry a projection.
6. Migrate only bypass-dependent positive raw-fact helpers to public `admit()`;
   retain raw facts as rejection controls. Keep event schemas/reasons and
   `matched_registered_task`; suspended is nonterminal. Resume/notify do not
   recompile, reset budgets, invoke providers or prove effects.

## Public end-to-end red, control and restart cases

| Case | Expected outcome |
| --- | --- |
| Original two-event fixture `3fa6f142bc300f87b9653f8db7fadbdcae73223e7e29cd48e6880316ce91b5e5` | Opens with two unchanged events, open status, no digest. |
| Accepted trace A `4c0b970c1d2d0687745e9f2acf84b028b885f82bfd29f51b12218e7ddfb4f0b9` | Ten unchanged events; accepted; original digest retained. |
| Trace B `1994743080033c29ec7e93f5714e30da83373c52d32e8e4d2fe509261c609de7` and current control `dfef58c0a4827e2f584e9b23184ed4c458f717a0215ae68ec591e1b33baf43b3` | Corroborating old trace and eleven-event current trace remain accepted. |
| Reopen twice; inspect via O1; attempt fresh use of legacy missing policy | File unchanged; no fresh compile/grant/dispatch/provider call. |
| Stripped current budgets, unbudgeted current execution, incomplete current failure, forged marker, malformed hash/commit | Reject without historical downgrade or append. |
| Forged raw resume/notify versus genuine authority ingress, both actions | Forgery appends nothing; valid ingress records one exact-lineage event. |
| Recreate authority/registry over file ledger; repeat ingress | Association survives restart; duplicate rejects with no second event. |
| Two synchronized issuers submit same ingress; terminal acceptance wins interleaving | Exactly one ingress event; loser duplicate; no post-terminal event. |
| Cross-run/profile/pack mismatch, unknown task; real suspended task | Negatives reject; suspended lineage resumes without identity/budget reset. |
| Stale ledger instance appends after another writer's new current task | `LifecycleSequenceConflict`; refresh sees event once, old prefix unchanged. |

Trace A digest: `verified-trace-digest:sha256:c10fb8218a46f99184db39d0dd99dbb26c350a339a64836e57165f72ce501a3d`.
Archive/member provenance and genuine fixture locations remain in the October 9
brief. Historical acceptance reports history, not present execution qualification.

## Acceptance, checks and stop condition

One PR contains only the ordered replay/ingress repair and required tests/docs.
Allowlist: `lifecycle.py`, `task_ingress_authority.py`, existing
`tests/test_lifecycle_ledger.py`, `tests/test_environment_ingress.py`, exact
historical fixture copies and necessary owner documentation. `task_registry.py`
changes require a demonstrated lock-local need; no second write interface.
Run public red tests on verified base, then focused ledger/ingress tests,
package-boundary tests, renderer `--check`, `git diff --check` and
`./scripts/run_precommit.sh` in isolated setup. Preserve all existing negatives.
Fresh reviews follow `REVIEW.md`; high-risk authority changes need a second
different-model reviewer. Record exact bytes, manifests, verdicts and receipts.
Stop after one approved PR-sized unit; report remaining evidence gaps upward.

## Unknowns, exclusions and rollback

No authentic old failed-execution ledger was found in the cited archives.
Locate one or obtain GRILL authorization for pinned-producer fake-owner fixture
production; never reconstruct history with current constructors. Leave that
qualification open if unavailable. Do not newly ban issuer-admitted notification
against historical unmarked lineage; changing continuation rights needs GRILL.
No schema redesign, generic compatibility framework, ledger split, new store,
crash/exactly-once claim, native adapter work, live calls, H3 crystallization or
entropy search. Retain all eight H1 families: success, invalid proposal,
unavailable tool, timeout, cancellation, retry exhaustion, stale evidence and
false completion. A smoke CLI cannot replace Python/native H2 qualification.
Rollback withdraws this candidate before transfer, or uses a human-authorized
revert of exact merged paths. Never rewrite historical ledger bytes or reset
the human's shared worktree; preserve current strict-write behavior and receipts.
