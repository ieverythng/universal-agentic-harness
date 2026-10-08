# R4-NESTED-OWNER: canonical nested fields and detached consumption

**Scoped gate closed 2026-10-08 at 18:20 Europe/Madrid: APPROVE.**

Start 2026-10-08 15:53:10 UTC (17:53:10 Europe/Madrid). Hard stop 16:23:10 UTC, source freeze target 16:05:10 UTC, review target 16:17:10 UTC. HEAD 28fab5e7f2c244d86a64c371f2118017999b2387. This is a separately authorized implementation round after R4-FIX closed CHANGES. The incomplete primary review's internal platform safety failure is not retried or claimed as a completed report.

## Pre-edit objective, scope and controls

SPEC-03 H0/H1 execution prerequisite only. The supported artifact owners must derive canonical nested data from actual concrete fields, never supplied instance serializers/verifiers, and use the same validated detached value for identity/provenance and effect consumption. AdmittedOperation owns proposal/snapshot identity, domain lifecycle owns leases, the environment owner owns native effects/evidence, and LifecycleLedger retains sole write/replay authority. No release closure claim, schema bump, module/process sandbox, generic codec/store/wrapper, provider/network/secrets or Git changes.

Potential scope is the four existing artifact-owner modules plus new tests/test_nested_admission_owner.py. Exact-before copies, complete dirty hashes/path inventory and protected controls are frozen before edits. R3 TraceEvent implementation/exports, O1 source/tests, dashboard, previous source-test fixtures, receipts and original probes are protected. Root owns canonical docs, examples, full hooks and fresh two-model reviews.

Agreed public seams: concrete artifact verification/serialization, current ledger semantic provenance, lease request/reuse, dispatch, receipt/evidence issuance and restart. Frozen attacks: actual proposal argument fields changed with a valid recomputed nested ID while its instance serializer misreports original bytes; no-op/misreport instance verifiers and serializers; missing/mutated snapshot and stale outer ID. Positive controls: untouched v3 wire and lease roundtrip, original proposal arguments in native handler, receipts and accepted restart, reviewed binding replacement, catalog pre/mid-handler drift, genuine old concrete rejection and all-marker read-only fencing. Native effects remain distinct from proven receipts and terminal acceptance. One own safe public red/control and minimal green slice at a time. Retained partial serializer script is source material, not executed review evidence. Stop for new policy/outside-scope dependency or budget, without an automatic extra round.

## Source freeze and owner repair

Source hash verification and announcement occurred at 16:04:47 UTC (18:04:47 Europe/Madrid), before the 16:05:10 target. The five files are frozen in [source_frozen.sha256](2026-10-08_uah_r4_nested_owner_evidence/source_frozen.sha256). Exact previous R4-FIX bytes are the four `.before` files; their hashes match [inputs.sha256](2026-10-08_uah_r4_nested_owner_evidence/inputs.sha256). [dirty_before.txt](2026-10-08_uah_r4_nested_owner_evidence/dirty_before.txt) and [dirty_before.sha256](2026-10-08_uah_r4_nested_owner_evidence/dirty_before.sha256) preserve the complete concurrent dirty tree inventory before edits. [source_delta.patch](2026-10-08_uah_r4_nested_owner_evidence/source_delta.patch) records this round's four-module delta, separately from earlier repairs.

Proposal and admission owner serializers now invoke the concrete owner implementation rather than supplied instance methods. Concrete `verified_copy` methods reconstruct the supported dataclass fields through their constructors. Execution lease reconstruction also detaches the nested admission, proposal and semantic snapshot. Dispatch validates a detached lease once and uses that detached authority for provenance, native arguments and subsequent evidence. Receipt/rejection issuance and ledger proposal/admission/lease fact conversion use the same owner-controlled reconstruction boundary. No schema version, shared codec, store, provider or ledger owner was added.

An intermediate issuance-time deep copy broke established alias-mutation controls: the supplied original admission no longer matched the returned lease's referenced object, so later mutation of that original stopped invalidating the lease. That intermediate state produced 17 failures and 108 passes (including an error-message assertion). Issuance-time reference compatibility was restored; detached reconstruction remains at actual consumption boundaries, and trusted owner serialization verifies actual nested fields at issuance. No existing tests were weakened or edited. The protected subset then passed. Fresh reviewers must assess this bounded ownership mechanism; this receipt does not claim isolation against module replacement, process-level mutation or arbitrary security attacks.

## Own public red and green evidence

The retained partial serializer script was read as mechanism source material and was not executed. The earlier incomplete primary review is not a completed review and was not retried. The new local tests use synthetic `cup`/`mug` arguments, real public artifact/ledger/environment seams and temporary workspaces. No providers, network, secrets or Git writes were used.

Three vertical slices produced the intended failures before their respective changes:

- `test_outer_identity_uses_actual_nested_fields_despite_instance_serializer`: a valid recomputed nested proposal ID plus a misleading instance serializer let stale outer admission identity verification return normally. Expected `ValueError` did not occur. [Red](2026-10-08_uah_r4_nested_owner_evidence/serializer_red.txt), [green](2026-10-08_uah_r4_nested_owner_evidence/serializer_green.txt).
- `test_dispatch_and_receipt_use_detached_authority_when_caller_fields_change`: the native handler changed the caller's original proposal arguments after dispatch. Shared caller fields invalidated receipt/failure recording. The repaired path performs one native call with the validated original `cup` arguments and retains that authority for the receipt. This probe records a native effect separately from receipt validation. [Red](2026-10-08_uah_r4_nested_owner_evidence/detached_dispatch_red.txt), [green](2026-10-08_uah_r4_nested_owner_evidence/detached_dispatch_green.txt).
- `test_proposal_record_ignores_instance_noop_verifier`: current ledger recording accepted changed actual proposal fields with a stale proposal ID when an instance verifier returned without checking. Expected `ValueError` did not occur. [Red](2026-10-08_uah_r4_nested_owner_evidence/ledger_record_red.txt), [green](2026-10-08_uah_r4_nested_owner_evidence/ledger_record_green.txt).

The final new file contains 25 cases, including serializer/verifier combinations at fresh lease, reused lease, dispatch, receipt, owner wire serialization and semantic provenance crossings; missing/mutated snapshots; valid concrete fields with misleading instance methods; exact ordinary wire/restart/receipt/acceptance controls. Invalid cases assert zero native calls, no ledger append and no invocation of supplied hooks. The test file reuses the existing public authority fixture and does not manufacture task-start authority.

## Executed validation

Commands used the repository virtual environment and disabled pytest cache/bytecode writes:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests .venv/bin/python -m pytest -q tests/test_nested_admission_owner.py -p no:cacheprovider
25 passed in 1.12s

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests .venv/bin/python -m pytest -q tests/test_nested_admission_owner.py tests/test_admitted_object_snapshot.py tests/test_admission_active_provenance.py tests/test_two_stage_admission.py tests/test_lifecycle_ledger.py -p no:cacheprovider
148 passed in 3.90s

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests .venv/bin/python -m pytest -q -p no:cacheprovider
504 passed in 10.96s

python -m ruff check src/ab_harness/proposal_admission.py src/ab_harness/domain_lifecycle.py src/ab_harness/environment.py src/ab_harness/lifecycle.py tests/test_nested_admission_owner.py
All checks passed

git diff --check
exit 0

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests .venv/bin/python docs/artifacts/reviews/2026-10-08_uah_r4_admitted_object_snapshot_evidence/second_review_probes.py current
exit 0
```

Logs: [new cases](2026-10-08_uah_r4_nested_owner_evidence/new_tests_final.txt), [focused](2026-10-08_uah_r4_nested_owner_evidence/focused_final.txt), [shared full suite](2026-10-08_uah_r4_nested_owner_evidence/full_shared_tree.txt), [unchanged original second-review controls](2026-10-08_uah_r4_nested_owner_evidence/original_second_review_controls.txt). The 504-test result describes the current shared dirty tree, including concurrent root-owned additions; it is not a clean-base result or an attribution of every test to this repair.

The unchanged original control probe retains valid execution, reviewed binding replacement, catalog drift before dispatch and during handler, missing/tampered wire rejection, all-marker active continuation rejection and genuine five-event metadata-only historical readability. Its `loaded` field describes the entire try-block, including attempted active continuation; it is not proof that historical read-only loading failed. Existing focused tests independently check historical loading and active fencing. Canonical document and O1 example checks also passed read-only; root owns full hooks and regeneration after source freeze.

The named uah-guardrails and uah-stack-iteration-loop skills constrained this to existing authority owners, explicit native-effect/evidence separation and a bounded source-specific gate. TDD, including its test/mocking references, required intended public red cases before the owner repairs. R3 TraceEvent and O1/dashboard code, old source tests, original receipts and probes remain protected. No source changes occurred after the freeze announcement; subsequent edits only record this evidence.

## Gate and limits at source freeze

Author validation is green for the bounded current concrete nested-field cases. Two fresh independent reviews and root's release checks remain pending. This round does not close SPEC-03 globally, certify H0/H1 release or establish a process sandbox. It does not upgrade historical metadata into active authority or fabricate semantic snapshot provenance. Issuance preserves prior alias behavior; consumption detaches and verifies supported concrete data. Hard stop remains 16:23:10 UTC. No further repair round is authorized by this receipt.

## Independent gate and integration

The [fresh primary](2026-10-08_uah_r4_nested_owner_primary_review.md) completes
at 18:17:05, and the [fresh second](2026-10-08_uah_r4_nested_owner_second_review.md)
at 18:19:43. Both return APPROVE, zero blocking and zero nit findings, and
report every REVIEW.md design principle. The second misses the soft 18:17:10
target but remains inside the hard 18:23:10 bound. No gate was removed.
Review configuration requested `gpt-6.1-sol/max` and `gpt-6-astra/max`;
independent backend identity is unavailable and is not attested.

Both reviewers declared and executed initial public controls before inspecting
the diff. Their isolated before/current trees share unaffected dependencies.
The primary retains 56 independent probes: current 56 pass, before 17 pass and
39 fail. An initial setup-counter issue is recorded rather than counted as
candidate behavior. The second retains 809 probes: current 809 pass, before
711 pass and 98 fail. Its missing historical-specimen setup was corrected
identically in both trees. These counts are observations, not distinct defects.
The reports retain current and historical authority controls, handler mutation,
receipt/replay agreement and the scoped limitations.

Root rechecks all five source/test hashes against the source-freeze manifest,
then confirms 504 shared-tree tests, all-files pre-commit, canonical-doc
synchronization, both O1 example checks and whitespace checks pass. O1's source
and test hashes remain unchanged. The current lifecycle diff leaves TraceEvent
construction, schema, identity and export contracts unchanged; its 39 focused
O1/example controls pass. The O1 correction has its own approval and receipt.

The reproduced nested serializer, stale supplied verifier and callback-settlement
mechanisms are closed within this frozen concrete-artifact scope. Original R4
and R4-FIX CHANGES receipts and the incomplete primary record remain untouched.
This is not a global SPEC-03 proof, H0/H1 exit, live-provider result, process
sandbox or complete O1 release. Raw-ingress producer provenance, shared static
prompt/admission eligibility, outgoing-cache coverage, O1 label conformance and
the remaining release evidence require their own gates. No source change after
freeze, failed-review retry, Git mutation or provider invocation occurred.
