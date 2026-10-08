# Synthetic notes: public-path integration contract

Date: 2026-10-08. Status: integration plan with a native owner foundation under
independent review returning CHANGES; not an executed full-chain qualification.
Owner: H1 synthetic environment fixture. Release order remains in the
[masterplan](universal_agentic_harness_masterplan.md). The accepted task oracle
requires both a historical write and valid current content at closure. Content
correctness means exact task-defined text or schema constraints; it does not
mean model-authored assessment of semantic quality.

## Protected boundaries

The current H1 actor example ends after fake-provider raw output. It does not
write a note, prove an effect or accept a task. This plan extends a separate
fixture rather than relabeling that example. It must use public task ingress,
not directly record a fabricated task-start fact. A provider response or
finish reason proves neither mutation nor correctness. Every temporary workspace
belongs to the fixture and is deleted after execution.

At this plan's initial checkpoint, the admission catalog repair remained
incomplete at execution. Its
[public counterexample](../artifacts/reviews/2026-10-08_uah_r2_catalog_semantic_fencing.md)
required repair under the human-selected semantic-snapshot contract before
integration could qualify that crossing. Subsequent scoped approvals for
catalog fencing, ledger integrity and static eligibility are recorded in the
[follow-up index](../artifacts/reviews/2026-10-08_uah_review_followup_status.md).
Raw task-start producer provenance remains unresolved. The fixture must not
bypass that prerequisite to obtain a successful terminal result.

## Native foundation checkpoint

The [R5 round](../artifacts/reviews/2026-10-08_uah_r5_owner_local_foundation.md)
adds `ab_harness_synthetic` outside the portable core. Its frozen oracle retains
the full compiled-task body and trusted fixture text before model output. The
native owner writes actual bytes and records historical occurrence separately
from one designated closure-content observation. Retained bodies permit replay
without rereading the live workspace. A single owner instance fences its own
writes during and after the closure callback, including callback failure.
Independent review reproduces a second public owner instance bypassing that
fence. Review also finds stale nested compiled-task identities accepted during
retained-body reconstruction, and a hardlink mutation outside the workspace.
The frozen candidate is not approved and no automatic repair follows this round.

Callback completion does not prove a ledger commit or terminal acceptance.
These observations are not authenticated receipts or admitted effect evidence.
This slice has no lease-only execution adapter, domain contract pack, provider
invocation, lifecycle acceptance, restart replay or O1 integration. Those remain
the proposed chain below. The oracle is content-addressed, not authenticated;
trusted fixture ownership and retained reference provenance remain assumptions.

## Proposed vertical chain

```text
registered environment profile and attestation
  -> public TaskIngressAuthority
  -> TaskSpecCompiler and frozen task constraints
  -> attached agent run, fixed-instance lease, owner readiness
  -> PromptCompiler and fake ProviderPort invocation
  -> raw output and typed normalization
  -> semantic admission and domain execution lease
  -> temporary-workspace owner mutation and historical receipt
  -> independent owner read at closure and exact-content assessment
  -> deterministic task acceptance
  -> file-backed restart, equivalent trace and digest, read-only O1
```

The write observation and closure observation remain separate facts. Altering
the file after a successful write cannot erase that write's receipt. It must
prevent acceptance when current content violates the frozen task constraint.
Missing or uncertain evidence cannot be replaced by model narration.

The current compiler projects every requested effect's owning object. The
synthetic domain can therefore declare separate write and verify objects as
two roots in the same `synthetic_notes` frame, without inventing an AB2 parent
or changing the compiler. Existing lifecycle grammar permits one evidence
issuance per operation. Use separately admitted/leased write and final verify
operations with distinct receipts; acceptance must include the complete recorded
evidence set. Core acceptance does not inspect payload predicate truth. The
owner performs the exact comparison and emits the closure-content effect only
when that comparison succeeds.

For the controlled fixture, the synthetic owner/coordinator fences permitted
workspace mutations from the designated final read through terminal commit.
An injected owner write between verify and acceptance must reject or prevent
success. The ledger lock alone does not guard the workspace. Keep the closing
phase and failure/retry/cleanup behavior local to this domain; do not introduce
a second lifecycle writer. No atomicity against arbitrary external filesystem
writers or universal freshness horizon is claimed. Repeated successful checks
are excluded from the first fixture because existing acceptance uses any
matching success, not newest-observation invalidation.

## Implementation slices and observables

| Slice | Public boundary | Independent expected result |
| --- | --- | --- |
| Authority setup | Environment registration and task ingress | Unique environment/run/task/trace lineage; foreign ingress rejects |
| Invocation | Fixed allocator, readiness, PromptCompiler, ModelInvocationAuthority | Raw output tied to the exact ready actor and compiled task; no execution yet |
| Admission | Normalization, SemanticAdmission, DomainLifecycleAdmission | Only scoped, schema-valid, authorized output obtains an execution lease |
| Historical effect | Lease-only temporary-workspace owner | Readable mutation receipt belongs to the responsible operation; invented write narration supplies no receipt |
| Closure content | Owner read of the actual workspace | Exact required content/schema matches the frozen task oracle, independently of provider text |
| Acceptance and restart | TaskAcceptanceEvaluator and LifecycleLedger | Both required claims proven; restart retains the same assessment and causal identity |
| Visibility | Observatory projection | Raw output, gates, lease, observations and terminal decision remain distinguishable |

Required tests, one failing public slice followed by its minimal implementation:

1. Untouched exact-content write and read accept after restart.
2. Schema-valid proposal containing wrong required text cannot accept the task.
3. Provider reports a write without workspace mutation; no effect is proven.
4. A successful write is followed by an external content change before closure;
   preserve the historical write and reject the current-content requirement.
5. Missing, foreign or mismatched operation evidence cannot satisfy either claim.
6. Forbidden object or prohibited effect rejects before dispatch.
7. Interruption or uncertain effect remains open or receives its typed failure;
   it must not become terminal success after reload.

Stale-evidence cases require an accepted temporal-validity contract. No freshness
horizon is invented for this fixture. Tests compare immutable historical facts
with a separately recorded closure observation, not a retroactive revision.

## Task-oracle binding for owner-local implementation

The existing TaskSpec carries a goal and requested effect IDs, but no typed
task-content predicate. The ledger's compiled-task projection does not persist
the full goal or predicate. Before implementing the closure checker, freeze how
the domain owner receives and verifies the exact task constraint, and how its
identity is retained for restart. A schema-valid string is insufficient proof
of exact requested content. Do not add implicit TaskSpec fields, use prose
parsing as trusted policy or make a second mutable task store.

A fixture-local deterministic oracle can test the chain only if its exact
task binding and provenance are explicit. It would not qualify a generic
cross-domain content evaluator. The agreed exact-content/schema meaning is
settled; its data-carrying interface is not implemented by this plan.

The alternatives below preserve the design discussion. On 2026-10-08 the human
selected the owner-local frozen predicate for the first suite; the common typed
constraint remains an unadopted follow-up. No adapter is implemented by this
plan. `ab_harness_synthetic` is the proposed domain-owner package alongside
`ab_harness_nao`, with no second lifecycle or admission owner.

| Alternative | Identity and replay requirement | Scope |
| --- | --- | --- |
| Reviewed owner-local predicate | Freeze exact expected inputs before model output; retain environment/task/trace, compiled-task ID, predicate/version and input hash, plus source body and closure assessment | Small synthetic-domain proof; not a portable constraint language |
| Common typed compiled constraint | Explicit reviewed domain contract for exact text/schema, covered by compiled identity and retained with its body at the owner assessment boundary | Portable follow-up requiring schema, owner and compatibility review |

Current CompiledTask serialization includes the complete TaskSpec, and its
content hash covers goal bytes. The partial `task_compiled` ledger event does
not make those bytes available at the owner or restart. A goal hash alone is
not a typed predicate. Neither alternative may derive expected content from the
model proposal: that would make a wrong, schema-valid response its own oracle.
Missing or mismatched predicate inputs must remain unproven. The pending
admitted-object snapshot decision addresses execution semantics;
it does not automatically define task-specific desired content.

Freeze fixture inputs, output literals, task/oracle identities, train/holdout
cases and success criteria before executing. Use the public fake-provider path
first. Freeze UTF-8 encoding and exact newline behavior before execution, with
empty and Unicode controls. Retain the task-bound predicate inputs and source
body. Restart replays the recorded closure observation and judgment; it does
not reinterpret the current file as its historical closure state.
Live provider connectivity and model-quality experiments are separate
rounds. No NAO parity, Watson endpoint or H1 exit is claimed here.
