# Selected agent checkpoint: dependency requirements

Date: 2026-10-08. Owner: DEV. Scope: CHECKPOINT-COMMIT-02.

## Outcome

No shared files were staged or committed. The exact human selection cannot pass
normal hooks against its parent revision. Nine additional source changes are
required by the tested whole-file candidate, and several are explicitly
unchecked. Request `CHECKPOINT-02-GAP` on the DEV board asks GRILL to obtain
their explicit disposition before staging. This checkpoint is permitted with
recorded CHECK debt; known review findings are not used to revoke that permission.

The shared branch remains `feat/pre-commit-queue` at
`06f5a29daef9bb877fb08b6c6ee47d870df94d71`. The original thirteen-path staged
binary diff remains SHA256
`af6bd13cf5b51420cdb078b8427cd2e472dfa2de0c6c9f35f78ab2e04123a77f`.
Observatory INDEX bytes remain distinct from its unstaged ARCH-02 label repair.
No changes were made to runtime code, the published WIP branch, or any remote.

## Exact candidate boundary

The restricted candidate contains 37 changed paths: eighteen selected
source/script/document paths, seventeen matching tests and two generated pages.
The diagnostic dependency-complete candidate contains 46 changed paths. These
are prospective Git trees in independent copies, not shared commits:

| Candidate | Prospective tree | Result |
| --- | --- | --- |
| Restricted selection | `ab4fb89039419635bac8ec6bb35a536c5a92baae` | Normal hooks fail: 23 test-collection errors |
| Selection plus nine dependencies | `32ce94cda61d47119583993b810391f976a9b2d0` | 445 tests pass; normal all-files hooks pass |

Both execute their own `src` using `PYTHONPATH=src`, with the existing interpreter
selected explicitly. The editable installation cannot supply missing modules
from the shared checkout. Interpreter links are execution aids, not tracked
candidate files. One diagnostic setup attempt failed to copy files; it did not
change the shared tree. The restricted candidate was then reconstructed and
the exact 37-path check repeated. Only the final manifest-bound results above
are decision-bearing.

### Selected paths

```text
docs/artifacts/research/2026-10-08_uah_arch02_and_nao_first_seam_handoff.md
scripts/render_agent_runtime_example.py
scripts/render_agentic_harness_docs.py
scripts/render_observatory_example.py
scripts/render_research_dashboard.py
src/ab_harness/__init__.py
src/ab_harness/agent_configuration.py
src/ab_harness/agent_identity.py
src/ab_harness/agent_lifecycle.py
src/ab_harness/domain_contracts.py
src/ab_harness/lifecycle.py
src/ab_harness/model_allocator.py
src/ab_harness/observatory.py
src/ab_harness/model_invocation.py
src/ab_harness/operation_edges.py
src/ab_harness/schema_validation.py
src/ab_harness/task_compiler.py
src/ab_harness/task_registry.py
```

The first thirteen use the actual INDEX snapshot. The remaining five use the
new screenshot selections and explicit model_invocation.py CHECK designation.

### Required additional source changes

Each omission restores that file to the parent revision, or removes it when it
did not exist there. Every one of the nine omission probes fails collection.
This establishes a tested whole-file dependency set, not a mathematical claim
that no smaller hunk-level refactor could exist.

| Additional path | Omission failure | Coupling |
| --- | --- | --- |
| `src/ab_harness/prompt_compiler.py` | Missing `ab_harness.prompt_compiler` | Selected invocation port and package exports import the compiled prompt |
| `src/ab_harness/runtime_controls.py` | Missing `ab_harness.runtime_controls` | Package exports, invocation accounting and lifecycle facts |
| `src/ab_harness/task_ingress_authority.py` | Missing `ab_harness.task_ingress_authority` | Package exports, task-start authority and selected runtime renderer |
| `src/ab_harness/environment_ingress.py` | Baseline imports removed `DuplicateEnvironmentIngressError` | Selected registry and compiler use the revised ingress contract |
| `src/ab_harness/proposal_admission.py` | Missing `ProposalNormalizationRejection` export | Selected exports and lifecycle serialization/replay |
| `src/ab_harness/domain_lifecycle.py` | Missing `DomainAdmissionRejection` export | Selected exports and lifecycle lease/rejection facts |
| `src/ab_harness/environment.py` | Missing `EvidenceDecision` export | Selected exports and execution/evidence facts |
| `src/ab_harness_nao/qualification.py` | Baseline imports removed `TaskIngressPolicy` | NAO fixture consumes the revised ingress and execution contracts |
| `src/ab_harness_nao/smoke.py` | Missing `record_smoke_run` export | Selected Observatory renderer and migrated NAO canary tests |

The NAO pair is a fixture/renderer consumer dependency. It is not a proposal
to move NAO interfaces into the portable kernel. Omitting those renderers and
separating combined modules would change the requested checkpoint boundary and
requires another scoped split, rather than an implicit edit here.

### Matching tests

```text
tests/test_agent_configuration.py
tests/test_agent_identity.py
tests/test_agent_runtime.py
tests/test_agent_runtime_example.py
tests/test_lifecycle_ledger.py
tests/test_observatory.py
tests/test_observatory_raw_identity.py
tests/test_observatory_format.py
tests/test_research_dashboard.py
tests/test_environment_ingress.py
tests/test_task_compiler.py
tests/test_two_stage_admission.py
tests/test_model_invocation.py
tests/test_prompt_compiler.py
tests/test_cli_smoke.py
tests/test_recorded_nao_qualification.py
tests/test_argument_schema_validation.py
```

Argument-schema tests now match an explicitly selected source file. Existing
ingress, compiler, admission and NAO tests carry necessary fixture migrations.
The generated counterparts are `docs/artifacts/observatory/o1_h1_agent_lifecycle.html`
and `docs/artifacts/observatory/o1_recorded_nao_canary.html`.

Five further tests are recommended authority regressions, not requirements
proven necessary for this normal-hook candidate:

```text
tests/test_admission_active_provenance.py
tests/test_admitted_object_snapshot.py
tests/test_content_identity_compatibility.py
tests/test_nested_admission_owner.py
tests/test_runtime_budget_contracts.py
```

Synthetic code/tests, uv.lock, canonical-document changes and unrelated research
notes remain outside the checkpoint. None has been added to the shared index.

## Requested message

Preserve the following paragraphs verbatim through a message file if the
dependency disposition permits a normal-hook-passing checkpoint:

```text
feat(Agent roles): Model agnostic agent role config, registration preflight

feat(Agent identity): Complete agent composition of role, model, prompt, build, revision of settled agent handle

feat(agent lifecycle): Agent run coupled to manifest and known handle, replay and lifecycle semantics

feat(domain): explicit rejection logic for env and trace creation

feat(model lease): model lease logic, preflight, instance config agnostic to agent identity, run, role

CHECK: lifecycle.py, model_invocation.py, observatory.py, operation_edges.py
```

## Retained review debt

Both independent reviewers returned CHANGES. Their reports and public
counterexamples are retained in the [pilot evidence](2026-10-08_uah_no_mistakes_pilot_evidence/).
The [pilot handoff](2026-10-08_uah_no_mistakes_pilot.md) records the actual tool
evaluation, which failed at its eight-minute Review invocation budget without
a structured verdict. Passing local tests does not supersede these results.

- STD-PILOT-01: introduced prompt-subclass invocation/provenance mismatch.
- STD-PILOT-02 / SPEC-PILOT-01: introduced non-boolean argument-schema policy.
- SPEC-PILOT-03: introduced rejection of genuine historical compiled-task replay.
- SPEC-PILOT-02: historical resume/notify ingress-authority debt.
- SPEC-PILOT-04: repeated budget-unit type consistency, without demonstrated
  additional debit.
- ARCH-02: unstaged Observatory label repair lacks final independent approval.

H0/H1/O1 exits remain open. This scope tests checkpoint dependencies; it does
not qualify a provider, H2 parity, or release closure.

## Successor No-Mistakes plan (not launched)

One isolated successor run, total envelope at most 45 minutes including setup,
all phases, custody recovery and handoff. Review receives an actual 25-minute
invocation budget. Set both global `review_agent_timeout: 25m` and
`review_agent_working_timeout: 25m`, verified against the pinned v1.91.0 parser;
these settings are not repository YAML controls. Client `--wait` is only a
bounded observation hold, never the agent budget.

1. Resolve CHECKPOINT-02-GAP. Bind the permitted commit or rejected-checkpoint
   snapshot by full parent, tree, path manifest and byte hashes. Do not run
   against mutable dirty-tree contents or change the immutable published WIP.
2. Provisional target: the nine unchecked dependencies plus four CHECK modules,
   their matching tests and the five additional authority regressions. Reviewed
   agent/configuration files and other selected modules supply context. Any
   remaining ARCH-02 repair is a separate byte-bound gate. Synthetic work and
   unrelated documents are excluded unless explicitly assigned.
3. Use a fresh independent clone and isolated local origin. Do not run upstream
   init in the attached linked worktree, because it resolves the common Git root.
   Reuse the pinned tool, but create fresh state, control wrappers and deadlines;
   the prior wrapper deadline has expired. Capture a clean user-owned custody
   receipt before submission.
4. Keep zero automatic repair budgets, cold sessions, no unattended approval,
   explicit native sandbox and trusted local test/lint commands. Document phase
   mutations may occur only within its isolated tool-owned lane and must be
   reported. Skip remote push, PR and CI; do not call this publication validation.
5. Verify the native backend's internal delegation control before launch.
   The earlier top-level launch cap did not bound its five internal rollout
   sessions. If internal delegation cannot be bounded and attested, return that
   concrete gap rather than claiming a token or agent-spend cap. Wall-clock and
   top-level launch caps remain separate controls.
6. Stop at the first actionable or ask-user gate. No source repair, approval
   override, retry or second run is implicit. Preserve exact phase output,
   model/session metadata, tests and structured branch_sync custody. Report
   missing phases if the total bound is reached.

The human has already authorized a larger review budget. The unresolved inputs
are the concrete target/custody and excluded dependency disposition, not an
abstract request for more time.

## Evidence

[Checkpoint evidence](2026-10-08_uah_checkpoint_commit_evidence/) contains both
manifests, byte hashes and index modes, prospective tree hashes, normal-hook
logs, the complete test receipt and nine independent omission logs. Every one
of the 46 candidate files is byte-identical to its counterpart in the immutable
published WIP commit `f85ae715669379a428e063d0c965e42e78b3ae3f`. That commit
already preserves the source, so this handoff does not duplicate its large
patch. The recorded prospective trees differ in selected paths, not new source
repairs. The DEV board owns the current decision request. These artifacts
remain uncommitted for human review.
