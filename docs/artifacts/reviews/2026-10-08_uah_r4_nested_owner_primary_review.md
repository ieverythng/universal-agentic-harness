# R4 nested-owner primary independent review

Date: 2026-10-08. Review completed before the 18:17:10 Europe/Madrid target.

No BLOCKING or NIT finding was found in the supplied five-file change. This is
a scoped approval of concrete nested-artifact verification and execution-value
isolation, not H0/H1 release qualification or provider/effect-freshness approval.

## Independence and fixed inputs

This fresh reviewer did not write the candidate. `REVIEW.md` was the first file
read. The inputs in `2026-10-08_uah_r4_nested_owner_primary_inputs.md` were saved
before implementation, diff, or test-source reading. The initial public control
then ran to completion in a throwaway copy before those reads.

The requested `gpt-6.1-sol`/`max` model-effort pair is not independently
observable through this reviewer runtime. No specific substitute was knowingly
selected. This report does not attest the different-model requirement for the
aggregate two-review gate.

The governing sources were root `AGENTS.md`, `CONTEXT.md`, relevant H0/H1 and H2
qualification sections of the masterplan, the foundation's admission and
execution authority section, and the current release-boundary sections of the
development log. These owning documents contain historical status summaries;
no linked writer receipt, other review, rationale, or interrupted review output
was opened. The UAH guardrails and code-review skills were read. The supplied
independent-review contract and individual reviewer assignment governed the
flow instead of spawning another standards/spec review pair.

Release boundary: H0/H1 authority repair on the route to H2. Semantic admission
owns the admitted snapshot, domain lifecycle admission owns execution leases,
the environment owner owns dispatch and observed effects, and `LifecycleLedger`
remains the single public append/replay authority.

The fixed base consists of the four exact-before copies in
`2026-10-08_uah_r4_nested_owner_evidence`, not Git HEAD or a merge base. The
current and before throwaway trees share every unaffected source, test, and
runtime dependency. The added candidate test module runs against both.

Current SHA-256 values, rechecked after all probes:

| File | SHA-256 |
| --- | --- |
| `src/ab_harness/proposal_admission.py` | `a2a76bf21eb865934d63b5eeece722b4b7827d659421fb7a5bc566bb3161455c` |
| `src/ab_harness/domain_lifecycle.py` | `48de0478d577b58567483f5fa22334f641a32855f32a240944b91346906dff6f` |
| `src/ab_harness/environment.py` | `9fd718a1d663dcc2bfe844a4b289f4191aaa90f520fe36215df5331e52047248` |
| `src/ab_harness/lifecycle.py` | `ef1cbd9d69c25735f94d14cd7df892ad97f1f0485c407f0b172d13d56e10b6d1` |
| `tests/test_nested_admission_owner.py` | `4175dc62a23955924ff10dd6653d6a5f23cc8305f87579e058ae368363fcc8c0` |

Base SHA-256 values, in the same four-source order:

```text
ae9cf6134e0d9fb3fa17ccf191e63a139222ab1661306d3e13d387d3e2be34c5
2ed2f0068b5ded25cd190850feed941f8be78a22157a07fbb0b6d42260ec7de0
4cedae9add9c50618e064964da8f3ad2c78f696969b9c9d2e5e593af32a19eaa
b35641d97b8d915df358e880de73400386395e8b3525a41cae99e329b04176ee
```

## Execution record

The interpreter was `/home/juanbeck/universal-agentic-harness/.venv/bin/python`.
No installation, provider call, source edit, staging, commit, or push occurred.
The root task owns repository hooks; this reviewer did not duplicate them.

Throwaway preparation commands, run from the repository:

```bash
mktemp -d /tmp/uah-r4-primary-current.XXXXXX
cp -a src tests pyproject.toml /tmp/uah-r4-primary-current.0xItKd
mktemp -d /tmp/uah-r4-primary-before.XXXXXX
cp -a /tmp/uah-r4-primary-current.0xItKd/. /tmp/uah-r4-primary-before.Jb7E5g
cp docs/artifacts/reviews/2026-10-08_uah_r4_nested_owner_evidence/proposal_admission.py.before /tmp/uah-r4-primary-before.Jb7E5g/src/ab_harness/proposal_admission.py
cp docs/artifacts/reviews/2026-10-08_uah_r4_nested_owner_evidence/domain_lifecycle.py.before /tmp/uah-r4-primary-before.Jb7E5g/src/ab_harness/domain_lifecycle.py
cp docs/artifacts/reviews/2026-10-08_uah_r4_nested_owner_evidence/environment.py.before /tmp/uah-r4-primary-before.Jb7E5g/src/ab_harness/environment.py
cp docs/artifacts/reviews/2026-10-08_uah_r4_nested_owner_evidence/lifecycle.py.before /tmp/uah-r4-primary-before.Jb7E5g/src/ab_harness/lifecycle.py
```

Commands below use the indicated working directory and explicit import path.

```bash
# cwd /tmp/uah-r4-primary-current.0xItKd (initial execution before source reading)
PYTHONPATH=/tmp/uah-r4-primary-current.0xItKd/src /home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest tests/test_two_stage_admission.py tests/test_nested_admission_owner.py -q
# 73 passed in 1.72s, exit 0

# cwd /tmp/uah-r4-primary-before.Jb7E5g
PYTHONPATH=/tmp/uah-r4-primary-before.Jb7E5g/src /home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest tests/test_two_stage_admission.py tests/test_nested_admission_owner.py -q
# 18 failed, 55 passed; exit 1
PYTHONPATH=/tmp/uah-r4-primary-before.Jb7E5g/src /home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest tests/test_two_stage_admission.py tests/test_nested_admission_owner.py -q --tb=no
# 18 failed, 55 passed in 1.74s; exit 1

# cwd /tmp/uah-r4-primary-current.0xItKd
PYTHONPATH=/tmp/uah-r4-primary-current.0xItKd/src /home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest tests/test_admitted_object_snapshot.py tests/test_admission_active_provenance.py tests/test_lifecycle_ledger.py -q --tb=short
# 75 passed in 2.55s, exit 0

# cwd /tmp/uah-r4-primary-before.Jb7E5g
PYTHONPATH=/tmp/uah-r4-primary-before.Jb7E5g/src /home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest tests/test_admitted_object_snapshot.py tests/test_admission_active_provenance.py tests/test_lifecycle_ledger.py -q --tb=short
# 75 passed in 2.47s, exit 0

# cwd /tmp/uah-r4-primary-current.0xItKd
PYTHONPATH=/tmp/uah-r4-primary-current.0xItKd/src:/tmp/uah-r4-primary-current.0xItKd/tests /home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest /home/juanbeck/universal-agentic-harness/docs/artifacts/reviews/2026-10-08_uah_r4_nested_owner_primary_probe.py -q --tb=no
# 56 passed in 2.92s, exit 0

# cwd /tmp/uah-r4-primary-before.Jb7E5g
PYTHONPATH=/tmp/uah-r4-primary-before.Jb7E5g/src:/tmp/uah-r4-primary-before.Jb7E5g/tests /home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest /home/juanbeck/universal-agentic-harness/docs/artifacts/reviews/2026-10-08_uah_r4_nested_owner_primary_probe.py -q --tb=no
# 39 failed, 17 passed in 2.86s, exit 1
```

The initial independent-probe iteration used the same commands with
`--tb=short`: current 56 passed in 3.65s; before 54 failed, 2 passed in 4.70s.
An instance-hook counter initially included calls while installing masks in the
test setup. Clearing that counter before the tested crossing removed 15
instrumentation-only failures from the before result. No candidate code changed.
The final probe SHA-256 is
`463ec51395c6a7b307b4662782761027beb0e4946dafff2099d593bfe951d79b`.

Historical test dependencies were copied without opening review prose: the
`legacy_v2_control.fixture` and two before source files from the historical
snapshot evidence directory, plus `authentic_v2_admitted.fixture` and
`authentic_v2_leased.fixture` from the fix evidence directory. Both throwaway
trees received identical copies.

```bash
diff -qr --exclude=__pycache__ /tmp/uah-r4-primary-current.0xItKd/src /tmp/uah-r4-primary-before.Jb7E5g/src
# Only the four reviewed source files differ.
diff -qr --exclude=__pycache__ /tmp/uah-r4-primary-current.0xItKd/tests /tmp/uah-r4-primary-before.Jb7E5g/tests
# No differences.
/home/juanbeck/universal-agentic-harness/.venv/bin/ruff check /home/juanbeck/universal-agentic-harness/docs/artifacts/reviews/2026-10-08_uah_r4_nested_owner_primary_probe.py
# All checks passed, exit 0.
```

## Spec and authority evidence

The initial control and independent probes together cover valid current
artifacts, actual-field versus instance-serializer/verifier disagreement,
separate and combined stale nested/outer identities, stale lease identity,
foreign owner fields, changed snapshots, provenance comparison, lease reuse,
dispatch, receipt issuance, and execution-start recording. The supplied tests
also cover missing snapshots and overridden instance copy methods.

A separately content-addressed valid proposal for `label=mug`, with an instance
serializer reporting the earlier `label=cup` proposal, is rejected at six
crossings because the outer admission still identifies the earlier proposal.
The current code verifies the concrete nested fields, not that instance method.
Before code accepts the masked representation at those six crossings.

Twelve independent handler callbacks mutate the caller-owned proposal,
snapshot, admission/lease-owner fields, or all of these. Each actual dispatch
still receives `label=cup` once. Success receipts retain the original lease and
admission identities and replay to `accepted`. Undeclared `direct_speech`
produces `undeclared_observed_effect`, no receipt, and replay failure stage
`evidence`. Native exceptions remain the original `RuntimeError` and replay
failure stage `execution`. The before code loses those coherent completion
paths after the caller mutation.

Two distinct operations execute in both orders without identity conflation.
Each receives a distinct lease and replay preserves that execution order.
Repeating either consumed lease rejects. Genuine old completed history remains
read-only, accepted, and preserves its known digest through the historical
control. Old concrete admissions/leases and stripped current provenance remain
unable to authorize active continuation in both versions.

No new reason-code, enum, unit, date policy, threshold, exemption, hook, or
template is introduced by the diff. The change retains existing error messages
and evidence-rejection attribution; no unknown owner or historical snapshot is
inferred.

## Standards and five principles

| Principle | Assessment |
| --- | --- |
| Separation of concerns | OK. Proposal/admission/lease classes verify their own content; domain and environment authority remain separate. No second ledger or semantic owner is added. |
| Programming by intention | OK. `verified_copy` states the trust-crossing operation directly, and callers invoke the owning concrete implementation. |
| Encapsulation | OK. Proposal, admitted snapshot, and lease are detached before dispatch; caller mutation cannot change the issued operation or its evidence path. |
| High cohesion | OK. Each artifact owns its own schema and reconstruction. The ledger owns provenance comparison and replay, while the environment owns receipt issuance. |
| Low coupling | OK. No provider, ROS, runtime-product, or new external dependency is introduced. Existing portable interfaces remain the integration seams. |

There is no duplicated new policy, dual owner, or business logic in UI/templates
in the supplied change. Artifact-local reconstruction is appropriate here;
combining separate schema and identity owners would add unnecessary coupling.

## Limits

All planned in-scope gates completed. This is finite adversarial evidence, not
a proof against arbitrary process/module replacement, concurrency races,
provider output, live adapters, or independent tampering with unrelated
artifact families. It does not establish the aggregate different-model gate or
whole-tree hooks. Root-owned integration evidence remains separate. Further
changes to these frozen bytes require a new independent review.

VERDICT: APPROVE
