# Independent research dashboard review

Review started 2026-10-08 14:38:46 UTC. Frozen Git base:
`28fab5e7f2c244d86a64c371f2118017999b2387`.

## Adversarial inputs declared before implementation inspection

1. Duplicate JSON keys at root, record, nested artifact and metric levels;
   duplicate experiment identifiers; empty and multiple-record registries.
2. Wrong field types, absent required fields, unknown fields, malformed dates,
   invalid source revisions, malformed artifact hashes and inconsistent metadata.
3. Absolute paths, parent traversal, symlink escape, URL-shaped paths, missing
   files, mismatched artifact bytes, and files mutated after registry creation.
4. Unknown status/kind labels, planned records carrying execution results,
   executed records lacking artifacts, reviewed records lacking review evidence,
   and incompatible kind/status combinations.
5. Null metrics, missing scores, boolean/nonfinite/negative/out-of-range numeric
   inputs, and invented aggregate or qualification claims.
6. HTML markup, quotes, script-closing text and malicious-looking paths/titles;
   Markdown escaping and relative links from both source documents and generated
   pages; empty search/filter results and combined status/kind/search filtering.
7. Public CLI check versus render, stale output rejection, deterministic output,
   source/Markdown/HTML agreement, and baseline CLI availability at frozen HEAD
   and the exact supplied pre-change general documentation renderer.

No implementation, tests, registry content, writer rationale, writer receipts,
or other reviewer findings were read before this declaration.

## Scope and independence

Requested reviewer configuration: `gpt-6.1-sol`, `max`, fresh context
(`fork_turns: none`), confirmed by the parent. No fallback was reported; backend
deployment identity is not independently observable. This reviewer did not write
the implementation and did not read the dashboard writer's receipts, rationale,
or another dashboard review.

The review covers exactly the seven new dashboard/catalog/test files below and
the eight added lines in `scripts/render_agentic_harness_docs.py`. Other dirty
runtime and documentation files are controls, not this delta. Standards were
reviewed against `AGENTS.md`, `REVIEW.md`, and UAH guardrails; no originating
issue/PRD was supplied, so the spec axis is bounded to this assigned review
contract and the new documentation's stated promises. No new agents were
spawned from this independent reviewer.

Affected boundary: H0/H1/H2 evidence navigation and H3/H4 research dependencies,
not execution or release qualification. The masterplan retains release-gate
ownership; source receipts retain observation ownership; the registry owns
catalog metadata. No model/provider, lifecycle, admission or environment owner
was invoked or changed. H-series dependencies remain frame-independent release
prerequisites, not AB capability scores. Adaptive research remains quarantined.

## Findings

### 1 of the 3 found so far. BLOCKING: reconciliation date has two owners

Locations: `docs/research/experiment_registry.json:3`,
`docs/research/uah_research_dashboard.md:3`, and
`scripts/render_research_dashboard.py:229`.

Input: in a throwaway repository containing the current Markdown template and
one valid hash-pinned record, change only `reconciled_at` from `2026-10-08` to
`2026-10-09`. Run the public renderer with `--repo-root TEMP --as-of 2026-10-09`,
then the identical command with `--check`.

Expected: the displayed reconciliation date must match the registry, or the
renderer/check must reject the mismatch. Actual: render exits 0 with
`Rendered 1 metadata records`; check exits 0 with `Checked 1 metadata records`.
Both Markdown and HTML still display `Reconciled: 2026-10-08`, while the JSON
states `2026-10-09`. The generated region derives records from JSON but preserves
the competing static date outside that region. This is ordinary catalog upkeep,
not an unsupported input. Derive the displayed date from its single metadata
owner or fail when the template disagrees.

### 2 of the 3 found so far. BLOCKING: metadata can author renderer delimiters and raw Markdown HTML

Locations: `scripts/render_research_dashboard.py:176`,
`scripts/render_research_dashboard.py:200`, and
`scripts/render_research_dashboard.py:225`.

Input: reset the throwaway Markdown to the current valid template and set the
otherwise-valid record summary to `<!-- research-records:end -->`. Run the public
renderer, then `--check`, both with `--as-of 2026-10-08`.

Expected: metadata is literal text, so render/check remain idempotent, or the
invalid metadata is rejected before output mutation. Actual: render exits 0
(`Rendered 1 metadata records`) and writes a second structural delimiter;
immediate check exits 1 with `Research catalog error: dashboard must contain one
ordered generated record region`. A subsequent render also cannot recover the
now-invalid region without manual editing. Escaping brackets/backticks/asterisks
and pipes does not protect the generator's own HTML-comment boundary.

The same escaping gap accepts summary `<img src=x onerror=alert(1)>` and writes
it unchanged to the generated Markdown. Rendering that Markdown through the
already-installed `MarkdownIt('commonmark', {'html': True})` preserves the active
image tag. The project's generated HTML does escape this payload; no browser
code execution occurred or is claimed. The Markdown output nonetheless remains
an HTML-authoring surface for registry metadata. Protect both output formats
and add the immediate-render/check delimiter regression.

### 3 of the 3 found so far. NIT: punctuation escapes are displayed literally in HTML

Location: `scripts/render_research_dashboard.py:178` and
`scripts/render_research_dashboard.py:232`.

Input: valid title `A [literal] *title* ` followed by a backtick-wrapped `value`
and ` | separator`; render through the public CLI.

Expected: the browser displays the literal original punctuation without making
it active Markdown formatting. Actual: the generated HTML contains
`A &amp;#91;literal&amp;#93;` and analogous doubly escaped entities for other
characters. HTML displays `&#91;literal&#93;`, not `[literal]`. The metadata
conversion emits numeric entities, then the shared renderer escapes their
ampersands. This does not currently affect the stored 12 plain-text titles.

## Executed evidence

- Before implementation inspection, recorded the adversarial inputs above and
  ran public `--help`, then repository `--check` (exit 0, 12 metadata records).
- Executed two throwaway public-CLI mutation matrices. The first baseline fixture
  used `evidence/report.md`, which the documented docs-only path contract rejects;
  those masked cases were not counted as evidence for deeper validation. The
  corrected fixture used `docs/research/fixture.md` and the current Markdown
  template in `/tmp/uah-dashboard-primary-valid-p2d3b7rk`.
- Public CLI and focused tests rejected duplicate root/record/source JSON keys,
  duplicate IDs, unknown kinds/status fields, absent/wrong-type fields, metric
  fields including null and boolean values, nonfinite JSON constants, boolean
  schema versions, invalid/future/leap-day/timestamp dates, duplicated/unknown
  H-series labels, missing documents/references, absolute/URL/parent traversal
  paths, escaping symlinks, wrong hashes and uppercase hashes. Invalid fixtures
  did not rewrite source documents. The source-hash mutation test also checks
  generated-output preservation.
- Empty and one-record catalogs rendered successfully. The focused test exercises
  two records in both orders. Null dates displayed `unknown`; dependency-only
  null hashes displayed `unpinned dependency link`; every row stayed `not_scored`.
  URLs for a valid filename containing spaces, parentheses, a closing bracket,
  quote and pipe were percent-encoded correctly. Fresh generated outputs passed
  check; stale Markdown and HTML were rejected without check-mode rewriting.
- Explicit `executed_probe` and `reviewed_outcome` labels on a hash-pinned fixture
  saying no execution/review occurred were accepted; so was a proposal summary
  claiming measured capability. These are human-authored document classifications,
  not mechanically verified execution/review evidence. The existing disclaimers
  correctly limit source hashes to document identity. This review does not infer
  certification from acceptance of those labels, and does not propose a second
  runtime evidence owner in this metadata-only catalog.
- Ran `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p
  no:cacheprovider tests/test_research_dashboard.py`: **23 passed**, 1.39 seconds.
  Green tests do not cover the two blocking counterexamples above.
- Ran `PYTHONDONTWRITEBYTECODE=1 python scripts/render_agentic_harness_docs.py
  --check`: exit 0, including `Checked 12 metadata records`.
- Compared the general renderer with the exact supplied pre-change file using
  `diff -u`: only the assigned eight-line subprocess integration is added. Direct
  execution of that file from its snapshot directory fails because its derived
  root is `/tmp`, where `/tmp/scripts/render_markdown_html.py` does not exist.
  Restored the same unchanged bytes under a throwaway `scripts/` directory,
  copied the shared renderer and current control docs, then executed its public
  `--check`: exit 0. Temporary baseline root:
  `/tmp/uah-dashboard-before-primary-znk1sydg`.
- Frozen HEAD contains none of the seven new scoped paths. `git show
  28fab5e:scripts/render_research_dashboard.py` reports that the path does not
  exist there. No baseline research CLI result can honestly be asserted.
- Used only the approved in-app browser, on a loopback-only local HTTP server.
  The real dashboard loaded 12 records and its CSS/JS. Selecting Proposed
  experiment, H3 and search `Jev` produced exactly the Jev proposal and
  `1 catalog records`. Search `no-record-should-match` produced zero data rows
  and `No matching catalog records.` Expanded record descriptions remain visible
  below the filtered table; filters are table navigation, not document-wide
  hiding. No browser access refusal occurred, and no alternate browser mechanism
  was used. The created tab and server were closed.
- Ran scoped `git diff --check`: exit 0. No setup/precommit hooks were executed
  because this review expressly prohibits source/provider/Git mutations and
  mutating hooks. No source fixes were made.

## Five design principles

1. Separation of concerns: **violation**, the reconciliation date has two
   writable owners (`experiment_registry.json:3` and dashboard Markdown `:3`),
   while `render_research_dashboard.py:229` trusts the competing template value.
   This is the blocking duplicated fact in finding 1. The runtime/roadmap boundary
   is otherwise maintained.
2. Programming by intention: **violation**, `metadata_text()` promises to prevent
   metadata from becoming Markdown-authored formatting, but preserves structural
   HTML comments and raw HTML (`render_research_dashboard.py:176`); finding 2.
3. Encapsulation: **OK**. Closed metadata objects, path confinement and source
   hashes are validated together before normal rendering; raw receipt values are
   not pulled into catalog metrics. No ledger or source-observation writer exists.
4. High cohesion: **OK**. One small script owns metadata validation and generation;
   its tests exercise the public command, and static prose retains release
   boundaries. The generator does not become a runtime evaluator.
5. Low coupling: **OK**. The new CLI depends on the established Markdown renderer,
   standard library and document paths, not portable-core/provider/runtime imports.
   The canonical renderer delegates to one public command. Browser filtering is
   presentation-only and contains no acceptance or promotion policy.

## Exact-byte boundary

Initial and final SHA-256 readings matched for every scoped source below; frozen
HEAD remained `28fab5e7f2c244d86a64c371f2118017999b2387`. No approval applies to
future fixes or to unrelated dirty runtime files.

| Scoped file | SHA-256 |
| --- | --- |
| `docs/research/README.md` | `b7e8424a47614245c5432473259aa100eb2cd7aef86d01603e01a0a8ea6f832c` |
| `docs/research/uah_research_dashboard.md` | `398fbaf361eaf7204b35f273f1150de6062056d27d1430ebac4b4cb6017ae11d` |
| `docs/research/uah_research_dashboard.html` | `8758404b6f378dfa046347fc44c32ecdfc87885d0e9ac6b27b1481f599701e80` |
| `docs/research/experiment_registry.json` | `d2871c360d5995c2d7a77eeff5b430f4c986225280dd4b83e54ffef7324e87c4` |
| `docs/artifacts/research/README.md` | `7c28c5f2f81cc95807a71ab7652e302c9e68d1cdabae89a1189316fbe8f75115` |
| `scripts/render_research_dashboard.py` | `3b6ae46eaea0428a402a8650e44f0b1bacb5ebbb9e3ebde1300c5afaabb3dbc3` |
| `tests/test_research_dashboard.py` | `6a8427e21427b309bfac44f0c0c0570802536f5215df69144e993b3c6be44bbf` |
| `scripts/render_agentic_harness_docs.py` | `ae0a51e043245fcd460ddf61708268c1132b5fffd0790e0cd743c318f85bd8da` |
| Exact supplied pre-change general renderer | `732aba2d4ea8c7e73b407ea11a14bafdbdda438f19da5816832d527a7b40c9f6` |

Residual limits: this is a bounded independent dashboard review, not full runtime
qualification, numerical scoring, semantic certification of historical receipt
claims, or a review of the existing generic Markdown renderer. Historical receipt
paths and hashes were checked without reading other reviewers' findings. The next
discriminating proof is public render/check idempotence for delimiter-bearing
metadata and reconciliation-date agreement after a registry-only date update.

VERDICT: CHANGES
