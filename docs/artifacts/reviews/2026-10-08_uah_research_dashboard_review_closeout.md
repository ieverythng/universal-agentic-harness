# Research dashboard: independent review closeout

Date: 2026-10-08. Closed at 16:50 Europe/Madrid. Verdict: CHANGES.
This closes the initial implementation/review round, not its repair work.

The [author receipt](../research/2026-10-08_uah_research_catalog_round.md)
records the frozen 12-record catalog and writer validation. Both fresh
[primary](2026-10-08_uah_research_dashboard_primary_review.md) and
[distinct-model second](2026-10-08_uah_research_dashboard_second_review.md)
reviews return CHANGES at unchanged implementation hashes. Their exact-byte
tables and executed counterexamples define the reviewed scope.

| Finding family | Classification | Required correction |
| --- | --- | --- |
| Registry versus displayed reconciliation date | BLOCKING, both reviews | One date owner, with consistent generation/check |
| Metadata authoring generated delimiters or raw Markdown HTML | BLOCKING, primary | Literal metadata in both supported presentations; render/check idempotence |
| Unicode/control line separators removing catalog rows | BLOCKING, second | Normalize or reject before output mutation; retain every valid record in filters |
| Literal punctuation displayed as entity syntax | NIT, both reviews | Safe, faithful literal display |

The author tests and pre-commit pass do not contradict these findings: their
input coverage omitted these cases. Saved desktop/mobile images show readable
layout for the ordinary catalog, not malformed-input correctness. No runtime,
model-performance or release gate is approved by this dashboard.

Primary report SHA-256:
`80240f8127482a5d439b30a9a8b469aa05f57510ee3fa7e6b698eaaf8884463a`.
Second report SHA-256:
`e08e16979c17b5fa60dfccafd2c369d07bfc84b2af57ee3e4b4e3df7438a871d`.
No historical reviewer report was changed. Main authorizes one separately
frozen, 20-minute renderer correction round with public red controls and fresh
reviews of its fix. The initial CHANGES verdict remains historical evidence.
