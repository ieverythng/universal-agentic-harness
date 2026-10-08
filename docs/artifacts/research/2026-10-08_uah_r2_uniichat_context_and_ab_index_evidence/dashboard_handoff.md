# R2 dashboard handoff to DEV

Date: 2026-10-08. Ownership: RESEARCH artifacts only.
DEV owns catalog schema, renderer, dashboard and implementation review.
Main GRILL owns scope/architecture decisions. This handoff requests cataloging,
not activation of context, evidence or model behavior.

## Existing artifact pointers

- Report: `docs/artifacts/research/2026-10-08_uah_r2_uniichat_context_and_ab_index.md`.
- Cards: `docs/artifacts/research/2026-10-08_uah_r2_uniichat_context_and_ab_index_evidence/experiment_cards.json`.
- Exact pinned source: sibling `optchat.md`.
- Primary metadata: sibling `source_manifest.json`.
- Source inspection baseline: sibling `baseline.sha256`.
- Source/math inspection receipt: sibling `static_probe.json`.
- Proposed metric definitions: sibling `metric_contract.md`.
- Final repository validation: sibling `validation.json` once present.
- No model/provider benchmark result exists; result_source/producer_run_id remain null.

## Proposed research identities

| ID | H-series | Dependencies | Implementation | Evidence |
| --- | --- | --- | --- | --- |
| UAH-CTX-ARCHIVE-v0 | Minimal proposed H1 continuity seam | Accepted scope/retention choice and current public owner/task path | unimplemented | planned / not_scored |
| UAH-CTX-HIERARCHY-v0 | Optional H3 context view | ARCHIVE; frozen synthetic source/labels/summaries | unimplemented | planned / not_scored |
| UAH-CTX-ABINDEX-v0 | Optional H3 separate semantic index | ARCHIVE + HIERARCHY comparison | unimplemented | planned / not_scored |
| UAH-CTX-S1RANK-v0 | Optional H3 classifier/ranker | ARCHIVE + qualified route; HIERARCHY only when ranking summaries | unimplemented | planned / not_scored |

All identity classes are provisional_experiment. None establishes H1 exit,
H3 performance or H4 promotion. This card file is a proposal format, not the
implemented registry schema. A registry may index the report/cards as research
source pointers; it must not adapt null values into observed metrics.

Frozen baseline is dirty-tree HEAD
`28fab5e7f2c244d86a64c371f2118017999b2387` plus retained relevant file hashes.
Fixture/model/holdout identities are null because no execution corpus or model
was qualified. Before execution, freeze actual bytes/hashes and oracles.
Same display names, AB depths or seeds do not establish comparability.
Each arm holds all declared factors fixed except its stated contrast.

## Concrete source boundaries

Pinned latest gist:
`3c190e06f34aba0c69f49042c526093269604935`, 19,092 UTF-8 bytes,
SHA-256 `12f300f760af82bc07bc5201051d1267824ded09c9def8186e4f8144368038d8`.
Current title UniiChat; file name optchat.md; historical OptMem is a distinct
implementation. Original tool-output loss occurs before logging at a 30,000
character cap. Raw preservation and retrieval fidelity are not equivalent.

Summary hierarchy depth measures chronological interval coverage, never AB
semantic level. Models can rank already-eligible closed candidates; deterministic
gates and environment owners retain authority. Historical context cannot prove
current content at task closure or override the accepted exact-content oracle.
Learned summaries cannot replace verified digests.

Ollama loopback/cloud and Watson/ZeroTier are separate route identities.
Archive UTF-8 bytes and production input tokens are separate budgets.
Anthropic cache simulations are source claims, not UAH telemetry.

## Next implementation dependency

Recommended narrow question for GRILL: accept synthetic-only exact archive and
immutable bounded source-resolving selection manifests first, leaving summary
trees, AB-indexing and model ranking as optional H3 screens.

Privacy must be decided before real history enters compiled prompts:
current invocation events inline rendered prompt/output bodies. Archive deletion
alone is not erasure. No live import, provider calls or schema change is authorized
by this handoff. The post-admission catalog/effect-evidence repair is separate
DEV authority work and cannot be solved by treating a context archive as an
authoritative CompiledTask store.

Existing September Jev note remains dated source investigation. Do not refresh
its pricing/access/hardware claims from this round. Jev is a classifier/ranker
candidate, not a summarizer or evidence owner.
