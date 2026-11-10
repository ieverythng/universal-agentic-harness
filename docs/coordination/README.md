# Chat coordination and evidence boundaries

GRILL is the sole cross-chat orchestrator and decision boundary. It dispatches
finite scopes to DEV and RESEARCH and owns priorities. DEV and RESEARCH remain
separate branches: their parents consolidate outcomes, requests, and blockers
through GRILL rather than contacting each other.

DEV1 and DEV2 may exchange narrowly scoped technical handoff only when GRILL
explicitly authorizes it for a particular integration pilot. That exception
does not permit DEV/RESEARCH peer messaging, transfer review authority, or
expand the active scope.

## Persistent coordination records

GRILL, DEV, and RESEARCH maintain separate owner-written coordination boards on
their persistent coordination base. This product repository contains the
coordination policy only; parent boards, transient logs, raw probe output, and
review workspaces are not copied into product PRs. A board records its scope,
owner, frozen branch or snapshot, time bound, evidence, gate state, next action,
and exact decision needed. Board writes do not wake another chat or grant
runtime, review, Git, or release authority.

## Product PR workflow

Product PRs target `main` from dedicated managed branch worktrees. Historical
implementation branches are evidence sources, not PR bases. After the exact
candidate passes its mechanical gates and fresh independent review, the
approved handoff stays unstaged in the PR worktree for the human to stage and
commit. The human owns push, PR publication, merge, and tags. Temporary PR
branches/worktrees are removed only after the human confirms merge.

## Release-label map

The human-selected planning map is migration/development `v0.1`, H0 `v0.2`,
H1/O1 `v0.3`–`v0.4`, Python NAO H2 `v0.5`, native H2.1 `v0.6`,
H3 `v0.7` through `v1.0`, and H4 `v1.5` (D-20261017-07). H5+ versions
remain unassigned. These labels are not release qualifications. A merge does not
close a milestone, and a tag may be created only on the exact human-selected
committed release after its required gates pass. No tag is created by this
workflow.

The repository's [REVIEW.md](../../REVIEW.md) remains the independent-review
contract. Research proposals, exact reviewed bytes, validation results, staged
files, and release qualification are separate states. Missing evidence cannot
close a gate.

## Orca coordination and SPR-11

The human-designated Orca GRILL thread owns [its current board](orca.md) on
`coordination/orca` in an independent checkout. The retained role boards are
snapshots; their historical active headings do not dispatch work. Each new
branch parent owns its board and reports to GRILL; peers do not edit it.
[SPR-11](sprints/SPR-11-state-machines.md) audits implicit state machines and
routes overlap to SPR-01..10. Discovery can proceed before PR2 merges; product
implementation still requires verified merged PR2, a fresh main base and finite
GRILL dispatch. Coordination commit/push authority is specific to this branch;
sprint/product staging and commits remain human-owned.
