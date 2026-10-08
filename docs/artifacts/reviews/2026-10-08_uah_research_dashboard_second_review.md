# Research dashboard independent second review

Date: 2026-10-08. Base: `28fab5e7f2c244d86a64c371f2118017999b2387`.
Requested reviewer configuration: `gpt-6-astra`, `max`, fresh context. The
orchestrator confirmed those requested settings; backend identity is not
independently observable. I did not author this change or inspect the dashboard
writer's receipt, rationale, or primary review.

## Scope and authority

Reviewed only the eight files hashed below. The generic renderer comparison is
against `/tmp/uah-research-dashboard-before-20261008/render_agentic_harness_docs.py`:
exactly eight added lines. Other dirty runtime and documentation changes are
outside this verdict. No source, Git state, provider, or hook was mutated.
Temporary CLI fixtures and this review artifact were written.

`REVIEW.md` owns this review's policy. The code-review and UAH guardrails skills
informed the standards/spec split and authority inspection. The supplied scope
did not include an originating issue or independently frozen product spec;
specification conclusions are limited to the new README's public contract and
the supplied review brief. I did not commission nested reviewers or present
this single review as two independent reviews.

This is H0-H4 research navigation, not a release gate implementation. The
masterplan retains release ownership; environment owners retain effect truth;
the ledger remains runtime evidence authority. The dashboard imports no runtime
or provider package, grants no execution authority, assigns no AB capability
score, and does not turn historical reviews into current-checkout approval.

## Predeclared probes

Before reading implementation/diff, I declared canonical and alternate CLI
forms, combined malformed inputs, duplicate IDs, unsupported kind/status,
additional metrics, invalid/leap/year-boundary dates, missing/traversing/symlink
paths, absent/altered hashes, HTML-special text, empty/no-match filtering, and
metadata/card/count/link agreement. I also declared exact-before generic
renderer comparison and inspection for invented measurements or authority.

Initial execution before source inspection:

```text
python scripts/render_research_dashboard.py --help
python scripts/render_research_dashboard.py --check
python scripts/render_research_dashboard.py --check --unknown
```

Results: help exit 0; check exit 0, 12 metadata records; unknown option exit 2.
Unicode line-separator probes were a follow-up to the predeclared escaping and
render-consistency checks after inspecting the shared parser boundary.

## Findings

### 1 of the 3 found so far. BLOCKING: reconciliation has two unchecked copies

Location: `scripts/render_research_dashboard.py:229` and
`docs/research/uah_research_dashboard.md:3`.

Input: render a valid registry and Markdown header dated `2026-10-08`, then
change only registry `reconciled_at` to `2026-10-09` and run `--as-of 2026-10-09
--check`. Expected: reject the stale displayed reconciliation date, or derive
that displayed date from registry metadata during generation. Actual: exit 0;
the displayed header remains `Reconciled: 2026-10-08.` while the canonical
registry says `2026-10-09`. The generator preserves `before` verbatim and does
not consume `reconciled_at` when building output. A later reconciliation can
therefore pass the documentation gate with contradictory snapshot metadata.

Reproduction: `.venv/bin/python /tmp/uah_dashboard_second_probe.py`, result
`changed_reconciliation`. Its full subprocess invocation is printed, including
the temporary paths. This also reproduces with the complete real dashboard
shape, which uses the same separately authored header outside the generated
region. The current checked-in values agree; the failure concerns the public
update/check path.

### 2 of the 3 found so far. BLOCKING: accepted line separators remove records from the filter table

Location: `scripts/render_research_dashboard.py:176` and
`scripts/render_research_dashboard.py:192`.

Input: a valid one-record registry with title `First\u2028Second`. The same
failure occurs with U+2029, U+0085, vertical tab and form feed. Expected: either
reject these inputs before writing output or normalize the title into one
table cell; the one catalog record must remain present in the interactive
index. Actual: generation exits 0, but the table body contains zero data cells
instead of six. `metadata_text` normalizes only CR/LF, whereas the shared
Markdown renderer uses `splitlines()`. The one row becomes prose outside the
table. Executing the generated filter script reports `No matching catalog
records.` on initialization although the registry contains one record.
`--check` accepts the generated result.

Reproduction:

```text
.venv/bin/python /tmp/uah_dashboard_second_probe.py
node /tmp/uah_dashboard_second_dom.cjs /tmp/uah-dashboard-second-0iznz3pv/docs/research/dashboard.html
.venv/bin/python scripts/render_research_dashboard.py --repo-root /tmp/uah-dashboard-second-0iznz3pv --registry /tmp/uah-dashboard-second-0iznz3pv/registry.json --markdown /tmp/uah-dashboard-second-0iznz3pv/docs/research/dashboard.md --as-of 2026-10-08 --check
```

The retained fixture uses the last separator, form feed; rerunning the Python
probe prints fresh temporary paths and independently tests all five forms.
The Node harness executes the actual generated script against a minimal DOM
model built from its HTML. This is not a claim of real-browser visual QA.

### 3 of the 3 found so far. NIT: literal punctuation is displayed as entity syntax

Location: `scripts/render_research_dashboard.py:178`.

Input title: `A [bracket] *star* ` followed by literal backtick-delimited `tick`,
then ` | pipe </script>`. Expected: display the literal title without making
active HTML or Markdown. Actual: the HTML parser exposes literal `&#91;`,
`&#42;`, `&#96;` and `&#124;` text because `metadata_text` inserts entities and
the shared renderer escapes their ampersands again. No injected image or
`javascript:` anchor was emitted. Reproduction: Python probe results
`escaping` and `literal_title`; `title_preserved=false`,
`encoded_bracket_visible=true`, `active_payload=[]`.

## Executed evidence

```text
.venv/bin/python -m pytest tests/test_research_dashboard.py -q -p no:cacheprovider
python scripts/render_agentic_harness_docs.py --check
git diff --check -- scripts/render_agentic_harness_docs.py
.venv/bin/python /tmp/uah_dashboard_second_probe.py
node /tmp/uah_dashboard_second_dom.cjs
diff -u /tmp/uah-research-dashboard-before-20261008/render_agentic_harness_docs.py scripts/render_agentic_harness_docs.py
git diff --numstat -- scripts/render_agentic_harness_docs.py
```

The focused suite passed 23 tests. Current generic check passed. The Python
probe imported the exact-before generic renderer with `ROOT` and `RENDERER`
pointing at this same checkout and ran `main(['--check'])`: exit 0. Thus the
old canonical-document path remains green; the new dashboard-specific failures
are not silently attributed to unrelated dirty files. `git cat-file -e
28fab5e:<path>` returned 128 for the dashboard script, tests and registry: no
base API exists for those new files, so a behavioral base comparison is
unavailable rather than a claimed base pass.

The independent CLI matrix rejected extra metrics at root/record level,
an extra `status`, duplicate IDs/JSON keys, unknown and uppercase kinds,
future date plus bad hash, non-leap February 29, timezone timestamps, numeric
dates, future reconciliation, dates after reconciliation, missing/absolute/
traversing/symlink-escaping sources, wrong/uppercase/missing hashes, duplicate
or non-string dependencies, and missing references. Every expected rejection
returned 1 and preserved both outputs. Valid leap day, year-boundary dates,
unknown date, all five kinds, 0/2/20 records, reverse ordering, and
`--as-of=20261008` succeeded.

All kind consumers were inspected: validation, the dependency-only null-hash
exception, Markdown row rendering, generated buttons, and JavaScript filtering.
No separate lifecycle status enum exists; adding a status field is rejected.
The real document has 12 rows, 12 `not_scored` cells, 12 source links and 12
summary IDs. Runtime script checks reported kind counts 4/1/2/2/3 and H0-H6
counts 7/9/3/4/2/0/0, matching registry metadata. A no-match query returned the
empty message. Filtering/search operates on table cells only; source summaries
remain outside that filtering scope. Source pinning validates stored bytes,
not historical claim truth or owner review completion. No numerical runtime
result was inferred.

Local href/src existence was checked with Python `HTMLParser`, URI-unquoting
each relative target against `docs/research`; no missing target was printed.
Static fallback includes all real records without a hidden attribute. I did
not conduct browser visual QA or bypass any browser access restriction. I did
not rerun setup or pre-commit hooks, as this review was explicitly non-mutating.

## Design principles

1. Separation of concerns: OK. Registry validation/rendering is independent
   of runtime admission and evidence authority; JavaScript filters presentation.
2. Programming by intention: OK. `local_document`, `catalog_date`,
   `load_registry`, and `render_records` express their bounded responsibilities.
3. Encapsulation: violation at `scripts/render_research_dashboard.py:229` and
   `docs/research/uah_research_dashboard.md:3`: registry reconciliation metadata
   is copied into independently authored output without a consistency boundary
   (finding 1). Encoding also fails its shared-parser boundary (finding 2).
4. High cohesion: OK. The new script owns a single metadata-navigation product;
   the generic renderer only delegates to it.
5. Low coupling: OK. Shared Markdown/theme dependencies are existing local
   utilities; the catalog does not import or write a runtime subsystem.

## Reviewed hashes

The first and final scope hash reads agreed.

```text
b7e8424a47614245c5432473259aa100eb2cd7aef86d01603e01a0a8ea6f832c  docs/research/README.md
398fbaf361eaf7204b35f273f1150de6062056d27d1430ebac4b4cb6017ae11d  docs/research/uah_research_dashboard.md
8758404b6f378dfa046347fc44c32ecdfc87885d0e9ac6b27b1481f599701e80  docs/research/uah_research_dashboard.html
d2871c360d5995c2d7a77eeff5b430f4c986225280dd4b83e54ffef7324e87c4  docs/research/experiment_registry.json
7c28c5f2f81cc95807a71ab7652e302c9e68d1cdabae89a1189316fbe8f75115  docs/artifacts/research/README.md
3b6ae46eaea0428a402a8650e44f0b1bacb5ebbb9e3ebde1300c5afaabb3dbc3  scripts/render_research_dashboard.py
6a8427e21427b309bfac44f0c0c0570802536f5215df69144e993b3c6be44bbf  tests/test_research_dashboard.py
ae0a51e043245fcd460ddf61708268c1132b5fffd0790e0cd743c318f85bd8da  scripts/render_agentic_harness_docs.py
732aba2d4ea8c7e73b407ea11a14bafdbdda438f19da5816832d527a7b40c9f6  exact-before generic renderer
c00ac945a7d27de753e84500f684d97edb64170da957af2f3ede0bfd7e0ff51d  /tmp/uah_dashboard_second_probe.py
807b6eaf293e950b78a479ff721822928adc9060a682745158a027910f4132ac  /tmp/uah_dashboard_second_dom.cjs
```

Two blocking findings and one optional nit. Existing measurements, independent
historical review conclusions and runtime qualification remain outside this
verdict. Next discriminating probes are a reconciliation-only update and the
five non-CR/LF separators through generation, check and filtering after repair.

VERDICT: CHANGES
