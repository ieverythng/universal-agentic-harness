# Source provenance

The initial H0 implementation and research documents were extracted without
rewriting the source repository or its history.

| Field | Value |
| --- | --- |
| Source repository | `https://github.com/ieverythng/nao-ros4hri-bridge` |
| Source branch | `feat/TFM-LLM_planner` |
| Source commit | `00f95f3b5c4dfed2abf56da854366e1d0d92aee5` |
| Commit subject | `feat: Universal Agentic Harness main docs and implementation` |
| H0 origin commit | `8e590f14503131c4565c7297f571427772771ea6` |
| Extraction date | 2026-07-25 |

## Extracted material

- `src/ab_harness/ab_harness/*` became `src/ab_harness/*`.
- `src/ab_harness/test/test_h0_nao_harness.py` became
  `tests/test_h0_nao_harness.py`.
- The parent-only canonical registry path in that test was replaced by the
  standalone fixture at `tests/fixtures/ab_registry.json`.
- `docs/agentic_harness/*` was retained at the same repository-relative path.
- `scripts/render_agentic_harness_docs.py` and
  `scripts/render_markdown_html.py` were retained.
- The ROS package metadata was retained at repository root as an optional
  wrapper.

The original package README is preserved at `docs/h0_source_readme.md`.
Standalone packaging, CI, repository guidance, and Watson integration notes
were added after extraction.
