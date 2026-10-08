# R1 domain-pack identity: independent second review

Date: 2026-10-08. Review window began at 14:04 UTC. Scope: only the R1 delta in
`src/ab_harness/domain_contracts.py`, `src/ab_harness/task_compiler.py`, and
`tests/test_task_compiler.py`, compared with the supplied frozen-before files.
Pinned HEAD: `28fab5e7f2c244d86a64c371f2118017999b2387`.

Requested reviewer: `gpt-6-astra`, `max`, fresh context. The parent confirmed
those requested spawn settings and reported no fallback notification. Actual
deployment identity is not independently observable. This is the requested
distinct-model second review, rather than the default `gpt-6.1-sol` review.
No writer handoff, development log, or first-review content was read.

## Contract and predeclared probes

Read `REVIEW.md`, `AGENTS.md`, `CONTEXT.md`, relevant masterplan and foundation
sections, ADR 0001, and the code-review and UAH guardrail skills. The review
uses their standards/spec distinction and owner-boundary checks. No separate
originating issue was supplied; the governing contract is content-addressed
domain policy revalidation at task compilation. This is an H0-H1 trust-boundary
repair, not H2 runtime qualification. The domain owns policy; the pack owns
content identity; `TaskSpecCompiler` consumes the verified policy.

Before implementation reading, declared: valid single/multiple packs, reordered
inputs, empty/unknown selections, malformed identity/version/schema/type values,
forged or mutated nested contracts, mismatched domain/object identities, and
invalid selected versus unused content. Public signature inspection established
that compilation accepts one pack, so multiple-input checks used multiple rules
and allowlist entries. Units and date arithmetic are not changed by R1.

Executed the focused suite and the initial public compiler probes before reading
the implementation diff. Later probes extended the predeclared categories;
they are not represented as independently predeclared exact values.

## Frozen bytes

SHA-256 values were checked before and after behavioral execution and matched
the requested current hashes.

| File | Current | Frozen before |
| --- | --- | --- |
| `domain_contracts.py` | `b47e522c1184786170df1d9f3bbbfb7398c340e44a7b44a514312a8da17baf1c` | `566809c92677c9460b3bfb417d4dc4c0261fa26387be743ad1951659136691db` |
| `task_compiler.py` | `b11625e4cb5a64f74327e2112a6e182b48e45ce9821135a5af39a9f36f92e9bf` | `980619769fb323a7b8b810ee9befd4b905008a57c88d0730c0bbb7adc891a369` |
| `test_task_compiler.py` | `d847db50aa939c02b4e7190234b434fa7eccac3548c70a122aac1ab66ffe5b29` | `1af7195585fa03966f399994fab36856b3e81f5a9ce61d8e662a4e3be9ae1c3d` |

## Executed checks

1. `.venv/bin/python -m pytest -q tests/test_task_compiler.py`: expected pass;
   actual **34 passed**.
2. The same current test file with `PYTHONPATH` pointing to a throwaway copy of
   current `src` with both implementation files replaced by their frozen-before
   bytes: expected both R1 rejection cases to fail; actual **2 failed, 32 passed**.
   Both failures were `Failed: DID NOT RAISE ValueError`, for replacement and
   nested failure-policy mutation.
3. `.venv/bin/python -m pytest -q tests/test_task_compiler.py
   tests/test_environment_ingress.py tests/test_content_identity_compatibility.py
   tests/test_prompt_compiler.py tests/test_recorded_nao_qualification.py
   tests/test_two_stage_admission.py`: expected pass; actual **136 passed**.
4. `git diff --check -- src/ab_harness/domain_contracts.py
   src/ab_harness/task_compiler.py tests/test_task_compiler.py`: exit 0.
5. `.venv/bin/python scripts/render_agentic_harness_docs.py --check`: exit 0.

Inline Python public-seam probes loaded `_compiler_inputs`, `_reissue_domain`,
and `_use_domain` from the test fixture using `runpy.run_path`, then called
`TaskSpecCompiler().compile(**inputs)`. Every case obtained fresh inputs.
The frozen-before implementation used the same surrounding source and fixture,
isolating R1 from the wider dirty worktree.

For all rows marked identity rejection, current behavior was exactly
`ValueError: domain contract pack revision does not match content`.

| Input | Expected | Current | Frozen before |
| --- | --- | --- | --- |
| Unmodified fixture | Accept | Accept, unchanged hash | Accept, same hash |
| Pack ID changed to `domain-pack:forged` after issue | Reject | Identity rejection | Accept |
| Prohibitions replaced with `('forbidden_unrelated',)` after issue | Reject | Identity rejection | Accept |
| Nested evidence owner changed to `forged` | Reject | Identity rejection | `ValueError: domain evidence owner does not own AB object: find_object` |
| Nested ingress binding changed to `forged` | Reject | Identity rejection | Accept |
| Effect tuple replaced with a rule whose failure policy is `retryable` | Reject | Identity rejection | Accept; compiled obligation becomes retryable |
| Existing nested rule's failure policy mutated to `retryable` | Reject | Identity rejection | Accept; compiled obligation becomes retryable |
| Effect rules replaced with `()` | Reject | Identity rejection | `ValueError: requested effect has no domain rule: fresh detector-backed result returned` |
| Revision replaced with `sha256:` plus 64 zeroes | Reject | Identity rejection | `ValueError: ingress domain contract revision does not match` |
| Properly reissued pack adds `harmless_other` prohibition and re-admits ingress | Accept | Accept | Accept, same hash |
| Properly reissued retryable policy and re-admitted ingress | Accept retryable | Accept retryable | Accept retryable, same hash |
| Two roles and two prohibitions issued in both orders | Same revision | Equal | Equal |
| Duplicate `planner` role | Reject | `ValueError: duplicate domain roles: planner` | Same |
| Empty role tuple | Reject | `ValueError: domain contract pack requires an allowed role` | Same |
| Role list passed to issuance | Reject | `TypeError: domain contract collections must be tuples` | Same |
| Empty pack ID passed to issuance | Reject | `ValueError: domain contract pack fields must not be empty: domain_contract_pack_id` | Same |

The unchanged valid compiled-task ID was
`compiled-task:sha256:54b3dd46199545f76341b5c1dfaa69023a9147e5adc5c758515802aacfba9739`.
The properly reissued retryable control had ID
`compiled-task:sha256:ed4d7da2c00d03e3f452806a2cc99046ec4f63373a5cbf438c957eb885d31c8d`
on both current and frozen-before implementations.

An additional current-only control added a second, unused ingress binding,
`binding:unused`. Issuing its rules in opposite orders produced equal revisions;
compilation succeeded with ID
`compiled-task:sha256:55d3750ed61a00a7cd83c016bfa40f84f9a4b34bf7678a8f5a8032322980f83a`.
Mutating the unused rule's lineage key to `forged` then produced the exact identity
rejection. The new check therefore covers unused nested content too.

## Base-commit comparison and limitations

Extracted the pinned commit with `git archive` into a throwaway directory. Running
the current fixture there failed with `ImportError: cannot import name
'TaskIngressAuthority' from 'ab_harness'`; that API is absent from the commit.
Then ran the commit's own `_compiler_inputs()` and public compiler. The valid
control accepted with the v1 ID
`compiled-task:sha256:0e16a007b5d533505bded1f44b7125370c8ea3f0084f9b4c57fb8cc9d0c87af1`.
Both replacement and nested policy mutations also accepted and compiled
retryable obligations. This establishes the older behavioral defect, not v1/v2
artifact byte parity. Exact R1 byte-parity evidence comes from frozen-before.

A representation-only mutation, `object.__setattr__(pack, 'allowed_role_ids',
['planner'])`, was expected to fail immutable-collection validation but accepted
on current, frozen-before, and native base. Its JSON content and compiled hash
remain unchanged. It is a pre-existing representation-validation limitation,
not a newly introduced R1 content-identity defect. Arbitrary in-process monkey
patching and concurrent mutation after verification are not qualified here.

Not all predeclared malformed/schema/unknown-selection combinations were run.
The review was bounded to R1 and used no live provider or environment calls.
Only this review artifact was authored; no source, skill, hook, or Git mutation
command was used. Full pre-commit execution was
not performed by this reviewer because hooks may rewrite the shared worktree;
the focused tests and read-only checks above are the evidence actually obtained.

## Standards and design principles

1. **Separation of concerns: OK.** Identity verification remains in
   `src/ab_harness/domain_contracts.py:267`; the compiler only calls it at its
   trust crossing, `src/ab_harness/task_compiler.py:260`.
2. **Programming by intention: OK.** `verify_identity()` names the operation
   directly and preserves the existing mismatch error.
3. **Encapsulation: OK.** The compiler neither reimplements the hash nor reaches
   into payload construction internals.
4. **High cohesion: OK.** Construction and later trust crossings share the same
   pack-owned identity calculation; the delta has one purpose.
5. **Low coupling: OK.** No runtime/provider dependency or new owner was added.
   Semantic admission, execution, and evidence ownership remain distinct.

## Spec and findings

The R1 repair rejects covered-content drift before compiler consumption while
preserving valid construction, serialization-derived identities, and properly
reissued policy behavior. No duplicated owner or policy logic was introduced.

Findings in the reviewed R1 delta: **0 BLOCKING, 0 NIT**. The representation-only
limitation above is explicitly outside the newly introduced change and is not
counted as an R1 finding. No additional H0-H2 closure claim is warranted.

VERDICT: APPROVE
