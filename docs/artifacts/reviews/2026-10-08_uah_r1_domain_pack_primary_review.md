# R1 domain-pack independent review

Review began 2026-10-08 14:04:16 UTC and concluded before 14:10:16 UTC. Parent confirmed the spawn requested `gpt-6.1-sol` at `max`, with no fallback notification received. Actual deployment identity is not independently observable to this reviewer. The reviewer did not write the implementation.

## Scope and frozen baseline

Only the R1 delta in `src/ab_harness/domain_contracts.py`, `src/ab_harness/task_compiler.py`, and `tests/test_task_compiler.py`, against `/tmp/uah-r1-domain-pack-20261008/*.before`, is in scope. HEAD is `28fab5e7f2c244d86a64c371f2118017999b2387`, but HEAD is not the behavioral baseline. Existing dirty-tree changes are excluded. No writer handoff or logs are read.

## Probes declared before implementation reading

1. Exercise a valid public domain-pack/compiler control and compare it with exact frozen-before bytes; if the old public API cannot express a new input, report it as unavailable parity, not a pass.
2. Exercise empty, one-entry, and multiple-entry packs, reversing multi-entry order. Cover duplicate identities and conflicting definitions where expressible.
3. Alter a claimed/content-addressed domain-pack identity and nested catalog identity before the compiler trust crossing. Expect typed rejection and no compiled authority artifact. Retain an unaltered valid control.
4. Supply definitions with unknown or mismatched resources, operations, frames, and owners; combine two invalid forms to establish rejection priority. Expect deterministic errors, no invented defaults, and no authority expansion.
5. Check equivalent alternative public forms of the same pack input, including omitted and explicit optional pack selection; the compiled snapshot and identity must agree where semantics agree, and remain distinct where provenance changes.
6. Execute the changed public seam and focused compiler tests. Report exact observed outcomes and errors, plus all five REVIEW.md design principles.

Architecture scope: H1/H2 contract qualification, not physical execution or release promotion. Environment/domain owners retain effect and execution authority; packs may carry definitions, not create authority.

## Reviewed bytes

| File | Current SHA-256 | Frozen-before SHA-256 |
| --- | --- | --- |
| `domain_contracts.py` | `b47e522c1184786170df1d9f3bbbfb7398c340e44a7b44a514312a8da17baf1c` | `566809c92677c9460b3bfb417d4dc4c0261fa26387be743ad1951659136691db` |
| `task_compiler.py` | `b11625e4cb5a64f74327e2112a6e182b48e45ce9821135a5af39a9f36f92e9bf` | `980619769fb323a7b8b810ee9befd4b905008a57c88d0730c0bbb7adc891a369` |
| `test_task_compiler.py` | `d847db50aa939c02b4e7190234b434fa7eccac3548c70a122aac1ab66ffe5b29` | `1af7195585fa03966f399994fab36856b3e81f5a9ce61d8e662a4e3be9ae1c3d` |

The delta extracts the existing revision comparison into `DomainContractPack.verify_identity()`, calls it at compiler ingress, and adds two regression cases. Current hashes were rechecked after execution. Standards and R1 behavior were assessed locally within this fresh review, without further delegation or access to writer reasoning. The development log was deliberately not read under the assigned no-logs restriction.

## Execution evidence

The probes were declared in this artifact before implementation reading. The initial black-box pass preceded reading the three diffs. The authoritative comparison then used isolated Python subprocesses for `before` and `current`. For `before`, `SourceFileLoader` loaded the exact frozen domain/compiler bytes under their original module names and updated `ab_harness` exports before loading the frozen test fixture. Other repository modules stayed at the same current dirty-tree state in both subprocesses. No HEAD reconstruction was substituted for this comparison.

Each compiler probe starts with `_compiler_inputs()` and calls public `TaskSpecCompiler().compile(**inputs)`. Tampering uses `object.__setattr__` after valid issuance, leaving the original revision and ledger-recorded ingress intact. Valid changed-policy controls use `_reissue_domain()` and `_use_domain()` to create a new revision and matching ledger-backed start.

| Input | Expected current result | Exact frozen-before result | Current actual result |
| --- | --- | --- | --- |
| Untouched fixture | Compile unchanged | Accepted, ID `compiled-task:sha256:54b3dd46199545f76341b5c1dfaa69023a9147e5adc5c758515802aacfba9739`, terminal policy | Same ID and policy |
| Replace `effect_rules` with a rule whose policy is `retryable` | Reject stale revision | Accepted, retryable policy under original revision | `ValueError: domain contract pack revision does not match content` |
| Mutate nested `effect_rules[0].failure_policy` to `retryable` | Reject stale revision | Accepted, retryable policy under original revision | Same revision-mismatch error |
| Remove pack prohibitions | Reject stale revision | Accepted, compiled prohibitions narrowed to `('direct_speech',)` | Same revision-mismatch error |
| Change pack ID to `domain-pack:other` | Reject stale revision | Accepted under original revision | Same revision-mismatch error |
| Change frame to `other_frame` | Reject | `ValueError: domain contract frame does not match compiler frame` | Revision-mismatch error takes precedence |
| Change registry revision to `sha256:` plus 64 zeros | Reject | `ValueError: domain contract registry version does not match` | Revision-mismatch error takes precedence |
| Combine unknown object `unknown` and owner `other` in a replacement rule | Reject | `ValueError: unknown AB object: unknown` | Revision-mismatch error takes precedence |
| Freshly issue retryable policy and matching ingress | Compile new revision | Accepted, ID `compiled-task:sha256:ed4d7da2c00d03e3f452806a2cc99046ec4f63373a5cbf438c957eb885d31c8d` | Same ID, revision and retryable policy |
| Two rules, original plus `unused effect`, in both orders | Canonical equivalent result | Both accepted with ID `compiled-task:sha256:50a65ae217a18c3f5c551ed11ac9da1719804272d845bcfa6d39c14fb3b129b5` | Same IDs in both orders |
| Issue empty ingress rules | Reject | `ValueError: domain contract pack requires an ingress rule` | Same error |
| Issue empty effect rules | Reject | `ValueError: domain contract pack requires an effect rule` | Same error |
| Duplicate original effect rule | Reject ambiguity | `ValueError: duplicate domain effect rules: fresh detector-backed result returned` | Same error |
| Issue mutable role list | Reject mutable input | `TypeError: domain contract collections must be tuples` | Same error |
| Direct valid constructor versus `issue()` | Equivalent identity | Same valid revision | Same valid revision |
| Call public `verify_identity()` | Validate current valid pack | `AttributeError` because the method does not exist | Returns `None`; baseline method parity is unavailable, not passed |

Additional current-only controls: omitted versus explicit empty `prohibited_effects` both produced `sha256:340241d2bf1cacc9e8a36bf3e915c4814c85efe6679c1f26f98f0be49767a78b`; omitting the required compiler pack produced `TypeError: TaskSpecCompiler.compile() missing 1 required keyword-only argument: 'domain_contract_pack'`. These are not claimed as frozen-before comparisons.

An exploratory harness invocation failed before executing because its driver omitted `import sys`; it was corrected and rerun successfully. That failed invocation supplies no behavioral evidence. The authoritative isolated subprocesses both exited 0 with empty stderr.

Commands executed: `.venv/bin/pytest -q tests/test_task_compiler.py` (34 passed in 0.11 seconds); `.venv/bin/python scripts/render_agentic_harness_docs.py --check` (exit 0); `git diff --check` restricted to the three scope files and this artifact (exit 0); read-only `sha256sum`, `git rev-parse HEAD`, and `diff -u` against the frozen files. Python probes used `.venv/bin/python` with inline scripts. No provider invocation, Git mutation, hook installation, or source edit occurred.

## Design principles

1. Separation of concerns: OK. The pack owns content identity; the compiler consumes that public verifier before deriving task scope (`domain_contracts.py:268`, `task_compiler.py:260`).
2. Programming by intention: OK. `verify_identity()` and its trust-crossing call express the rejection requirement directly.
3. Encapsulation: OK. The compiler does not reproduce the pack payload or hash algorithm.
4. High cohesion: OK. Identity validation remains in the domain contract artifact, using the existing canonical payload.
5. Low coupling: OK. The change adds one public portable contract call and no provider, runtime, ROS, or NAO dependency.

Standards axis: no in-scope violations or actionable smells. R1 behavior axis: no in-scope violation. The regression fixtures exercise both replacement and nested valid-policy mutation; independent controls additionally cover authority narrowing and provenance changes. The identity mismatch remains an exception from the public compiler, with the exact message recorded above; this delta adds no reason-code enum or UI renderer.

## Findings and limitations

No BLOCKING or NIT findings were discovered in this three-file R1 delta (0 findings, so no numbered finding entries). The wider dirty-tree changes, other trust crossings, concurrent mutation during compilation, and full release qualification were not reviewed. The full repository hook suite was not rerun by this reviewer. No live owner/effect, model, NAO parity, or H2 release claim follows from these probes. Unit/date variants are inapplicable to the changed pack verifier, which has no corresponding fields. This review establishes the compiler's stale-content rejection only, not that every domain-pack consumer now reverifies identity.

VERDICT: APPROVE
