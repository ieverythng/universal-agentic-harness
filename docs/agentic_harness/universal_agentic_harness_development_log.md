# Universal Agentic Harness: Development Log

**Purpose:** Practical implementation ledger linked to the semantic masterplan  
**Updated:** 2026-07-30  
**Current release boundary:** H0 contract spine plus one H1 synthetic vertical
slice; no live ROS or model-provider integration

## Current state

| Area | State | Evidence |
| --- | --- | --- |
| Portable semantic kernel | Green | Frame-relative AB views, projection, role gate, JSONL trace |
| Semantic implementation bindings | Green | Candidate quarantine, approved resolution, runtime-mode selection |
| ROS-free environment owner | Green | Approved AB1 dispatch and owner-issued effect evidence |
| Recorded NAO qualification | Green | Chatbot handoff to planner proposal to gate to fake owner to evidence closure |
| Latest NAO AB0 seam map | Declared candidates | Five revision-pinned pointers across four canonical AB0 objects |
| Live chatbot/planner coupling | Not started | H2 shadow adapter and parity suite required |
| Watson/Bonsai model matrix | Not started | Frozen cases and configuration identity still required |
| Neural Workbench adaptation | Quarantined design only | No trusted runtime mutation or registry promotion implemented |

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

See [ADR 0001](../adr/0001-semantic-objects-and-shadow-first-bindings.md) and
the root [domain model](../../CONTEXT.md).

## Source assimilation record

The 2026-07-30 inspection used:

| Source | Revision | Relevant public seam |
| --- | --- | --- |
| `ieverythng/nao_chatbot_llm`, `feat/planner_llm_hooks` | `a1cddc2cf100ac9e1f7a33c1b67d55cd7bf48e37` | `build_planner_request_payload`, `DialogueTurnEngine`, `PlannerHandoff` |
| `ieverythng/nao-ros4hri-bridge`, `feat/TFM-LLM_planner` | `00aa66e54f55c82719ebeae469886ee127ebaf47` | `PlannerRequest`, `PlannerEngine.plan_request`, supervisor/gate, `FakeSkillEngine` |
| ZeroTier Watson/Bonsai evaluation | 2026-07-29 report | Watson strict-workflow control; Bonsai memory-efficient high-context challenger |

The UAH source does not import either NAO repository. The inspected seams are
represented as candidate pointers or reproduced as portable behavioral
contracts.

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

### 2026-07-30 — Latest NAO contract bindings

Declared candidate bindings for:

- `/planner/request` chatbot publisher;
- `/planner/request` `PlannerRequest` contract;
- `/planner/execution_feedback` `ExecutionFeedback` contract;
- `/planner/dialogue_act` `PlannerDialogueAct` contract;
- `/scene/summary` `SceneSummary` contract.

They remain candidates because declaration and discovery are not approval.

## Verification dashboard

| Command | Result |
| --- | --- |
| `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp .test-tmp\pytest` | 23 passed |
| Core forbidden-import audit | Pending final verification |
| `python scripts/render_agentic_harness_docs.py` | Pending after this canonical edit |
| Markdown/HTML synchronization diff | Pending after render |
| System-design DOCX render inspection | Pending |

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
- [ ] Add serialized `TaskSpec`, environment identity, and configuration identity.
- [ ] Append lifecycle events for compile, proposal, gate, dispatch, evidence,
  and terminal decision.
- [ ] Add stale evidence, timeout, cancellation, retry exhaustion, and
  false-completion cases.

### P1 — Build the evaluation runner

- [ ] Store frozen case suites and configuration manifests.
- [ ] Add milestones, minefields, repeated trials, and reliability aggregation.
- [ ] Add failure-injection fixtures and attribution checks.
- [ ] Add model adapter protocol and recorded-proposal replay mode.
- [ ] Produce Watson/Bonsai comparison artifacts without touching live ROS.

### P2 — NAO shadow parity

- [ ] Capture package-owned chatbot and planner golden fixtures.
- [ ] Validate candidate AB0 bindings against their exact source revisions.
- [ ] Run read-only shadow gates beside current validators.
- [ ] Classify every disagreement before enabling a cooperative gate.
- [ ] Preserve dialogue, planning, orchestrator, perception, and execution owners.

### P3 — Neural Workbench coupling

- [ ] Ingest immutable traces and counterexamples.
- [ ] Permit retrieval/posterior candidates only in reversible state.
- [ ] Add replay, opposing traces, disjoint holdout, owner review, provenance,
  and rollback gates.
- [ ] Keep code, canonical registry, permissions, evaluator, and promotion
  thresholds outside online mutation.

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
