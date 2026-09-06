# Universal Agentic Harness Domain Model

This file records the project vocabulary that should remain stable across code,
documentation, evaluations, and environment adapters.

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

### AB object

A stable semantic object in an abstraction frame. It describes a contract,
primitive, skill, composition, or governed system boundary independently of the
method, topic, endpoint, or provider that happens to implement it.

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

### Agent

An immutable embodiment whose manifest composes one agent role configuration
with one model configuration, prompt pack, and harness build. Changing any
member of that composition creates a different agent.
_Avoid_: Agent instance; runtime instance

### Agent handle

A stable human-facing or deployment-facing identity that resolves through an
immutable revision to one active agent. Rebinding preserves the role contract
but requires fidelity evidence and rollback lineage.

### Agent run

One bounded activation of an agent under one agent role configuration. It owns
activation-scoped state and contains domain tasks until shutdown, failure, or
replacement ends the activation.
_Avoid_: Agent embodiment

### Prompt compiler

A deterministic assembler of the universal UAH protocol, role contract,
versioned domain policy, task-scoped AB projection, and current task context.
It produces model-facing context but grants no execution authority.

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

An environment-owned, content-addressed package of abstraction frames, AB
objects, binding policy, evidence rules, minimal domain prompt policy, and
qualification cases. Assisted onboarding may propose one but cannot approve it.

### Proposal

A typed model output that requests an operation. It is not execution and cannot
prove an effect.

### Admitted operation

An immutable UAH-issued value proving that a typed proposal passed semantic
admission for one role, frame, object, binding, argument set, and evidence
obligation. It still has no domain execution authority.

### Execution lease

A domain-owner decision authorizing one admitted operation after native
lifecycle checks. The lease is distinct from semantic admission and cannot
change the admitted operation.

### UAH trace

The causally connected record rooted in one admitted interaction or workflow.
A trace may contain several AB operations and domain-lifecycle references, but
it is not a conversation session or an authority source.

### Operation

One identified AB-object request within a UAH trace as it moves through
proposal, semantic admission, domain lifecycle admission, execution, and
owner-issued evidence.

### Effect evidence

An owner-issued observation tied to the object, binding, environment, and
execution result that produced it. Successful model text is not effect
evidence.

### Lifecycle ledger

The append-only source of UAH lifecycle events and artifact references across
prompt compilation, proposal, admission, lease, execution, evidence, and
terminal judgment. It records authority decisions but does not make them.

### Recorded qualification

A deterministic replay of frozen chatbot and planner outputs through the UAH
projection, gates, mounted fake environment owner, and terminal evidence check.
It validates harness mechanics without claiming live-node or model capability.

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
