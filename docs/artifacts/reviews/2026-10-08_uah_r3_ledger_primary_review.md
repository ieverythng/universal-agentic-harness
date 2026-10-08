# R3 ledger integrity: independent primary review

## Probe declaration

Before execution, the bounded probe inputs are:

- Empty and populated memory/file ledgers. Mutate exported `events()`, returned commits, task replay, and agent-run replay via `object.__setattr__`; ledger state, digest, budget accounting, and restart results must remain unchanged.
- Fresh and stale `TraceEvent` identity; mutate `kind`, task/sequence lineage, and canonical nested budget data independently and in combination. Authority consumers must reject content that no longer matches its event identity.
- Finite task/model budgets at exhaustion; exported data must not grant extra authority.
- Terminal restart, digest and O1 projection parity; ordinary valid events must remain accepted.
- Two file writers and a rejected multi-event commit; sequence/replay must remain contiguous and no failed transition may append.

The reviewer opened the lifecycle diff while locating the exact before copies before writing this declaration. The probe families were supplied in the review brief before that read, but selection is not claimed to have been fully blind.

## Scope

Only `src/ab_harness/lifecycle.py` and `tests/test_lifecycle_ledger.py`, compared with exact `.before` copies under `docs/artifacts/reviews/2026-10-08_uah_r3_ledger_integrity_evidence/`. Frozen lifecycle hash: `01a5523a438c6142385df8ffa241e225dfbb0394076082cbd609070c02503f81`. Frozen test hash: `c604aca096056ea0e543792a80f041b9e4530ef6ff0c10bbc7cdd7aaab1bb68c`.

## Qualification and ordering

This report is a protocol-limited, non-qualifying review. The parent stopped this
review after the ordering deviation was disclosed and requested a fresh
replacement. No source fix is inferred from this report.

The first tool invocation read the UAH guardrails and code-review skills and
located the exact before copies. The second invocation read `REVIEW.md`,
`AGENTS.md`, and the first section of `CONTEXT.md`, checked both frozen hashes,
and printed the lifecycle delta. The probe declaration was written only after
that delta read. Later inspection read the test delta, relevant governing
documentation, and selected lifecycle source. No dynamic probe or pytest test
was executed before implementation inspection, or afterward.

The requested reviewer model/backend is not independently observable from
this review. No exact model/effort qualification is asserted.

## Findings

### BLOCKING: 1 of the 1 found so far. Independent-review ordering did not pass

Contract: `REVIEW.md:20` requires test inputs to be written before implementation
inspection and the changed behavior to be executed before reading it.

Reproduction input: the initial review commands included
`diff -u docs/artifacts/reviews/2026-10-08_uah_r3_ledger_integrity_evidence/lifecycle.py.before src/ab_harness/lifecycle.py`
before the probe declaration was saved.

Expected: declare inputs, execute those inputs against exact before and candidate
copies, then inspect implementation and explain the comparison.

Actual: the lifecycle delta was printed before the declaration, and no behavior
comparison was executed. The review cannot supply the independent primary gate.
The appropriate next action is a fresh review, not a code change justified by
this process failure.

## Design principles

The statuses below concern the inspected delta only. They are static observations
and do not constitute behavioral or release qualification.

1. Separation of concerns: OK. Event identity checking and lifecycle export
   isolation remain in the lifecycle owner. Observatory remains a read consumer.
2. Programming by intention: OK. `verify_identity()` and value replacement
   expose the intended validation and detached-export behavior.
3. Encapsulation: OK for the inspected implementation shape. Returned commit,
   event, task-replay, and agent-run event values are replaced before export.
   Resistance to mutation has not been independently executed here.
4. High cohesion: OK. The narrow identity/export changes remain within the
   existing lifecycle event and ledger abstractions.
5. Low coupling: OK. The delta adds only the standard-library `replace` import
   to production code. No provider/runtime dependency is introduced.

No domain gains a second owner, no business logic is added to templates or UI,
and no blocking duplicated domain logic was identified in this static delta.

## Evidence limits

The candidate differs from the exact before copy by revalidating trace-event
identity on data/serialization/reduction, and replacing exported event values.
The added tests cover ordinary export aliases, stale identity on data,
serialization and rendering, and nested model-call-budget mutation. This report
does not establish whether those tests pass on either tree.

Budget/model authority, restart/digest/O1 parity, agent-run mutation, competing
writers, and failed commits remain unexecuted by this reviewer. Direct raw
iterable O1 projection is unchanged by this delta; no new defect or successful
residual reproduction is asserted for that API.

The affected release boundary is the existing H0/H1 lifecycle spine and its O1
read consumers. `LifecycleLedger` remains the event/write/replay owner;
environment owners and deterministic gates retain execution/evidence authority.
No H0/H1 exit, H2, live-provider, or adaptive-promotion claim follows.

Both frozen hashes matched on initial inspection and again after the bounded
review inspection. No source, test, Git state, live service, or formatting hook
was changed or invoked. Only this report was written. The checks executed were
file discovery, governing-document/source/diff reads, and two SHA-256 checks.

VERDICT: CHANGES
