# Universal Agentic Harness Documentation

Markdown is canonical. The selected architecture and plan documents have
generated HTML companions; regenerate them after canonical edits.

## Plans

- [Implementation masterplan](plans/universal_agentic_harness_masterplan.md):
  H0-H6 delivery spine and current qualification gates.
- [Development log](plans/universal_agentic_harness_development_log.md):
  implementation evidence and open release gates.
- [Domain initialization](plans/domain_initialization_and_ab_coupling.md):
  onboarding, qualification, and activation boundaries.

## Architecture

- [Foundation](architecture/universal_agentic_harness_foundation.md): portable
  kernel and environment-owner boundaries.
- [Neural Workbench integration](architecture/neural_workbench_adaptive_ab_harness.md):
  H3+ adaptive search and quarantined promotion.
- [Observatory contract](architecture/observatory_contract.md): O1 read-only
  projection and O2 interaction boundary.
- [Watson inference seams](architecture/watson_inference_seams.md): local
  inference integration constraints.
- [Semantic object and binding decision](architecture/decisions/0001-semantic-objects-and-shadow-first-bindings.md).

## Decision records and examples

- [H2 and Workbench ownership grill](artifacts/decisions/2026-08-04_uah_h2_neural_workbench_grill.md).
- [Identity, environment, and memory grill](artifacts/decisions/2026-09-08_uah_identity_environment_and_memory_grill.md).
- [Synthetic owner-test deferral](artifacts/decisions/2026-10-09_synthetic_owner_test_deferral.md).
- [Source provenance](artifacts/provenance.md).
- [Recorded NAO O1 example](artifacts/observatory/o1_recorded_nao_canary.html):
  deterministic fixture only, not live H2 parity.
- [Agent lifecycle O1 example](artifacts/observatory/o1_h1_agent_lifecycle.html):
  synthetic fixed-model/fake-provider evidence only.

## Status and publication boundary

H0, H1, and O1 remain partial; H2 NAO parity is unqualified. These documents
describe implemented seams and roadmap separately. Detailed reviewer
narratives, coordination boards, raw probe archives, GTM material, and binary
design artifacts are not part of the core-plus-CI migration. The five exact
historical fixture files under `artifacts/reviews/` exist only as inputs to
`tests/test_admission_active_provenance.py`; they are not published review
reports. Historical receipt filenames cited in the canonical Markdown remain
plain-text references for traceability; their source reports are outside this
product candidate.

## Rendering and local checks

Regenerate the selected HTML companions and legacy browser redirects with:

```bash
python scripts/render_agentic_harness_docs.py
```

Use `./scripts/setup_dev_tools.sh` to create the local environment and install
hooks, then `./scripts/run_precommit.sh` for the repository checks. Provider
credentials and machine-specific paths must remain outside tracked artifacts.
