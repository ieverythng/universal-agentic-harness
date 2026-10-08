# Observatory Contract

**Status:** O1 environment/task/trace index and explicit actor rendering implemented;
complete configuration comparison and O2 deferred
**Date:** 2026-10-04
**Applies to:** UAH H0-H6 and NeuralWorkbench H3+

## 1. Decision

The product-facing trace surface is called **Observatory**.

O1 is a small, read-only API with a static HTML renderer. It is required for
H1 lifecycle debugging and H2 NAO parity. O2 is the proper interactive
implementation and may evolve through H4 before H5 product polish.

Observatory is never an execution owner, evidence issuer, policy gate, or
registry authority.

Trace emission and trace inspection are separate authorities. The UAH kernel
records every admitted lifecycle automatically. A model receives Observatory
access only through an explicit, task-scoped, read-only frame projection.

## 2. Authority and Data Flow

```mermaid
%% uah-render: Figure 1. Admission, execution, and Observatory data flow
flowchart TB
    Prompt["Model-facing Prompt + Schemas<br/>immutable compiled artifact"]:::projection
    Model["Model Output<br/>raw immutable artifact"]:::model
    Normalize["Proposal normalization<br/>proposal or typed rejection"]:::compiler
    Proposal["TypedProposal<br/>operation request"]:::proposal
    Semantic["UAH Semantic Admission<br/>role + frame + object + binding"]:::gate
    Admitted["AdmittedOperation<br/>immutable semantic value"]:::gate
    Domain["Domain Lifecycle Admission<br/>readiness + dedupe + fencing"]:::domain
    Lease["ExecutionLease<br/>owner-granted authority"]:::execution
    Control["H1 Runtime Control<br/>budget + cancellation + timeout"]:::gate
    Owner["Environment Owner<br/>native execution"]:::execution
    Evidence["Result + Evidence Decision<br/>accepted or rejected"]:::evidence
    Acceptance["Task Acceptance<br/>explicit terminal authority"]:::gate
    Ledger["Lifecycle Ledger<br/>append-only events + artifacts"]:::trace
    Observatory["Observatory O1/O2<br/>read-only views"]:::observatory
    Workbench["NeuralWorkbench H3+<br/>candidate analysis only"]:::compiler
    Prompt --> Model
    Model --> Normalize
    Normalize --> Proposal
    Proposal --> Semantic
    Semantic -->|accepted| Admitted
    Admitted --> Domain
    Domain -->|leased| Lease
    Lease --> Control
    Control --> Owner
    Owner --> Evidence
    Evidence --> Acceptance
    Acceptance --> Ledger
    Ledger --> Observatory
    Ledger --> Workbench
```

The diagram shows the authority order. The current ledger records accepted and
rejected proposal, admission, evidence, control, obligation, and terminal task
facts. Semantic rejection is appended explicitly by the coordinating caller;
domain rejection is appended by the domain lifecycle owner. Neither
Observatory nor NeuralWorkbench sits in the execution call chain.

## 3. Layered Visualization Contract

| Layer | Required views | Source of truth |
| --- | --- | --- |
| UAH H0-H2 | domain and environment-run index; environment, task, actor, and operation-graph views; configuration, frame, role, projected AB graph, bindings, proposals, gates, owner evidence, obligation status, failures, terminal state, replay comparison | UAH registry snapshots and lifecycle ledger |
| NeuralWorkbench H3 | pulse candidates, verification failures, energy terms, entropy proxy, retrieval lineage, counterexamples, recommendation, shadow replacement comparison | versioned Workbench request/candidate/observation payloads |
| H4 review | crystallization clusters, counterfactual results, holdout results, provenance, promotion review, rollback lineage | quarantined candidate and review artifacts |
| H5 product | cross-domain and cross-runtime navigation, capability/configuration comparison, live streams | conformance-qualified adapters and immutable traces |

## 4. O1 API

The complete O1 contract accepts immutable, JSON-compatible inputs and returns
a self-contained review document:

```text
render_observatory(
  registry_snapshot,
  configuration_manifest,
  lifecycle_events,
  workbench_payloads = optional,
  comparison_run = optional
) -> ObservatoryDocument
```

`ObservatoryDocument` contains:

- one static HTML payload;
- trace and configuration identities;
- source revisions and protocol compatibility state;
- filter facets for environment run, task, actor agent run, role, object,
  owner, gate outcome, event type, and failure stage;
- ordered event cards with inspectable raw payloads;
- graph data embedded as inert JSON for later O2 reuse.

The implemented 2026-10-04 slice is narrower:

```text
render_observatory(
  validated_ledger_or_event_collection,
  title = optional,
  data_label = inferred
) -> ObservatoryDocument
```

It retains the global ordered event collection and indexes immutable
`TraceEvent` values as `environment_run_id -> task_id -> trace_id`, with
separate actor views keyed by explicit `agent_run_id`. An environment with only
actor events remains visible without a fabricated task or trace. The projection
verifies consistent task, trace, and actor environment lineage and derives
terminal task status only from explicit terminal facts,
retains nonterminal failure stages, escapes displayed payloads, and embeds an
inert graph payload. Graph JSON contains lifecycle-event nodes, explicit
operation nodes, `ledger_parent_event` edges, and only recorded operation
relations. A `recorded` label requires a validated `LifecycleLedger`;
an arbitrary event collection defaults to `synthetic`. Configuration comparison
and the remaining identity facets are not implemented. Static index links,
search, and event-type filtering cover recorded actor event cards alongside
task trace cards. A v1 task event is not assigned to an actor by matching names
or nearby events.

### Target mandatory identity envelope

The H1/H2 Observatory contract requires every lifecycle event to carry or
resolve the following identities without heuristic reconstruction. The current
H0 envelope implements only the subset documented below:

| Identity | Scope |
| --- | --- |
| `role_configuration_id` | Immutable semantic role, model admission profile, primary frame, auxiliary frame allowlists and access modes, authority and capability packs |
| `model_configuration_id` | Model artifact, runtime and decoding contract |
| `agent_handle_id`, `agent_handle_revision_id` | Stable routed identity and the immutable active-agent mapping resolved for this run |
| `agent_id` | Immutable role, model, prompt pack and harness composition |
| `environment_profile_id`, `environment_run_id` | Reusable native-environment contract and one attested activation that groups agent runs, tasks, traces, and native evidence |
| `environment_ingress_id` | One immutable native observation, request, feedback item, or control stimulus before deterministic task association |
| `agent_run_id` | One bounded actor activation attached to exactly one environment run; it may span many tasks, leases, and invocations |
| `provider_pool_id`, `resource_snapshot_id` | Runtime supply considered and the measured capacity state used by allocation |
| `model_instance_id`, `model_lease_id` | Loaded process or endpoint replica and its bounded reservation |
| `model_invocation_id` | One exact prompt-to-output call joining an agent run, trace and model lease |
| `registration_preflight_id`, `startup_preflight_id` | Non-reserving compatibility result and post-lease readiness result |
| `trace_id` | One causally connected workflow containing one or more operations |
| `domain_id`, `task_type_id`, `task_id` | Domain namespace, task family and work instance |
| `operation_id`, `parent_operation_id`, `operation_relation` | One frame-relative AB-object lifecycle, related operation, and governed edge type such as decomposition or delegation |
| `proposal_id`, `admission_id`, `execution_lease_id` | Proposal, UAH semantic decision and domain-granted authority |
| `event_id`, `parent_event_id`, `sequence`, `commit_id`, `commit_index`, `commit_size` | Append-only event ordering, causality, and atomic multi-event fact framing |

Each operation also records `frame_id`, `registry_version`, `ab_object_id`,
`binding_id`, prompt and projection hashes, evidence obligations, native domain
lineage, and owner-issued result references.

One `trace_id` may include several actor agent runs. The environment, task,
handle, and actor views are query projections over one append-only ledger. They
must not become independent trace stores whose ordering or terminal judgments
can diverge.

### Target lifecycle event families

```text
registration_preflight_started | registration_preflight_passed | registration_preflight_failed
agent_registered
agent_handle_revision_promoted | agent_handle_revision_rolled_back | agent_handle_resolved
environment_run_start_requested | environment_run_attested | environment_run_ready | environment_run_failed
environment_ingress_recorded | environment_ingress_classified | environment_ingress_rejected
task_started | task_compiled | task_resumed | task_notified | environment_state_updated
agent_run_start_requested | agent_run_initializing | agent_run_attached
model_lease_requested | model_lease_acquired | model_lease_rejected
startup_preflight_started | startup_preflight_passed | startup_preflight_failed
agent_run_ready | agent_run_standby | agent_run_startup_failed
prompt_compiled
model_invocation_started | model_invocation_completed | model_invocation_failed
model_output_recorded
proposal_normalized | proposal_rejected
semantic_admission_accepted | semantic_admission_rejected
domain_admission_leased | domain_admission_rejected
execution_started | execution_feedback
execution_completed | execution_failed | execution_cancelled
evidence_issued | evidence_rejected
operation_edge_recorded
budget_granted | budget_exhausted
task_timeout_recorded
retry_approved | retry_not_retryable | retry_exhausted
effect_obligation_satisfied | effect_obligation_failed | effect_obligation_pending
task_suspended | terminal_task_accepted | terminal_task_accepted_with_deficit | terminal_task_rejected
model_lease_released
agent_run_detached | agent_run_terminated
environment_run_closing | environment_run_closed
```

The current H0 `LifecycleLedger` is the single writable trace authority. Its
content-addressed `uah.trace_event/v1` envelope supplies global sequence,
recorded time, causal parent, environment/task/trace/operation lineage,
artifact references, canonical replay data, and atomic `commit_id`,
`commit_index`, and `commit_size` positions. Task registration is a ledger
projection rather than a second task event store. Strict JSONL reload rebuilds
task and operation state after restart and rejects incomplete or interleaved
multi-event facts. Cooperating processes serialize reload, transition
validation, append, and `fsync` through an OS advisory lock. Crash recovery for
an interrupted multi-event append still rejects the incomplete commit rather
than repairing it automatically.

The v1 task envelope remains:

```text
schema_version, event_id, sequence,
commit_id, commit_index, commit_size,
recorded_at, event_type,
environment_run_id, task_id, trace_id, operation_id,
parent_event_id, artifact_refs, data_json
```

`uah.trace_event/v2` adds explicit `event_scope` and `agent_run_id` to that
envelope. Agent-scoped facts use null task and trace identities and no operation
identity. New task-scoped invocation facts preserve real task/trace lineage and
carry the actor. Older v1 events retain their serialized identity and have no
inferred actor. `data_json` remains a canonical JSON object serialized as a
string. Attachment embeds the pinned manifest, handle revision, environment
profile, and attestation; model allocation and startup events preserve exact
leases, resource snapshots, and owner readiness reports. Dynamic provider pool
and scheduler identities remain H3 work. Operation nodes and
`uah.operation_edge/v1` identities are emitted when their source facts are
recorded.

The O1 static renderer now covers environment/task/trace grouping, ordered actor
cards, explicit terminal
status, failure-stage visibility, searchable event cards, and inert graph JSON
for accepted, rejected, actor, control, and operation-edge families. Later
configuration, stale-evidence, and false-completion views follow their
replay-stable event contracts. This order
keeps traceability available during H1 development without making Observatory a
writer or a prerequisite for ledger correctness.

The committed recorded-NAO page is a qualification artifact rendered through the
O1 static index. Validated records are indexed as `environment_run_id -> task_id
-> trace_id`, and each trace can be inspected independently. Actor events use
their explicit activation IDs and remain outside fabricated task traces. Domain
or environment-profile navigation likewise requires explicit recorded identity;
the renderer must not infer either value from a title, adapter package, or trace
payload. Live filtering, graph exploration, comparison, and cross-environment
navigation remain O2 work.

The implemented `uah.domain_contract_pack/v1` revision covers its role/task
allowlists, ingress rules, effect-to-object and evidence-owner rules, failure
policy, and prohibited effects. `uah.environment_ingress/v1` and
`uah.task_ingress_decision/v1` are also content-addressed, and the decision
binds the ingress artifact identity. Compilation requires matching task-start
fields in the lifecycle ledger. SPEC-02 remains open because public raw facts
can populate those fields without authentic admitted-ingress provenance. A
content hash or matching fields alone cannot close that authority gap.
The task-start event preserves the
ingress artifact ID, decision ID, and domain-pack revision; the registry does
not expose a raw task-start mutation method; the common ledger still accepts
raw `TaskStartedFact` values, which is the separately tracked SPEC-02 gap.

The H0 `CompiledTask` is now a content-addressed artifact binding start-task
ingress, task and trace lineage, role, frame, registry, DomainContractPack,
closed interaction projection, effect obligations, prohibited effects, and
retry-aware budgets. Tool-call consumption is enforced atomically at dispatch,
and model-call consumption is atomic with provider invocation start. The accepted
tracer records its `task_compiled` event separately from proposal, admission,
lease, evidence, and terminal judgment. The recorded NAO tracer does not invoke
a provider. The new H1 invocation fixture records the compiled prompt inside
the exact invocation request, then preserves typed raw-output completion or
failure. A standalone `prompt_compiled` event remains a target family rather
than an emitted fact.

The current H0 authority slice also emits content-addressed
`uah.typed_proposal/v1`, `uah.admitted_operation/v3`,
`uah.execution_lease/v1`, and `uah.operation_edge/v1` artifacts.
`AdmittedOperation` pins the reviewed input-schema identity and the exact
frame-relative object snapshot. Its full current artifact is recorded for
identity verification on replay. Historical metadata-only events remain
readable. Original R4 probes exposed replay downgrade and active old-object
consumer gaps. The separately reviewed [nested-owner gate](../artifacts/reviews/2026-10-08_uah_r4_nested_owner.md)
now approves the concrete-artifact correction and its historical read-only
controls. This does not establish release-wide provenance or causal completeness.
Accepted values are appended as distinct proposal,
semantic-admission, and domain-admission events. Semantic rejection is appended
by the coordinating caller; the domain owner appends its own rejection. The
environment owner accepts only the exact lease,
records execution start before native dispatch, and emits a content-addressed
receipt containing separate native result and normalized evidence artifacts.
Replay verifies receipt admission, object, binding, and evidence-owner lineage.
Terminal acceptance must reference the complete recorded evidence set rather
than a caller-selected subset.
Accepted, best-effort-deficit, and required-effect-rejected traces replay into
deterministic `VerifiedTraceDigest` values. Proposal, semantic, domain, and
evidence rejection remain nonterminal operation facts. Budget exhaustion,
pre-dispatch cancellation, recorded timeout, and retry outcomes are visible
without inventing terminal task status. Stale evidence and false-completion
events remain incomplete. O1 does not infer absent failure or terminal events.

The current raw-iterable conformance repair reconstructs detached `TraceEvent`
values through the existing owner's constructor before ordering, actor grouping
and status derivation. It validates both versioned shape and content identity.
The earlier identity-only repair returned CHANGES because v1 actor/scope fields
are excluded from its hash but prohibited by its constructor. Valid raw
illustrative inputs remain distinct from validated ledger-origin records.
Content identity alone proves neither causal prerequisites nor measured/reviewed
provenance; ARCH-02 label conformance remains open. Both fresh independent
reviews approve this bounded repair at its frozen source/dependency bytes,
as recorded in the [O1 conformance receipt](../artifacts/reviews/2026-10-08_uah_o1_conformance_fix.md).
Current integration also passes after inspection of the concurrent lifecycle
diff, which leaves TraceEvent's constructor, schema, identity and export
contracts unchanged. Approval does not establish the complete O1 exit.

This is the common startup-to-task order, not a rule that every lease ends with
one task. A lease may be invocation-, task-, or run-scoped; its declared scope
determines the release edge.

The raw model output, normalized proposal, `AdmittedOperation`, execution lease,
native owner result, normalized evidence, and terminal judgment remain distinct
artifacts. Observatory may place them beside each other but may not collapse
them into one generated summary.

`execution_feedback` is evidence-bearing input, not terminal proof by name. A
task closes only after the task acceptance evaluator compares its immutable
required and best-effort obligations with owner-issued evidence. A failed
best-effort report may therefore produce `accepted_with_deficit` while a failed
required manipulation effect produces rejection or suspension. The operation
that succeeded remains succeeded even when a later reporting operation fails.

The first renderer may reuse the proven NAO `interaction_trace_viewer` pattern:
JSONL ingestion, normalization, searchable cards, and static HTML. UAH must
replace dialogue-only correlation heuristics with explicit configuration,
trace, task, frame, proposal, binding, evidence, replay, and Workbench IDs.

### NAO viewer assimilation boundary

The 2026-08-04 source audit found four pieces worth porting as behavior, not as
a ROS dependency:

| Reuse in O1 | Do not inherit |
| --- | --- |
| Frozen normalized event records | ROS subscriptions and `rosout` parsing |
| Append-only JSONL plus deterministic load | A trace ID synthesized from whichever topic arrives first |
| Searchable static cards with raw payload inspection | An AB level guessed from the presence of a skill name |
| Channel-specific normalization and concise summaries | Treating planner dialogue or robot speech as universally terminal |

O1 assigns distinct event types to the existing authority seams:

- `/nao_orchestrator/planner_request` -> `planner_gate_request`;
- orchestrator gate decision -> `planner_gate_accepted` or
  `planner_gate_rejected`;
- `/planner/request` -> `planner_request_admitted`;
- `/intents` -> `planner_output_candidate`;
- `/planner/execution_feedback` -> owner/execution lifecycle events;
- `/planner/dialogue_act` -> planner communication request, never direct speech
  proof.

The NAO `report_result` flow remains one causal trace. The planner-owned AB1
operation may delegate grounded language composition to the chatbot agent run,
which receives its own operation and model-invocation identities. The returned
text cannot prove robot motion or manipulation. Native report dispatch and
speech evidence remain owned by the NAO runtime.

The source `goal_id`, `request_id`, `plan_id`, `plan_version`, and `step_id`
remain payload lineage. UAH role, model, agent, run, trace, operation, and event
identities are mandatory envelope fields and are never reconstructed
heuristically.

## 5. Graph Grammar

Graph nodes may represent:

- AB objects and decomposition relations;
- environment components and implementation bindings;
- proposals, pulse programs, verification decisions, and evidence artifacts;
- complete model-harness-domain configurations;
- trace clusters and reviewed candidate abstractions.

Graph edges must declare a type such as `decomposes_to`, `delegates_to`,
`continues_with`, `bound_by`,
`proposed_by`, `admitted_by`, `leased_by`, `rejected_by`, `executed_by`,
`evidenced_by`, `supersedes`, `retrieved_from`, or `compared_with`. A visual
edge may not imply authorization or causality unless the underlying event or
contract proves it.

An operation node has exactly one source coordinate `(frame_id, ab_object_id,
ab_level, registry_version)`. A parent operation may decompose into children at
other levels in the same frame. `decomposes_to` never crosses a frame boundary.
Cross-frame work uses `delegates_to` and records the source operation, target
frame, target role or handle, closed input artifact, expected output artifact,
and authority boundary. `continues_with` records ordered workflow progression
without claiming abstraction decomposition.

The v1 ledger accepts an edge only after both endpoint operations have been
normalized and semantically admitted with matching frame identities. It
rejects duplicate pairs, cycles, a second structural parent, and edges recorded
after the target lease. Same-frame decomposition and continuation are
executable. Cross-frame delegation remains fail-closed until the target has a
separately compiled projection and explicit artifact contract.

## 6. Metrics and Honesty Rules

Every metric is keyed by the complete content-addressed configuration. Model
family names alone are not aggregation keys.

Metric values carry one of these labels:

- `conceptual`: explanatory geometry with no runtime measurement;
- `synthetic`: generated evaluation data;
- `recorded`: replayed fixture or captured runtime data;
- `measured`: evaluator-produced result under a frozen configuration;
- `reviewed`: measured result accepted through the applicable gate.

Conceptual NeuralWorkbench capability-space, energy-landscape, entropy, and AB
maturity figures are design references. Observatory may reproduce their visual
grammar, but it must never present synthetic or conceptual values as runtime
evidence.

## 7. O1 Exit Gate

The renderer does not yet satisfy this exit gate. Static environment/task/trace
and actor views exist; complete configuration comparison, artifact-separated
prompt/model views, and the H2 parity trace remain open.

O1 is complete when one accepted and one rejected H1 lifecycle plus the H2 NAO
planner parity run can be rendered with:

- complete ordered lineage;
- environment-run activation, ingress classification, attached actor runs, and
  standby or lease transitions;
- configuration and source identity;
- raw model output, proposal, admission, lease, result, evidence, and terminal
  judgment as separate artifacts;
- projected and directly callable object distinction;
- binding and owner-evidence closure;
- required and best-effort obligation evaluation with explicit deficits;
- failure-stage attribution;
- model-free replay comparison;
- optional H3 shadow candidate lineage without granting it authority.

## 8. O2 Deferred Scope

O2 may add a domain index above the O1 environment-run hierarchy, actor-run and
operation-graph exploration, live streaming, multi-run comparison, interactive
AB/evidence graphs; Watson/Bonsai overlays; replay controls; counterfactual
controls; Workbench review queues; promotion/rollback inspection; and
cross-domain navigation.
Those features must consume the O1 event and graph contracts rather than invent
a second trace vocabulary.
