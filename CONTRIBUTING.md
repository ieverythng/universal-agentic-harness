# Contributing

This guide complements the repository's `AGENTS.md` and `REVIEW.md`. Current
publication state is recorded in the [PR delivery status](docs/plans/pr-delivery-status.md).

## Ownership and coordination

- The human owns staging, commits, pushes, pull requests, merges, and release
  tags.
- GRILL owns cross-chat orchestration, priorities, and finite scope assignment.
  DEV and RESEARCH remain separate branches. DEV1 and DEV2 may exchange
  technical evidence only within a scope that explicitly permits it.
- RESEARCH owns investigation, experiments, evaluation, and proposals. A
  proposal does not authorize implementation or change release qualification.
- Models may propose typed operations. Deterministic gates and environment
  owners decide admission, execution, and effect evidence.

## Branch and pull request flow

1. Start product branches from the current `main`. If a change depends on an
   unmerged pull request, identify the exact prospective commit and keep the
   result conditional. After that pull request merges, verify the actual `main`,
   rebase, refreeze affected files, and repeat the required checks and review.
2. Keep each pull request within its assigned scope. Record the exact source,
   base, and path manifest; exclude unrelated worktree and coordination-board
   changes.
3. Keep local checks, independent review, hosted CI, merge, and milestone state
   separate. Required hosted checks must pass for the current pull request
   candidate. A local result does not establish hosted CI or merge readiness.
4. Follow `REVIEW.md`. Reviewers assess the same frozen bytes and report the
   requested model and effort, exact review-unit identity, evidence, and
   verdict. Changes after review require a fresh review of the changed unit.
5. Transfer only the exact approved manifest after checking that each
   destination path has its recorded base bytes or is absent as expected. Keep
   the delivered files unstaged for the human unless the human explicitly
   authorizes staging.
6. The human performs commit, push, pull-request publication, merge, and
   tagging. Remove a temporary branch or worktree only after the human confirms
   merge and custody of the reviewed work.

## Worktree and board custody

- Use an independent Git common directory for private validation. Do not
  install or remove hooks through a worktree that shares the human checkout's
  Git metadata.
- Coordination boards are owner-maintained records. Keep them outside product
  manifests and indexes, and leave them unstaged in the persistent base.
- GRILL may commit and push reviewed board and related history updates to the
  designated base branch only when explicitly authorized by the human. This
  narrow authority does not cover product changes, PR publication, merges, or tags.
- Stop before a destination write if any selected path differs from its
  recorded bytes. Preserve the existing content and report the collision.

## Local checks and hosted CI

The current pre-commit configuration runs repository hygiene checks, Ruff,
source-aware tests, and generated-document synchronization. The current
pre-push guard also requires a recorded successful local pre-commit state for
the outgoing branch tip. These local hooks remain active and provide feedback.
The required hosted test jobs (`test (3.10)`, `test (3.12)`, and `test (3.13)`)
are the merge gate for the pull request; local cache state is not hosted CI.

Evaluating whether to remove the custom pre-push cache requirement is a
separate workflow change. It needs a scoped before-and-after check showing that
required CI blocks a failing change and ordinary changes do not depend on stale
local cache state. This documentation does not remove or change a hook, cache,
CI workflow, or repository policy.

GitHub pre-fills new pull request descriptions from
`.github/PULL_REQUEST_TEMPLATE.md` after that file is available on the default
branch. The template is a static scaffold; it does not run checks, create
visuals, or claim that a gate passed.
