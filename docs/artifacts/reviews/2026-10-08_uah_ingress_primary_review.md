# Independent primary review: authority-bound task starts

Reviewed on 2026-10-08. Scope: SPEC-02 task-start production, lifecycle append
and replay, compiler provenance checks, registry projection, six affected test
files, the foundation/masterplan/development-log Markdown and HTML, and two O1
fixtures. The reviewer did not author the repair or consult another review.
Inputs were the repository, `REVIEW.md`, and the exact before/current diff.

Requested reviewer configuration: `gpt-6.1-sol`, `max`. The agent-facing tools
do not expose effective model/effort attestation. The requested pair cannot be
claimed as independently verified.

## Verdict scope and identity

No blocking finding was reproduced in the frozen ingress repair. Approval is
limited to the reviewed bytes and the trusted-runtime ledger-file boundary.
It does not qualify H0/H1 exit, H2 parity, arbitrary host-code tampering, or
resistance to an attacker rewriting the complete ledger and its hashes.

The release seam is H0-H1. `TaskIngressAuthority` owns task-start policy;
`LifecycleLedger` owns the sole append/replay interface; the task registry is
a read-only consumer. No new registry writer or environment-effect authority
was introduced.

Before tree: `/tmp/uah-ingress-before-checkout`, reconstructed actual dirty
bytes rooted at HEAD `06f5a29`, not an unmodified HEAD substitute.
Candidate: `/tmp/uah-ingress-candidate-frozen`.

All 17 entries of the original `round_frozen.sha256` matched again at final
verification. Exact before/current source, fixture and document SHA-256 values
are recorded in:

- [before_reviewed.sha256](2026-10-08_uah_ingress_primary_review_evidence/before_reviewed.sha256)
- [current_frozen_reviewed.sha256](2026-10-08_uah_ingress_primary_review_evidence/current_frozen_reviewed.sha256)

The latter also pins unchanged `task_compiler.py` and `CONTEXT.md`, which were
read to trace the compiler consumer and governing terminology. Principal source
identities are:

| File | Before SHA-256 | Approved candidate SHA-256 |
| --- | --- | --- |
| `task_ingress_authority.py` | `f16683d1378ddd5c517e8331d1044dcfaf6b9e59be4cd77daa535acf6788a9ab` | `d38a56709c6b93b61750abb717dedfa72dcabeab94c3cc0039d48dc2fd48dc7a` |
| `lifecycle.py` | `ef1cbd9d69c25735f94d14cd7df892ad97f1f0485c407f0b172d13d56e10b6d1` | `528907e7e8fe02d83c62adec6670dc3d6893e21449e6610368a6c04e684c1ca4` |
| `task_registry.py` | `5340bbbf30dc1874af688bd5ba58950e506f72990b753a9bf42a35d8eb207d2b` | `e0cd048a2752387846477f18eb26ae3f2b3a23d81e11b8e36acb6aaa230800ef` |
| `task_compiler.py` (unchanged) | `b11625e4cb5a64f74327e2112a6e182b48e45ce9821135a5af39a9f36f92e9bf` | `b11625e4cb5a64f74327e2112a6e182b48e45ce9821135a5af39a9f36f92e9bf` |

## Execute-before-read evidence

`REVIEW.md` was read first. The input plan was saved in
`/tmp/uah-ingress-primary-predeclared.md` before implementation or diff reading.
Runtime signature discovery bound those inputs to public constructors without
reading their bodies. Both imports resolved to their respective snapshot
`src/ab_harness/__init__.py`, not the working-tree package.

The same [public_probes.py](2026-10-08_uah_ingress_primary_review_evidence/public_probes.py)
executed 42 cases per tree before implementation reading. Its corrected API
binding uses the fixture's actual observable and accepted `matched_rule`
reason. The initial unsuccessful compiler binding is retained separately, not
counted as a valid control. Final pre-read results:

- [before_bound_public_probes.json](2026-10-08_uah_ingress_primary_review_evidence/before_bound_public_probes.json)
- [current_bound_public_probes.json](2026-10-08_uah_ingress_primary_review_evidence/current_bound_public_probes.json)

Reproduction: use the chosen snapshot as working directory, set
`PYTHONPATH=<snapshot>/src`, and execute the script with
`/home/juanbeck/universal-agentic-harness/.venv/bin/python`.

| Public input | Actual before | Frozen candidate |
| --- | --- | --- |
| Caller-created `TaskStartedFact` plus matching accepted decision | Appends one visible start; compilation succeeds | `record` rejects with `new starts require an authority-bound task-start command` |
| Genuine admitted start and matching TaskSpec | Compiles | Compiles to the same content ID |
| Genuine start after file-backed restart | Same compiled content and lineage | Same compiled content and lineage |
| Decision-only authority | No recorded-start rejection | Same rejection |
| One-field decision lineage/revision alternatives | Reject | Reject |
| Duplicate start, request order reversed | Exactly one start | Exactly one start |
| Two tasks in both orders; same domain task in another run | Distinct environment-scoped traces | Same traces and isolation |
| Resume/notify present, absent, foreign and wrong-run inputs | Original lineage or stable typed rejection | Same behavior |
| Suspended task resume/notify | Remains resumable | Remains resumable |
| Unknown binding/type; absent/wrong lineage key | No lineage created | No lineage created |
| Two independently opened file-backed writers, same ingress | One start, contiguous sequence | One start, contiguous sequence |

The public ledger has no additional bulk append surface; the registry has no
public mutator. Null/integer lineage inputs fail during unchanged envelope
construction; these are not evidence of a new typed-rejection API. The
independent terminal-rejected fixture stopped at acceptance validation and is
not claimed as a completed adversarial terminal control. Existing accepted and
terminal-counterexample tests ran successfully in the focused suite.

After reading the diff, [additional_probes.py](2026-10-08_uah_ingress_primary_review_evidence/additional_probes.py)
bound ten supplementary cases, including the predeclared legacy/export forms.
These are explicitly post-read evidence:

- [before_additional_probes.json](2026-10-08_uah_ingress_primary_review_evidence/before_additional_probes.json)
- [current_additional_probes.json](2026-10-08_uah_ingress_primary_review_evidence/current_additional_probes.json)

An unmarked historical start remains readable in both trees. Before, it grants
compilation and accepts a compiled append. Candidate rejects both with
`fresh compilation requires authoritative task-start provenance`, leaving one
historical event. Exported event, mapping, iterable and replay values cannot
manufacture authority through public `record`. A stale covered domain rule at
authority construction is accepted before and rejected by candidate content
verification. Later mutation of the caller's pack does not rewrite the
authority's previously frozen policy.

## Tests and documentation checks

- Six-file focused suite, actual before: 173 passed, one committed O1 freshness
  mismatch. Candidate: 190 passed.
- Candidate Ruff check over all three changed sources and six affected tests:
  passed.
- Candidate `scripts/render_agentic_harness_docs.py --check`: passed, 12
  metadata records checked.
- Candidate O1/runtime example suite after final identity verification:
  25 passed.
- Final candidate full suite (`python -m pytest -q tests`): 548 passed in
  12.39 seconds.

Pytest used the original venv with explicit candidate source/root/test paths.
`GIT_DIR` pointed to the real repository and `GIT_WORK_TREE` to the selected
snapshot for Git-aware tests. Package, renderer-script and test-module
`__file__` values were independently checked and resolved to the frozen tree.
Copied bytecode retained original traceback filenames; those filenames alone
did not establish a mixed import.

Two intervening full-suite runs observed 546 passing tests and two O1 freshness
failures while the candidate's O1 HTML hashes differed from the freeze. The
original fixture hashes were restored, all 17 original manifest entries were
verified, and the full suite was repeated successfully. The intermediate
`current_reviewed.sha256` records the observed altered fixture bytes; it is not
the approval manifest. No reviewer source or canonical-document edit occurred.

## Findings

### NIT: governing glossary retains the superseded raw-start behavior

1 of the 1 found so far.

Location: `CONTEXT.md:281-284` (unchanged; supplementary governing document).

Input: the `03-public-raw-start` and `06-public-raw-start-then-compile` probes,
followed by reading the Task ingress decision glossary entry.

Expected: present-tense glossary text describes the candidate's rejection of
raw start facts, while preserving historical SPEC-02 evidence as historical.

Actual: it states that current public `LifecycleLedger.record` still accepts
caller-created `TaskStartedFact`. That was true in the actual before tree and
is false at the approved candidate bytes. The candidate foundation and devlog
already describe the new boundary accurately. Updating the governing glossary
is optional follow-up; it is not a runtime blocker or permission to expand
this frozen repair.

## Five design principles

| Principle | Assessment |
| --- | --- |
| Separation of concerns | OK. Start policy stays in `task_ingress_authority.py:110-133`; append/reduction and provenance persistence stay in `lifecycle.py:581-647`; the registry checks read-only provenance at `task_registry.py:90-109`. |
| Programming by intention | OK. `require_fact` and `require_authoritative_task_start` name the rejected authority boundary and expose explicit error messages. |
| Encapsulation | OK. The private exact-type command is bound to its issuer capability and exact ledger; raw starts and exported events cannot enter through the public append API. The trusted runtime owns the ledger file. |
| High cohesion | OK. Frozen start policy and command validation are colocated with their issuer; replay authority is one trace-state property, not a separate writable task store. |
| Low coupling | OK. The narrow internal command dependency stays inside the portable kernel. Registry and compiler use the ledger provenance query, without native/provider imports or an alternate authority owner. |

The lock still covers disk reload, command revalidation, transition reduction,
append, flush and fsync. The changed status is start provenance only; models
still propose operations and environment owners still prove effects. Canonical
documentation preserves historical decisions and keeps H0/H1/H2 qualification
separate from this scoped correction.

VERDICT: APPROVE
