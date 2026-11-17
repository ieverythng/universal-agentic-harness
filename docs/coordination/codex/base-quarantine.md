# Base branch recovery and residual routing

Snapshot: 3 November 2026. Owner: GRILL. This document records coordination
custody and candidate routing, not implementation approval or release closure.

## Current base policy

The human authorized reconciling `feat/base-implementation-H0` with merged
`main` while preserving its dirty state privately. Future product changes live
in their scoped PR branches/worktrees. This base retains owner boards and
existing operator guidance under `.codex/skills/` and the review-workflow note.
Those retained instructions do not become runtime policy or a product PR.

GRILL may checkpoint and push coordination history on this branch. The human
continues to own product publication, main merges and release tags. Do not
restore an old index into the live checkout or copy the complete quarantine
into main. A historical APPROVE applies only to its exact reviewed bytes.

## Recoverable pre-cleanup state

Private recovery root:
`/home/juanbeck/uah-experiments/checkpoint-20261103/grill/base-before-cleanup/`.

- `freeze.json`: exact original branch/HEAD, file hashes/modes and ignored inventory.
- `working-files.tar.gz`: original tracked/untracked working files.
- `index.before` and `index-entries.z`: original staged state, distinct from working bytes.
- `staged.patch`, `unstaged.patch`, `working.patch`: binary-capable changes.
- `branch-history.bundle`: original committed branch ancestry.
- `required-ignored-supplement.tar.gz` and JSON: six historical JSONL artifacts.

Readable recovered files are under sibling
`quarantine/working-tree/`. They are private, unreviewed integration inputs;
archives and probes are not product dependencies. Virtual environments, caches,
credentials and existing ignored local artifacts are not cleanup targets.
The original No-Mistakes run remains parked and untouched. Its 30 already
committed pilot-evidence files remain in place as base-only historical custody.
Seven unpublished checkpoint-native receipts remain in place and untracked;
they are excluded from publication and must not be included by a blanket add.

The cleanup transaction and exact retained paths are recorded in sibling
`base-reconciliation.json`. If adoption is interrupted, consult its journal
before further Git writes; do not improvise a reset. Its target product tree
must equal the verified merged-main tree, apart from explicitly retained
coordination/operator files. It closes no H gate and does not rerun main CI.

## Residual dispositions

DEV1 owns the exact per-path manifest and review provenance under
`/home/juanbeck/uah-experiments/checkpoint-20261103/dev1/`.

| Residual | Route |
| --- | --- |
| Bytes already in PR1/main | Use main; retain original only as recovery evidence. |
| Older lifecycle, prompt and admission/test variants | Superseded quarantine; never overwrite newer main. |
| Synthetic package additions | Deferred candidate for SPR-01/06 evaluation after source closure; no automatic promotion. |
| Historical fixtures, replay and contract notes | SPR-01/02 evidence; verify authentic sources and current interfaces first. |
| History/context/evidence and activation notes | SPR-03/04/05 candidate inputs; current-task original evidence and owner gates remain. |
| Conformance and ablation plans | SPR-06; proposed experiments are not executed results. |
| NAO parity and native integration notes | SPR-07 Python H2, SPR-08 native H2.1; separate qualification gates. |
| Workbench/interpretability/adaptation notes | SPR-10 then SPR-09, with H3/H4 quarantine and source/version distinctions. |
| Old probe archives, raw review logs and unrelated GTM artifacts | Private historical quarantine; excluded from product PRs. |

Existing sprint planning worktrees contain old source bases and local planning
files. Preserve them, refreeze against the actual merged destination before
implementation, and require a finite dispatch and exact review. A missing
remote PR or blocked predecessor must remain explicit. No new source sprint
is dispatched by this custody cleanup.

## Product delivery location

The masterplan viewer belongs to `codex/uah-pr2-docs` in
`/home/juanbeck/.codex/worktrees/uah-pr2-docs/universal-agentic-harness`.
During development its candidate/review receipts are private. Only exact fresh
approval permits a collision-safe unstaged transfer. Human commit `d97fadd`
changes `uv.lock`; preserve it. PR1 is merged; PR2 publication/merge and H0-H2
qualification remain distinct decisions.
