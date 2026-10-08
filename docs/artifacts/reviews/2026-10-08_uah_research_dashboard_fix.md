# Research dashboard correction round

## Independent review close, 17:06 Europe/Madrid

Overall verdict: CHANGES. The fresh primary reports two introduced blocking
scope leaks: global date substitution rewrites historical fenced dates, and
global entity restoration changes authored code examples in HTML. The distinct
second reviewer returns APPROVE with no findings. Approval of the round is
withheld because the reproduced primary findings remain unresolved.

The [primary report](2026-10-08_uah_research_dashboard_fix_primary_review.md)
and [second report](2026-10-08_uah_research_dashboard_fix_second_review.md)
retain their individual evidence and unchanged four-file hashes. Their hashes
are respectively `dec7d6b259a39bf6878e81c21359c36fe061deaa9fc606cd499414a2d6c37852`
and `5428a1563e1a98d91050f1449a116541a006508fe05eaabb2e6f902d14ef0b1f`.
Original malformed-metadata regressions pass, as do 403 then-current repository
tests and root pre-commit. Those controls do not close the new findings.

Main authorizes one final, separately frozen 15-minute authored-region
correction after R4 source freeze permits slots. It must preserve historical
preamble/code bytes and limit processing to the owned metadata/record region.
No source repair occurred after this review freeze. Earlier CHANGES receipts
remain retained; no dashboard qualification or H-series closure is claimed.

Date: 2026-10-08. Start 14:51:19 UTC (16:51:19 Europe/Madrid). Stop 15:11 UTC. Source freeze target 14:59 UTC. Separate from frozen R3 and the initial dashboard CHANGES closeout. HEAD 28fab5e7f2c244d86a64c371f2118017999b2387; no Git mutation or provider calls.

## Locked objective and scope

Registry reconciled_at is the date owner. Catalog text is literal in Markdown and HTML, cannot author generated delimiters/raw HTML/links, and cannot remove table rows with Unicode/control separators. Safe faithful punctuation display is part of the same escaping boundary. No metadata, record, registry, README, runtime or plan edits. Own only research renderer/tests and generated MD/HTML if changed, plus this dated receipt/evidence. Exact before copies and full dirty SHA-256 manifest retained. Initial independent CHANGES reports and closeout remain unmodified.

## Frozen acceptance and public seams

Use the existing CLI render/check with real temporary files, one red/minimal-green slice at a time. Train: registry-only date update; delimiter/raw HTML payload; Python splitlines separator forms. Holdout: punctuation and entity-looking literals, multiple-record MD/HTML counts/cards/links, actual generated filter script, unchanged valid source bytes, immediate check and rerender idempotence, invalid links and metadata preserving outputs. Tests and existing source-aware/docs/O1 checks must pass. Root coordinates full hooks after source freeze and commissions two fresh distinct-model reviews. No approval is claimed from author checks.

## Frozen correction delta

Source freeze: 14:56:36 UTC (16:56:36 Europe/Madrid), before the 14:59 UTC target.

| File | SHA-256 |
| --- | --- |
| scripts/render_research_dashboard.py | 7d6f73a54f3e334905b90ed67b51dbf2a43f94df540e1c96ab31850e60f8cf61 |
| tests/test_research_dashboard.py | 964350ab2950eb2e3a09a9278bb960982b0fa9306cdd7cfdf4f969c1dd7dad0c |
| docs/research/uah_research_dashboard.md | 3e7cc69e0a7df0acb833f8f2c0a9165fe0652e4f118ac7c0a1fb7f31826b3359 |
| docs/research/uah_research_dashboard.html | 8758404b6f378dfa046347fc44c32ecdfc87885d0e9ac6b27b1481f599701e80 |

The ordinary catalog HTML is byte-identical to the initial reviewed output. Markdown metadata punctuation is represented by numeric character references, preserving literal Markdown semantics. The shared renderer and theme were not edited. The existing reconciliation header is derived from registry metadata during render and check. Single-pass punctuation encoding prevents metadata from creating Markdown syntax or HTML comments. After the shared parser, the corresponding HTML-escaped punctuation is restored for literal display. Python splitlines normalization covers Unicode and control line separators before both presentations.

The registry remains 12 records and retains SHA-256 d2871c360d5995c2d7a77eeff5b430f4c986225280dd4b83e54ffef7324e87c4. Both catalog READMEs, all runtime sources, R3 hashes, original CHANGES reports and closeout are unchanged by this round. The copied public Python and Node probes retain their exact source hashes c00ac945a7d27de753e84500f684d97edb64170da957af2f3ede0bfd7e0ff51d and 807b6eaf293e950b78a479ff721822928adc9060a682745158a027910f4132ac.

## Executed vertical slices

1. Date test: one actual failure with a stale displayed date, then one pass after registry-derived header generation. Registry-only update rejects stale check, render updates both presentations, immediate check passes.
2. Literal text: five actual failures for generated start/end markers, raw image markup, punctuation/entity-looking text, and Markdown link/heading syntax. All five pass after single-pass encoding and safe display restoration. An intermediate replacement-loop implementation re-encoded its own entities and remained red; it was corrected within this same slice.
3. Separators: nine actual failures, then nine passes for U+2028, U+2029, U+0085, vertical tab, form feed, U+001C/U+001D/U+001E, and CRLF. Two records retain twelve cells, two source links, two not_scored cells and two summary IDs; normalized labels remain visible.

Each slice ran the public CLI with real temporary files. Initial red, final green and scoped delta files are retained in the evidence directory. No failing input was removed, no validation gate was weakened, and no provider was invoked.

## Verification and limits

- `.venv/bin/python -m pytest -q tests/test_research_dashboard.py`: 38 passed in 3.17 seconds.
- `.venv/bin/python -m pytest -q tests`: 403 passed in 6.76 seconds.
- Real CLI render, check, rerender and SHA-256 comparison: idempotent, 12 metadata records.
- Existing independent Python public probe: changed reconciliation check exits 1; title_preserved true, encoded_bracket_visible false, active_payload empty; each of the five original separator cases retains six cells.
- The unchanged Node probe executes the actual generated filter script against its minimal DOM model. Real initial count is 12; kind counts 4/1/2/2/3 and H0-H6 counts 7/9/3/4/2/0/0. The form-feed fixture initializes one catalog record, rather than losing its row. Empty search/filter results retain their existing message.
- Ruff check for renderer/tests, scoped Git diff check, canonical docs check and both O1 example checks pass. The invalid path/hash/link/metric tests continue rejecting before output writes; source bytes remain unchanged.
- Read-only Git manifest/diff checks were executed; no Git state was changed. The copied original public probe also performs read-only Git base-existence checks.
- MarkdownIt is unavailable in the current virtual environment, so no alternate Markdown engine run is asserted or dependency installed. Generated Markdown is checked for raw active markup and structural delimiters; the supported repository renderer is exercised end to end.
- No new browser visual QA is claimed. The real unchanged HTML remains covered only by prior visual evidence; this round's filter proof is an executed minimal-DOM harness, not browser layout certification.
- No full hooks were run by the author. Root coordinates those after this source freeze. No runtime, model, release or research-outcome qualification follows from these renderer checks.

## Handoff gate

Author implementation is frozen and handed off. Both initial independent CHANGES verdicts remain historical evidence. This correction requires two new fresh reviews on different models before acceptance. Review outcomes are pending at author handoff; no further autonomous correction round is authorized.
