# Universal Agentic Harness: Development Log

**Purpose:** Practical implementation ledger linked to the semantic masterplan  
**Updated:** 2026-10-02
**Target:** UAH H2 NAO planner qualification after ordered evidence gates pass
**Current release boundary:** H0 contract spine, one H1 synthetic vertical
slice, profile-bound state-update and new-task ingress, explicit NAO adapter
canary, quarantined Workbench retrieval, and enforced repository hooks;
the accepted authority chain, typed rejection branches, explicit operation
edges, and terminal required-effect counterexamples persist in one strict
common JSONL ledger and replay after restart. Initial H1 runtime controls,
agent identity registration, and O1 rendering are present, while stale-evidence
policy, model runtime, and H2 planner parity remain incomplete

## Current state

| Area | State | Evidence |
| --- | --- | --- |
| Portable semantic kernel | Green | Frame-relative AB views, projection, typed admission, lease authority, and common lifecycle replay |
| Semantic implementation bindings | Green | Candidate quarantine, approved resolution, runtime-mode selection |
| ROS-free environment owner | Green | Exact lease-only dispatch, binding-fingerprint fencing, atomic tool-budget grant plus execution start, native result receipt, owner-issued effect evidence, typed evidence rejection, and pre-dispatch cancellation |
| Recorded NAO contract slice | Green | One H0 fixture records accepted, semantic-rejected, and terminal required-effect-rejected traces through the generic authority chain; this is not H2 planner parity |
| Latest NAO AB0 seam map | Declared candidates | Seven revision-pinned pointers across six canonical AB0 objects |
| H2 planner coupling | Active target | NAO `v1.0.0` planner ingress/egress must adopt the implemented lease-only authority chain, then add package-owned parity fixtures and `report_result` delegation |
| Chatbot coupling | Deferred after planner parity | Existing node retained as compatibility/reference implementation |
| Watson/Bonsai model matrix | Not started | Frozen cases and configuration identity still required |
| Configuration identity | Partial | Environment profile, run, ingress, registered task/trace lineage, content-addressed `AgentManifest`, initial immutable handle revision, roster-bound `AgentRun`, and frame-relative operation edges are explicit; role-configuration, model instance/lease/invocation, persistence, and durable actor lifecycle remain incomplete |
| Environment lifecycle | Partial green | Frozen profiles and attestation registration enforce owner, runtime, DomainContractPack revision, readiness evidence, and unique IDs; `TaskIngressAuthority` is the only task-bearing ingress writer; accepted terminal state blocks later ingress after restart; cooperating writers are advisory-lock serialized; owner cancellation is pre-dispatch only; rostered agent runs attach in memory as `attached_standby` |
| Domain contract authority | Green narrow kernel seam | `uah.domain_contract_pack/v1` derives its SHA-256 revision from role/task allowlists, ingress rules, effect-evidence rules, failure policy, and prohibited effects |
| Task compilation and closure | Green narrow kernel seam | `uah.task_spec/v2` and `uah.compiled_task/v2` supply the sole projection, obligations, prohibitions, retry-aware budgets, and revision lineage; tool-call consumption is enforced atomically at dispatch, while model-call consumption awaits the provider port |
| NAO adapter canary | Green recorded qualification | Injected DomainContractPack, authoritative ingress admission, strict planner-step validation, content-addressed raw output, input-schema validation, accepted lease-only execution, semantic no-dispatch rejection, terminal counterexample, restart replay, and verified digest run via `python -m ab_harness_nao` |
| Neural Workbench retrieval | Green candidate slice | Failure-aware bounded retrieval emits provenance-bearing candidates only |
| Neural Workbench promotion/adaptation | Quarantined design only | No trusted runtime mutation or registry promotion implemented |
| NeuralWorkbench repository | Boundary defined, gitlink missing | Intended companion revision is `e76ba7e`; `.gitmodules` exists but the UAH tree does not currently mount the gitlink |
| Workbench adapter protocol | Green contract slice | Focused tests cover serialization, handshake, mismatch, and observation-only override |
| Prompt compiler | Specified, not implemented | Layered UAH kernel, role, domain, AB projection and task context contract is documented |
| Two-stage admission and execution | Green narrow kernel seam | Proposal normalization or typed rejection, bounded input-schema validation, semantic admission, domain lease, exact lease-only execution, distinct result/evidence artifacts, typed evidence rejection, explicit operation edges, and terminal required-effect rejection are executable; output validation, concurrency, stale evidence, and false-completion policy remain open |
| Runtime controls | Green initial H1 slice | Typed execution failure, idempotent model/tool budget decisions, atomic tool-call dispatch, pre-dispatch cancellation, recorded-time timeout evaluation, and bounded retry decisions replay without granting proposal or lease authority; provider model accounting and in-flight interruption remain open |
| Agent identity and standby | Green initial H1 slice | In-memory content-addressed manifests, one-time handle registration with declared evidence references, roster-bound run attachment, and handle-revision pinning; rebinding, persistence, preflights, leases, transitions, and provider calls remain open |
| Observatory | Green initial O1 slice | Validated-ledger trace projection, terminal-status honesty, control/rejection failure stages, explicit operation nodes and recorded edges, provenance labels, static searchable HTML, inert graph JSON, and a committed recorded-canary example; full actor/configuration/comparison views and O2 remain open |
| Repository guardrails | Green | Python-native pre-commit and pre-push hooks enforce hygiene, Ruff, tests, generated-doc synchronization, and a fresh repository-signature cache |

### H0-H2 launch preparation

The development target is the H2 cooperative NAO planner demonstration. H0 and
H1 are its qualification prerequisites rather than separate documentation
tracks.

| Release | Already proved | Required next | Exit evidence |
| --- | --- | --- | --- |
| H0 contract spine | Frame-relative AB views, binding quarantine, domain rules and ingress decisions, task compilation, input-schema validation, two-stage admission, typed normalization/semantic/domain/evidence rejection, operation edges, lease-only execution, terminal acceptance or required-effect rejection, persistence, restart replay, and verified digests | Output validation, stale evidence, false-completion attribution, and cross-frame target projection | Serializable accepted and counterexample lifecycles with model-free terminal replay |
| H1 runtime kernel | Narrow accepted/deficit/rejected vertical slices, smoke CLI, initial manifest/handle/standby registries, tool-budget dispatch, pre-dispatch cancellation, recorded timeout, retry policy, and O1 | Durable agent lifecycle, scoped activation events, fixed-instance model lease, preflights, prompt compiler, provider port, and model-call consumption | Frozen synthetic suite reconstructs every terminal decision and `VerifiedTraceDigest` without the model |
| H2 cooperative NAO | Revision-pinned source map and one strict recorded qualification through the generic authority chain | Owner-reviewed package-owned golden fixtures and NAO DomainContractPack, AB0/AB1 projections, environment/trace bridge, planner ingress/egress gate, fixed NAO handles, `report_result` delegation, fake/sim execution, `legacy / shadow / uah` parity | Reviewed multi-actor parity report with lineage, admission, lease, result, obligations, failure attribution, and no duplicate activation or speech |

H3 Workbench retrieval and dynamic allocation remain specified companion work.
They may supply interfaces or shadow fixtures needed to avoid later redesign,
but they cannot displace an H0-H2 exit criterion.

### Documentation topology

`docs/plans/universal_agentic_harness_development_log.md` is the only canonical
development-log source. Its HTML companion is generated. The legacy
`docs/agentic_harness/universal_agentic_harness_development_log.html` file is a
redirect maintained for old links. The masterplan follows the same rule. No
second Markdown source or independently editable HTML copy exists in the legacy
directory.

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

- `NaoQualificationCase`
- `NaoQualificationResult`
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

Historical checkpoint. This version added `ConfigurationIdentity` and an early
canary exposed by `python -m ab_harness_nao`. That recorded run:

1. identifies the complete recorded model, runtime, harness, adapter, registry,
   environment, suite, and evaluator configuration;
2. runs one admitted chatbot/planner/fake-owner path;
3. runs one out-of-projection rejection canary;
4. records both as Workbench experiences;
5. proves retrieval returns both supporting and opposing evidence.

This command is the initial boot qualification surface. It uses a recorded
fixture, not Watson, Bonsai, ROS, or a claim of general agent capability.
The 2026-09-28 authority pass replaced the manually authored Workbench
experience checks in the CLI with lease-only execution, strict replay, and a
verified digest. Workbench retrieval remains independently tested.

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

This checkpoint originally changed no runtime authority. `AgentRoleSpec` and
the monolithic `ConfigurationIdentity` remain compatibility contracts, while
the later 2026-09-28 seam removed `HarnessTrace` in favor of the single
`LifecycleLedger` authority.

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

The NAO source audit confirmed the reusable startup behavior. Chatbot revision
`a2ecca796` performs tiny and optional realistic probes during lifecycle
configuration, fails configuration when required readiness is absent, exposes
dialogue services only on activation, and may run a bounded keepalive. NAO
`v1.0.0` performs planner tiny and optional planner-shaped probes before the
planner node reports ready, while launch sequencing holds `dialogue_manager`
configuration until `chatbot_llm` becomes active.

UAH separates those behaviors into non-reserving `RegistrationPreflight`,
post-lease `StartupPreflight`, and the final agent-run readiness transition.
Registration cannot load or invoke a model. A startup request acquires the
first model lease, runs bounded readiness probes, and exposes task ingress only
after the required policy passes.

The documentation coherence pass also removed conflicting H labels from the
foundation and adaptive extension. The masterplan is the only canonical H0-H6
spine: H2 remains cooperative NAO, H3 remains trace-adaptive Workbench plus its
supporting dynamic allocator, H4 remains crystallization, H5 remains federation,
and H6 remains optional AB5 policy research.

### 2026-09-07: NeuralWorkbench muscle-memory audit

The intended companion revision `e76ba7e` was inspected at source resolution.
Its current client is a deterministic symbolic bootstrap: template pulse
generation, registry verification, hand-tuned energy scoring, lowest-energy
valid selection, append-only JSONL traces, and offline macro proposals. Trace
records are not yet retrieved or adapted by the proposal client.

The companion specification defines a broader search system containing
deterministic templates, host-model candidates, retrieved-and-adapted traces,
and hybrid candidates. The architecture diagrams now expose that portfolio,
its verifier/scorer/selector, typed action memory, the UAH candidate filter, and
the distinct outputs for read-only prompt context and shadow typed proposals.
The trace observation path updates future search state only.

No training dependency was added to H3. The initial muscle-memory loop can be
built from typed trace indexing, retrieval, adaptation, symbolic checks, and
shadow evaluation. Learned embeddings or scorers remain optional versioned
adapters. Crystallization stays in the H4 quarantine and cannot follow directly
from retrieval frequency or a successful trace count.

### 2026-09-08: Environment-run, ingress, and task-closure checkpoint

The continuing architecture grill resolved the runtime envelope that was
missing between domain startup and operation admission:

- `EnvironmentProfile` is a reusable domain runtime contract with a pinned
  DomainContractPack and stable agent roster. `EnvironmentRun` is one
  owner-attested native activation.
- The environment owner mints readiness evidence after native preflight; UAH
  validates and registers the attestation. Registering an agent or environment
  does not invoke a model.
- Each `AgentRun` is attached to exactly one environment run. It may process
  many stimuli and tasks while moving between standby, acquiring a compatible
  model lease, and invoking. Releasing the model does not terminate the actor.
- `EnvironmentIngress` records immutable native stimuli. Deterministic
  `TaskIngressPolicy` classifies each item as a state update, task start, task
  resume, notification, or rejection before prompt compilation.
- One causal trace may include several actor agent runs. Environment, task,
  chatbot, planner, handle, and operation views are filters over one lifecycle
  ledger rather than separately authored traces.
- Operation graphs distinguish same-frame `decomposes_to`, cross-frame
  `delegates_to`, and ordered `continues_with` edges. Every operation retains
  exactly one frame-relative AB coordinate.
- `EffectObligation` distinguishes `required` from `best_effort` effects.
  `TaskAcceptance` is derived deterministically from owner-issued evidence.
  Best-effort failure records a deficit without erasing a successful required
  operation.
- `VerifiedTraceDigest` is the model-free, replayable memory projection used by
  Observatory and future Workbench retrieval. Model-authored reflection is not
  admitted into this trusted digest.

The source-resolution audit revisited NAO tag `v1.0.0`, chatbot revision
`a2ecca796...`, and the intended NeuralWorkbench revision `e76ba7e`. The
chatbot `DialogueTurnEngine`, planner request adapter, supervisor goal/version
state machine, planner gate, and orchestrator `report_result` callback already
contain domain behavior that should be preserved behind adapters. Focused
read-only checks passed for 112 chatbot turn-engine cases and 41 planner
supervisor/gate cases.

`report_result` is frozen as AB1 in the planner runtime frame. Its source-proven
implementation verifies planner execution evidence, delegates grounded text
composition to the chatbot actor, then returns to the native communication
owner. The intended NeuralWorkbench registry models an older same-frame
decomposition. H2 must correct that drift through an owner-reviewed,
content-addressed DomainContractPack revision rather than live registry sync.

This checkpoint changed the contract and implementation order, not the release
claim. The environment registry and task-acceptance evaluator were implemented
in the following 2026-09-09 TDD slices. Ingress classification, a multi-actor
ledger, and the `report_result` adapter remain open. H2 remains the first NAO
demonstration and H3 remains the first Workbench implementation stage.

### 2026-09-09: First task-acceptance TDD seam

The owner confirmed the public interface and closed the architecture grill:

```text
TaskAcceptanceEvaluator.evaluate(
    effect_obligations,
    evidence_set,
) -> TaskAcceptance
```

Four vertical red-green behaviors now prove the pure seam:

- required owner evidence closes its declared effect;
- failure of a best-effort report preserves required-effect acceptance and is
  recorded as a deficit;
- terminal failure of a required effect rejects the task;
- duplicate obligation identities and empty obligation sets fail closed.

The recorded NAO qualification path now accepts explicit effect obligations
and returns an optional `TaskAcceptance` artifact. Its existing
At this checkpoint, `required_observables` remained as a compatibility surface.
The 2026-09-28 lease-only continuation removed it after typed obligations became
the sole qualification input.
This additive path reuses `InProcessEnvironmentOwner` evidence and does not
move NAO retry, replan, speech, or lifecycle policy into the evaluator.

The NAO source informed the contract without becoming a dependency:
`observable_success` supplies effect names, the AB object and binding identify
the evidence owner, and NAO retry or terminal policy must be compiled into the
obligation before evaluation. The evaluator does not parse planner text,
interpret `plan_completed`, or decide native retryability.

### 2026-09-09: Environment registration and NAO package boundary

`EnvironmentRunRegistry.register(attestation)` now admits one complete owner
attestation and returns an immutable active `EnvironmentRun`. Registration
requires a frozen `EnvironmentProfile`, at least one non-empty readiness
evidence reference, and exact agreement on the environment owner, native
runtime revision, and DomainContractPack revision. Unknown profiles,
mismatches, and reused run or attestation identities fail before state is
written. Registration does not start native infrastructure, attach an agent,
reserve hardware, or invoke a model.

`EnvironmentProfileRegistry` rejects duplicate identities and incomplete
authority lineage. The contracts are currently in-memory and do not yet
provide serialization, durable persistence, attestation signature validation,
or environment close semantics.

The deslop boundary audit also moved all NAO-specific projection,
qualification, and canary code into the explicit `ab_harness_nao` package.
The `ab_harness` kernel has a regression test that rejects imports from this
adapter. Future domains should normally supply declarative DomainContractPack
content. A Python package is warranted only for irreducible native
normalization or parity behavior.

### 2026-09-11: Repository guardrails and first EnvironmentIngress slice

The repository now uses a Python-native pre-commit pipeline, following the
proven NAO and iTrader approach without introducing Node or Husky into a Python
package. `scripts/setup_dev_tools.sh` creates an ignored `.venv`, installs the
editable package and pinned development tools, then installs pre-commit and
pre-push hooks. The pre-commit suite checks merge markers, YAML, EOF and
whitespace hygiene, Ruff, the full test suite, and generated HTML consistency.

`scripts/run_precommit.sh` records a repository signature only after every hook
passes. Pre-push rejects a missing or stale signature. This corrects a weakness
in the inspected NAO pattern, where an ordinary final hook could record a cache
entry even after an earlier hook failed. The signature sorts repository paths,
so staging an unchanged file cannot invalidate the result merely by changing
Git's tracked/untracked listing order. `.env.example`, `.editorconfig`, and
`.gitattributes` define local-secret, line-ending, and editor boundaries across
the Linux and main-PC environments.

The confirmed `TaskIngressPolicy.classify(environment_run, ingress)` seam now
accepts immutable normalized ingress under an exact environment profile,
DomainContractPack revision, environment run, binding, and ingress-type rule.
The implemented positive action is `state_update`. Cross-environment input,
unknown bindings, unknown ingress types, and policy provenance mismatches return
typed rejection decisions without invoking a model. Duplicate rules and
malformed contracts fail closed.

The current implementation extends this checkpoint: every ingress carries a
content-derived artifact identity, every `TaskIngressDecision` carries a
content-derived `decision_id`, and an accepted start can reach
`TaskSpecCompiler` only if the exact task start is already recorded in the
common lifecycle ledger.

At this checkpoint, task-bearing actions were deliberately rejected at policy
construction until a task and trace identity issuer existed. The next TDD seam
was required to define that lineage before enabling `start_task`,
`resume_task`, or `notify_task`.

### 2026-09-13: Domain task identity and initial UAH trace issuance

This checkpoint implements the next seam confirmed by the closed identity,
environment, and memory grill. A `start_task` rule names the immutable native
lineage field that owns the domain task identifier. Classification preserves
that value as `task_id` and derives `trace_id` with the versioned
`uah-trace-v1` scheme over `environment_run_id` and `task_id`. A repeated task
identity within a different environment activation therefore receives a
different trace namespace.

Missing task identity returns `missing_task_identity` without constructing
partial lineage. Mutable lineage containers, duplicate lineage keys, empty
keys, and empty values fail at contract construction. `resume_task` and
`notify_task` remain disabled because the current stateless policy cannot prove
that a referenced task is registered and active in the same environment run.
The next lifecycle seam is an environment-bound task registry with duplicate
start protection and lookup for existing-task ingress.

### 2026-09-13: Environment-bound task registry and existing-task ingress

`EnvironmentTaskRegistry` now records immutable `TaskLineage` beneath the exact
`environment_run_id`. Replaying the same task-bearing ingress returns
`duplicate_environment_ingress`. A different ingress that attempts to start
the same environment-scoped domain task returns `task_already_registered`.
Both rejections preserve the registered task and trace identifiers for
diagnosis without granting another start action. Incomplete lineage identities
fail contract construction.

`resume_task` and `notify_task` rules now require an injected task registry and
a configured native task-identity field. A registered same-environment task
reuses its original `trace_id`; unknown tasks and cross-environment references
return `unknown_task_identity`. The registry records task-bearing ingress only.
State-update deduplication, durable persistence, terminal task transitions,
and concurrent transaction control remain open lifecycle work.

### 2026-09-19: Acceptance-derived terminal state and task replay

Historical checkpoint. The separate task-event types described below were
removed on 2026-09-28; their accepted behavior now runs through
`uah.trace_event/v1` and `LifecycleLedger`.

`EnvironmentTaskRegistry.record_acceptance(...)` now records the deterministic
judgment produced by `TaskAcceptanceEvaluator`. `accepted`,
`accepted_with_deficit`, and `rejected` are terminal and prevent later resume
or notify ingress with reason `task_terminal`. `suspended` remains nonterminal
and permits further task work. Terminal judgments cannot be replaced, and an
acceptance from another environment activation cannot close the task.

Task start, resume, notification, suspension, and terminal acceptance now emit
immutable `TaskLifecycleEvent` values using the Observatory event vocabulary.
Each event identity is a SHA-256 digest of its exact content. Duplicate event
identity, modified content, acceptance-before-start ordering, trace mismatch,
and duplicate task-bearing ingress fail closed. A fresh
`EnvironmentTaskRegistry.replay(events)` reconstructs task lineage, terminal
state, and duplicate-ingress protection without model invocation or evaluator
execution.

The lifecycle stream at this checkpoint remained in memory. The following
round adds its bounded persistence contract. Cancellation and native failure
are not accepted as generic terminal calls because their environment-owner
authority contract is not yet implemented.

### 2026-09-23: Versioned task-event persistence and restart reload

Historical checkpoint. `JsonlTaskLifecycleStore` and
`uah.task_lifecycle_event/v1` were superseded and deleted when the common
ledger became the only writable lifecycle authority.

`TaskLifecycleEvent` now has an exact
`uah.task_lifecycle_event/v1` serialization envelope. Missing or additional
fields, unsupported versions, non-string values, empty values, incompatible
event/status pairs, and event identifiers that do not match the serialized
content fail validation.

`JsonlTaskLifecycleStore` appends canonical JSON records and flushes each
accepted append through `fsync`. Reload first parses the complete stream, then
replays it into a fresh `EnvironmentTaskRegistry`; no partially reconstructed
registry is published. Missing stores produce an empty registry. Blank
records, non-UTF-8 data, malformed JSON, invalid events, duplicate events,
invalid event order, and an unterminated final record fail closed. A process
restart can therefore reconstruct task lineage, ingress replay protection, and
terminal acceptance without invoking a model or rerunning the evaluator.

This is a local, single-writer task stream rather than the full lifecycle
ledger. Cross-process locking, global sequence, timestamps, parent-event
links, compaction, and a directory-level power-loss transaction are not
claimed. Owner-authorized cancellation and native failure also remain open.

### 2026-09-23: TaskSpec compilation into one admission source of truth

`TaskSpecCompiler.compile(...)` now accepts one successful `start_task`
decision, a frozen `uah.task_spec/v1`, role, frame, registry, and reviewed
DomainContractPack. It emits one immutable `uah.compiled_task/v1` artifact.
The artifact contains the closed `InteractionModuleSpec`, compiled
`EffectObligation` values, merged prohibited effects, finite budgets, task and
trace lineage, environment lineage, and exact domain-pack revision.

Effect requests no longer carry object or evidence-owner authority. The
DomainContractPack maps each requested effect to one AB object, evidence owner,
and failure policy. Compilation fails if the rule is ambiguous, the owner does
not own the object, the effect is not a declared owner observable, the object
is outside the role's inspectable control band, the effect is prohibited, or
the ingress, task, frame, registry, role, task type, or pack revisions differ.
Mutable contract collections and altered compiled-task identities also fail
closed.

Only accepted task-start ingress may compile. Resume and notify ingress must
resolve the existing compiled artifact so a task cannot silently change its
projection, acceptance obligations, or budgets. The artifact excludes the
machine-local registry path from its content identity. The following round now
consumes this artifact through two-stage admission. At this checkpoint,
compiled-task and admission lifecycle events remained open; the common-ledger
section below records their implementation.

### 2026-09-28: Typed proposal and two-stage admission TDD seam

`ProposalNormalizer.normalize(...)` now converts one raw typed model output
into one content-addressed `uah.typed_proposal/v1`. The normalizer requires a
UAH-issued operation identity and raw-output artifact reference, canonicalizes
finite JSON arguments, requires exact object-reference agreement, and rejects
model-authored effect claims. Expected malformed output returns deterministic
reason codes rather than raising from later admission code.

`SemanticAdmission.admit(...)` evaluates that proposal only against its exact
`CompiledTask`. It checks task and trace lineage, role-owned output type,
projection reach, direct-control band, runtime callability, prohibited effects,
effect obligations, approved binding availability, binding ownership, runtime
mode, environment, schemas, and evidence adapter. Success emits an immutable
`uah.admitted_operation/v1` containing the exact proposal, binding revision,
schema references, runtime mode, and obligation identities. It grants no native
execution authority.

`DomainLifecycleAdmission.request_execution(...)` independently rechecks the
active environment run, binding environment, DomainContractPack revision,
operation deduplication, lifecycle owner, and readiness attestation. Success
emits an operation-scoped `uah.execution_lease/v1`; rejection returns domain
reason codes. The accepted tracer reaches a lease without invoking an
environment handler. Candidate bindings, foreign owners, inspection-only AB0
objects, incomplete binding contracts, changed domain revisions, duplicate
lease requests, and tampered proposal, admission, or lease content fail closed.

This was the initial executable two-stage authority slice. At that checkpoint it
did not validate arguments against referenced input schemas, persist admission
or lease events, model operation trees, express
cancellation/concurrency/version fencing, or dispatch the fake owner through
the lease. The next section records lease-only dispatch and accepted-path
events; schema validation and lifecycle controls remain open.

### 2026-09-28: Lease-only execution and common-ledger TDD seam

This continuation removes the direct
`execute(object_id, arguments, runtime_mode)` path instead of preserving it as
compatibility code. `InProcessEnvironmentOwner.execute(...)` accepts only an
exact `ExecutionLease`. It re-resolves and fingerprints the complete approved
binding, checks environment and lifecycle ownership, records
`execution_started` before invoking the native handler, and rejects a second
attempt even from a new owner instance. Native exceptions produce a durable
`execution_failed` event before they propagate.

Successful dispatch returns a content-addressed `uah.execution_receipt/v1`.
The receipt retains the owner-native result separately from normalized
`EffectEvidence` and binds both to the exact lease, admission, environment run,
task, trace, operation, binding, and owner. The recorded NAO qualification was
updated rather than bypassed: it now compiles typed obligations, normalizes
each planner operation, performs semantic and domain admission, executes the
lease, evaluates acceptance, and records the lifecycle. The redundant planner
gate and `required_observables` fallback were removed.

`LifecycleLedger` replaces `HarnessTrace`, `JsonlHarnessTraceStore`,
`TaskLifecycleEvent`, and `JsonlTaskLifecycleStore` as the writable source of
truth. Its `uah.trace_event/v1` envelope supplies a global sequence, causal
parent, recorded time, environment/task/trace/operation lineage, artifact
references, canonical replay data, strict JSONL persistence, optimistic
sequence checks, and `commit_id`/`commit_index`/`commit_size` framing. Reload
rejects incomplete or noncontiguous multi-event facts.
`EnvironmentTaskRegistry` now projects task lineage from that ledger rather
than maintaining a second event stream.

The authority-hardening pass also makes `DomainContractPack.issue(...)` derive
the revision from the exact role/task allowlists, ingress rules,
effect-to-object and evidence-owner rules, failure policies, and prohibited
effects. `EnvironmentIngress` and `TaskIngressDecision` are both
content-addressed. `TaskSpecCompiler` verifies their linked authority through
the decision and calls `EnvironmentTaskRegistry.require_start(...)`. The
ledger records the exact ingress artifact, decision ID, and domain-pack
revision. The raw task-start mutation method is not public, so compilation
cannot be authorized by registering a caller-authored `TaskLineage`.

Recorded NAO qualification now receives an injected content-addressed pack
rather than synthesizing one from a test case. It classifies a real
`EnvironmentIngress`,
uses the resulting ledger-backed decision, rejects malformed planner steps
instead of dropping them, and hashes the complete raw planner payload before
proposal normalization. These remain recorded ROS-free mechanics, not H2 owner
review, live planner parity, or model qualification.

The accepted tracer records task start, compilation, proposal, semantic
admission, domain lease, execution start/completion, evidence, obligation
outcome, and terminal acceptance. Restart replay reconstructs the authority
chain and derives a content-addressed `uah.verified_trace_digest/v1` without a
model or native handler. A second tracer proves that an unsatisfied
best-effort obligation remains visible as a deficit while the task is accepted.

Task budgets are carried as immutable declared limits in `CompiledTask`; no
runtime budget counter or enforcement loop is implemented yet. Proposal and
admission rejection, evidence rejection, stale evidence, timeout, cancellation,
retry exhaustion, false completion, `OperationEdge`, and prompt/model events
remain open.

### 2026-09-30: H0/H1 seam audit and authority hardening

The deslop and architecture audit tested the newest seams through their public
interfaces. Constructor-only content checks were insufficient: a proposal
could be changed after lease issuance and the in-process owner would dispatch
the changed arguments under stale proposal, admission, and lease identities.
`EnvironmentIngress` had the same weakness at classification. Content-addressed
ingress, compiled tasks, proposals, admitted operations, and execution leases
now reverify recursively at each policy, admission, ledger, receipt, and owner
trust crossing. Invalid nested content fails before native dispatch.

Two independently opened ledgers could also consume the same lease from stale
in-memory state, invoke the handler twice, and append duplicate global sequence
numbers. File-backed ledgers now take a portable OS advisory lock, reload and
reduce the complete stream, validate the proposed transition, append, and
`fsync` before releasing the lock. The second owner observes the recorded
execution start and rejects the consumed lease without dispatch. The lock
coordinates `LifecycleLedger` writers; arbitrary external file writers remain
outside the contract.

The pass also closed four narrower consistency gaps:

- resume and notify events retain the exact ingress artifact, decision, and
  DomainContractPack revision through restart;
- stale task-registry projections reload before admitting start or existing-task
  ingress, while replay globally fences task-bearing ingress identity and
  rejects a second `task_started` fact on one trace;
- a valid pre-dispatch `suspended` acceptance can be recorded without inventing
  an execution lease;
- owner-result normalization and receipt construction failures record
  `execution_failed` after the durable execution start and before propagation;
- registry snapshots reject duplicate object identities and projection rejects
  a frame from another registry revision;
- replay rejects event types outside the implemented lifecycle grammar.

The next blocking seam is typed counterexample replay. Native exceptions,
semantic and domain rejection, stale evidence, timeout, cancellation, and retry
exhaustion still need explicit artifacts and deterministic terminal or
resumable transitions before the H2 cooperative planner proof.

Observatory O1 now advances in parallel with those final H0 lifecycle slices.
Its first implementation target is a read-only projection and static renderer
for accepted, semantic-rejected, and domain-rejected traces. The ledger remains
the only writer. Each later failure family joins O1 only after restart replay is
stable, preventing the visualization layer from defining or repairing runtime
truth.

The follow-up architecture research is recorded in
`../research/uah_h0_h1_seam_deepening.md`. It compares three interface shapes
and recommends retaining the deep ledger interface, replacing the private
task-start callback with one public task-ingress authority, freezing
`OperationEdge`, and implementing failure families as TDD vertical slices. The
repo-local `.codex/skills/uah-guardrails` skill now routes implementation and
review work through the applicable authority, evidence, release, and validation
checks. Domain onboarding remains a separate future skill because it authors
and qualifies domain contracts rather than reviewing ordinary changes.

### 2026-10-01: Ingress authority, admission rejection, O1, and identity slice

Five TDD slices moved architecture contracts into executable seams:

- `TaskIngressAuthority` became the only public writer for accepted
  task-bearing ingress. `EnvironmentTaskRegistry` is now a read-only projection
  over the common lifecycle ledger. State updates and rejected ingress still
  lack an environment-scoped event family.
- Semantic and domain admission now return content-addressed rejection
  artifacts. Domain admission records its own rejection; the semantic
  coordinator records the returned artifact. Replay exposes both as
  nonterminal failure stages and does not infer terminal task rejection.
- Semantic admission now validates canonical arguments through a reviewed,
  content-addressed portable object-schema subset. The subset covers required
  fields, top-level JSON types, and additional-property policy. Executable
  callable validators were removed because their behavior was not determined
  by the claimed schema identity. `uah.admitted_operation/v2` pins the validated
  input-schema identity.
- The initial O1 renderer accepts a validated lifecycle ledger for `recorded`
  data, groups events into immutable trace projections, distinguishes terminal
  task status from nonterminal operation failure, escapes raw payloads, and
  embeds inert graph JSON. Arbitrary event collections default to `synthetic`.
- Initial H1 identity registries now cover content-addressed `AgentManifest`,
  one-time `AgentHandleRevision` registration, and environment-roster-bound
  `AgentRun` attachment in `attached_standby`. The registry refuses handle
  rebinding because the H3 fidelity evaluator is not implemented. It does not
  persist runs, emit lifecycle events, perform preflight, reserve hardware, or
  invoke a provider.

The integrity pass also made domain lease requests idempotent. Repeating an
exact request returns the same deterministic lease without appending a
conflicting rejection. Cross-task proposal/admission misuse now raises before
creating a trace-scoped rejection that could not replay under either lineage.
The recorded NAO semantic-rejection canary appends its typed rejection, so O1
can inspect the no-dispatch path.

At the 2026-10-01 checkpoint, the next H0 seam was `OperationEdge`, followed by
typed normalization and evidence rejection plus a terminal required-effect
counterexample. The following section records their completion.

### 2026-10-02: Operation graph, counterexamples, runtime controls, and O1 example

The next three ordered seams now have executable, replay-checked slices:

- `uah.operation_edge/v1` records frame-relative `decomposes_to`,
  `continues_with`, and `delegates_to` relationships. Replay requires both
  operations and their semantic admissions, rejects cycles or a second
  structural parent, and refuses an edge after the target lease. Cross-frame
  delegation remains fail-closed until a separately compiled target projection
  exists.
- Proposal normalization emits either one `TypedProposal` or a
  content-addressed rejection. Native completion emits either accepted effect
  evidence or `uah.evidence_rejection/v1`. Neither operation rejection invents
  terminal task status. A valid negative owner result can instead reach task
  acceptance, produce `terminal_task_rejected`, and derive a rejected
  `VerifiedTraceDigest` with the failed required obligation and native evidence.
- `uah.task_spec/v2` and `uah.compiled_task/v2` add a retry-attempt limit.
  Initial H1 runtime controls include typed execution failure, idempotent
  model/tool budget decisions, an atomic tool-budget plus execution-start
  commit, owner-authorized pre-dispatch cancellation, ledger-derived timeout
  evaluation, and bounded retry decisions. A retry decision grants neither a
  proposal nor an execution lease. Timeout facts record an observation; they
  do not claim asynchronous scheduler interruption.

O1 now renders explicit operation nodes and only recorded operation edges. It
also projects proposal, evidence, budget, cancellation, timeout, retry, and
task-acceptance failure stages without converting nonterminal facts into a task
rejection. The committed `o1_recorded_nao_canary.html` is regenerated from the
same deterministic smoke ledger and shows one accepted trace, one open semantic
rejection, and one terminal required-effect rejection.

The bounded SkillOpt wording pass used implemented accepted/rejected/control
traces as the train set and provider, multi-actor, and H2 claims as holdouts.
The accepted mutation removes completed seams from the forward queue while
preserving partial H1 and unqualified H2 labels.

### 2026-10-02: Lifecycle and identity deslop parity pass

The deslop pass used the latest dirty DEV checkpoint and compared the affected
seams with `nao_orchestrator`, `planner_common`, and `chatbot_llm`. Those
repositories contain useful owner-level gates and pure policy extractions, but
no authority-grade content-addressed identity layer. Their largest authority
owners also remain substantial. The UAH ledger and task compiler therefore keep
their existing public interfaces, and the pass does not split modules by line
count or copy the chatbot pattern of importing many private helpers across a
shallow file split.

The bounded corrections are:

- `_content_addressing.py` now owns the strict finite canonical-JSON and
  namespaced SHA-256 byte contract shared by H0/H1 authority artifacts;
- artifact-specific `verify_identity()` methods remain at their trust crossings
  because they own schema, nested-artifact, and domain checks;
- representative public artifacts have fixed golden IDs to detect byte drift;
- `CompiledTask v2` stores budgets once under its embedded `TaskSpec`, while
  retaining the `CompiledTask.budgets` property and lifecycle budget projection;
- lifecycle event support, prerequisite, and operation-scope metadata now live
  in one immutable private table, while transition dispatch remains explicit;
- optimistic ledger races use the typed `LifecycleSequenceConflict` rather than
  parsing exception text;
- the duplicate accepted-start compiler condition is one predicate.

The final two-axis review also found and closed two fail-closed defects. Domain
lease idempotency now accepts only the exact recorded `AdmittedOperation` and
lease identity, including the concurrent-writer fallback. `AgentRun` now
rejects lifecycle states other than the sole implemented `attached_standby`
state. Public-seam regression tests cover both cases.

The large lifecycle reducer remains cohesive and replay-tested. A separate
grammar module, operation-state rewrite, artifact base class, compiler context
wrapper, and broad runtime facade remain deferred because they would increase
the active DEV conflict surface or fail the deletion test.

## Verification dashboard

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest -q` on 2026-10-02 | 223 passed after operation-edge replay, rejection counterexamples, exact lease-idempotency fencing, agent-run status validation, runtime controls, O1 rendering, identity-byte characterization, and lifecycle/compiler deslop |
| `.venv/bin/python scripts/render_observatory_example.py --check` | Passed; committed O1 example matches the deterministic recorded NAO canary byte for byte |
| `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp .test-tmp\full-suite` | 42 passed |
| Focused `tests/test_workbench_protocol.py` red-green pass | 9 passed after strict identity, capability, duplicate-ID, and JSON checks |
| `PYTHONPATH=src .venv/bin/python -m ab_harness_nao` | Passed accepted lease-only execution, semantic no-dispatch rejection, strict replay, and verified-digest canaries through the explicit NAO adapter package |
| NeuralWorkbench `python -m pytest -q -p no:cacheprovider` | 29 passed |
| NAO planner/common/gate/supervisor/trace-viewer seam suite | 177 passed; 60 expected warnings for unavailable optional `interaction_skills` manifest |
| Chatbot planner-handoff/grounding/request-adapter seam suite | 72 passed with `planner_common` and `kb_skills` on `PYTHONPATH` |
| Chatbot `DialogueTurnEngine` focused read-only baseline | 112 passed against revision `a2ecca796...` |
| NAO planner supervisor and orchestrator gate focused read-only baseline | 41 passed against the `v1.0.0` source boundary |
| Current NAO/chatbot reference recheck at `81b14ef...` | Chatbot `DialogueTurnEngine`: 112 passed; pure NAO planner gate: 18 passed. The orchestrator relay-guard test remains ROS-environment dependent because generated `chatbot_msgs` is unavailable in the standalone Python environment |
| Wheel packaging regression | Passed: a temporary stale `build/lib` was seeded with five removed core modules, the wheel was rebuilt without isolation, and all removed modules were absent while `ab_harness_nao` remained packaged |
| Core forbidden-import audit | Passed; only stdlib and `ab_harness` imports |
| `./scripts/run_precommit.sh` | Passed after the authority-hardening, packaging, and documentation pass |
| `python scripts/render_agentic_harness_docs.py --check` | Passed after regenerating all canonical Markdown/HTML pairs |
| Markdown/HTML synchronization | Passed |
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
- [~] Split immutable identities. Agent manifests, initial handle revisions,
  roster-bound standby runs, tasks, traces, operations, and operation edges are distinct;
  role/model registries, durable actor lifecycle, model leases,
  and invocation identities remain open.
- [~] Add serialized contracts: versioned `TaskSpec` and a serializable
  content-addressed `CompiledTask` are implemented; strict standalone
  TaskSpec round-trip plus `EnvironmentProfile`, `EnvironmentRun`,
  `EnvironmentIngress`, and `TaskIngressDecision` round trips remain open.
- [x] Add frozen in-memory `EnvironmentProfile`, exact attestation authority
  checks, readiness-evidence presence, unique activation identities, and lookup.
- [x] Add content-addressed `EnvironmentIngress` and profile-, revision-, run-,
  binding-, and type-bound classification with typed rejection.
- [x] Preserve a configured domain task identity and issue a deterministic,
  environment-scoped UAH trace for `start_task` ingress.
- [x] Add an in-memory environment-bound task registry, duplicate-start
  rejection, and same-run `resume_task`/`notify_task` lineage lookup.
- [x] Add acceptance-derived terminal task state, common trace events, ordered
  replay, and rejection of later existing-task ingress after restart.
- [x] Add strict versioned common-event serialization, global sequence,
  timestamps, causal parents, atomic commit positions, canonical fsynced JSONL
  persistence, and process-restart registry reconstruction.
- [x] Derive the DomainContractPack revision from exact role/task allowlists,
  ingress rules, effect-evidence rules, failure policy, and prohibitions.
- [x] Content-address task-ingress decisions and require the matching
  ledger-recorded start before TaskSpec compilation.
- [x] Add cross-process advisory writer locking with reload-before-append and a
  two-ledger one-shot execution test.
- [~] Add owner-authorized cancellation/timeout/retry transitions. Pre-dispatch
  cancellation, recorded timeout decisions, and bounded retry policy are
  implemented; in-flight interruption and approved-retry continuation are open.
- [x] Add content-addressed `TypedProposal`, `AdmittedOperation`, and
  `ExecutionLease` contracts with separate semantic and domain decisions.
- [x] Validate proposal arguments through the reviewed portable input-schema
  subset and pin the schema identity in `uah.admitted_operation/v2`.
- [x] Add `EffectObligation`, `TaskAcceptance`, and pure task-acceptance
  evaluation after public seam confirmation.
- [x] Compile one closed projection, obligation set, prohibited-effect set, and
  budgets deterministically from accepted task ingress, `TaskSpec`, role,
  frame, registry, and DomainContractPack rules.
- [~] Enforce wall-time, model-call, tool-call, and retry budgets. Tool calls
  debit atomically with execution start, timeouts use recorded ledger time, and
  retry decisions enforce the compiled limit; provider model-call consumption
  is open.
- [ ] Add deterministic `PromptCompiler` output and artifact hashing from the
  same `InteractionModuleSpec` consumed by semantic admission.
- [x] Append content-addressed task start/resume/notify, compile, proposal,
  semantic admission, domain lease, execution, evidence, obligation, and
  acceptance events for the accepted authority path.
- [x] Derive a deterministic `VerifiedTraceDigest` from replayed lifecycle and
  obligation events.
- [x] Add typed semantic- and domain-admission rejection artifacts and events.
- [x] Add typed normalization- and evidence-rejection artifacts and events.
- [x] Add frame-relative operation edges with cycle, parent, and timing checks.
- [x] Add terminal required-effect counterexample replay and rejected digest.
- [~] Add stale evidence, timeout, cancellation, retry exhaustion, and
  false-completion cases. Timeout, pre-dispatch cancellation, and retry
  exhaustion are replay-covered; stale evidence and false completion are open.

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
- [ ] Freeze the NAO environment profile, named chatbot/planner roster, and
  content-addressed DomainContractPack revision.
- [~] Replace the recorded planner path with compiled projection, two-stage
  admission, exact fake-owner lease dispatch, evidence closure, and replay;
  package-owned `v1.0.0` parity fixtures remain open.
- [ ] Run explicit `legacy | uah | shadow` planner parity.
- [ ] Classify every disagreement before enabling UAH authority.
- [ ] Preserve dialogue, planning, orchestrator, perception, and execution owners.
- [ ] Keep chatbot assimilation behind planner parity.
- [ ] Preserve native `goal_id`, `request_id`, `plan_id`, `plan_version`, and
  `step_id` beneath UAH task, trace and operation identities.
- [ ] Preserve `report_result` as AB1 while tracing its explicit delegation to
  the chatbot run and return to native communication ownership.

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

| Gate | State on 2026-09-23 | Required before qualification |
| --- | --- | --- |
| Installable portable package | Green | Clean install smoke in a fresh venv |
| Deterministic boot command | Green | Preserve machine-readable output and nonzero failure exit |
| Accepted and rejected AB canaries | Green | Retain owner evidence and no-dispatch rejection proof |
| Workbench form | Green, bounded retrieval and protocol | H3 remains optional and shadow-only |
| Complete configuration identity | Partial | Agent manifests, initial handle revisions, standby runs, profiles, environment runs, ingress, and operation edges are distinct in memory; add role/model registries, persistence, scoped lifecycle events, fixed leases, and invocation identity |
| Lifecycle replay | Green H0, initial H1 controls | Common-ledger restart reconstructs proposal/semantic/domain/evidence rejection, operation edges, lease execution, obligations, accepted or rejected digests, cancellation, timeout, retry, and budgets; stale evidence and multi-actor events remain open |
| Failure suite | Partial | Add stale evidence, false completion, in-flight interruption, and approved-retry continuation |
| Task acceptance | Green accepted/deficit/rejected seam | TaskSpec v2 compilation, two-stage admission, exact lease dispatch, pure obligation evaluation, terminal replay, accepted-with-deficit, and required-effect-rejected digests are implemented; stale-evidence policy remains open |
| Documentation | Architecture checkpoint active | Keep Markdown/HTML diagrams, plans, contracts, artifacts and implementation status synchronized |
| Watson/Bonsai runner | Not started | Freeze provider-neutral protocol; one reproducible paired dry run |
| NAO planner parity | Not started | Recorded/fake full path under explicit authority mode, multi-actor trace, `report_result` delegation, and reviewed disagreement report |
| Live NAO/ROS authority | Explicitly excluded | Not required for H2; remains NAO-owner gated after fake/sim parity |

## Open issues

| ID | Issue | Blocking condition | Next proof |
| --- | --- | --- | --- |
| UAH-D01 | Lifecycle failure grammar is incomplete | Normalization/evidence rejection, terminal counterexamples, cancellation, timeout, retry, and budgets now replay; stale evidence, false completion, allocation, and agent transitions remain absent | Extend the same content-addressed grammar without inferring task status from operation facts |
| UAH-D02 | Candidate NAO bindings are unvalidated | No source-schema parity artifact | Compile fixtures from package-owned tests |
| UAH-D03 | No live model adapter | Watson/Bonsai matrix cannot run | Freeze provider-neutral request/result protocol |
| UAH-D04 | No stale/freshness contract in `ABObjectView` | Evidence closure is incomplete | Add clock/freshness fixture and counterexample |
| UAH-D05 | Identity layers only partly implemented | Agent manifests, initial handle revisions, roster-bound standby runs, environment activations, tasks, traces, and operations are distinct in memory; role/model configuration, persistence, lifecycle transitions, leases, and invocations remain open | Add scoped activation events, role/model registries, fixed leases, and invocation identity without synthetic task IDs |
| UAH-D06 | No Workbench trace bridge | Adaptation remains a paper design | Implement terminal-ledger to `WorkbenchObservation` adaptation without direct mutation |
| UAH-D07 | No PromptCompiler | Prompt, projection and deterministic admission can drift | Compile a prompt artifact and gate from the same immutable interaction module |
| UAH-D08 | Operation rejection is intentionally nonterminal | Normalization, semantic, domain, and evidence rejection replay as operation failure stages; explicit task acceptance separately creates terminal counterexamples | Preserve this separation in multi-operation and multi-actor traces |
| UAH-D09 | NeuralWorkbench gitlink absent | Intended companion revision is documented but not mounted | Restore and verify gitlink at `e76ba7e` without changing core dependency rules |
| UAH-D10 | Workbench protocol uses legacy `configuration_id` | Per-agent and per-run candidate provenance cannot be reconstructed under the new identity model | Version the protocol after identity contracts define exact request and model-call correlation |
| UAH-D11 | No hardware-aware model allocator | Local RAM, VRAM, context and concurrency constraints cannot govern model reuse or eviction | Implement an H1 fixed-instance lease interface, then add dynamic scheduling at H3 |
| UAH-D12 | No fidelity evaluator or qualified handle rebinding | Initial immutable handle registration exists and refuses a second binding | Add held-out fidelity evaluation, reviewed promotion, and rollback only in the H3 allocation/rebinding phase |
| UAH-D13 | Advisory locking does not repair crash-truncated commits | Cooperating writers serialize reload, validation, append, and fsync; strict reload rejects an incomplete multi-event commit | Add an explicit recovery or quarantine policy without weakening strict replay |
| UAH-D14 | NAO `report_result` registry drift | Intended NeuralWorkbench decomposition does not match the `v1.0.0` orchestrator callback | Owner-review a DomainContractPack revision and replay planner-to-chatbot delegation |
| UAH-D15 | Stale-evidence acceptance policy is incomplete | The same `CompiledTask` now controls accepted, best-effort-deficit, and required-effect-rejected outcomes, but evidence freshness is not typed | Add a recorded clock/freshness counterexample |
| UAH-D16 | H1 control facts do not terminate tasks | Cancellation, timeout, budget exhaustion, and retry exhaustion are visible nonterminal facts unless task acceptance closes the trace | Freeze task-level closure policy without turning every operation failure into task rejection |

## Next discriminating probe

Extend the initial H1 identity registries with scoped activation events,
fixed-instance model leases, startup preflights, and AgentRun transitions.
In parallel, add stale-evidence and false-completion fixtures. The following
runtime slice is deterministic PromptCompiler output and a provider-neutral
invocation port with model-call budget consumption before the ZeroTier Watson
probe.
