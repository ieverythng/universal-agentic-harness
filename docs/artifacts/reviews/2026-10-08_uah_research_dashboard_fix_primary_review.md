# Research dashboard FIX primary independent review

## Predeclared inputs (before implementation or diff inspection)

Scope: the dashboard renderer, its tests, and generated dashboard Markdown/HTML against the four exact `.before` copies under `2026-10-08_uah_research_dashboard_fix_evidence`. No writer receipt, rationale, or other reviewer findings are inputs. HEAD is expected to be `28fab5e`; current target hashes will be verified. This reviewer did not author the fix. Review instructions: root `AGENTS.md`, `REVIEW.md`, and the code-review and UAH guardrails skills.

Declared on 2026-10-08 at approximately 16:58 Europe/Madrid, before inspecting source or diff. Public controls: `PYTHONDONTWRITEBYTECODE=1 python scripts/render_research_dashboard.py --help` and `PYTHONDONTWRITEBYTECODE=1 python scripts/render_research_dashboard.py --check`.

Predetermined attack inputs:

- Literal metadata: `A <!-- comment --> B`, `<b>raw</b>`, `<script>probe</script>`, `[label](https://example.invalid)`, pipe, backtick, backslash, ampersand, quote, apostrophe, Markdown punctuation, existing entities (`&amp;`, `&#39;`, `&#x3c;`). Combine comments, links, entities, and punctuation in one field; reverse their order.
- Line boundaries: LF, CR, CRLF, VT, FF, NEL, U+2028, U+2029, and ASCII controls. Test empty, one character, boundary-adjacent variants, and duplicate/malformed metadata fields.
- Dates: valid leap day `2024-02-29`, invalid leap day `2025-02-29`, `2026-12-31`, `2027-01-01`, timezone-looking date strings, and wrong-width/whitespace forms. Changing a valid as-of date must change only the authoritative date metadata, not dated historical source facts.
- Evidence controls: wrong source hash, missing input, stale generated output, Markdown/HTML literal-display parity, record/filter counts, repeat-render idempotence, and public render check. Exact-before execution must be compared; missing new API behavior is recorded honestly rather than simulated.

All probes will run against throwaway copies or read-only public seams. No source, Git, provider, or mutating-hook changes are authorized.

## Pinned evidence and review method

HEAD: `28fab5e7f2c244d86a64c371f2118017999b2387`. Comparison is exact frozen-before bytes, not the Git merge-base: the fix is in the dirty tree. Both public CLIs exist in the exact-before script; no missing API was substituted. The shared Markdown renderer is an unchanged dependency, not a reviewed change. No writer receipt or other dashboard review was read.

| Target | Current SHA-256 | Exact-before SHA-256 |
| --- | --- | --- |
| scripts/render_research_dashboard.py | 7d6f73a54f3e334905b90ed67b51dbf2a43f94df540e1c96ab31850e60f8cf61 | 3b6ae46eaea0428a402a8650e44f0b1bacb5ebbb9e3ebde1300c5afaabb3dbc3 |
| tests/test_research_dashboard.py | 964350ab2950eb2e3a09a9278bb960982b0fa9306cdd7cfdf4f969c1dd7dad0c | 6a8427e21427b309bfac44f0c0c0570802536f5215df69144e993b3c6be44bbf |
| docs/research/uah_research_dashboard.md | 3e7cc69e0a7df0acb833f8f2c0a9165fe0652e4f118ac7c0a1fb7f31826b3359 | 398fbaf361eaf7204b35f273f1150de6062056d27d1430ebac4b4cb6017ae11d |
| docs/research/uah_research_dashboard.html | 8758404b6f378dfa046347fc44c32ecdfc87885d0e9ac6b27b1481f599701e80 | 8758404b6f378dfa046347fc44c32ecdfc87885d0e9ac6b27b1481f599701e80 |

Current target hashes were rechecked after the probes and remained unchanged. The code-review skill's standards and spec axes were evaluated by this single fresh reviewer, rather than delegated again; the parent task owns the independent parallel review. Model/effort selection is inherited from the parent; this review cannot independently verify its configured model. The issue-tracker setup workflow and mutating hooks were not run because this bounded review prohibits those mutations.

Release boundary: metadata navigation only; no H0/H1 exit, H2 qualification, H3 promotion, execution, or owner-evidence claim is produced. The masterplan and environment owners retain release and effect authority. Root CONTEXT, the relevant masterplan current/target contract, development-log current state, and ADR 0001 informed that boundary.

## Exact execution and results

Commands ran from `/home/juanbeck/universal-agentic-harness`:

```bash
PYTHONDONTWRITEBYTECODE=1 python scripts/render_research_dashboard.py --help
PYTHONDONTWRITEBYTECODE=1 python scripts/render_research_dashboard.py --check
git rev-parse HEAD
sha256sum scripts/render_research_dashboard.py tests/test_research_dashboard.py docs/research/uah_research_dashboard.md docs/research/uah_research_dashboard.html docs/artifacts/reviews/2026-10-08_uah_research_dashboard_fix_evidence/*.before
diff -u docs/artifacts/reviews/2026-10-08_uah_research_dashboard_fix_evidence/render_research_dashboard.py.before scripts/render_research_dashboard.py
diff -u docs/artifacts/reviews/2026-10-08_uah_research_dashboard_fix_evidence/test_research_dashboard.py.before tests/test_research_dashboard.py
diff -u docs/artifacts/reviews/2026-10-08_uah_research_dashboard_fix_evidence/uah_research_dashboard.md.before docs/research/uah_research_dashboard.md
diff -u docs/artifacts/reviews/2026-10-08_uah_research_dashboard_fix_evidence/uah_research_dashboard.html.before docs/research/uah_research_dashboard.html
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q tests/test_research_dashboard.py -p no:cacheprovider
PYTHONDONTWRITEBYTECODE=1 python /tmp/uah_dashboard_fix_primary_probe.py
PYTHONDONTWRITEBYTECODE=1 python /tmp/uah_dashboard_fix_primary_probe.py --focused
PYTHONDONTWRITEBYTECODE=1 python /tmp/uah_dashboard_fix_primary_probe.py --entities
```

The scratch probe has been preserved as `docs/artifacts/reviews/2026-10-08_uah_research_dashboard_fix_evidence/fix_primary_probe.py` (SHA-256 `760434e77fcc349d8b12e3cc7eaf24c3fbb86fae25feb30cd3a5512b3960aa84`); replace its former `/tmp` path in the last three commands to reproduce. It runs the actual current and exact-before CLI processes with `--repo-root`, `--registry`, `--markdown`, and `--as-of 2027-01-01`. Fixtures and output writes are temporary. `--focused` runs the generated filter JavaScript under Node with a minimal DOM built from parsed HTML, not a real browser.

- Public control: exit 0, `Checked 12 metadata records`; focused suite: 38 passed.
- Literal matrix: current passes all 24 cases, including delimiter comments, raw HTML, links, entity spellings, all ASCII punctuation, reversed combined attacks, and 14 control/line-separator variants. Two rows retain six cells each; no active metadata links or raw HTML; source bytes, repeat-render bytes, and `--check` remain stable. Exact-before fails 15 cases, including delimiter duplication, literal-display loss, and Unicode row loss.
- Leap/year dates: `2024-02-29`, `2026-12-31`, `2027-01-01` accepted; `2025-02-29`, wrong width, leading whitespace, and timezone suffix rejected by both versions. For an ordinary single metadata line, changing reconciliation changes only that date in both output formats, leaving historical dates and source bytes unchanged. Exact-before leaves the metadata stale.
- Empty/one/two records and reversed ordering execute. Wrong source hash and missing source fail before output writes. Stale HTML fails `--check`. The inherited focused suite additionally exercises duplicate/malformed registry inputs and source/path fences.
- Current filter results for all, H3, investigation+H3, Control+H1, and literal-entity+proposal+H3 are respectively 2, 1, 0, 1, 1, with matching count labels. Exact-before's Unicode fixture produces zero parsed catalog rows for every filter.
- Throwaway rendering of the real catalog passes render/check in both versions: 12 rows, six columns per row, 12 `not_scored`, three `unknown` dates. Their relocated HTML is byte-identical (SHA-256 `8f3d1912526ee14a78012b9ec19d37909fe312c2c2017a9cc21cb61e233a9446`). Existing checked-in HTML is also unchanged. Metadata escape changes do not promote research or invent scores.

## Findings

### 1 of the 2 found so far. BLOCKING: reconciliation replacement alters historical text outside its owned field

`scripts/render_research_dashboard.py:229` applies a multiline substitution to the entire handwritten preamble, including code fences. This violates REVIEW.md section 7 (dated documentation retains historical facts) and the assigned requirement that date changes affect only metadata.

Reproduction: run the preserved probe without extra arguments and inspect `current-date-owner-historical-fence` versus `before-date-owner-historical-fence`. Registry reconciliation is `2026-10-08`; Markdown begins with `Reconciled: 2026-10-07.` and contains a fenced historical example `Reconciled: 2024-02-29.` before the generated records.

Expected: update the catalog's metadata line to `2026-10-08`, preserve the fenced historical date `2024-02-29`, and reject ambiguous/malformed ownership if a unique metadata field cannot be located. Actual: current changes both dates to `2026-10-08`; render and subsequent `--check` return 0. Exact-before preserves both original dates. Separate malformed input `Reconciled: 2026-10-07T23:00:00+02:00.` becomes `Reconciled: 2026-10-08T23:00:00+02:00.` and also passes check; a missing metadata line passes unchanged. Those variants demonstrate that the replacement is not an exact owned-field boundary.

Required repair: locate one explicit catalog reconciliation field and update only its full validated value, without traversing historical prose/code. Add a public CLI regression for the fenced example.

### 2 of the 2 found so far. BLOCKING: metadata entity decoding also changes handwritten code examples

`scripts/render_research_dashboard.py:240` applies metadata punctuation decoding to the entire rendered HTML body. Numeric punctuation references in ordinary fenced code outside the generated region are therefore treated as metadata encodings. Markdown and HTML no longer show the same code value.

Reproduction: run the preserved probe with `--entities`. The valid dashboard preamble contains a fenced code line `&#35; &#60; &#39; &amp;`, and registry fields use normal valid metadata.

Expected: HTML code text remains exactly `&#35; &#60; &#39; &amp;`, matching the unchanged Markdown code. Actual: current HTML displays `# < ' &amp;`; Markdown still contains the original code. Both render and `--check` return 0. Exact-before HTML displays the original literal references and also passes check. This is a new regression, not an inherited renderer limitation or an active-code injection.

Required repair: restrict decoding to content emitted from metadata, preserving independently authored prose and code. Add a public CLI regression that checks both output presentations outside the generated region.

## Standards and spec axes

Standards: finding 1 violates historical-fact preservation; finding 2 violates representation agreement and the handwritten/generated-content boundary. No new provider dependency, runtime authority path, scoring computation, or learned promotion was found. No smell-only optional finding is reported.

Spec: the declared literal-metadata attacks are fixed and the normal reconciliation control works. Findings 1 and 2 are collateral changes outside those owned fields. The repository contract and parent's bounded literal/date requirements are the available spec; no writer rationale was used.

## Five design principles

1. Separation of concerns: violation at `scripts/render_research_dashboard.py:240`, finding 2. Metadata decoding runs over independent handwritten code rather than the generated metadata representation.
2. Programming by intention: OK. The CLI, registry validation, and record renderer retain named public responsibilities; no additional naming-only issue was found.
3. Encapsulation: violation at `scripts/render_research_dashboard.py:229`, finding 1. Updating one owned metadata field mutates historical text in the surrounding preamble.
4. High cohesion: OK within the bounded change, apart from the two identified scope leaks. Record projection remains metadata/navigation-only.
5. Low coupling: OK. No new runtime/provider/core imports or independent release authority were added. Registry labels remain unscored; valid source-hash rejection remains enforced.

No duplicated domain policy, second release owner, or business-rule computation in filter templates was found. The metadata-to-HTML decoding contract must be scoped correctly before approval.

Residual limits: browser-layout/accessibility behavior was not exercised; Node checked filter logic over parsed generated rows. Hooks were intentionally not installed or run. No package-wide or live-provider claim follows from these checks. The next discriminating probe is the same exact-before/current fixture after an explicitly bounded field/region repair.

VERDICT: CHANGES
