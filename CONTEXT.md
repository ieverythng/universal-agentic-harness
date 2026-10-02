# Universal Agentic Harness Domain Model

This file records the project vocabulary that should remain stable across code,
documentation, evaluations, and environment adapters.

Terms describe the target architecture unless an entry explicitly names an
implemented schema or source seam. The current code distinguishes environment,
ingress, task, trace, operation, proposal, admission, lease, result, evidence,
and lifecycle-event identities. Content-addressed agent manifests, initial
handle revisions, and roster-bound standby agent runs now have in-memory
registries. General role-configuration, durable agent lifecycle,
model-instance, model-lease, model-invocation, and PromptCompiler registries
remain H1/H2 work.

## Core terms

### Abstraction frame

The frame-relative coordinate system that says what counts as an atomic object
for one substrate. An AB level has meaning only inside its named frame. It is
not a global intelligence or capability score.

### Primary abstraction frame

The one abstraction frame whose atomicity rule and control band define an agent
role's default task-facing coordinates. Every agent role configuration names
exactly one primary frame.

### Additional frame projection

An explicitly versioned and role-authorized subset of another abstraction
frame. It carries its own control band and frame access mode and never implies
automatic cross-frame equivalence.

### Frame access mode

The immutable role-level limit on an additional frame projection:
`inspect_only`, `direct_proposal`, or `delegate_only`. Task compilation may
narrow this limit but cannot widen it.

### Cross-frame delegation

A typed causal relationship in which an operation requests work from an agent
whose primary frame matches the target frame. Delegation creates a distinct
target operation and grants no implied coordinate, admission, or execution
authority across frames.

### AB object

A stable semantic object in an abstraction frame. It describes a contract,
primitive, skill, composition, or governed system boundary independently of the
method, topic, endpoint, or provider that happens to implement it.

An object's level follows the atomicity rule of its frame. Internal step count,
implementation complexity, or delegation to an object in another frame does
not promote the object automatically.

### AB implementation binding

A versioned pointer from one AB object to one environment representation. A
binding records the implementation owner, interface kind, locator, source
revision, schemas, evidence adapter, runtime modes, and lifecycle status.

Changing a binding must not silently change the AB object. Multiple bindings may
represent the producer, contract, consumer, fake implementation, or live
implementation of one semantic object.

Bindings begin as `candidate`. Only an explicitly `approved` binding can be
resolved for use. Discovery may propose candidate bindings; discovery is never
authorization, semantic truth, or evidence.

### Semantic owner

The package or environment component declared by the AB registry as
authoritative for an object or effect. The semantic owner is distinct from a
binding's implementation owner. For example, `chatbot_llm` may implement the
publisher side of `/planner/request` while `planner_llm` remains the registry
owner of that interface.

An executable AB1 binding may issue effect evidence only when its implementation
owner is the semantic effect owner.

### Interaction module

The minimal, task- and role-scoped projection of inspectable and directly
controllable AB objects presented to a model or worker.

### Task spec

A frozen `uah.task_spec/v2` intent created for one accepted task start. It pins
task and trace lineage, task type, role, frame, DomainContractPack revision,
requested effects, prohibited effects, and finite budgets. Resume and notify
ingress reuse the compiled task rather than compiling a replacement.

### Compiled task

The content-addressed `uah.compiled_task/v2` artifact produced once from an
accepted start-task decision, TaskSpec, role, frame, registry, and
DomainContractPack. It is the shared source of the interaction module, effect
obligations, prohibited effects, and budgets for prompt compilation, semantic
admission, task acceptance, and replay.

### Agent role configuration

An immutable, reusable definition that fixes an agent role, domain, abstraction
frame, projected AB objects, binding policy, control band, budgets, and
authority policy. It does not select a model, prompt pack, or harness build.

### Model configuration

An immutable definition of the model artifact, provider runtime, decoding
parameters, and declared protocol capabilities used by an agent.

### Model admission profile

The provider-neutral capability, behavior, and evaluation requirements a model
must satisfy to embody one agent role. Deployment policy may further restrict
eligible providers and hardware placements.

### Provider pool

The registered supply of compatible model runtimes from which UAH may allocate
capacity. Membership describes availability and placement, not agent identity.

### Model instance

One loaded local model process, endpoint replica, or provider allocation that
can serve a declared model configuration. It is a runtime resource rather than
an agent.

### Model lease

A bounded reservation of one model instance for an agent run, task, or model
invocation under declared resource and isolation constraints.

### Model invocation

One identified prompt-to-output call made by an agent run using a model lease.
It records the exact model instance and artifacts used but does not own agent
state.

### Registration preflight

A non-reserving validation that an agent manifest, role, provider policy, and
declared resource requirements are compatible. It never loads or invokes a
model.

### Startup preflight

A readiness evaluation performed after a model lease is acquired and before an
agent run accepts work. It may use bounded liveness and role-shaped probes but
does not establish task capability.

### Agent

An immutable embodiment whose manifest composes one agent role configuration
with one model configuration, prompt pack, and harness build. Changing any
member of that composition creates a different agent.
_Avoid_: Agent instance; runtime instance

### Agent handle

A stable human-facing or deployment-facing identity that resolves through an
immutable revision to one active agent. Rebinding preserves the role contract
but requires fidelity evaluation and rollback lineage. The current H1 slice
registers only the initial revision and refuses rebinding. H3 owns qualified
revision promotion.

### Agent registration

The publication of an immutable agent embodiment and, when requested, a handle
revision. Registration creates no agent run, model lease, or model invocation.

### Agent run

One bounded activation of an agent, attached to exactly one environment run.
It owns activation-scoped state and may span several domain tasks, model
leases, and model invocations until shutdown, failure, or replacement ends the
activation.
_Avoid_: Agent embodiment; model invocation; turn

The current `AgentRunRegistry` implements only in-memory roster-bound
attachment in `attached_standby`. Termination, replacement, persistence,
lifecycle events, preflight, and model leasing remain open.

### Agent standby

The state of an active agent run that remains attached to its environment and
retains activation-scoped continuity without holding a model lease or executing
an invocation.
_Avoid_: Stopped agent; unloaded model

### Environment run

One bounded activation of a concrete domain environment that groups the agent
runs, tasks, traces, and native evidence produced while that environment is
active. Restarting or replacing the environment creates a new environment run
even when its domain contracts and participating agents are unchanged.
_Avoid_: Domain; environment profile; session

### Environment profile

A reusable frozen domain runtime contract that pins a DomainContractPack
revision, native runtime and owner, required interfaces, and a stable
agent-handle roster. Activating the profile produces a new environment run.
The current `EnvironmentProfile` is validated in memory but is not itself
content-addressed or serializable.

### Environment ingress

A content-addressed `uah.environment_ingress/v1` observation, request, or
feedback item received from an approved environment binding during an
environment run. Its artifact identity covers binding, ingress type, payload
artifact, native lineage, observation time, and environment activation.
Ingress is not automatically a task, trace, model invocation, or execution
authority.
_Avoid_: Prompt; task

### Task ingress authority

The deterministic `TaskIngressAuthority.admit(environment_run, ingress)` module
that associates environment ingress with state updates, new tasks, resumed
tasks, notifications, or rejection. It owns rule matching, deterministic task
and trace identities, duplicate fencing, and ledger append for accepted
task-bearing ingress. State updates, ignored items, and rejected items do not
yet have environment-scoped ledger facts. A model may interpret admitted
content but cannot rewrite its task or trace lineage.

A new task preserves the domain-owned task identifier selected from a named
native-lineage field in the reviewed ingress rule. The task identity is scoped
by `environment_run_id`. UAH derives the initial `trace_id` from the trace
scheme version, environment run, and domain task identity. Resume and notify
classification resolve registered lineage and cannot infer it from model
output or an unregistered ingress item.

### Task ingress decision

A content-addressed `uah.task_ingress_decision/v1` classification result. An
accepted `start_task` decision records the exact DomainContractPack revision,
environment activation, starting ingress artifact, task, and trace. Its fields
alone do not authorize compilation. `TaskSpecCompiler` also requires the
matching task start to exist in the common lifecycle ledger through
`EnvironmentTaskRegistry.require_start(...)`.
The task-start event stores the ingress artifact ID, decision ID, and frozen
domain-pack revision. The raw task-start fact is internal to the ledger
projection; callers cannot authorize compilation through a public raw-lineage
registration method.

### Environment task registry

The read-only environment-scoped projection of immutable task and trace lineage
from the common ledger. `TaskIngressAuthority` rejects replayed task-bearing
ingress and a second start for the same domain task within one environment run.
Resume and notify ingress may reuse a lineage only when the task is registered
under that exact environment activation. Acceptance-derived terminal states
reject later ingress. A suspended acceptance remains resumable. The registry
has no task-ingress write interface and does not prove native effects.

### Trace event

A content-addressed `uah.trace_event/v1` fact in the globally sequenced common
lifecycle ledger. It carries environment, task, trace, optional operation and
causal-parent identities, immutable artifact references, a timestamp, and a
minimal canonical replay projection. Each event also carries `commit_id`,
`commit_index`, and `commit_size`, so strict reload rejects an incomplete or
noncontiguous multi-event fact. Task start, resume, notification,
compilation, proposal, admission, operation edge, lease, budget, execution,
evidence, cancellation, timeout, retry, obligation, and terminal-acceptance or
rejection events currently use this envelope. Cooperating writers use
cross-process advisory locking. Proposal, semantic, domain, and evidence
rejection facts are implemented. Stale-evidence and false-completion policy,
scoped actor events, and the model runtime remain open.

### Prompt compiler

The planned deterministic assembler of the universal UAH protocol, role
contract, versioned domain policy, task-scoped AB projection, and current task
context. It will produce model-facing context but grant no execution authority.
No executable PromptCompiler exists in the current H0/H1 slice.

### Prompt pack

An immutable, versioned wording and output-format artifact selected by an agent
manifest. Changing the prompt pack creates a different agent identity even when
the agent role configuration is unchanged.

### Skill artifact

A versioned instruction package that may implement an AB object through an
approved binding in a named abstraction frame. An AB object need not have a
skill artifact, and a skill artifact has no global AB level.

### Capability pack

A versioned, role-selectable allowlist of AB objects and binding policies within
one named abstraction frame. A pack may be required, optional, or forbidden by
an agent role configuration, but it does not create cross-frame equivalence.

### Domain contract pack

An environment-owned semantic package rather than executable domain code. The
implemented `uah.domain_contract_pack/v1` identity covers the pack and frame
IDs, registry version, allowed roles, supported task types, ingress rules,
effect-to-object and evidence-owner rules, failure policy, and prohibited
effects. Changing any covered rule changes its SHA-256 revision. Frames, AB
objects, binding catalogs, minimal prompt policy, and qualification cases
remain separate artifacts in the current slice; the longer-term onboarding
contract may package them together after owner review. Assisted onboarding may
propose a pack but cannot approve it.

### Proposal

A content-addressed `uah.typed_proposal/v1` normalized from one raw model-output
artifact. It requests exactly one operation under a compiled task and carries
task, trace, operation, object, output-type, and canonical argument lineage. It
is not execution and cannot prove an effect. Model-authored effect claims are
rejected during normalization.

### Admitted operation

An immutable, content-addressed `uah.admitted_operation/v2` proving that a typed
proposal passed UAH semantic admission for one compiled task, role, frame, AB
object, approved binding revision, validated input-schema identity, argument
set, runtime mode, and evidence obligation set. It still has no domain
execution authority.

### Admission rejection

`uah.semantic_admission_rejection/v1` and
`uah.domain_admission_rejection/v1` are content-addressed operation-scoped
facts with ordered stable reason codes. Semantic rejection proves that no
`AdmittedOperation` was issued for that decision. Domain rejection proves that
the environment owner did not issue an execution lease for that request. Domain
admission records its own rejection. Semantic rejection becomes replayable
when the coordinating caller appends the returned artifact. O1 exposes both as
nonterminal failure stages and does not relabel either as terminal task
rejection.

### Execution lease

A content-addressed `uah.execution_lease/v1` issued by the domain lifecycle
owner after rechecking the environment activation, binding environment,
DomainContractPack revision, operation deduplication, and readiness attestation.
The lease authorizes exactly one admitted operation, is distinct from semantic
admission, and cannot change the admitted value. The in-process owner accepts
no direct object/argument call. It consumes the lease by durably recording
`execution_started` before invoking the native handler, then records either a
content-addressed execution receipt or a typed execution failure. A new owner
instance cannot consume the same operation lease again from the same ledger.
Replay checks each receipt and evidence artifact against the recorded
admission ID, object, binding, and evidence owner. Terminal acceptance must
name the complete evidence set recorded for the trace; omitted or unrecorded
evidence is rejected.

### UAH trace

The causally connected, potentially cross-agent record of one domain workflow
inside an environment run. A trace may contain events from several agent runs,
AB operations, and domain-lifecycle references, but it is not a conversation
session or an authority source.

### Trace projection

A derived, read-only view of one UAH trace filtered by actor, role, handle
lineage, frame, task, or operation. Agent and environment views are projections
of the same causal record rather than separately authored traces.
_Avoid_: Agent trace; environment trace

### Operation

One identified AB-object request within a UAH trace as it moves through
proposal, semantic admission, domain lifecycle admission, execution, and
owner-issued evidence.

### Operation edge

A governed relationship between two operations. `decomposes_to` refines an
object inside one abstraction frame, `delegates_to` crosses into another frame
through an explicit role or handle and typed artifact contract, and
`continues_with` records workflow order without claiming decomposition.

### Effect evidence

An owner-issued observation tied to the object, binding, environment, and
execution result that produced it. Successful model text is not effect
evidence.

### Effect obligation

A typed task requirement naming an expected effect, its evidence rule, owner,
freshness policy, and whether satisfaction is required or best effort. An
operation result may satisfy one obligation without deciding the task outcome.

### Task acceptance

The deterministic terminal judgment compiled from a task's effect obligations.
All required obligations must be satisfied; an unsatisfied best-effort
obligation is retained as a deficit without invalidating otherwise complete
work. `suspended` is explicitly nonterminal because required evidence remains
pending.
_Avoid_: Plan completed; model-declared completion

### Verified trace digest

A deterministic, model-free projection of immutable task, operation,
admission, execution, evidence, and effect-obligation events. Observatory and
NeuralWorkbench may index or display the digest, but the lifecycle ledger
remains authoritative and model-authored reflection is excluded.

### Memory policy

A versioned rule that limits which verified trace digests an agent may inspect
or retrieve by domain, environment profile, frame, role, task family, object,
outcome, and approved handle lineage. The policy grants read scope only and
does not transfer evidence or execution authority.

### Lifecycle ledger

The append-only source of UAH lifecycle events and artifact references across
task compilation, proposal, admission, lease, execution, evidence, and
terminal judgment. The implemented `LifecycleLedger` owns global sequence,
causal parent, canonical JSONL persistence, strict reload, optimistic sequence
checks, atomic commit framing, transition validation, cross-process advisory
writer locking, and replay-derived `VerifiedTraceDigest` artifacts. Each
cooperating writer reloads and validates the stream while holding the lock
before it appends and flushes a fact. The ledger records authority decisions
but does not make them. Initial pre-dispatch cancellation, recorded timeout,
retry, and runtime-budget facts are present; in-flight interruption and
task-level closure policy for those facts remain open.

Observatory O1 now consumes replay-stable ledger events through immutable trace
projections and a self-contained static HTML renderer. It distinguishes
terminal task status from recoverable admission or execution failures and
labels recorded, synthetic, conceptual, measured, or reviewed data. O1 never
appends lifecycle facts, issues evidence, or changes admission.

### Recorded qualification

A deterministic replay of frozen chatbot and planner outputs through
`CompiledTask`, operation normalization, semantic admission, domain lease
issuance, the lease-only fake environment owner, task acceptance, common-ledger
reload, and verified digest construction. It validates harness mechanics
without claiming live-node or model capability.

### Boot qualification

A short deterministic check that one immutable model-harness-environment
configuration is ready and has sufficient resource and protocol headroom to
accept bounded work. Passing boot does not prove general agentic capability.

### Promotion qualification

A repeated, held-out evaluation that may approve a configuration, binding, or
AB proposal after quality, safety, regression, provenance, owner-review, and
rollback requirements pass.

### Runtime evaluation

Continuous observation of a promoted configuration. Runtime evaluation may
continue, degrade, quarantine, interrupt, or roll back a configuration. It may
generate candidates but may not promote them.

### Neural Workbench candidate

An untrusted, reversible pulse, retrieval policy, recovery hint, binding, or
higher-order AB proposal derived from traces. It remains quarantined until
replay, counterexamples, disjoint holdouts, owner review, provenance, and
rollback gates pass.

### Neural Workbench attachment

An optional adaptive-engine relationship that receives bounded frame-relative
search requests and completed trace observations from UAH. It returns
candidate artifacts with no admission, execution, or promotion authority.

### Neural Workbench search

The bounded construction and comparison of a mechanism-diverse candidate
portfolio within one supplied abstraction frame. Candidate sources may include
deterministic templates, host-model generation, retrieved-and-adapted traces,
and hybrids. Search includes deterministic verification, auditable scoring,
selection, and provenance. It is not synonymous with deterministic lookup and
does not confer execution authority.

### Typed action memory

An indexed store of complete operation and trace experience, including support,
counterexamples, outcomes, evidence, frame-relative AB coordinates, and exact
configuration provenance. It is distinct from conversation history. H3 may use
it to retrieve and adapt candidates or context; it cannot mutate the active
task, trusted registry, or admission state.

### Crystallization

The H4 process that turns repeated, causally supported structures into reviewed
higher-order candidate artifacts. Frequency is supporting evidence only.
Replay, counterexamples, disjoint holdout, owner review, provenance, and
rollback are required before any trusted promotion.

## Reference NAO ownership

| Concern | Owner |
| --- | --- |
| Dialogue lifecycle and speech | `dialogue_manager` |
| User-facing response, route, grounding projection, planner handoff | `chatbot_llm` |
| Planning, supervision, replanning, planner dialogue acts | `planner_llm` |
| Deterministic admission, dispatch, lineage, feedback | `nao_orchestrator` |
| Scene observations | `nao_scene_grounding` |
| Runtime effect evidence | The invoked AB1 skill owner |

The UAH mounts these semantics; it does not absorb or replace their ownership.
