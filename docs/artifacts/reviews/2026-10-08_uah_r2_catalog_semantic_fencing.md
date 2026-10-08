# R2 DEV: catalog semantics at admission

Date: 2026-10-08. Status: admission-only repair independently approved;
global SPEC-03 remains PARTIAL/OPEN.
Round began 16:21 Europe/Madrid; target stop 16:41. Branch:
`feat/pre-commit-queue`; HEAD `28fab5e7f2c244d86a64c371f2118017999b2387`.
The separate research/dashboard lanes do not approve this authority repair.

## Frozen target

SPEC-03, H0 semantic admission: a binding catalog must not replace the frozen
ABObjectView consumed by a CompiledTask. Compare the existing projected object
with the catalog's view before binding admission. Preserve a legitimate approved
binding and valid object semantics. No new semantic fingerprint, generic codec,
effect/freshness policy, runtime schema or owner interface is authorized.

The [start manifest](2026-10-08_uah_r2_catalog_start.sha256) captures dirty and
untracked inputs. Exact before snapshots of `proposal_admission.py` and its
public integration tests are in `/tmp/uah-r2-catalog-20261008/`. Dashboard source
and dated RESEARCH artifacts may change concurrently; no human change is reset.

Red input: same object ID/owner/approved binding but added prohibited
`direct_speech` effects/observables in the catalog. Expected: typed semantic
rejection, no AdmittedOperation, no lease/dispatch, nonterminal replay. Control:
unchanged approved-binding chain remains valid. Widening to valid binding
replacement must not require whole-registry/source-label equality.

Acceptance: focused/relevant/full tests, pre-commit, docs and O1 examples,
fresh REVIEW.md reviews with a distinct second model. Public admission semantics
remain the owner of this check. Runtime/provider qualification is not scored.

## Exact downstream gap

The existing owner receives an ExecutionLease and catalog, while the ledger's
task_compiled projection retains only task/revision/role/frame/registry/budgets.
It does not retain the full projected object. A post-admission catalog replacement
therefore needs a separately approved data-carrying seam to reverify that object
at execution. This round must not invent an owner constructor argument, artifact
store or admission schema. Probe and return this choice to GRILL; do not claim
global SPEC-03 closure from the admission slice alone.

## Evidence

The public effect-drift regression failed before the change because admission
returned an AdmittedOperation. It now returns `catalog_object_mismatch` before
any lease or dispatch. Its rejection survives file-backed restart, remains
nonterminal and is visible in O1. A second control accepts a reviewed binding
revision and locator change when the complete projected object is unchanged.
The implementation adds one equality check against the existing ABObjectView;
it does not compare whole-registry versions or source labels.

Validation executed:

- 110 relevant admission, compiler, prompt, identity and recorded-canary tests
  passed.
- A full suite passed 366 tests, including concurrently authored dashboard
  tests. That count is not attributed entirely to this two-file repair.
- `./scripts/run_precommit.sh`, both O1 example freshness checks, the canonical
  documentation check and `git diff --check` passed before receipt finalization.
- Fresh [primary](2026-10-08_uah_r2_catalog_primary_review.md) and
  [distinct-model second](2026-10-08_uah_r2_catalog_second_review.md) reviews
  returned APPROVE, each with zero blocking findings and zero nits. Their
  executed probes and comparison limitations are retained in those reports.

Reviewed source SHA-256:
`3d107015d02cf0faf7fb85e23c1c642c1f4064b1b5f05319ca2e7aa8f8db7c5c`.
Reviewed test SHA-256:
`3097ab6c04959d7730b9a2c1b2058abf0da6d1d773794f72d4a8860fbe8210a8`.

## Downstream public counterexample and controls

Run from the repository root:

```bash
PYTHONPATH=src .venv/bin/python docs/artifacts/reviews/2026-10-08_uah_r2_catalog_repros/owner_after_admission_probe.py
```

The retained probe uses public task ingress, admission and lease-only owner
execution with temporary ledgers. Fixture builders supply input data only.

| Case | Observed result after restart |
| --- | --- |
| Replace catalog semantics after valid admission, retaining binding identity | Prohibited `direct_speech` observation is accepted; task is accepted |
| Original catalog, same undeclared observed effect | Evidence rejects with `undeclared_observed_effect`; no terminal acceptance |
| Original catalog, declared successful observation only | Evidence and task are accepted |

This synthetic result proves an execution-boundary gap. It supplies no model,
native environment or hardware measurement. The owner lacks the admitted
semantic snapshot, and the persisted compiled-task projection cannot recover
it. The admission check alone does not fix post-admission replacement.

GRILL has the choice between a versioned admitted-object snapshot and durable
complete compiled-artifact resolution. Human direction is pending. No owner
constructor, admission schema or artifact store was changed in this round.
Both review approvals cover only the two-file admission delta. H0/H1 exit,
provider qualification and global SPEC-03 closure remain unscored or open.

## Round close and retained provenance

Closed at 16:39 Europe/Madrid, within the 16:41 target. HEAD and branch remain
unchanged; no files were staged, committed or pushed. The isolated
[zero-context repair patch](2026-10-08_uah_r2_catalog_semantic_fencing.patch)
passed `git apply --reverse --check --unidiff-zero` against the reviewed bytes.
Canonical Markdown/HTML were regenerated; pre-commit and subsequent canonical
and whitespace checks passed. The end manifest pins the final artifacts.

The R1 receipt's second-review table retains an older report hash
`d39502b9b65e03051925eb4cfe1596bf7cf725dfeb3763b26f8fe56a6e35f462`.
The retained report and R1 end manifest instead agree on
`85a97f05f2ec16668acf7fc310277558908820bcd98d780416fc7ea469c6b284`.
Its reviewed source hashes remain unchanged. The reason for the report-byte
difference is not established here; historical receipt values were not replaced.
This is a provenance discrepancy, not evidence of a new runtime approval.

Post-close navigation amendment at 16:47 Europe/Madrid: the subsequent
[read-only provenance check](2026-10-08_uah_r1_report_provenance_check.md)
could not recover the original report bytes. Exact transformation and materiality
remain unknown. The round-end manifest pins the pre-amendment receipt bytes;
the source/test review scope and hashes are unchanged.
