# SPEC-02 bounded ingress authority repair

Date: 2026-10-08. Source freeze: 18:47:51 UTC. Writer self-check only.
HEAD: `06f5a29daef9bb877fb08b6c6ee47d870df94d71`. No staging, commit or push.

## Scope and authority

The affected boundary is the H0/H1 task-ingress and compilation seam. The human
selected an authority-bound ledger command. `TaskIngressAuthority` owns admission;
`LifecycleLedger` remains the sole lifecycle writer and replay owner.
The root agent approved the narrow `task_registry.py` addition and exact affected
fixture migrations. Canonical documentation, runtime products, caches, dashboard
work and synthetic integration were not changed by this writer.

The root baseline includes the complete dirty-file manifest, hashes and binary
diff in `/tmp/uah-ingress-round-20261008-before/`. Existing dirty source is
human-owned. This directory retains the exact before bytes for affected files,
the incremental per-file deltas and the frozen SHA-256 manifest. The original
three-file scope includes `task_compiler.py`, which required no edit.

## Mechanism

| Route | Owner | Discriminating observation |
| --- | --- | --- |
| Genuine ingress | TaskIngressAuthority | Policy is identity-verified before freezing. Accepted starts issue a private command bound to the issuer capability and exact ledger. |
| Fresh append | LifecycleLedger | The command is checked inside the existing lock/reload/reduce/append/flush/fsync critical section. Its ingress and decision identities are reverified; the start decision is recomputed under the issuer's frozen policy. Only then does the ledger add its durable start-authority marker. |
| Fresh compilation | EnvironmentTaskRegistry and LifecycleLedger | `require_start` checks exact lineage and the ledger-owned start marker. The active append reducer also rejects a fresh `task_compiled` event from unmarked historical lineage. |
| Raw fact | LifecycleLedger | Caller-created `TaskStartedFact`, even with fields matching a valid decision, is rejected without an append. |
| Historical replay | LifecycleLedger | Unmarked starts remain readable and projectable, but cannot authorize fresh compilation. Replay never issues the private command capability. |
| Cooperating writers | LifecycleLedger | Barrier-based simultaneous duplicate starts produce one start and one rejection; distinct starts produce a contiguous sequence of two starts. |

Content hashes verify identity, not issuer authority. There is no second task
store, secret sidecar or authenticated-proof protocol. The durable marker uses
the existing trusted-ledger-file ownership boundary. This repair does not resist
an attacker who can rewrite trusted ledger files and recompute hashes, or mutate
private issuer internals in the trusted Python process. Public event, mapping,
replay and iterable exports cannot be submitted as authoritative record inputs.

## Baseline and red/green evidence

Baseline command:

```text
.venv/bin/python -m pytest tests/test_task_compiler.py tests/test_environment_ingress.py tests/test_lifecycle_ledger.py -q
89 passed in 0.67s
exit 0
```

The first vertical slice added a public `LifecycleLedger.record` assertion that
a raw matching start must be rejected before changing source. Its red command:

```text
.venv/bin/python -m pytest tests/test_task_compiler.py::test_raw_task_start_cannot_authorize_a_matching_compiler_decision -q
Failed: DID NOT RAISE <class 'ValueError'>
1 failed in 0.18s
exit 1
```

The minimal command gate made that test green. Additional public-seam probes
cover genuine compilation and restart/record, unmarked historical replay with
fresh compile/record rejection, foreign rehashed decisions, stale decision
content, mutated ingress, rejected ingress with no start, stale domain policy,
public export forms and simultaneous cooperating writers. Exact affected
fixtures now request starts through `admit`, rather than fabricating raw facts.

The frozen focused gate is in [focused-green.txt](focused-green.txt): 189 passed,
one current O1 example-freshness test deselected. This is a named exclusion, not
a full-suite pass. The initial full suite is in
[full-suite-initial.txt](full-suite-initial.txt): 546 passed, two current O1 example
freshness failures. The root recorded both freshness failures at baseline;
the new durable marker also changes current example event IDs. The root owns
current-example regeneration and the isolated full-hook run. Historical
artifacts were not regenerated.

Additional writer checks:

```text
.venv/bin/python -m ruff check src/ab_harness/task_ingress_authority.py src/ab_harness/lifecycle.py src/ab_harness/task_registry.py tests/test_task_compiler.py tests/test_environment_ingress.py tests/test_lifecycle_ledger.py tests/test_two_stage_admission.py tests/test_observatory.py tests/test_observatory_raw_identity.py
All checks passed! (exit 0)
python scripts/render_agentic_harness_docs.py --check
Checked 12 metadata records (exit 0)
git diff --check
exit 0
```

No formatter was run against unrelated human-owned files or historical evidence.
The parent round will run repository hooks on an isolated snapshot so hook
formatting cannot alter this source freeze.

## Bounded disposition

Implementation and writer self-check are complete for this source freeze.
Independent review is pending and owned by the root round. H0/H1/H2 qualification,
NAO parity and provider connectivity are not established by these fixtures.
No new compatibility policy beyond historical read/replay without fresh
compilation authority was adopted. Legacy raw-start writer fixtures were
migrated explicitly; old persisted history was not upgraded to authoritative
start provenance. Next gate: two fresh independent reviews against the exact
before bytes and frozen incremental deltas, followed by the root full-hook result.
