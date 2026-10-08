# O1 conformance fix independent second review

## Declared inputs before implementation or diff inspection

Review contract read first. This fresh reviewer did not author the repair.
Requested review backend: `gpt-6-astra` with `max` reasoning; actual backend
identity is not observable from the tool API.

Independent initial public control: an incomplete but valid v1 terminal event
through both `project_observatory` and `render_observatory`, as tuple and
generator. Expected: accepted status and synthetic label, without causal replay
requirements. Negative forms: the same event with only actor identity changed,
only scope changed, or both changed after construction. Expected: rejection
before grouping or rendering.

Additional inputs chosen before source inspection: valid v1 task, v2 actor and
v2 task events alone and mixed in both orders; covered event fields changed with
stale identity; original input mutated after projection; invalid member type,
duplicate event, unsupported schema and event type; empty input; synthetic and
conceptual illustration labels; read-only validated ledger rendering.

Compare current bytes with retained exact-before Observatory bytes while using
identical lifecycle and other dependencies. Do not add causal, freshness, or
provenance-label requirements. ARCH-02 is outside this repair.

Mandatory UAH guardrail reading included the owning Observatory contract. It
contains a short repair-status paragraph; that incidental exposure is disclosed.
No writer receipt, other review report, or writer test result was read. The
original public Observatory tests were inspected only for public fixture syntax.

Both code-review axes (standards and spec) are assessed locally because all four
agent slots were occupied. Review work does not run hooks or change source.

## Execution and result

The initial controls executed at 17:51 Madrid, before reading the implementation
or its diff. The current code rejected all actor-only, scope-only, and combined
v1 mutations through both public APIs and both iterable forms. Exact-before
code accepted the mutations. The initial observation helper indexed the first
trace after the old implementation hid it and therefore emitted a helper
`IndexError`; a subsequent direct observation confirmed acceptance with an empty
trace collection, not application rejection.

The fixed point is the retained exact-before file, not Git HEAD. Both isolated
source trees used the same copied dependencies and the retained lifecycle file.
A recursive comparison excluding bytecode caches found only `observatory.py`
different between those trees.

| Reviewed bytes | SHA-256 |
| --- | --- |
| Current `src/ab_harness/observatory.py` | `313798f6e660f913622695dd8c19d52c0ab269c71dbc6eab1e6a5472d26236fe` |
| Exact-before `observatory.py.before` | `aec50ca2e77d5c5bbe187ae08e6700797dee28bf7a703ac35f593de884ecb878` |
| Current `tests/test_observatory_raw_identity.py` | `d20059458b6fe87e1e7ac8bdf0a7307aed2f26d71244009e22c861a3e6bc3b2a` |
| Shared exact lifecycle dependency | `b35641d97b8d915df358e880de73400386395e8b3525a41cae99e329b04176ee` |

The independent executable is
[second probe](2026-10-08_uah_o1_conformance_fix_second_probe.py).
Its complete observations are retained as
[current results](2026-10-08_uah_o1_conformance_fix_second_current_results.json)
and [exact-before results](2026-10-08_uah_o1_conformance_fix_second_before_results.json).
Each execution produced 138 observations: 33 cases crossed with two public APIs
and tuple/generator forms, four illustration-label controls, one input-alias
control, and one file-backed ledger control.

| Input and expected result | Exact-before actual | Current actual |
| --- | --- | --- |
| Empty input, valid v1 task, v2 actor/task, mixed v1/v2 histories in both orders: accept with explicit membership only | 24 accepted combinations | Same 24 combinations accepted; identities and ordering preserved |
| Mutate v1 `agent_run_id` to `actor:forged`, `event_scope` to `agent`, or both: reject before membership/status/rendering | All 12 combinations accepted; actor-only invents membership, scope-only hides the trace, combined does both | All 12 rejected with `v1 events require task scope without actor identity` |
| Unsupported schema, noncanonical/object-invalid JSON, mutable reference list, invalid v2 actor/scope/task shape, including rehashed forms: reject | Multiple invalid forms accepted; missing v2 trace also reaches a rendering `TypeError` | Rejected by existing owner-constructor checks |
| Change any of 13 covered fields without updating identity: reject | All rejected | All rejected; invalid commit position is rejected before the hash check |
| Foreign member or duplicate identity: reject | Rejected | Rejected |
| Mutate source actor, event type, and environment after projection/rendering: retained document/projection must not change | Both projections retained caller aliases | Both detached; trace/global event views share the same owned copy |
| Incomplete terminal illustration, synthetic/conceptual labels: accept and preserve labels without causal replay | All four accepted with requested labels | Same results |
| Render a file-backed ledger: preserve file bytes, event values, and recorded label | All preserved | All preserved |

The current matrix has 24 accepted and 108 rejected input/API/form combinations,
with all six additional controls meeting expectations. Exact-before has 66
accepted and 66 rejected combinations and fails both alias-detachment checks.
These are observed behavior comparisons, not evidence of causal validity or
provenance qualification.

Additional public controls used freshly identified event types
`external_extension_event` and `task_failed_without_terminal_fact`. Both
implementations rendered them as open and included their identities. The owner
does not enumerate event-type strings; this repair correctly adds no new event
vocabulary policy and infers no terminal status from an unfamiliar name.

Executed focused suites with `PYTHONPATH` and pytest's `pythonpath` override
pointing to the isolated source tree:

```text
current source + current tests/test_observatory.py and raw-identity tests:
37 passed in 0.29s
exact-before source + the same current tests:
33 passed, 4 failed in 0.31s
current source + original Observatory tests and retained exact-before raw tests:
31 passed in 0.39s
exact-before source + those same retained tests:
31 passed in 0.38s
```

The four expected exact-before failures are actor-only mutation, scope mutation
with each actor alternative, and post-projection input aliasing. The initial
public controls and independent matrix establish these behaviors separately
from the writer's regression tests.

For reproduction, the isolated trees are
`/tmp/uah-o1-second-24bZch/current` and
`/tmp/uah-o1-second-24bZch/before`. The latter replaces only Observatory with
`2026-10-08_uah_o1_conformance_fix_evidence/observatory.py.before`; both use the
same retained `lifecycle.py.before`. Run the independent probe with the chosen
tree first in `PYTHONPATH`, followed by this repository root.

## Standards

No BLOCKING or NIT finding in the reviewed repair.

1. Separation of concerns: OK. `src/ab_harness/observatory.py:242` reconstructs
   through the existing `TraceEvent` owner before sorting or deriving views;
   versioned validation remains in `src/ab_harness/lifecycle.py:105`.
2. Programming by intention: OK. One direct constructor call expresses the
   boundary's validated, detached value rather than adding a second validator.
3. Encapsulation: OK. The alias controls confirm the projection no longer
   retains caller-owned events. No ledger internal state or write API is used.
4. High cohesion: OK. The change is confined to raw-event intake and directly
   related public tests. No renderer policy or unrelated lifecycle rule changed.
5. Low coupling: OK. Dependencies remain the existing portable lifecycle owner
   and standard-library dataclass conversion. No provider, ROS, or runtime
   product dependency was introduced.

## Spec

No BLOCKING or NIT finding in the reviewed repair. Existing v1/v2 constructor
conformance and identity checks occur before ordering, grouping, status, graph
generation, or HTML rendering. Valid historical and mixed inputs remain
readable, and incomplete illustrative inputs retain their labels. No duplicated
domain owner, new causal replay gate, freshness policy, or provenance-label
requirement was added.

The affected boundary is O1's read-only consumer of H0/H1 lifecycle events.
`TraceEvent` owns versioned event conformance; `LifecycleLedger` remains the
single event-write/replay authority. This approval qualifies only the bounded
raw-event conformance/detachment repair at the hashes above. ARCH-02 label
conformance, full O1 exit, H0/H1 release closure, H2 parity, and R4 remain
separate. No hooks, providers, Git state changes, or source edits were performed.
Repository-wide checks and independent backend identity are not established by
this review. The next separate discriminating probe is ARCH-02's label-policy
conformance, not an expansion of this repair.

Standards: 0 blocking, 0 nit. Spec: 0 blocking, 0 nit.

VERDICT: APPROVE
