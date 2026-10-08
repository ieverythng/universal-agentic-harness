# Independent O1 raw-event identity review

Review started 2026-10-08 at 17:33 Europe/Madrid. Requested reviewer configuration: `gpt-6.1-sol` / `max`; the backend model and reasoning setting are not observable from this reviewer runtime, so that exact pair is not independently confirmed.

## Scope and predeclared inputs

This is a fresh independent review of the O1 raw-event identity gate only. The reviewer did not write the fix and will not read the writer receipt, rationale, or other reviewers. ARCH-02 provenance labels, causal validation, concurrent R4-FIX changes, and release qualification are outside the verdict. The affected boundary is the bounded O1 read-only projection alongside H0/H1; `TraceEvent` owns canonical identity and Observatory owns projection admission without acquiring execution authority.

Before reading implementation or diff, I predeclared these probes:

1. Run the existing public `tests/test_observatory.py` against an isolated snapshot of current dependencies.
2. Submit a genuine event whose event kind has been modified while its original ID is retained, through a tuple and a generator. Expect rejection before any projected status or grouping.
3. Modify genuine event replay content, task/trace grouping lineage, actor lineage, and environment lineage while retaining IDs. Expect identity rejection, with no rendered forged record.
4. Submit valid raw illustrative incomplete events, an empty input, one event, multiple events in normal and reversed order, and an ordinary ledger. Expect preservation of existing successful behavior and explicit unknown/incomplete states where applicable.
5. Combine a valid event with a stale event in both orders. Expect whole-projection rejection, not a partial result.
6. Submit non-event input and duplicate valid events. Expect existing type and duplicate behavior to remain consistent; identity failures must not bypass those contracts.
7. Feed successful projections to JSON, Markdown, HTML, search, actor/environment grouping, and terminal-status consumers. Expect consumers to agree with admitted event identities.

The comparison baseline is an isolated copy of the same current dependencies with only the exact retained `observatory.py.before` overlaid. The retained original test file is separately checked. This is not a complete historical baseline: the root did not capture a complete shared-tree manifest until after the edit freeze, and only the two exact before files are retained.

## Execution evidence

Completed at 17:38 Europe/Madrid, before the 17:41 probe/report deadline. `REVIEW.md` was read first. The input list above was saved before implementation or diff inspection. The existing public control was then executed before reading the implementation. No writer receipt, rationale, or other review was read.

The code-review skill's Standards and Spec axes are reported separately. Its additional-agent workflow was not used because this assignment requires one independent reviewer. The UAH guardrails limited the assessment to the common event owner and read-only O1 projection. No source, hook, Git state, or provider configuration was edited.

### Frozen bytes and comparison

| File | SHA-256 |
| --- | --- |
| Current `src/ab_harness/observatory.py` | `aec50ca2e77d5c5bbe187ae08e6700797dee28bf7a703ac35f593de884ecb878` |
| Current `tests/test_observatory_raw_identity.py` | `02e90f519120ebfe7d785954606a24bc8d286c5e6ff01b9f09a1ad3211e236d1` |
| Exact-before `observatory.py.before` | `bb3d2b359fec4adeb15619abee12b86bc20734548cccfd3929ab17f9ce7cfcd0` |
| Exact-before and current original `test_observatory.py` | `491e95bf7305d0c50179bd5cf1ef94aaf87aa03994142b4b22d804815406cf92` |

The package was copied into `/tmp/uah-o1-primary-review.gbpU6d/src`. The comparison package at `/tmp/uah-o1-primary-before.gbpU6d/src` is a copy of those dependencies with only the exact-before Observatory module overlaid. Its original public test is the retained exact-before test, which has the same bytes as the current original test. Thus the executable comparison changes only Observatory source behavior, not its package dependencies.

The copied `lifecycle.py` hash is `361c902defafc0e8273eb5d40c3d329111fd60647f7884cbdc62dcb88dc28a9f`. At 17:36:58 the shared file had become `b35641d97b8d915df358e880de73400386395e8b3525a41cae99e329b04176ee` during concurrent R4-FIX work. The frozen Observatory module and new test still matched the requested hashes. All probes used the copied package, not that changing shared source. This is a dependency snapshot, not a claim to have captured the complete historical tree atomically. Public test helpers and the recorded-canary script were imported from the shared repository; their full historical manifest is unavailable.

### Executed checks

1. Initial control: `PYTHONPATH=/tmp/uah-o1-primary-review.gbpU6d/src python -m pytest /tmp/uah-o1-primary-review.gbpU6d/tests/test_observatory.py -q`: **23 passed**, executed before source/diff inspection.
2. Exact-before overlay control: the corresponding original test command with `/tmp/uah-o1-primary-before.gbpU6d`: **23 passed**.
3. Current original and new identity test files together: **31 passed**.
4. The new identity test file against the exact-before overlay: **6 failed, 2 passed**. All six failures were missing stale-ID rejection; they were not infrastructure failures.
5. `/tmp/uah-o1-primary-review.gbpU6d/probe_identity.py`, run separately with each package on `PYTHONPATH`: **54 observed outcomes per version**. This independent script supplements, rather than replaces, the assertions in the public suite. Its final SHA-256 is `ef1b366361a1021a8183ff1747fc3af36f2d25102dedd2f53020e0838ff563f5`.
6. After writing this report, `python scripts/render_agentic_harness_docs.py --check` passed (12 metadata records checked), and `git diff --check -- docs/artifacts/reviews/2026-10-08_uah_o1_raw_identity_primary_review.md` exited successfully. The latter does not validate untracked-file whitespace; the Markdown report was also inspected directly.

The independent stale-field matrix used a genuine ledger-created v1 task-start event, retained its ID, and individually altered `event_type`, `environment_run_id`, `task_id`, `trace_id`, `data_json`, `recorded_at`, `sequence`, `artifact_refs`, `parent_event_id`, `operation_id`, `commit_id`, `commit_index`, `commit_size`, and `schema_version`. Each was submitted as a tuple and generator. Current code rejected all 28 inputs with `ValueError: trace event identity does not match content`; the before overlay admitted them. A forged terminal kind produced `accepted` under the before overlay and was rejected by current code.

Valid-plus-stale collections in both orders were wholly rejected by current code. A sentinel patched into `_project_trace` confirmed rejection before status projection: current returned the identity error, whereas before reached the sentinel. An invalid non-event retained the existing `TypeError`; duplicate valid IDs retained the uniqueness error. A collection containing both a stale event and a non-event retained type-check precedence. Duplicate stale events now fail the identity check before uniqueness. No new error code was added.

Empty, genuine one-event raw, ordinary ledger, valid illustrative incomplete, multiple-event, and reversed multiple-event controls agreed between versions. Incomplete raw events remained open; no causal completeness or ledger membership was required. Genuine v2 actor mutations of actor ID, environment ID, scope, and content were rejected by current code and admitted by the before overlay. Valid actor events remained visible without an invented task.

Rendering checks exercised the public HTML document and graph JSON, event IDs, actor/environment hierarchy, open-status attributes, and static search/event-filter attributes. Valid consumers agreed. Stale canonical-content rendering already failed under the before overlay through downstream identity-aware serialization and still fails now, earlier at projection admission. The script did not execute browser JavaScript. There is no separate public Markdown rendering API in this seam.

Date mutations included a leap-day timestamp with an explicit offset. The changed gate compares canonical content; it does not introduce calendar, duration, unit, threshold, or upper-bound policy.

## Standards

The change is two lines, calls the event owner's existing public verifier, and introduces no duplicated canonicalization, platform dependencies, write authority, or speculative abstraction. The reviewed standards were root `AGENTS.md`, `CONTEXT.md`, the Observatory contract, relevant O1 masterplan sections, the development log's current qualification boundary, and `REVIEW.md`.

| Principle | Result |
| --- | --- |
| Separation of concerns | **OK**. Observatory requests verification from `TraceEvent`; it remains a projection and renderer. |
| Programming by intention | **OK** for the added call. Its placement makes identity admission precede ordering and status derivation. |
| Encapsulation | **Violation**, Finding 1 at `src/ab_harness/observatory.py:242` and `src/ab_harness/lifecycle.py:164`: the delegated predicate permits mutated v1 scope/actor representation that the projection then consumes. |
| High cohesion | **OK**. The added admission step belongs to the existing raw-input boundary. |
| Low coupling | **OK**. No private canonicalization or second event owner was introduced. |

## Spec

The canonical-content-ID residual is repaired for the tested covered fields, including status, task/environment grouping, and genuine v2 actor lineage. Valid raw illustrative inputs and validated-ledger controls remain compatible. No introduced functional regression was found in those controls.

The broader raw representation-integrity gate remains incomplete for v1 actor/scope fields. The existing `TraceEvent` constructor rejects a v1 actor or non-task scope (`lifecycle.py:108`), while its later identity verifier ignores those two fields for v1 (`lifecycle.py:190`). Observatory consumes them after that verifier (`observatory.py:251`). This is directly within identity before actor/status grouping; it is not ARCH-02 provenance-label review, causal validation, or an authority-ownership allegation.

## Findings

### BLOCKING: 1 of the 1 found so far. V1 actor/scope mutation bypasses the raw identity gate

Location: `src/ab_harness/observatory.py:242`, with consumption at lines 251 and 253. Owner-predicate context: copied `src/ab_harness/lifecycle.py:164`, 190. These dependency line numbers refer to the stated snapshot, not an assertion that concurrent R4-FIX kept the same lines.

Input: a genuine ledger-created v1 `task_started` event. Change only its in-memory `agent_run_id` or `event_scope` using the same frozen-object mutation mechanism as the supplied stale-ID tests. Retain its original event ID. The independent probe uses this event:

```python
ledger = LifecycleLedger(clock=lambda: "2026-10-08T15:30:00Z")
ledger.record(TaskStartedFact(
    environment_run_id="environment-run:primary", task_id="task:primary",
    trace_id="trace:primary", environment_ingress_id="ingress:primary",
    ingress_artifact_id="artifact:primary", decision_id="decision:primary",
    domain_contract_pack_revision="domain:primary",
))
event = ledger.events()[0]
object.__setattr__(event, "agent_run_id", "agent-run:forged")
event.verify_identity()  # returns successfully
projection = project_observatory((event,))
document = render_observatory((event,))
```

Expected: reject the invalid v1 representation before actor grouping, with no projection or document. V1 events require task scope and no actor, and changing these fields must not create alternate views over the same event identity.

Actual, current and exact-before overlay: the verifier succeeds, the original ID `trace-event:sha256:d86088b879ec00e73b84827051a661e3bab135da7c81cfe2d4e2da05b76eac0e` remains unchanged, and `projection.agent_runs` contains `agent-run:forged`. The HTML has an actor card and graph JSON records that actor. The v1 raw serialized event does not contain that actor field, so raw serialization and actor/graph views disagree about the same identity.

A second variant from a fresh genuine event sets `event_scope="agent"`. Both versions again verify and return successfully, but the task trace disappears: `projection.trace_ids == ()`, while graph JSON still records the original task/trace identities. These variants are one missing v1 representation-invariant check, not two unrelated findings.

This is a **pre-existing incomplete gate**, not a regression introduced by the two-line patch. The supplied gate now rechecks covered canonical content but does not enforce the v1 constructor's already-established scope/actor invariant at this crossing. Repair should remain with the event owner's invariant predicate and preserve historical v1 serialized identities. No source repair was made by this reviewer.

## Limits and handoff

There are no NIT findings. The tested canonical-ID attack is blocked, but Finding 1 prevents claiming that raw event identity integrity is closed before every actor/status grouping path. This verdict neither qualifies H0/H1 exit nor changes ARCH-02 status. Full repository hooks were not run by this independent reviewer against the concurrently changing shared tree; the parent must run the final documentation and hook checks and separately freeze any repair. The next discriminating probe is a fresh v1 task event with each nonserialized scope/actor field mutated, plus an unchanged-v1 control after an owner-local fix.

VERDICT: CHANGES
