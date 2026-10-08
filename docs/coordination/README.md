# Chat coordination board

GRILL dispatches finite instructions to DEV and RESEARCH. Branch parents record
outcomes, requests and blockers here instead of sending unsolicited messages to
GRILL. DEV and RESEARCH do not contact or delegate to one another. Descendants
report to their own parent; the parent consolidates their evidence.

| File | Sole continuing writer | Purpose |
| --- | --- | --- |
| [grill.md](grill.md) | GRILL parent | Active dispatch, decisions and bounded queue |
| [dev.md](dev.md) | DEV parent | Implementation and independent-review outcomes |
| [research.md](research.md) | RESEARCH parent | Investigation outcomes and proposals |

DEV created the initial four documents under the authorized board-setup scope.
After initialization, each parent owns its file. Do not rewrite another branch's
status or treat its silence as consent.

Record the start of a scope, an actionable blocker, and the final handoff. Keep
one current scope, a short pending queue and a bounded closed summary. Include
the update time, owner, task, status, frozen branch/HEAD or snapshot, time bounds,
completed evidence, independent-gate state, next action, and the exact decision
needed. Link reports rather than copying transcripts or routine probe output.

GRILL reads the board at active task gates and new user turns. Ordinary file
writes do not wake GRILL. This board does not claim continuous monitoring and
does not schedule work.

## Source-of-truth limits

The board coordinates chats. It grants no runtime, review, Git or release
authority. Direct human instructions and explicit scoped dispatch remain the
authorization record. Governing contracts remain in the canonical architecture
and plan documents; [REVIEW.md](../../REVIEW.md) owns review requirements.

Research proposals, exact reviewed bytes, staged or committed files, and release
qualification are separate states. A test pass is not an independent review. A
review pass is not permission to add an excluded dependency. Missing evidence
cannot close a gate. When blocked, record the exact needed decision and stop
dependent actions. Elapsed time does not grant permission.

Evidence under `/tmp` is local and temporary. Preserve it in an explicitly
authorized durable artifact scope before relying on it for a release or commit
approval. Board Markdown is not part of the generated architecture HTML pairs.
