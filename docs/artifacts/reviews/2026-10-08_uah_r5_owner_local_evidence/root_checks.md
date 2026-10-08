# R5 root integration checks

Date: 2026-10-08. Root checks apply to the frozen native foundation, not release
qualification. Commands run from /home/juanbeck/universal-agentic-harness.

| Command | Observed result |
| --- | --- |
| `.venv/bin/python -m pytest -q` | 532 passed in 10.66 seconds |
| `./scripts/run_precommit.sh` | Passed, including Ruff, source-aware tests and canonical-document synchronization |
| `.venv/bin/python scripts/render_agentic_harness_docs.py` | Rendered 12 metadata records |
| `.venv/bin/python scripts/render_agentic_harness_docs.py --check` | Checked 12 metadata records |
| `.venv/bin/python scripts/render_observatory_example.py --check` | Passed; existing recorded-canary example only |
| `.venv/bin/python scripts/render_agent_runtime_example.py --check` | Passed; existing synthetic activation/invocation example only |
| `sha256sum -c docs/artifacts/reviews/2026-10-08_uah_r5_owner_local_evidence/source_frozen.sha256` | All three frozen paths match |
| `awk '$2 ~ /^src\/ab_harness\// \|\| $2 ~ /^src\/ab_harness_nao\// \|\| $2 ~ /^tests\// {print}' docs/artifacts/reviews/2026-10-08_uah_r5_owner_local_evidence/dirty_before.sha256 \| sha256sum --quiet -c -` | All protected preexisting source/test paths match |
| `git diff --check` | Passed |

Independent retained probes rerun without changes:

```bash
PYTHONPATH=src:tests .venv/bin/python docs/artifacts/reviews/2026-10-08_uah_r5_native_primary_evidence/probe.py
PYTHONPATH=src:tests .venv/bin/python docs/artifacts/reviews/2026-10-08_uah_r5_native_second_evidence/probes.py
PYTHONPATH=src:tests .venv/bin/python docs/artifacts/reviews/2026-10-08_uah_r5_native_second_evidence/boundary_repros.py
```

Primary: 48 cases, 42 pass and six failing variants of two mechanisms. Second:
20 cases, 18 pass and two failing mechanisms. Boundary reproducer: both owner
construction orders permit the competing mutation, and the hardlink mutates
the outside inode. These reporters exit zero after recording failures; the
gate is CHANGES. The primary rerun occurred before its evidence-retention rename
from probe.py to probe.txt. The final retained text is executable with the same
Python command and corrected .txt path. Comparison against the original
temporary probe shows only removal of one final blank line; no probe logic
changed. The report link and execution note were updated by the reviewer.
The initial second-probe command omitted tests from PYTHONPATH
and failed to import test_prompt_compiler; the corrected command above is the
comparable executed result, not that failed import.

The two O1 examples contain no R5 write or closure evidence. No source edit was
made after freeze, no live endpoint was invoked, and no staging, commit, push,
branch change or additional repair round occurred. Precommit's ordinary local
success-cache recording is not outgoing-tree qualification; STD-02 remains open.
