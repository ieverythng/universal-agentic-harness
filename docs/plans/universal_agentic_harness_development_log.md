# Universal Agentic Harness: Development Log

**Purpose:** Practical implementation ledger linked to the semantic masterplan  
**Updated:** 2026-09-07
**Target:** UAH H2 NAO planner qualification after ordered evidence gates pass
**Current release boundary:** H0 contract spine, one H1 synthetic vertical
slice, smoke CLI, quarantined Workbench retrieval, and frozen Workbench adapter
protocol; H1 lifecycle and H2 planner parity remain incomplete

## Current state

| Area | State | Evidence |
| --- | --- | --- |
| Portable semantic kernel | Green | Frame-relative AB views, projection, role gate, JSONL trace |
| Semantic implementation bindings | Green | Candidate quarantine, approved resolution, runtime-mode selection |
| ROS-free environment owner | Green | Approved AB1 dispatch and owner-issued effect evidence |
| Recorded NAO qualification | Green | Chatbot handoff to planner proposal to gate to fake owner to evidence closure |
| Latest NAO AB0 seam map | Declared candidates | Seven revision-pinned pointers across six canonical AB0 objects |
| H2 planner coupling | Active target | NAO `v1.0.0` planner ingress/egress projection, two-stage admission, fake owner, evidence and parity suite required |
| Chatbot coupling | Deferred after planner parity | Existing node retained as compatibility/reference implementation |
| Watson/Bonsai model matrix | Not started | Frozen cases and configuration identity still required |
| Configuration identity | Partial | Monolithic model-harness-environment tuple is content-addressed; role, agent, run, trace and operation identities are specified but not implemented |
| Launch smoke CLI | Green | Accepted path, rejected canary, and Workbench retrieval run via `python -m ab_harness smoke` |
| Neural Workbench retrieval | Green candidate slice | Failure-aware bounded retrieval emits provenance-bearing candidates only |
| Neural Workbench promotion/adaptation | Quarantined design only | No trusted runtime mutation or registry promotion implemented |
| NeuralWorkbench repository | Boundary defined, gitlink missing | Intended companion revision is `e76ba7e`; `.gitmodules` exists but the UAH tree does not currently mount the gitlink |
| Workbench adapter protocol | Green contract slice | Focused tests cover serialization, handshake, mismatch, and observation-only override |
| Prompt compiler | Specified, not implemented | Layered UAH kernel, role, domain, AB projection and task context contract is documented |
| Two-stage admission | Specified, not implemented | Typed proposal to immutable admitted operation to domain execution lease |
| Observatory | O1 identity/event contract frozen | Static renderer implementation required for H1/H2 review; O2 deferred |

## Frozen architectural invariant

```text
stable AB semantic object
  -> zero or more versioned implementation bindings
  -> deterministic approval and runtime-mode resolution
  -> environment owner
  -> owner-issued effect evidence
```

A method, topic, service, or endpoint is a replaceable pointer. It does not
become a new AB object merely because it was discovered. AB0 interfaces may
have producer, contract, and consumer bindings with different implementation
owners. Only the registry-declared owner may close an executable AB1 effect.

See [ADR 0001](../architecture/decisions/0001-semantic-objects-and-shadow-first-bindings.md) and
the root [domain model](../../CONTEXT.md).

## Source assimilation record

The 2026-07-30 inspection used:

| Source | Revision | Relevant public seam |
| --- | --- | --- |
| `ieverythng/nao_chatbot_llm`, `origin/feat/planner_llm_hooks` | `a2ecca7` | `build_planner_request_payload`, `DialogueTurnEngine`, `PlannerHandoff`; remote tree matches the inspected local source |
| `ieverythng/nao-ros4hri-bridge`, tag `v1.0.0` on `feat/TFM-LLM_planner` | `ebffe93a74be4e013ce0f60fdfc41268dba73fc3` | Immutable H2 compatibility baseline for `PlannerRequest`, `PlannerGate.decide`, planner/supervisor lineage, orchestrator dispatch and fake execution |
| `juanbendek-aily/Neural-Wokbench`, `feat/base-implementation` | `e76ba7eafbd90f9ed239a65f741d2598ecd033cb` | Standalone package boundary, candidate engine, verifier, trace memory, registry tools, stack observer, and synchronized generated docs |
| ZeroTier Watson/Bonsai evaluation | 2026-07-29 report | Watson strict-workflow control; Bonsai memory-efficient high-context challenger |

The UAH source does not import either NAO repository. The inspected seams are
represented as candidate pointers or reproduced as portable behavioral
contracts.

The current `feat/TFM-LLM_planner` head is comparative evidence only. H2 parity
targets the peeled `v1.0.0` commit so later documentation or unrelated branch
changes cannot move the baseline. Direct source and focused tests, rather than
the stale 2026-05-31 GitNexus index, are the evidence for the seam map.

## Implementation ledger

### 2026-07-30: Semantic binding slice

Added:

- `ABImplementationBinding`
- `BindingCatalog`
- `OwnerExecutionResult` and `EffectEvidence`
- `InProcessEnvironmentOwner`

Proved:

- changing a locator leaves the semantic object unchanged;
- unknown AB targets fail catalog construction;
- candidate bindings cannot resolve;
- runtime mode is part of binding resolution;
- AB0 interface bindings cannot dispatch;
- executable AB1 bindings must be implemented by the semantic effect owner;
- successful evidence must use declared observables and a durable reference.

### 2026-07-30: Recorded NAO qualification slice

Added:

- `QualificationCase`
- `QualificationResult`
- `RecordedNaoQualificationHarness`

The initial case is intentionally narrow:

```text
recorded chatbot execution handoff
  -> chatbot role gate
  -> recorded planner AB1 proposal
  -> planner role and projection gate
  -> approved in-process find_object binding
  -> fake object_finder result
  -> terminal observable closure
```

The negative cases prove that an out-of-projection planner proposal never
dispatches and a failed owner result cannot close the task.

### 2026-08-04: Latest NAO contract bindings

Declared candidate bindings for:

- `/nao_orchestrator/planner_request` chatbot handoff publisher;
- `/planner/request` orchestrator admission decision and `PlannerRequest`
  contract;
- `/intents` planner executable-plan publication;
- `/planner/execution_feedback` `ExecutionFeedback` contract;
- `/planner/dialogue_act` `PlannerDialogueAct` contract;
- `/scene/summary` `SceneSummary` contract.

They remain candidates because declaration and discovery are not approval.
The gate-ingress and admitted-request topics are deliberately separate AB0
objects even though they reuse the planner request schema. This preserves the
deterministic admission boundary already implemented by `nao_orchestrator`.

### 2026-08-04: Quarantined Workbench memory

Added `TraceExperience`, `WorkbenchMemory`, and
`WorkbenchContextCandidate`. Retrieval is deterministic, query-scoped, and
bounded separately for supporting traces and counterexamples. Missing support
or counterevidence is surfaced as an explicit gap. The output status is always
`candidate`; the module has no promotion or registry-write path.

This is a concrete Neural Workbench coupling seam, not an H3 completion claim.
It prepares structured context for a later model adapter while keeping prompt
policy, trusted code, permissions, evaluator rules, and canonical AB objects
outside online mutation.

### 2026-08-04: Content-addressed v0 smoke launch surface

Added `ConfigurationIdentity` and `python -m ab_harness smoke`. The smoke run:

1. identifies the complete recorded model, runtime, harness, adapter, registry,
   environment, suite, and evaluator configuration;
2. runs one admitted chatbot/planner/fake-owner path;
3. runs one out-of-projection rejection canary;
4. records both as Workbench experiences;
5. proves retrieval returns both supporting and opposing evidence.

This command is the initial boot qualification surface. It uses a recorded
fixture, not Watson, Bonsai, ROS, or a claim of general agent capability.

### 2026-08-04: H2 and NeuralWorkbench boundary freeze

The design grill established:

- H2 closes planner ingress/egress over recorded and fake NAO contracts;
- approved AB1 operations are callable while AB0 dialogue, KB, transport, and
  feedback seams remain inspection-only;
- NAO owns explicit `legacy | uah | shadow` routing with no silent fallback;
- existing planner and chatbot packages remain compatibility/reference nodes;
- NeuralWorkbench begins authoritative work at H3 and can emit shadow
  replacement candidates, but UAH gates and environment owners execute;
- UAH owns the mandatory execution ledger and NeuralWorkbench owns derived
  adaptive traces;
- Observatory O1 freezes the read-only API; O2 is the interactive product;
- automated domain initialization is H3+ and emits candidate artifacts only.

The full decision record is
`../artifacts/decisions/2026-08-04_uah_h2_neural_workbench_grill.md`.

### 2026-08-04: Workbench protocol seam and intended pin

Recorded the intended NeuralWorkbench revision and added
`ab_harness.workbench_protocol`. The current tree does not contain the gitlink,
so mounting the companion repository remains open:

- content-addressed, JSON-compatible `WorkbenchRequest`;
- candidate-only `WorkbenchCandidate` and `WorkbenchCandidateBatch`;
- immutable UAH-to-Workbench `WorkbenchObservation`;
- protocol descriptor and in-process engine port;
- fail-closed mismatch behavior;
- visible development override restricted to observation-only.

The protocol is transport-neutral. Network/service transports are deferred.

### 2026-09-03: Identity, prompt, admission, and Observatory architecture checkpoint

The post-review architecture grill resolved these contracts:

- `AgentRoleConfiguration` is immutable and model-independent. It names one
  primary abstraction frame plus explicit, versioned auxiliary frame
  projections and capability packs.
- `agent_id` identifies one immutable composition of role, model
  configuration, prompt pack, harness build, and adapter revisions.
  `agent_run_id` identifies one activation.
- `task_id` remains a domain work identity. `trace_id` identifies a causal
  workflow, while `operation_id` identifies one frame-relative AB-object
  lifecycle and may form a parent/child decomposition tree.
- `PromptCompiler` deterministically assembles the UAH protocol kernel, role
  contract, minimal domain policy, task AB projection, and current context.
  The semantic admission gate consumes the same `InteractionModuleSpec`.
- UAH semantic admission emits an immutable `AdmittedOperation`. Domain
  lifecycle admission may then emit an `ExecutionLease` after readiness,
  duplicate, concurrency, cancellation, supersession, and version checks.
- Mandatory trace emission belongs to the UAH kernel. Agent-visible trace
  inspection is a separate, normally read-only and task-scoped capability.
- `SkillArtifact` is an optional binding target in a named frame. NAO objects
  may bind directly to ROS or Python contracts; coding-frame objects may bind
  to TDD, SkillOpt, deslop, or other developer skills.
- `uah-domain-onboarding` produces a candidate `DomainContractPack`, applies
  structural validation and prompt SkillOpt gates, and cannot approve itself.
- A fixed multi-agent system is not automatically AB5. AB5 remains reserved for
  independently evaluated governance over a family of AB4 systems.

The canonical diagrams and node-level responsibilities are in
`../architecture/universal_agentic_harness_foundation.md`. The trace identity
and event grammar are in `../architecture/observatory_contract.md`.

This checkpoint changes no runtime authority. It defines the next TDD seams;
the current implementation still uses `AgentRoleSpec`, `HarnessTrace`, and the
monolithic `ConfigurationIdentity` compatibility contracts.

### 2026-09-04: Auxiliary-frame access and Workbench attachment checkpoint

The grill resolved the maximum access modes for each role-authorized additional
frame projection:

- `inspect_only` permits bounded observation without state-changing proposals;
- `direct_proposal` permits typed proposals but grants no admission or execution
  authority;
- `delegate_only` permits only a typed handoff to an agent whose primary frame
  matches the target frame.

The declaration belongs to `role_configuration_id`; `agent_id` inherits it and
the task compiler may only narrow it. Effect-bearing cross-frame work defaults
to `delegate_only`, while read-only foreign state and Observatory views default
to `inspect_only`.

NeuralWorkbench remains an optional H3 companion engine rather than an
abstraction frame. UAH may issue a bounded frame-relative `WorkbenchRequest`
before a configured model call and an immutable `WorkbenchObservation` after
terminal trace closure. Candidate artifacts pass a UAH filter before prompt or
shadow use. The existing transport-neutral `WorkbenchEnginePort` remains the
semantic seam; an MCP connection would be another adapter, not a different
contract or authority path.

Hardware allocation is now separate from logical agent identity. A
`provider_pool_id` supplies compatible `model_instance_id` resources; UAH
reserves one through `model_lease_id`, and every prompt-to-output call receives
a `model_invocation_id`. The invocation joins the actual model resource to
`agent_run_id` and `trace_id`. Reallocation among equivalent instances leaves
`agent_id` unchanged, while a different `model_configuration_id` creates a new
agent.

### 2026-09-06: Stable agent handle and fidelity checkpoint

`agent_handle_id` is the minimal stable routing identity for names such as
`watson.system.primary`. It does not replace immutable agent identity. Each
`AgentHandleRevision` points to one active `agent_id`, pins the required
`role_configuration_id`, records a fidelity report, and retains a rollback
revision.

The model allocator may move the active agent among compatible instances of its
declared model configuration. It may not silently select another model
configuration. A model, prompt, harness, or adapter change produces a new
`agent_id`; the stable handle moves only after role-fidelity qualification and
an immutable revision update. This keeps the routing interface small while
preserving evaluation and Observatory provenance.

### 2026-09-07: Outside-in provisioning and release staging

The canonical construction order is now:

```text
DomainContractPack
  -> AgentRoleConfiguration
  -> AgentManifest and agent_id
  -> AgentHandleRevision
  -> AgentRun
  -> Task and trace
  -> ModelLease
  -> ModelInvocation
  -> Operation lifecycles
```

An `agent_id` is an immutable embodiment of its handle; an `agent_run_id` is
the runtime activation. Each run pins the resolved handle revision, so later
rebinding cannot rewrite past work or silently alter an in-flight task.

Identity contracts and static handle resolution belong in H0-H1. H2 uses named
NAO handles and fixed provider/resource leases. Dynamic provider pools,
hardware scheduling, lease arbitration, and fidelity-gated hot replacement
belong in H3. H4 may evaluate candidate embodiments, and H5 adds cross-runtime
allocation conformance.

The hardware module remains `ModelAllocator`. `AgentRegistry` owns immutable
agent construction and lookup; the handle registry owns continuity and
promotion. Calling the hardware scheduler `AgentAllocator` would merge semantic
identity with resource placement.

Every role will reference a versioned `model_admission_profile_id` containing
provider-neutral capability and behavioral requirements. Handle fidelity tests
candidate models against that profile plus deployment-specific provider and
hardware constraints. The allocator still receives one resolved model
configuration and cannot choose a merely similar model on its own.

## Verification dashboard

| Command | Result |
| --- | --- |
| `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp .test-tmp\full-suite` | 42 passed |
| Focused `tests/test_workbench_protocol.py` red-green pass | 9 passed after strict identity, capability, duplicate-ID, and JSON checks |
| `.venv\Scripts\python.exe -m ab_harness smoke` | Passed all four canaries |
| NeuralWorkbench `python -m pytest -q -p no:cacheprovider` | 29 passed |
| NAO planner/common/gate/supervisor/trace-viewer seam suite | 177 passed; 60 expected warnings for unavailable optional `interaction_skills` manifest |
| Chatbot planner-handoff/grounding/request-adapter seam suite | 72 passed with `planner_common` and `kb_skills` on `PYTHONPATH` |
| Offline wheel build, install into fresh venv, then `python -m ab_harness smoke` | Passed; wheel SHA-256 recorded by build output |
| Core forbidden-import audit | Passed; only stdlib and `ab_harness` imports |
| `python scripts/render_agentic_harness_docs.py` | Passed after canonical edits |
| Markdown/HTML synchronization | Generated companions updated |
| NeuralWorkbench standalone document render | HTML companions regenerated; mathematical basis PDF structurally and visually inspected |
| System-design DOCX structural inspection | Passed: 89 paragraphs, 9 tables, 0 template placeholders |
| System-design DOCX page rendering | Blocked locally: LibreOffice absent; Word/Orca unavailable to managed session |

The workspace-local pytest temp root is used because the managed session cannot
write the inherited Windows pytest temp directory. This is an environment
constraint, not a product failure.

## Evaluation lifecycle

### Gate A: Boot qualification

Question: can this exact immutable configuration safely accept bounded work?

Minimum record:

- model, quantization, runtime build and flags;
- harness, adapter, prompt, registry, environment, and evaluator hashes;
- health/readiness and resource headroom;
- effective context, KV configuration, slots, and cache behavior;
- one accepted and one rejected AB canary;
- strict structured-output canary.

Boot acceptance proves operability only.

### Gate B: Promotion qualification

Question: does the candidate improve its intended task distribution without an
unacceptable regression?

Minimum record:

- frozen development and disjoint holdout sets;
- repeated trials and reliability across repeats;
- milestones, terminal effects, and protected-state minefields;
- failure-attribution slices;
- quality, latency, memory, and cost Pareto comparison;
- owner review, provenance, rollback target, and rollback rehearsal.

### Gate C: Runtime evaluation

Question: is a promoted configuration still inside its approved envelope?

Runtime evaluation may continue, degrade, quarantine, interrupt, or roll back.
It may create Workbench candidates but cannot promote itself.

## Failure attribution

Every failed case receives one primary observed stage plus evidence:

| Stage | Example |
| --- | --- |
| `runtime_preflight` | Wrong model, flags, context, or insufficient memory headroom |
| `transport_or_provider` | Timeout, malformed stream, proxy field loss |
| `context_projection` | Required AB object or fresh evidence absent |
| `model_proposal` | Invalid output, wrong operation, fabricated effect |
| `gate_or_harness` | Valid proposal rejected or invalid proposal admitted |
| `environment_owner` | Valid admitted operation failed in its owner |
| `evidence_closure` | Execution occurred but proof is missing, stale, or wrong-owner |
| `evaluator` | Broken fixture, ambiguous goal, nondeterministic acceptance |
| `resource_budget` | Context, latency, memory, concurrency, or energy budget exceeded |

Attribution is an observed classification, not causal proof. Controlled replay
or component substitution is required to sharpen cause.

## Watson versus Bonsai qualification matrix

The evaluation unit is the complete configuration, not the model name.

| Axis | Watson control | Bonsai challenger |
| --- | --- | --- |
| Initial role | Strict routed orchestration control | Memory-efficient high-context candidate |
| Harness modes | Flat; AB projection; projection plus counterexample retrieval | Same frozen modes |
| Task slices | Chatbot handoff, valid AB1, AB0 rejection, stale evidence, tool failure, cancellation, recovery, strict JSON, long-context retrieval | Identical |
| Primary graders | Owner state/effects, milestones, minefields, evidence closure | Identical |
| Resource record | TTFT, prompt/decode throughput, peak/min-free memory, cache/concurrency | Identical |
| Promotion rule | Quality and safety constraints before speed/capacity | Same; memory advantage alone is insufficient |

Specific Bonsai experiments must treat FP16 versus calibrated KV4 and
speculative decoding as distinct configurations because their cache,
concurrency, latency, and quality envelopes differ.

## Ordered work queue

### P0: Complete the synthetic contract

- [x] Freeze semantic object versus implementation binding.
- [x] Enforce candidate quarantine and approved resolution.
- [x] Mount one deterministic owner without ROS.
- [x] Replay success, gate rejection, and failed evidence.
- [x] Add content-addressed configuration identity.
- [ ] Split immutable role, model, agent, run, trace, task, and operation
  identities behind compatibility exports.
- [ ] Add serialized `TaskSpec` and complete environment policy.
- [ ] Add `TypedProposal`, `AdmittedOperation`, and `ExecutionLease` contracts.
- [ ] Add deterministic `PromptCompiler` output and artifact hashing from the
  same `InteractionModuleSpec` consumed by semantic admission.
- [ ] Append lifecycle events for compile, proposal, gate, dispatch, evidence,
  and terminal decision.
- [ ] Add stale evidence, timeout, cancellation, retry exhaustion, and
  false-completion cases.

### P1: Build the evaluation runner

- [ ] Store frozen case suites and configuration manifests.
- [ ] Add milestones, minefields, repeated trials, and reliability aggregation.
- [ ] Add failure-injection fixtures and attribution checks.
- [ ] Add model adapter protocol and recorded-proposal replay mode.
- [ ] Render raw model output, proposal, admission, lease, result, evidence and
  terminal judgment as separate Observatory artifacts.
- [x] Add recorded-proposal boot smoke mode.
- [ ] Produce Watson/Bonsai comparison artifacts without touching live ROS.

### P2: NAO planner parity

- [ ] Capture package-owned chatbot and planner golden fixtures from NAO tag
  `v1.0.0` and chatbot revision `a2ecca796...`.
- [ ] Validate candidate AB0 bindings against their exact source revisions.
- [ ] Implement full planner projection, proposal gate, fake-owner dispatch,
  evidence closure, and replay.
- [ ] Run explicit `legacy | uah | shadow` planner parity.
- [ ] Classify every disagreement before enabling UAH authority.
- [ ] Preserve dialogue, planning, orchestrator, perception, and execution owners.
- [ ] Keep chatbot assimilation behind planner parity.
- [ ] Preserve native `goal_id`, `request_id`, `plan_id`, `plan_version`, and
  `step_id` beneath UAH task, trace and operation identities.

### P3: Neural Workbench coupling

- [x] Ingest immutable success and counterexample experiences in memory.
- [x] Emit bounded, provenance-bearing retrieval candidates only.
- [x] Pin the independent repository and freeze transport-neutral adapter
  contracts with fail-closed compatibility.
- [ ] Persist experiences in an append-only, replay-addressed store.
- [ ] Add capability posteriors and calibrated retrieval scores.
- [ ] Add replay, opposing traces, disjoint holdout, owner review, provenance,
  and rollback gates.
- [ ] Keep code, canonical registry, permissions, evaluator, and promotion
  thresholds outside online mutation.

## H2 qualification gate

H2 is qualified only when the core rows and planner parity rows are green:

| Gate | State on 2026-09-04 | Required before qualification |
| --- | --- | --- |
| Installable portable package | Green | Clean install smoke in a fresh venv |
| Deterministic boot command | Green | Preserve machine-readable output and nonzero failure exit |
| Accepted and rejected AB canaries | Green | Retain owner evidence and no-dispatch rejection proof |
| Workbench form | Green, bounded retrieval and protocol | H3 remains optional and shadow-only |
| Complete configuration identity | Partial | Split role, model, agent, run, trace and operation identities while preserving the current content hash as a compatibility snapshot |
| Lifecycle replay | Partial | Append compile-to-terminal events and replay without the model |
| Failure suite | Partial | Add stale evidence, timeout, cancellation, and false completion |
| Documentation | Architecture checkpoint active | Keep Markdown/HTML diagrams, plans, contracts, artifacts and implementation status synchronized |
| Watson/Bonsai runner | Not started | Freeze provider-neutral protocol; one reproducible paired dry run |
| NAO planner parity | Not started | Recorded/fake full path under explicit authority mode; reviewed disagreement report |
| Live NAO/ROS authority | Explicitly excluded | Not required for H2; remains NAO-owner gated after fake/sim parity |

## Open issues

| ID | Issue | Blocking condition | Next proof |
| --- | --- | --- | --- |
| UAH-D01 | No complete lifecycle event grammar | Cannot reconstruct every runtime transition | Add event types and replay test |
| UAH-D02 | Candidate NAO bindings are unvalidated | No source-schema parity artifact | Compile fixtures from package-owned tests |
| UAH-D03 | No live model adapter | Watson/Bonsai matrix cannot run | Freeze provider-neutral request/result protocol |
| UAH-D04 | No stale/freshness contract in `ABObjectView` | Evidence closure is incomplete | Add clock/freshness fixture and counterexample |
| UAH-D05 | Identity layers specified but not implemented | Agent, activation, trace and operation state remain conflated in current contracts | Add immutable identity contracts behind compatibility exports |
| UAH-D06 | No Workbench trace bridge | Adaptation remains a paper design | Implement terminal-ledger to `WorkbenchObservation` adaptation without direct mutation |
| UAH-D07 | No PromptCompiler | Prompt, projection and deterministic admission can drift | Compile a prompt artifact and gate from the same immutable interaction module |
| UAH-D08 | No two-stage admission contracts | Domain lifecycle cannot grant or deny authority independently | Add `TypedProposal`, `AdmittedOperation` and `ExecutionLease` vertical slice |
| UAH-D09 | NeuralWorkbench gitlink absent | Intended companion revision is documented but not mounted | Restore and verify gitlink at `e76ba7e` without changing core dependency rules |
| UAH-D10 | Workbench protocol uses legacy `configuration_id` | Per-agent and per-run candidate provenance cannot be reconstructed under the new identity model | Version the protocol after identity contracts define exact request and model-call correlation |
| UAH-D11 | No hardware-aware model allocator | Local RAM, VRAM, context and concurrency constraints cannot govern model reuse or eviction | Implement an H1 fixed-instance lease interface, then add dynamic scheduling at H3 |
| UAH-D12 | No agent-handle registry or fidelity evaluator | A named deployment cannot change model configuration without losing continuity or hiding an identity change | Add immutable handle-revision resolution and held-out fidelity evidence after core identity contracts |

## Next discriminating probe

Serialize one configuration and task, execute the recorded success and a stale
evidence counterexample into append-only lifecycle events, replay both without a
model, and require the same terminal decisions. This completes the semantic
center before a Watson or Bonsai provider is allowed into the loop.
