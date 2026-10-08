# O1 raw-evidence identity: second independent review

## Predeclared inputs (2026-10-08, before source or diff inspection)

1. Run the existing public `tests/test_observatory.py` suite unchanged and unread as the initial control.
2. Genuine `TraceEvent` instances with stale content IDs in raw tuple and one-shot generator inputs, compared with a genuine unchanged ledger.
3. Identity-bearing mutations before status interpretation and before actor/trace ordering; check earliest rejection without projection or rendering.
4. Valid incomplete illustrative raw event sequences, including empty and singleton controls.
5. Invalid member types, duplicate IDs, and two or more events in both input orders.
6. All rendering consumers of the resulting projection; unchanged valid output and propagated errors for invalid evidence.
7. Read-only behavior of input events and ledger; propagation of iterator and identity errors.

I will freeze dependencies in an isolated copy and compare the retained exact-before Observatory source against the frozen current source, keeping other dependencies identical. This is a byte-bounded comparison, not a clean whole-repository baseline. The complete shared dirty manifest was captured after the edit freeze, not before all edits. No writer receipt, rationale, or other review is an input.

The requested review model is `gpt-6-astra` at `max`; the actual backend is not observable to this reviewer. Scope is identity integrity only, not ARCH-02 measured/reviewed-label authenticity or causal validation. Concurrent R4-FIX changes outside the two-file O1 scope are excluded from attribution.

## Scope, provenance, and execution

Completed at approximately 17:40 Europe/Madrid on 2026-10-08. This fresh reviewer
did not write the implementation and did not read writer receipts, rationale
reports, or another review. Required repository guidance and canonical contract
sections were read; their status claims were not substituted for execution.
The code-review skill's standards and spec axes are reported separately here;
no nested review input was used. UAH guardrails kept schema identity ownership in
`TraceEvent` and excluded causal validation or expanded provenance claims.

The initial plain `python -m pytest -q tests/test_observatory.py` attempt failed
collection because that interpreter could not import `ab_harness`. Before reading
implementation or diff, the isolated control was rerun using the repository
virtual environment and explicit `PYTHONPATH=src`: **23 passed**.

The isolated trees are `/tmp/uah-o1-second-review-20261008/after` and
`/tmp/uah-o1-second-review-20261008/before`. Dependencies were copied at roughly
17:35 Madrid. The before tree differs by the retained exact-before Observatory
source; the retained original test was also overlaid and is byte-identical to
the frozen current original test. A recursive source comparison excluding
bytecode confirmed only `src/ab_harness/observatory.py` differs. The new test is
present on both sides for the counterfactual. No Git commit is claimed as the
whole-tree baseline.

| Input | SHA-256 |
| --- | --- |
| Current `src/ab_harness/observatory.py` | `aec50ca2e77d5c5bbe187ae08e6700797dee28bf7a703ac35f593de884ecb878` |
| New `tests/test_observatory_raw_identity.py` | `02e90f519120ebfe7d785954606a24bc8d286c5e6ff01b9f09a1ad3211e236d1` |
| Exact-before Observatory source | `bb3d2b359fec4adeb15619abee12b86bc20734548cccfd3929ab17f9ce7cfcd0` |
| Retained original Observatory test | `491e95bf7305d0c50179bd5cf1ef94aaf87aa03994142b4b22d804815406cf92` |

The live two-file target hashes were rechecked at approximately 17:40 and still
matched. The dependency manifest is
`2026-10-08_uah_o1_raw_identity_second_dependencies.sha256`; it records the
isolated source, scripts, and tests, not a pre-edit whole-repository baseline.
Concurrent R4-FIX bytes are held identical across this comparison and receive
no approval from this review.

Executed in the isolated after tree:

```text
PYTHONPATH=src /home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest -q tests/test_observatory.py
23 passed

PYTHONPATH=src /home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest -q tests/test_observatory.py tests/test_observatory_raw_identity.py
31 passed

PYTHONPATH=src /home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest -q tests/test_observatory.py tests/test_observatory_raw_identity.py tests/test_agent_runtime_example.py
33 passed

PYTHONPATH=src /home/juanbeck/universal-agentic-harness/.venv/bin/python scripts/render_observatory_example.py --check
exit 0

PYTHONPATH=src /home/juanbeck/universal-agentic-harness/.venv/bin/python scripts/render_agent_runtime_example.py --check
exit 0
```

The same original plus new test command in the before tree produced **6 failed,
25 passed**. All six failures were expected stale-content rejection assertions
that the before implementation did not satisfy.

The durable independent probe is
`2026-10-08_uah_o1_raw_identity_second_probe.py`. From either isolated tree:

```bash
PYTHONPATH=src:. /home/juanbeck/universal-agentic-harness/.venv/bin/python /home/juanbeck/universal-agentic-harness/docs/artifacts/reviews/2026-10-08_uah_o1_raw_identity_second_probe.py
```

Its full results are retained in
`2026-10-08_uah_o1_raw_identity_second_before.json` and
`2026-10-08_uah_o1_raw_identity_second_after.json`. The output identifies the
actual imported module path and source hash. Of 124 cases, the before version
has 62 expected-result mismatches; the current version has eight, all instances
of the single finding below. Covered-field mutations in genuine v1 task, v2
actor, and v2 task events reject through tuples and generators. Checks include
status, sequence, environment, data, time, artifact and causal-reference bytes;
v2 actor/scope mutations; foreign member types and duplicates; two-event input
orders; empty and incomplete illustrative controls; file-backed read-only
behavior; iterator errors; graph and HTML rendering.

## Spec

### BLOCKING: 1 of the 1 found so far. V1 fixed-field mutation bypasses the identity boundary

Location: `src/ab_harness/observatory.py:241-242`, with the incomplete owner
verification at `src/ab_harness/lifecycle.py:164-166` and v1 omission in
`src/ab_harness/lifecycle.py:174-194`.

Input: obtain a genuine `uah.trace_event/v1` task-start event from
`LifecycleLedger.events()`. Preserve its event ID and all canonical serialized
fields. Set `agent_run_id` to `agent:forged` with `object.__setattr__`, then pass
the event as a tuple or one-shot generator to `project_observatory` or
`render_observatory`. Repeat separately with `event_scope="agent"`.

Expected: reject the incompatible v1 representation before grouping or
rendering. V1 requires task scope and no actor identity. Those constraints are
enforced at construction, and the documented O1 contract forbids assigning
actor membership to v1 task events.

Actual: all eight combinations succeed in both before and current versions.
The actor mutation creates `agent:forged` in the actor projection and rendered
graph, although `event.to_dict()` contains no `agent_run_id`. The scope mutation
removes the only task trace, leaving `projection.trace_ids == ()`. The original
ledger continues to show `("trace:one",)` with no actors. The current check
calls `verify_identity()`, whose v1 payload excludes both fixed fields and does
not revalidate their fixed values.

This is an unresolved representation-integrity gap, not a regression introduced
by the two added lines. It does not depend on forging causal prerequisites or a
measured/reviewed label. It is the same genuine-object mutation threat model as
the new stale-ID tests. The repair works for hashed fields but is insufficient
for all identity-relevant state consumed by the projection.

Keep the correction with the `TraceEvent` owner: revalidate the version-specific
fixed-field contract at the identity trust boundary while preserving historic
v1 serialized IDs. Add both actor and scope bypasses as public-seam controls.
Do not replicate a second canonicalization policy in Observatory.

## Standards

1. **Separation of concerns: OK.** The added projection check delegates identity
   verification to `TraceEvent`; it adds no ledger writes or renderer business
   rules.
2. **Programming by intention: OK.** Calling the artifact's named verification
   boundary before ordering expresses the intended check directly. Its incomplete
   v1 behavior is the single finding above, not a separate naming finding.
3. **Encapsulation: violation**, `src/ab_harness/lifecycle.py:164-166`, exposed at
   `src/ab_harness/observatory.py:241-242`. The artifact boundary does not enforce
   its own v1 fixed-field invariants before consumers use them. This is finding 1.
4. **High cohesion: OK.** The change is confined to validating event identity at
   one projection ingress point; no unrelated mechanism was added.
5. **Low coupling: OK.** It uses the existing lifecycle artifact interface and
   introduces no provider, ROS, NAO, runtime-product, or new codec dependency.

Standards: one blocking encapsulation finding. Spec: the same one blocking
incomplete-boundary finding. Total unique findings: **one BLOCKING, zero NIT**.

## Limits and gate outcome

Affected gate: the O1 read-only slice alongside H0/H1 closure. The lifecycle
artifact owner remains authoritative for identity; Observatory remains a
consumer. The covered stale-content repair is demonstrated, but the raw-input
identity-integrity gate cannot close until the fixed v1 representation is also
validated. No conclusion is made about full H1 closure, H2 parity, ARCH-02 label
authenticity, or causal completeness of illustrative raw events.

No source, hooks, Git state, provider configuration, or external service was
changed by this reviewer. Only this report and its probe/evidence files were
written. The global hook suite was not run against the concurrently changing
working tree; its potentially mutating formatting and setup operations are
outside this read-only assignment. The exact next probe is the eight v1
fixed-field cases above against a separately frozen correction.

VERDICT: CHANGES
