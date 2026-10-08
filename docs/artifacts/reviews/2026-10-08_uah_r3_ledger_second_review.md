# R3 ledger integrity: second independent review

Reviewed on 2026-10-08. Probes finished by 16:53 Europe/Madrid; report creation
finished at 16:54:36, approximately 36 seconds beyond the requested window.
Fresh reviewer, not the writer. Requested configuration: `gpt-6-astra`, `max`;
the serving backend is not independently observable from this review.

## Scope and provenance

Only the retained-before to current delta in `src/ab_harness/lifecycle.py` and
`tests/test_lifecycle_ledger.py` is approved here. HEAD remained
`28fab5e7f2c244d86a64c371f2118017999b2387`. SHA-256 values matched at entry and
again after execution:

| File | Current | Retained before |
| --- | --- | --- |
| lifecycle.py | `01a5523a438c6142385df8ffa241e225dfbb0394076082cbd609070c02503f81` | `df665eb4d8d5d815451ef99ab36145548813d0be0d5dfb5f3543b4825949b1f6` |
| test_lifecycle_ledger.py | `c604aca096056ea0e543792a80f041b9e4530ef6ff0c10bbc7cdd7aaab1bb68c` | `620bf209839a407a6ecfac40a7036a139583f45825c146a8943f483e50f23ce6` |

Before files are under `docs/artifacts/reviews/2026-10-08_uah_r3_ledger_integrity_evidence/`.
The comparison environment copied current `src` into a temporary directory and
replaced only lifecycle.py with its exact retained before file. Other ambient
dependencies were held constant, not reviewed or approved. No R3 writer
rationale, other reviewer output, or unrelated dirty diff informed this review.

The applicable contract was AGENTS.md, REVIEW.md, CONTEXT.md and the relevant
foundation, masterplan and Observatory sections, using the UAH guardrails.
The affected gate is H0/H1 lifecycle integrity. `LifecycleLedger` remains the
single write/replay owner; domain owners retain effect authority. This is not
H0/H1 exit, H2 qualification or live-provider evidence.

## Predeclared inputs and execution

Before reading source or the diff, I declared: mutation through events, record
returns and replay; nested model-budget mutation; admitted source and foreign
event mutation; serialization/data/reducer checks; identity canonicalization;
normal/durable/restart/competing-writer/atomic-commit/digest/O1 controls.
The initial export and foreign-consumer probes ran before implementation reading.
Remaining controls ran subsequently. An initial probe used nonexistent `.digest`
instead of `.verified_trace_digest`; it was corrected and both versions rerun.

Independent probe script: `/tmp/uah_r3_second_probe.py`. The before implementation
was `/tmp/uah-r3-second-7Y3U17/src`. Each invocation used
`PYTHONDONTWRITEBYTECODE=1`, the relevant `PYTHONPATH`, and `BEFORE_TEST` pointing
to the retained test file for its unchanged minimal ledger fixture.

| Input and expected result | Current | Before |
| --- | --- | --- |
| Change exported `task_id` via `object.__setattr__` through events, replay and record; retained ledger must stay identical | All three isolated | All three rewrite retained values |
| Mutate foreign `task_id`, `data_json` or `event_id`; data and serialization must reject stale identity | Six rejections with `trace event identity does not match content` | Six accepted |
| Mutate foreign replay data, then reduce | Identity rejection | Accepted |
| Restart a durable ordinary ledger | Events equivalent | Events equivalent |
| Reverse outer dictionary key order | Same identity | Same identity |
| Noncanonical data JSON, NaN, Infinity or array data, including recomputed outer identities | Rejected | Rejected |
| Duplicate start append | Rejected; file bytes unchanged and two prior events retained | Same |
| Mutated event type passed to raw O1 renderer | Identity rejection | Accepted |

The reducer probe called `_reduce_events` directly as a diagnostic, not a public
API claim. The minimal restart probe had no terminal digest; terminal digest
coverage instead came from the accepted and rejected lifecycle fixtures below.

Executed in both environments:

```text
.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_lifecycle_ledger.py tests/test_observatory.py \
  tests/test_two_stage_admission.py
```

Current: **98 passed**. Before: **86 passed, 12 failed**. Expected before failures
were three exported-reference mutations, six foreign event consumer mutations,
and three in-memory budget mutations. The budget input consumes the declared
three model calls, changes exported nested `model_calls` to 99, then assesses
and consumes a fourth call. Current remains exhausted at three; before grants
against 99 for events, commit and replay exports. Source-fact mutation and
durable cases remain safe in both versions. The suite also exercised stale
writers, competing execution owners, restart deduplication, incomplete commit
rejection, accepted/counterexample terminal digests and O1 ledger rendering.

```text
.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_agent_runtime.py tests/test_runtime_budget_contracts.py \
  tests/test_model_invocation.py
```

**48 passed in each environment**, including fake-provider invocation atomicity
and actor/runtime controls. No live provider was contacted. Total: current
146 passed; before 134 passed and the 12 targeted regressions failed.

## Standards and design principles

1. **Separation of concerns: OK.** Identity validation and export isolation stay
   in the existing lifecycle owner; no policy or evidence ownership moves.
2. **Programming by intention: OK.** `verify_identity()` names the check directly;
   standard dataclass replacement expresses detached validated exports.
3. **Encapsulation: OK.** Public exports no longer expose retained event objects.
   Their fields are immutable scalar values or tuples of strings; nested data
   is decoded afresh, so shallow event replacement suffices for this contract.
4. **High cohesion: OK.** The changes address one event-integrity boundary and
   reuse its existing identity payload. No second domain owner or duplicated
   identity algorithm was introduced.
5. **Low coupling: OK.** The implementation adds only a standard-library import;
   schema identities, domain ownership and provider-independent boundaries stay
   unchanged.

## Spec result, findings and limits

No BLOCKING or NIT findings in the scoped delta. The declared mutation and
reverification behavior is supported by differential execution, not only green
tests. Lock/reload/reduce/append ordering is unchanged.

An unchanged residual remains: mutate an exported event's `event_type` to
`terminal_task_accepted`, then call `project_observatory(events)` directly.
Both versions report `accepted`. This raw-iterable projection is not the
validated ledger path and is outside this repair's closure. Rendering that
collection now rejects its stale identity. Do not claim that every O1 entry
point validates arbitrary foreign event collections.

Content identity is not issuer authenticity. This patch does not redesign the
existing public fact API, authorize arbitrary correctly rehashed foreign facts,
or isolate hostile Python code with access to private state. No stress/performance
qualification or exhaustive crash injection was attempted. No setup scripts,
mutating hooks, Git mutations or implementation edits were performed. The next
separate discriminating probe is identity validation at raw O1 projection ingress.

VERDICT: APPROVE
