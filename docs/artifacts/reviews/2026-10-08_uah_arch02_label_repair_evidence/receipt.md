# ARCH-02 unsupported-label repair

Date: 2026-10-08. Writer source/test freeze: 19:11:26 UTC.
Base and HEAD: `864c6d3d6eb7b978c426327f877059e956a9e882`.
No staging, commit, push or other Git write was performed in this round.

## Scope and mechanism

The human selected rejection of unsupported `measured` and `reviewed` requests.
The affected seam is O1 read-only projection over H0/H1 lifecycle records.
`project_observatory` owns label consistency for both projection and rendering.
Evaluator/result and independent-gate owners retain measurement and review
authority. A validated ledger or content hash establishes neither class.

The implementation adds one two-line check after the existing source-default
and enum resolution. Either unsupported enum member raises `ValueError` with
an explicit unsupported-label message. `render_observatory` reaches the same
check through its existing projection call. There is no downgrade, evidence
interface, new store or caller-hash proof. Enum vocabulary, falsey defaults,
invalid-enum errors and raw-recorded rejection remain unchanged.

Only `src/ab_harness/observatory.py` and the new
`tests/test_observatory_provenance.py` were changed. The previously committed O1
template whitespace fix and the existing identity, shape and detachment tests
were not changed. Canonical documentation belongs to the root round.

| Mechanism | Public probe | Observed outcome |
| --- | --- | --- |
| Unsupported caller upgrade | measured/reviewed × enum/string × ledger/tuple/generator × empty/nonempty × project/render | All 48 requests reject. No ledger append or file creation occurs. |
| Supported explicit labels | conceptual/synthetic across both label forms and every source/consumer/population | Requested label and exact lineage are retained. |
| Existing defaults | None, empty string, False and zero across source/consumer/population | Ledger remains recorded; raw remains synthetic. |
| Existing restriction and errors | Raw recorded requests and unknown enum values | Original rejection/error behavior is retained. |
| Restart and read-only output | Explicit/default recorded projections after reopening a ledger | Projection/document, graph JSON and file bytes remain equal. |

## Baseline, red and green

The root captured full dirty status, exact before bytes and hashes in
`/tmp/uah-arch02-before`. This evidence directory retains the source before
bytes, incremental delta and predeclared controls. Existing human-owned changes
and concurrent canonical-document edits were preserved.

Baseline: [baseline.txt](baseline.txt), 38 existing Observatory tests passed.
First public red: [red.txt](red.txt), raw events requesting `measured` did not
raise. The first minimal green slice passed 39 tests. The expanded gate in
[focused-checks.txt](focused-checks.txt) passes 213 tests, comprising the 38
protected tests and 175 new rejection/compatibility controls.
[full-suite.txt](full-suite.txt) records 724 passing shared-workspace tests in
12.72 seconds. This includes the existing uncommitted synthetic tests without
modifying their source or claiming that integration is accepted.

Exact additional commands executed:

```text
.venv/bin/python -m ruff check src/ab_harness/observatory.py tests/test_observatory_provenance.py
.venv/bin/python scripts/render_agent_runtime_example.py --check
.venv/bin/python scripts/render_observatory_example.py --check
.venv/bin/python scripts/render_agentic_harness_docs.py --check
git diff --check
```

Ruff, both current O1 freshness checks, canonical synchronization (12 metadata
records) and diff hygiene passed. The root round owns the final normal hook run
on an isolated snapshot, protecting concurrent human bytes from hook rewriting.

Frozen SHA-256:

```text
d63bcd3dd465019f04cc19ef0a8a84101e747491211426a6a159e484ad5ab13d  src/ab_harness/observatory.py
d8211c637c8af63c4121fd4c78e8dc14e0814ea75180bd32f023e6be4ce905d7  tests/test_observatory_provenance.py
```

## Disposition

The bounded correction and writer self-check are complete. Independent reviews
and final normal-hook evidence remain root-owned gates. This receipt does not
issue implementation approval or close O1/H0/H1/H2 release qualification.
Authentic measurement/reviewer evidence consumption remains deferred. No new
policy decision or compatibility path was adopted beyond the human-selected
unsupported-label rejection.
