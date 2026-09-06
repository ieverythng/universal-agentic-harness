# Observatory Contract

**Status:** O1 API and identity grammar frozen; O2 implementation deferred
**Date:** 2026-09-07
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
    Prompt["Compiled Prompt + Schemas<br/>model-facing projection"]:::projection
    Model["Model Output<br/>raw immutable artifact"]:::model
    Proposal["TypedProposal<br/>operation request"]:::proposal
    Semantic["UAH Semantic Admission<br/>role + frame + object + binding"]:::gate
    Admitted["AdmittedOperation<br/>immutable semantic value"]:::gate
    Domain["Domain Lifecycle Admission<br/>readiness + dedupe + fencing"]:::domain
    Lease["ExecutionLease<br/>owner-granted authority"]:::execution
    Owner["Environment Owner<br/>native execution"]:::execution
    Evidence["Terminal Result + EffectEvidence<br/>owner-issued"]:::evidence
    Ledger["Lifecycle Ledger<br/>append-only events + artifacts"]:::trace
    Observatory["Observatory O1/O2<br/>read-only views"]:::observatory
    Workbench["NeuralWorkbench H3+<br/>candidate analysis only"]:::compiler
    Prompt --> Model
    Model --> Proposal
    Proposal --> Semantic
    Semantic -->|accepted| Admitted
    Admitted --> Domain
    Domain -->|leased| Lease
    Lease --> Owner
    Owner --> Evidence
    Evidence --> Ledger
    Ledger --> Observatory
    Ledger --> Workbench
```

Every stage, including rejection, appends its own event. The diagram shows the
accepted path for readability. Neither Observatory nor NeuralWorkbench sits in
the execution call chain.

## 3. Layered Visualization Contract

| Layer | Required views | Source of truth |
| --- | --- | --- |
| UAH H0-H2 | configuration, task, frame, role, projected AB graph, bindings, proposals, gates, owner evidence, failures, terminal state, replay comparison | UAH registry snapshots and lifecycle ledger |
| NeuralWorkbench H3 | pulse candidates, verification failures, energy terms, entropy proxy, retrieval lineage, counterexamples, recommendation, shadow replacement comparison | versioned Workbench request/candidate/observation payloads |
| H4 review | crystallization clusters, counterfactual results, holdout results, provenance, promotion review, rollback lineage | quarantined candidate and review artifacts |
| H5 product | cross-domain and cross-runtime navigation, capability/configuration comparison, live streams | conformance-qualified adapters and immutable traces |

## 4. O1 API

O1 accepts immutable, JSON-compatible inputs and returns a self-contained review
document:

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
- filter facets for event type, task, role, object, owner, gate outcome, and
  failure stage;
- ordered event cards with inspectable raw payloads;
- graph data embedded as inert JSON for later O2 reuse.

### Mandatory identity envelope

Every lifecycle event carries or resolves without heuristic reconstruction:

| Identity | Scope |
| --- | --- |
| `role_configuration_id` | Immutable semantic role, model admission profile, primary frame, auxiliary frame allowlists and access modes, authority and capability packs |
| `model_configuration_id` | Model artifact, runtime and decoding contract |
| `agent_handle_id`, `agent_handle_revision_id` | Stable routed identity and the immutable active-agent mapping resolved for this run |
| `agent_id` | Immutable role, model, prompt pack and harness composition |
| `agent_run_id` | One bounded activation of the agent |
| `provider_pool_id`, `resource_snapshot_id` | Runtime supply considered and the measured capacity state used by allocation |
| `model_instance_id`, `model_lease_id` | Loaded process or endpoint replica and its bounded reservation |
| `model_invocation_id` | One exact prompt-to-output call joining an agent run, trace and model lease |
| `trace_id` | One causally connected workflow containing one or more operations |
| `domain_id`, `task_type_id`, `task_id` | Domain namespace, task family and work instance |
| `operation_id`, `parent_operation_id` | One frame-relative AB-object lifecycle and its decomposition parent |
| `proposal_id`, `admission_id`, `execution_lease_id` | Proposal, UAH semantic decision and domain-granted authority |
| `event_id`, `parent_event_id`, `sequence` | Append-only event ordering and causality |

Each operation also records `frame_id`, `registry_version`, `ab_object_id`,
`binding_id`, prompt and projection hashes, evidence obligations, native domain
lineage, and owner-issued result references.

### Required lifecycle event families

```text
prompt_compiled
agent_handle_resolved | agent_handle_revision_promoted | agent_handle_revision_rolled_back
model_lease_requested | model_lease_acquired | model_lease_rejected | model_lease_released
model_invocation_started | model_invocation_completed | model_invocation_failed
model_output_recorded
proposal_normalized | proposal_rejected
semantic_admission_accepted | semantic_admission_rejected
domain_admission_leased | domain_admission_rejected
execution_started | execution_feedback
execution_completed | execution_failed | execution_cancelled
evidence_issued | evidence_rejected
terminal_task_accepted | terminal_task_rejected | terminal_task_suspended
```

The raw model output, normalized proposal, `AdmittedOperation`, execution lease,
native owner result, normalized evidence, and terminal judgment remain distinct
artifacts. Observatory may place them beside each other but may not collapse
them into one generated summary.

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

Graph edges must declare a type such as `decomposes_to`, `bound_by`,
`proposed_by`, `admitted_by`, `leased_by`, `rejected_by`, `executed_by`,
`evidenced_by`, `supersedes`, `retrieved_from`, or `compared_with`. A visual
edge may not imply authorization or causality unless the underlying event or
contract proves it.

An operation node has exactly one source coordinate `(frame_id, ab_object_id,
ab_level, registry_version)`. A parent operation may decompose into children at
other levels in the same frame. Cross-frame edges remain explicit mappings or
delegations and never inherit a coordinate automatically.

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

O1 is complete when one accepted and one rejected H1 lifecycle plus the H2 NAO
planner parity run can be rendered with:

- complete ordered lineage;
- configuration and source identity;
- raw model output, proposal, admission, lease, result, evidence, and terminal
  judgment as separate artifacts;
- projected and directly callable object distinction;
- binding and owner-evidence closure;
- failure-stage attribution;
- model-free replay comparison;
- optional H3 shadow candidate lineage without granting it authority.

## 8. O2 Deferred Scope

O2 may add live streaming, multi-run comparison, interactive AB/evidence graphs,
Watson/Bonsai overlays, replay controls, counterfactual controls, Workbench
review queues, promotion/rollback inspection, and cross-domain navigation.
Those features must consume the O1 event and graph contracts rather than invent
a second trace vocabulary.
