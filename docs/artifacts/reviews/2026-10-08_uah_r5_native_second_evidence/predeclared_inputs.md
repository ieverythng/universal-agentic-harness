# R5 independent native-owner second review: predeclared inputs

Declared 2026-10-08 before implementation or test-source read.

Scope: three new package/test files at the hashes supplied in the task. Base is
the exact dirty-before state with these new files absent. The same current core
dependencies will be retained in both throwaway controls. No fabricated parity
implementation will replace the absent package.

Initial public valid control: independent frozen expected UTF-8 text
`review note\n`, with environment `review-env`, task `review-task`, trace
`review-trace`, and compiled task identity from a real core fixture if required.
Write that text to an owned temporary note, perform the designated closure read,
and execute a callback returning a benign sentinel. Expected: historical write
and exact closure content are distinct observations and callback completion
means only normal return.

Then probe exact/wrong content; Unicode composed/decomposed, CRLF versus LF,
trailing newline, invalid UTF-8, empty text, missing/no write; distinct task,
owner, source, and compiled identities; foreign/tampered/missing observation
bodies; nested aliases; duplicate operations; mutation within callback,
callback failure, concurrent owner-mediated write at callback boundary; and
preexisting paths/symlinks using temporary directories only. External hostile
process writes are excluded. Reconstruct complete source and observation bodies
without rereading the current note. Run comparable unchanged-core controls in
both snapshots. Probe order is fixed before implementation inspection.

Time boundary: target 19:08:53 Europe/Madrid, hard stop 19:12:53. Unknown and
unexecuted checks remain explicit. Reviewer model/backend identity is not
directly observable from within this execution; parent selection is reported
separately when provided.
