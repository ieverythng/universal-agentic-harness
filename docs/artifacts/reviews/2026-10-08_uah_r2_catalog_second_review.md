# R2 catalog semantic fencing: independent second review

Date: 2026-10-08. Scope: the two-line production addition in
`src/ab_harness/proposal_admission.py` and the two added tests in
`tests/test_two_stage_admission.py`, relative to the frozen dirty-before files
in `/tmp/uah-r2-catalog-20261008/`. No other dirty-tree changes are approved.

Requested reviewer configuration: `gpt-6-astra` at `max`. Actual deployment
identity is not observable to this reviewer. This is a fresh reviewer that did
not write the implementation and did not inspect the writer handoff, development
log, rationale, or other reviewer reports. The review used `REVIEW.md`, the
standards/spec axes of the code-review skill, and UAH guardrails. No additional
reviewers were spawned within this independent review.

## Pins and authority

- HEAD: `28fab5e7f2c244d86a64c371f2118017999b2387`.
- Current production SHA-256: `3d107015d02cf0faf7fb85e23c1c642c1f4064b1b5f05319ca2e7aa8f8db7c5c`.
- Current test SHA-256: `3097ab6c04959d7730b9a2c1b2058abf0da6d1d773794f72d4a8860fbe8210a8`.
- Frozen-before production SHA-256: `8990fe6b9acbd6fca67a7185f64c7ccf2b3af5f5be5005582cb2d213e206a667`.
- Frozen-before test SHA-256: `1b0861e6a2d86537d888a7deac0bc1bcd6abc63606cb16f3d2979ffd0e3c3f7e`.

The current hashes were checked again after execution and were unchanged.
This affects the H0-H1 semantic-admission seam. The compiled task owns the
task-scoped object semantics. The catalog supplies approved implementation
bindings, and the domain owner separately owns execution authority. The
guardrail assessment checked that discovery remains non-authoritative, AB
coordinates remain frame-relative, and semantic rejection grants no lease or
effect evidence. This is not SPEC-03, H0/H1 closure, or release approval.

## Predeclared adversarial inputs

Before implementation inspection, the reviewer sent the parent this test plan:
empty, single, and multiple catalog rows with reversed order; alternate binding
keys and coordinates; combined stale/unknown references; the same semantic
object with different approved implementations; unknown, forged, stale, and
ambiguous selection; rejection/ledger consumers; content mutation; and exact
frozen-before versus HEAD comparisons with missing APIs reported honestly.
The unchanged positive public admission was executed before implementation
inspection. The remaining adversarial probes were executed after the diff was
read, using the predeclared categories. No unit conversion, date arithmetic, or
timestamp policy is changed by this delta; no new date/unit claim is made.

## Executed controls and results

Commands used `.venv/bin/python`. Independent probes loaded the existing
`_admission_fixture`, `_proposal`, and `_semantic_admission` helpers with
`runpy.run_path`, then called the public `SemanticAdmission.admit(compiled,
proposal)` seam. The frozen-before production module was executed in an
isolated in-memory module, with the same current dependency/fixture objects.
It was not substituted into the working tree.

Each catalog below was built with `BindingCatalog(RegistrySnapshot(objects,
source="synthetic:second-review", version="independent-label"), bindings)`.
The selected object was `find_object`; its original binding was
`nao_fake.find_object.v1`, approved for `fake` in `nao_fake`.

| Input and expected result | Frozen before | Current actual |
| --- | --- | --- |
| Original catalog: accept original binding | Accepted | Accepted |
| Empty registry and no bindings: reject | `binding_unavailable` | `catalog_object_mismatch` |
| Same object, no binding: reject | `binding_unavailable` | `binding_unavailable` |
| Object field changed to `ab_level=2`: reject semantic drift | Accepted | `catalog_object_mismatch` |
| `kind="contract"`: reject drift | Accepted | `catalog_object_mismatch` |
| `category="control"`: reject drift | Accepted | `catalog_object_mismatch` |
| `owner_package="different_owner"`: reject drift | Accepted | `catalog_object_mismatch` |
| `expected_effects=("direct_speech",)`: reject drift | Accepted | `catalog_object_mismatch` |
| `observable_success=("direct_speech",)`: reject drift | Accepted | `catalog_object_mismatch` |
| `decomposes_to=()`: reject drift | Accepted | `catalog_object_mismatch` |
| `runtime_callable=False`: reject drift | Accepted | `catalog_object_mismatch` |
| Combined `owner_package="x"` and prohibited expected effect: reject | Accepted | `catalog_object_mismatch` |
| Same object, new approved ID/revision/locator: accept new binding | Accepted v2 | Accepted v2 |
| Two approved fake bindings, both orders: reject ambiguity | `binding_unavailable` | `binding_unavailable` |
| Approved v1 plus candidate v2, both orders: select v1 | Accepted v1 | Accepted v1 |
| Approved fake v1 plus approved live-only v2, both orders: select v1 | Accepted v1 | Accepted v1 |
| Selected object plus unrelated object exposing prohibited effect, both orders: accept selected object | Accepted v1 | Accepted v1 |

The v2 binding used `binding_id="nao_fake.find_object.v2"`,
`source_revision="fixture-rev-2"`, and
`locator="fake_nao.skills_v2:find_object"`. Its semantic object was unchanged.
Thus the guard does not accidentally freeze the implementation locator or the
registry source/version label.

Additional executed controls:

- Replacing a proposal's `compiled_task_id` with `compiled-task:forged`, or its
  `object_id` with `unknown`, while retaining its identity raised the expected
  `ValueError: typed proposal identity does not match content`.
- A real task-ingress decision, compilation, proposal, and drift rejection were
  recorded into a temporary file-backed ledger and reloaded. Artifact reasons
  were `("catalog_object_mismatch",)`; ledger reasons were
  `["catalog_object_mismatch"]`. Replay returned failure stage
  `semantic_admission`, terminal status `None`, and exactly the event sequence
  `task_started`, `task_compiled`, `proposal_normalized`,
  `semantic_admission_rejected`. No lease or execution event existed.
- `render_observatory` over that reloaded ledger contained the exact reason
  `catalog_object_mismatch` in its HTML. The typed reason reaches the user-facing
  event representation; it is not relabeled terminal task failure.
- Replacing rejection reasons with `("binding_unavailable",)` raised the
  expected `ValueError: semantic rejection identity does not match content`.
- Both newly added tests were executed against the frozen-before admission
  module. The drift-rejection test failed with `AssertionError`; the
  same-object/reviewed-binding-change test passed. The current implementations
  of both tests passed in the suite.
- Exact HEAD production source was loaded separately. Calling its constructor
  with the current `schema_validator` argument raised
  `TypeError: SemanticAdmission.__init__() got an unexpected keyword argument
  'schema_validator'`. Using its actual legacy API with the current fixture,
  both the original object and prohibited-effect drift were accepted. This
  compares the older admission algorithm only, not an isolated full HEAD tree
  or current input-schema qualification.
- `.venv/bin/python -m pytest -q tests/test_two_stage_admission.py`: **48 passed**.
- `.venv/bin/python -m pytest -q tests/test_two_stage_admission.py
  tests/test_lifecycle_ledger.py tests/test_observatory.py`: **81 passed**.
- `git diff --check -- src/ab_harness/proposal_admission.py
  tests/test_two_stage_admission.py`: passed.

## Standards and design principles

1. Separation of concerns: **OK**. SemanticAdmission owns the comparison;
   BindingCatalog continues to own binding selection. Domain lease authority
   is unchanged.
2. Programming by intention: **OK**. The direct object comparison and typed
   `catalog_object_mismatch` reason state the guarded condition.
3. Encapsulation: **OK**. Production code uses public `object_for`; it does
   not inspect catalog internals or duplicate registry storage.
4. High cohesion: **OK**. The guard is adjacent to binding resolution after
   compiled-task semantic checks, with focused regression tests.
5. Low coupling: **OK**. No provider, ROS, NAO, UI, or runtime-product dependency
   is introduced. Existing generic rejection and ledger consumers retain
   their ownership and carry the new reason.

## Spec assessment, findings, and limits

The narrow behavior matches the stable-semantic-object and replaceable-approved-
binding contract. The implemented comparison closes the tested catalog drift
path without granting execution authority or treating registry labels as
semantic identity. No duplicated domain owner or blocking design violation was
found in the delta.

Findings: **0 BLOCKING, 0 NIT**. There are no numbered findings to enumerate.

Downstream binding changes after admission, hostile replacement of catalog
methods, broad artifact integrity, full holdout qualification, provider paths,
and existing ledger/owner gaps are outside this two-line delta review. No source,
skill, hook, provider, or Git mutation was performed. The hook suite and renderer
were not executed by this reviewer; this report is the only repository write.
The next discriminating qualification is separately scoped downstream
admission-to-lease binding consistency, not expansion of this verdict.

VERDICT: APPROVE
