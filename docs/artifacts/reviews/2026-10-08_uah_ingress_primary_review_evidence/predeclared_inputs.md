# Independent ingress review: predeclared public input plan

Declared on 2026-10-08 before reading implementation or the forthcoming repair
diff. Review inputs are the repository contract, `REVIEW.md`, and exact
before/current bytes. No author rationale or previous review report is used.

Baseline: `/tmp/uah-ingress-before-checkout` (actual dirty-tree bytes, rooted at
HEAD `06f5a29`). Current: await the frozen snapshot and exact diff.

Requested reviewer: `gpt-6.1-sol` with `max` reasoning. The agent-facing tools
do not expose an effective model/effort attestation; do not claim it verified.

## Fixed test values

- Environment activations: `review-run-a`, `review-run-b`.
- Domain task identifiers: `review-task-alpha`, `review-task-beta`.
- Native request identifiers: `review-request-1`, `review-request-2`.
- Native missing-value alternatives: omitted key, null, empty string, whitespace,
  non-string integer, and a value under the wrong lineage field.
- Native observation timestamp: `2026-10-08T18:00:00+00:00`; a separate equivalent
  offset timestamp is `2026-10-08T20:00:00+02:00`.
- Foreign artifact identifiers: a syntactically valid 64-zero hash and the
  corresponding genuine artifact identifier from another activation.
- Use the repository's portable registry/domain/profile fixtures to construct
  otherwise valid envelopes; hold their semantics fixed across snapshots.

## Public operations and cases to execute, before reading implementation

The adapter script may discover constructor signatures at runtime; that is API
binding only, not permission to change these input choices or expected results.
Each case runs in a fresh temporary environment through public methods only.

1. Valid start: `TaskIngressAuthority.admit` receives an approved-binding start
   ingress with task alpha/request 1 in run A; then `TaskSpecCompiler.compile`
   consumes the returned accepted decision with its matching TaskSpec. Expect
   one ledger-owned lineage and successful compilation.
2. Restart control: close and reload the ledger after case 1; construct a new
   registry and compiler; compile the same admitted decision. Expect identical
   lineage, not a second start or a fabricated task.
3. Pure forged start: construct `TaskStartedFact` directly, with internally
   consistent run/task/trace/ingress/decision/domain revision, and call public
   `LifecycleLedger.record`. Expect rejection without events or registry state.
4. Alternative bulk surface: submit the same caller-authored start through
   every public multi-record/atomic append entry point exposed by the ledger.
   Expect the same rejection, including a batch containing an ordinary fact.
5. Decision-only compiler input: create a content-addressed accepted start
   decision and matching TaskSpec without calling admitted ingress. Expect
   compilation rejection, even when the hashes and all lineage fields agree.
6. Forged fact plus forged decision: use public raw ledger append first, then
   compile the matching accepted decision. Expect no compilation authority.
7. Wrong activation: real admitted start from run A, then compile or register
   its artifacts under run B. Expect rejection and no run-B lineage.
8. Wrong artifact alternatives: replace exactly one of starting ingress ID,
   decision ID, trace ID, task ID, or domain-pack revision on a genuine decision
   or matching TaskSpec; keep all other values unchanged. Expect rejection.
9. Duplicate start: submit identical ingress twice, then a second ingress with
   request 2 but the same task alpha in run A. Repeat in the reverse request
   order. Expect at most one start and deterministic duplicate outcomes.
10. Two tasks: admit task alpha and beta in both orders. Expect independent
    lineages. Reusing task alpha in run B must neither inherit run A authority
    nor collide across activations.
11. Resume/notify valid controls: after an admitted start, admit each supported
    resume and notification form. Expect the original immutable task/trace
    lineage and no replacement compilation/start.
12. Resume/notify adversaries: before a start, after a start under a different
    activation, and with a foreign task identifier. Expect typed rejection,
    never task creation inferred from native/model text.
13. Terminal lifecycle: admitted task with terminal accepted/rejected closure,
    then resume/notify. Expect rejection. Suspended acceptance control remains
    resumable and does not become terminal by label alone.
14. Missing/alternative native task lineage values listed above. Expect typed
    invalid-lineage rejection, not a task assigned by fallback/hash/model text.
15. Unapproved or changed binding, wrong ingress type, or a changed covered
    domain rule after artifact construction. Expect rejection before lineage
    creation and no accidental compilation authority.
16. Registry projection: directly call any public registry mutator or lineage
    registration alternative exposed by runtime API discovery with a forged
    lineage. Expect no independent writable task store; ledger reload must be
    the sole source of accepted task lineage.
17. Contending writers: two independently opened file-backed ledger/authority
    instances admit the same task/start at the same time. Expect one accepted
    start, consistent rejection/no-op for the other, intact contiguous replay.
18. Serialization alternative: round-trip genuine accepted start decision and
    lifecycle JSONL through public serializers; repeat a pure caller-authored
    start and tampered lineage body through strict reload. Genuine provenance
    must replay; alternate representations must not silently gain authority.

All cases compare baseline and current results and record exact public calls,
exceptions/reason codes, event counts, registry visibility, and compiler result.
If a declared public form does not exist, record it as not applicable instead
of substituting an internal method. Additional inputs discovered after reading
will be explicitly labelled post-read and never described as predeclared.

## After execution

Read the frozen diff and affected implementation/fixtures, then trace authority
origin to compiler and registry projection. Assess all five REVIEW.md design
principles, public error propagation, no second writable owner, lock/reload/
append atomicity, canonical documentation truth and generated parity. Report
BLOCKING/NIT findings with reproducible inputs and before/current comparisons.
Record SHA-256 for exact reviewed source/docs and all evidence files. Approval
is limited to the bounded reviewed bytes, not H0/H1/H2 exit qualification.
