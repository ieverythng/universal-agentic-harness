# Consolidation: root documentation checks

Scope: documentation-only, start 2026-10-08 20:10:03 Europe/Madrid, hard stop
20:25:03. Author freeze: 20:13:39. Initial HEAD
`28fab5e7f2c244d86a64c371f2118017999b2387`, branch `feat/pre-commit-queue`.
The same HEAD remained at the 20:15 read-only check. No agent Git mutation.

Five frozen documents are pinned in doc_frozen.sha256: canonical masterplan
and development-log Markdown/HTML pairs, plus the new consolidated handoff.
The baseline Markdown copies match their original start-manifest hashes:

- masterplan: `949f9152e3a0ce750b773f10ed2f52a9430628befd644cd5ff5bef2bedd4809f`;
- development log: `7965ae0cdd81f05a702a743b964c05c6bb6b76de38f8908e25197e6a820c7312`.

Executed after freeze:

| Command/check | Observed result |
| --- | --- |
| `.venv/bin/python scripts/render_agentic_harness_docs.py` | Rendered 12 metadata records before freeze |
| `.venv/bin/python scripts/render_agentic_harness_docs.py --check` | Checked 12 metadata records |
| `./scripts/run_precommit.sh` | All hooks pass: hygiene, Ruff, source-aware tests and canonical docs |
| `.venv/bin/python scripts/render_observatory_example.py --check` | Existing recorded O1 example remains fresh |
| `.venv/bin/python scripts/render_agent_runtime_example.py --check` | Existing synthetic activation example remains fresh, not R5 qualification |
| `git diff --check` | Passed |
| `sha256sum --quiet -c .../doc_frozen.sha256` | Five frozen documents match |
| Start-manifest hashes excluding the four authorized canonical doc paths | All preserved files match |

Exact preserved-file check:

```bash
awk '$2 !~ /^docs\/plans\/universal_agentic_harness_(masterplan|development_log)\.(md|html)$/ {print}' docs/artifacts/reviews/2026-10-08_uah_consolidation_evidence/start.sha256 | sha256sum --quiet -c -
```

Root reread every changed paragraph and the complete new handoff, then compared
each canonical Markdown source with the exact baseline copy using diff -u.
The diff's exit 1 indicates expected documented edits, not a validation failure.
H0/H1 synthetic acceptance requirements, historical findings/receipts and source
bytes were not changed. Current work order is NAO-first; ingress choice remains
pending and source/release qualification is not granted.

Fresh reviewer requests are gpt-6.1-sol/max and gpt-6-astra/max. Their effective
backend execution is not independently attested. Independent reports and final
root disposition are separate; these writer checks do not approve the gate.
No runtime/provider/NAO startup, source/skill repair, staging, commit or push
occurred. The ordinary hook records its local success cache, which does not
close STD-02 outgoing-tree coverage.
