# Research

Start with the [UAH Research Dashboard](uah_research_dashboard.md)
([HTML](uah_research_dashboard.html)). The HTML view has record-kind tabs,
search and H-series dependency filters; every record remains visible without
JavaScript. Its [registry](experiment_registry.json) contains metadata and
source pointers only. Receipts own observations and numerical results.

The [masterplan](../plans/universal_agentic_harness_masterplan.md) owns delivery
order and release gates. Architecture documents own system boundaries. This
catalog neither qualifies an implementation nor supplies execution authority.
H-series labels are dependencies, not capability scores or completed gates.

## Existing investigations

- [Jev and System One decision models](jev_system_one_uah_research.md):
  investigation and proposed ranking experiment, with no UAH run result.
- [Evaluation, adaptation and runtime trade-offs](uah_agent_evaluation_adaptation_runtime_research.md):
  research inputs for configuration-level evaluation, not model qualification.
- [Research artifact catalog](../artifacts/research/README.md): dated evidence
  and historical review pointers. Existing notes stay at their original paths.

## Catalog rules

1. Index only existing completed documents; retain their historical paths.
2. Keep investigation, proposed experiment, executed probe and reviewed outcome
   distinct; link H-series prerequisites without copying roadmap authority.
3. Store metadata/pointers only; unknown metrics and qualification remain
   `unknown` or `not_scored`, never inferred from names, AB depth or logged text.

Generate and check both dashboard files with:

```bash
.venv/bin/python scripts/render_research_dashboard.py
.venv/bin/python scripts/render_research_dashboard.py --check
```

The renderer rejects duplicate JSON keys/record IDs, undeclared fields (including
metric values), invalid or future snapshot dates, missing/escaping document
paths and source-hash disagreement. A matching source hash proves which document
was indexed, not that its claims or runtime effects were independently verified.
Dependency-only links may be unpinned and carry no current-state certification.
The canonical documentation check also checks this generated pair.
