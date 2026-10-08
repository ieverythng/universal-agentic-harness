# R1: domain-pack identity at task compilation

Date: 2026-10-08. Status: APPROVED compiler-only repair; overall H0/H1 review remains CHANGES.
Start: 16:03 Europe/Madrid. Target stop: 16:23, one repair batch only.
Stopped: 16:14 Europe/Madrid after artifact validation. No automatic continuation.
Branch: `feat/pre-commit-queue`. HEAD: `28fab5e7f2c244d86a64c371f2118017999b2387`.

## Target and ownership

Repair STD-01/SPEC-01 only: `TaskSpecCompiler.compile` must reject replacement
or nested mutation of an issued domain policy under its unchanged revision,
before producing a CompiledTask. DomainContractPack owns the content identity;
the compiler reverifies that identity before consuming its rules. Keep the
existing payload/hash format and valid compilation result unchanged.

The [R0 receipt](2026-10-08_uah_r0_baseline_and_skill_handoff.md) is closed before
this round. The [R1 start manifest](2026-10-08_uah_r1_start.sha256) records the
dirty/untracked bytes, including R0 additions. Prior implementation changes
remain human-owned. Isolate this round from the large pre-existing diff using
the before snapshots in `/tmp/uah-r1-domain-pack-20261008/`.

## Frozen probes and acceptance

- Red: replace `effect_rules` with a retryable rule while retaining the issued
  revision; public compilation must raise a content-revision ValueError.
- Red: mutate the issued nested rule's `failure_policy` to retryable while
  retaining that revision; the same public boundary must reject it.
- Control: the existing untouched frozen-projection test must retain its pinned
  compiled-task identity and legitimate terminal policy.
- Gate: focused compiler and identity compatibility tests, relevant ingress/
  admission tests, full tests, pre-commit, generated-doc synchronization, both
  O1 examples, whitespace, and fresh REVIEW.md review including a distinct
  second model for the validation gate.

No evidence/freshness representation, provider adapter, runtime authority
redesign, shared codec extraction, remaining six mechanisms or release closure
is authorized. No live request, model startup, staging, commit or push.
Any follow-up correction needs its own independent review. An incomplete gate
at the time target is reported as incomplete, not approved.

## Evidence

### Red and green through the public compiler

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_task_compiler.py::test_task_compiler_rejects_domain_policy_tamper_after_issue tests/test_task_compiler.py::test_task_spec_compiles_one_frozen_projection_and_obligation_set
```

Before implementation: both `replacement` and `nested` cases failed with
`DID NOT RAISE ValueError`; the untouched valid control passed (2 failed, 1 passed).
After implementation: 3 passed. Both mutated inputs now raise
`ValueError: domain contract pack revision does not match content`.

The implementation adds `DomainContractPack.verify_identity()` by reusing the
existing payload/hash check, keeps constructor validation, and calls that check
at `TaskSpecCompiler.compile` before reading domain rules. There is no new
payload, schema version, hash format or generic identity codec. The unchanged
control retains `compiled-task:sha256:54b3dd46199545f76341b5c1dfaa69023a9147e5adc5c758515802aacfba9739`.

### Executed gates

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_task_compiler.py tests/test_content_identity_compatibility.py tests/test_environment_ingress.py tests/test_two_stage_admission.py
PYTHONPATH=src .venv/bin/python docs/artifacts/reviews/2026-10-05_uah_review_repros/standards_domain_tamper.py
./scripts/run_precommit.sh
.venv/bin/python -m pytest -q
.venv/bin/ruff check src tests scripts
.venv/bin/python scripts/render_agentic_harness_docs.py --check
PYTHONPATH=src .venv/bin/python scripts/render_observatory_example.py --check
PYTHONPATH=src .venv/bin/python scripts/render_agent_runtime_example.py --check
git diff --check
```

Results: 109 relevant tests and 346 full tests passed; the saved domain-tamper
diagnostic now reports the expected ValueError rather than accepted retryable
policy. Pre-commit, Ruff, documentation and both O1 example checks passed.
Exit zero of the diagnostic alone is not a conformance claim; its changed
expected/actual rejection is the discriminating result.

The canonical development log and masterplan now identify the original review
gaps and this separate repair receipt. Their HTML companions were regenerated.
R0 reviewer/holdout retention was completed without mutating the frozen skill.
No other runtime correction was made.

### Frozen repair bytes and review

| File | SHA-256 |
| --- | --- |
| `src/ab_harness/domain_contracts.py` | `b47e522c1184786170df1d9f3bbbfb7398c340e44a7b44a514312a8da17baf1c` |
| `src/ab_harness/task_compiler.py` | `b11625e4cb5a64f74327e2112a6e182b48e45ce9821135a5af39a9f36f92e9bf` |
| `tests/test_task_compiler.py` | `d847db50aa939c02b4e7190234b434fa7eccac3548c70a122aac1ab66ffe5b29` |

Fresh reviews requested at `gpt-6.1-sol/max` and `gpt-6-astra/max`, using only
the repository, REVIEW.md and this three-file delta against the exact dirty-tree
before snapshots. No fallback reported; deployment identity is not independently
observable.

| Independent review | Findings | Verdict | Artifact SHA-256 |
| --- | --- | --- | --- |
| [Primary](2026-10-08_uah_r1_domain_pack_primary_review.md) | 0 BLOCKING; 0 NIT | APPROVE | `14da7145ad7a3b3f575d4438a5d959abdbd7923c65655be788ae19f52eb8abab` |
| [Distinct model](2026-10-08_uah_r1_domain_pack_second_review.md) | 0 BLOCKING; 0 NIT | APPROVE | `d39502b9b65e03051925eb4cfe1596bf7cf725dfeb3763b26f8fe56a6e35f462` |

Both reviewers addressed all five principles and independently confirmed the
public mutation rejection and unchanged valid identities. They compared exact
frozen-before bytes; the second reviewer also ran the native HEAD fixture and
confirmed the older defect. HEAD lacks the current ingress interface and uses
v1 artifacts, so that comparison is not v1/v2 byte parity. Their test counts
overlap the parent suite and must not be added together.

The [isolated repair patch](2026-10-08_uah_r1_domain_pack_identity.patch), SHA-256
`dbbfc419a070f36ae1fa774c0ad8b9a1765e4ce53c72de03dab7751b02db8ad5`,
preserves the complete three-file delta for later human review. Before-file
hashes are retained in both independent artifacts. Seven captured start files
changed as expected: the compiler/test, two canonical documents plus generated
HTML, and R0 report retention. `domain_contracts.py` was clean at the start and
is an additional deliberate change. Other captured start hashes match; HEAD,
branch and empty staging remain unchanged.
The [end manifest](2026-10-08_uah_r1_end.sha256) retains the final captured
dirty/untracked contents, excluding the manifest itself.

An explicit pre-commit run over the newly retained artifacts removed trailing
spaces from blank patch-context lines, initially returning a formatting failure.
That normalized patch then failed reverse validation with `corrupt patch at line
51`. The artifact was regenerated as a zero-context diff, which avoids those
whitespace-only context lines; the final hash is above. The command
`git apply --unidiff-zero --reverse --check` now passes without writing source.
No reviewed runtime bytes or independent reports changed. Artifact hook checks
were repeated after regeneration.

**Closure:** STD-01/SPEC-01's consumed-policy content-drift mechanism is repaired
at the compiler crossing for the reviewed bytes. This is not a claim that every
domain-pack consumer now revalidates or that arbitrary in-process mutation is
safe. The second reviewer observed that a tuple-to-list replacement with identical
JSON content is still accepted before/current/base. That pre-existing
representation-validation limitation is preserved as a separate gap, not hidden
by this content-identity fix. No follow-up correction was made.

## Residual mechanisms and next proposal

| Original IDs | Remaining mechanism |
| --- | --- |
| STD-02 | Outgoing Git coverage versus working-tree cache |
| STD-03, SPEC-04 | In-memory event integrity and its budget/O1 consequences |
| SPEC-02 | Raw-start ingress provenance bypass |
| SPEC-03 | Catalog semantics drift against the compiled projection |
| ARCH-01 | Prompt static eligibility differs from semantic admission |
| ARCH-02 | Unsupported O1 provenance labels |

The three original documentation/tooling NITs remain open. Subsequent repairs
require separate authorized batches. The next settled-invariant candidate is
catalog semantic fencing with an unchanged approved-binding control; ingress
provenance, O1 label response and outgoing-ref coverage still require their
explicit contract decisions. Evidence/freshness representation is not approved.

For later full-chain troubleshooting, reuse `synthetic_notes`, not a new general
frame. Compose environment registration/ingress, actor/fixed lease/readiness,
frozen prompt/invocation, the exact raw-output normalization, semantic/domain
gates, a real synthetic owner mutation and owner evidence, acceptance, restart
and digest. The existing actor example stops at raw output; it does not prove
that composed path. Bind parsing provenance and evidence validity under approved
contracts before claiming completion. A raw artifact ID alone does not prove
that parsed values came from the recorded output.

Both approved future providers (local Ollama with a cloud model and personal
Watson through ZeroTier) must use the same provider-neutral contract. Cloud
structured-schema support is not presumed. No provider was called and no
main-PC startup was requested. Model performance, live transport, full H0/H1
failure-suite closure and H2 NAO parity remain `not_scored`.

VERDICT: APPROVE
