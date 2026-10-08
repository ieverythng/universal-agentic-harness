# R4 admitted-object snapshot: independent second review

Date: 2026-10-08, Europe/Madrid. Public probes completed at 17:23; final freeze
checked at 17:26. Scope: H0 semantic admission, owner execution and common-ledger
replay, with bounded H1 consumers. This is an implementation review, not release
qualification.

Requested reviewer: `gpt-6-astra`, reasoning `max`, fresh `fork_turns=none`, as
reported by the coordinating agent. The backend model identity and reasoning
configuration are not independently observable through this review's tools.
The different-model requirement is therefore recorded as requested configuration,
not an independently attested backend fact. This reviewer did not write runtime
code and did not read the writer receipt, rationale, or another review.

## Scope and method

Read `REVIEW.md` before implementation. Applied the code-review standards/spec
axes, UAH guardrails and bounded stack-review workflow. The repository workflow
keeps findings local and configures no external tracker. Governing sources were
`AGENTS.md`, `CONTEXT.md`, the masterplan, foundation, ADR 0001, current development
status and `docs/agents/uah_review_workflow.md`.

The exact base is the five supplied `.before` files in
`2026-10-08_uah_r4_admitted_object_snapshot_evidence`, overlaid onto an isolated
copy of the current repository's other source and test files. It is not the
Git merge-base. Both copies have Git context
`28fab5e7f2c244d86a64c371f2118017999b2387`, branch `feat/pre-commit-queue`;
no review commit was created. The tree was already dirty. No runtime files were
edited, staged, reset, or committed by this reviewer.

[Predeclared inputs](2026-10-08_uah_r4_admitted_object_snapshot_evidence/second_review_predeclared.md)
were written before source/diff inspection. The first execution was the unread
existing public two-stage admission suite on both isolated copies: 48 passed
on current and 48 on base. The implementation was inspected only afterward.

Current reviewed SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `src/ab_harness/proposal_admission.py` | `7b52d38ebda8e377c4100494ed6d40bc2a027485da031afbee01a5a90ee2e86c` |
| `src/ab_harness/environment.py` | `d754415fe07e301da635706c5a9af218c507e35126a400b82b2d9a609ba5c0b7` |
| `src/ab_harness/lifecycle.py` | `2b3d80aa559257d0c6bb7165c73b7fe52d79319ba46cdab4736737b18be725a4` |
| `src/ab_harness/domain_lifecycle.py` | `ce472670140e418ba67c11736d70e240d9511b25584de7e638e36cac245c5aa3` |
| `tests/test_admitted_object_snapshot.py` | `cbff9c50f69659f2497b9b1a63f7d6088166589f726ff8be4bfeb466da696b5b` |

`domain_lifecycle.py` is byte-identical to its supplied base. Full dirty-path,
branch and additional test hashes are retained in
[the freeze record](2026-10-08_uah_r4_admitted_object_snapshot_evidence/second_review_freeze.txt).
The coordinator separately owns compatibility-test literals and generated O1
artifacts; these are not included in this frozen-source verdict.

## Standards

No separate standards-only finding. Semantic-artifact construction, environment
effects and lifecycle persistence retain their established owners. The snapshot
copy consists of immutable scalar/tuple fields, and the new serialized form is
detached. The change does not introduce ROS, provider SDK or runtime-product
imports, a second authority store, or UI-owned policy. The blocking issue below
is an authority-boundary failure, not a stylistic objection.

## Spec

### R4-S2-01: BLOCKING, 1 of the 1 found so far.

**Missing all v3 fields downgrades current admission to historical metadata and
allows active continuation.**

Location: `src/ab_harness/lifecycle.py:1878`, especially the optional `if any(...)`
guard before nested identity validation. The unchanged existing-lease consumer
at `src/ab_harness/domain_lifecycle.py:287` accepts the resulting ledger state.
Owner: common lifecycle ledger. Affected gate: H0 admission/replay authority,
also consumed by H1 execution.

Governing rule: foundation section 9 states that current semantic-admission
events carry the full artifact for nested/outer revalidation, while historical
metadata-only events remain read-only evidence. UAH guardrails require artifact
identity revalidation at trust crossings. AB coordinates remain frame-relative.

**Exact input:** produce a valid current admission and its already-recorded
lease through the public fixture. In only the `semantic_admission_accepted`
event's data, delete `admitted_operation`, `object_snapshot` and `schema_version`.
One variant leaves every remaining alias unchanged; a second sets
`frame_id="foreign_frame"`. Recompute the modified event's SHA-256 identity and
the causal descendant event IDs/parent references. Preserve all admission and
lease artifact IDs, including the original outer `admission_id`.

**Expected:** a current record missing its required authority bytes cannot be
treated as verified current admission. Historical metadata can remain readable,
but must not satisfy the active verified-snapshot prerequisite. The foreign
frame alias must not survive as an authoritative current admission projection.
No native handler call or terminal accepted continuation should result from
this downgraded admission record.

**Actual:** `LifecycleLedger(path)` and replay succeed. The record has no
snapshot; the altered variant reports `foreign_frame`.
`DomainLifecycleAdmission.request_execution(original_admitted_v3)` returns the
same existing lease ID. `InProcessEnvironmentOwner.execute(...)` calls the
native handler once and returns an execution receipt. Recording deterministic
acceptance succeeds; restart yields `terminal_status="accepted"`,
`failure_stage=None`. Both the admission ID and lease ID are unchanged.
The native effect in this probe is legitimate; the defect is active continuation
and accepted replay over missing authority bytes and inconsistent frame
metadata, not a demonstrated new unauthorized native effect.

**Base comparison:** the exact-before v2 metadata stream also permits the frame
alias alteration and active accepted continuation. This is a retained mechanism
that bypasses the new R4 full-artifact gate, not a claim that R4 introduced the
original metadata weakness. Removing any one of the three fields from current
records is rejected; removing all three reaches the historical branch.

**Repair boundary:** retain genuine historical read-only compatibility, but
represent unverified legacy admission separately from verified current
admission and fence active continuation. Do not synthesize missing snapshots
from the mutable catalog. A fresh focused review is required after repair.

## Executed evidence

The public reproduction is
[second_review_probes.py](2026-10-08_uah_r4_admitted_object_snapshot_evidence/second_review_probes.py).
It uses fixture construction only for valid starting inputs and independently
mutates the public serialized ledger boundary. All hostile files and native
handlers are synthetic. No provider, hardware or real environment was called.

Commands, with each command run from the indicated isolated directory:

```bash
# Both /tmp/uah_r4_second_review_current and /tmp/uah_r4_second_review_base
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q -p no:cacheprovider tests/test_two_stage_admission.py

# Current copy
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q -p no:cacheprovider tests/test_admitted_object_snapshot.py tests/test_two_stage_admission.py tests/test_lifecycle_ledger.py tests/test_content_identity_compatibility.py

# Base copy, then current copy; the first produces genuine v2 history
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python /home/juanbeck/universal-agentic-harness/docs/artifacts/reviews/2026-10-08_uah_r4_admitted_object_snapshot_evidence/second_review_probes.py base
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python /home/juanbeck/universal-agentic-harness/docs/artifacts/reviews/2026-10-08_uah_r4_admitted_object_snapshot_evidence/second_review_probes.py current
```

The current focused suite passed 108 tests. Running the new snapshot suite on
the exact-before implementation produced 28 failures and 4 passes, including
expected unavailable-v3-field/API failures. That count is not itself proof of
28 defects. Independent before/current outputs provide the behavior comparison:
[base](2026-10-08_uah_r4_admitted_object_snapshot_evidence/second_review_base_output.jsonl),
[current](2026-10-08_uah_r4_admitted_object_snapshot_evidence/second_review_current_output.jsonl).

| Input | Exact-before | Current |
| --- | --- | --- |
| Unchanged valid object | One native call, receipt | One native call, receipt |
| Catalog widens observables before dispatch | One call, receipt | Rejected, zero native calls |
| Catalog widens observables inside handler | One call, receipt | One call, typed `undeclared_observed_effect`, no receipt, replay failure stage `evidence` |
| Revised reviewed binding with unchanged semantic object | Admission accepted | Admission accepted |
| Genuine v2 historical metadata produced on base | Five recorded events | Reloads without inventing a snapshot |
| Current missing snapshot/version fields individually, empty snapshot, active v2 payload | v3 reader unavailable | Rejected |
| Rehashed nested proposal for `{"label":"knife"}` under stale outer admission ID | v3 reader unavailable | Rejected by outer identity |
| Frame/object/input-schema/boolean-level summary alias mismatch | Not a v3 contract | Rejected when v3 body remains |
| All v3 fields removed, with/without foreign-frame alias | Metadata continuation accepted | Same continuation accepted; blocking |

The 108-test suite additionally exercised active lease/dispatch/receipt/serialization
crossings for stale IDs, missing/foreign/mutated snapshots and old schemas,
wire-copy detachment, and unchanged positive restart paths. These are reported
as supplied-suite evidence, distinct from the independent probe script.

## Design principles

1. **Separation of concerns: OK.** Admission, domain leasing, effect ownership
   and common-ledger persistence remain separate.
2. **Programming by intention: OK.** The current snapshot payload and explicit
   catalog-equality gate express the intended policy; the identified branch
   omission is recorded under Spec.
3. **Encapsulation: violation, R4-S2-01**, `lifecycle.py:1878`.
   Deleting all authority fields selects a less-validated representation that
   still satisfies active lifecycle consumers.
4. **High cohesion: OK.** Snapshot integrity resides with `AdmittedOperation`;
   current replay joins the artifact with event aliases locally.
5. **Low coupling: OK.** No adapter dependency or generalized cross-artifact
   codec was introduced. The ledger uses the artifact's own decoder.

## Limits and handoff

The isolated review intentionally did not repair runtime code. The predeclared
independent two-distinct-object/order probe was not completed within the bounded
window; no pass is claimed. Genuine historical active-object reconstruction was
not inferred from metadata. Generated O1 freshness remains a coordinator-owned
final gate. This reviewer ran `./scripts/run_precommit.sh` after saving the
report; every hook passed, including source-aware tests and generated-document
synchronization. Canonical-document `--check` and final `git diff --check`
also passed. Final runtime/test hashes remain identical to the frozen table. The
bounded owner/evidence protection is improved, but R4 remains open on the replay
downgrade. H0/H1 exit and H2 qualification are not established.

VERDICT: CHANGES
