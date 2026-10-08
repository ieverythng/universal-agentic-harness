# UAH unchecked-file review and No-Mistakes pilot

Final status at 2026-10-08 20:19 UTC: both independent REVIEW lanes require
changes. The one actual No-Mistakes run FAILED at its eight-minute Review
invocation budget, before returning a structured verdict. This document grants
no integration or release approval. No retry or repair round was started.
The bounded scope closed at 20:20:22 UTC, before its 20:21:41 hard stop.

## Scope and byte identity

Human branch: `feat/pre-commit-queue`, unchanged HEAD
`06f5a29daef9bb877fb08b6c6ee47d870df94d71`. The original thirteen staged paths
remain unchanged; staged binary-diff SHA256:
`af6bd13cf5b51420cdb078b8427cd2e472dfa2de0c6c9f35f78ab2e04123a77f`.

The frozen integration contains selected13 context, fourteen unchecked supporting
source modules, twenty-two matching/regression tests and two generated O1 pages.
The REVIEW target is the fourteen sources plus twenty-two tests, not implicit
approval of the context files. ARCH02's unstaged label/provenance changes,
synthetic R5 work, other dirty canonical docs and uv.lock are excluded.

[Target manifest](2026-10-08_uah_no_mistakes_pilot_evidence/review36.paths),
[integration manifest](2026-10-08_uah_no_mistakes_pilot_evidence/seed51.paths),
[hashes](2026-10-08_uah_no_mistakes_pilot_evidence/candidate51.sha256) and
[modes](2026-10-08_uah_no_mistakes_pilot_evidence/candidate51.modes)
identify the submitted application bytes. All hashes matched after normal local
hooks. Independent baseline tests: 162 passed; integration tests: 527 passed.
These passes are distinct from independent review and release qualification.

## Independent review outcomes

Both reviewers predeclared adversarial cases before implementation inspection,
used separate disposable copies and compared public behavior with the exact
baseline. Each ran 458 candidate tests and 93 available matching baseline tests.
Reports include all five REVIEW principles, counterexamples and residual limits.

| Finding | Status and ownership |
| --- | --- |
| STD-PILOT-01 | BLOCKING, introduced invocation-provenance defect. A compiled-prompt subclass sends different messages to the provider from those serialized into the ledger. Invocation admission must own exact consumed content. |
| STD-PILOT-02 / SPEC-PILOT-01 | BLOCKING, independently reproduced schema-policy defect. Non-boolean additional-property policy permits undeclared arguments through semantic admission, lease and owner dispatch. |
| SPEC-PILOT-02 | BLOCKING historical debt, present before and after. Caller-created resume/notify facts bypass the sole task-ingress authority. Start-command hardening is not alleged to fail. |
| SPEC-PILOT-03 | BLOCKING dependency regression. A genuine two-event baseline ledger remains readable in base but candidate rejects its old compiled-task envelope for lacking budgets. The failing lifecycle reducer was context-only, not silently included in source-review approval. |
| SPEC-PILOT-04 | NIT. Repeated budget requests accept boolean/float values equal to a previously valid integer; no extra debit or authority increase was demonstrated. |

[Standards report](2026-10-08_uah_no_mistakes_pilot_evidence/standards_review.md)
and [Spec report](2026-10-08_uah_no_mistakes_pilot_evidence/spec_review.md) both
conclude CHANGES. Requested models were gpt-6.1-sol/max and gpt-6-astra/max;
actual serving-model attestation was unavailable for these app subagents. That
limitation is retained, not inferred away from requested metadata.

Complete manual inspection of every test hunk, independent exhaustive concurrent
writer/actor combinations and every downstream reason-code consumer were not
completed. No smaller split or selected context receives blanket approval.
Baseline/candidate wheel probes shared the missing-setuptools limitation.

## Actual No-Mistakes execution

Authorized NM-PILOT-01 start: 19:56:41 UTC. Hard stop: 20:21:41 UTC, including
setup and durable handoff. One AXI run, maximum three native top-level sessions,
cold starts, zero automatic follow-up repairs and no `--yes`. Initial Document
edits/local commits are permitted only if reached inside the isolated lane.
No paid API key or production endpoint is used.

Executable: No-Mistakes v1.91.0, revision
`420adfd317e29e31bf6b5cd5d770529580084610`.
Release archive SHA256:
`951619324a6b3e5968a4f3a08de1c13557f32a0bb1a8c3cb1b9e7c01eceba893`.
Binary SHA256:
`ee68dd986ebeb334a62a9d51fb4777a1defdafab56d1998ec8cbe2a88ea70f48`.
The primary release checksum matches artifact identity; no reproducible-build
or independent source-to-binary proof is claimed.

Native backend: Codex CLI 0.160.0, existing ChatGPT account login. Effective
session metadata identifies gpt-6.1-sol, high effort, approval never,
workspace-write and network access false. No model name was guessed or user
global configuration edited. A separate CODEX_HOME contains minimal isolated
configuration and a local reference to existing account authentication; neither
credentials nor authentication files are included in this evidence package.

[Operator config](2026-10-08_uah_no_mistakes_pilot_evidence/operator_config.yaml)
and [trusted repository config](2026-10-08_uah_no_mistakes_pilot_evidence/repository_config.yaml)
select deterministic source-aware tests and Ruff. The
[bounded wrapper](2026-10-08_uah_no_mistakes_pilot_evidence/codex-capped)
rejects a fourth top-level launch and applies a finite native-process deadline.
This bounds operator launches, not tokens or all model-internal tool requests.
It is not a tamper-proof process boundary against arbitrary same-user code.
Native workspace-write keeps its ordinary temporary-directory allowance;
the original home-directory checkout is outside those writable paths.

The [controlled shell](2026-10-08_uah_no_mistakes_pilot_evidence/controlled-shell)
and [launcher](2026-10-08_uah_no_mistakes_pilot_evidence/nm) isolate HOME, XDG and
NM_HOME, disable telemetry/update checking, and avoid profile loading. Both a
shell-consumer probe and the actual daemon environment were checked. No sandbox
bypass was passed. Cold sessions avoid the narrower exec-resume flag surface.

Actual tool lane: `/tmp/uah-no-mistakes-pilot-repo`, independent Git clone with
local diagnostic origin. Upstream initialization resolves linked worktrees to
the common Git root and would modify shared remotes, so it was not initialized
against the attached managed worktree. Its foreground daemon/state live under
`/tmp/uah-nm-pilot-01`. Diagnostic base configuration commit:
`f92821ec2e5f4557d19c6ea5b8f07e965753d202`.
Submitted seed/pipeline head:
`f85ae715669379a428e063d0c965e42e78b3ae3f`.
Both diagnostic commits used normal hooks. Initial baseline hook collection
followed the existing editable installation into the primary checkout; explicit
`PYTHONPATH=src` corrected fixture isolation and the hooks then passed.

Run ID: `01M4EHYDDZ8MBE4PGBQ76SZMF2`.
Launch nonce: `NM-PILOT-01-20261008`.
Generation: `frozen-51-f85ae715`.
Persisted intent digest:
`08488a756d8e3c3c717fb474cd7bff0b4d5f61aa67767bd779f7323716b9cef7`.
[Intent](2026-10-08_uah_no_mistakes_pilot_evidence/INTENT.md) and
[launch receipt](2026-10-08_uah_no_mistakes_pilot_evidence/axi-launch.log)
are retained. The forty-five-second client hold expired while Review was active;
this is not a pipeline failure. No second run, fix, approval or skip response
was issued. Final AXI reports user-owned custody returned with no head change;
the private branch remains clean at the submitted seed.

Enabled phases: Intent, Review, Test, Document, Lint. Explicitly skipped: Rebase,
Push, PR, CI. Intent completed. Review FAILED after 485,084 ms. Test, Document,
Lint and the publication phases were not reached. Configured publication skips
remain distinct from the final step table's still-pending states. No local,
shipping, PR or CI pass is claimed.

Exact terminal error, retained in [status](2026-10-08_uah_no_mistakes_pilot_evidence/axi-final-status.log):

```text
step review failed: agent review reached its invocation budget after 8m0s (silent budget; no still-working cap is set; ran 8m5s): agent last produced output 7s ago (28 observed); agent reported: codex parse events: read |0: file already closed
```

The [review log](2026-10-08_uah_no_mistakes_pilot_evidence/axi-review-log.log)
contains an interim historical-replay observation but no structured findings or
final approval. The pipe error accompanies timeout handling; no independent
underlying pipe-bug diagnosis is asserted. A later reattachment without intent
was refused because the prior run had ended. No new intent was supplied.

Exactly one native top-level launch occurred. Five isolated rollout files show
internal model delegation. [Metadata and usage counters](2026-10-08_uah_no_mistakes_pilot_evidence/native-session-metadata.json)
retain per-session cumulative values. A launch cap does not cap internal model
sessions, tokens or spend. Summed counters are not billing attestation; parent
and child aggregation was not independently established. The wrapper's start
receipt has no finish row because upstream terminated it. A subsequent process
check found no remaining capped/native-exec worker for this lane.

No pipeline fix or Document commit exists. Submitted and final heads match; the
private clone is clean. The transient run worktree was removed by terminal
cleanup. This establishes no persisted application change, not a full audit of
transient filesystem operations. The isolated daemon is stopped; state and logs
remain available. No automatic continuation or monitor was created.

## Separate source visibility

The human subsequently authorized one remote WIP snapshot with known CHANGES
status. A separate immutable ref at the submitted seed was published with normal
all-files hooks, normal pre-push cache validation and a non-force push:
[codex/wip-uah-nm-pilot-20261008-f85ae71](https://github.com/ieverythng/universal-agentic-harness/tree/codex/wip-uah-nm-pilot-20261008-f85ae71).
Git ls-remote independently confirmed full SHA
`f85ae715669379a428e063d0c965e42e78b3ae3f`.

Attached managed worktree:
`/home/juanbeck/.codex/worktrees/no-mistakes-pilot-20261008/universal-agentic-harness`.
Its own dependencies and per-worktree pre-commit cache were used. This visibility
branch does not include board/evidence updates or other dirty files and does not
alter active AXI custody. No PR, main-branch merge, cherry-pick or human-branch
commit was made.

## Proposed integration boundaries, not approved commits

1. Prioritize model-independent role configuration and immutable manifest/handle
   identity as a bounded unit. The current whole identity file also includes run
   registration. A real split must defer that behavior and unrelated eager
   exports/renderers explicitly, then validate the resulting exact bytes.
2. Environment-bound AgentRun, allocator/preflight and lifecycle events form the
   next cohesive unit. Their ledger/runtime dependencies cannot be omitted
   merely because selected tests still import successfully.
3. The schema gate and matching admission tests remain blocked on malformed
   policy validation. A leaf schema-only commit would not itself prove the
   normalization/admission/owner contract.
4. Prompt compilation and invocation provenance remain blocked on exact-content
   enforcement. Supporting provider, runtime and task lineage must be explicit
   dependencies rather than implicit permission to include the rest of the tree.
5. Ingress sole-writer completion and historical read-only replay require owner
   repairs and discriminating before/after tests before further integration.

The human confirmed manual review of agent_configuration.py, agent_identity.py
and agent_lifecycle.py. GRILL verified those current/index/seed bytes match.
That is exact human review provenance, not approval of their unchecked support
closure or future revisions.

Recommendation: keep integration blocked. A later authorized tool trial should
reduce the review scope and verify internal-delegation controls before setting
its budget. Do not waive timeout evidence, increase budgets automatically, or
turn CHANGES findings into a successful commit. This evaluation demonstrated
submission/custody and failure handling, not a completed validation pipeline.

These are finite split proposals, not independently importable whole-file
checklists or approval to refactor reviewed files. Exact eventual split bytes
need fresh coverage of both required gates and explicit permitted paths. No
repair or second scope starts automatically. H0/H1/O1 exits and H2 parity remain
open. Current coordination and decisions are in
[DEV board](../../coordination/dev.md).

Final handoff/evidence checks passed through normal pre-commit in the disposable
execution copy. The source-aware suite passed, the renderer checked twelve
metadata records, and whitespace checks passed. These documentation-mechanics
results do not change the runtime CHANGES/FAILED outcomes. Original shared HEAD,
selected13 staged-diff checksum and pre-existing working file hashes were
rechecked unchanged. Only authorized board/AGENTS documentation and durable
pilot evidence were added in the primary checkout; no source repair was made.
