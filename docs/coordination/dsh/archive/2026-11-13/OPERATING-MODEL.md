# Standing coordination: one human front door

## Intended user experience

Ask GRILL for work. GRILL records the mission, derives its bounded scope/budget from the request, dispatches to the actual role parents, gathers evidence and reports the result. The human should not renew messaging availability for every task, copy progress between chats, or maintain multiple synchronized boards. Scope expansion, destructive ambiguity, unavailable capabilities or exhausted work budgets return to the human as real decisions—not routine setup.

## Availability is not a work budget

**Standing availability** is permission to receive scoped GRILL missions until explicitly revoked. It has no per-mission clock. An idle receiver uses event-driven I/O, not a model heartbeat, scheduled polling or an endlessly continuing goal.

**A work mission** has its own task ID, allowed paths/actions, acceptance evidence, model/effort metadata, capacity and stop condition. Availability does not authorize unbounded work or bypass source, review, Git or runtime permissions. A deadline stops that mission, not future ability to receive missions. After cleanup, the parent rearms its receiver. Never run an expired mission merely because a registration says ACTIVE.

## Roles and teams

GRILL owns cross-role priorities, scope and acceptance. CREATOR owns DSH control/provisioning, independent-review integration and supported installation—not mandatory semantic relay. VISUALS owns Explorer presentation/build-validation work and actual visual QA. DEV and RESEARCH retain their distinct implementation/research branches. Every independently addressable role parent may own a local flat native Agent Team. Organizational hierarchy does not mean nested native Teams. Local Team target lead means that local parent, not necessarily GRILL.

Parents own their boards and integrate children. GRILL sees consolidated scope/dependency/outcome pointers, not duplicate copies of every local task. DEV/RESEARCH cross-branch contact remains forbidden; explicit DEV1/DEV2 exceptions do not widen scope or review authority.

## Message and evidence lifecycle

A mission moves through planned → dispatched → recipient ACK → running → result. File publication, accepted transport, ACK, task completion, source approval, installation and actual GUI acceptance are distinct evidence states. Inactive means no model turn is running, not task complete or an owner slot released.

The bootstrap channel uses immutable JSON plus a signal published last. Exact runtime sender/recipient, current mission scope and hash are checked by the parent; duplicates reuse recorded outcome and changed bytes conflict. The notification process does not execute task contents or confer authority. Receiver job IDs and actual ARMED output are recorded. Mark admitted bytes and rearm before long work; recover uncertain partial work rather than repeat effects.

## Current implementation and honest limits

Native Team creation, peer messaging, inactive-member wake and task CAS/dependency/advisory-scope behavior passed the local canary. The actual existing CREATOR also completed a bidirectional warm bootstrap file round-trip with GRILL. The plugin-first receiver now has CREATOR and VISUALS lanes; fixture tests are not substitutes for each actual registration ACK.

**The registered-role native dispatcher is not installed.** Its partial source remains private and unapproved. The current fallback depends on the Host and managed receivers running. A standing registration file is not proof of durable cold wake. Recovery after Host restart/unload, delayed notifications, model/effort routing and owned reviewer cancellation must be qualified; do not describe this as proven always-on infrastructure. No credential replay, log injection, forged human principal, preset/model-policy bypass or replacement server is an acceptable shortcut.

## Startup, steady state and recovery

1. GRILL arms its event receiver before the one-time role activation and records the actual job.
2. Each actual parent confirms its runtime identity, local Team, model/effort metadata, useful work goal and owned receiver; publishes ACK. A same-named substitute is not registration.
3. Thereafter GRILL sends finite missions; parents manage their own Teams and reply through the configured channel. No human forwarding per task.
4. On work completion/expiry, stop or collect owned children and effects, preserve evidence, close that work goal, and retain/rearm standing availability without an idle goal loop.
5. On Host restart, missing jobs or cold targets, mark availability UNVERIFIED until a supported recovery handshake proves it. GRILL owns recovery; do not silently claim delivery or ask the human to repeat all scopes. A one-time activation may remain necessary until native cold recovery is deployed.
6. Revocation closes receiving jobs and rejects new missions; it does not erase history.

## Storage, review and custody

Use verified writable `/data` for large private workspaces, caches and build outputs. Clean reviewer context does not require cloning every dependency tree. Keep exact source/dependency manifests, required baselines, genuine artifacts and recovery evidence. Inventory resolved ownership/references and verify migration hashes/origin/replay before removing originals. Never blanket-delete live dependencies, unique work or pinned review inputs.

Follow [REVIEW.md](<../../REVIEW.md>): fresh independent contexts, actual configured models/efforts or documented limitations, public controls and different-model second review for high-risk gates. Writer self-check is not approval. Human owns staging, commits, pushes, PR publication, merge and tags. No H/AB milestone or runtime effect follows from coordination status.

## Where to look

- [Current GRILL board](<grill.md>): brief owner-maintained status and next decisions.
- [Coordination index](<README.md>): policy/evidence boundaries and related records.
- [Historical evening handoff](<continuation-20261111-evening/README.md>): dated facts remain historical.

Concrete control paths, session IDs, current mission times and raw receipts stay on the owner-maintained operational base linked by the board. Product PRs exclude those transient boards/logs/workspaces unless a separately reviewed sanitized artifact is required.
