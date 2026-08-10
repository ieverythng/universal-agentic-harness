# Universal Agentic Harness: Development Log

**Purpose:** Practical implementation ledger linked to the semantic masterplan  
**Updated:** 2026-08-04
**Target:** UAH H2 NAO planner launch gate by 2026-08-10
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
| H2 planner coupling | Active target | Planner ingress/egress projection, gate, fake owner, evidence and parity suite required |
| Chatbot coupling | Deferred after planner parity | Existing node retained as compatibility/reference implementation |
| Watson/Bonsai model matrix | Not started | Frozen cases and configuration identity still required |
| Configuration identity | Green | Complete model-harness-environment tuple is content-addressed |
| Launch smoke CLI | Green | Accepted path, rejected canary, and Workbench retrieval run via `python -m ab_harness smoke` |
| Neural Workbench retrieval | Green candidate slice | Failure-aware bounded retrieval emits provenance-bearing candidates only |
| Neural Workbench promotion/adaptation | Quarantined design only | No trusted runtime mutation or registry promotion implemented |
| NeuralWorkbench repository | Green boundary | Clean Aily branch pinned as `src/Neural-Wokbench` submodule |
| Workbench adapter protocol | Green contract slice | Focused tests cover serialization, handshake, mismatch, and observation-only override |
| Observatory | O1 contract frozen | Static renderer implementation required for H1/H2 review; O2 deferred |

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
| `ieverythng/nao-ros4hri-bridge`, `origin/feat/TFM-LLM_planner` | `9da89c0` | `PlannerRequest`, `PlannerGate.decide`, `PlannerEngine.plan_request`, supervisor, orchestrator dispatch, `FakeSkillEngine`; runtime tree differs from the local checkout only by unrelated career artifacts |
| `juanbendek-aily/Neural-Wokbench`, `feat/base-implementation` | `e76ba7eafbd90f9ed239a65f741d2598ecd033cb` | Standalone package boundary, candidate engine, verifier, trace memory, registry tools, stack observer, and synchronized generated docs |
| ZeroTier Watson/Bonsai evaluation | 2026-07-29 report | Watson strict-workflow control; Bonsai memory-efficient high-context challenger |

The UAH source does not import either NAO repository. The inspected seams are
represented as candidate pointers or reproduced as portable behavioral
contracts.

The 2026-08-04 revalidation fetched both remote branch heads without switching
the dirty NAO workspace. The chatbot remote and local source trees are
identical. The NAO remote adds only unrelated career artifacts over the local
runtime tree. Direct source and focused tests, rather than the stale 2026-05-31
GitNexus index, are the evidence for the current seam map.

## Implementation ledger

### 2026-07-30 — Semantic binding slice

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

### 2026-07-30 — Recorded NAO qualification slice

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

### 2026-08-04 — Latest NAO contract bindings

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

### 2026-08-04 — Quarantined Workbench memory

Added `TraceExperience`, `WorkbenchMemory`, and
`WorkbenchContextCandidate`. Retrieval is deterministic, query-scoped, and
bounded separately for supporting traces and counterexamples. Missing support
or counterevidence is surfaced as an explicit gap. The output status is always
`candidate`; the module has no promotion or registry-write path.

This is a concrete Neural Workbench coupling seam, not an H3 completion claim.
It prepares structured context for a later model adapter while keeping prompt
policy, trusted code, permissions, evaluator rules, and canonical AB objects
outside online mutation.

### 2026-08-04 — Content-addressed v0 smoke launch surface

Added `ConfigurationIdentity` and `python -m ab_harness smoke`. The smoke run:

1. identifies the complete recorded model, runtime, harness, adapter, registry,
   environment, suite, and evaluator configuration;
2. runs one admitted chatbot/planner/fake-owner path;
3. runs one out-of-projection rejection canary;
4. records both as Workbench experiences;
5. proves retrieval returns both supporting and opposing evidence.

This command is the initial boot qualification surface. It uses a recorded
fixture, not Watson, Bonsai, ROS, or a claim of general agent capability.

### 2026-08-04 — H2 and NeuralWorkbench boundary freeze

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

### 2026-08-04 — Pinned Workbench protocol seam

Added the NeuralWorkbench submodule and `ab_harness.workbench_protocol`:

- content-addressed, JSON-compatible `WorkbenchRequest`;
- candidate-only `WorkbenchCandidate` and `WorkbenchCandidateBatch`;
- immutable UAH-to-Workbench `WorkbenchObservation`;
- protocol descriptor and in-process engine port;
- fail-closed mismatch behavior;
- visible development override restricted to observation-only.

The protocol is transport-neutral. Network/service transports are deferred.

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

### Gate A — Boot qualification

Question: can this exact immutable configuration safely accept bounded work?

Minimum record:

- model, quantization, runtime build and flags;
- harness, adapter, prompt, registry, environment, and evaluator hashes;
- health/readiness and resource headroom;
- effective context, KV configuration, slots, and cache behavior;
- one accepted and one rejected AB canary;
- strict structured-output canary.

Boot acceptance proves operability only.

### Gate B — Promotion qualification

Question: does the candidate improve its intended task distribution without an
unacceptable regression?

Minimum record:

- frozen development and disjoint holdout sets;
- repeated trials and reliability across repeats;
- milestones, terminal effects, and protected-state minefields;
- failure-attribution slices;
- quality, latency, memory, and cost Pareto comparison;
- owner review, provenance, rollback target, and rollback rehearsal.

### Gate C — Runtime evaluation

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

### P0 — Complete the synthetic contract

- [x] Freeze semantic object versus implementation binding.
- [x] Enforce candidate quarantine and approved resolution.
- [x] Mount one deterministic owner without ROS.
- [x] Replay success, gate rejection, and failed evidence.
- [x] Add content-addressed configuration identity.
- [ ] Add serialized `TaskSpec` and complete environment policy.
- [ ] Append lifecycle events for compile, proposal, gate, dispatch, evidence,
  and terminal decision.
- [ ] Add stale evidence, timeout, cancellation, retry exhaustion, and
  false-completion cases.

### P1 — Build the evaluation runner

- [ ] Store frozen case suites and configuration manifests.
- [ ] Add milestones, minefields, repeated trials, and reliability aggregation.
- [ ] Add failure-injection fixtures and attribution checks.
- [ ] Add model adapter protocol and recorded-proposal replay mode.
- [x] Add recorded-proposal boot smoke mode.
- [ ] Produce Watson/Bonsai comparison artifacts without touching live ROS.

### P2 — NAO planner parity

- [ ] Capture package-owned chatbot and planner golden fixtures.
- [ ] Validate candidate AB0 bindings against their exact source revisions.
- [ ] Implement full planner projection, proposal gate, fake-owner dispatch,
  evidence closure, and replay.
- [ ] Run explicit `legacy | uah | shadow` planner parity.
- [ ] Classify every disagreement before enabling UAH authority.
- [ ] Preserve dialogue, planning, orchestrator, perception, and execution owners.
- [ ] Keep chatbot assimilation behind planner parity.

### P3 — Neural Workbench coupling

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

## August 10 H2 launch gate

The date is a focus mechanism, not permission to overclaim. H2 is launch-ready
when the core rows and planner parity rows are green:

| Gate | State on 2026-08-04 | Required before launch |
| --- | --- | --- |
| Installable portable package | Green | Clean install smoke in a fresh venv |
| Deterministic boot command | Green | Preserve machine-readable output and nonzero failure exit |
| Accepted and rejected AB canaries | Green | Retain owner evidence and no-dispatch rejection proof |
| Workbench form | Green, bounded retrieval and protocol | H3 remains optional and shadow-only |
| Complete configuration identity | Green | Add manifest input for Watson/Bonsai configurations |
| Lifecycle replay | Partial | Append compile-to-terminal events and replay without the model |
| Failure suite | Partial | Add stale evidence, timeout, cancellation, and false completion |
| Documentation | Active reorganization | Keep plans, architecture, artifacts, research, HTML, decisions, and system design synchronized |
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
| UAH-D05 | No configuration manifest | Results cannot be compared reproducibly | Hash the complete model-harness-environment tuple |
| UAH-D06 | No Workbench trace bridge | Adaptation remains a paper design | Define append-only candidate input, never direct mutation |

## Next discriminating probe

Serialize one configuration and task, execute the recorded success and a stale
evidence counterexample into append-only lifecycle events, replay both without a
model, and require the same terminal decisions. This completes the semantic
center before a Watson or Bonsai provider is allowed into the loop.
