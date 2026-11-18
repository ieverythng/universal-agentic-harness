# Release process

This document records the human-selected release targets and required evidence.
It does not assign a version to a commit or establish a milestone. See the
[PR delivery status](plans/pr-delivery-status.md) for the dated publication
snapshot.

## Release rule

A planned version does not waive acceptance evidence, convert partial work into
a completed milestone, or authorize promotion of quarantined work. Do not
create a release tag until the human selects an actual committed release SHA
and the applicable review, hosted checks, and acceptance gates pass for that
SHA.

## Version map

| Target | Release meaning |
| --- | --- |
| `v0.1` | Reviewed migration baseline. It does not imply H0, H1, O1, or H2 closure. |
| `v0.2` | H0 acceptance evidence. |
| `v0.3`–`v0.4` | H1 and O1 increments through their acceptance gates. |
| `v0.5` | Complete Python NAO planner-parity H2 evidence. Recorded or fake-owner qualification remains distinct from live-model evidence. |
| `v0.6` | Native NAO H2.1 evidence after the Python H2 target. |
| `v0.7`–`v1.0` | H3 increments through full Neural Workbench integration. `v1.0` records the H3 target only. |
| `v1.5` | H4 crystallization and reviewed AB-promotion target. |
| H5 and later | Release numbers remain unassigned. |
| H6 | Research only; no release target is committed. |

The `v1.0` H3 target does not imply H4 or H5 completion, cross-domain
conformance, or release-gate completion. The separate version of the companion
package does not set the UAH release number.

## Release evidence and tagging

For a release candidate:

1. Select the target from the version map and state the acceptance evidence.
   Record known gaps without treating a later target as evidence for an earlier
   one.
2. Select the exact committed SHA after the human merges the reviewed
   candidate. Do not identify a release only by a branch name, a local cache
   entry, or an uncommitted worktree.
3. Confirm the required hosted checks passed for that candidate and that
   independent reviews approved the exact manifest. Local checks do not replace
   hosted CI.
4. Verify that release notes and evidence refer to the same selected SHA. The
   human decides whether to create a tag after this verification.

Until the human selects the reviewed committed SHA, there is no release tag. A
planned version, migration baseline, partial milestone, or passing local cache
does not change this rule.

## Current check workflow

The repository currently uses local pre-commit checks for feedback and a
pre-push cache guard that requires a recorded successful local run for the
outgoing branch tip. Required hosted PR CI is the merge gate. The possible
removal of the custom cache requirement is a separate, unadopted workflow
proposal; see the [contribution guide](../CONTRIBUTING.md). No local hook or CI
policy change follows from this release guide.

## Quarantined work

H3 candidate generation remains offline or shadowed and cannot change trusted
runtime, permissions, evaluators, or registries. H4 promotion requires replay,
counterexample, holdout, owner-review, provenance, and rollback gates. Keep
adaptive or learned structures out of a stable release claim while an
applicable gate remains open. H2 NAO parity also keeps recorded or fake-owner
evidence distinct from live-model or robot evidence.
