# R4 admitted-object snapshot independent primary review

## Independence and declared inputs

I am a fresh reviewer and did not author the runtime change. I read `REVIEW.md`
before inspecting implementation or diff. These inputs were declared before
source inspection on 2026-10-08 at 15:16 UTC:

- Public control: existing `tests/test_two_stage_admission.py`, executed without
  reading its implementation first.
- Unchanged admitted object through a lease, nested proposal, outer envelope,
  serialized restart, and evidence consumer.
- Same semantic object with a revised binding and unchanged lineage.
- Object ID, schema version, operation contract, and descriptive metadata
  mutations, individually and together, before admission and dispatch.
- Missing, foreign, tampered, and unknown-version snapshots; historical metadata
  inspected read-only versus old authority used actively.
- Live catalog drift before dispatch and during dispatch; multiple objects and
  alternative operation orderings where the interfaces permit them.
- Exact pre-change equivalents of executable probes, in isolated temporary
  copies, to distinguish regressions from deliberate tightening.

Requested reviewer configuration is `gpt-6.1-sol` at `max` per `REVIEW.md`.
The tool interface does not expose backend model identity or reasoning effort;
I cannot independently attest the actual backend configuration.

No writer receipt or rationale is an input to this review. Runtime files in the
dirty working tree will not be edited.

## Execution and results

Scope is the supplied exact-before files versus the frozen current runtime,
plus `tests/test_admitted_object_snapshot.py`. `domain_lifecycle.py` and
`test_two_stage_admission.py` have no delta. The four supplied SHA-256 values
matched when inspected. No writer receipt or rationale was read.

The governing sources are `AGENTS.md`, `CONTEXT.md`, the foundation control-loop
contract, ADR 0001, the masterplan's current implementation and H2 qualification
sections, and the development log's current-state qualification. The affected
implementation is the H0/H1 portable authority prerequisite to H2. Semantic
admission owns the frozen artifact, domain lifecycle owns leasing, and the
environment owner owns dispatch and evidence. This review does not close
SPEC-03 as a whole, H0/H1 exit, H2 parity, or provider qualification.

Executed with `PYTHONDONTWRITEBYTECODE=1`, isolated source paths and
`pytest -p no:cacheprovider`:

- Before source inspection, the existing admission suite: 48 passed.
- Current isolated snapshot and admission suites: 80 passed.
- Exact-before isolated admission suite: 48 passed.
- Current isolated lifecycle and argument-schema suites: 34 passed. The latter
  includes the coordinating agent's separately updated v3 schema assertion.
- An independently constructed comparative probe changed every ABObjectView
  field. Current pre-dispatch semantic changes reject with zero native calls and
  no execution-start record. Unknown object IDs fail catalog construction.
  Before, observable widening dispatches and accepts prohibited `direct_speech`;
  changes to level, kind, category, expected effects and decomposition dispatch
  before evidence rejection. Owner and callable restrictions already rejected.
- A mid-handler observable widening accepts evidence before; current returns
  `undeclared_observed_effect` and restarts with failure stage `evidence`.
- Same unchanged semantic object with an approved revised binding remains
  admissible before and current. Current wire round-trip preserves identity.
  Missing/null/foreign snapshots, v2/v999 schemas, nested proposal mutation,
  stale admission ID, Boolean level, and a string instead of an effect list
  all reject. The new suite additionally exercised nested snapshot mutation
  across leasing, dispatch, receipt issuance, and serialization.
- Exact-before historical metadata loads and replays in current code. A newly
  issued v3 artifact cannot substitute for its recorded v2 identity. However,
  the retained authentic old concrete artifact input produces the finding below.

Temporary copies were `/tmp/uah-r4-primary.XfPHYA/current` and `before`, with
the latter overwritten by all five exact-before files. The pre-read control
used the isolated source and tests while resolving fixtures from the original
working directory. Subsequent comparative executions used the isolated working
directories too. No runtime file in the dirty tree was changed.

A full isolated-suite attempt stopped at collection because the minimal copy
did not include `scripts` (four import errors); it is not reported as a test
pass. The coordinating agent's full-suite results are separate evidence, not
independent isolated executions by this reviewer. For the review artifacts,
`git diff --check`, the generated-document renderer check, Ruff, and one
`./scripts/run_precommit.sh` execution passed. The existing initialized dev
toolchain was reused. Hooks updated `.git/precommit-success.json`; the four
frozen source/test hashes still match. No further hook run was started.

## Design principles

1. Separation of concerns: OK. Semantic admission, lease issuance, native
   dispatch and ledger replay remain distinct owners; no UI business logic was
   added.
2. Programming by intention: OK. The snapshot and explicit current wire reader
   express the intended authority contract. The consumer enforcement gap is
   classified under encapsulation below.
3. Encapsulation: violation at `src/ab_harness/domain_lifecycle.py:69` and
   `:287`. Current authority trusts the supplied old implementation's verifier
   rather than enforcing its own supported nested artifact contract. Finding 1.
4. High cohesion: OK. Snapshot identity and wire reconstruction stay with
   AdmittedOperation; environment execution consumes it without redefining
   object semantics.
5. Low coupling: OK. The delta adds no provider/runtime import and keeps the
   existing artifact identity boundaries instead of a shared generic hash API.

## Findings

### 1 of the 1 found so far. BLOCKING: authentic v2 objects retain active authority

Locations: `src/ab_harness/domain_lifecycle.py:287` (lease request),
`src/ab_harness/domain_lifecycle.py:69` (nested lease verification), and
`src/ab_harness/environment.py:123` (receipt issuance delegation). These
unchanged consumers do not enforce the new v3 contract at the crossing.

Input: execute the exact-before admission fixture in the isolated before copy;
retain its valid v2 artifact and historical ledger, truncating only the final
single-event lease commit so the history ends after semantic admission. Load
that history using current LifecycleLedger. Instantiate the old artifact using
the unmodified exact-before proposal-admission module loaded under a separate
module name, then pass it to current `DomainLifecycleAdmission.request_execution`.
This uses the actual old dataclass and verifier, not a forged duck-typed stub.

Expected: historical metadata remains readable, but active current leasing and
receipt issuance reject the v2 artifact because it has no frozen object snapshot.

Actual: current leasing issues a new execution lease. Current
`ExecutionReceipt.issue` accepts it, `start_execution` appends current execution
start and budget records, and `complete_execution` appends two receipt/evidence
events. Restart replays the resulting nine-event ledger. The alternative old
object's own verifier still considers v2 valid, and current consumers delegate
to it. Current `AdmittedOperation.from_dict(old_wire)` correctly rejects, so
the gap is the concrete artifact input, not the current wire reader.

Native-dispatch limit: current `InProcessEnvironmentOwner.execute` raises
`AttributeError: 'AdmittedOperation' object has no attribute 'object_snapshot'`
at `src/ab_harness/environment.py:485`, before execution start or the handler.
This finding does not demonstrate native live-catalog fallback or a native
side effect. It demonstrates new lease and evidence authority for an old
snapshot-free object outside any explicitly guaranteed type/version isolation.

The retained executable reproduction is
`docs/artifacts/reviews/2026-10-08_uah_r4_admitted_object_snapshot_evidence/r4_snapshot_primary_history_probe.py`.
Run its `generate` mode with the isolated exact-before source/test paths, then
`inspect` with current paths and the retained old source path. Both runs must
use their matching isolated working directory for fixture resolution. For
example, after preparing the two copies as above:

```bash
ROOT=/home/juanbeck/universal-agentic-harness
TMP=/tmp/uah-r4-primary.XfPHYA
PROBE=$ROOT/docs/artifacts/reviews/2026-10-08_uah_r4_admitted_object_snapshot_evidence/r4_snapshot_primary_history_probe.py
cd "$TMP/before"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$TMP/before/src:$TMP/before/tests" python "$PROBE" "$TMP/history-fresh" generate
cd "$TMP/current"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$TMP/current/src:$TMP/current/tests" python "$PROBE" "$TMP/history-fresh" inspect "$TMP/before/src/ab_harness/proposal_admission.py"
```

Enforce the current supported artifact type/version and snapshot at active
consumer boundaries. Keep legacy metadata replay separate from execution
authority. Retest the unchanged v3 path and this authentic old-type input.

## Limits

This is a bounded, source-and-execution review of the frozen R4 delta. No claim
is made about unexecuted combinations, real providers, native NAO dispatch,
in-flight cancellation, general concurrency, or whole-release qualification.
There are no new date, time-zone, unit, or numeric-threshold contracts in this
delta. The public proposal contract accepts one operation at a time; existing
multi-operation lifecycle tests provide controls, not exhaustive permutations.

VERDICT: CHANGES
