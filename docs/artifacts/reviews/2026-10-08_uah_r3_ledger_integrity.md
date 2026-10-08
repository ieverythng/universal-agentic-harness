# UAH R3 ledger integrity: pre-edit freeze

Date: 2026-10-08. Start: 14:40:16 UTC (16:40:16 Europe/Madrid). Stop target: 15:00 UTC; implementation freeze target 14:48 UTC. HEAD: `28fab5e7f2c244d86a64c371f2118017999b2387`.

## Locked objective and scope

Repair STD-03 / SPEC-04 stale-content identity and returned-event aliasing through the public lifecycle ledger. Preserve existing TraceEvent identity, event wire schemas, ledger write/replay ownership, replay prerequisites, budget authority, durable competing-writer and commit semantics, read-only O1 and terminal digest. No new admission semantics or owner authority.

Owned implementation: `src/ab_harness/lifecycle.py`, `tests/test_lifecycle_ledger.py`. Owned evidence: this receipt and the `2026-10-08_uah_r3_ledger_integrity_evidence/` directory. Canonical documents, dashboard, existing review probes and all other dirty files remain outside ownership. No Git mutation or provider calls; no formatting hooks during parallel dashboard review. Root runs final hook suite.

Before inputs: lifecycle `df665eb4d8d5d815451ef99ab36145548813d0be0d5dfb5f3543b4825949b1f6`; tests `620bf209839a407a6ecfac40a7036a139583f45825c146a8943f483e50f23ce6`. Exact pre-edit copies and complete dirty-file SHA-256 manifest are retained alongside this receipt. Concurrent root-owned synthetic-notes plan is included if present in that snapshot; other changes remain concurrent work, not reset.

## Frozen acceptance

Train: public stale-ID event-kind mutation, returned committed/replayed event alias, and budget-payload mutation must not change ledger authority. The saved original STD-03 probe is retained without modification. Implement one actual red at a time. Holdout: valid in-memory and restarted file-backed traces; stale writers; atomic multi-event commits; O1 read-only outputs; terminal digest; foreign mutated event serialization/rendering. Relevant existing tests and read-only lint/docs checks must pass. No claim of runtime release qualification. Stop if the red requires a new schema or normative owner choice. Independent reviews belong to root after frozen implementation hashes.

## Implementation freeze and observed delta

Frozen at 14:47:13 UTC (16:47:13 Europe/Madrid), before the 14:48 UTC review-dispatch target.

- `src/ab_harness/lifecycle.py`: `01a5523a438c6142385df8ffa241e225dfbb0394076082cbd609070c02503f81`.
- `tests/test_lifecycle_ledger.py`: `c604aca096056ea0e543792a80f041b9e4530ef6ff0c10bbc7cdd7aaab1bb68c`.

The scoped delta is retained separately from the much larger pre-existing Git diff. The ledger exports newly constructed TraceEvent values from record, events, replay and agent-run replay. Construction uses the existing canonical identity validator. TraceEvent data and serialization revalidate canonical identity; the existing reducer loop revalidates each event before applying it. No additional whole-ledger traversal, new schema, codec, store, admission rule or policy owner was introduced. Export construction has linear cost in the exported event collection and hashes each exported event. No performance benchmark was run.

## Actual red and repair chronology

The initial six tests failed before implementation: mutations through events, replay and commit corrupted ledger replay; stale event-kind content passed data, serialization and foreign rendering. The initial budget test used a nonexistent request method and failed with AttributeError. That was a test setup error, not an intended red. It was corrected to the actual public assess/consume interface.

The budget matrix was added after the initial isolation repair. A fresh-process baseline package was then reconstructed from the exact before copy, with the ordinary package initialization and remaining source modules. This post-repair baseline replay is not claimed as a withheld pre-edit run. Its final result was 12 intended failures and five passing controls. Three in-memory budget assessments returned granted with limit 99 after a stale-ID payload mutation instead of exhausted with limit 3. File-backed reload and source-fact mutation controls already passed before repair. The baseline output is preserved in baseline_red.log. An earlier same-process module replacement produced class-identity setup failures and was discarded as invalid evidence.

The new tests exercise public authority seams with existing real compiled-task fixtures. No provider invocation or native execution is involved. Ordinary source-fact budgets were already isolated by serialized event data; the fix does not claim a newly repaired source-fact alias.

## Validation

- `.venv/bin/python -m pytest -q tests/test_lifecycle_ledger.py`: 27 passed.
- `.venv/bin/python -m pytest -q tests`: 388 passed in 5.19 seconds.
- `.venv/bin/ruff check src/ab_harness/lifecycle.py tests/test_lifecycle_ledger.py`: passed.
- `git diff --check -- src/ab_harness/lifecycle.py tests/test_lifecycle_ledger.py`: passed.
- `.venv/bin/python scripts/render_agentic_harness_docs.py --check`: passed, 12 metadata records.
- `.venv/bin/python scripts/render_observatory_example.py --check`: passed.
- `.venv/bin/python scripts/render_agent_runtime_example.py --check`: passed.
- Saved STD-03 probe `2026-10-05_uah_review_repros/standards_event_tamper.py`: unchanged hash `1a6ffbed7040250ca0a9a0b42fee8f82e27644c5b379ecafe0f2614eac064882`; now displayed_status open with unchanged event identity.
- Read-only Ruff format check reports pre-existing formatting differences only (four lifecycle regions and the pre-existing stale-writer assertion). These were preserved; no formatting hook was run. Root owns the full hook run after parallel frozen dashboard review.

## Explicit residual and gate status

`project_observatory(iterable)` can still classify a foreign stale-ID mutated event as accepted before payload inspection. The executable mutation/control probe `raw_iterable_o1_residual.py` retains ID R3-O1-RAW-ITERABLE-IDENTITY. Valid raw control and ledger-origin projection remain open; foreign render rejects the mutated identity. This residual concerns raw iterable identity validation, independently of ARCH-02 provenance labels. Root confirmed that observatory.py remains outside this round. No claim that every foreign-event O1 entry point is repaired.

The sole writable ledger boundary, sequence conflict, competing writers, commit positions, disk reload, terminal replay and digest remain covered by the passing existing suite and synchronized O1 examples. No evidence of live-provider or release qualification is asserted. Independent Standards and Spec reviews remain pending at author handoff. R2 owner-choice/admission work remains separate and unchanged.

## Independent gate and round close

Closed at 16:56 Europe/Madrid, within the 17:00 round target. The fresh
[replacement primary](2026-10-08_uah_r3_ledger_primary_replacement_review.md)
and [distinct-model second](2026-10-08_uah_r3_ledger_second_review.md)
return APPROVE, zero scoped findings. Both execute 146 current tests and an
exact-before overlay with 134 passes and 12 expected mutation failures.
Source/test hashes match the implementation freeze. Their report-confirmation
overruns are recorded, not hidden as within-cutoff execution.

The [initial primary report](2026-10-08_uah_r3_ledger_primary_review.md) is
non-qualifying because it read the delta before declaring and executing probes.
Its CHANGES verdict concerns review ordering, not an inferred code defect.
It is retained and excluded from the qualifying two-review gate.

Root ran `./scripts/run_precommit.sh`: all hooks passed. Current reviewed
runtime bytes were unchanged afterward. This closes the reproduced ledger
export alias and stale-content consumer mechanisms under STD-03/SPEC-04,
not every O1 projection input or H0/H1 release gate. The raw-iterable projection
counterexample remains open and requires a separate frozen correction.
No Git state or live provider was changed. Other bounded dashboard and research
work is concurrent and supplies no runtime approval.
