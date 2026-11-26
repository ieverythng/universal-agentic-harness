<!-- Local planning scaffold; not a published product change. -->

Planning checkout: `codex/sprint-02-contract-budgets` at `eddfa6d28ebcc6f2967c0568a6ed2d29eccf665e` (main).
Predecessors must be reviewed, human-merged and this branch rebased/refrozen
before implementation. This checkout does not contain unmerged PR1 source.
Reviewed brief: [SPR-02](/home/juanbeck/universal-agentic-harness/docs/plans/pr-sprints/SPR-02-contract-and-budget-coverage.md); documentation approval and exact
source identity are recorded in `PLANNING-RECEIPT.json`.

# SPR-02: canonical contract and exact-budget coverage

Status: `planning-only`; readiness: `blocked_predecessors`.
Target repository: Universal Agentic Harness (UAH).
Proposed branch: `codex/sprint-02-contract-budgets`.
Future worktree key: `sprint-02-contract-budgets`.
Gate: H0 contract coverage and H1 budget controls. H0 target v0.2; H1/O1
v0.3-v0.4; complete Python H2 v0.5; native H2.1 v0.6; H3 spans v0.7-v1.0.
Controlling D-20261017-07 targets H4 v1.5; H5+ versions remain unassigned.
These human-approved targets are not achieved gates or repository tags.

## Entry and owners

PR1 must be independently approved and human-merged into verified main; PR2
documentation must exist on actual main, without requiring dirty source.
SPR-01 must also be approved and human-merged before this sprint starts.
The parent provisions the future worktree from verified main and freezes its
revision. Do not implement from this selected-dirty planning snapshot or treat
PR1's open three-bug/resumed predecessor repair as completed here.
DEV owns implementation/reviews; GRILL owns unresolved contract policy.
TaskBudgetAuthority owns call debit semantics; existing artifact owners own
canonical serialization; environment owners retain effect truth. Human staging,
commits and pushes are separate authority, not granted by this plan.

## Evidence and exact inspected references

HEAD: `0fd09174e95c536b44bcc22bace8f462cf5b58de` plus selected dirty bytes.
Reuse [October 9 exact-unit brief](/home/juanbeck/universal-agentic-harness/docs/artifacts/research/2026-10-09_uah_historical_replay_and_resume_notify_seam_briefs.md)
(`ba9cd1e6e2c762034d1b72a2f59a040d489a82e83ca6987051887b5ab4445e91`),
[October 11 seam design](/home/juanbeck/universal-agentic-harness/docs/artifacts/decisions/2026-10-11_uah_mechanical_seam_design.md)
(`582d4bf854ed4924bafc49a97789135782634c5b590eec190a8d13bdf319abf1`)
and [approved October 17 dossier](/home/juanbeck/universal-agentic-harness/docs/artifacts/research/2026-10-17_uah_history_recovery_workbench_evaluation_and_nao_seams.md)
(`71507e55c42f045fa50dcc35f6318c42e864a19f18fc7e23590b369b616cf796`).
The last dossier pins governing dirty documents and settled SOURCE-PACK-01;
neither prompt issuance nor source retention is reopened by this sprint.

| Source path / owner | Inspected SHA-256 |
| --- | --- |
| `src/ab_harness/runtime_controls.py`, budget authority | `ddf5a85a0722606ddb1e6622f74dbfbaba7eea112f74322600be4c797fea6aa7` |
| `src/ab_harness/task_compiler.py`, TaskSpec/CompiledTask | `b11625e4cb5a64f74327e2112a6e182b48e45ce9821135a5af39a9f36f92e9bf` |
| `src/ab_harness/contracts.py`, portable values | `bacb7c0098851ffd4235000005a86dc3d519cf099ee9f9e86633f29e0419047d` |
| `src/ab_harness/domain_contracts.py`, domain pack | `b47e522c1184786170df1d9f3bbbfb7398c340e44a7b44a514312a8da17baf1c` |
| `src/ab_harness/environment_profiles.py`, profile owner | `9f63227dbe37c0421e3d76bd8581d245e89176dbcbb1fa68e1841eb053784584` |
| `src/ab_harness/schema_validation.py`, argument validator (selected dirty) | `6512a14cf5b203b6b39b5b624ef9e76ebd87944af1c3ff354be7fa352d4bc292` |
| `src/ab_harness/environment.py`, lease-only result/evidence owner | `9fd718a1d663dcc2bfe844a4b289f4191aaa90f520fe36215df5331e52047248` |

## Bounded guided TODOs

1. Record a compact owner/contract coverage table against verified main before
   edits. Mark implemented, tested, proposed and unknown separately. Cover
   HarnessSpec, TaskSpec/CompiledTask, ModelProfile/ModelConfiguration,
   EnvironmentProfile/run/ingress, AB views/bindings, proposal/admission,
   execution receipt/evidence and trace schemas. Do not equate target grammar
   with an implemented serializer or conflate ModelProfile with configuration.
2. For implemented contracts, map exact schema constants, canonical encoding,
   exporter/loader, identity verifier, compatibility policy and every consumer.
   Add missing public round-trip/version/tamper controls in existing tests.
   Preserve historical v1 identity and SPR-01's strict fresh-use distinction.
   Unsupported versions reject; no `latest`, coerced defaults or generic codec.
3. First reproduce `True == 1 == 1.0` reuse through public budget interfaces.
   Validate `type(units) is int` and `units > 0` at `assess()` entry, before
   ledger lookup, existing-subject equality or arithmetic. `consume()` retains
   delegation. Preserve `ValueError`, exact-request identity and debit policy.
4. Trace TaskBudgets fields and budget decision quantities through compilation,
   persistence, replay and consumers. Quantities remain exact integers;
   wall time is positive, model/tool/retry limits are nonnegative. Decision
   units are positive; limit and consumption are nonnegative. Do not change
   limits or invent token/cost accounting to fill absent fields.
5. Add bounded controls at existing input-schema, owner-result/evidence and
   acceptance interfaces. Record output-schema resolution/validation coverage
   explicitly. An output schema reference alone is not validation, and valid
   output is not effect evidence. Unknown freshness/output semantics require
   an owner decision before new enforcement, not a broad inferred validator.
6. Change only the demonstrated budget entry defect and minimal missing
   existing-contract checks supported by frozen policy. If another row needs
   a new serializer, version, evidence policy or abstraction, report a separate
   owner-scoped follow-up rather than expanding this PR.

## Public end-to-end red, control and restart cases

| Case | Expected outcome |
| --- | --- |
| `assess` and `consume`, model/tool resources, fresh and existing subjects, `True`/`1.0` | `ValueError` before lookup/reuse; ledger bytes, events and debit unchanged. |
| Exact `units=1` reuse after file-ledger reopen | Same decision ID; no extra grant/debit. |
| Existing subject changes to `2`; `0`, `-1`; fresh positive integers at limit and over limit | Existing immutability/positivity errors; valid grant then exhaustion, no over-limit debit. |
| Two competing valid consumers for one subject | One grant identity/event; no double debit; reopen preserves consumption. |
| Admitted-operation tool fixture and ready-actor fake invocation | Atomic call accounting before dispatch; rejected quantity makes zero handler/provider calls. |
| Implemented contract export/load/export and identity check | Same canonical content/identity after restart; unsupported version, mutation and nonfinite values reject where contract requires. |
| Public semantic admission with invalid input schema, absent resolver or mismatched binding revision | Fail closed without lease/execution; stable rejection evidence. |
| Owner receipt/evidence mismatch, foreign owner/binding/result or model success text without owner evidence | No accepted effect or required-obligation closure; replay retains rejection. |
| Matching owner evidence; required missing effect versus best-effort deficit | Valid control accepted; missing required effect does not pass; allowed best-effort deficit retained. |
| Declared output-schema row lacking executable validation | Coverage remains explicitly open; no false H0-complete label. |

Use existing public tests, not source-text assertions or a second fixture
framework. The recorded numeric defect demonstrated reuse, not extra debit;
retain that evidence's narrow classification rather than claim escalation.

## Acceptance and one-PR stop

Allowlist implementation starts with `runtime_controls.py` and existing
`tests/test_runtime_budget_contracts.py` / `tests/test_lifecycle_ledger.py`.
Coverage controls may extend existing core/compiler/argument-schema,
two-stage-admission and task-acceptance tests. Other owner source changes
require a reproducible frozen-policy gap and explicit path-manifest review.
Run red cases on verified base, then focused tests for affected owners,
content-identity compatibility, package boundaries, renderer `--check`,
`git diff --check` and `./scripts/run_precommit.sh` in isolated setup.
Fresh independent review follows `REVIEW.md`, including a second different-model
reviewer for budget/validation gates. Bind exact path hashes and check inputs.
Stop at one reviewed PR with exact-unit repair and truthful contract coverage;
the table may retain blocked rows. Do not advertise completion of all H0 schemas.

## Decisions, exclusions and rollback

Owner decisions remain for unimplemented output/freshness contracts, missing
serializer/version policies and complete token/USD/descendant envelopes.
Do not reset budgets on restart, standby, resume or lease release. O1 reads
accounting; it cannot enforce a missing spend contract or write lifecycle facts.
Preserve all eight H1 families: success, invalid proposal, unavailable tool,
timeout, cancellation, retry exhaustion, stale evidence and false completion.
No weaker CLI milestone substitutes for Python H2 or native H2.1 integration.
No generic numeric refactor, new resource enum, ledger/store, runtime rewrite,
live provider/robot calls, H3 crystallization or entropy search is included.
Rollback withdraws the candidate or uses a human-authorized exact-path revert;
never alter historical ledger identities, restore missing policy as defaults,
or reset shared work. Preserve receipts and route new decisions upward.
