# Primary consolidation review: executed controls

Commands were executed from `/home/juanbeck/universal-agentic-harness`.
The baseline-only renderer wrote exclusively in `/tmp/uah-consolidation-primary-before-8V75fz`.
The baseline HTML was reconstructed, not a retained original HTML receipt.
The baseline command aggregate exits 1 because `git diff --no-index --stat` reports
expected generated HTML differences; the renderer and its check each completed successfully.

## Opening frozen hashes, public renderer and scoped diff check

Exit: 0.

```text
78b68a465e1caff51eecbbdb3a7e31e544a986775aaf87b0c6bdada54d2957e5  docs/plans/universal_agentic_harness_masterplan.md
0332424e062579ee1b0ffcf70f9d2fabd491a535c9a62263f169a6db0388a5e9  docs/plans/universal_agentic_harness_masterplan.html
1a55a1e73400b78d5e4db5f747f779904ccc3d52fa4ad5ea779d156eab10ef68  docs/plans/universal_agentic_harness_development_log.md
9293aa675529c23aec31ff960c2b62a6a2b66f8d1eb34b2f153f115d936d82f2  docs/plans/universal_agentic_harness_development_log.html
a860e754ca51b1dac67e3739b6f648a4daad4bbe266d8177c340e43bc7838a58  docs/artifacts/reviews/2026-10-08_uah_consolidated_handoff.md
28fab5e
feat/pre-commit-queue
Checked 12 metadata records
```

## Predeclared local-link and format inputs

Exit: 0.

```text
docs/artifacts/reviews/2026-10-08_uah_consolidation_evidence/before/universal_agentic_harness_masterplan.md.txt: local_links=11; missing=[]; trailing_whitespace=[]; terminal_newline=True
docs/artifacts/reviews/2026-10-08_uah_consolidation_evidence/before/universal_agentic_harness_development_log.md.txt: local_links=14; missing=[]; trailing_whitespace=[]; terminal_newline=True
docs/plans/universal_agentic_harness_masterplan.md: local_links=13; missing=[]; trailing_whitespace=[]; terminal_newline=True
docs/plans/universal_agentic_harness_development_log.md: local_links=15; missing=[]; trailing_whitespace=[]; terminal_newline=True
docs/artifacts/reviews/2026-10-08_uah_consolidated_handoff.md: local_links=11; missing=[]; trailing_whitespace=[]; terminal_newline=True
```

## Throwaway before render, opening result

Exit: running at first yield.

```text
Rendered 12 metadata records
```

## Throwaway before render/check and generated-consumer comparison

Exit: 1.

```text
Checked 12 metadata records
949f9152e3a0ce750b773f10ed2f52a9430628befd644cd5ff5bef2bedd4809f  /tmp/uah-consolidation-primary-before-8V75fz/docs/plans/universal_agentic_harness_masterplan.md
7965ae0cdd81f05a702a743b964c05c6bb6b76de38f8908e25197e6a820c7312  /tmp/uah-consolidation-primary-before-8V75fz/docs/plans/universal_agentic_harness_development_log.md
 .../docs => docs}/plans/universal_agentic_harness_masterplan.html     | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)
 .../plans/universal_agentic_harness_development_log.html             | 5 ++++-
 1 file changed, 4 insertions(+), 1 deletion(-)
```
