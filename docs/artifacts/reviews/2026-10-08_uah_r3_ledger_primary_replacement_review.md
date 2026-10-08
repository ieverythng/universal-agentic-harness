# R3 lifecycle ledger integrity: independent primary replacement review

Date: 2026-10-08. Requested review window: 16:50–16:55 Europe/Madrid.
The initial clock read was 16:50:17. Runtime probes finished before 16:55;
the saved-report confirmation and final hash check occurred at 16:55:32,
32 seconds after the requested cutoff. No further runtime probes followed.

## Scope and independence

I did not write this change and did not inspect writer receipts, research notes,
or other review reports. The review compares only `src/ab_harness/lifecycle.py`
and `tests/test_lifecycle_ledger.py` with the exact same-basename `.before`
files in `2026-10-08_uah_r3_ledger_integrity_evidence/`. The supplied repository
anchor is `28fab5e`; no Git mutation or source modification was performed.

The dispatch requested `gpt-6.1-sol` at `max`. No fallback was attempted.
The child session has no independent scheduling-metadata readout.

The affected gate is the H0/H1 lifecycle integrity seam. `LifecycleLedger`
remains the event, persistence, and replay owner. Domain owners retain execution
and evidence authority. This review does not qualify H0/H1 exit or H2 parity.

## Execute-before-read inputs

Before reading implementation or either before copy, I declared: empty memory
and file ledgers; normal task/agent flows; `events()`, `record()` return, and
replay exports with changed event kind and nested budgets; stale identities;
altered source artifacts; budget exhaustion; restart/digest/O1 equivalence;
and competing writers with atomic commits.

The first public control constructed an empty ledger and observed `events() ==
()`. An attempted `digest()` call raised `AttributeError` because that public
method does not exist. A separate temporary file-ledger control also returned
empty events. Missing-trace replay raised `KeyError`, not the `ValueError` my
initial exception handler expected. These were probe mistakes, not findings.

## Executed evidence

- HEAD: `PYTHONPATH=src:tests python -m pytest -q` with
  `tests/test_lifecycle_ledger.py`, `tests/test_model_invocation.py`,
  `tests/test_observatory.py`, `tests/test_runtime_budget_contracts.py`,
  `tests/test_two_stage_admission.py`, and `tests/test_agent_runtime.py`:
  **146 passed**. Coverage includes accepted/deficit/rejected trace digests,
  restart reconstruction, O1, stale writers, incomplete multi-event commits,
  invocation grant/start atomicity, and rejected-commit rollback.
- BEFORE: copied the current portable package into
  `/tmp/uah-r3-primary-before.3WqhmK/`, replaced only its lifecycle module with
  the exact before copy, and ran the same six files using
  `PYTHONPATH=/tmp/uah-r3-primary-before.3WqhmK:src:tests`,
  `-o pythonpath=/tmp/uah-r3-primary-before.3WqhmK`, and
  `-p no:cacheprovider --tb=no`: **134 passed, 12 failed**. The failures were
  the three export-alias attacks, six foreign-event identity attacks, and
  three in-memory exported-budget attacks. The original before ledger test
  file was separately copied into that temporary directory and executed:
  **10 passed**.
- Independent public probes changed `event_type` to
  `terminal_task_accepted` through each of `events()`, replay events, and
  commit events. BEFORE changed ledger content and ledger-backed O1 to
  `accepted`; HEAD preserved ledger content and O1 `open`. HEAD rejected the
  detached stale event at `data`, `to_dict()`, and `render_observatory()` with
  `ValueError: trace event identity does not match content`. BEFORE accepted
  each access.
- Independent nested-budget probes changed `budgets.model_calls` from 3 to
  99 before consumption. BEFORE granted the fourth call at limit 99 through
  all three event-export origins; HEAD exhausted at limit 3 with consumption
  3. Mutating the original compiled artifact after recording left authority
  at 3 in both versions. HEAD also exhausted after three prior grants for
  all four origins. On BEFORE, mutation after prior grants instead produced
  a budget-limit replay mismatch, so that case is not evidence of a fourth
  granted call.
- Recording an altered compiled source artifact with its stale identity
  rejected on HEAD with `compiled task identity does not match content` and
  appended nothing. The targeted suite also exercises proposal identity and
  foreign receipt lineage rejection.
- HEAD: eight independent task starts through four competing processes into
  one temporary JSONL ledger all completed; restart returned contiguous
  sequences 1 through 8. An agent-run replay event mutated to termination
  did not change the authoritative ledger.

Two preliminary pytest attempts named nonexistent control/replay files and
ran no tests. A first before invocation used an unsuitable `/dev/null`
configuration, and another lacked the NAO adapter import path; neither
completed collection. The corrected comparisons above completed. The initial
actor probe treated a fixture's tuple return as a ledger; the corrected probe
passed.

## Findings and limits

No BLOCKING or NIT finding was established in the frozen delta.

`project_observatory((detached_forged_terminal_event,))` still reports `accepted`
on both versions when the caller changes only the event kind while retaining
its stale content ID. Rendering that iterable now rejects it. The direct raw
iterable projection is unchanged, outside the covered ledger-backed authority
boundary, and remains an explicit gap. This approval must not be described as
closure of every O1 input path.

The before comparison is a one-module overlay on the current dependency tree,
not a reconstruction of the complete historical repository. The process race
and corrected actor-export probe ran only on HEAD. Existing atomicity tests
ran on both versions; no crash-injection stress campaign was performed.
No providers, hooks, or broad release qualification were run.

## Five design principles

1. Separation of concerns: OK. Ledger exports and event identity checks stay
   with the lifecycle owner; Observatory remains a consumer.
2. Programming by intention: OK. `verify_identity()` names the trust check
   explicitly (`lifecycle.py:164`).
3. Encapsulation: OK. Defensive copies cover commits, event enumeration,
   trace replay, and agent-run replay (`lifecycle.py:635`, `:707`, `:769`,
   `:780`). Public nested data is decoded independently.
4. High cohesion: OK. One event identity check is reused for initialization,
   public decoding/serialization, and reduction (`lifecycle.py:1533`).
5. Low coupling: OK. No SDK/runtime dependencies or second authority owner
   are introduced. Standard-library `dataclasses.replace` implements copying.

## Frozen hashes

HEAD hashes matched before and after execution:

- lifecycle: `01a5523a438c6142385df8ffa241e225dfbb0394076082cbd609070c02503f81`
- ledger tests: `c604aca096056ea0e543792a80f041b9e4530ef6ff0c10bbc7cdd7aaab1bb68c`

Before-file hashes:

- lifecycle: `df665eb4d8d5d815451ef99ab36145548813d0be0d5dfb5f3543b4825949b1f6`
- ledger tests: `620bf209839a407a6ecfac40a7036a139583f45825c146a8943f483e50f23ce6`

VERDICT: APPROVE
