---
name: uah-guardrails
description: Apply Universal Agentic Harness architecture, authority, evidence, and release-boundary guardrails when implementing, reviewing, refactoring, or changing architecture or status claims for UAH core, lifecycle, admission, environment, adapter, trace, evaluation, or Workbench seams. Use for H0-H2 work and H3+ proposals that could cross the trusted-runtime boundary; skip citation-only or editorial changes that preserve claim semantics.
---

# UAH Guardrails

Preserve the semantic kernel and its authority chain while making the narrowest
change supported by current evidence.

For citation-only or editorial work that preserves claim semantics, follow the
repository documentation checks without loading this architecture workflow.

## Establish the governing contract

1. Read the nearest `AGENTS.md` and the root `CONTEXT.md`.
2. Read the relevant current-state and target sections in
   `docs/plans/universal_agentic_harness_masterplan.md`.
3. Read the architecture document that owns the affected seam:
   - portable kernel, identity, admission, lifecycle, or adapters:
     `docs/architecture/universal_agentic_harness_foundation.md`;
   - Observatory events or projections:
     `docs/architecture/observatory_contract.md`;
   - Workbench, adaptation, or crystallization:
     `docs/architecture/neural_workbench_adaptive_ab_harness.md`;
   - semantic objects and implementation bindings:
     `docs/architecture/decisions/0001-semantic-objects-and-shadow-first-bindings.md`.
4. Use `docs/plans/universal_agentic_harness_development_log.md` to distinguish
   implemented behavior from roadmap claims. Use research notes as evidence,
   not as accepted architecture.

State the affected release gate (`H0`, `H1`, `H2`, or `H3+`) and the
authoritative owner before changing code or normative documentation.

## Audit the authority chain

Follow the changed value from origin to effect:

```text
environment ingress
  -> task lineage and compiled projection
  -> PromptCompiler artifact (when inference is required)
  -> ModelLease and ModelInvocation
  -> raw model output
  -> typed proposal
  -> semantic admission
  -> domain execution lease
  -> environment owner
  -> owner-issued effect evidence
  -> deterministic task acceptance
  -> append-only replay and digest
```

At every affected seam, verify these invariants:

- `src/ab_harness` stays independent of ROS, NAO, provider SDKs, and runtime
  products.
- AB coordinates remain frame-relative. Discovery supplies candidates, never
  authority or evidence.
- Models and Workbench components may propose typed artifacts. Deterministic
  gates and environment owners decide execution and effect truth.
- Semantic admission and domain lifecycle admission remain distinct.
- Adapters submit portable typed contracts. Lifecycle event types, transition
  rules, and raw event serialization remain owned by `src/ab_harness`.
- Content-addressed authority artifacts reverify their own content and nested
  artifacts at trust crossings.
- Task-bearing ingress obtains immutable lineage through the common lifecycle
  ledger. The task registry remains a projection, not a second writable store.
- File-backed lifecycle writes keep lock, reload, transition reduction, append,
  flush, and `fsync` in one critical section.
- Terminal success follows declared obligations and owner evidence. Timeout,
  cancellation, stale evidence, retry exhaustion, and false completion remain
  typed outcomes rather than exceptions erased from replay.
- Agent registration never reserves hardware, loads a model, or invokes a
  provider. Releasing a model lease does not terminate the logical agent run.
- Provider responses are untrusted inputs, never authority or effect evidence.
  Keep provider credentials and sensitive configuration out of artifacts and logs.
- Endpoint smoke tests qualify provider connectivity only. They do not qualify
  H2 semantic admission, domain admission, execution, evidence, or task closure.
- O1 begins alongside final H0 closure. It consumes replay-stable ledger events
  through read-only projections and never writes authority back into the ledger.
- Adaptive or learned structures remain quarantined until replay,
  counterexample, holdout, owner-review, provenance, and rollback gates pass.
- Documentation labels H0 implementation, H1 work, H2 qualification, and H3+
  research separately.

When an invariant conflicts with a requested implementation, report the
conflict and propose the smallest compliant seam. Do not silently move
ownership.

## Deepen modules without speculative structure

Apply the deletion test before adding a new interface: if removing it later
would simplify the code without losing an independently useful policy or
mechanism, keep the behavior local. Require one real adapter and one credible
second adapter before generalizing an adapter seam.

For lifecycle changes, keep `LifecycleLedger` as the single public write and
replay interface. Internal event-family extraction is justified only when it
localizes conversion, transition validation, replay state, and digest effects
for real event families. File size alone is not evidence for a split.

For artifact identity, preserve each artifact's `verify_identity()` boundary.
Extract shared canonicalization only after the artifacts share one serialized
contract, error semantics, and compatibility policy. Similar SHA-256 syntax is
not sufficient.

For admitted-operation fields, introduce a binding/evidence value object only
when it is consumed as one concept by admission, leasing, execution, and replay.
Avoid a data-transfer wrapper used by a single caller.

## Test the public seam first

For behavior changes, add or adjust a failing test through the public interface
before implementation. Cover the negative branch that would otherwise cross an
authority boundary. Prefer restart and competing-writer fixtures for ledger or
task-ingress work, and replay-equivalence fixtures for lifecycle work.

Run the narrowest focused tests while iterating, then run:

```bash
./scripts/run_precommit.sh
```

For a changed document listed in `scripts/render_agentic_harness_docs.py`, edit
canonical Markdown and run:

```bash
python scripts/render_agentic_harness_docs.py
python scripts/render_agentic_harness_docs.py --check
```

For a document outside the renderer manifest, retain Markdown only and run the
renderer in `--check` mode, `git diff --check`, and the repository hook suite.

## Completion report

Report:

1. release gate and owner affected;
2. authority invariants checked;
3. tests or documentation checks run;
4. implemented behavior versus deferred roadmap behavior;
5. residual evidence gaps and the next discriminating probe.

Run a bounded SkillOpt-style iteration (baseline -> mutate -> holdout gate -> accept/reject log) before finalizing major wording changes.
