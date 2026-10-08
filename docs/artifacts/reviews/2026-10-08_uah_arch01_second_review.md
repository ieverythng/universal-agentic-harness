# ARCH-01 independent second review

Date: 2026-10-08. Scope: the frozen changes to `src/ab_harness/proposal_admission.py`, `src/ab_harness/prompt_compiler.py`, and `tests/test_prompt_compiler.py`, compared with their supplied exact `.before` files. This reviewer did not write those changes and did not read the writer's review, rationale, or execution receipts.

The requested distinct-model/highest-effort backend identity is not independently observable inside this reviewer. Model identity, effort, and distinctness therefore remain orchestration provenance to verify, not claims established by this report. Both Standards and Spec assessments and all five design-principle assessments below were performed by this reviewer.

## Contract and scope

The requested change is one pure, semantic-owned static object-eligibility rule consumed by prompt compilation and semantic admission. It includes projection membership, direct-control band, callability, prohibited expected or observable effects, and obligation presence. Stateful binding/schema checks and domain authority must retain their owners. No framework or artifact schema is requested.

The release boundary is H0 semantic admission consumed by H1 prompt compilation. The semantic owner is `SemanticAdmission`; `DomainLifecycleAdmission` and the environment owner retain execution authority. This is not H0/H1 closure or H2 qualification.

Governing material read: `REVIEW.md`, `AGENTS.md`, `CONTEXT.md`, the UAH guardrail skill, the foundation architecture, ADR 0001, relevant H0/H1 masterplan sections, and the prompt-compiler implementation entry in the development log. The code-review skill supplied the separate Standards and Spec axes. The supplied frozen snapshots replaced a branch comparison so unrelated workspace changes were outside the review.

## Executed evidence

[Inputs were predeclared](2026-10-08_uah_arch01_second_review_evidence/inputs.md) before reading the changed source or diff. The first execution was the documented public `python -m ab_harness_nao` control against two throwaway source trees. Both came from the same current `src`; the baseline replaced only the two implementation modules with the supplied `.before` files. A directory comparison confirmed those were the only source differences, excluding bytecode caches. Both test trees contained identical candidate tests. Imported module paths were checked explicitly.

| Execution | Candidate | Exact-before |
| --- | --- | --- |
| Recorded public NAO smoke | Passed | Passed, identical JSON and verified digest |
| Candidate `test_prompt_compiler.py`, `test_two_stage_admission.py`, `test_task_compiler.py`, `test_lifecycle_ledger.py` | 135 passed | 133 passed, 2 expected observable-only regression failures |
| Independent public-API matrix | 29 expected outcomes passed | 29 baseline outcomes passed |
| Serialized semantic decision comparison | All 29 admission/rejection artifacts identical to baseline | Reference |

The baseline failures were `test_prompt_compiler_excludes_an_operation_with_a_forbidden_observable` and the observable-only case of `test_prompt_and_admission_agree_on_task_prohibited_effects`. Both failed because the old compiler exposed the operation instead of raising, while semantic admission already rejected it.

Exact paired commands used `/home/juanbeck/universal-agentic-harness/.venv/bin/python` throughout. For each of `current` and `before`, the initial smoke ran from `/tmp` with `PYTHONPATH=/tmp/uah-arch01-second-review/<variant>/src` and `-m ab_harness_nao`. The test command ran from `/tmp/uah-arch01-second-review/<variant>`:

```bash
PYTHONPATH=src /home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_prompt_compiler.py tests/test_two_stage_admission.py tests/test_task_compiler.py tests/test_lifecycle_ledger.py
```

The independent script ran from `/tmp` with the same variant-specific `PYTHONPATH`, its absolute path under this report's evidence directory, and one positional argument, `current` or `before`.

The [independent probe](2026-10-08_uah_arch01_second_review_evidence/probe.py) constructs its own registry, domain pack, real ingress decision, task compilation, role configuration, bindings, schemas, examples, and proposals through public APIs. It does not call the new helper as its oracle. Its cases cover:

- Allowed effects; unrelated prohibition; exact case-sensitive effect identifiers; expected-only, observable-only, and combined prohibitions.
- Non-callability; inspect-only AB0; absent projection; forbidden output type; the combined ordered rejection sequence, including missing obligation.
- A callable decomposition with no task obligation; two required objects in both registry/request orders, with zero, one, or two eligible operations.
- Exact output-schema choices and required argument fields, task-narrowed output types, source-contract object IDs, and filtered example content/order. Repeated compilation is equal and private locators stay out of prompt artifacts.
- Missing, mistyped, and additional arguments; candidate/disabled bindings; wrong environment/runtime/owner; missing reviewed schema.

Six prompt outcomes change, all intended: observable-only prohibition for one object, missing obligation for a decomposition, and one/both observable-prohibited objects in each two-object order. All other prompt outcomes and all semantic decision artifacts match. The compiled read-only projection may still describe an ineligible object; the operation schema, source contracts, and operation examples exclude it. Inspection is not direct-proposal authority.

The paired two-stage/lifecycle tests also retain lease-only dispatch, domain revision and activation checks, duplicate/idempotent leasing, binding drift fencing, replay, and owner evidence behavior. No native runtime or provider was invoked.

## Standards

No BLOCKING or NIT findings.

1. **Separation of concerns: OK.** `proposal_admission.py:866` owns the pure static predicate. `prompt_compiler.py:358` consumes it without constructing an admission decision or touching execution authority. Stateful catalog, binding, and schema checks remain at `proposal_admission.py:946` and onward.
2. **Programming by intention: OK.** `static_object_rejection_reasons` names its scope and result. The prompt call site skips ineligible objects; the admission call site extends the existing reason sequence at `proposal_admission.py:935`. The method does not pretend to establish full admission.
3. **Encapsulation: OK.** Callers supply the frozen compiled task and object ID, not the semantic owner's private catalog or environment state. Existing public entry points reverify content identity before using the helper (`proposal_admission.py:910`, `prompt_compiler.py:314`). The helper returns an immutable reason tuple, not an authority artifact.
4. **High cohesion: OK.** Projection, band, callability, effect, and obligation eligibility are localized at `proposal_admission.py:866`. Admission's later obligation selection constructs the emitted evidence references; it is not a second eligibility policy. No new framework or schema was introduced.
5. **Low coupling: OK.** The prompt compiler adds one dependency on the existing portable semantic owner. No ROS, NAO, provider SDK, runtime product, stateful admission instance, or domain execution dependency is added. The static decision has one owner, with no duplicate condition cascade left in prompt rendering.

The Fowler smell baseline yielded no actionable issue in this bounded diff. Import/style checks enforced by tooling were not recast as review findings.

## Spec

No BLOCKING or NIT findings.

The helper preserves the original semantic checks and their order. The independent five-reason case returns `role_output_type_forbidden`, `object_inspection_only`, `object_not_runtime_callable`, `object_effect_prohibited`, then `missing_effect_obligation` in both versions. Projection failure preserves `object_outside_projection` before `missing_effect_obligation`.

Prompt compilation now uses the same union of expected effects and observable-success effects, and the same obligation requirement, before building operation schemas or examples. Mixed-object probes retain the eligible operation and remove only ineligible direct-operation content. Output ownership remains enforced by the task's output-type enum and semantic admission's proposal-level check. Binding resolution, schema validation, catalog equality, domain lease issuance, and owner evidence semantics are unchanged.

## Provenance, limits, and handoff

Candidate SHA-256 values, checked before and after probing:

```text
proposal_admission.py 033ba785928c9019b76711ed27c603b6f3f30a2e3110443875bdfea6af019888
prompt_compiler.py    9caaf597a1d08983f53f27672e425ba7971cc2b47e9ce0b099f0fa9ba5121ae1
test_prompt_compiler.py c04db4be3abc125e43ace67d4416a412f18c2288da8a30362ae85c199c63774b
```

Baseline SHA-256 values:

```text
proposal_admission.py.before a2a76bf21eb865934d63b5eeece722b4b7827d659421fb7a5bc566bb3161455c
prompt_compiler.py.before c76d829b9e6b9e04c6856fcb35ce6f61e26953f881a27cdd3ef79e1016a34b82
test_prompt_compiler.py.before 53b19f5e5d9d8c05d5b328034b54874d58e6e35924aa7b543e672d55f47eb183
```

[Candidate results](2026-10-08_uah_arch01_second_review_evidence/current.json), [baseline results](2026-10-08_uah_arch01_second_review_evidence/before.json), and the [comparison](2026-10-08_uah_arch01_second_review_evidence/comparison.json) retain exact schemas, source contracts, artifacts, and messages. Initial controls, paired pytest output, and imported paths are retained beside them. Ruff check/format-check passed on the independent probe; scoped `git diff --check` passed. The parent owns repository hooks and renderer checks. No source, Git, provider, or external authority changes were made by this reviewer.

No evidence gap remains for this bounded static-eligibility assessment. Broader authority provenance, complete release qualification, and backend model attestation remain outside its result. The next action is the parent's final hook/renderer gate and orchestration-provenance check, not another code-fix round. Units, calendar boundaries, new enum consumers, hooks, and exemptions are not changed by this diff.

Standards: 0 findings. Spec: 0 findings. No worst issue exists within either axis.

VERDICT: APPROVE
