# Research dashboard fix: independent second review

Reviewed 2026-10-08, approximately 16:58-17:04 Europe/Madrid. Scope is the
four-file fix against the exact `.before` copies in
`2026-10-08_uah_research_dashboard_fix_evidence`, not the entire dirty checkout.
The supplied checkout anchor is `28fab5e`; no Git operations were performed.

This fresh reviewer did not write the fix and did not consult writer receipts,
rationale, saved probe programs, or other review reports. Dispatch explicitly
requested `gpt-6-astra` with `max` reasoning as the distinct-model second review.
The backend model identity is not independently observable from this session.

## Frozen bytes

SHA-256 identities were verified before probing and again afterward:

| File | Exact before | Reviewed current |
| --- | --- | --- |
| `scripts/render_research_dashboard.py` | `3b6ae46eaea0428a402a8650e44f0b1bacb5ebbb9e3ebde1300c5afaabb3dbc3` | `7d6f73a54f3e334905b90ed67b51dbf2a43f94df540e1c96ab31850e60f8cf61` |
| `tests/test_research_dashboard.py` | `6a8427e21427b309bfac44f0c0c0570802536f5215df69144e993b3c6be44bbf` | `964350ab2950eb2e3a09a9278bb960982b0fa9306cdd7cfdf4f969c1dd7dad0c` |
| `docs/research/uah_research_dashboard.md` | `398fbaf361eaf7204b35f273f1150de6062056d27d1430ebac4b4cb6017ae11d` | `3e7cc69e0a7df0acb833f8f2c0a9165fe0652e4f118ac7c0a1fb7f31826b3359` |
| `docs/research/uah_research_dashboard.html` | `8758404b6f378dfa046347fc44c32ecdfc87885d0e9ac6b27b1481f599701e80` | `8758404b6f378dfa046347fc44c32ecdfc87885d0e9ac6b27b1481f599701e80` |

The unchanged HTML bytes are expected for the canonical data. Markdown now
encodes punctuation while preserving the rendered text.

## Execute-before-read evidence

Before implementation or diff inspection, inputs and expected behavior were
recorded in `/tmp/uah-dashboard-fix-second-predeclared.txt`, SHA-256
`b0566b5708df859046813f4fd74d3766a4497bc3a990fa8dab201ec01319bdd5`.
The first public probes were `python scripts/render_research_dashboard.py
--help` and `python scripts/render_research_dashboard.py --repo-root
/home/juanbeck/universal-agentic-harness --check`. The latter returned
`Checked 12 metadata records` before implementation inspection.

Two setup failures are excluded from product findings: running the relocated
before-copy without `PYTHONPATH=scripts` lacked its shared renderer import;
rendering to a nonexistent Markdown template correctly failed. The corrected
before-copy ran with `PYTHONPATH=scripts` and explicit root/template arguments.
Its check against current Markdown rejected stale generated content. Subsequent
paired renders used existing templates in isolated copies and each version's
own regenerated output. The before-copy API was available; no committed-HEAD
API parity is claimed or inferred if that API is absent at the supplied anchor.

Independent executable probes are `/tmp/uah-dashboard-fix-second-probe.py`
(SHA-256 `aa56a6c516fe885e2e00a6d0319e59e83e5d3776ad2211b17b82e304db848b7c`)
and `/tmp/uah-dashboard-fix-second-filters.cjs`
(`b6b0c5495fabee711562707b66fa151efaa001959a703bdda76c1e6221529c1c`).
Run them as:

```bash
python /tmp/uah-dashboard-fix-second-probe.py
node /tmp/uah-dashboard-fix-second-filters.cjs /tmp/uah-second-21oustyh
python -m pytest tests/test_research_dashboard.py -q -p no:cacheprovider
python scripts/render_research_dashboard.py --check
```

The Python probe prints its new temporary root on each run; use that root for
the JavaScript probe. Saved results from this run are
`/tmp/uah-second-21oustyh/results.json`, SHA-256
`62be041e7b95a657c16a072a6ff6cf465910e9ab9e137c52190744aff70fe75e`.
These temporary paths are reproducibility aids, not permanent repository APIs.

### Results

- 27 fixtures were rendered against both exact versions: 54 public CLI render
  calls. Current results were 15 accepted and 12 rejected, all as expected.
  Every accepted current render passed its following `--check`. Every rejected
  case retained its input Markdown and created no HTML.
- The untouched 12-record control, reversed record order, empty catalog and
  one-record fixtures retained source order/counts and six columns per row.
  Source references were copied byte-for-byte, not interpreted as instructions.
- Literal fixtures combined HTML/script tags, Markdown links, backticks,
  underscore/asterisk emphasis, pipes, quotes, slashes, every common punctuation
  class, marker comments, literal numeric/named/hexadecimal entities, tabs,
  Greek/Japanese text, combining accents, emoji and bidi controls. Current
  HTML text preserved the intended literals, with no injected image or unsafe
  link. Markdown entity-decoded rows and detail headings/summaries agreed with
  registry text and retained exactly one generated-region marker pair.
- A combined LF/CRLF/U+2028/U+2029/U+0085/VT/FF/U+001C/U+001D/U+001E fixture
  produced zero parsed catalog rows before and 12 after. Current output
  consistently normalizes these separators to spaces. Literal marker comments
  also broke the before-copy's following check, but current render/check passes.
- Reconciliation ownership: registry `2026-10-07` with an existing Markdown
  `2026-10-08` header and one eligible record left the old date before, but
  updated both current presentations to `2026-10-07`. Leap day `2024-02-29`,
  year boundary dates and null record date remained valid; null displayed
  `unknown`. Invalid `2026-02-29`, empty dates, future dates and timezone-qualified
  timestamps rejected with explicit CLI errors. An extraneous `owner` field
  rejected under the closed record schema.
- `javascript:`, `data:`, protocol-relative and traversal source paths rejected.
  A nonexistent entity-obfuscated document path also rejected. Missing hash
  rejected with the exact-source-fields error; null hash on a research record
  rejected with the SHA-256 requirement. A permitted null-hash dependency stayed
  an `unpinned dependency link`, never a measured or reviewed result.
- The actual generated filter JavaScript executed against a small DOM model
  for canonical, three adversarial, empty and reversed fixtures. All 1,440
  kind/dependency/search combinations agreed with independent source-derived
  visible-row counts and displayed count labels. There are no status-promotion
  cards: detail sections and rows retain metadata kinds and `not_scored`.
- Focused public suite: **38 passed in 3.24 seconds**. The final canonical
  generator check again returned `Checked 12 metadata records`.

## Standards

No BLOCKING or NIT findings in the scoped fix. The exact diffs were inspected
after executable controls. The added tests exercise the public generator;
generated Markdown and unchanged HTML remain synchronized.

## Spec and authority

No BLOCKING or NIT findings in the scoped fix. Governing sources were
`AGENTS.md`, `REVIEW.md`, `CONTEXT.md`, relevant masterplan/Observatory/current
development sections, and `docs/agents/uah_review_workflow.md`. The requested
literal-text and reconciliation-ownership fixes match their public behavior.

This is research navigation for H0-H2 dependencies and H3+ proposals, not a
release gate implementation. The registry owns catalog metadata; canonical
plans own release decisions; environment owners retain effect authority. No
portable-kernel import, admission, lifecycle, provider or promotion seam changes.
The UAH guardrail skill constrained interpretation of every passing check to
metadata/rendering evidence. No source document or receipt hash is itself
qualification, and no result here closes H0, H1, O1, H2 or model-performance gates.

## Design principles

1. **Separation of concerns: OK.** Validation remains separate from projection;
   client filters select already-rendered metadata without authority decisions.
2. **Programming by intention: OK.** `metadata_text` expresses literal rendering;
   public regression tests name the intended ownership and preservation rules.
3. **Encapsulation: OK.** The registry stays the metadata owner; escaping and
   corresponding presentation decoding remain local to this renderer.
4. **High cohesion: OK.** Changed logic concerns one projection's literal text
   and reconciliation date, not runtime semantics.
5. **Low coupling: OK.** No new external dependency or runtime-owner coupling.
   The paired encoding/decoding is one presentation mechanism, not duplicated
   domain policy or a second owner.

## Limits

This was a bounded four-file FIX review, not whole-repository certification.
No graphical browser/layout test was performed; JavaScript evidence uses a DOM
model. Exhaustive Unicode, every possible filename and arbitrary template
variants were not tested. No full suite, mutating hooks, setup, Git changes,
provider calls, or implementation edits were performed. The supplied commit
anchor/branch and complete dirty-file inventory were not independently queried;
the exact before/current hashes above delimit the approval. Review skill axes
are reported separately within this independent second-review scope; no further
reviewer delegation was performed. The next broader probe, if needed, is a real
browser test of accepted adversarial fixtures and accessibility/layout behavior.

VERDICT: APPROVE
