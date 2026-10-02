# UAH Identity, Environment, and Memory Design Grill

**Date:** 2026-09-08
**Status:** Architecture decisions accepted; grill closed; first TDD seam implemented
**Scope:** H0-H2 contracts, with H3-H5 compatibility seams only

## 1. Purpose

This record captures the decisions made after the H2 commit review. It keeps
the original H0-H6 delivery spine intact while resolving agent identity,
hardware allocation, environment activation, multi-actor traces, task closure,
Observatory, and NeuralWorkbench ownership.

## 2. Role, Agent, and Runtime Identity

**Question:** Does changing the model change the role configuration or the
agent?

**Decision:** `AgentRoleConfiguration` is model-independent. It freezes the
role's primary abstraction frame, approved additional frame projections,
capability packs, authority, budgets, bindings, and model-admission profile.
`AgentManifest` combines that role with a model configuration, prompt pack,
harness build, and adapter revisions. Changing any member creates a new
`agent_id`.

**Question:** How do stable names such as Watson or NAO planner survive model
changes?

**Decision:** `agent_handle_id` is a stable routed name. Each immutable handle
revision selects one `agent_id`, preserves the required role, cites fidelity
evidence, and retains rollback lineage. A handle is not the agent and does not
own memory.

```text
role_configuration_id
  + model_configuration_id
  + prompt_pack_id
  + harness_build_id
  + adapter revisions
  -> agent_id
  -> immutable agent_handle_revision_id
  -> stable agent_handle_id
```

## 3. Provider and Hardware Allocation

**Question:** Can one loaded model process embody several logical agents?

**Decision:** Yes, when the hardware and provider isolation contracts permit
it. The provider process is a computational resource; the harness owns logical
agent identity. Separate agents retain distinct runs, prompts, frame
projections, task state, and authority even when they share an equivalent
model instance.

```text
provider_pool_id
  -> model_instance_id
  -> model_lease_id
  -> model_invocation_id
```

Registration does not reserve hardware or invoke a model. An explicit startup
or invocation request acquires a lease after capacity and freshness checks.
`ModelAllocator` may choose an equivalent instance of the declared model
configuration. It cannot silently substitute another model configuration.

H1 supplies a fixed-instance lease interface. H2 uses fixed NAO provider
profiles. Dynamic pools, eviction, arbitration, multi-agent scheduling, and
fidelity-gated rebinding begin in H3.

## 4. Environment Activation and Continuous Agents

**Question:** What groups a running NAO container, its chatbot and planner, and
the tasks they process?

**Decision:** `EnvironmentProfile` is the reusable native-runtime contract.
`environment_run_id` identifies one owner-attested activation. It groups native
ingress, attached agent runs, tasks, traces, and native evidence.

```text
EnvironmentProfile
  -> EnvironmentRunAttestation
  -> environment_run_id
       -> chatbot agent_run_id
       -> planner agent_run_id
       -> task_id
            -> trace_id
                 -> operation graph
```

Each `agent_run_id` attaches to exactly one environment run and may process
many stimuli, tasks, model leases, and model invocations. A run may enter
standby without holding a model. A normal turn creates an invocation, not a new
agent run. Restart, terminal failure, explicit detach, or changed embodiment
creates a new run.

The environment owner starts native infrastructure and issues readiness
evidence. UAH validates and registers the attestation. It does not claim native
readiness from discovery alone.

## 5. Environment Ingress and Task Association

**Question:** Does every incoming user message or runtime event create a new
task or model call?

**Decision:** No. Approved bindings normalize input into immutable
`EnvironmentIngress`. Deterministic `TaskIngressAuthority` classifies and
admits each item as an environment state update, new task, resumed task,
notification to an existing task, or rejection. It is the only public writer
for accepted task-bearing ingress; the task registry is a read-only ledger
projection. A model may interpret admitted task content but cannot rewrite the
assigned task or trace lineage.

Domain task IDs retain native meaning. NAO goal, request, plan, version, and
step IDs cross the UAH boundary unchanged. UAH identities supplement this
lineage rather than reconstructing or replacing it.

## 6. Trace, Actor, and Operation Graph

**Question:** Is `trace_id` equivalent to a chat session or one agent's log?

**Decision:** No. It identifies one causal workflow and may contain operations
from several actor agent runs. Environment, task, chatbot, planner, role, and
handle views are read-only projections over one append-only ledger.

Every operation is anchored to exactly one frame-relative AB object. Internal
complexity or cross-frame delegation does not promote its AB level.

- `decomposes_to` refines an operation inside the same frame.
- `delegates_to` crosses into another frame through a typed role or handle,
  closed input artifact, expected output artifact, and authority boundary.
- `continues_with` records ordered workflow progression without claiming
  decomposition.

## 7. NAO `report_result`

**Question:** Is `report_result` AB2 because it verifies evidence, calls the
chatbot, and dispatches speech?

**Decision:** It remains AB1 in the planner runtime frame because it is one
planner-visible semantic operation. It verifies execution evidence, delegates
grounded response composition to the chatbot agent run in the dialogue frame,
then returns to the native communication owner. The delegated model text can
produce a typed report artifact but cannot prove navigation, manipulation, or
speech effects.

The NAO `v1.0.0` runtime and pinned chatbot source are authoritative. The
intended NeuralWorkbench revision contains an older same-frame decomposition.
H2 must correct that drift through an owner-reviewed, content-addressed
DomainContractPack revision. Live mutable registry synchronization is rejected.

## 8. Task Effects and Terminal Acceptance

**Question:** How should the harness represent an operation whose primary
effect succeeds but whose final spoken report fails?

**Decision:** Tasks declare typed `EffectObligation` values before execution.
Each is `required` or `best_effort` and names its evidence contract, owner, and
freshness policy. A pure evaluator derives `TaskAcceptance` from these
obligations and owner-issued evidence.

```text
all required satisfied              -> accepted
all required satisfied,
best-effort deficit recorded         -> accepted_with_deficit
required effect still obtainable     -> suspended
required effect terminally failed    -> rejected
```

An operation retains its own result. A later reporting failure cannot
retroactively turn successful navigation or manipulation into failure. Model
text and an event named `execution_feedback` are not terminal proof by
themselves.

## 9. Observatory and Verified Memory

**Question:** Should Observatory and NeuralWorkbench be one frame or service?

**Decision:** No. Observatory renders immutable facts and read-only projections.
NeuralWorkbench consumes evidence to retrieve experience, compare candidates,
and change future candidate priors. Workbench cannot mutate the ledger, and
Observatory does not construct memory or candidates.

`VerifiedTraceDigest` is a deterministic, model-free projection of lifecycle,
operation, evidence, and obligation events. It is the trusted compact unit for
Observatory and future Workbench retrieval. `memory_policy_id` limits which
digests a role may inspect by domain, environment profile, frame, role, task,
object, outcome, and approved handle lineage.

Model-authored reflection is excluded from the trusted digest. H3 may later
create reflection candidates under Workbench quarantine.

## 10. NeuralWorkbench Intervention

**Question:** Must full Workbench search run on every interaction?

**Decision:** No. H2 freezes the attachment seams only. H3 may perform a cheap,
deterministic task-root retrieval according to `memory_policy_id`. Empty memory
returns no candidate. Full `ConsultWorkbench` search is explicit or triggered
by deterministic policy based on task complexity, uncertainty, failure,
recovery need, and budget. It does not run by default for every trivial AB0 or
AB1 operation.

Workbench remains the muscle-memory engine: retrieved and adapted traces,
host-model multi-trajectory candidates, deterministic verification and
scoring, then H4 crystallization quarantine. It is not merely deterministic
lookup and does not require learned retrieval for its first implementation.

## 11. Domain Onboarding Boundary

**Question:** Does every domain require a new UAH kernel package?

**Decision:** No. Domain onboarding produces a declarative, content-addressed
DomainContractPack containing frames, objects, role projections, bindings,
evidence rules, prompt policy, environment profile, and qualification cases.
A custom adapter is permitted only for irreducible native semantics. NAO may
need a ROS-free normalization and parity adapter, while ROS imports and native
lifecycle ownership remain in the NAO repository.

Assisted onboarding may propose pack content and apply SkillOpt, TDD, and
deslop workflows. It cannot approve its own semantic objects or bindings.

## 12. Delivery Spine

- **H0:** freeze the complete identity, environment, ingress, operation-edge,
  obligation, acceptance, trace, and provider grammar.
- **H1:** implement registries, deterministic ingress, attached run lifecycle,
  standby, fixed-instance leases, PromptCompiler, admission, obligation
  evaluation, append-only replay, O1, and deterministic trace digests.
- **H2:** register the NAO environment, fixed chatbot/planner handles and
  providers, preserve native lifecycle owners, implement planner parity and
  `report_result` delegation, then run recorded and fake/sim qualification.
- **H3:** add hardware-aware provider pools and the first retrieval/search
  NeuralWorkbench.
- **H4:** add crystallization and reviewed promotion.
- **H5:** federate local and remote provider pools with conformance tests.
- **H6:** retain AB5 policy-foundry research as optional.

## 13. TDD Seam Confirmed on 2026-09-09

The owner confirmed the public seam and closed the architecture grill:

```text
TaskAcceptanceEvaluator.evaluate(
    effect_obligations,
    evidence_set,
) -> TaskAcceptance
```

The first red-green slices now distinguish required-effect failure from a
best-effort deficit using the same immutable evidence grammar. Duplicate
obligation identities and empty obligation sets fail closed. At this checkpoint
the recorded NAO result retained a `required_observables` compatibility field.
Decision 21 records its removal once typed obligations became the sole input.

The owner-attested synthetic environment registration seam is now implemented.
It requires a registered frozen `EnvironmentProfile`, exact owner, native
runtime, and DomainContractPack revisions, plus readiness evidence. Reused run
or attestation identities fail before state is written. Registration performs
no native startup or model action. Immutable environment ingress and
deterministic state-update classification are now implemented under exact
profile, DomainContractPack revision, run, binding, and type checks.

Task-bearing actions remained disabled at this checkpoint until task and trace
identity issuance was defined. This prevented `start_task`, `resume_task`, or
`notify_task` decisions from carrying absent or reconstructed lineage.

## 14. Evidence and Limits

The architecture was checked against NAO tag `v1.0.0`, chatbot revision
`a2ecca796...`, and intended NeuralWorkbench revision `e76ba7e`. Focused
read-only baselines passed 112 chatbot turn-engine tests and 41 planner
supervisor/gate tests. These results constrain compatibility but do not qualify
UAH H2. `EffectObligation`, `TaskAcceptance`, the pure acceptance evaluator,
and profile-verified environment-run registration are now implemented. The NAO
projection and recorded qualification live in the separate `ab_harness_nao`
adapter package. No TaskSpec obligation compiler, environment-profile
serialization or signature verification, task registry, ingress persistence
and deduplication, multi-actor ledger, `report_result` adapter, or Workbench
retrieval policy is implemented at this checkpoint. The current in-memory
registration and ingress contracts do not provide durable persistence,
attestation signature validation, or environment close semantics.

## 15. TDD Continuation on 2026-09-13

This implementation checkpoint applies Decision 5 without reopening the
architecture grill. A reviewed `start_task` rule now selects the domain-owned
task identifier from a named immutable native-lineage field. UAH preserves
that identifier and derives the initial causal `trace_id` with the versioned
`uah-trace-v1` scheme over the environment run and task identity.

Missing task lineage produces typed rejection. Mutable lineage containers,
duplicate keys, and empty lineage fields fail contract construction. Resume
and notify remain disabled until an environment-bound task registry can prove
that the referenced task exists in the same activation. No model may author,
replace, or infer these identities.

## 16. Environment Task Registry TDD Continuation on 2026-09-13

The next implementation round applies the same Decision 5 boundary.
`EnvironmentTaskRegistry` records immutable task and trace lineage under the
exact environment activation. Replayed task-bearing ingress is rejected. A
different ingress cannot start a domain task that is already registered in the
same environment run. Both decisions retain the existing task and trace
identifiers for inspection without authorizing another activation.

Registered `resume_task` and `notify_task` ingress reuse the original trace.
Unknown task identifiers and references to a task registered under another
environment run fail closed. This registry is an in-memory H0 contract proof.
It does not supply durable recovery, terminal task transitions, concurrent
transaction guarantees, or native effect evidence.

## 17. Acceptance and Task Replay TDD Continuation on 2026-09-19

Historical checkpoint. Section 21 supersedes the separate task-event authority
described below with the common `LifecycleLedger`.

This round connects the existing pure `TaskAcceptance` judgment to the
environment task registry. `accepted`, `accepted_with_deficit`, and `rejected`
become terminal registry states and reject later resume or notify ingress.
`suspended` remains nonterminal because required evidence is still pending.
A terminal judgment cannot be replaced, and no acceptance may close a task
registered under another environment activation.

Task start, resume, notification, suspension, and terminal acceptance emit
content-addressed `TaskLifecycleEvent` values using the Observatory event
vocabulary. Ordered replay reconstructs lineage, terminal state, and
duplicate-ingress protection without a model or a second acceptance-evaluator
pass. Modified event content, duplicate event identity, and acceptance before
task start fail closed.

The event stream remains an in-memory H0 proof. Durable storage, global event
sequence, timestamps, and process-restart recovery remain open. Cancellation
and native failure are not represented as generic terminal calls because their
environment-owner authority contract has not yet been implemented.

## 18. Task Lifecycle Persistence TDD Continuation on 2026-09-23

Historical checkpoint. `uah.task_lifecycle_event/v1` and
`JsonlTaskLifecycleStore` were removed when `uah.trace_event/v1` became the
single writable lifecycle envelope.

This round applies Decision 5 to restart recovery without expanding the event
authority model. `TaskLifecycleEvent` now serializes through the exact
`uah.task_lifecycle_event/v1` envelope. Missing or additional fields,
unsupported versions, empty or non-string values, incompatible event/status
pairs, and content-address mismatches fail validation.

`JsonlTaskLifecycleStore` provides a canonical, append-only local stream. Each
append is flushed through `fsync`. Reload validates the complete UTF-8 stream
before replaying it into a fresh `EnvironmentTaskRegistry`, so malformed JSON,
blank records, invalid events, duplicates, invalid ordering, and an
unterminated final record cannot publish partial registry state. A missing
store reconstructs an empty registry. A valid stream reconstructs task and
trace lineage, ingress replay protection, suspension, and terminal acceptance
after process restart without a model or evaluator call.

The accepted scope is a single-writer, task-event subset. It does not claim
cross-process locking, a global event sequence, timestamps, parent-event
links, compaction, or a filesystem-wide power-loss transaction. Integration
with the common lifecycle ledger remains required. Cancellation and native
failure remain excluded until an environment-owner authority contract defines
who may assert those transitions and which evidence must accompany them.

## 19. TaskSpec Compiler TDD Continuation on 2026-09-23

The next H0 seam compiles one accepted task start into a single immutable
source of truth. `TaskSpecCompiler.compile(...)` consumes the admitted
`TaskIngressDecision`, `uah.task_spec/v1`, role, frame, registry, and reviewed
DomainContractPack. It emits a content-addressed `uah.compiled_task/v1` with
task and trace lineage, one closed `InteractionModuleSpec`, compiled effect
obligations, merged prohibited effects, finite budgets, and exact domain-pack
provenance.

The task author selects semantic effects and whether each is required or
best-effort. The DomainContractPack owns the mapping from each effect to one AB
object, evidence owner, and failure policy. The compiler verifies that the
owner matches the AB object and that the effect is a declared normalized
observable. This prevents task text or future model output from selecting its
own evidence authority.

Compilation occurs once after successful `start_task` ingress. Resume and
notify ingress resolve the existing compiled artifact. Recompilation is
rejected so a task cannot change projection, obligations, prohibitions, or
budgets while retaining the same task and trace identities. Domain-rule
ambiguity, duplicate obligation identities, prohibited requested effects,
lineage or revision mismatches, mutable collections, and altered content
identities fail closed.

This round does not implement prompt wording, proposal normalization, semantic
admission, domain lifecycle admission, execution leases, or ledger events for
compilation. The next seam must make `CompiledTask` the sole authority input to
`TypedProposal -> AdmittedOperation -> ExecutionLease`.

## 20. Typed Proposal and Two-Stage Admission TDD Continuation on 2026-09-28

This round implements the authority path selected during the grill without
granting execution authority to model output or to UAH semantic admission.
`ProposalNormalizer` converts one raw typed model-output artifact into one
content-addressed `uah.typed_proposal/v1`. The proposal preserves the exact
compiled task, environment run, task, trace, operation, output type, AB object,
and canonical finite-JSON arguments. It rejects model-authored effect claims,
ambiguous payload shapes, missing artifact lineage, and disagreement between
the requested object and the model's object references.

`SemanticAdmission` is the domain-agnostic UAH gate. It rechecks the compiled
task identity and causal lineage, role output policy, task projection, direct
control band, runtime callability, prohibited effects, effect obligations, and
the selected approved binding. The binding must match the environment and
runtime mode, retain the semantic owner's implementation boundary, and provide
input, output, and evidence adapter references. Acceptance produces one
content-addressed `uah.admitted_operation/v1`. That artifact records a semantic
decision and still cannot authorize native execution.

`DomainLifecycleAdmission` is a separate environment-owned gate. It rechecks
the active environment activation, environment identity, DomainContractPack
revision, and duplicate-operation state before issuing an operation-scoped,
attestation-bound `uah.execution_lease/v1`. The accepted tracer therefore has
the following authority order:

```text
CompiledTask + raw typed model output
  -> TypedProposal
  -> UAH semantic admission
  -> AdmittedOperation
  -> domain lifecycle admission
  -> ExecutionLease or typed rejection
```

All three artifacts reject content tampering. At this checkpoint the slice did
not validate arguments against the binding's input schema, decrement task
budgets, dispatch to an environment owner, persist proposal and admission
events in the common ledger, or implement cancellation, concurrency, expiry,
and fencing. Section 21 records the subsequent lease-only owner and accepted
event chain. Argument-schema validation, runtime budget enforcement, and the
remaining lifecycle controls remain open.

## 21. Lease-Only Execution and Common-Ledger Continuation on 2026-09-28

The next authority seam is implemented without retaining a direct-dispatch
compatibility path. `InProcessEnvironmentOwner.execute(...)` accepts only an
exact `ExecutionLease`. Before invoking the mounted native handler, it verifies
environment and lifecycle ownership, re-resolves the approved binding, compares
the complete binding fingerprint, and records `execution_started` in the common
ledger. A repeated attempt is rejected even after constructing a new owner or
domain-admission instance over the same ledger.

Successful execution returns a content-addressed `uah.execution_receipt/v1`
that keeps the native owner result separate from normalized `EffectEvidence`.
The receipt preserves lease, admission, environment, task, trace, operation,
binding, and evidence lineage. Native exceptions append `execution_failed`
before propagating. A consumed lease is not retried implicitly; cancellation
and reviewed retry authority require a later lifecycle contract.

The old `HarnessTrace`, `JsonlHarnessTraceStore`, `TaskLifecycleEvent`, and
`JsonlTaskLifecycleStore` were removed rather than layered beneath another
store. `LifecycleLedger` is now the single writable authority. Its
`uah.trace_event/v1` values provide global sequence, causal parent, timestamp,
artifact references, strict canonical JSONL reload, optimistic sequence
conflict checks, and transition validation. `EnvironmentTaskRegistry` rebuilds
its routing projection from these events.

The accepted tracer now records:

```text
task_started
  -> task_compiled
  -> proposal_normalized
  -> semantic_admission_accepted
  -> domain_admission_leased
  -> execution_started
  -> execution_completed
  -> evidence_issued
  -> effect_obligation_satisfied | effect_obligation_failed/pending
  -> terminal_task_accepted | terminal_task_accepted_with_deficit
```

Strict restart replay derives a content-addressed
`uah.verified_trace_digest/v1` without a model or native handler. The paired
best-effort case remains accepted while preserving its deficit. Recorded NAO
qualification now uses task-owned `TaskEffectRequest` values against an
injected domain-owned contract pack and the same compiled authority chain; the
older `required_observables` fallback and duplicate planner gate were removed.

This continuation does not complete the lifecycle grammar. Proposal,
semantic-admission, and domain-admission rejection artifacts, evidence
rejection, required-effect failure, stale evidence, timeout, cancellation,
retry exhaustion, false completion, `OperationEdge`, cross-process writer
locking, and agent/model events remain scheduled H0/H1 work.

## 22. Authority-Hardening Continuation on 2026-09-28

The review rejected caller-authored routing and domain-rule provenance. The
implemented `uah.domain_contract_pack/v1` now derives its SHA-256 revision from
the exact pack/frame/registry identifiers, role and task allowlists, ingress
rules, effect-to-object and evidence-owner rules, failure policies, and
prohibited effects. Any covered rule change requires a new revision.

`uah.environment_ingress/v1` now has a content-derived ingress artifact ID, and
`uah.task_ingress_decision/v1` has a content-derived `decision_id` that binds
that artifact. Identity verification is necessary but not sufficient:
`TaskSpecCompiler` also calls `EnvironmentTaskRegistry.require_start(...)` and
rejects a decision unless the same environment activation, starting ingress,
task, and trace are already recorded in the common ledger. The ledger, not a
caller-constructed decision, owns task-start authority. The internal start
fact records the exact ingress artifact, decision ID, and pack revision; no
public raw-lineage registration method can create compilation authority.

`uah.trace_event/v1` now includes `commit_id`, `commit_index`, and
`commit_size`. All events emitted for one lifecycle fact share a commit frame.
Strict reload rejects an incomplete, noncontiguous, or interleaved commit, so a
newline-terminated crash after only part of a multi-event fact cannot publish
partial authority state. The ledger remains single-writer; cross-process
coordination is still open.

Recorded NAO qualification must receive an injected, content-addressed
DomainContractPack. It may not synthesize policy from the qualification case.
It routes the supplied
`EnvironmentIngress` through the real `TaskIngressPolicy`, uses the
ledger-backed decision for compilation, rejects malformed planner steps
without dropping them, and content-hashes the complete raw planner payload.
This is a strict recorded qualification of the generic seam, not H2 owner
review, live-node, or planner-parity evidence.

Task budgets remain immutable declarations in `CompiledTask`. No current
runtime decrements wall time, model calls, or tool calls, so documentation and
qualification must not describe budget enforcement as implemented.

Terminal acceptance must account for the complete evidence set already
recorded on the trace. Replay rejects both unrecorded evidence and omitted
evidence. Receipt replay also compares the admission ID, AB object, binding,
and evidence owner with the recorded semantic admission before accepting an
execution result. The NAO recorded parser rejects unknown plan or step fields,
so dependency, retry, and ordering semantics cannot be silently flattened.

## 23. Seam-Audit Continuation on 2026-09-30

The H0/H1 audit found that constructor-time hashing did not protect later trust
crossings. Content-addressed ingress, compiled tasks, proposals, admitted
operations, and execution leases now reverify their complete nested identity
before policy classification, semantic admission, domain admission, ledger
recording, receipt issuance, or native dispatch. A post-lease proposal change
therefore fails before its handler can run.

File-backed ledgers now coordinate cooperating processes with an OS advisory
lock. A writer locks, reloads and validates the stream, evaluates the proposed
transition, appends, and calls `fsync` before it releases the lock. Two stale
ledger instances cannot consume the same lease twice. Strict reload still
rejects a crash-truncated multi-event commit; automatic repair is not claimed.

Resume and notify facts now retain the exact ingress artifact, decision, and
DomainContractPack revision. Pre-dispatch suspension is representable without
an invented lease. Stale task-registry projections reload before start and
existing-task admission. Replay globally fences task-bearing ingress identity
and rejects a second start on one trace.
Receipt construction failures record `execution_failed` before they propagate.
Registry snapshots reject duplicate object identity, frame projection rejects
registry-revision mismatch, and replay rejects unknown event types. Typed
counterexample and cancellation grammar remains the next H0/H1 decision.

The final H0 lifecycle slices and Observatory O1 now proceed in parallel. O1 is
a read-only replay projection and static review surface over the common ledger.
It cannot append events, issue evidence, repair traces, or promote memory. Each
failure family enters O1 only after its restart-replay contract is stable.

## 24. Executable-Seam Continuation on 2026-10-01

The public task-ingress authority is implemented. It snapshots primitive
DomainContractPack rule values, owns accepted task-bearing ledger writes, and
refreshes its read-only task projection before duplicate and terminal checks.
State updates and rejected ingress still require an environment-scoped event
family before they can claim durable replay.

Semantic admission now validates canonical arguments through a reviewed,
content-addressed portable object-schema subset. The subset covers required
fields, top-level JSON types, and additional-property policy. Executable
callable validators were removed because a source-revision string did not make
captured callable state deterministic. `uah.admitted_operation/v2` records the
validated input-schema identity.

`uah.semantic_admission_rejection/v1` and
`uah.domain_admission_rejection/v1` are immutable operation-scoped facts. The
semantic coordinator appends the returned semantic rejection; the domain
lifecycle owner appends its own rejection. Replay exposes either as a
nonterminal failure stage. Only explicit task-acceptance authority may make the
trace terminal. Repeated requests for an already issued domain lease return the
same deterministic lease and do not append a contradictory rejection.

Initial H1 identity registries now implement content-addressed `AgentManifest`,
one-time `AgentHandleRevision` registration, and roster-bound `AgentRun`
attachment in `attached_standby`. The handle registry refuses rebinding because
the required fidelity evaluator is H3 work. These registries are in-memory and
do not emit lifecycle events, perform preflight, allocate a model, persist run
state, or invoke a provider.

The initial O1 implementation projects validated ledger events into immutable
trace views and static searchable HTML. It derives terminal status only from
explicit terminal facts, retains operation failure stages, escapes raw payloads,
and embeds inert graph JSON. Arbitrary event collections default to
`synthetic`; the `recorded` label requires a validated `LifecycleLedger`. The
full actor, configuration, provider, comparison, and Workbench views remain
open.

The next ordered seams are `OperationEdge`, typed normalization and evidence
rejection, terminal required-effect counterexample replay, scoped activation
events, fixed-instance model leases and preflights, then `PromptCompiler` and a
provider-neutral invocation port.
