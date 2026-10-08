# O1 raw iterable identity: bounded repair

**Closed 2026-10-08 at 17:43 Europe/Madrid: CHANGES.** A separate
constructor-conformance correction requires a new freeze and fresh review.

Date: 2026-10-08, Europe/Madrid. Start 17:29:31, hard stop 17:49:31.
Source freeze target 17:33; fresh reviews target 17:43.
HEAD: `28fab5e7f2c244d86a64c371f2118017999b2387`.
Owner: read-only O1 projection, consuming the common ledger's TraceEvent contract.

The separately authorized target is R3-O1-RAW-ITERABLE-IDENTITY. Before any
status derivation, reject a foreign genuine TraceEvent whose kind or covered
content changed under a stale ID. Preserve valid raw illustrative inputs and
the ledger-origin path. This is separate from ARCH-02 measured/reviewed label
provenance, which is untouched. No new schemas, freshness, causal validator,
effect authority or provider/runtime work is authorized.

Owned sources: observatory.py and new public tests. Exact-before copies of
observatory.py and existing test_observatory.py are retained in the evidence
directory. R4-FIX, dashboard and original residual probe are protected.
Root owns current-state docs, generated O1 examples and full hooks after
source freezes. No Git or provider mutations.

Frozen public train/control inputs: valid resume-kind raw events; the same
events mutated to accepted with stale content ID; unchanged ledger-origin
projection. Additional cases cover generator/tuple inputs, field mutations,
foreign invalid content before actor/status grouping, valid incomplete
illustrative terminal records, duplicate identity and invalid value controls.
The original saved residual stays unchanged and must now stop at identity
rejection. Public tests precede the minimal change; relevant tests, docs and
examples, full hook suite and fresh distinct-model independent reviews govern
the bounded gate. Stop on any new normative choice or at the time limit.

## Implementation freeze

Source frozen at 17:31:36, before the 17:33 target. The sole runtime change
invokes the existing `TraceEvent.verify_identity()` for each typed input before
identity uniqueness, ordering, actor grouping or trace status derivation.
No new event grammar or label policy is introduced. SHA-256:

- observatory.py: `aec50ca2e77d5c5bbe187ae08e6700797dee28bf7a703ac35f593de884ecb878`.
- test_observatory_raw_identity.py: `02e90f519120ebfe7d785954606a24bc8d286c5e6ff01b9f09a1ad3211e236d1`.

The initial public stale-terminal test fails with DID NOT RAISE before the
two-line repair, then passes. The retained public red/green logs record both.
Eight new cases and the existing O1/actor-example controls pass 33 tests; scoped
Ruff passes. The additional mutation cases are holdout coverage added after the
first repair, not pre-edit red claims.

Evidence limit: the two exact source/test copies precede edits, but the complete
shared dirty-tree hash manifest was captured at the post-edit source freeze,
not before it. It is labeled `shared_tree_at_freeze.sha256`. Concurrent R4-FIX
changes are outside this round and must not be treated as a frozen whole-tree
baseline. Fresh review, source equality and final integration checks are pending;
no full hook or release approval is claimed at this handoff.

## Independent gate

[Primary](2026-10-08_uah_o1_raw_identity_primary_review.md) and
[distinct-model second](2026-10-08_uah_o1_raw_identity_second_review.md)
each return CHANGES with the independently reproduced v1 actor/scope finding.
They execute controls before source reading and compare isolated packages with
the exact-before O1 source. The primary retains 54 outcome probes per version;
the second retains 124 paired cases. All five principles and dependency-snapshot
limits are recorded. Requested reviewers are gpt-6.1-sol/max and gpt-6-astra/max;
backend identity is not independently observable.

The covered stale-ID fields now reject. However, v1 identity does not serialize
the v2-only actor/scope fields; mutating them on a genuine v1 object passes
`verify_identity()` and invents an actor view or suppresses a task trace.
The existing constructor prohibits those forms, but projection does not invoke
that shape validation. The same gap exists before this repair, so it is an
incomplete gate rather than a newly introduced regression or ARCH-02 issue.

Both frozen source/test hashes remain unchanged. Root ran the all-files hooks
after concurrent R4-FIX source freeze; they pass, as do both O1 freshness checks.
Passing checks do not override the independent findings. No historical schema,
label policy, authority, Git state or live provider was changed. The original
saved residual is unchanged and now stops at identity rejection, with its later
control lines not claimed executed in that invocation.
