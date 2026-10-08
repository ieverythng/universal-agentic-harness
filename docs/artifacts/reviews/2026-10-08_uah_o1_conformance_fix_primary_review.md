# Independent O1 conformance fix review

Date: 2026-10-08, Europe/Madrid. Review completed before 17:54.

## Scope and independence

I read `REVIEW.md` first. Inputs were recorded in
`2026-10-08_uah_o1_conformance_fix_primary_review_inputs.md` before inspecting
the changed source, test, or diff. The initial public control executed before
that inspection. No writer receipt, writer test logs, or other review report
was opened. Required UAH governing-contract reading incidentally encountered
the current-state repair paragraph in `observatory_contract.md`; the paragraph
was not an input oracle, and its linked writer receipt was not opened.

The review compares the exact-before copies of `observatory.py` and
`test_observatory_raw_identity.py` with the frozen current files. Both isolated
packages use the identical immutable `lifecycle.py.before` dependency.
Other copied package dependencies were identical between the environments.
Their origin is the contemporaneous checkout, not a claim that unrelated R4
or documentation changes belong to O1.

Reviewed current SHA-256 values, rechecked after probing:

- `src/ab_harness/observatory.py`:
  `313798f6e660f913622695dd8c19d52c0ab269c71dbc6eab1e6a5472d26236fe`
- `tests/test_observatory_raw_identity.py`:
  `d20059458b6fe87e1e7ac8bdf0a7307aed2f26d71244009e22c861a3e6bc3b2a`
- Both isolated lifecycle dependencies:
  `b35641d97b8d915df358e880de73400386395e8b3525a41cae99e329b04176ee`

Requested reviewer configuration: sol/max. The backend model and effort are
unobservable through the available tools, so exact compliance cannot be
attested. No nested reviewer agents were used; standards and spec were assessed
separately within this fresh reviewer.

## Executed evidence

Throwaway root: `/tmp/uah-o1-primary.8e8Vqy`. `PYTHONPATH` selected its `before`
or `current` package. Imports were checked to resolve to the isolated current
Observatory and lifecycle modules. Pytest used `-q -p no:cacheprovider -c
/dev/null`, avoiding repository pytest configuration and cache writes.

| Public execution | Exact-before | Current |
| --- | --- | --- |
| Initial original `test_observatory.py` control, before source/diff inspection | 23 passed | 23 passed |
| Original control plus exact-before raw-identity suite | 31 passed | 31 passed |
| Current `test_observatory.py` and raw-identity suite | 33 passed, 4 failed | 37 passed |
| Independent public-seam matrix | 134 cases, 60 expectation mismatches | 134 cases, 0 expectation mismatches |

The initial control setup first omitted the identical `ab_harness_nao` fixture
dependency, causing collection errors in both environments. Copying that
dependency identically corrected collection; the successful controls above
still preceded source/diff inspection.

The independent executable is
`2026-10-08_uah_o1_conformance_fix_primary_probe.py`. Complete expected/actual
records are saved in
`2026-10-08_uah_o1_conformance_fix_primary_before_results.json` and
`2026-10-08_uah_o1_conformance_fix_primary_current_results.json`.

Reproduce either matrix with:

```bash
PYTHONPATH=/tmp/uah-o1-primary.8e8Vqy/before python3 docs/artifacts/reviews/2026-10-08_uah_o1_conformance_fix_primary_probe.py
PYTHONPATH=/tmp/uah-o1-primary.8e8Vqy/current python3 docs/artifacts/reviews/2026-10-08_uah_o1_conformance_fix_primary_probe.py
```

The matrix covers both projection and render consumers, raw tuples and
single-use generators, genuine v1 excluded-field mutations individually and
combined, valid v1 tasks, v2 tasks and agents, all six mixed-history input
orders, empty inputs, covered stale identities, invalid constructor shapes and
types, unknown schemas, foreign formats, duplicate identities, existing actor
and trace lineage checks, and later input alias mutation. Graph event IDs and
rendered HTML agree with accepted projections. Explicit acceptance, acceptance
with deficit, rejection, and nonterminal failure families preserve their
existing status distinctions.

Representative discriminating probes:

- Input: a genuine v1 event with only `agent_run_id="actor:forged"` changed.
  Its v1 hash remains valid. Expected: owner-shape rejection before actor
  grouping. Exact-before creates the forged actor view; current raises
  `ValueError: v1 events require task scope without actor identity`.
- Input: the same event with only `event_scope="agent"`, or both excluded
  scope and actor fields changed. Expected: rejection without hiding the task
  trace. Exact-before accepts and omits that task trace; current rejects in
  both public consumers and both iterable forms with the owner message above.
- Input: change a covered terminal kind, environment, task, trace, sequence,
  timestamp, commit framing, artifact references, payload, operation, or parent
  while retaining the old identity. Expected and current: rejection before
  status/grouping/rendering. These protections also remain present in the
  exact-before identity-only implementation.
- Input: project a valid v2 task event, then mutate its original environment,
  actor, kind, trace, and payload. Expected: all retained fields and grouping
  stay unchanged. Exact-before retains aliases and changes the environment
  projection; current retains a detached event shared by its event, trace,
  and actor views. Mutating a dictionary returned by `event.data` changes
  neither original nor projected canonical payload.
- Input: a correctly identified standalone terminal illustration, missing
  causal parent, incomplete commit illustration, or distinct events sharing a
  sequence. Expected: preserve the existing raw synthetic contract rather
  than impose ledger causal completeness. Both versions accept these inputs;
  current preserves their synthetic label. Duplicate event identities remain
  rejected in both versions.

Additional checks: reviewer probe Ruff check passed; documentation renderer
`--check` passed with 12 metadata records. The full pre-commit runner was not
invoked by this reviewer because its hygiene fixers and cache recording can
write outside the permitted reviewer artifacts. Its repository-wide gate
remains the parent's responsibility. No source, hook, provider, or Git state
was edited.

## Standards

1. Separation of concerns: OK. At `src/ab_harness/observatory.py:242`, the
   projection delegates shape and identity to the existing lifecycle-owner
   constructor. It does not duplicate those rules or acquire write authority.
2. Programming by intention: OK. The boundary reconstructs validated event
   values before duplicate checks, ordering, actor grouping, or status
   derivation (`observatory.py:240`). The added tests state the excluded-field,
   aliasing, and valid-input intent directly.
3. Encapsulation: OK. The public owner constructor provides validation and a
   detached frozen value. The retained actor and trace views share that
   detached value, not the original caller object (`observatory.py:242`).
4. High cohesion: OK. The change is confined to Observatory ingress and its
   public regression tests. Rendering consumes the same projection at
   `observatory.py:288`; no business logic was added to HTML or client code.
5. Low coupling: OK. The existing `TraceEvent` dependency and standard-library
   dataclass conversion suffice. No provider, ROS, NAO, or runtime-product
   import enters the portable kernel (`observatory.py:5`).

No domain acquires two owners, no validation logic is duplicated, and no
business rule moves into a template or UI.

## Spec

The affected boundary is the bounded O1 read-only projection supporting H0/H1
review. `TraceEvent` owns versioned event shape and content identity;
`LifecycleLedger` remains the write/replay owner. The fix preserves v1 identity
compatibility without treating hash-excluded v1 actor/scope fields as valid
lineage. Valid v2 explicit actors remain visible in actor and task views.
Read-only snapshot detachment prevents later caller mutations from changing
retained facts. The current implementation matches the bounded requested
conformance repair.

Shape and content identity are not evidence of causal completeness, effect
truth, freshness, or measurement provenance. ARCH-02 label policy remains
outside this verdict. This review does not qualify the complete O1 exit gate,
H0/H1 closure, H2 parity, or unrelated R4 fixes. The guardrails limited the
assessment to the existing owner constructor and preserved valid synthetic
illustrations rather than adding a second lifecycle policy.

## Findings

0 BLOCKING findings and 0 NIT findings in the frozen O1 fix. The exact-before
counterexamples above demonstrate repaired behavior, not remaining findings.
Residual gaps are the stated unobservable backend configuration and the
unexecuted repository-wide hook gate. After that gate, rerun the focused suite
if either frozen file or its owner dependency changes.

VERDICT: APPROVE
