# UAH H0/H1 seam deepening and guardrails research

**Date:** 2026-09-30

**Status:** Architecture research input, not an accepted implementation decision

**Scope:** Lifecycle grammar, task ingress, artifact identity, admitted-operation
context, public interfaces, repository guardrails, and the H0/H1 path required
before H2 planner work.

## Executive decision

The current H0/H1 implementation has a sound authority chain. The immediate
architecture problem is incomplete lifecycle grammar, not the size of
`lifecycle.py` by itself. The next implementation should preserve
`LifecycleLedger` as the single append and replay interface while making each
new rejection or failure family local to a closed typed grammar.

The recommended sequence is:

1. record normalization, semantic-admission, and domain-admission rejection as
   typed lifecycle facts;
2. replace the private seam from `TaskIngressPolicy` to
   `EnvironmentTaskRegistry._record_policy_start()` with one public
   task-ingress authority that classifies and durably records a decision;
3. define and test the `OperationEdge` contract before multi-operation policy;
4. add evidence rejection and false-completion attribution;
5. add owner-authorized cancellation, recorded timeout decisions, bounded retry
   decisions, and retry exhaustion as separate vertical slices;
6. extract an internal lifecycle grammar module only when those slices create a
   second coherent event family.

This sequence closes the masterplan's immediate H0/H1 gate without adding a
generic pipeline, plugin registry, stateful trace session, or broad runtime
facade. H2 should consume the same typed authority interfaces through the NAO
adapter. It should not receive a direct ledger or owner-dispatch escape hatch.

## 1. Target contract

The research target is the smallest architecture that can make the following
cases replayable and attributable before H2 planner parity:

- proposal normalization rejection;
- semantic and domain admission rejection;
- native owner failure and receipt-construction failure;
- stale or otherwise inadmissible evidence;
- timeout and cancellation;
- retry continuation and retry exhaustion;
- false completion;
- multi-operation lineage through `OperationEdge`.

The following ownership rules are fixed:

- models produce typed proposals, not authority or effect truth;
- semantic admission and domain lifecycle admission remain separate;
- an environment owner issues native results and effect evidence;
- deterministic task acceptance closes declared obligations;
- the common lifecycle ledger is the writable lifecycle authority;
- AB coordinates remain frame-relative;
- H3+ candidates remain quarantined.

Non-goals for this pass are provider integration, a generic event plugin system,
an ORM or database migration, arbitrary hash-algorithm selection, and a
monolithic runtime object that absorbs the existing authority modules.

## 2. Evidence base

The findings are grounded in the current branch through commit `e81e369` and
the following sources:

- `CONTEXT.md`, especially proposal, admitted-operation, operation-edge,
  evidence, task-acceptance, digest, and ledger definitions;
- `docs/plans/universal_agentic_harness_masterplan.md`, especially the H2 hard
  gates and ordered H0/H1 queue;
- `docs/architecture/universal_agentic_harness_foundation.md` and ADR 0001;
- `src/ab_harness/lifecycle.py`, `environment_ingress.py`, `task_registry.py`,
  `proposal_admission.py`, `domain_lifecycle.py`, and `environment.py`;
- focused lifecycle, task-ingress, compiler, and two-stage-admission tests;
- the 2026-09-30 architecture scan of the H0/H1 seams;
- the iTrader `itrader-architecture-check` skill and the NAO
  `iiia-ros4hri-check` and `seam-hypothesis-audit` skills.

The deslop audit found no hard repository-standard violation after the
correctness fixes. It retained four judgment calls: lifecycle grammar locality,
the private task-start seam, repeated content-ID mechanics, and the admitted
operation field group. The specification review found the accepted path sound
and identified the typed counterexample grammar as the remaining partial H0/H1
requirement.

## 3. Current strengths to preserve

### 3.1 The lifecycle ledger is already a deep module

`LifecycleLedger.record()` hides global sequence allocation, causal parents,
atomic commit framing, strict reload, transition reduction, advisory locking,
append, flush, and `fsync`. `replay()` derives terminal status and a
`VerifiedTraceDigest` without a model. Deleting this module would spread
ordering, persistence, and replay mechanics across every authority owner.

The module's 1,412 lines are therefore not sufficient evidence for a split.
The relevant measure is interface depth. Its small write and replay interface
hides substantial implementation detail and supplies high leverage.

### 3.2 Authority artifacts fail closed at trust crossings

Ingress decisions, compiled tasks, proposals, admitted operations, leases, and
receipts verify content identity before authority is granted. The ledger and
environment owner reverify nested artifacts. This prevents a content-addressed
outer value from authenticating mutated nested content.

### 3.3 File-backed writers now share one critical section

Competing ledger instances lock, reload, reduce, append, flush, and `fsync`
under one advisory writer lock. Stale task-registry instances refresh before
using their projections. Duplicate starts and duplicate lease consumption fail
closed across cooperating processes.

### 3.4 The task registry is a projection, not a second event store

`EnvironmentTaskRegistry` reconstructs task and ingress lineage from lifecycle
events. This matches the masterplan and should remain true after the task-start
interface changes.

## 4. Findings and deletion tests

### 4.1 Lifecycle event knowledge has low locality

Adding one event currently requires coordinated edits to several regions of
`lifecycle.py`:

- the accepted `LifecycleFact` union;
- `_event_specs()` conversion;
- `_SUPPORTED_EVENT_TYPES`;
- `_EVENT_PREREQUISITES` and operation-event classification;
- `_apply_event()` dispatch and a reducer function;
- digest projection where the event contributes to the verified result.

This is a repeated-switch problem. It becomes material when the remaining
failure families are added. A partial extraction that moves only the event-name
set would make the module shallower because contributors would still need to
know every other location.

**Deletion test:** deleting a cohesive typed grammar would return event
conversion, transition rules, state reduction, and digest projection to
separate switches. It earns a seam once at least two failure families use it.

**Decision:** keep the public ledger interface. During the first rejection
slice, co-locate the new fact, conversion, transition, and projection logic.
Extract an internal grammar module only after the pattern is proven by a second
slice.

### 4.2 Task ingress crosses a private mutation seam

`TaskIngressPolicy` constructs `TaskLineage` and calls
`EnvironmentTaskRegistry._record_policy_start()`. The policy therefore performs
stateful authority work while its name and public shape suggest pure
classification. The registry exposes public mutation for resume and notify but
a private mutation for start. The division is difficult to explain and creates
an implementation-shaped test surface.

**Deletion test:** deleting a task-ingress authority would force every domain
adapter to coordinate rule matching, deterministic IDs, duplicate checks,
terminal checks, ledger writes, and projection refresh. The module earns depth.

**Decision:** introduce one public task-ingress authority with an operation such
as:

```python
class TaskIngressAuthority:
    def admit(
        self,
        environment_run: EnvironmentRun,
        ingress: EnvironmentIngress,
    ) -> TaskIngressDecision: ...
```

`admit()` owns rule matching, content verification, deterministic task and trace
identity, duplicate and terminal checks, decision issuance, ledger append, and
projection refresh. The task registry becomes an internal or explicitly
read-only projection. The compiler continues to require the accepted start
decision and exact recorded lineage.

The migration should preserve the present decision schema until the first
counterexample proves that a new schema is needed. A broad
`AuthorityRepository` abstraction is deferred.

### 4.3 The current event envelope assumes a task already exists

`TraceEvent` requires environment-run, task, and trace identifiers, and replay
requires each trace to begin with `task_started`. Some ingress rejections occur
before a valid domain task identity exists. Recording such a rejection by
inventing an empty or synthetic task identity would weaken lineage semantics.

**Decision:** distinguish two work items:

1. Record proposal, semantic, domain, execution, and evidence failures that
   already have task and trace lineage under the current envelope.
2. Before recording pre-task ingress rejection, specify a versioned event scope
   such as `EnvironmentScope | TaskScope | OperationScope`. Continue to read v1
   events, emit v2 only after the migration contract and digest implications are
   tested, and never rewrite historical event identities.

This is the strongest reason to consider a trace-event v2. It should not be
introduced merely to reorganize Python code.

### 4.4 Content-addressing code is repeated but not yet one contract

Several modules implement canonical JSON plus SHA-256. Their observable
behavior is not identical. Prefixes, error messages, finite-number checks,
separator choices, and payload schemas differ. Extracting `_content_id(prefix,
payload)` today would centralize syntax while leaving compatibility policy
distributed.

**Deletion test:** a generic hashing helper can be deleted with little effect
on callers or domain policy, so it is shallow. A canonical artifact codec earns
depth only if it owns serialization rules, schema validation, identity issuance,
and verification for more than one artifact family.

**Decision:** first freeze serialization conventions with golden tests for each
authority artifact. Keep public `issue()`, `from_dict()`, `to_dict()`, and
`verify_identity()` behavior on the artifact. If the conventions converge,
introduce one private fixed codec. Do not expose a pluggable hash service or
caller-facing `content_id()` utility.

### 4.5 `AdmittedOperation` contains a real but not yet proven data clump

Binding identity, source revision, fingerprint, owner, schema references,
evidence adapter, environment, and runtime mode travel together through
admission, lease validation, owner fencing, receipts, and replay. The existing
`ABImplementationBinding` is close to this concept but includes registry state
that may not belong in an immutable admission snapshot.

**Deletion test:** a wrapper used only by `_new_admitted_operation()` would be a
data-transfer object with no depth. A binding snapshot earns a seam if the
catalog issues it and admission, leasing, the owner, receipts, and replay all
validate it as one concept.

**Decision:** defer extraction until the H2 adapter consumes the same snapshot.
The likely shape is a content-addressed `AdmittedBindingContext` containing the
resolved binding contract and fingerprint. It must not merge semantic admission
with domain execution authority.

### 4.6 The package-root interface overstates stability

`ab_harness.__init__` re-exports about sixty names, including lifecycle commit
and fact types. The facade is broad relative to the small number of intended
authority interfaces. Removing exports now would create churn before the
failure grammar settles.

**Decision:** after the H0/H1 grammar is complete, classify exports as stable
contracts, public authority interfaces, adapter protocols, or internal facts.
Narrow the root only with migration evidence and direct-import replacements.

## 5. Proposed failure and edge grammar

The grammar should use typed artifacts with stable reason codes. User-facing
messages are derived and are not authoritative lifecycle data.

| Stage | Typed record | Required lineage | Replay consequence |
| --- | --- | --- | --- |
| Normalization | `ProposalRejection` | task, trace, raw-output artifact, optional operation | suspend or reject according to frozen task policy |
| Semantic admission | `SemanticAdmissionRejection` | compiled task, proposal, operation, ordered reason codes | no domain lease may exist |
| Domain admission | `DomainAdmissionRejection` | admitted operation, environment run, reason codes | no execution start may exist |
| Execution | `ExecutionFailure` | exact lease, stage, safe failure reference, retry classification | terminal operation failure or retry decision |
| Evidence | `EvidenceDecision` | result, binding context, obligation, observed time | accept evidence or reject it as stale, foreign, malformed, or insufficient |
| Cancellation | `CancellationDecision` | requester, owner authorization, target, reason | accepted cancellation terminates the target exactly once |
| Timeout | `TimeoutDecision` | target, declared deadline, recorded observation time, policy revision | replay uses the recorded decision, not the current clock |
| Retry | `RetryDecision` | failed operation, attempt ordinal, maximum attempts, policy revision | create a new operation or record `retry_exhausted` |
| Task closure | `TaskAcceptance` plus terminal fact | complete recorded obligation set | false completion rejects or suspends despite a successful model or native result |

False completion does not need a special successful-result type. It occurs when
a completion claim or successful native result lacks admissible evidence for a
required obligation. The ledger must retain the result, the evidence rejection,
and the deterministic terminal judgment.

### OperationEdge v1

The first edge schema should remain closed:

```python
@dataclass(frozen=True)
class OperationEdge:
    edge_id: str
    source_operation_id: str
    target_operation_id: str
    relation: Literal["decomposes_to", "delegates_to", "continues_with"]
    source_frame_id: str
    target_frame_id: str
    artifact_contract_ref: str | None = None
    schema_version: str = "uah.operation_edge/v1"
```

Required invariants are:

- both operations exist in the same trace;
- an edge cannot target itself;
- `decomposes_to` remains within one frame;
- `delegates_to` names another frame and a typed artifact contract;
- `continues_with` records order without claiming decomposition;
- decomposition and delegation edges are acyclic;
- retry semantics live in `RetryDecision`; a retry may use
  `continues_with` to link the new operation.

The edge is an immutable lifecycle fact. It is not mutable graph state and does
not grant the target operation admission or execution authority.

## 6. Interface alternatives

Three independent designs were compared.

| Design | Interface | Strength | Main cost | Decision |
| --- | --- | --- | --- | --- |
| Minimal authority | `LifecycleAuthority.append/replay` plus `TaskIngressAuthority.admit` | Preserves existing owners and hides event ordering | Closed fact union remains substantial | Recommended direction, retaining current names during migration |
| Typed transaction core | Existing authority modules return `Recorded[T]` through an internal journal | Every decision is durable at its owner boundary | Requires a transaction and artifact-store contract | Adopt incrementally if two rejection slices repeat commit mechanics |
| Common runtime facade | `HarnessLifecycle.ingest/run_operation/judge_task` | Very simple H2 caller interface | Risks becoming a command bus and hiding legitimate authority stages | Defer until recorded and NAO callers prove identical orchestration |

A stateful `open_trace()` session was rejected. It broadens the caller
interface, leaks transaction lifetime, and complicates global sequence and
cross-process lease consumption. Deleting it would mostly replace method calls
with typed fact appends, so it fails the deletion test.

## 7. Recommended module shape

The target should preserve public depth and improve internal locality:

```text
TaskIngressAuthority
  interface: admit(run, ingress) -> TaskIngressDecision
  hides: rules, deterministic IDs, fencing, task projection
             |
             v
LifecycleLedger
  interface: record(typed_fact), replay(trace_id), read projections
  hides: grammar, transitions, commit framing, locking, persistence, digest
             |
             +--> SemanticAdmission
             +--> DomainLifecycleAdmission
             +--> EnvironmentOwner
             +--> TaskAcceptanceEvaluator
```

The arrows indicate recorded facts, not transferred ownership. The ledger
validates and records decisions; it does not make semantic, domain, owner, or
acceptance decisions.

An internal grammar can later group:

- typed fact to event conversion;
- allowed predecessor and terminal rules;
- reducer state changes;
- digest fields and failure attribution.

The grammar remains a closed in-process implementation. It has no dynamic event
registration, hooks, middleware, subclass framework, or domain adapter imports.

## 8. TDD implementation queue for the DEV thread

Each slice begins with a public-seam counterexample and ends with model-free
restart replay.

1. **Semantic rejection**
   - Test a rejected proposal through `SemanticAdmission` and the ledger.
   - Require stable reason codes, no lease, a terminal or suspended judgment,
     and a replayed digest with failure stage.
2. **Domain rejection**
   - Test inactive run, revision mismatch, binding-environment mismatch, and
     duplicate lease.
   - Require no execution start and deterministic replay.
3. **Task-ingress authority**
   - Test start, resume, notify, duplicate ingress, second start, terminal task,
     restart, and two independently opened writers through one public method.
   - Remove `_record_policy_start()` only after parity.
4. **OperationEdge**
   - Test same-frame decomposition, explicit cross-frame delegation,
     continuation, missing endpoint, self-edge, cycle, and cross-trace rejection.
5. **Evidence decision and false completion**
   - Add observed time and the frozen freshness policy required to decide stale
     evidence.
   - Test successful native result with stale or insufficient evidence.
6. **Cancellation**
   - Test request before start, owner-authorized cancel during execution,
     unauthorized request, duplicate cancel, and cancel after terminal result.
7. **Timeout**
   - Use a fake clock only when issuing the decision. Replay must not reevaluate
     time.
8. **Retry and exhaustion**
   - Test bounded attempt allocation, a successful retry, non-retryable failure,
     and exhaustion. Each attempt uses a distinct operation identity.
9. **Grammar extraction decision**
   - Measure repeated edits after two slices. Extract only if conversion,
     transition, reduction, and digest behavior can move together.
10. **H2 adapter handoff**
    - Run the recorded NAO fixture through the same ingress, admission, lease,
      owner, evidence, and replay interfaces. No compatibility dispatch path is
      allowed.

The suite should retain strict JSONL corruption, artifact-tamper, stale-writer,
lease-consumption, and forbidden-import tests. Implementation-coupled tests may
be deleted only after equivalent public-interface coverage exists.

## 9. UAH guardrails skill

The new repo-local `.codex/skills/uah-guardrails` skill follows the strongest
parts of the comparison repositories:

- iTrader contributes a concise phase-aware architecture check;
- NAO contributes change classification, explicit owner boundaries, validation
  routing, and stop conditions;
- the NAO hypothesis skill contributes target-contract, competing-route, and
  adversarial-evidence discipline for difficult seams.

The UAH skill routes an agent to the canonical document for the affected seam,
walks the complete authority chain, applies lifecycle and deslop checks, and
selects targeted validation. It deliberately does not reproduce the full
masterplan, contain external research links, implement a repository scanner, or
grant commit, push, promotion, or runtime authority.

The skill is model-invoked because ordinary UAH implementation and review work
can cross an authority boundary without the user knowing to request a separate
check. Its description is narrow enough to avoid firing for unrelated Python or
documentation work.

A bounded forward test exercised two routes. The architecture case rejected a
public hash utility and adapter-owned event registration while permitting
core-defined typed facts. The citation-only holdout exposed unnecessary
architecture loading, so the final trigger excludes editorial changes that
preserve claim semantics and clarifies validation for Markdown outside the
renderer manifest.

### Future onboarding skill

A later `uah-domain-onboarding` skill should remain separate. Onboarding has a
different sequence and completion criterion: produce and qualify a
`DomainContractPack`, environment profile, frames, semantic registry, candidate
and approved bindings, ingress rules, owner evidence rules, recorded fixtures,
and rollback data. The guardrails skill reviews those artifacts but should not
author them implicitly.

The onboarding skill should use
`docs/plans/domain_initialization_and_ab_coupling.md` as its canonical source,
require an owner-reviewed recorded qualification before activation, and leave
new bindings as candidates until the documented gates pass. It should be built
after the H0/H1 lifecycle grammar can record onboarding rejection and
qualification evidence without special cases.

## 10. Accepted, deferred, and rejected proposals

### Accepted for the next implementation plan

- closed typed rejection and failure facts;
- one task-ingress authority and read-only registry projection;
- `OperationEdge` v1 before multi-operation policy;
- public-seam TDD and restart-equivalent replay for each vertical slice;
- the repo-local UAH guardrails skill.

### Deferred until a second real consumer exists

- a common `HarnessLifecycle` runtime facade;
- an `AuthorityRepository` or standalone artifact-store interface;
- `AdmittedBindingContext` extraction;
- a canonical artifact codec shared by all modules;
- package-root export removal;
- a separate lifecycle grammar file;
- the domain-onboarding skill.

### Rejected for H0/H1

- splitting `lifecycle.py` by line count;
- arbitrary event registration or plugin handlers;
- a generic command bus or stateful trace session;
- a public hash helper with caller-chosen prefixes;
- a second writable task store;
- replay-time wall-clock decisions;
- invented task identities for pre-task rejection;
- direct H2 adapter dispatch around leases or the common ledger.

## 11. Completion gate and residual risks

This architecture research is ready for DEV review when the guardrails skill
validates, repository documentation checks pass, and the branch remains free of
source behavior changes.

The H0/H1 implementation is not complete until the frozen synthetic suite
records and replays success, typed rejection, owner failure, stale evidence,
timeout, cancellation, retry exhaustion, and false completion, with governed
operation edges and identical terminal digests after restart.

| Residual risk | Required probe |
| --- | --- |
| Typed facts reproduce the existing switches in new files | Implement two failure slices and apply the locality and deletion tests before extraction |
| Task-ingress authority absorbs domain semantics | Confirm it consumes only the frozen `DomainContractPack` and never invents domain task intent |
| Event v2 creates an avoidable migration | Attempt all task-scoped rejection slices under v1 first; introduce scoped events only for a real pre-task case |
| Binding snapshot duplicates `ABImplementationBinding` | Wait for the H2 adapter, then compare exact consumers and delete redundant fields |
| Retry edges imply authority | Require fresh semantic and domain admission for every retry operation |
| Guardrails documentation drifts | Keep canonical claims in architecture and plan documents; make the skill route to them and validate it after major wording changes |
