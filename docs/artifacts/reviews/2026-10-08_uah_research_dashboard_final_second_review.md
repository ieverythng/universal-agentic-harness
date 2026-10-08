# Research dashboard final fix: independent second review

Reviewed 2026-10-08. Requested reviewer configuration: `gpt-6-astra` at `max`.
The executing backend is not independently observable from this review.
The reviewer did not write the changes and did not read writer rationale,
implementation receipts, or other dashboard reviews.

## Scope and execution order

Read `REVIEW.md` first. Predeclared canonical versus historical reconciliation
dates, malformed and repeated fields, delimiter duplication and reordering,
Unicode controls, authored numeric entities, escaped metadata, idempotence,
and client record/filter/count behavior. Executed the actual CLI `--help` and
`--check` before reading implementation or diffs. The initial check reported
`Checked 12 metadata records`.

Compared the four exact-before files in
`docs/artifacts/reviews/2026-10-08_uah_research_dashboard_final_evidence/`
with the corresponding current renderer, tests, Markdown and HTML. Both
dashboard output files are byte-identical to their exact-before versions.
The current hashes were verified at the beginning and after probes:

| File | SHA-256 |
| --- | --- |
| `scripts/render_research_dashboard.py` | `e636579246575f68508612ca25d47bf82aba7deb82da1491baf03dfc2f79fea3` |
| `tests/test_research_dashboard.py` | `0a086b3f98255dfe34eacf01ec1801b7427ff935961b3beb3d0c5a2a0f0d91ef` |
| `docs/research/uah_research_dashboard.md` | `3e7cc69e0a7df0acb833f8f2c0a9165fe0652e4f118ac7c0a1fb7f31826b3359` |
| `docs/research/uah_research_dashboard.html` | `8758404b6f378dfa046347fc44c32ecdfc87885d0e9ac6b27b1481f599701e80` |

The code-review standards and spec axes were evaluated against `AGENTS.md`,
`REVIEW.md`, and the requested preservation/validation behavior. This is a
metadata-navigation repair, not an H0-H6 implementation or qualification
claim. No runtime, provider, Git, hook, or source modifications were made.

## Findings

### BLOCKING: 1 of the 2 found so far. Valid historical headings fail validation

Location: `scripts/render_research_dashboard.py:211`.

The new boundary scanner recognizes only unindented headings followed by an
ASCII space. The existing Markdown renderer accepts a tab after the heading
marker and strips leading indentation before recognizing headings. The scanner
therefore mistakes a historical reconciliation field in a valid section for a
second field in the dashboard header.

Input, with `\t` denoting one actual tab:

```text
# Independent review dashboard

Reconciled: 2026-10-07. Scope: metadata.

##\tHistorical prose

Reconciled: 2024-02-29.

## Catalog

<!-- research-records:start -->
<!-- research-records:end -->
```

An otherwise valid registry has `reconciled_at: "2026-10-08"`. The same failure
occurs with `  ## Historical prose` (two leading spaces).

Expected: update only the canonical top date, retain the historical date,
render the historical heading, and pass the subsequent check.

Actual: render exits 1 with
`Research catalog error: dashboard requires one top reconciliation field`.
No output is written. Exact-before exits 0 and recognizes the heading in HTML,
but incorrectly rewrites the historical date. The fix must preserve this
accepted heading syntax while correcting that previous historical rewrite.

Reproduction already executed for both versions:
`python /tmp/uah_dashboard_second_review_probe.py`, cases
`tab_heading_history` and `indented_heading_history`. Fixtures are retained in
`/tmp/uah-dashboard-second-review-7k90sewf/`.

### BLOCKING: 2 of the 2 found so far. Unicode separators bypass duplicate-header rejection

Location: `scripts/render_research_dashboard.py:214` and `:221`.

The header scanner counts lines with a multiline regular expression, while
`render_markdown` splits text with `str.splitlines()`. U+2028 is consequently
part of one permitted suffix during validation and a separate line during
rendering.

Replace the canonical field in the preceding minimal document with this value,
where `\u2028` denotes one actual Unicode LINE SEPARATOR, and omit the
historical section:

```text
Reconciled: 2026-10-07. \u2028Reconciled: 2024-02-29.
```

Expected: reject the second top reconciliation field without changing outputs,
as for the same input separated by an LF.

Actual: render and subsequent `--check` both exit 0. The generated HTML contains:

```html
<p>Reconciled: 2026-10-08. Reconciled: 2024-02-29.</p>
```

The exact-before renderer also accepts this input. This is an uncovered bypass
of the newly introduced duplicate-field gate, not a claim that the previous
renderer rejected it. Use the same logical-line semantics for validation and
rendering, or explicitly reject separator controls in canonical metadata.

Reproduction already executed: the `unicode_duplicate` case in
`/tmp/uah_dashboard_second_review_probe.py`, with both versions' render and
check commands in the retained fixture tree.

## Executed evidence

- `python -m pytest -q tests/test_research_dashboard.py`: 52 passed.
- `python -m pytest -q /tmp/uah-dashboard-second-review-7k90sewf/before/tests/test_research_dashboard.py`:
  38 passed against the copied exact-before renderer, not the current renderer.
- Independent actual CLI probes ran identical fixtures through current and
  exact-before renderers. Normal two-record rendering/checking was idempotent;
  rows had six cells, unknown dates stayed `unknown`, and scoring stayed
  `not_scored`. Empty registries, reversed record order and literal delimiter
  strings inside metadata rendered and checked successfully.
- Missing, repeated and blank-line-repeated canonical fields, an invalid leap
  date, a zoned timestamp and an attached malformed suffix were rejected by
  current with no write. Exact-before accepted them. Missing, repeated,
  reversed and differently spaced generated delimiters were rejected by both.
  Duplicate record IDs and duplicate JSON keys were rejected without changing
  existing outputs by both.
- Historical fenced dates before the generated region and prose dates after
  it remained unchanged in current. Literal `&#35; &#60; &#39; &amp;` in authored
  code remained literal text in HTML. Authored trailing prose retained literal
  entities. Exact-before changed the fenced date and decoded authored numeric
  entities. Source Markdown fixture bytes remained unchanged in every case.
- Metadata containing HTML tags, JavaScript-link syntax, punctuation, pipes,
  numeric entities and delimiter strings stayed literal. No active image or
  JavaScript link was produced. U+2028, U+2029, U+0085, vertical tab, form feed,
  U+001C/U+001D/U+001E and CRLF inside titles/summaries normalized without losing
  records in either version.
- `node /tmp/uah_dashboard_second_review_client.cjs` executed each version's
  actual emitted client script against HTML-parsed rows in a minimal DOM
  harness. All eight checks passed in both: all records, kind, combined
  kind/dependency, no matches, dependency-only, literal-entity search,
  case/whitespace-normalized search and absent search. Counts and pressed
  states agreed. This is JavaScript behavior evidence, not full-browser visual
  or accessibility certification.
- Additional registry/delimiter probes:
  `python /tmp/uah_dashboard_second_review_more.py`.

## Design principles

1. Separation of concerns: OK. Registry validation, record generation and
   authored-body rendering remain distinct; the client filters metadata only.
2. Programming by intention: OK. `reconcile_header` expresses the ownership
   intent clearly, although its accepted syntax is incomplete.
3. Encapsulation: OK. Header reconciliation remains inside the generator and
   does not rewrite source receipts.
4. High cohesion: OK. The changes concern reconciliation and the boundary of
   generated metadata escaping.
5. Low coupling: violation at `scripts/render_research_dashboard.py:211` and
   `:214`. Header scanning depends on a divergent subset of the downstream
   renderer's heading and logical-line grammar, producing both findings.

Standards: two blocking findings; no nits. Spec: historical/entity preservation
works for the ordinary forms tested, but alternative accepted headings and the
duplicate-header gate remain incomplete. No release or runtime authority is
conferred by these checks. No hooks were installed or executed.

VERDICT: CHANGES
