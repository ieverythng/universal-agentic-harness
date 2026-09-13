# Agent Guide

Universal Agentic Harness is a portable Python package. Preserve these
boundaries:

- `src/ab_harness` must not import ROS, NAO packages, provider SDKs, or runtime
  products.
- Models propose typed operations; deterministic gates and environment owners
  decide whether they execute and what effects are proven.
- AB coordinates are frame-relative. Do not present an AB level as a global
  capability or intelligence score.
- Runtime discovery is not authorization or evidence.
- Keep H0 implementation claims distinct from the H1-H6 roadmap.
- Any adaptive or learned structure remains quarantined until replay,
  counterexample, holdout, owner-review, provenance, and rollback gates pass.

Run `./scripts/setup_dev_tools.sh` once, then `./scripts/run_precommit.sh` for
source or documentation changes. The hook suite runs Ruff, source-aware tests,
repository hygiene, and `python scripts/render_agentic_harness_docs.py --check`.
Generated HTML and Markdown documents must remain synchronized.
