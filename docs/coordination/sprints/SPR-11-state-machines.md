# SPR-11: implicit state machines and transition ownership

**Date:** 2026-11-10. **Status:** startup discovery active; production
implementation blocked on predecessors and candidate selection.
**Coordinator:** Orca GRILL. **Repository:** Universal Agentic Harness.
**Branch:** `codex/sprint-11-state-machines`.
**Worktree:** `/home/juanbeck/.codex/worktrees/sprint-11-state-machines/universal-agentic-harness`.
**Planning base:** main `d9eb84a04099431d774f459792bcd16524ab54ce`.
No sprint staging, commits or pushes are authorized by this brief.

## Contract and purpose

Inventory explicit and implicit state machines, including event order, Boolean
flags, presence in maps/sets, consumed identities and derived projections.
An implicit state machine is a behavior whose legal next action depends on
prior actions even when no enum or transition table names that dependence.
A status field or pure validator alone does not establish a state machine.
Finding a machine is not finding a defect or requiring an FSM framework.

The governing contracts are root AGENTS.md, CONTEXT.md, REVIEW.md, the UAH
guardrails and stack iteration skills, canonical masterplan, foundation,
Observatory contract and semantic-object ADR. H0/H1/O1 owners remain the
deterministic ledger, ingress, admission, allocation, invocation, environment
and acceptance owners. H2 belongs to the NAO contract owner; Workbench remains
H3/H4 proposal-only. No release gate closes through this audit.

## Coverage and non-goals

Survey tracked Python source, adapters, executable scripts, examples, tooling
and JavaScript assets; inspect tests and canonical docs for transition claims.
Record each path as stateful, supporting a machine, stateless, generated,
historical or not inspected. Cross-repository NAO/Workbench implementations
require separate owner dispatch; their contracts can be mapped here without
claiming exhaustive external-source coverage. Dependencies, Git internals,
virtual environments and vendored packages are excluded.

Do not add a generic state-machine engine, second lifecycle store, speculative
adapter interface, compatibility path, or file-size-driven extraction. Keep
LifecycleLedger as the sole public lifecycle write/replay interface. Models
propose, deterministic owners admit, and environment owners prove effects.
Registry discovery, UI labels and coordination states confer no authority.
No live provider, hardware, model tuning, promotion or autonomous successor.

## Existing sprint routing

| Family | Existing owner scope | SPR-11 contribution |
| --- | --- | --- |
| Historical replay, ingress and deduplication | SPR-01 | Transition inventory and current-main counterexamples; preserve authentic fixtures. |
| Contracts, binding eligibility and budgets | SPR-02 | State-dependent contract cases, missing illegal transitions and exact thresholds. |
| Task/context persistence | SPR-03 | Original-versus-derived continuity and restart requirements. |
| Evidence, acceptance and O1 projection | SPR-04 | Distinguish terminal outcome from failure stage; expose projection drift. |
| Actor/model lease, invocation, interruption and accounting | SPR-05 | Cross-machine ordering, unfinished work and late settlement. |
| Qualification and conformance | SPR-06 | Transition coverage matrix and independent behavioral oracles. |
| Python/native NAO authority modes and parity | SPR-07/08 | Map wrapper state and external owner gaps; no native repair dispatch. |
| Workbench protocol, retrieval, host and promotion | SPR-10 then SPR-09 | Candidate/quarantine and terminal-observation ordering; no promotion. |
| Repository hook cache and coordination delivery | Repository tooling/GRILL | Separate tooling behavior and human Git authority from runtime qualification. |

SPR-11 does not change SPR-01..10 dependencies or claim their work. Existing
findings retain their IDs. A new cross-machine defect receives `SM-###`, one
authoritative owner, and either an existing-sprint route or a separately
selected bounded SPR-11 repair. GRILL resolves overlap before any DEV edit.

## Finite phases and blockers

1. **Discovery (current):** one core RESEARCH and one surrounding-seam Explore
   pass, each at most 15 minutes. Record states, transitions, storage, owner,
   public interface, allowed control, forbidden action, restart/replay and
   concurrency coverage. Reports are hypotheses/observations, not review.
2. **Selection:** GRILL consolidates evidence and presents architecture
   candidates; the human selects a candidate through grill-me before interface
   design. Missing source or policy choices remain explicit blockers.
3. **Public red:** after verified human-merged PR2 and fresh main provisioning,
   DEV freezes one bounded owner scope and a failing public behavioral probe
   with an untouched valid control. A coverage gap alone is not a bug.
4. **Owner repair:** TDD through the public interface, minimum change with
   behavior, restart, replay/digest and competing-writer checks as applicable.
   One scope at a time; no automatic following round.
5. **Review and handoff:** Standards, Spec and architecture/O1 scopes as
   applicable under REVIEW.md; fresh fix review and different-model high-risk
   coverage. Full hooks, examples and synchronized canonical docs. Exact
   approved bytes transfer unstaged to a dedicated main-based PR worktree
   after per-path/index collision checks. The human owns product publication.

## Evidence record and acceptance

Each machine record names source revision/lines, state carrier, initial/terminal
states, transitions and guards, authoritative writer, read-only projections,
public executable probes, oracle, observed result, existing finding overlap,
release gate, owner, next probe and remaining gap. Mark findings `reproduced`,
`coverage_gap`, `hypothesis` or `not_scored`; inventory completeness is a separate
claim. Preserve timeout, cancellation, stale evidence, retry exhaustion, unknown
settlement and false completion as distinct typed outcomes.

Startup exits with a path coverage manifest, machine inventory, candidate
report, isolated planning scaffold, updated coordination and a documentation
follow-up. A partial survey must name exclusions and never claim all machines
were found. Product repair exits require the selected red/control, independent
approval for exact hashes and full required evidence; a merged PR or successful
command alone does not qualify H0/H1/O1/H2.

## Documentation and commit structure

Edit canonical `docs/plans/universal_agentic_harness_masterplan.md` and its
development log for accepted status/behavior changes, then regenerate listed
HTML. `docs/agentic_harness/universal_agentic_harness_masterplan.html` remains
the legacy redirect to the canonical plan. Research-to-sprint and PR status
notes distinguish historical observations from the new audit.

Coordination history is committed/pushed only on `coordination/orca`, as the
human explicitly requested. Proposed sprint/product commits for the human:
planning freeze; one tested owner repair; exact reviewed docs/evidence handoff.
Do not mix parent boards, raw probes, private archives or unrelated PR2 bytes
into a product commit. Refreeze against post-PR2 main before implementation.
