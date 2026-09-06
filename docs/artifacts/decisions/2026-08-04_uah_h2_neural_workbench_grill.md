# UAH H2 and NeuralWorkbench Design Grill

**Date:** 2026-08-04
**Status:** Shared understanding confirmed; implementation authorized

## 1. H2 Scope

- H2 closes with a full planner ingress/egress implementation over recorded and
  fake/simulated NAO contracts.
- No live robot is required.
- Chatbot receives registry/provenance visibility but remains the existing
  dialogue owner.
- H3 is a stretch: Observatory consumption, protocol scaffolding, or shadow
  pulse creation are useful but not required for release success.
- Any H3 replacement candidate has zero execution authority for this launch.

## 2. H2 NAO Migration

The planner is the first cooperative seam:

```text
existing chatbot or recorded PlannerRequest
  -> UAH projection and model port
  -> typed planner proposal
  -> deterministic UAH gate
  -> fake/existing orchestrator owner
  -> normalized evidence and trace
```

The projection includes approved AB1 planner operations and inspectable,
non-callable AB0 dialogue, KB, transport, and feedback seams. Visibility does
not imply callability.

NAO later supports explicit `legacy`, `uah`, and `shadow` modes. Routing belongs
in the NAO repository; UAH records the selected authority mode. There is no
silent fallback during qualification.

Existing `planner_llm` and `chatbot_llm` packages remain compatibility adapters
and reference implementations. They are not deleted to manufacture a migration
claim.

## 3. UAH and NeuralWorkbench Ownership

UAH owns H0-H2 contracts, domain initialization inputs, frame-relative registry
content, projections, implementation bindings, deterministic gates,
environment-owner execution, mandatory evidence ledger, replay, configuration
identity, and qualification.

NeuralWorkbench is a standalone companion engine beginning at H3. It owns pulse
candidate generation, validation/scoring, adaptive trace products, retrieval,
entropy experiments, capability profiles, and quarantined crystallization.

NeuralWorkbench can recommend a replacement candidate. UAH alone gates it and
the environment owner alone executes and proves effects.

## 4. Repository and Protocol Boundary

- NeuralWorkbench remains independently versioned in the Aily repository.
- UAH pins it as the `src/Neural-Wokbench` Git submodule.
- The first integration is synchronous and in-process.
- Request, candidate-batch, and observation contracts remain JSON-compatible,
  content-addressed, and transport-neutral.
- NeuralWorkbench core receives a host-supplied model-inference port; provider
  clients do not enter the engine core.
- Protocol mismatches fail closed. A development override is visibly degraded
  to observation-only.

## 5. Trace and Observatory Boundary

UAH owns the mandatory execution-event ledger. NeuralWorkbench derives enriched
pulse, scoring, entropy, retrieval, and crystallization traces from it.

The trace product is called **Observatory**. O1 freezes a read-only static
rendering API and is required for H1/H2 review. O2 is the later interactive
implementation. Conceptual and synthetic graphs must be labeled and may never
masquerade as measured evidence.

## 6. Domain Initialization

Manual and LLM-assisted initialization produce the same candidate domain
package. Frontier coupling models are encouraged, but the intended local model
may be used with reduced authority and stronger review. `coupling_model` and
`runtime_model` remain distinct roles.

Discovery and model confidence never activate registry objects. Deterministic
validation, sandbox/replay qualification, and environment-owner approval are
required.

## 7. Implementation Quality Boundary

- Use deep, narrow interfaces and keep ROS/provider dependencies outside the
  portable core.
- Implement vertical behavior test-first.
- Run architecture review at meaningful seams.
- Apply behavior-preserving deslop only after the suite is green.
- Keep canonical Markdown and generated HTML synchronized.
