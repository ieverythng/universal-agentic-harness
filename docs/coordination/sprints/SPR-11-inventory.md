# SPR-11 startup state inventory

**Date:** 2026-11-10. **Baseline:** merged main `d9eb84a`.
**Evidence status:** source survey and selected public controls, not independent
implementation approval or release qualification. The core lane inspected
existing tests but did not execute them. The surrounding-seam lane executed
19 controls and in-memory diagnostic probes. Repository hooks ran separately.

The path [coverage manifest](SPR-11-coverage.json) classifies all 31 portable
source modules plus tracked wrapper/tool/UI entry paths. Classification means
these paths were inspected or mapped to the owning machine, not that every
transition or hidden machine has been discovered. External NAO/Workbench
implementation, synchronized process races, crash/fsync schedules, live
providers and production recovery remain outside this startup's proof.

## Portable state families

| ID | State carrier and transition concern | Owner and route |
| --- | --- | --- |
| S01 | Ledger sequence, commit framing, causal tails, lock/reload/reduce/append | LifecycleLedger; SPR-01/05/06 |
| S02 | Ingress rules, task and ingress identity maps, duplicate and terminal fences | TaskIngressAuthority plus ledger; SPR-01 |
| S03 | Compile-once marker, active versus historical provenance | Compiler plus ledger; SPR-01/02/03 |
| S04 | Normalized/rejected operation identity and nonterminal failure stage | Normalizer plus ledger; SPR-02/05 |
| S05 | Semantic admission, pinned object/binding snapshots and current provenance | SemanticAdmission plus ledger; SPR-02/04 |
| S06 | Leased operation set and exact lease reuse | DomainLifecycleAdmission plus ledger; SPR-05/07/08 |
| S07 | Started/settled/evidence-issued or rejected operation sets and receipts | Environment effect owner plus ledger; SPR-04/05/06 |
| S08 | Obligation satisfaction, suspended state, terminal judgment and deficits | Acceptance evaluator plus ledger; SPR-04/05/06 |
| S09 | Subject identity, monotone budget debit and grant/start joins | TaskBudgetAuthority plus ledger; SPR-02/05/06 |
| S10 | Recorded-time deadline, monotone observation and timeout fence | Runtime control authority plus ledger; SPR-05/06 |
| S11 | Failure identity, retry ordinal and reserved target identities | RetryAuthority plus ledger; SPR-05/06 |
| S12 | Admitted operation graph, cycle/parent/order constraints | Typed edge contract plus ledger; SPR-07/08 |
| S13 | Role/model/manifest/initial-handle publication maps | Registries; SPR-02/05; later H3 rebinding separate |
| S14 | Environment profile/run maps and consumed attestation identities | Environment registry and native owner; SPR-05/07/08 |
| S15 | Actor roster, attachment, refreshed projection and idle termination | AgentRunRegistry plus ledger; SPR-05/06 |
| S16 | Exclusive model reservation, startup readiness, release to standby | FixedModelAllocator/readiness owner plus ledger; SPR-05/06 |
| S17 | Invocation identity, ready/invoking state and settled outcomes | ModelInvocationAuthority plus ledger; SPR-03/05/06 |
| S18 | Pinned source/schema/binding maps and graph-closure traversal | Configured owners and deterministic consumers; SPR-02/03/04 |
| S19 | Advisory experience tuple and compatible/degraded handshake | Workbench engine/host seam; SPR-10 then SPR-09 |
| S20 | Derived trace/actor grouping, terminal display and browser filters | Read-only Observatory; SPR-04/06 |

These families include explicit and implicit state. Immutable eligibility
values and per-call graph traversal are supporting mechanisms, not automatic
new lifecycle owners. LifecycleLedger already has depth: its public write and
replay interface concentrates ordering and persistence. A generic FSM module
would spread domain policy rather than improve locality.

## Surrounding machines and candidate disposition

| Observation | Confidence and route | Next discriminating probe |
| --- | --- | --- |
| Malformed NAO plan returns normalization failure after admitted start; O1 retains an open prefix with no corresponding diagnostic stage. Reusing the ingress is fenced. | Reproduced diagnostic difference; production harm and desired continuation not established. SPR-04/07, recovery SPR-05. | Freeze owner policy for refusal visibility and allowed continuation; never infer terminal rejection. |
| Workbench nested request mutation, differing batch source and repeat observation delivery are possible through current advisory transport. | Reproduced limitations; host qualification/dedup are already deferred SPR-10/09 work. No demonstrated effect-authority bypass. | Frozen source/history cut and duplicate/reopen observation controls after predecessors. |
| Hook readiness spans venv, wrapper, delegate and success receipt. Shared metadata custody and interrupted install are not covered by inspected tests. | Hypothesis/coverage gap, distinct tooling candidate for SPR-11. | Disposable shared-common-directory and interrupted-install/rerun controls; preserve human hooks. |
| Ledger and invocation durable starts can precede missing external settlement. | Existing uncertainty/coverage gap, SPR-05/06. | Fake-owner loss at each start/effect/append point; reopen and count calls, effects and debit. |
| Resume/notify issuer structure, numeric budget alternatives and same-operation rejection revision require additional public or policy oracles. | Source hypotheses already routed to SPR-01/02/04; no new exploit claim. | Use existing sprint red/control requirements, with owner decision before changing rejection semantics. |

Build-output cleaning and hosted CI step/matrix state are recorded separately
from runtime lifecycle; a successful build/job does not qualify a release.
Renderer publication state, CLI diagnostic exit and coordination delivery state
remain separate from runtime authority. Browser filter/enhancement state changes
visibility only. No new installer wrapper, second task store, lifecycle plugin
or review authority is supported by the deletion test.

## Next decision

Keep runtime observations with their existing sprint owners. The distinct
SPR-11 candidate is a disposable hook-custody/interruption investigation.
Human selection through grill-me precedes interface design or repair. The
[finite sprint brief](SPR-11-state-machines.md) retains PR2 and review gates.

Private detailed source citations, commands and unreviewed research reports
remain under `/home/juanbeck/uah-experiments/orca-state-machines-20261110/`;
raw traces and private receipts are excluded from product delivery.
