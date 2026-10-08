# Independent Standards review

## Standards summary (under 400 words)

Two introduced BLOCKING findings require changes. No NIT is raised.

1 of the 2 found so far. **STD-PILOT-01, BLOCKING:** `src/ab_harness/model_invocation.py:366-367` trusts overridable artifact verification and subsequently passes the original prompt object to the provider. A `CompiledPrompt` subclass can serialize an authentic prompt while exposing different actual messages. The candidate calls the provider once with forged messages, records the authentic messages and prompt identity, and returns `RawModelOutput`. Expected: reject the mismatched concrete content before provider work or budget consumption. The base lacks this invocation seam.

2 of the 2 found so far. **STD-PILOT-02, BLOCKING:** `src/ab_harness/schema_validation.py:139` does not require a boolean `allow_additional_properties`; line 205 interprets it through truthiness. The string `"false"` admits undeclared arguments, obtains a lease, dispatches once, and produces a successful receipt. Boolean `False` rejects those same arguments. Expected: reject a non-boolean policy value at schema construction/verification. The base lacks this schema seam.

All five REVIEW principles:

- Separation of concerns: OK. Semantic admission, domain leases, owner evidence, and ledger projection remain distinct.
- Programming by intention: violation STD-PILOT-02 at `schema_validation.py:205`.
- Encapsulation: violation STD-PILOT-01 at `model_invocation.py:366-367`.
- High cohesion: OK. No additional writable task owner or duplicated eligibility policy was found.
- Low coupling: OK. AST checks find no prohibited direct imports in the changed portable modules.

Candidate scoped tests: **458 passed**. Available matching base tests: **93 passed**. Public probes precede implementation inspection; green tests did not cover the two reproduced defects. Findings concern H0/H1 contract and invocation boundaries, not live NAO/provider qualification. Scope is the frozen 36-path manifest only, with 13 selected paths and two O1 outputs treated as integration context, not additional approvals. Requested reviewer policy is `gpt-6.1-sol/max`; runtime model/effort is not independently attested. The different-model requirement remains unverified by this reviewer.

## Evidence appendix

### Frozen inputs and independence

- GO: 2026-10-08 19:38:17 UTC; hard stop: 19:58:17 UTC.
- Base: parent-supplied exact `06f5a29` export at `/tmp/uah-pilot-review-before`.
- Candidate: `/tmp/uah-pilot-review-candidate`.
- Scope: `/tmp/uah-pilot-preparation/review36.paths`, SHA-256 `7c708b650a41c33bbabdc28e66155df9ac81080c9b670ebcff769c5d3090fa93`.
- Integration hashes: `/tmp/uah-pilot-preparation/candidate51.sha256`, SHA-256 `8496f56f6b95d224d6779f1236b25d65370580a7fdc792d2b569314cb450263b`.
- Integration modes: `/tmp/uah-pilot-preparation/candidate51.modes`, SHA-256 `29ed895310747746b7c5dc846a1fe901bca026697265a34698be2254689999c7`.
- Immutable predeclaration: `/tmp/uah-standards-predecl-y4p10t/PREDECLARATION.md`, SHA-256 `b9ff4fca04986f9d27505ee830006a71515c9ff09e558d95fa9738aedbc9fd36`, unchanged after execution.
- Disposable execution trees: `/tmp/uah-pilot-standards-result/execution/before` and `execution/candidate`.

The reviewer read REVIEW.md first and sealed the input families before any implementation, test, or diff read. Governing AGENTS.md, CONTEXT.md, relevant foundation/masterplan sections, and current-state development-log sections were then read from the separate frozen governing directory. Public constructor/signature introspection and observations through public NAO factories mapped the sealed cases to concrete APIs. Initial fixture mapping failures are preserved in the intermediate JSON files; they are not findings. Public corpus results existed before source inspection. The two focused reproductions apply the predeclared nested-artifact and alternate-scalar families after source inspection, without claiming they were complete initial probes.

No writer narrative or another reviewer's conclusions were supplied or consulted. No other reviewer/chat was contacted. No shared source, docs, index, frozen tree, hooks, staging, commit, or push was changed. No fake Git metadata was needed. All execution mutations were confined to disposable copies and temporary fixture files.

### Governing standards and ownership

- AGENTS.md: portable core imports no ROS, NAO, provider SDK, or runtime products; typed proposals do not decide execution or effect truth; discovery is not authorization; release claims remain separate.
- CONTEXT.md, Prompt compiler, Model invocation, Admitted operation, Execution lease, and Lifecycle ledger: immutable artifacts pin exact prompt/task/binding lineage; the ledger records decisions and projections do not become independent owners.
- Foundation, two-stage admission and prompt compilation: finite canonical arguments and reviewed input-schema validation precede semantic admission; invocation records the exact prompt and lease.
- REVIEW.md sections 2, 4, 5, and 6: execute before reading, compare with base, do not silently resolve unknown data, report all principles, and attack gates with alternate input forms.
- Applicable UAH guardrails: content-addressed authority artifacts reverify their own content and nested artifacts at trust crossings. Similar hash syntax alone does not justify shared canonicalization.

Affected release gates are H0/H1. `SemanticAdmission` owns schema-gated operation eligibility, the domain owner owns leases/effects, `ModelInvocationAuthority` owns call admission and atomic accounting, and `LifecycleLedger` owns writing/replay. No H0/H1 release closure, H2 parity, provider connectivity, or live hardware claim follows.

### STD-PILOT-01: exact reproduction

Run in each disposable tree:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python /tmp/uah-pilot-standards-result/prompt_boundary_repro.py
```

Input: a ready leased actor and compiler-issued prompt from the existing fake-provider fixture. Construct a `CompiledPrompt` subclass whose `verify_identity()` is a no-op and `to_dict()` returns the authentic prompt payload; mutate only its actual messages to `Review-forged instruction outside recorded prompt.` and `Review-forged task input.`. Invoke the public `ModelInvocationAuthority.invoke` with that object.

Expected: the trust crossing verifies concrete content or consumes a verified detached representation; mismatched artifact bytes reject before a provider call and model-call debit.

Base observation: `{"public_seam_absent":"ab_harness.model_invocation"}`. This is a newly introduced surface, not a pre-existing defect.

Candidate observations, saved in `prompt_boundary_candidate.json`:

- `provider_calls`: 1.
- Provider actual messages: the two forged strings above.
- Recorded messages: authentic kernel/domain/task wording.
- Recorded and authentic prompt ID: `compiled-prompt:sha256:03d3add34d5421a54c72ecc8079214520f09b96782c502fba5e22f8a42a81624`.
- `provider_and_recorded_bytes_agree`: false.
- `result_type`: `RawModelOutput`.

The request constructor also uses the virtual verification at `model_invocation.py:58-59`. The provider sees the supplied object's actual fields, while hashing/persistence consume its overridable serialization. The mismatch breaks exact invocation provenance and the claim that the recorded artifact identifies what the provider consumed. This does not itself demonstrate a downstream native-operation admission bypass. Fix ownership belongs at the invocation artifact/trust crossing; a fresh independent review is required for any repair.

### STD-PILOT-02: exact reproduction

Run in each disposable tree:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python /tmp/uah-pilot-standards-result/schema_flag_repro.py
```

Input: one schema with only required string property `value`, plus arguments `{"value":"review","review_extra":"unreviewed"}`. Compare `allow_additional_properties=False` with `allow_additional_properties="false"`. Run normalization, semantic admission, domain leasing, and a fake owner through public APIs.

Expected: reject the non-boolean control value. Boolean False should reject the extra property, without dispatch.

Base observation: both cases report `public ab_harness.schema_validation seam absent`.

Candidate observations, saved in `schema_flag_candidate.json`:

- Boolean False: `ValueError`, `public semantic rejection: ('proposal_arguments_schema_invalid',)`.
- String `"false"`: admission ID `admission:sha256:3ba095a52df787f04db40596c66008afdf2ea1ae90ec171b4082f5a80bb7e5b0`; one handler call with the complete arguments, including `review_extra`; successful receipt.

The broader matrix also accepts string `"true"` and integer 1 as permission-bearing policy values. Unknown policy types acquire meaning through Python truthiness. Require the boolean field's domain type when issuing and reverifying the schema, then preserve that check at consumers.

### Other public before/after observations

The latest complete corpus is `public_probes.py`, with outputs `public_before_authority_extended.json` and `public_candidate_authority_extended.json`.

| Predeclared input family | Before | Candidate |
| --- | --- | --- |
| Raw caller-created TaskStartedFact | Appends task_started | ValueError: new starts require an authority-bound task-start command |
| TaskBudgets(-1,-1,-1), (0,0,0) | Rejects | Rejects |
| TaskBudgets(1,1,1) | Accepts | Accepts, retry_attempts=0 |
| Boolean True and non-finite budget quantities | Accepts True/NaN/infinity | Rejects as non-integer limits |
| Unsupported schema type spellings, numeric/boolean forms | Schema seam absent | Rejects |
| Schema value-type matrix | Schema seam absent | Distinguishes booleans from integer/number; direct number-schema validator accepts NaN/infinity under its canonical-argument precondition |
| A/B, B/A, A/A edges and unknown relation spellings | Edge seam absent | A/B and B/A same-frame edges accepted; self-edge/unknown spelling rejected; same-frame delegation rejected |
| Invalid leap day and timezone-naive ingress timestamp | Accepts strings | Accepts strings unchanged |
| Empty ingress timestamp | Rejects | Rejects |
| Null ingress timestamp | AttributeError | AttributeError |
| Outer identity and nested admitted owner tampering | New schema/current-snapshot fixture unavailable | Rejects modified proposal, compiled task, admitted owner, and pack identity |
| Admission wire markers v1, v2, v3, unknown | Current snapshot fixture unavailable | Accepts v3 only |
| Exact lease consumed twice | New schema/current-snapshot fixture unavailable | First receipt succeeds; repeat rejects: execution lease already consumed |
| Owner in another environment | New schema/current-snapshot fixture unavailable | Rejects: execution lease belongs to another environment |
| Public NAO smoke | Report passes accept/reject/replay checks | Report passes, adding an explicit required-effect-failure counterexample; its acceptance is rejected |

Invalid date acceptance and null-type error quality are baseline observations, not introduced findings. The initial budget-idempotence probe used a subject without current semantic provenance and correctly rejected; it does not establish alternate-scalar replay coverage. No additional finding is inferred from that invalid fixture. Unit-bearing magnitude conversion is outside these typed seams; wall-time quantities are declared integer seconds and string/numeric alternatives were exercised.

### Executed checks and coverage limits

Both test runs use the same 36-path selection, retaining only existing `tests/` paths in each tree:

```bash
mapfile -t paths < /tmp/uah-pilot-preparation/review36.paths
args=()
for path in "${paths[@]}"; do
  if [[ "$path" == tests/* && -f "$path" ]]; then args+=("$path"); fi
done
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q "${args[@]}"
```

- Candidate: all 22 scoped test modules, 458 passed in 11.06 seconds.
- Before: available matching test modules, 93 passed in 0.57 seconds. An earlier attempt named a nonexistent new test and ran zero cases; it was corrected to the existence-filtered command above.
- AST parsing/compilation: 14 scoped source files compile; no prohibited direct imports in changed portable core modules. `static_checks.txt` preserves the observation.
- `git diff --no-index --check /tmp/uah-pilot-review-before/src /tmp/uah-pilot-review-candidate/src`: no whitespace diagnostics; exit 1 denotes differing trees.
- `sha256sum -c /tmp/uah-pilot-preparation/candidate51.sha256` against the frozen candidate: all 51 checks OK.
- `candidate51.modes` versus `stat -c %a`: no mismatches.

Manual inspection covered the 14 scoped source modules, their trust crossings and NAO result/message consumers. The candidate's scoped tests exercise restart, competing writers, v1/v2/v3 compatibility, active admission provenance, cancellation, timeout, retry exhaustion, effect closure, and read-only Observatory projections. They were executed, but this bounded review did not inspect every test-body hunk in the 7,436-line test delta. Neither every reason-code combination nor every downstream consumer was independently reprobed through a custom public fixture. No complete Cartesian product, live provider, live robot, hook installation, repository pipeline, release gate, or held-out qualification was run. These are explicit coverage limits, not evidence of success.

No separate Fowler-smell finding was established. Static operation eligibility has one owner and is reused by PromptCompiler; per-artifact hash helpers implement different serialized contracts, so their similar syntax is not a duplication finding.

### Possible finite split units (proposals only)

- Schema gate: `schema_validation.py` plus `test_argument_schema_validation.py`, after STD-PILOT-02 repair and fresh review.
- Invocation provenance: `model_invocation.py` plus `test_model_invocation.py`, with `prompt_compiler.py` and its matching test only if the repair actually changes their boundary; STD-PILOT-01 remains blocking.
- Task ingress projection: `environment_ingress.py`, `task_ingress_authority.py`, `task_registry.py`, and their matching ingress/compiler tests, retaining the selected ledger context as an explicit dependency.

These are logical review-sized units, not independently importable or authorized commit selections. The selected INDEX context and all shared import/ledger dependencies must be reconciled explicitly. No blanket approval of the 51-path integration or the human-selected 13-path partial tree is given. Both independent gates and direct human staging/commit authority remain necessary.

VERDICT: CHANGES
