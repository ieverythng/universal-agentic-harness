# UAH and NeuralWorkbench Investor Handoff

**Prepared:** 2026-10-04

**Audience:** prospective investors, design partners, strategic operators, and
technical diligence teams

**Status:** external diligence draft, not an offering memorandum

**Evidence boundary:** implementation claims refer to the repository state and
validation ledger current on the preparation date

## Package purpose

This package explains the Universal Agentic Harness (UAH) and NeuralWorkbench
as one product thesis with separate authority boundaries:

- **UAH** is the portable control kernel. It compiles task scope, constrains
  model proposals, preserves domain ownership, and records evidence.
- **NeuralWorkbench** is the H3+ adaptive engine. It retrieves prior
  experience, constructs and compares candidate interaction structures, and
  proposes reusable structures without receiving execution authority.
- **Observatory** is the read-only evidence surface. It renders model output,
  admission, execution, evidence, acceptance, and Workbench provenance without
  becoming another source of truth. The current implementation is an initial
  static environment/task/trace index with explicit actor views; the broader
  comparison and interactive product views remain roadmap work.

The package separates implemented behavior from the roadmap. Commercial and
market statements are hypotheses for validation unless identified as
repository evidence.

## Reading order

1. [Executive brief](executive_brief.html) ([Markdown](executive_brief.md))

   Product thesis, current proof, target users, differentiation, and financing
   narrative in a short form.
2. [Technical diligence](technical_diligence.html) ([Markdown](technical_diligence.md))

   Architecture, identity, task compilation, two-stage admission,
   NeuralWorkbench, Observatory, security boundaries, implementation status,
   and open risks.
3. [GTM and investment case](gtm_and_investment_case.html) ([Markdown](gtm_and_investment_case.md))

   Beachhead, buyer hypotheses, packaging, commercialization sequence,
   milestone gates, metrics, capital use, and diligence disclosures.

HTML companions are generated from these Markdown sources and use the shared
UAH documentation theme:

- `README.html`
- `executive_brief.html`
- `technical_diligence.html`
- `gtm_and_investment_case.html`

## Evidence packet

The following canonical documents support the package. They should accompany
the handoff when the recipient requests technical depth:

| Document | Diligence purpose |
| --- | --- |
| [Implementation masterplan](../../plans/universal_agentic_harness_masterplan.md) | H0-H6 delivery spine, hard gates, ownership, and acceptance criteria |
| [Development log](../../plans/universal_agentic_harness_development_log.md) | Implemented seams, test evidence, open issues, and current release boundary |
| [UAH foundation](../../architecture/universal_agentic_harness_foundation.md) | System model, identities, frames, task lifecycle, agent embodiment, and runtime architecture |
| [NeuralWorkbench architecture](../../architecture/neural_workbench_adaptive_ab_harness.md) | Search, trace memory, uncertainty, candidate scoring, crystallization, and H3/H4 boundaries |
| [Observatory contract](../../architecture/observatory_contract.md) | Immutable evidence views, lifecycle event families, and read-only authority |
| [Domain onboarding](../../plans/domain_initialization_and_ab_coupling.md) | DomainContractPack production, validation, activation, and portability model |
| [Identity and memory decisions](../../artifacts/decisions/2026-09-08_uah_identity_environment_and_memory_grill.md) | Frozen decisions for roles, agents, runs, environments, tasks, traces, operations, memory, and allocation |
| [H2 and Workbench decisions](../../artifacts/decisions/2026-08-04_uah_h2_neural_workbench_grill.md) | UAH versus NeuralWorkbench ownership and H2/H3 staging |

## Current evidence in one page

As of 2026-10-04:

- the portable kernel and NAO compatibility package have focused and full-suite
  validation recorded in the canonical development log; complete pre-commit,
  document-render, and clean-wheel gates are rerun before package distribution;
- H0 implements task projection, deterministic gates, binding quarantine,
  content-addressed domain rules, normalized ingress, and classification
  decisions, ledger-authorized task starts, environment registration, task and
  trace lineage, TaskSpec compilation, bounded input-schema validation,
  two-stage operation admission, explicit operation edges, typed rejection
  replay, atomic tool-budget dispatch, pre-dispatch cancellation, recorded
  timeout and retry policy, exact lease-only execution, task acceptance,
  advisory-lock-coordinated restart replay, and verified trace digests;
- the deterministic NAO adapter canary covers accepted lease execution,
  recorded semantic no-dispatch rejection, terminal required-effect
  counterexample, restart replay, and verified digest output;
- H1 implements role/model declarations, non-reserving registration preflight,
  durable actor attachment/termination, fixed leases, bounded owner readiness,
  standby, deterministic prompt compilation, and fake-provider invocation with
  atomic model accounting; O1 indexes real environments, tasks, traces, and
  explicit actors. Live provider integration and durable context remain open;
- H2 NAO planner parity has not yet been demonstrated;
- the Watson/Bonsai model comparison has not started;
- NeuralWorkbench is an optional H3 companion, and its intended repository
  revision is documented but the gitlink is not currently mounted in this
  repository;
- no production customer, revenue, live robot qualification, market-simulator
  result, or measured NeuralWorkbench uplift is claimed by this package.

## Recommended external use

Send the executive brief first. Provide the GTM and investment case for a
commercial discussion, then the technical diligence document and canonical
evidence packet for architecture review. Any slide deck, financial model,
pricing proposal, or market-size estimate should remain a separate artifact
until it has its own sources and assumptions.
