# SPR-02 contract coverage

Pre-edit inventory of the cumulative local source based on main
`5e6734173f2f755430f85e2fbe7d937bfbaa8b7d` plus the exact accepted SPR-01
fourteen-path dependency. Acceptance is not a merge. H0/H1/O1/H2 remain open.
This is a coverage map, not a complete schema or release-qualification claim.

## Owner and contract inventory (before code edits)

I = implemented; T = existing public tests located, not qualification;
P = proposed target grammar; U = unknown/owner decision still open.
A missing loader is explicitly absent, never an invented generic serializer.
Paths below are relative to the product root.

| Family | Status / owner | Schema, encoding, export/load, identity and versions | Public consumers / controls | Open row |
| --- | --- | --- | --- | --- |
| HarnessSpec | P; architecture owner | Foundation target `ab_harness/v0` YAML example only; no source type, exporter, loader or verifier found | Architecture planning only | U: executable serializer/version policy |
| TaskSpec | I/T; task_compiler | `TASK_SPEC_SCHEMA=uah.task_spec/v2`; nested canonical compiled payload; no standalone to_dict/from_dict or independent identity | TaskSpecCompiler; tests/test_task_compiler.py | No standalone wire contract promised |
| CompiledTask | I/T; task_compiler | `COMPILED_TASK_SCHEMA=uah.compiled_task/v2`; sorted compact finite JSON SHA-256; to_dict, verified_copy, verify_identity; no public from_dict; legacy v1 replay-only policy remains unchanged | proposal_admission, prompt_compiler, runtime_controls, lifecycle; compiler/two-stage/content-identity tests | Export/reload means existing ledger replay, not a new task loader |
| ModelProfile | P/U; architecture owner | No implemented ModelProfile source contract or serializer found; NOT ModelConfiguration | Target model policy only | Owner must define profile schema/version/consumer |
| ModelConfiguration | I/T; agent_configuration | Literal `uah.model_configuration/v1`; local canonical JSON identity; to_dict/from_dict/verify_identity reject unsupported version | registries, model_allocator, prompt_compiler, model_invocation; tests/test_agent_configuration.py | Configuration does not implement ModelProfile |
| EnvironmentProfile | I/T; environment_profiles | Frozen value, no schema constant, canonical exporter/loader or content ID; registry verifies concrete detached fields | EnvironmentRunRegistry, ingress authority; tests/test_environment_runs.py | U: portable wire/version policy |
| Environment run | I/T; environment_runs | Owner attestation and registry; no standalone versioned exporter/loader/identity verifier | TaskIngressAuthority, owner dispatch, actor lifecycle; environment-run/ingress tests | U: standalone wire/version policy; registration is not startup |
| Environment ingress | I/T; environment_ingress + task_ingress_authority | `ENVIRONMENT_INGRESS_SCHEMA=uah.environment_ingress/v1`, `TASK_INGRESS_DECISION_SCHEMA=uah.task_ingress_decision/v1`; sorted compact finite JSON IDs, to_dict/verify_identity; no public from_dict | common ledger, task registry/compiler; ingress/boundary/issuance tests | Preserve strict fresh issuance and historical unavailable None |
| AB views / bindings | I/T; contracts + bindings | ABObjectView/ABImplementationBinding are values; no standalone schema/exporter/loader/content verifier; bindings.binding_fingerprint hashes sorted compact finite JSON of the complete binding; nested frozen snapshots in compiled/admitted artifacts | registry, projection, semantic/domain admission, environment owner; binding/core/two-stage tests | output_schema_ref is a reference, NOT executable output validation |
| Proposal / admission | I/T; proposal_admission + domain_lifecycle | `uah.typed_proposal/v1`, `uah.proposal_normalization_rejection/v1`, `uah.admitted_operation/v3`, `uah.semantic_admission_rejection/v1`, `uah.execution_lease/v1`, `uah.domain_admission_rejection/v1`; local sorted compact finite JSON IDs; to_dict/verify_identity; public from_dict on AdmittedOperation and normalization rejection only | normalizer, SemanticAdmission, DomainLifecycleAdmission, owner, ledger; argument-schema/two-stage/nested-owner tests | Unsupported active v2 rejects; no generic compatibility codec |
| Execution receipt | I/T; environment | `EXECUTION_RECEIPT_SCHEMA=uah.execution_receipt/v1`; local canonical finite JSON content ID; to_dict/from_dict/verify_identity | completion, evidence adapter, common ledger; tests/test_two_stage_admission.py | Valid output alone is not effect evidence |
| Effect evidence / owner result | I/T; contracts + environment + acceptance | EffectEvidence/OwnerExecutionResult values have no standalone schema/content ID/loader; nested receipt canonicalization and owner validation; `uah.evidence_rejection/v1` owned by environment | TaskAcceptanceEvaluator, execution completion/replay; tests/test_task_acceptance.py and two-stage tests | U: new freshness/output semantics require owner decision |
| Trace schemas | I/T; lifecycle | `TRACE_EVENT_SCHEMA=uah.trace_event/v1`, `SCOPED_EVENT_SCHEMA=uah.trace_event/v2`, `VERIFIED_TRACE_DIGEST_SCHEMA=uah.verified_trace_digest/v1`, `COMPILED_TASK_OBLIGATIONS_SCHEMA=uah.compiled_task_obligations/v1`; strict canonical JSONL; TraceEvent.to_dict/from_dict/verify_identity, digest to_dict/from_dict; common ledger replay | task registry, runtime controls, acceptance, read-only Observatory; tests/test_lifecycle_ledger.py and historical/content-identity controls | Preserve authentic raw fixtures and legacy replay identities |

## Supporting implemented contracts

| Owner contract | Schema / canonical encoding / public round-trip interface | Consumers and compatibility |
| --- | --- | --- |
| DomainContractPack, domain_contracts | `DOMAIN_CONTRACT_PACK_SCHEMA=uah.domain_contract_pack/v1`; local sorted compact finite JSON revision, issue/to_dict/verify_identity/verified_copy; no public from_dict | Compiler, ingress and prompt source ownership; unsupported versions reject, no new loader |
| ObjectArgumentSchema, schema_validation | `OBJECT_ARGUMENT_SCHEMA_VERSION=uah.object_argument_schema/v1`; local sorted compact finite JSON schema ID, issue/verify_identity and registry resolution; no public to_dict/from_dict | Semantic admission and PromptCompiler; exact schema identity/revision, no output-schema validator inferred |
| BudgetDecision, runtime_controls | `BUDGET_DECISION_SCHEMA=uah.budget_decision/v1`; local sorted compact finite JSON decision ID, issue/to_dict/verify_identity; no public from_dict (ledger owns reconstruction) | Lifecycle ledger, budget authority, execution/invocation starts and read-only Observatory; exact integers, unsupported versions reject |

## Budget quantities and policy

[TaskBudgets](<../../../src/ab_harness/task_compiler.py>) accepts exact integers:
positive wall_time_seconds and nonnegative model_calls/tool_calls/retry_attempts.
The compiler hashes these fields and the ledger freezes their projection.
[TaskBudgetAuthority](<../../../src/ab_harness/runtime_controls.py>) reads that
projection; decisions use `BUDGET_DECISION_SCHEMA=uah.budget_decision/v1` and
positive units, nonnegative limit/consumed_before/consumed_after. File reload
preserves consumption. Tool execution and ready-actor invocation atomically
record accounting before dispatch. Their public dispatch interfaces fix units to
one; they do not accept a caller quantity. Malformed-quantity tests therefore
cross public assess/consume separately; actual owner/provider fixtures exercise
valid fixed-unit accounting and exhaustion before handler/provider work. No
private quantity injection or new dispatch parameter is claimed. No token/USD/descendant budget is added.

Confirmed test seams for this scope: public assess/consume, LifecycleLedger
record/events/replay/reopen, admitted owner execution and ready fake-provider
invocation, existing exporters/loaders, semantic admission and deterministic
acceptance. No private method tests, new store, numeric framework or new policy.

The specific entry defect under test is bool/float equality reusing an existing
unit-one decision, not extra debit. The minimal repair must reject non-int or
nonpositive units before ledger lookup, equality or arithmetic and preserve
consume delegation, ValueError, immutable subject requests and debit policy.

## Source anchors

- [Portable values](<../../../src/ab_harness/contracts.py>)
- [Compiler](<../../../src/ab_harness/task_compiler.py>)
- [Model configuration](<../../../src/ab_harness/agent_configuration.py>)
- [Profile](<../../../src/ab_harness/environment_profiles.py>) and [run](<../../../src/ab_harness/environment_runs.py>)
- [Ingress](<../../../src/ab_harness/environment_ingress.py>)
- [Proposal/admission](<../../../src/ab_harness/proposal_admission.py>) and [lease](<../../../src/ab_harness/domain_lifecycle.py>)
- [Receipt/evidence](<../../../src/ab_harness/environment.py>) and [acceptance](<../../../src/ab_harness/acceptance.py>)
- [Ledger](<../../../src/ab_harness/lifecycle.py>)
- [Input schema validator](<../../../src/ab_harness/schema_validation.py>)

Output validation, evidence freshness and missing standalone serializer/version
policies remain owner-scoped open rows. This inventory does not close all H0
schemas or any H gate.


## Production consumer index

Source-symbol census includes owning modules and package re-exports, not only
direct import lines. It covers repository source and scripts; arbitrary external
consumers are unknown. Tests are named separately in the inventory above.

| Family | Source and script consumers |
| --- | --- |
| TaskSpec | [scripts/render_agent_runtime_example.py](<../../../scripts/render_agent_runtime_example.py>), [ab_harness/__init__.py](<../../../src/ab_harness/__init__.py>), [ab_harness/prompt_compiler.py](<../../../src/ab_harness/prompt_compiler.py>), [ab_harness/task_compiler.py](<../../../src/ab_harness/task_compiler.py>), [ab_harness_nao/qualification.py](<../../../src/ab_harness_nao/qualification.py>), [ab_harness_nao/smoke.py](<../../../src/ab_harness_nao/smoke.py>) |
| CompiledTask | [ab_harness/__init__.py](<../../../src/ab_harness/__init__.py>), [ab_harness/lifecycle.py](<../../../src/ab_harness/lifecycle.py>), [ab_harness/prompt_compiler.py](<../../../src/ab_harness/prompt_compiler.py>), [ab_harness/proposal_admission.py](<../../../src/ab_harness/proposal_admission.py>), [ab_harness/runtime_controls.py](<../../../src/ab_harness/runtime_controls.py>), [ab_harness/task_compiler.py](<../../../src/ab_harness/task_compiler.py>) |
| ModelConfiguration | [scripts/render_agent_runtime_example.py](<../../../scripts/render_agent_runtime_example.py>), [ab_harness/__init__.py](<../../../src/ab_harness/__init__.py>), [ab_harness/agent_configuration.py](<../../../src/ab_harness/agent_configuration.py>), [ab_harness/model_allocator.py](<../../../src/ab_harness/model_allocator.py>) |
| EnvironmentProfile | [scripts/render_agent_runtime_example.py](<../../../scripts/render_agent_runtime_example.py>), [ab_harness/__init__.py](<../../../src/ab_harness/__init__.py>), [ab_harness/agent_lifecycle.py](<../../../src/ab_harness/agent_lifecycle.py>), [ab_harness/environment_profiles.py](<../../../src/ab_harness/environment_profiles.py>), [ab_harness_nao/smoke.py](<../../../src/ab_harness_nao/smoke.py>) |
| Environment run | [scripts/render_agent_runtime_example.py](<../../../scripts/render_agent_runtime_example.py>), [ab_harness/__init__.py](<../../../src/ab_harness/__init__.py>), [ab_harness/agent_identity.py](<../../../src/ab_harness/agent_identity.py>), [ab_harness/agent_lifecycle.py](<../../../src/ab_harness/agent_lifecycle.py>), [ab_harness/domain_lifecycle.py](<../../../src/ab_harness/domain_lifecycle.py>), [ab_harness/environment.py](<../../../src/ab_harness/environment.py>), [ab_harness/environment_runs.py](<../../../src/ab_harness/environment_runs.py>), [ab_harness/task_ingress_authority.py](<../../../src/ab_harness/task_ingress_authority.py>), [ab_harness_nao/qualification.py](<../../../src/ab_harness_nao/qualification.py>), [ab_harness_nao/smoke.py](<../../../src/ab_harness_nao/smoke.py>) |
| Environment ingress | [scripts/render_agent_runtime_example.py](<../../../scripts/render_agent_runtime_example.py>), [ab_harness/__init__.py](<../../../src/ab_harness/__init__.py>), [ab_harness/environment_ingress.py](<../../../src/ab_harness/environment_ingress.py>), [ab_harness/task_compiler.py](<../../../src/ab_harness/task_compiler.py>), [ab_harness/task_ingress_authority.py](<../../../src/ab_harness/task_ingress_authority.py>), [ab_harness_nao/qualification.py](<../../../src/ab_harness_nao/qualification.py>), [ab_harness_nao/smoke.py](<../../../src/ab_harness_nao/smoke.py>) |
| AB views / bindings | [scripts/render_agent_runtime_example.py](<../../../scripts/render_agent_runtime_example.py>), [ab_harness/__init__.py](<../../../src/ab_harness/__init__.py>), [ab_harness/bindings.py](<../../../src/ab_harness/bindings.py>), [ab_harness/contracts.py](<../../../src/ab_harness/contracts.py>), [ab_harness/environment.py](<../../../src/ab_harness/environment.py>), [ab_harness/prompt_compiler.py](<../../../src/ab_harness/prompt_compiler.py>), [ab_harness/proposal_admission.py](<../../../src/ab_harness/proposal_admission.py>), [ab_harness/registry.py](<../../../src/ab_harness/registry.py>), [ab_harness/task_compiler.py](<../../../src/ab_harness/task_compiler.py>), [ab_harness_nao/contracts.py](<../../../src/ab_harness_nao/contracts.py>), [ab_harness_nao/smoke.py](<../../../src/ab_harness_nao/smoke.py>) |
| Proposal / admission | [ab_harness/__init__.py](<../../../src/ab_harness/__init__.py>), [ab_harness/domain_lifecycle.py](<../../../src/ab_harness/domain_lifecycle.py>), [ab_harness/environment.py](<../../../src/ab_harness/environment.py>), [ab_harness/lifecycle.py](<../../../src/ab_harness/lifecycle.py>), [ab_harness/prompt_compiler.py](<../../../src/ab_harness/prompt_compiler.py>), [ab_harness/proposal_admission.py](<../../../src/ab_harness/proposal_admission.py>), [ab_harness/runtime_controls.py](<../../../src/ab_harness/runtime_controls.py>), [ab_harness_nao/qualification.py](<../../../src/ab_harness_nao/qualification.py>) |
| Execution receipt | [ab_harness/__init__.py](<../../../src/ab_harness/__init__.py>), [ab_harness/environment.py](<../../../src/ab_harness/environment.py>), [ab_harness/lifecycle.py](<../../../src/ab_harness/lifecycle.py>) |
| Effect evidence / owner result | [ab_harness/__init__.py](<../../../src/ab_harness/__init__.py>), [ab_harness/acceptance.py](<../../../src/ab_harness/acceptance.py>), [ab_harness/contracts.py](<../../../src/ab_harness/contracts.py>), [ab_harness/environment.py](<../../../src/ab_harness/environment.py>), [ab_harness/lifecycle.py](<../../../src/ab_harness/lifecycle.py>), [ab_harness_nao/qualification.py](<../../../src/ab_harness_nao/qualification.py>), [ab_harness_nao/smoke.py](<../../../src/ab_harness_nao/smoke.py>) |
| Trace schemas | [scripts/render_agent_runtime_example.py](<../../../scripts/render_agent_runtime_example.py>), [ab_harness/__init__.py](<../../../src/ab_harness/__init__.py>), [ab_harness/agent_identity.py](<../../../src/ab_harness/agent_identity.py>), [ab_harness/agent_lifecycle.py](<../../../src/ab_harness/agent_lifecycle.py>), [ab_harness/domain_lifecycle.py](<../../../src/ab_harness/domain_lifecycle.py>), [ab_harness/environment.py](<../../../src/ab_harness/environment.py>), [ab_harness/lifecycle.py](<../../../src/ab_harness/lifecycle.py>), [ab_harness/model_allocator.py](<../../../src/ab_harness/model_allocator.py>), [ab_harness/model_invocation.py](<../../../src/ab_harness/model_invocation.py>), [ab_harness/observatory.py](<../../../src/ab_harness/observatory.py>), [ab_harness/runtime_controls.py](<../../../src/ab_harness/runtime_controls.py>), [ab_harness/task_ingress_authority.py](<../../../src/ab_harness/task_ingress_authority.py>), [ab_harness/task_registry.py](<../../../src/ab_harness/task_registry.py>), [ab_harness_nao/qualification.py](<../../../src/ab_harness_nao/qualification.py>), [ab_harness_nao/smoke.py](<../../../src/ab_harness_nao/smoke.py>) |

## Frozen entry owner pins

These SHA-256 pins identify inspected dependency bytes before SPR-02 code edits;
they do not assert that every owner changes in this scope.

| Product source | Entry SHA-256 |
| --- | --- |
| [contracts.py](<../../../src/ab_harness/contracts.py>) | `06e99272df0ac1d22cf45e065c0ee240557df334c982819428ace498990d7c54` |
| [task_compiler.py](<../../../src/ab_harness/task_compiler.py>) | `5d5627f53535a01686c3e433fdc6f2ea3dfd466e67ac1b6f33a7424e28a36a39` |
| [agent_configuration.py](<../../../src/ab_harness/agent_configuration.py>) | `52e8954f458405ac11414a20003a04044e0756f279416e5b9c287aa1a7e3ab32` |
| [environment_profiles.py](<../../../src/ab_harness/environment_profiles.py>) | `e4a3147e8bab6e68d755aadd57a61f5a0f606046b02479199739793c882a482f` |
| [environment_runs.py](<../../../src/ab_harness/environment_runs.py>) | `261d0a75ad94e286be19722dacdc15c4fdc6f0340c529779b66ddeaa78ce556c` |
| [environment_ingress.py](<../../../src/ab_harness/environment_ingress.py>) | `faeb661ebfc43eef62c2599d68881dc304247e2fb9b7aa18b2e4e8e35e0e7ee4` |
| [bindings.py](<../../../src/ab_harness/bindings.py>) | `1492eb91866ed67b1691ecdbe95c5307efcaefdfd3bd8daa595c53af90fca33d` |
| [proposal_admission.py](<../../../src/ab_harness/proposal_admission.py>) | `d4e52a281d8d9db1157e7ef2b5be5878ac2e08c5215ad4d031c548cd70a93013` |
| [domain_lifecycle.py](<../../../src/ab_harness/domain_lifecycle.py>) | `48de0478d577b58567483f5fa22334f641a32855f32a240944b91346906dff6f` |
| [environment.py](<../../../src/ab_harness/environment.py>) | `7d8a0a702ddc589102c790656dde19ce6cb5605f729e592b75330380637a6300` |
| [acceptance.py](<../../../src/ab_harness/acceptance.py>) | `d720df5c294e9d340921f6ee77b3441c7fd1f78eb8ead906ca2e77ca220ee1ed` |
| [lifecycle.py](<../../../src/ab_harness/lifecycle.py>) | `22f2b39d587ed670b209c66ad0f79d8eb1a3228942fbf37aee7cea3363ca482e` |
| [schema_validation.py](<../../../src/ab_harness/schema_validation.py>) | `6512a14cf5b203b6b39b5b624ef9e76ebd87944af1c3ff354be7fa352d4bc292` |
| [runtime_controls.py](<../../../src/ab_harness/runtime_controls.py>) | `020b9f368a850e7ccdb5cc3c68520e27c0bb7f86ae17cb90350034d1b6315a32` |
