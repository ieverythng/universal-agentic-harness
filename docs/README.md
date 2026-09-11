# Universal Agentic Harness Documentation

Markdown is canonical. Generated HTML companions are committed for local review
and must be regenerated after canonical edits.

## Plans

- `plans/universal_agentic_harness_masterplan.md`: canonical H0-H6 delivery
  spine and current H2 qualification gates.
- `plans/universal_agentic_harness_development_log.md`: implementation and
  verification ledger.
- `plans/domain_initialization_and_ab_coupling.md`: manual and LLM-assisted
  domain onboarding, qualification, and activation gates.

## Architecture

- `architecture/universal_agentic_harness_foundation.md`: project thesis and
  portable kernel architecture.
- `architecture/neural_workbench_adaptive_ab_harness.md`: H3+ adaptive engine
  integration and AB research synthesis.
- `architecture/observatory_contract.md`: O1 read-only API and O2 interactive
  Observatory boundary.
- `architecture/watson_inference_seams.md`: local-model inference seams.
- `architecture/decisions/`: architectural decision records.

## Artifacts

- `artifacts/decisions/2026-08-04_uah_h2_neural_workbench_grill.md`: initial
  H2 and Workbench ownership decisions.
- `artifacts/decisions/2026-09-08_uah_identity_environment_and_memory_grill.md`:
  identity, environment, ingress, multi-actor trace, task-closure, and memory
  decisions from the extended architecture grill.
- `artifacts/reviews/`: dated implementation and release-gate audits.
- `artifacts/design-reports/uah_environment_ingress_task_closure_design_report.docx`:
  retained-template review of the 2026-09-08 architecture checkpoint.
- `artifacts/system-design/`: system-design document, retained template, and
  architecture figure.
- `artifacts/provenance.md`: source and extraction provenance.
- `artifacts/h0_source_readme.md`: retained H0 source note.

## Research

- `research/`: primary-source reviews and experimental notes. Research claims
  remain separate from implementation status.

## Repository Relationship

`src/ab_harness` is the portable UAH core. It owns H0-H2 contracts, domain
projection, bindings, gates, environment-owner evidence, configuration identity,
and the mandatory execution ledger. `src/ab_harness_nao` is the explicit
ROS-free NAO compatibility and recorded qualification adapter. The kernel has a
test-enforced dependency boundary against importing that adapter.

NeuralWorkbench remains an independently usable companion repository and begins
its authoritative role at H3 through a versioned adapter. The intended revision
is `e76ba7e`, but the current UAH tree does not contain the declared
`src/Neural-Wokbench` gitlink. Documentation and qualification must treat that
revision as an intended pin until the gitlink is restored and verified. The
companion owns pulse search, adaptive trace products, scoring, entropy
experiments, and quarantined crystallization, not UAH execution authority or
environment registry content.

NAO is the first reference domain. Existing chatbot, planner, orchestrator,
dialogue, knowledge, perception, and skill ownership remains in the NAO
repository while UAH provides compatibility adapters and comparable traces.

## Rendering

Regenerate every canonical HTML companion and the legacy browser redirects:

```bash
python scripts/render_agentic_harness_docs.py
```

The shared theme lives in `docs/assets/`. The old
`docs/agentic_harness/*.html` paths are redirects only and are not canonical.
