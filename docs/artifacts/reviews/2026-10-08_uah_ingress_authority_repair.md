# SPEC-02 ingress authority repair round

**Date:** 2026-10-08, Europe/Madrid  
**Status:** Scoped ingress correction independently approved; H0/H1 exits remain open  
**HEAD:** `06f5a29daef9bb877fb08b6c6ee47d870df94d71`  
**Window:** 20:39:05 to 21:09:05 Madrid (18:39:05 to 19:09:05 UTC)

## Accepted boundary

The human selected an authority-bound ledger command in GRILL. Other callers
may request a start through `TaskIngressAuthority`; the authority admits the
request and `LifecycleLedger` owns durable writing and replay. Constructing a
matching decision or raw `TaskStartedFact` must not grant fresh compilation
authority. The task registry remains a read-only projection. Historical events
remain readable without becoming new command authority.

This is a bounded H0/H1 authority repair, not H0/H1 release qualification.
Authenticated-proof storage, malicious filesystem rewriting, provider calls,
NAO parity, cache repair and Observatory label policy are outside this round.
The current trusted-runtime boundary includes ownership of the ledger file.

## Frozen inputs and scope

Root captured the complete tracked/untracked path hashes, dirty status, binary
diff and exact affected source bytes at
`/tmp/uah-ingress-round-20261008-before/` before author edits. The writer retains
affected before bytes and command evidence in the dated evidence directory.
The committed docs/artifact batch is separate from these uncommitted repairs.

Scope: task-ingress authority, lifecycle command/replay, the compiler's start
provenance check, the read-only task registry consumer and exact affected tests.
Canonical foundation, masterplan and development log may record this decision
and the observed implementation state. No Git staging, commit or push is allowed.

## Predeclared controls

- Genuine admitted start compiles and preserves lineage after restart.
- Caller-created raw start facts and matching decisions cannot authorize
  fresh compilation; public replay/export inputs cannot mint command authority.
- Rejected ingress leaves no authoritative task start.
- Foreign, stale or mutated ingress/decision provenance is rejected.
- Legacy unmarked starts remain inspectable without fresh compilation rights.
- Cooperating writers preserve atomic lock, reload, reduce, append and fsync.

## Baseline limitation

Before this repair both committed O1 examples already fail their public
`--check` freshness commands. This is the previously recorded generated-byte
drift, not a newly attributed ingress regression. Canonical Markdown/HTML
checking passes. These observations must remain separate from scoped source
approval and release qualification; no historical manifest is rewritten.

## Completion

Both fresh reviews approve the restored original seventeen-path target:
[primary](2026-10-08_uah_ingress_primary_review.md) and
[second](2026-10-08_uah_ingress_second_review.md). They report no blocking source
findings and optional stale-current-prose nits in `CONTEXT.md` and the
Observatory contract. Requested reviewer configurations were sol/max and
astra/max; effective backend configuration was not independently attested.
The restored candidate passes 548 full tests. The root hook mutation of two
review artifacts, preserved altered bytes and exact restoration are documented
in [root checks](2026-10-08_uah_ingress_authority_repair_evidence/root_checks.md).
Original freeze hashes and intermediate failures remain evidence.

DEV interpreted the human's request for selected agent files and minimum
supporting modules and tests as permission for a broader batch. Its subagent created
`864c6d3d6eb7b978c426327f877059e956a9e882` at 19:04:41 UTC, with the prepared
message unchanged. That fifty-one-path snapshot passes 527 tests and normal
hooks; it excludes the deferred synthetic adapter/test and adds one formatting
regression. The formatting fix removes literal template indentation before an
empty optional graph section, without normalizing raw payloads. Event records
and graph JSON remain equivalent. The original ingress source and test bytes
are unchanged in that commit. No push occurred; the index was empty at completion.

The commit's broader supporting modules remain subject to human review. The
two ingress approvals do not approve that entire batch, establish provider
readiness or close H0/H1/H2. ARCH-02 remains a separate queued correction.
The next canonical-doc scope must reconcile the two current-state prose nits
without rewriting historical findings or removing deferred provenance work.

## Subsequent commit-scope correction

At 19:15 UTC the human clarified that the fifty-one-path batch exceeded the
authorized selection. DEV removed `864c6d3` from the branch using a mixed reset
to `06f5a29`, preserving all working-tree bytes and a recovery reference.
Exactly thirteen paths are staged: the ten checked in the screenshot, plus
`lifecycle.py`, `model_allocator.py` and `observatory.py`. Other modules, NAO
changes and tests remain uncommitted for manual review. The later ARCH-02
source delta remains unstaged. No replacement commit or push was made.

The exact thirteen-path export fails source-test collection because its package
exports import uncommitted `model_invocation.py`. Other direct imports also
reference unstaged modules. That dependency failure does not authorize adding
them. The ingress approvals retain their frozen source scope; they do not
establish approval of either the removed commit or the partial staged snapshot.
