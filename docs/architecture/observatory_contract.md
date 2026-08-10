# Observatory Contract

**Status:** O1 API frozen; O2 implementation deferred
**Date:** 2026-08-04
**Applies to:** UAH H0-H6 and NeuralWorkbench H3+

## 1. Decision

The product-facing trace surface is called **Observatory**.

O1 is a small, read-only API with a static HTML renderer. It is required for
H1 lifecycle debugging and H2 NAO parity. O2 is the proper interactive
implementation and may evolve through H4 before H5 product polish.

Observatory is never an execution owner, evidence issuer, policy gate, or
registry authority.

## 2. Layered Visualization Contract

| Layer | Required views | Source of truth |
| --- | --- | --- |
| UAH H0-H2 | configuration, task, frame, role, projected AB graph, bindings, proposals, gates, owner evidence, failures, terminal state, replay comparison | UAH registry snapshots and lifecycle ledger |
| NeuralWorkbench H3 | pulse candidates, verification failures, energy terms, entropy proxy, retrieval lineage, counterexamples, recommendation, shadow replacement comparison | versioned Workbench request/candidate/observation payloads |
| H4 review | crystallization clusters, counterfactual results, holdout results, provenance, promotion review, rollback lineage | quarantined candidate and review artifacts |
| H5 product | cross-domain and cross-runtime navigation, capability/configuration comparison, live streams | conformance-qualified adapters and immutable traces |

## 3. O1 API

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
remain payload lineage. UAH `configuration_id`, `trace_id`, and event sequence
are mandatory envelope identity and are never reconstructed heuristically.

## 4. Graph Grammar

Graph nodes may represent:

- AB objects and decomposition relations;
- environment components and implementation bindings;
- proposals, pulse programs, verification decisions, and evidence artifacts;
- complete model-harness-domain configurations;
- trace clusters and reviewed candidate abstractions.

Graph edges must declare a type such as `decomposes_to`, `bound_by`,
`proposed_by`, `rejected_by`, `executed_by`, `evidenced_by`, `retrieved_from`,
or `compared_with`. A visual edge may not imply authorization or causality unless
the underlying event or contract proves it.

## 5. Metrics and Honesty Rules

Every metric is keyed by the complete content-addressed configuration. Model
family names alone are not aggregation keys.

Metric values carry one of these labels:

- `conceptual` — explanatory geometry with no runtime measurement;
- `synthetic` — generated evaluation data;
- `recorded` — replayed fixture or captured runtime data;
- `measured` — evaluator-produced result under a frozen configuration;
- `reviewed` — measured result accepted through the applicable gate.

Conceptual NeuralWorkbench capability-space, energy-landscape, entropy, and AB
maturity figures are design references. Observatory may reproduce their visual
grammar, but it must never present synthetic or conceptual values as runtime
evidence.

## 6. O1 Exit Gate

O1 is complete when one accepted and one rejected H1 lifecycle plus the H2 NAO
planner parity run can be rendered with:

- complete ordered lineage;
- configuration and source identity;
- projected and directly callable object distinction;
- binding and owner-evidence closure;
- failure-stage attribution;
- model-free replay comparison;
- optional H3 shadow candidate lineage without granting it authority.

## 7. O2 Deferred Scope

O2 may add live streaming, multi-run comparison, interactive AB/evidence graphs,
Watson/Bonsai overlays, replay controls, counterfactual controls, Workbench
review queues, promotion/rollback inspection, and cross-domain navigation.
Those features must consume the O1 event and graph contracts rather than invent
a second trace vocabulary.
