# Universal Agentic Harness Domain Model

This file records the project vocabulary that should remain stable across code,
documentation, evaluations, and environment adapters.

## Core terms

### Abstraction frame

The frame-relative coordinate system that says what counts as an atomic object
for one substrate. An AB level has meaning only inside its named frame. It is
not a global intelligence or capability score.

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

### Proposal

A typed model output that requests an operation. It is not execution and cannot
prove an effect.

### Effect evidence

An owner-issued observation tied to the object, binding, environment, and
execution result that produced it. Successful model text is not effect
evidence.

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
