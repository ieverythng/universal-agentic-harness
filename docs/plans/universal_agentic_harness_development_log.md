# Universal Agentic Harness: Development Log

**Purpose:** Practical implementation ledger linked to the semantic masterplan  
**Updated:** 2026-10-08
**Target:** UAH H2 NAO planner qualification after ordered evidence gates pass
**Current release boundary:** H0 contract spine, one H1 synthetic vertical
slice, profile-bound state-update and new-task ingress, explicit NAO adapter
canary, quarantined Workbench retrieval, and enforced repository hooks;
the accepted authority chain, typed rejection branches, explicit operation
edges, and terminal required-effect counterexamples persist in one strict
common JSONL ledger and replay after restart. Initial H1 runtime controls,
durable actor activation, fixed model allocation, and O1 environment/task/trace
and actor rendering are present. Stale-effect-evidence policy, the live provider
path, and H2 planner parity remain incomplete

## Current state

### Consolidation and NAO-first priority on 2026-10-08

The human selected NAO as the first parity/test environment and deferred the
synthetic environment. The [consolidated handoff](../artifacts/reviews/2026-10-08_uah_consolidated_handoff.md)
records four original scoped closures plus the extra approved raw O1 repair.
At consolidation, original STD-02, SPEC-02 and ARCH-02 remained open. The R1 report-hash discrepancy,
incomplete R4-FIX primary review, stopped dashboard blockers and three R5
defects remain visible in their historical artifacts. R5 source is deferred
and unapproved, including if the human commits it.

NAO-first changes implementation order, not H0/H1/H2 qualification. The
masterplan's synthetic replay/failure-suite exit requirements remain unchanged
until a release-contract coverage mapping is explicitly agreed. Ingress
authority-bound command versus authenticated admitted proof was pending at
consolidation; an explanatory diagram was not adoption. The next prerequisite
was that human decision and reviewed core correction, then owner-reviewed NAO fixtures and
recorded/fake parity with O1 inspection. No source repair or live call is part
of this consolidation. The accounts below retain earlier round verdicts.

### 2026-10-08: Accepted task-start command boundary

The human subsequently selected the authority-bound ledger command for SPEC-02.
Callers request work through `TaskIngressAuthority`; they do not obtain task
authority by constructing matching decision IDs or raw start facts. The ledger
remains the sole public writer and replay owner. Its task registry is a
read-only provenance consumer, and historical unmarked starts remain readable
without authorizing fresh compilation. Ledger-file ownership remains part of
the trusted runtime boundary.

The [bounded ingress round](../artifacts/reviews/2026-10-08_uah_ingress_authority_repair.md)
began from committed docs HEAD `06f5a29`, with dirty runtime bytes frozen
separately. The candidate now rejects raw task-start writes, records command
provenance and checks it before fresh compilation. Historical unmarked starts
remain replayable without acquiring that authority. Exact implementation,
independent verdicts and closure checks are tracked in the round receipt.
Existing O1 example freshness drift was reproduced before repair.
No provider invocation or H0/H1 release sign-off follows from the accepted
decision. Subsequent scoped approval and the separately human-authorized
`864c6d3` agent/dependency commit are recorded in the round receipt. Both fresh
ingress reviews approve the restored seventeen-path target, not every supporting
module in that fifty-one-path commit. ARCH-02 is a separate scope.

The human subsequently clarified that this commit exceeded the selected-file
boundary. DEV removed `864c6d3` from the branch without changing working-tree
bytes. The ten screenshot selections and three explicitly named modules are
staged; other implementation and test changes remain uncommitted for manual
review. The exact partial snapshot fails import collection and is not qualified
for a replacement commit. The ingress review remains scoped to its frozen bytes.

### 2026-10-08: Accepted Observatory label restriction

The human selected rejecting unsupported `measured` and `reviewed` requests
through the current projector and renderer, including both source branches and
empty inputs. The [ARCH-02 round](../artifacts/reviews/2026-10-08_uah_arch02_label_repair.md)
starts from `864c6d3`; its source change and fresh gate remain separate from
SPEC-02 approval and the broader committed modules awaiting human review.
Supported recorded, synthetic and conceptual views retain their existing
behavior. No evaluator/review issuer or new writable store is introduced.

Two states must remain distinct: the unsupported-label defect's repair/review
status, and the **not-implemented** evaluator/reviewer provenance interface.
The latter is owned by evaluator/result and independent gate owners, with O1
as read-only consumer. Reopen on a real result consumer plus an owner-reviewed
contract binding complete frozen configuration, evaluator, source and exact
result, independent gate, scope/freshness and mixed populations, with replay
verification. The [owning contract](../architecture/observatory_contract.md#deferred-evaluator-and-review-provenance-interface)
retains the target label definitions and reopening criteria. A passing temporary
rejection gate cannot qualify measurement support or close H0/H1/O1.

The commit-scope correction stopped the separate ARCH-02 gate before either
fresh reviewer issued a verdict. Writer controls and isolated normal hooks
pass, but the correction remains uncommitted and independently unapproved.
The future evidence interface is still not implemented. No automatic new round
or release closure follows from the passing tests.

### Independent review qualification

The [October 5 review](../artifacts/reviews/2026-10-05_uah_h0_h1_independent_review.md)
found seven distinct blocking mechanisms. The [October 8 R0 receipt](../artifacts/reviews/2026-10-08_uah_r0_baseline_and_skill_handoff.md)
reproduces all seven against the captured dirty tree. Passing narrow fixtures,
including the rows marked Green below, does not establish H0/H1 exit or complete
authority conformance. R0 performed no runtime repair.

The [separate R1 receipt](../artifacts/reviews/2026-10-08_uah_r1_domain_pack_identity.md)
tracks only STD-01/SPEC-01: domain-pack identity revalidation before compilation.
R1 alone did not address the remaining six mechanisms or establish complete
failure-suite evidence and release qualification. Provider transport and evidence/freshness contracts
remain separately staged; no live endpoint result is implied by these checks.

[R2](../artifacts/reviews/2026-10-08_uah_r2_catalog_semantic_fencing.md)
is independently approved only for the admission-time catalog comparison.
SPEC-03 remains PARTIAL/OPEN because the post-admission owner gap reproduces
through public execution and restart. Five other mechanisms remained open
at that checkpoint. H0/H1 exit is not established by these repairs.

[R3](../artifacts/reviews/2026-10-08_uah_r3_ledger_integrity.md) closes the
reproduced ledger-export alias and stale-event consumer mechanisms under
STD-03/SPEC-04 at its independently reviewed bytes. Raw-iterable O1 projection
identity remains a separate reproduced residual, alongside the four untouched
mechanisms and incomplete catalog execution fencing. Human-approved versioned
admitted-object snapshots are the next separately frozen repair, not delivered
by R3. The synthetic suite will use a reviewed owner-local exact-content
predicate; its adapter and full integration evidence remain unimplemented.

[R4](../artifacts/reviews/2026-10-08_uah_r4_admitted_object_snapshot.md)
adds the v3 exact object snapshot and replay body, but returns CHANGES. The
catalog controls pass while all-marker removal and genuine old-object active
consumer probes reproduce authority gaps. The next separately frozen repair
must preserve historical readability without granting current execution or
evidence authority. Passing 435 tests and hooks before review did not detect
those alternative inputs; H0/H1 and SPEC-03 closure remain unqualified.

The [R4-FIX receipt](../artifacts/reviews/2026-10-08_uah_r4_fix.md) preserves a
complete second-review approval and an interrupted primary review with a
nested-field mismatch. Its aggregate gate remains CHANGES. The separately
authorized [nested-owner round](../artifacts/reviews/2026-10-08_uah_r4_nested_owner.md)
froze sources at 18:04:47 and closes with two fresh approvals and passing
integration, without retrying the interrupted review. Approval covers the
reproduced concrete-artifact mechanisms, not a release-wide authority proof.
The [O1 constructor correction](../artifacts/reviews/2026-10-08_uah_o1_conformance_fix.md)
has two scoped approvals and passing current integration checks after the
concurrent author freeze. The [follow-up index](../artifacts/reviews/2026-10-08_uah_review_followup_status.md)
tracks original findings without rewriting their historical verdicts.

The separately authorized [ARCH-01 correction](../artifacts/reviews/2026-10-08_uah_arch01_static_eligibility.md)
shares static operation eligibility between PromptCompiler and semantic
admission. The forbidden-observable public red fails before repair and passes
after it; permitted effects remain usable. Sources freeze at 18:26:32, with 116
focused and 510 shared-tree tests passing. Two fresh reviews approve the
bounded static rule and final integration passes.
Original SPEC-03 probes now reject catalog widening at admission and dispatch;
their early-stop limits and separately executed valid controls are recorded in
that receipt. These are finding-specific results, not release-wide conformance.

The separately frozen [R5 native foundation](../artifacts/reviews/2026-10-08_uah_r5_owner_local_foundation.md)
adds the synthetic note owner outside the core. The 22 native controls pass,
and the shared tree passes 532 tests. The source froze at 18:58:38, after the
18:55:53 soft target; the 19:12:53 hard bound is unchanged. Both fresh independent
reviewers reproduce a second-owner closure-fence bypass. Additional findings
cover retained-task nested identity and hardlink mutation; the candidate returns
CHANGES and stops without another automatic repair. Actual write and closure-content observations are distinct;
callback completion is not lifecycle commit or acceptance. Full-chain synthetic
qualification remains blocked on task-ingress producer provenance.

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
| Configuration identity | Partial | Role/model configurations, manifests, initial handles, profile-bound activations, fixed leases, startup reports, prompts, invocations, task/trace lineage, and operation edges are explicit; dynamic provider pools, context persistence, and complete configuration comparison remain open |
| Environment lifecycle | Partial green | Frozen profiles and attestation registration enforce owner, runtime, DomainContractPack revision, readiness evidence, and unique IDs; task-bearing ingress and terminal routing replay from the ledger; rostered agent attachment/termination, exact allocation, readiness, and standby are ledger-projected; in-flight interruption and native environment close persistence remain open |
| Domain contract authority | Reviewed compiler content-identity seam | `uah.domain_contract_pack/v1` derives its SHA-256 revision from role/task allowlists, ingress rules, effect-evidence rules, failure policy, and prohibited effects; compilation reverifies covered content, while other consumer and representation gaps remain unqualified |
| Task compilation and closure | Green narrow kernel seam | `uah.task_spec/v2` and `uah.compiled_task/v2` supply the sole projection, obligations, prohibitions, retry-aware budgets, and revision lineage; tool-call and model-call consumption are atomic with execution/invocation start |
| NAO adapter canary | Green recorded qualification | Injected DomainContractPack, authoritative ingress admission, strict planner-step validation, content-addressed raw output, input-schema validation, accepted lease-only execution, semantic no-dispatch rejection, terminal counterexample, restart replay, and verified digest run via `python -m ab_harness_nao` |
| Neural Workbench retrieval | Green candidate slice | Failure-aware bounded retrieval emits provenance-bearing candidates only |
| Neural Workbench promotion/adaptation | Quarantined design only | No trusted runtime mutation or registry promotion implemented |
| NeuralWorkbench repository | Boundary defined, gitlink missing | Intended companion revision is `e76ba7e`; `.gitmodules` exists but the UAH tree does not currently mount the gitlink |
| Workbench adapter protocol | Green contract slice | Focused tests cover serialization, handshake, mismatch, and observation-only override |
| Prompt compiler | Green bounded H1 slice | Versioned prompt pack and deterministic compiled task/role/domain projection, direct-operation schema, reviewed input-schema and binding fingerprints, task-scoped examples, and content-addressed prompt |
| Two-stage admission and execution | Green narrow kernel seam | Proposal normalization or typed rejection, bounded input-schema validation, semantic admission, domain lease, exact lease-only execution, distinct result/evidence artifacts, typed evidence rejection, explicit operation edges, and terminal required-effect rejection are executable; output validation, concurrency, stale evidence, and false-completion policy remain open |
| Runtime controls | Green initial H1 slice | Typed execution failure, model/tool accounting atomic with call/dispatch start, pre-dispatch cancellation, recorded-time timeout evaluation, and bounded retry decisions replay without granting proposal or lease authority; token/cost accounting and in-flight interruption remain open |
| Provider invocation | Green fake-provider H1 slice | Exact ready actor, unexpired lease, recorded compiled task, atomic model-call grant/start, raw finite-JSON completion or typed failure, restart-safe completed-call lookup, and no automatic retry of an outstanding call; live ZeroTier transport remains open |
| Agent identity and standby | Green bounded H1 slice | Role/model registries and non-reserving declaration preflight, ledger-backed roster attachment/termination with frozen profile/manifest/attestation/handle lineage, exclusive fixed leases, bounded owner readiness, ready/invoking/standby replay, and release; rebinding, dynamic scheduling, durable context, and live provider calls remain open |
| Observatory | Green bounded O1 slice | Static environment-run/task/trace index, explicit actor cards even before task start, terminal-status honesty, control/rejection failure stages, explicit operation nodes and recorded edges, provenance labels, search, inert graph JSON, and recorded-canary example; complete configuration/comparison views and O2 remain open |
| Repository guardrails | Green | Python-native pre-commit and pre-push hooks enforce hygiene, Ruff, tests, generated-doc synchronization, and a fresh repository-signature cache |

### H0-H2 launch preparation

The development target is the H2 cooperative NAO planner demonstration. H0 and
H1 are its qualification prerequisites rather than separate documentation
tracks.

| Release | Already proved | Required next | Exit evidence |
| --- | --- | --- | --- |
| H0 contract spine | Frame-relative AB views, binding quarantine, domain rules and ingress decisions, task compilation, input-schema validation, two-stage admission, typed normalization/semantic/domain/evidence rejection, operation edges, lease-only execution, terminal acceptance or required-effect rejection, persistence, restart replay, and verified digests | Output validation, stale evidence, false-completion attribution, and cross-frame target projection | Serializable accepted and counterexample lifecycles with model-free terminal replay |
| H1 runtime kernel | Narrow accepted/deficit/rejected slices, smoke CLI, role/model preflight, durable actor activation, fixed leases, owner startup reports, standby, PromptCompiler, fake-provider invocation with atomic model accounting, runtime controls, and O1 hierarchy | Live adapter, durable context, output validation, and complete failure-suite closure | Frozen synthetic suite reconstructs every terminal decision and `VerifiedTraceDigest` without the model |
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

### 2026-10-08: Review baseline and domain-pack compilation repair

R0 retained the October 5 finding IDs and captured hashes. All seven blocking
mechanisms still reproduced despite 344 passing tests. Two fresh reviewers
approved instruction fit for the new UAH iteration skill; one optional wording
nit remains. This is a workflow result, not runtime or model qualification.

R1 adds one compiler check using DomainContractPack's existing content hash.
Replacement and nested mutation of a failure policy under its issued revision
both failed the new public regression before the change. Both are rejected
afterward, while the untouched projection control retains its pinned compiled
identity. The initial relevant suite passed 109 tests. Final validation and
independent repair verdicts are recorded in the R1 receipt, not inferred from
that count. No schema, effect/freshness policy, provider or other authority seam
is changed by this repair. H0 and H1 remain partial implementations.

### 2026-10-08: Admission catalog fencing, bounded R2

SemanticAdmission now compares the catalog object with the existing complete
compiled ABObjectView before resolving a binding. The public drift regression
rejects without a lease and survives restart; a reviewed binding replacement
with unchanged object semantics remains accepted. Two fresh reviewers approve
the narrow delta. A separate public owner probe still accepts a prohibited
effect after post-admission catalog replacement, with negative and untouched
controls retained in the R2 receipt. This gap requires an approved data-carrying
seam at execution. No schema/store change or global SPEC-03 closure is claimed.

### 2026-10-08: Ledger integrity, bounded R3

Ledger public event, commit and replay exports now return detached TraceEvents.
Their existing content identity is reverified at serialization/data/reduction
crossings. Independent controls reproduce twelve old failures and pass on the
new bytes; the actual budget attack no longer changes a limit of three to 99.
Two qualifying fresh reviewers approve this narrow repair, with 388 tests and
hooks passing. One protocol-limited review remains retained and excluded.
Direct raw-iterable Observatory projection still has an identity bypass and is
explicitly outside this round. Neither release exit nor a provider result is
inferred from these checks.

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

The subsequent `codex/deslop-refactor` parity review accepted only changes that
preserve the existing authority contracts. Lifecycle sequence conflicts now
have a typed exception, lifecycle prerequisite and operation-scope metadata use
one immutable rule table, and an `AgentRun` rejects unsupported states at
construction. Domain admission fences idempotency on the exact admission and
lease identities through a lifecycle-owned query rather than scanning ledger
serialization in the domain owner. `CompiledTask` no longer repeats its budget
payload outside the nested `TaskSpec`; the content identity continues to cover
that authoritative nested value.

The proposed shared content-addressing helper was not ported. Representative
golden vectors now characterize four public artifact families, but they do not
establish one compatibility policy for every persisted identity, finite-number
rule, or error contract. Consolidation remains deferred until that complete
contract is specified. The recorded O1 canary also remains an inner trace view.
Static environment-run, task, and trace indexing belongs to the O1 H2 review
gate; actor facets wait for recorded `agent_run_id` events, while interactive
cross-environment navigation remains O2.

### 2026-10-04: Scoped actor activation, fixed model allocation, and O1 hierarchy

This continuation implements grill Decisions 2, 3, 4, 6, and 9 while retaining
the original H0-H2 gates. `uah.agent_role_configuration/v1` pins the typed role,
primary frame, reviewed domain-pack revision, projected object allowlist, and
declared model requirements. `uah.model_configuration/v1` pins the model artifact,
opaque endpoint reference, finite decoding settings, capabilities, and context.
Their registries and `RegistrationPreflight` are non-reserving. The preflight
checks declarations and never supplies measured hardware or task-capability
evidence.

`AgentRunRegistry` now attaches and terminates through the common ledger. An
attachment embeds the immutable manifest, handle revision, environment profile,
and owner attestation. Replay rejects a second live rostered handle and changed
profile/activation content under the same identity. Termination releases an idle
lease and appends its terminal fact atomically; an outstanding call blocks it.
Standby preserves the logical actor without
claiming durable conversation state.

The v1 task envelope keeps its serialized identity. `uah.trace_event/v2` adds
explicit actor scope and `agent_run_id`; agent events use null task and trace
identities. New task-scoped invocation events retain real task/trace identity
and name their actor. Older v1 task events are not heuristically assigned to
an actor.

`FixedModelAllocator` validates the exact configured model, a fresh owner-issued
resource snapshot, finite RAM/VRAM/context capacity, and exclusive host/instance
occupancy within the ledger. A snapshot older than 30 seconds fails. Only an
active exact request is idempotent; after release, a new acquisition requires a
new request identity. Startup preflight consumes the instance owner's exact
model/instance/lease readiness report with evidence, at most two attempts over
ten seconds, and 30-second freshness. Failure and release are atomic. The
allocator executes no provider probes or dynamic scheduling.

The dirty-tree audit tightened numeric contracts before allocation and call
admission. `TaskBudgets` rejects booleans, fractions, NaN, and infinity;
`BudgetDecision` requires integer debit, limit, and consumption values.
Replay also rejects changed model-instance or resource-snapshot content under
an already recorded owner identity. These guards retain valid artifact identities
and do not introduce a shared content-addressing codec.

O1 now indexes environment runs, tasks, and traces and renders explicit actor
events beside task views. Environments remain visible before any task exists.
Actor and trace cards retain raw immutable events, search, and event-type
filtering; graph JSON carries recorded actor identity. Conflicting actor
environment lineage is rejected. Complete configuration comparison and O2
interactivity remain deferred.

The bounded documentation iteration used restart, negative capacity, exact
lease, startup failure/release, and O1 grouping fixtures as implemented evidence.
The holdout was live endpoint capability, complete H1 context/failure handling,
NAO H2 parity, and H3 dynamic allocation. Accepted wording records the executable
contracts while preserving those open gates.

The continuation implements versioned `PromptPack`, deterministic
`PromptCompiler`, and `ModelInvocationAuthority` against a fake `ProviderPort`.
The compiler derives a direct-operation output schema from the same compiled
task and reviewed input schemas consumed by admission. It preserves binding
fingerprints and exact role/frame/domain/manifest/pack identity; examples are
filtered and validated under task scope. One model-call grant and invocation
start share an atomic ledger commit before the provider receives a request.
Completion preserves untrusted finite raw JSON; failure remains typed. A
completed ID resolves its recorded artifact after restart without reinvoking;
an outstanding call cannot retry automatically. Task acceptance waits for all
of its calls to settle. This proves fake-provider control mechanics, not live
transport readiness, model task capability, or H2 NAO parity.

## Verification dashboard

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest -q` on 2026-10-04 | 344 passed after scoped actor replay, role/model declarations, fixed allocation/readiness/standby, deterministic prompts, fake-provider invocation and failure/authority holdouts, strict numeric budget artifacts, and O1 hierarchy; no live provider or H2 parity claim |
| `.venv/bin/python scripts/render_agent_runtime_example.py --check` | Passed; synthetic H1 activation/invocation example matches its deterministic fixture |
| `.venv/bin/python -m pytest -q` on 2026-10-02 | 223 passed after operation-edge replay, normalization/evidence rejection, terminal counterexample digest, atomic tool-budget dispatch, cancellation, recorded timeout, retry exhaustion, O1 control stages, deslop-branch parity vectors, and recorded-canary rendering |
| `.venv/bin/python scripts/render_observatory_example.py --check` | Passed; committed O1 example matches the deterministic recorded NAO canary byte for byte |
| `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp .test-tmp\full-suite` | 42 passed |
| Focused `tests/test_workbench_protocol.py` red-green pass | 9 passed after strict identity, capability, duplicate-ID, and JSON checks |
| `PYTHONPATH=src .venv/bin/python -m ab_harness_nao` | Passed accepted lease-only execution, semantic no-dispatch rejection, strict replay, and verified-digest canaries through the explicit NAO adapter package |
| NeuralWorkbench `python -m pytest -q -p no:cacheprovider` | 29 passed |
| NAO planner/common/gate/supervisor/trace-viewer seam suite | 177 passed; 60 expected warnings for unavailable optional `interaction_skills` manifest |
| Chatbot planner-handoff/grounding/request-adapter seam suite | 72 passed with `planner_common` and `kb_skills` on `PYTHONPATH` |
| Chatbot `DialogueTurnEngine` focused read-only baseline | 112 passed against revision `a2ecca796...` |
| NAO planner supervisor and orchestrator gate focused read-only baseline | 41 passed against the `v1.0.0` source boundary |
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
- [~] Split immutable identities. Role/model configurations, manifests, initial
  handle revisions, ledger-projected actor runs, fixed leases, tasks, traces,
  operations, operation edges, prompts, and invocations are distinct; dynamic
  pool identities and automated invocation-to-proposal wiring remain open.
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
  subset and pin the schema identity in `uah.admitted_operation/v3`. The v3
  admitted-object snapshot and concrete-field consumption have scoped reviewed
  replay and active old-artifact fencing. Release-wide qualification remains open.
- [x] Add `EffectObligation`, `TaskAcceptance`, and pure task-acceptance
  evaluation after public seam confirmation.
- [x] Compile one closed projection, obligation set, prohibited-effect set, and
  budgets deterministically from accepted task ingress, `TaskSpec`, role,
  frame, registry, and DomainContractPack rules.
- [~] Enforce wall-time, model-call, tool-call, and retry budgets. Tool/model calls
  debit atomically with execution/invocation start, timeouts use recorded ledger
  time, and retry decisions enforce the compiled limit; in-flight interruption
  and task token/cost accounting remain open.
- [x] Add deterministic `PromptCompiler` output and artifact hashing from the
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
| Complete configuration identity | Partial | Role/model configurations and initial handles register in memory; actor attachment, fixed leases/readiness, prompt/invocation identity, and standby replay in the ledger; add context persistence and complete configuration comparison |
| Lifecycle replay | Green H0, bounded H1 activation | Common-ledger restart reconstructs authority/rejection/control facts, accepted or rejected digests, actor activation/termination, fixed allocation, readiness, and release; stale-effect-evidence policy and NAO multi-actor task parity remain open |
| Failure suite | Partial | Add stale evidence, false completion, in-flight interruption, and approved-retry continuation |
| Task acceptance | Green accepted/deficit/rejected seam | TaskSpec v2 compilation, two-stage admission, exact lease dispatch, pure obligation evaluation, terminal replay, accepted-with-deficit, and required-effect-rejected digests are implemented; stale-evidence policy remains open |
| Documentation | Architecture checkpoint active | Keep Markdown/HTML diagrams, plans, contracts, artifacts and implementation status synchronized |
| Watson/Bonsai runner | Not started | Freeze provider-neutral protocol; one reproducible paired dry run |
| NAO planner parity | Not started | Recorded/fake full path under explicit authority mode, multi-actor trace, `report_result` delegation, and reviewed disagreement report |
| Live NAO/ROS authority | Explicitly excluded | Not required for H2; remains NAO-owner gated after fake/sim parity |

## Open issues

| ID | Issue | Blocking condition | Next proof |
| --- | --- | --- | --- |
| UAH-D01 | Lifecycle failure grammar is incomplete | Rejection, terminal counterexamples, initial controls, allocation rejection, actor activation, and startup failure/release replay; stale effect evidence, false completion, and in-flight interruption remain open | Extend the same content-addressed grammar without inferring task status from operation facts |
| UAH-D02 | Candidate NAO bindings are unvalidated | No source-schema parity artifact | Compile fixtures from package-owned tests |
| UAH-D03 | No live model adapter | Fake invocation passes, but Watson/Bonsai matrix cannot run | Probe ZeroTier transport and live readiness through the frozen request/result protocol |
| UAH-D04 | No stale/freshness contract in `ABObjectView` | Evidence closure is incomplete | Add clock/freshness fixture and counterexample |
| UAH-D05 | Identity layers only partly implemented | Role/model configurations, manifests, initial handles, durable actors, fixed leases, readiness, prompts, invocations, and standby are explicit; durable context and dynamic pool identities remain open | Extend context persistence and configuration comparison without inferred lineage |
| UAH-D06 | No Workbench trace bridge | Adaptation remains a paper design | Implement terminal-ledger to `WorkbenchObservation` adaptation without direct mutation |
| UAH-D07 | Prompt compiler has a bounded direct-operation proof | Compiled prompt uses the same immutable task projection; dynamic context/memory and delegated outputs are absent | Run source-schema parity and live provider fixtures without widening deterministic admission |
| UAH-D08 | Operation rejection is intentionally nonterminal | Normalization, semantic, domain, and evidence rejection replay as operation failure stages; explicit task acceptance separately creates terminal counterexamples | Preserve this separation in multi-operation and multi-actor traces |
| UAH-D09 | NeuralWorkbench gitlink absent | Intended companion revision is documented but not mounted | Restore and verify gitlink at `e76ba7e` without changing core dependency rules |
| UAH-D10 | Workbench protocol uses legacy `configuration_id` | Per-agent and per-run candidate provenance cannot be reconstructed under the new identity model | Version the protocol after identity contracts define exact request and model-call correlation |
| UAH-D11 | Dynamic hardware allocation is absent | H1 fixed allocation checks fresh owner capacity and exclusive host/instance occupancy; provider pools, eviction, and arbitration are absent | Retain fixed H1 contracts and defer dynamic scheduling to H3 |
| UAH-D12 | No fidelity evaluator or qualified handle rebinding | Initial immutable handle registration exists and refuses a second binding | Add held-out fidelity evaluation, reviewed promotion, and rollback only in the H3 allocation/rebinding phase |
| UAH-D13 | Advisory locking does not repair crash-truncated commits | Cooperating writers serialize reload, validation, append, and fsync; strict reload rejects an incomplete multi-event commit | Add an explicit recovery or quarantine policy without weakening strict replay |
| UAH-D14 | NAO `report_result` registry drift | Intended NeuralWorkbench decomposition does not match the `v1.0.0` orchestrator callback | Owner-review a DomainContractPack revision and replay planner-to-chatbot delegation |
| UAH-D15 | Stale-evidence acceptance policy is incomplete | The same `CompiledTask` now controls accepted, best-effort-deficit, and required-effect-rejected outcomes, but evidence freshness is not typed | Add a recorded clock/freshness counterexample |
| UAH-D16 | H1 control facts do not terminate tasks | Cancellation, timeout, budget exhaustion, and retry exhaustion are visible nonterminal facts unless task acceptance closes the trace | Freeze task-level closure policy without turning every operation failure into task rejection |

## Next discriminating probe

Complete the separately reviewed authority-bound ingress correction adopted
on 2026-10-08. Then freeze owner-reviewed NAO `v1.0.0` contract and fixture
coverage, including output-schema, stale-evidence and false-completion cases,
and run the authorized recorded/fake parity through the existing public seams.
Inspect explicit environment/task/actor lineage in O1. Synthetic environment
integration is deferred; its acceptance obligations are not waived. ZeroTier
Watson transport remains a separately authorized later probe, and cannot
replace owner evidence, parity or release qualification.
