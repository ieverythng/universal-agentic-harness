# R2 catalog primary independent review

## Frozen scope and predeclared probes

Scope is only the current delta in `src/ab_harness/proposal_admission.py` and
`tests/test_two_stage_admission.py` against the exact dirty-before snapshots in
`/tmp/uah-r2-catalog-20261008`. HEAD is
`28fab5e7f2c244d86a64c371f2118017999b2387`.

The following probes were declared before reading the implementation or diff:

1. Unchanged approved binding: admit, preserve captured binding/schema/evidence
   identity, obtain domain lease, and retain normal rejection controls.
2. An exact catalog match represented by a different Python object: accept;
   caller object identity must not determine semantic authority.
3. Approved, candidate, missing, duplicated, and reordered bindings: only an
   exact uniquely authoritative approved record can resolve.
4. Catalog-versus-registry semantic drift: individually alter owner, frame,
   level, effects, evidence policy, schema, lifecycle status, and binding object
   relation; reject semantic changes even when an identifier still matches.
5. Combine drift with alternate binding revision/owner or multiple records;
   validate both record orders and ambiguous alternatives.
6. Registry/catalog replacement after gate construction and caller mutation of
   nested collections: a constructed gate must not silently widen authority.
7. Inspect every newly introduced rejection reason through admission, ledger
   serialization/replay, and the read-only O1 projection where applicable.
8. Compare current behavior with the frozen dirty-before source and the pinned
   base where feasible. A base lacking a current API is a compatibility gap,
   not evidence of byte parity.

No writer rationale, receipts, development log, or other reviewer report was
read. Requested review model is `gpt-6.1-sol` at `max`; no fallback was
reported. Actual model identity is not independently observable here.

## Identity and method

Current hashes were verified before execution and again after execution:

| File | SHA-256 |
| --- | --- |
| `src/ab_harness/proposal_admission.py` | `3d107015d02cf0faf7fb85e23c1c642c1f4064b1b5f05319ca2e7aa8f8db7c5c` |
| `tests/test_two_stage_admission.py` | `3097ab6c04959d7730b9a2c1b2058abf0da6d1d773794f72d4a8860fbe8210a8` |
| Frozen-before admission | `8990fe6b9acbd6fca67a7185f64c7ccf2b3af5f5be5005582cb2d213e206a667` |
| Frozen-before tests | `1b0861e6a2d86537d888a7deac0bc1bcd6abc63606cb16f3d2979ffd0e3c3f7e` |

The implementation delta is two lines at
`src/ab_harness/proposal_admission.py:827`, followed by two new tests at
`tests/test_two_stage_admission.py:560` and `:611`. Other dirty-tree changes
are not attributed to R2.

The repository review contract and UAH authority guidance were read first.
Public signatures and the existing fixture were inspected without displaying
implementation source. The initial matrix executed before the full source or
diff was read. The frozen-before and HEAD modules were evaluated in separate
in-memory module namespaces, without modifying checkout files. Tests used
`PYTHONDONTWRITEBYTECODE=1` and disabled pytest's cache provider. Durable replay
probes used temporary directories. No Git, hook, provider, or live environment
state was mutated. The only saved file is this report.

HEAD lacks the current `schema_validator` constructor parameter. The first
direct invocation explicitly reported that incompatibility. A subsequent HEAD
probe used its supported constructor. It accepted exact objects and semantic
effect drift. HEAD also accepted an unavailable schema reference, whereas both
dirty-before and current rejected it. That schema difference predates R2 and
is not evidence for R2 correctness or complete HEAD/current parity.

## Public behavior and alternative attacks

For each case, the fixture supplied a real compiled task and typed proposal.
Catalog objects were independently constructed using `dataclasses.replace`,
`RegistrySnapshot`, and `BindingCatalog`; object pointer identity was not reused
for the exact-match control. Expected current results below were observed.

| Input | Expected and actual current | Frozen-before |
| --- | --- | --- |
| Distinct object with equal fields | Admit | Admit |
| Remove expected effects | `catalog_object_mismatch` | Admit |
| Add prohibited `direct_speech` expected effect | `catalog_object_mismatch` | Admit |
| Remove observable success | `catalog_object_mismatch` | Admit |
| Change owner and matching implementation owner | `catalog_object_mismatch` | `binding_owner_mismatch` |
| Change level from 1 to 2 | `catalog_object_mismatch` | Admit |
| Change runtime callability to false | `catalog_object_mismatch` | Admit |
| Remove decomposition | `catalog_object_mismatch` | Admit |
| Change kind or category | `catalog_object_mismatch` | Admit |
| Missing catalog object | `catalog_object_mismatch` | `binding_unavailable` |
| Zero bindings | `binding_unavailable` | Same |
| Candidate, disabled, wrong runtime, or wrong environment binding | `binding_unavailable` | Same |
| Foreign implementation owner, unchanged object | `binding_owner_mismatch` | Same |
| Binding targets a different known object | `binding_unavailable` | Same |
| Drift plus candidate binding | `catalog_object_mismatch` | `binding_unavailable` |
| Two approved compatible bindings, either order | `binding_unavailable` | Same |
| Candidate plus approved, either order | Admit approved binding | Same |
| Two projected objects, either order | Admit selected object | Same |
| Reviewed revision and locator change, unchanged object | Admit | Same |
| Unknown input schema reference | `input_schema_unavailable` | Same |
| Empty input/output schema or evidence adapter | `binding_contract_incomplete` | Same |
| Duplicate binding IDs | Catalog construction rejects | Existing control |
| Duplicate object IDs | Registry construction rejects | Existing control |
| Replace tuple-valued effect/observable/decomposition field with a list | `catalog_object_mismatch` | Additional current-only representation attack |

The combined effect/observable drift in the new regression rejects before any
admitted operation exists. Running that exact new regression against
frozen-before failed its `admitted_operation is None` assertion, as expected.
The new reviewed-binding control passed against both versions.

The ordinary approved admission's complete `to_dict()` value, including
binding fingerprint, schema identity, obligations, and admission ID, was
identical between current and frozen-before:
`admission:sha256:85bab99bb172c0f3bdf009ee53285c98bcd197f6567d6c07cdf18f7c2302ed3e`.
This is tested parity for that admitted artifact, not a claim of global parity.

A registry entry changed after gate construction was rejected at the next
`admit` call with `catalog_object_mismatch`. This mutation probe deliberately
altered the registry's private lookup map; no public registry mutation API is
claimed. Catalog frame, schema, and evidence-policy fields are not members of
`ABObjectView`, so no nonexistent field was invented for the predeclared
semantic-object matrix. Input schema and evidence adapter alternatives were
tested through the actual binding contract. Frame identity remains the compiled
task's verified frame, not a new catalog frame check introduced by this patch.

## Reproduction and downstream visibility

The core matrix can be reproduced from the repository root without writes:

```python
import dataclasses
import importlib.util
from ab_harness.bindings import BindingCatalog
from ab_harness.registry import RegistrySnapshot

spec = importlib.util.spec_from_file_location(
    "fixture", "tests/test_two_stage_admission.py"
)
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
compiled, original_catalog, environment = fixture._admission_fixture()
proposal = fixture._proposal(compiled)
original = original_catalog.object_for("find_object")
changed = dataclasses.replace(original, expected_effects=("direct_speech",))
catalog = BindingCatalog(
    RegistrySnapshot((changed,), source="review", version="review"),
    original_catalog.bindings_for("find_object"),
)
decision = fixture._semantic_admission(catalog).admit(compiled, proposal)
assert decision.admitted_operation is None
assert decision.reason_codes == ("catalog_object_mismatch",)
```

Expected and actual for the new reason: a typed, content-addressed rejection;
coordinator recording preserves `reason_codes` as
`["catalog_object_mismatch"]`; disk reload reports
`failure_stage == "semantic_admission"` and `terminal_status is None`;
there is no domain lease or execution-start event. `render_observatory` on the
reloaded ledger contains the reason in both HTML and graph JSON. The HTML shows
it inside the existing expandable immutable-event payload, not an invented new
human-readable explanatory label. The gate remains non-writing and O1 remains
read-only.

One downstream limitation was also reproduced and is not introduced by R2:
after a valid admission and lease, replace only the catalog object's expected
effects through `catalog._registry._by_id["find_object"]`, keeping its complete
binding unchanged. `InProcessEnvironmentOwner.execute` still produces a
receipt. The same outcome occurred with the identical frozen-before admitted
artifact rehydrated as the current artifact class for ledger compatibility.
The rehydration is explicit; it is not a claim that frozen-before module
classes are directly interchangeable in the current ledger. If execution-time
semantic catalog identity is required, expected behavior would be rejection;
actual behavior remains receipt issuance in both cases. This existing private
mutation/TOCTOU seam is outside the two-line R2 delta and prevents a global
SPEC-03 closure claim. R2 proves catalog-versus-projection equality at semantic
admission only. It neither adds reviewed-binding promotion authority nor
removes owner/binding drift checks.

## Standards and design principles

1. Separation of concerns: OK. The comparison is in UAH semantic admission
   (`proposal_admission.py:827`), not domain execution, ledger, or UI code.
2. Programming by intention: OK. The comparison and typed
   `catalog_object_mismatch` reason directly express the admission invariant.
3. Encapsulation: OK. The change uses `BindingCatalog.object_for` and ordinary
   value equality, without reaching into catalog storage or adding a second
   registry owner.
4. High cohesion: OK. Both added tests exercise the same catalog/projection
   boundary and its compatible binding alternative.
5. Low coupling: OK. No new imports, provider dependencies, duplicate domain
   policy, or UI business logic were introduced. Existing dataclass value
   equality owns comparison across declared object fields.

The UAH guardrails influenced the scope and verdict: semantic authority remains
separate from domain lease issuance and owner evidence; discovery does not
authorize; AB levels remain frame-relative. This is H0/H1 admission evidence,
not H0/H1 completion, H2 qualification, live execution qualification, or global
SPEC-03 closure.

## Checks and findings

Executed:

- The predeclared public matrix above against current and frozen-before, with
  compatible HEAD probes explicitly separated from unavailable current APIs.
- Both new regressions against frozen-before: drift test red, compatible
  binding control green.
- Durable semantic rejection, read-only O1 rendering, and the existing
  post-admission semantic-object drift limitation.
- `python -m pytest -q -p no:cacheprovider tests/test_two_stage_admission.py
  tests/test_observatory.py`: 71 passed.
- `python -m pytest -q -p no:cacheprovider
  tests/test_argument_schema_validation.py`: 7 passed.
- Scoped `git diff --check`: passed.
- `python scripts/render_agentic_harness_docs.py --check`: passed.

An initial pytest command named nonexistent `tests/test_schema_validation.py`
and collected no tests. It was corrected to the actual argument-schema suite;
the failed invocation is not counted as validation.

In-scope findings: 0 BLOCKING and 0 NIT. No finding ordinals are emitted because
none were found in this delta. The existing downstream limitation above is an
explicit scope exclusion, not a newly introduced R2 defect. No hook suite was
installed or run during the isolated read-only review. Reviewed hashes remain
the pinned hashes recorded above.

VERDICT: APPROVE
