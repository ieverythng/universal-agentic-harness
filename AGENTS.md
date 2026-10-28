# Agent Guide

Universal Agentic Harness is a portable Python package. Preserve these
boundaries:

- `src/ab_harness` must not import ROS, NAO packages, provider SDKs, or runtime
  products.
- Models propose typed operations; deterministic gates and environment owners
  decide whether they execute and what effects are proven.
- AB coordinates are frame-relative. Do not present an AB level as a global
  capability or intelligence score.
- Runtime discovery is not authorization or evidence.
- Keep H0 implementation claims distinct from the H1-H6 roadmap.
- Any adaptive or learned structure remains quarantined until replay,
  counterexample, holdout, owner-review, provenance, and rollback gates pass.

Run `./scripts/setup_dev_tools.sh` once, then `./scripts/run_precommit.sh` for
source or documentation changes. The hook suite runs Ruff, source-aware tests,
repository hygiene, and `python scripts/render_agentic_harness_docs.py --check`.
Generated HTML and Markdown documents must remain synchronized.

## Chat coordination and delegation

- GRILL is the sole cross-chat orchestration and decision boundary. It owns
  grilling, priorities and scoped dispatch, and synthesizes research into one
  finite DEV scope at a time.
- Product PRs target `main` from a dedicated managed branch/worktree. Historical
  implementation branches remain evidence sources, not product integration
  bases.
- DEV owns implementation and independent-review coordination. RESEARCH owns
  source investigation, experiments, evaluation and proposals. These chat roles
  confer no runtime authority; direct human instructions retain their authority.
- DEV and RESEARCH, including their descendants, must not message or delegate
  work directly across their branches. Route cross-branch coordination through
  the branch parent and GRILL.
- At the human's request, DEV1 and DEV2 may exchange technical dependencies and
  handoffs within their GRILL-assigned scopes. This does not expand either
  scope or deadline, relax the DEV/RESEARCH boundary, or confer review authority.
- Encourage useful communication and delegation within each branch. Authorized
  subagents may delegate further within bounded scopes and available capacity.
  Assign clear ownership; parents integrate child outcomes and remain accountable.
- Delegated tasks carry their scope, governing contract, evidence references,
  non-goals and budget or stop condition. New decisions and dependencies return
  upward rather than expanding another branch's work.
- GRILL sends scoped task instructions to branch parents. Record consolidated
  outcomes, requests and blockers on the coordination board, not in unsolicited
  messages to GRILL. Descendants report to their parent;
  branch parents own their board files. Board writes do not wake GRILL, and
  elapsed time grants no permission. Keep routine probe updates local.
- Coordination boards and research records persist on their owner-maintained
  base. Product PRs exclude parent boards, coordination logs, and transient
  probe archives unless a separately reviewed, sanitized artifact is needed.
- Record the actual writer model/effort in each bounded scope. The current app
  catalog supports `gpt-6-luna` through `max`, not `xhigh`; do not report an
  unsupported effort as selected.
- Preserve fresh-review independence and [REVIEW.md](REVIEW.md). Independent
  reviewers receive no writer history; delegation does not relax existing gates.
- The human owns staging, commits, pushes, PR publication, merge, and tags. Do
  not perform them without explicit authorization. Delete a temporary PR
  branch/worktree only after the human confirms its PR merged.

## Reviewed handoff and PR integration

- Keep development history on branch-owned private work. After exact independent
  approval, transfer only the reviewed unit and its required tests and
  documentation into the dedicated PR worktree, unstaged for the human's
  commit. Record its source revision or patch hash, exact path/dependency
  manifest, review IDs and verdicts, and validation evidence.
- Before each destination write, verify the PR worktree path has its recorded
  base bytes or is absent as expected. Stop on any dirty or staged collision
  and preserve the human's content.
- Private setup must use an independent Git common directory or proven
  hook-local isolation. Never install or uninstall hooks through a worktree
  that shares the human checkout's Git metadata.

This is an organizational task tree. The binary-tree analogy imposes no fixed
branching count, AB level, context-store implementation or new runtime component.
