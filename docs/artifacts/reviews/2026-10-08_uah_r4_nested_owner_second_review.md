# R4 nested-owner second independent review

Date: 2026-10-08. Scope: the frozen four implementation files and new
`tests/test_nested_admission_owner.py`, compared with the exact-before files in
`2026-10-08_uah_r4_nested_owner_evidence`. This is a bounded H0 admission and
owner-execution review, not H0/H1 exit or H2 qualification.

Evidence and final identity checks completed at 18:19:43 Europe/Madrid
(16:19:43 UTC), after the 18:17:10 soft target and before the 18:23:10 hard
stop. No declared gate was removed to meet either time.

## Independence and method

This fresh reviewer did not write the candidate. `REVIEW.md` was read first.
The input plan was saved in
`2026-10-08_uah_r4_nested_owner_second_inputs.md` before implementation or diff
inspection. Three public positive controls then ran on both isolated trees:
two-stage proposal admission, exact-lease execution, and accepted common-ledger
restart. Both returned `3 passed, 45 deselected`. Only then were the candidate
implementation and diff inspected.

The parent requested a distinct-model second reviewer. This agent cannot
independently observe the actual backend model or reasoning setting and does
not attest that identity. The code-review skill's normal additional Standards
and Spec subagent split was not used: the parent explicitly retained two fresh
review lanes and directed this lane to report both axes locally. The fixed
point is the supplied exact-before copies, not a Git merge-base. No writer
receipt, other review narrative, or interrupted-review contents were consulted.
Required owning documents were read, including their current qualification
statements. Historical source specimens and fixtures were used as test inputs.

Both trees reside under `/tmp/uah-nested-second.DDsI9f/`. Source, tests and
`pyproject.toml` were copied once into `current`, then copied to `before`; only
the four named source files were replaced with their exact-before versions.
The current test file was deliberately present in both trees. Final recursive
comparison, excluding bytecode caches, found exactly those four source
differences and no test differences. Archived historical specimens were copied
identically to both trees.

## Frozen identity

Hashes matched both before execution and at final verification:

| File | SHA-256 |
| --- | --- |
| `src/ab_harness/proposal_admission.py` | `a2a76bf21eb865934d63b5eeece722b4b7827d659421fb7a5bc566bb3161455c` |
| `src/ab_harness/domain_lifecycle.py` | `48de0478d577b58567483f5fa22334f641a32855f32a240944b91346906dff6f` |
| `src/ab_harness/environment.py` | `9fd718a1d663dcc2bfe844a4b289f4191aaa90f520fe36215df5331e52047248` |
| `src/ab_harness/lifecycle.py` | `ef1cbd9d69c25735f94d14cd7df892ad97f1f0485c407f0b172d13d56e10b6d1` |
| `tests/test_nested_admission_owner.py` | `4175dc62a23955924ff10dd6653d6a5f23cc8305f87579e058ae368363fcc8c0` |

## Executed evidence

All commands used the repository `.venv/bin/python`, each isolated tree as the
working directory, and that tree's `src` as `PYTHONPATH`.

| Execution | Candidate | Exact-before |
| --- | --- | --- |
| Initial positive controls, before reading implementation | 3 passed | 3 passed |
| `test_two_stage_admission.py`, `test_admitted_object_snapshot.py`, `test_nested_admission_owner.py`, `test_lifecycle_ledger.py` | 132 passed | 114 passed, 18 failed |
| `test_admission_active_provenance.py` | 16 passed | 16 passed |
| Independent second-review probe | 809 passed | 711 passed, 98 failed |

The initial historical-suite attempt had 15 passes and one missing-file error
on each tree because the isolated harness had not copied
`legacy_v2_control.fixture`. Copying that same existing specimen to both trees
resolved the setup omission; the complete rerun passed on both. This was not
classified as a candidate defect. Matrix failures on the baseline include
accepted tampering, invocation of caller-controlled verifiers, and incoherent
post-handler settlement; they are not 98 distinct findings or 98 dispatches.

The independent, retained executable is
`2026-10-08_uah_r4_nested_owner_second_probe.py`. Its machine-readable results
are `2026-10-08_uah_r4_nested_owner_second_current_matrix.json` and
`2026-10-08_uah_r4_nested_owner_second_before_matrix.json`. To reproduce, invoke
that script with the selected isolated tree as the working directory and
`PYTHONPATH=<tree>/src`.
The final probe SHA-256 is
`eb01e1f9562567cf7e281efc3f1dd03d3ad3fcbab8617ed05af898133f42237c`.

The probe mutates all 11 proposal fields, nine snapshot fields, 16 scalar or
collection admission fields, and five lease fields. Relevant crossings include
fresh and reused leases, provenance, dispatch, receipts, evidence rejection,
owner serialization, and ledger recording. Every case is exercised with and
without instance serializer/verifier/copy overrides. Additional cases cover
missing snapshots, empty obligations, combined proposal/snapshot changes, and
six validly rehashed inner-proposal alternatives hidden behind old wire values.

Ten handler controls cover unchanged values and caller mutation of the
proposal, snapshot, admission, or lease, each with valid or undeclared effects.
Candidate dispatch receives `{"label":"cup"}` once. Valid results retain the
original admission ID and owner, then reach accepted restart replay. Undeclared
effects produce `undeclared_observed_effect`, retain the frozen lease, and
replay an evidence failure without inventing terminal acceptance.

Seven independently assembled historical controls confirm that authentic old
concrete objects cannot obtain current leases, dispatch or receipts, while
fully marker-stripped history remains readable but cannot authorize lease
reuse, dispatch, execution start or current semantic provenance. The separate
public historical suite also covers completion and acceptance continuation,
foreign verifiers, wrong-frame metadata, and authentic completed-history
readability.

The matrix records the exact rejection-message distribution. Missing snapshot
fields still raise `AttributeError` in two direct verification/serialization
routes, as on the baseline; these routes fail closed without dispatch or ledger
append. This candidate does not promise a new uniform exception taxonomy.
No new enum, unit, time, threshold, UI label, hook installation or exemption is
introduced. Date/time and unit permutations therefore do not add a relevant
changed contract. Existing multi-operation, retry, evidence-rejection and
restart tests were included in the focused run.

## Standards

No BLOCKING or NIT findings were reproduced in the frozen candidate.

| REVIEW.md principle | Assessment |
| --- | --- |
| Separation of concerns | OK. Artifact owners construct verified copies; the ledger checks recorded provenance; environment execution remains the effect owner (`proposal_admission.py:147`, `domain_lifecycle.py:114`, `environment.py:484`, `lifecycle.py:758`). |
| Programming by intention | OK. `verified_copy` names the validation-and-detachment operation and callers state which artifact owner is authoritative. |
| Encapsulation | OK. Concrete owner methods ignore supplied instance method overrides. Detached copies prevent caller mutation during a handler from altering settlement authority. The independent matrix exercises every covered nested field. |
| High cohesion | OK. Proposal, admission and lease verification remain with their existing artifact classes. No registry, policy or runtime subsystem is added. |
| Low coupling | OK. Consumers reuse those artifact-owned boundaries; no ROS, NAO, provider SDK or runtime-product dependency is introduced. Similar copy methods compose distinct artifact contracts rather than create a second owner or duplicate business policy. |

## Specification

No BLOCKING or NIT findings were reproduced. The bounded repair meets the
supplied-instance contract at the changed canonicalization, provenance,
execution, receipt and restart crossings. A valid current artifact still
round-trips and executes; a different but independently valid nested proposal
cannot borrow the original admission's identity via an instance serializer.
Historical readability remains distinct from current execution authority.

The UAH guardrails directed checks of the proposal-to-admission-to-lease-to-owner
chain, owner evidence, and replay. No authority moves to a model, registry
discovery, Observatory, or provider. Semantic admission and native execution
admission remain separate. Adaptive promotion and live providers are outside
this review.

## Limits and handoff

Approval is limited to the frozen five-file candidate and concrete supplied
instance fields/methods. Arbitrary modification of trusted module symbols,
classes, process memory, hostile concurrency, and release-wide qualification
were not tested or claimed. No source repairs, staging, commits, pushes or
provider calls were performed. `git diff --check` passed. The parent owns the
repository hook run and aggregate gate; this review does not substitute for it.

The next distinct qualification work remains the separately owned broader
authority, freshness, output-validation and release gates, not an expansion of
this bounded approval.

VERDICT: APPROVE
