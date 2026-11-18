# Coordination: Codex and DSH

This is the shared front door for two continuing coordination namespaces:

| Namespace | Start here | Ownership |
| --- | --- | --- |
| Codex | [Existing Codex guide](<codex/README.md>) | Codex branch parents continue their owner-written boards. |
| DeepSeek Harness (DSH) | [Current DSH guide](<dsh/README.md>) | This GRILL coordinates registered independent role sessions and their local Teams. |

For another DSH instance or project, start with the standalone [DSH coordination bootstrap](<dsh/DSH-COORDINATION-BOOTSTRAP.md>): reviewed source retrieval, private local bindings, supported installation, verification and rollback. The [repository methodology](<dsh/METHODOLOGY.md>) applies that generic workflow here. Setup still requires owner-approved local inputs; neither document authorizes arbitrary session creation or installation.

## Shared rules

- GRILL is the cross-chat priority, decision and scoped-dispatch boundary. It integrates parent outcomes into finite work; a role name conveys no runtime authority.
- DEV and RESEARCH remain separate branches. Cross-branch requests return through their parents and GRILL. DEV1/DEV2 technical handoff requires the human-authorized scoped exception; it does not widen work or confer review authority.
- Parents own their boards, children and consolidation. Native local-Team chatter is not duplicated into every board. Files preserve outcomes and evidence pointers; editing a board does **not** wake a session.
- Namespaces are not competing product authorities. Existing bounded Codex work keeps its assigned scope; DSH dispatch does not adopt, cancel or overwrite it. Cross-namespace dependencies or write collisions return to the human/designated GRILL decision boundary before either scope expands.
- Availability until revoked is different from a finite mission's paths, budget, acceptance and stop condition. A dated stop or expired scope is not restarted by moving a file.
- Use **steer by default in both directions** for missions, ACKs, results and blockers, so coordination arrives at the next safe step boundary rather than waiting for turn end. Queue needs an explicit reason/request; never resend an accepted item merely to change its scheduling.
- Transport admission, recipient ACK, result, independent source review, installation and actual acceptance are distinct. Inactive does not mean complete; a message or board is not environment effect evidence or H-gate closure.
- The [repository Agent Guide](<../../AGENTS.md>) and canonical [independent-review contract](<../../REVIEW.md>) govern product work. Fresh review independence, exact-byte custody and deterministic/environment-owner gates are not relaxed by delegation.
- Product PRs target `main` from dedicated managed worktrees. Human authorization controls staging, commits, pushes, PR publication, merge and tags. A finite explicit delegation may authorize only named actions; this does not grant blanket future publication rights. Never install hooks through a worktree sharing the human checkout's Git common directory.

Implementation status and release-label decisions remain owned by the [canonical masterplan](<../plans/universal_agentic_harness_masterplan.md>) and [development log](<../plans/universal_agentic_harness_development_log.md>), not by namespace names, dated board entries or an old version map retained in a board. No H0/H1/H2 or sprint qualification follows from this reorganization.

## Codex continuity: no board rewrites

The following existing files were copied into `codex/` **byte-for-byte**, including their headings, dates, scopes and contents:

- [GRILL](<codex/grill.md>)
- [DEV](<codex/dev.md>) and [DEV2](<codex/dev2.md>)
- [RESEARCH](<codex/research.md>)
- [Technical synchronization](<codex/dev-sync.md>)
- [Base quarantine](<codex/base-quarantine.md>)
- [Existing guide](<codex/README.md>)

This is their continuing coordination home, **not a retired Codex namespace**. After the human coordinates cutover, Codex sessions should be pointed to these paths. Each parent remains the writer of its own board. No scope, completion, model setting or publication permission was inferred or changed by the relocation.

Some preserved text refers to former relative paths or DSH bootstrap instructions. Small compatibility notices resolve those references without editing the original boards. For **current DSH** operation, use the DSH guide, not the preserved Codex guide's DSH-specific HOLD/control-gap section. Canonical review authority remains the root review contract; redirects are not new owners.

## DSH current guidance and dated evidence

The [DSH guide](<dsh/README.md>) records what was actually proved, what remains instance-specific, and the bounded research lane. The [bootstrap](<dsh/DSH-COORDINATION-BOOTSTRAP.md>) is project-agnostic harness setup; the [methodology](<dsh/METHODOLOGY.md>) is this repository's application. Use the [parent-owned boards](<dsh/boards/README.md>) for actual role readiness and bounded outcomes, and the [planning catalog](<dsh/planning/README.md>) to find useful sprint/H3 material without treating expired execution windows as current work. The [Cordis/PTC lifecycle synthesis](<../artifacts/research/2026-11-16_dsh_ptc_cordis_lifecycle.md>) identifies concrete reuse candidates, not a replacement kernel or adopted implementation.

Earlier DSH material remains exact evidence, not current activation authority:

- [November 13 operating model](<dsh/archive/2026-11-13/OPERATING-MODEL.md>)
- [November 13 control-gap record](<dsh/archive/2026-11-13/CONTROL-GAP.md>) and [glossary](<dsh/archive/2026-11-13/CONTEXT.md>)
- [Evening continuation](<dsh/archive/continuation-20261111-evening/README.md>)
- [Night campaign](<dsh/archive/night-20261111/README.md>)

Keep their expired budgets, partial outcomes and old blocker statements in context. They do not reinstate the old Explorer HOLD, prove restart recovery, or authorize a new sprint.

## Compatibility, custody and publication

The [migration manifest](<migration-manifest.json>) records every original path, destination, exact bytes/hash and Git-versus-uncommitted source provenance. It also records the five old night-path **regular-file compatibility snapshots** needed by the locked read-only Explorer. Its source reader rejects symlinks. These copies retain closed source declarations; they are not duplicate writable boards or execution authority. The [compatibility notice](<night-20261111/README.md>) identifies their archive counterparts. Do not edit them independently or remove them before a separately reviewed source-path migration.

The live source checkout, concurrent Codex worktrees, accepted sprint packets and installed plugin directories are not moved or rewritten by this PR. Recheck source hashes before publication and coordinate the human's cutover; if Codex writes a board meanwhile, stop and re-freeze/re-review rather than overwriting either version. Merge and worktree removal remain human decisions.

Normally product PRs exclude parent boards, coordination logs and raw probes. **This coordination reorganization is an explicit human-authorized exception for these existing operational records**, reviewed for exact custody and bounded privacy concerns. It is not permission to publish credentials, new raw session transcripts, caches, experiment databases or future probe archives. Machine-local references in preserved boards are not portable installation instructions. The standalone bootstrap and reusable plugin must not carry this host's concrete identities or paths.
