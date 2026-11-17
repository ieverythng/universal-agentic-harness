# Cordis/PTC lifecycle mechanisms worth reapplying to UAH

**16 November 2026 — bounded RESEARCH synthesis; proposals, not adopted architecture.**

The question is what can be **reused or adapted**, not whether either system replaces UAH. Two bounded assignments examined shipped DSH artifacts, used REA static analysis, exercised isolated public APIs, and compared existing UAH source/test assertions. Each was handled by the actual existing RESEARCH parent with its own native Team; the coordinator's Team remained separate. No kernel or sprint implementation was performed.

## Recommended direction

Reuse the existing UAH owners and strengthen a concrete missing seam: one frozen source for projected capabilities and rendered interfaces; separate raw/canonical/rendered results; exact-generation publication checks; retire admission before draining consumers; one owner for joined cleanup; subordinate resource limits; trusted safe overlap with exclusive barriers; separate actor/task/lease/program lifetimes.

Several are **already present** in UAH. The first useful transfer may be a conformance test or an adapter contract, not another framework. H0 projection/evidence, H1 invocation/allocation/resource ownership and optional future H3 composition are different owners/gates. These findings do not close H0/H1/H2 or authorize adoption.

## Selected artifacts and evidence types

The installed DSH packages were version **0.2.2-rc.1**; the DeepSeek Cordis vendor package was **4.1.0**. These are local artifact/version observations, not verified publisher provenance, an upstream Git tag, or a transitive dependency audit. Inspected package licenses declare MIT; actual copying or substantial translation still needs exact license/attribution review.

Portable source coordinates below identify the inspected built bytes, without publishing host paths, session identities, raw transcripts or analysis databases:

```text
C @deepseek-ai/cordis@4.1.0 / lib/index.js
  SHA256 627409afa06a265f7253200d3bc4648e88805c39fd3768568eb9b9518a31fe8f
T @deepseek-ai/dsh-tool-executor-ptc@0.2.2-rc.1 / lib/index.js
  SHA256 aab21d46e71316a97ad2a071ab7d8d21aa876c4192a4cd98094f61b2800cad9a
N @deepseek-ai/dsh-ptc-runtime-node@0.2.2-rc.1 / lib/index.js
  SHA256 952ffdd55654ccaedce2a9c004b68028fdcb31085987cc969d02438076260738
R @deepseek-ai/dsh-tools@0.2.2-rc.1 / lib/index.js
  SHA256 1889cbf718d64518dd83245d4dba1e1f080b2c5326259c3ed5b1be7a7666a2bd
P @deepseek-ai/dsh-tools@0.2.2-rc.1 / lib/pipeline.js
  SHA256 f6c850cefce30831c4c5f160e831856b105935331bacd1ae0823129001614bc6
```

Existing REA CLI **6.4.0** analyzed only two narrow extracted-JavaScript targets. Its actual analysis schema lacked a detail parameter, so each complete narrow result was retained once and reused through summary/page views; no duplicate PTC analysis or setup/upgrade was performed.

| Target | Retained parent Evidence | Coverage limit |
| --- | --- | --- |
| PTC runtime | `ev_43a687649fa877c1e76978fc55ebbcce5839757435b9a21419b14875fdcfbcaa` | Partial application/semantic coverage; 1,804 semantic unknowns and process-result budget limits. |
| Cordis | `ev_de5166eb8891c11c5690c9575ed4ca93523c4471d1c0fb78d106fd1658144b6a` | Application inventory complete only within analyzer scope; semantic status unknown, family coverage partial, 4,355 unknowns. |

REA parsed syntax; it did **not execute either target application**. Source inspection and the separate isolated public-API probes below are different evidence. Full private source/evidence manifests and probe results remain owner-custodied, not published as a raw operational archive by this PR. Summary documentation review does not turn proposals into architecture approval.

## How the lifecycles work

### Cordis: dependency availability and resource lifetime

```text
Context / plugin registration
  -> required injections resolved, or stable INACTIVE (no execution)
  -> generation/epoch captured -> LOADING -> ACTIVE or FAILED
  -> provider withdrawal hides new lookup
  -> existing committed consumers retire and finish owned cleanup
  -> provider release settles
  -> replacement can activate a new generation
```

Source coordinates: **C336–407** (construction/disposal), **C600–711** (requirements, epoch, activation and dependent retirement), **C1384–1413** (provider publication/withdrawal), **C463–529** (owned effects and cleanup).

An actual detached public `Context` probe, using memory-only services/plugins, observed:

- Missing provider: zero consumer activations. Late provider: ACTIVE generation1.
- Withdrawal hid lookup immediately, but its promise waited while consumer cleanup was deliberately blocked.
- `consumer-cleanup-end:1` preceded `provider-withdrawal-complete`; replacement activated generation2.
- Top-level cleanup trace `B-start -> A -> B-end`: reverse initiation is **not serial completion**.
- A failing nested cleanup skipped an earlier nested callback; root disposal restarted the root and permitted another effect. Do not copy failure-suppression/short-circuit assumptions as UAH success semantics.

All owned private plugin/provider disposers were awaited. A stale asynchronous publication race was **not executed**; generation checks are source-backed only. No global DSH Context, Host, worker process, provider, device or application was run.

### PTC: projected surface, program state and nested calls

```text
scoped registry selection -> generated SDK / exposed run_code
  -> exact policy + program-state ownership acquired
  -> lossless JSON subcall snapshots + correlated identities
  -> ordered pre/admission -> safe-body overlap or exclusive barrier
  -> schema-checked canonical result -> inert rendering -> ordered commit
  -> program return/error -> abort new callouts and drain started work
  -> release, or explicitly retained state under matching owner/policy
```

Source coordinates: **R477–591** (selection/current-definition checks), **T381–666** (program ownership, scheduler, subcall pipeline, drain), **T1709–1758** (SDK), **P451–565/P709–778** (dispatch/result), **N950–1068/N1273–1417** (worker cleanup/state ownership). The actual worker/RPC/sandbox/deadline/retained-state lifecycle was **source-inspected, not executed**.

A separate probe used the actual installed `PtcExecutor`, `defineTool` and shared pipeline with a **fake registry/context/evaluator and private memory**. It observed safe-body overlap with submission-order commits and an exclusive barrier; schema validation rejected malformed arguments before the body. An earlier mutation and an invalid-output mutation survived outer failure; explicit same-ID resubmission executed again; cancellation after a started memory effect did not undo it. These are executor-seam results, not claims about an uninspected higher live dedupe layer or real native effects.

## Ranked reuse matrix

Ranking is investigation/test priority, not implementation authorization. “Existing test” means full assertions were read, **not run** in this research assignment.

| Mechanism to reapply | Existing UAH analogue / actual gap | Narrow placement and next discriminator |
| --- | --- | --- |
| **1. One frozen source for callable view and SDK/diagnostics** | **Partial:** [configured invocation source closure](<../../../src/ab_harness/model_invocation.py>) already pins actor/lease/prompt identity. Worker lexical bindings/code-span diagnostics were not established. | Existing H0 projection and H1 compiler/invocation owners; optional derived renderer, not a second registry. Same source must yield the same permissions; rendering-only change cannot widen them. |
| **2. Raw, canonical and rendered results stay separate** | **Partial:** [execution receipts](<../../../src/ab_harness/environment.py>) already verify native/normalized agreement and detachment. General rendering/O1 behavior was not audited. | H0 evidence/identity and O1 consumer; add only a demonstrated missing diagnostic conformance test. Rendering changes must leave canonical receipt/digest unchanged; mismatched owner result rejects. |
| **3. Exact-generation publication fencing** | **Partial:** invocation identity, unfinished-call and pinned-source guards already exist. Generic hot-worker late-callback coverage is unverified. | Existing H1 invocation/allocator atomic transitions, using immutable actor/environment/lease references—not a global epoch service. Holdout: late failure from A cannot release or overwrite newer B. |
| **4. Consumer settlement before provider release** | **Already present** for invocation/fixed-model lease: [allocator release](<../../../src/ab_harness/model_allocator.py>) rejects busy release. General asynchronous resource drain is only partial/conditional. | Reuse the H1 busy-release guard. A real adapter may need no-new-consumer retirement while exact old users finish. Never-settling cleanup stays unresolved, not silently freed. |
| **5. Program caps subordinate to task-owned caps** | **Already present** model-call debit/no-refund; partial for a future program's elapsed/output/pending caps. | H1/adapter resource owner; local caps only narrow existing budgets. Holdout: local failure cannot refund the task debit or imply native stop. No second model counter. |
| **6. Trusted safe overlap with exclusive barriers** | **Partial:** [fixed-instance exclusion](<../../../tests/test_agent_runtime.py>) exists; general operation classifier/fairness/stress coverage does not follow. | Optional H1 bounded dispatch or environment adapter; default exclusive. Safe disjoint reads may overlap; unknown/throwing classifier serializes. AB level and `Promise.all` are not resource-safety evidence. |
| **7. One owner, joined cleanup outcome** | **Conditional new candidate:** release idempotency/startup-failure handling exist; a generic asynchronous physical-cleanup receipt protocol was not established. | H1 resource owner; H0 grammar changes only if existing obligations cannot represent a real case. Two waiters join one release; cleanup failure remains typed and does not suppress independent obligations silently. |
| **8. Actor/task, lease and evaluator-state lifetimes differ** | **Already present** actor versus lease/invocation; partial for subordinate worker-program identity. | Reuse H0 lineage/H1 owner contracts. Ending a program does not fabricate actor/task termination; unfinished invocation stays fenced after restart rather than replaying conversation memory. |

The inspected [invocation tests](<../../../tests/test_model_invocation.py>) already cover same-actor standby, cap0/no-call, failure/no-refund, early release inside provider invocation, unfinished-restart fencing and changed completed-prompt identity. Other source/receipt/late-result test names were discovery-only; inspect their complete bodies before adding tests. Do not present the research as executing those existing tests or proving a new coverage gap by filename search.

## Smallest next three experiments — not dispatched

1. **Fake worker reservation conformance:** first run/review existing allocator/invocation/budget tests; add an adapter-specific case only if it can bypass an existing guard. No process launch or new lifecycle framework.
2. **Source/canonical/rendered boundary conformance:** verify exact source/prompt identity, owner-result agreement and rendering-only invariance; inspect the currently discovery-only test bodies before adding another test.
3. **Partial native effect plus separately attested cleanup:** one fake owner effect remains recorded when a second operation fails; any cleanup needs its own real owner evidence. Begin with current receipts/obligations; new grammar only for a demonstrated unrepresentable obligation.

Preserve the [semantic-object/binding ADR](<../../architecture/decisions/0001-semantic-objects-and-shadow-first-bindings.md>), [foundation](<../../architecture/universal_agentic_harness_foundation.md>) and [masterplan](<../../plans/universal_agentic_harness_masterplan.md>): frame-relative AB objects, candidate-binding quarantine, separate semantic/domain admission, environment-owner effects, deterministic acceptance and one append-only ledger. Code adoption needs exact source/license review, a public-seam failing test, negative/holdout and replay/restart evidence, owner approval and fresh independent review. Optional dynamic composition may be H3; practical H0/H1 lifecycle lessons are not automatically H3. No runtime-product import into the portable core is proposed.
