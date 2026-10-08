# Independent final dashboard correction review

Reviewed on 2026-10-08. Fresh reviewer, no implementation authorship, no source repairs. Requested reviewer configuration: `gpt-6.1-sol` at `max`; backend model identity is not independently observable from this agent.

## Scope and independence

Read `REVIEW.md` first. Before reading implementation or diffs, declared tests of canonical, missing, repeated and malformed reconciliation metadata; authored historical prose and fenced examples; literal numeric entities; punctuation and active HTML; Unicode/control separators; delimiter variants; repeat rendering; actual record filters and counts. Then executed public `--help` and repository `--check` controls. The latter exited 0 with `Checked 12 metadata records`.

Compared only these four current files with their exact `.before` files in `docs/artifacts/reviews/2026-10-08_uah_research_dashboard_final_evidence/`: renderer, tests, dashboard Markdown and dashboard HTML. Did not read writer receipts, rationales, existing probe logs or other reviews. Git, hooks and providers were not invoked.

Frozen current SHA-256 values verified:

| File | SHA-256 |
| --- | --- |
| `scripts/render_research_dashboard.py` | `e636579246575f68508612ca25d47bf82aba7deb82da1491baf03dfc2f79fea3` |
| `tests/test_research_dashboard.py` | `0a086b3f98255dfe34eacf01ec1801b7427ff935961b3beb3d0c5a2a0f0d91ef` |
| `docs/research/uah_research_dashboard.md` | `3e7cc69e0a7df0acb833f8f2c0a9165fe0652e4f118ac7c0a1fb7f31826b3359` |
| `docs/research/uah_research_dashboard.html` | `8758404b6f378dfa046347fc44c32ecdfc87885d0e9ac6b27b1481f599701e80` |

Exact-before renderer hash: `7d6f73a54f3e334905b90ed67b51dbf2a43f94df540e1c96ab31850e60f8cf61`. Exact-before tests hash: `964350ab2950eb2e3a09a9278bb960982b0fa9306cdd7cfdf4f969c1dd7dad0c`. Both document files are byte-identical to exact-before.

The code-review contract informed separate standards and behavior assessments. This change preserves dashboard claim semantics and does not alter H0-H6 gates. The registry owns current navigation metadata; authored history retains its own recorded facts. No runtime or release qualification is inferred from these checks.

## Finding

### BLOCKING: 1 of the 1 found so far. Authored heading variants are misclassified as top metadata

Location: `scripts/render_research_dashboard.py:211`.

The new reconciliation boundary accepts only unindented headings with an ASCII space after their hashes. The Markdown renderer strips leading whitespace and recognizes headings with `\s+` (`scripts/render_markdown_html.py:455`). Thus supported authored sections using a tab separator or two leading spaces remain inside the supposed top metadata region. An historical date beneath such a section is counted as a second top field and the public command rejects the document.

Reproduction: execute `python docs/artifacts/reviews/2026-10-08_uah_research_dashboard_final_primary_probe.py`; inspect `history-tab-heading` and `history-indented-heading`. The probe creates a throwaway root, one valid dated proposal and a registry reconciled on `2026-10-08`, then invokes each exact renderer through its public CLI with `--repo-root`, `--registry`, `--markdown` and `--as-of 2026-10-08`.

Input (`\t` below denotes a literal U+0009 tab, supplied by the durable probe):

```text
# Independent dashboard

Reconciled: 2026-10-07. Scope: navigation.

##\tHistorical prose

Reconciled: 2024-02-29.

## Catalog

<!-- research-records:start -->
<!-- research-records:end -->
```

Equivalent second input uses `  ## Historical prose`. These are authored section variants, not alterations of the canonical top reconciliation field. The exact-before generated HTML contains `<h2>Historical prose</h2>` for both, proving support through actual execution rather than inferred Markdown semantics.

Expected: rendering succeeds, only the top reconciliation date becomes `2026-10-08`, the historical date remains `2024-02-29`, and subsequent `--check` succeeds. Ordinary `## Historical prose` already demonstrates this behavior in the current renderer.

Actual current: render and `--check` both exit 1 with `Research catalog error: dashboard requires one top reconciliation field`. Markdown is unchanged and no HTML file is created. This finding is rejection of a supported input, not historical mutation by the current renderer.

Exact-before comparison: render/check exit 0 and preserve the heading presentation, but the historical date is overwritten. That is the pre-existing preservation defect the correction intends to remove, not acceptable expected behavior. Current canonical headings correct that defect; alternative supported headings regress to rejection. NBSP heading separation reproduces the same mismatch under this renderer. Four-space fences also hit it under the renderer's permissive fence handling, but the blocking classification does not depend on either nonstandard case.

Repair direction: make metadata ownership consistent with supported authored block boundaries, without weakening missing/repeated/malformed top-field rejection or rewriting historical dates. Preserve authored heading spelling and indentation.

## Standards and design principles

- Separation of concerns: OK. Registry validation, record rendering and top-field reconciliation remain distinct; browser controls compute navigation visibility, not research scores or release decisions.
- Programming by intention: OK. `reconcile_header` names the intended operation and errors fail before output writes.
- Encapsulation: OK. Entity conversion is restricted to generated record HTML; authored fragments no longer receive global numeric-entity conversion.
- High cohesion: OK. The changed behavior stays within the dashboard generator and its public-command tests.
- Low coupling: violation at `scripts/render_research_dashboard.py:211`, finding 1. Metadata ownership relies on an independently narrower rendering grammar. This inconsistent duplicate classification breaks supported authored input. No second domain owner or business logic in UI was otherwise found.

## Execution evidence

Durable independent inputs and results: `docs/artifacts/reviews/2026-10-08_uah_research_dashboard_final_primary_probe.py` and `.log`.

- Current suite: `python -m pytest tests/test_research_dashboard.py -q`, 52 passed.
- Exact-before renderer and tests were copied into a separate temporary tree with the unchanged Markdown helper: 38 passed independently.
- Public CLI render/check/repeat-render against 20 synthetic inputs for current and exact-before, including zero records and two records in both orders. Current ordinary headings and backtick-fenced history retain historical dates; authored numeric entities before and after the generated region remain literal. Exact-before loses those protected representations. All accepted current fixtures preserve the exact prefix/suffix outside the generated region, except the declared top date replacement.
- Missing, repeated, timestamp-shaped and invalid-leap-day top metadata reject without writes in current. Missing, repeated, reversed and spaced delimiters reject in both. Error output was checked at the CLI boundary.
- Generated title/summary combined HTML event payloads, Markdown link syntax, table delimiters, quotes, entity text, U+2028 and vertical-tab separators. Both versions keep six table cells per fixture row, one control block, and no active injected HTML or JavaScript link. Current successful inputs are Markdown/HTML-idempotent and preserve source hashes.
- Copied the real registry, all source/reference files and exact-before dashboard documents into throwaway roots. Both renderers' initial check, render, subsequent check and repeated render exit 0, retain exact document bytes, and leave all source/registry hashes unchanged.
- Executed the actual generated inline filter script in Node with a minimal DOM fixture built from generated HTML. Real catalog counts: 12 overall, kinds 4/1/2/2/3, H3 4, candidate search 1, unmatched search zero. The one-record adversarial fixture also selects correctly. This executes script logic but is not a real-browser layout/accessibility certification.

Residual gap: no real-browser visual inspection or hook integration was attempted in this bounded independent round; the root agent owns integration. Current file hashes were rechecked after probes and still match the frozen scope. One blocking finding and no nits. No source fix is included.

VERDICT: CHANGES
