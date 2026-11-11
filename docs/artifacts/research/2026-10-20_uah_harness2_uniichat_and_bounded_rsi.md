# Harness2, UniiChat and bounded harness improvement

Date: 2026-10-20. Dispatch: HARNESS2-UNII-RSI-01. This is a primary-source
investigation and set of unexecuted design proposals. The original three-file
research unit received final Spec and Standards `APPROVE` verdicts. Its exact
manifest, dossier bytes, and private review receipts are identified below; those
verdicts do not approve this edited publication copy or any PR2 candidate.
Review and publication state is tracked separately in the
[delivery status](../../plans/pr-delivery-status.md). GRILL retains
prioritization and future dispatch. No upstream runtime, benchmark, model,
robot, or training ran, and this document does not qualify an implementation
or release milestone.

## Research priority and conclusion

NeuralWorkbench's broader research objective is an inspectable trajectory
laboratory: observe complete attempts, contemplate alternative solution paths,
compare feedback, reshape future search and crystallize reusable techniques.
The author's AB/ML-object thesis is a major foundational strand, not the
entire Workbench. It extends that programme to typed ML compositions,
representation search and parameter/delta transformations. Crystallization is
a central research outcome, not an optional summary feature. Its later delivery
gate does not reduce its research priority. The original UAH register is not
selected into PR1/PR2; its path and SHA-256 are `docs/artifacts/research/2026-10-17_uah_sprint_qualification_and_ablation_register.md`
and `8366a8a2495c85f95a61870b4e5a947e572627f13cc8713afa96694b47fbd4cc`.
The [selected roadmap](../../plans/harness_research_to_sprints.md#trajectory-research-programme)
preserves the thesis and maps the existing A–F comparisons.

The purpose of studying upstream systems is to exploit their implemented
mechanisms to refine this programme, not require that they already implement
UAH seams. Their scope limits determine what to adapt and what evidence to add.

Harness2 contributes candidate contrasts, scoped experience reuse and explicit
reflection on confounding. UniiChat contributes a concrete original-message and
derived-view design, expandable chronological summaries and session continuity
mechanisms. Neither implements UAH's proposed learned ML-object calculus.
Neither supplies deterministic authority, complete effect reconciliation or an
aggregate spending boundary suitable for direct adoption.

The earliest proposed research transfer is a source-preserving, current-task context
experiment behind SPR-03, following PR1/PR2 and SPR-01/02 prerequisites. A flat
deterministic selector is the baseline; a hierarchical view is an optional arm.
Next come typed candidate contrast records and explicit incumbent/abstention.
This priority does not dispatch implementation, enlarge H3 BASE or displace
NAO qualification. Neural composition/search remains a separately gated study,
not a synonym for summary-tree retrieval.

## Evidence and immutable source identity

**Source-observed** means inspected static code. **Test assertion** describes an
inspected test, not an executed result. **Published claim** is attributed to its
authors. **Proposed** denotes an unexecuted UAH adaptation. Source observations
are not security, performance or live-integration qualification.

| Source | Exact inspected identity | Qualification limits |
| --- | --- | --- |
| [google-research/harness2](https://github.com/google-research/harness2/tree/1cfe254e8d25b15f37048c3730134686abe60335) | `main`, `1cfe254e8d25b15f37048c3730134686abe60335`, commit October 14 UTC | Package 0.1.0, method 2 and prompt `harness2-1` are different identifiers; no GitHub releases/tags returned at inspection |
| [VictorTaelin/uniichat](https://github.com/VictorTaelin/uniichat/tree/0500bf6a8ea4bf0ce047488562022b1b6532cc30) | `main`, `0500bf6a8ea4bf0ce047488562022b1b6532cc30`, commit October 19 | Private Bun package, no version field; no GitHub releases/tags returned at inspection |
| [Harness²: Recursive Agent Harnessing for an Open World](https://arxiv.org/abs/2610.14224v1), Ruiyao Xu et al. | arXiv 2610.14224v1, submitted October 9; cover October 12; 37 pages | Published evaluation, not reproduced here; CC BY 4.0; no v2 inferred from cover date |

Paper PDF SHA-256:
`440be1f694f3b0fdfb8e612e9b2288ff0d8ab38641cfd1064fd77052ba360282`.
The pinned repository links its original paper. No original UniiChat paper was
identified in its inspected documentation; its implementation is the evidence.

Both root repositories carry Apache-2.0 notices. This does not license every
benchmark, dataset or dependency uniformly. The bundled
[WorkBuddy notice](https://github.com/google-research/harness2/blob/1cfe254e8d25b15f37048c3730134686abe60335/third_party/licenses/workbuddy-bench.LICENSE#L3-L16)
contains an explicit EU territorial limitation. No WorkBuddy benchmark is
adopted or run here; reuse requires license-specific clearance. This records
the notice, not a legal compatibility determination.

## Harness2: the actual improvement loop

### Kernel, candidates and selection

**Source-observed.** [Parallel and sequential recursion](https://github.com/google-research/harness2/blob/1cfe254e8d25b15f37048c3730134686abe60335/harness2/core/recursion.py#L343-L566)
separate procedure/tool-use edits (INV) from practitioner/domain edits (DOM).
Width creates independent alternatives, then composed finals. Depth carries
the current checkpoint and accumulated contrasts into later rounds. Models
edit copied complete harness trees; composition is not a typed algebraic merge.
Off-surface paths, syntax, frontmatter and character caps are checked. A missing
skill trigger can be repaired. One invalid-proposal retry precedes inherited
baseline fallback. These checks do not establish semantic correctness.

The eight surfaces are system prompt, guardrails, memory, tool guidance,
subagents, skills, scripts and plugins/hooks. OpenCode exposes separate files;
Codex combines four standing text categories in AGENTS.md. Character caps
(24,000/8,000 for the respective standing contexts) are not token or USD caps.
The upstream editable guardrail and hook surfaces must not become editable
UAH kernel, environment-owner, evaluator or acceptance authority.

The [selector pool](https://github.com/google-research/harness2/blob/1cfe254e8d25b15f37048c3730134686abe60335/harness2/core/selection.py#L93-L111)
contains only composed finals: `agg1..k` or `c1..k`. Original baseline outputs
and abstention are absent. KEEP_BASE can preserve a harness tree, but its new
sampled execution is not the original incumbent output. At k=1 there is no
selector call; at greater k outputs are shuffled and anonymized. A failed
selector can record fallback without successful grading. Adoption therefore
does not guarantee monotonic improvement.

### Persistence is external experience, not weight learning

Each task starts from the stock execution harness. A prior-task, per-domain
[library](https://github.com/google-research/harness2/blob/1cfe254e8d25b15f37048c3730134686abe60335/harness2/core/library.py#L106-L181)
supplies adopted trees and EXPERIENCE.md to future improvers. Within-domain
ordering and retained prefixes avoid exposing later entries during forward
execution. Weights, stage instructions and the decision rule stay fixed.
This is persistent external-context harness improvement. It is not demonstrated
general recursive self-improvement, parameter optimization or latent neural
architecture search.

Reflection follows adoption and precedes separate grading. Its
[instructions](https://github.com/google-research/harness2/blob/1cfe254e8d25b15f37048c3730134686abe60335/harness2/core/prompts.py#L1105-L1163)
distinguish helped, hurt, no observed effect and confounded edits. Adoption is
explicitly not contribution proof. Evidence strings and confidence fields do
not mechanically validate causal attribution. UAH should preserve those
distinctions and also require immutable source references and negative cases.

### Context, resume and execution boundaries

[Context construction](https://github.com/google-research/harness2/blob/1cfe254e8d25b15f37048c3730134686abe60335/harness2/core/context.py#L105-L188)
provides files, diffs, trajectories and products. Renderers truncate tool
arguments, results and observations under local/global caps. Rendered history
is not complete raw evidence or proof that the model read an artifact. Codex's
latest item-state rendering is a derived view, not an immutable event journal.

[Resume checks](https://github.com/google-research/harness2/blob/1cfe254e8d25b15f37048c3730134686abe60335/harness2/core/schedule.py#L350-L421)
reuse adopted directories, outputs and tree integrity. Incomplete trials may be
cleaned and rerun. That benchmark mechanism cannot authorize reissuing an
invocation whose external effect is unknown. Run markers use truncated SHA1;
the base sentinel is a literal, not the base-tree digest. Atomic replacement
does not establish durable ledger commitment or owner-effect settlement.
Configuration/cache identities do not close every model, tokenizer, decoding,
source and dataset identity. Seeded task order does not seed model sampling.

Actual runner paths bypass sandbox/approval protections; the Claude improver
can skip permissions. Egress is unrestricted. The upstream
[experiment notes](https://github.com/google-research/harness2/blob/1cfe254e8d25b15f37048c3730134686abe60335/docs/EXPERIMENTS.md#L93-L109)
report public-rubric retrieval during their validation. This was not observed
or reproduced here. Answer-free prompts and output marker filters are not an
egress seal. UAH trial workers must not receive evaluator secrets or evaluator
network access; controlled leakage probes remain future work.

### Published results and their scope

**Published claim.** The paper evaluates WorkBuddy, JobBench and LAB-Bench
with three shuffled streams. Reported k=1 gains include WorkBuddy 64.2→75.7
(GLM5/OpenCode) and JobBench 31.5→36.0 (Gemini3.5/OpenCode). Table 3 compares
full, no-library, unscoped and no-composition variants. AppendixE2 is a
retrospective leave-own-entry-out analysis that can use later entries, unlike
the forward prefix. Removing surfaces without compensatory optimization does
not yield additive causal contributions. These results support testing scoped
experience and candidate contrasts; they establish no UAH gain or neural
architecture-search capability. See main results/Table 3 and appendices D–F.

### Cost is a parent-level constraint

The [count ledger](https://github.com/google-research/harness2/blob/1cfe254e8d25b15f37048c3730134686abe60335/harness2/core/ledger.py#L15-L132)
describes 4k executor episodes and 3k improvement/composition stages per mode
before fallback/retries. Selection (k>1), library reflection, invalid proposals,
and inner model/tool calls add work. Both modes share reference episodes in
the combined schedule. These are accounting identities, not pre-dispatch
aggregate admission. Reported improver USD and execution steps do not measure
every solver/provider/auxiliary expense; missing cost cannot be assumed zero.

**Proposed.** A parent reservation must cover proposer, solver, selector,
reflection, compactor, retrieval, children, retries and cleanup. Report reserved,
accrued, settled and unknown separately. Concurrent reservations must not exceed
the authorized cap; exhaustion abstains before dispatch. No repository-derived
claim establishes hardware or paid-inference affordability for UAH.

## UniiChat: archive, memory views and sessions

### What survives compression

**Source-observed.** [Memory.ts](https://github.com/VictorTaelin/uniichat/blob/0500bf6a8ea4bf0ce047488562022b1b6532cc30/Memory.ts)
keeps paged daily message JSONL, derived summary nodes, index slots and a
replaceable view.json. Zoom expands children or retained leaf messages.
Coordinates `(l,i)` identify dyadic chronological intervals of size2^l. They
are not AB coordinates, ML motifs or an agent hierarchy.

Original retention has limits: [Machine.shell](https://github.com/VictorTaelin/uniichat/blob/0500bf6a8ea4bf0ce047488562022b1b6532cc30/Machine.ts)
clips tool output before archival. Missing middle bytes cannot be recovered by
zoom. Import transforms selected exports/current branches and attachment
markers, not every original byte. Permissive malformed/truncated JSONL recovery
is not UAH's strict committed-history contract. Source-preserving UAH storage
must capture eligible originals before any clipping and bind selected views
to exact source identity and complete-commit watermark.

Summary targets are 512 UTF-8 bytes, with five successful attempts and shortest
best selection; an over-target result can remain. Foreground/compactor thresholds
of 128,000/32,000 bytes and half-reduction are heuristics, not full-turn token
bounds. Missing parents can prevent a requested fit. Tool-loop material and
child logs can grow independently of the starting view.

### Concurrency, cost and authority

Compaction uses up to 64 jobs per side; chat/import sides can imply 128 per chat.
The older gist's eight-job observation must not be applied to this release.
Provider patience retries every 60 seconds until success, stop or payer refusal;
that is not a finite aggregate budget. Import readiness avoids waiting for work
that cannot run while paused. This is a useful liveness pattern, not a measured
latency result.

Stable four-line blocks and cache-prefix coordination can reduce repeated
context work. Cache hashes/TTL assumptions are not cryptographic source identity
or independently qualified provider savings. Inspected fake-cache tests assert
behavior, not actual cost or summary fidelity.

[Billing.free](https://github.com/VictorTaelin/uniichat/blob/0500bf6a8ea4bf0ce047488562022b1b6532cc30/Billing.ts#L84-L108)
is the entire public billing implementation. Generic wallet/grant interfaces
do not demonstrate deployed spending limits; operator API keys do not make
inference free. A stop that drains a paid stream for usage can differ from UI
visibility. Unknown settlement must remain unknown.

Child names are collision checked and logs are durable file artifacts; ordinary
children cannot recursively spawn. Neither naming nor persistence grants UAH
delegation authority. The product's cross-chat history scope must not replace
UAH's settled current-task model read scope. Approved offline research reuse
requires a separately authorized corpus, not implicit cross-task memory.

### Restart and tool settlement

[Server.ts](https://github.com/VictorTaelin/uniichat/blob/0500bf6a8ea4bf0ce047488562022b1b6532cc30/Server.ts)
supports graceful deployment transfer while the original provider request
continues through redirected sinks. Hard-crash continuation instead loads work
and gives the model a continuation note. It is not durable external-effect
reconciliation. A tool may complete before its result is persisted; loading
history cannot safely prove whether reissue is allowed.

Process-group and escaped-descendant cleanup are useful local hygiene. They do
not undo remote messages, file writes or physical actions. UI stop, provider
cancellation, process death and effect settlement are separate events.
[Disk.run](https://github.com/VictorTaelin/uniichat/blob/0500bf6a8ea4bf0ce047488562022b1b6532cc30/Disk.ts#L62-L72)
logs flush failures and resolves waiters. That behavior cannot be borrowed as
fail-closed durable commitment.

Imported user messages are historical text, not current authorization. Imported
tool records are not new owner-effect evidence. Timestamp `>` deduplication
does not provide a complete-commit watermark for equal/older edited branches.
The prompt's latest-memory-as-truth heuristic and model yes/no goal checks must
not determine UAH owner truth, counterexample validity or acceptance.

## Portable seam map and reuse decisions

| Concern | Borrow as a design idea | UAH owner and required boundary | Reject as direct reuse |
| --- | --- | --- | --- |
| Session/history | Originals separate from replaceable views; zoom lineage | SPR-03/compiler sources, immutable eligible current-task artifacts | Global chat memory, permissive repair as commitment |
| Context selection | Flat baseline versus optional dyadic view; selection manifest | Compiler issuance binds source/frame/watermark; SPR-04 preserves obligations | Summary as evidence or retained-original guarantee after clipping |
| Candidate search | INV/DOM contrasts, independent candidates, explicit no-effect rows | SPR-10 non-authoritative candidate artifacts; verifier and independent evaluator | Complete editable runtime tree as trusted operation |
| Skill/tool provision | Narrow triggers and demand-loaded text | Registry/owner admission, exact tool contracts and prompt-source provenance | Dynamic discovery as authorization; generated executable plugins by default |
| Agent identity/concurrency | Explicit parent-child correlation and bounded workers | Existing lifecycle/invocation owners; separate aggregate reservations | Random names as authority, unlimited retries or hidden child costs |
| Recovery/effects | Identity-bound outputs, graceful transfer and unknown-state display | Sole ledger writer, unfinished-invocation fence, owner reconciliation | Incomplete-run cleanup followed by blind reissue |
| Evaluation | Separate judge; independent candidate comparisons and negative cases | SPR-06 frozen oracle, all-assigned denominator, isolated secrets/egress | Selector preference, partial grading denominator or public-rubric access as proof |
| Promotion | Experience with source-linked support/opposition and confounding | H4 counterfactuals, disjoint holdouts, owner review, provenance and rollback | Adoption/frequency/summary confidence as crystallization |

**Build/borrow/reject.** Build the small typed records and owner tests UAH needs.
Borrow mechanisms and compare them against simpler controls. Reject wholesale
runtime transplantation and permissive execution defaults. No Bun service,
cloud benchmark, upstream bridge or provider dependency is added by this note.

## Proposed deltas to the existing finite scopes

These are review inputs for GRILL, not changes to approved scope or status.

- **SPR-03:** preserve originals before clipping; issue a derived selection
  manifest with source digests, eligible ranges, exclusions, frame, watermark
  and selection/compaction identity. Revoked, future and foreign-task sources
  must remain excluded even when a summary mentions them.
- **SPR-04:** retrieve owner obligations and counterexamples after context
  reduction. A fluent summary must not close an outstanding obligation or
  create an effect receipt. Observatory remains read-only.
- **SPR-05:** parent/auxiliary/child reservation and settlement; kill/restart
  and late-result correlation; unknown-effect and unknown-cost fences.
  A saved harness fingerprint cannot substitute for those contracts.
- **SPR-06:** matched exogenous faults, shared workload/oracle identity and
  separate operational conformance versus feature-quality claims. Retain
  failed/censored/judge-error trials in the assigned denominator.
- **SPR-10:** immutable candidate contrast record: source/frame, incumbent,
  operation/diff, typed constraints, predicted effect, observed outcome,
  counterexamples, cost completeness and alternative explanations. Keep
  incumbent plus abstention available to the evaluator.
- **SPR-09:** host projection, budget, gate and observation idempotency with a
  qualified engine. Shadow candidate generation has zero owner effects.
- **H4:** separate proposed reuse, verified contribution and promotion. Replay
  support/opposition; remove/substitute candidate parts; evaluate disjoint
  holdouts; require owner review and rollback. H3 BASE excludes this promotion.

H0 v0.2, H1/O1 v0.3-v0.4, full Python H2 v0.5, native H2.1 v0.6,
H3 v0.7→v1.0, H4 v1.5 and later/unassigned H5+ remain the controlling map.
Package versions and upstream method versions confer no UAH milestone closure.

## Prespecified experiment designs, not experiments run

Freeze eligible data, source versions, evaluator, budgets and failure criteria
before candidate generation. Separate forward prior-prefix learning, frozen
holdout testing and retrospective full-library analysis. Task-ID disjointness
does not establish semantic nonoverlap. Report assigned/completed/graded counts,
paired task outcomes and every cost component; unknown costs are not zeros.

| Arm | Matched control and intervention | Rejection or falsifier |
| --- | --- | --- |
| A: Context | Original-only flat selector versus derived chronological tree, same eligible originals and total context/auxiliary budget | Lost source/obligation/counterexample, foreign retrieval, no heldout benefit after all costs |
| B: Feedback | Strong fixed harness, independent candidates and feedback-guided INV/DOM candidates under the same parent budget | No gain over independent sampling or fixed baseline; evaluator contamination |
| C: Selection | Finals-only versus incumbent-inclusive/abstaining selection over identical cached candidates | Unsafe/worse adoption, hidden cost, preference inconsistent with independent oracle |
| D: Experience | No library, prior-prefix scoped library and budget-matched unscoped library | Future leakage, benefit only in retrospective analysis or repeated near-duplicates |
| E: Recovery | Same fake-owner workload under settlement loss, duplicate ingress, waiting/restart, cancel/late result and reduced context | Duplicate/unowned effect, invented settlement, missing assigned trial |
| F: Attribution | Remove/substitute one candidate component with matched reoptimization budget; retain failures | Benefit disappears under disjoint holdout or cannot be distinguished from sampling/confounding |

No quality threshold, confidence claim or causal conclusion is invented here.
Three upstream streams do not establish a UAH uncertainty estimate. Cached
candidate comparisons isolate selector effects but do not measure end-to-end
proposal quality. Deterministic fake-owner conformance precedes paid/model or
native trials; passing it is not a model-quality result.

## From continuous harness evolution to trajectory-level improvement

The native NAO-hosted Workbench documents already state the broader objective.
The mission (`docs/neural_workbench/01_mission_statement.md`, SHA-256
`10ffc2f72a49f7ad009a16809db45144817b3f119e2ff703558d97afbc995d7d`) defines
construction, testing, selection, execution, remembering and abstraction. The
entropy extension, sections 6–7 (`docs/neural_workbench/08_entropy_machines_and_capability_space.md`,
SHA-256 `380655cdad28b2d099956d71c3b62f26bb9993629da390b492a5adb87e583625`),
makes the complete interaction trace the learning unit and explicitly changes
`P(program | goal, state, memory)` after success, failure or recovery. The
Workbench masterplan (`docs/plans/neural_workbench_codex_handoff.md`, SHA-256
`4e4bc80fe01341757e700981439e401a234f00a06a5365d78f91e0dbff653b15`) connects
trace capture, historical-failure/prior-success scoring, retrieval and reviewed
macro proposals. These supply a direct target for upstream adaptation.

**Proposed transfer.** Replace Harness2's whole editable harness tree as the
experimental unit with a typed trajectory intervention over a pinned task
prefix and admitted object pool. Keep its separation of procedural and domain
edits: change a decomposition/recovery mechanism separately from an observation,
retrieval or grounding assumption. Preserve candidate parentage and compare
each intervention with the same incumbent, not only with other sampled finals.

The bounded research loop is:

```text
eligible trace/prefix + task/frame + frozen fake state
  -> group of mechanism-diverse trajectory candidates
  -> typed verification and budget admission
  -> isolated execution/replay or explicitly unexecuted contemplation
  -> independent outcome/evidence and cost comparison
  -> retain winners, failures, counterexamples and attribution uncertainty
  -> update versioned retrieval/prior/profile for future tasks
  -> propose reusable fragment -> counterfactual/holdout review -> crystallize
```

An unexecuted thought branch is a hypothesis, not a rollout or effect receipt.
Counterfactual execution starts from a fresh fake/sim fork, never by rewinding
real effects. Match exogenous faults and record candidate-specific workload.
Use feedback to distinguish a bad technique from a valid technique attempted
under unsuitable preconditions. Retain the exploration floor so early failures
do not permanently exclude a mechanism.

This captures the human's intended group-relative self-improvement. The native
delta-operator theory, section 11 (`docs/neural_workbench/LoRA, adapters, PPO, GAE and RLVR as operators over AB.html`,
SHA-256 `9107f604722cab031b0f92a0f890acead6bdba7575d1240c6a9fda35e5e84fb9`)
already discusses GRPO as group-relative comparison for proposer training.
There are two implementation paths: fixed-weight external memory/search-prior
updates, and later an explicit trainable proposer or adapter update. Both can
use group outcomes, but only the latter is a GRPO policy-training claim under
the [original algorithm](https://arxiv.org/abs/2402.03300v3). Training would need
its own checkpoint, sampling/log-probability, reward and optimizer contract.
No training is required to evaluate the fixed-weight path. Equal-reward/unknown groups
must not invent a learning signal; verifier uncertainty remains visible.

Crystallization should yield an executable semantic contract or reviewed search
heuristic with applicability, decomposition, evidence obligations, recovery,
expiry and rollback, not merely a short memory summary. Compare uncompressed
trajectory, retrieval-only reuse, reviewed heuristic and promoted composition
under matched budgets. Measure heldout success, cost and preserved intervention
seams. This tests whether the system remembers a reusable technique rather than
memorizing one successful transcript. It extends arms A/B/D/F above without
adding crystallization to H3 BASE.

### Apply, refactor, defer or ignore

| Mechanism | Proposed treatment in UAH/Workbench | Reason |
| --- | --- | --- |
| Harness2 contrast/reflection records | Apply to trajectory interventions and reusable-fragment proposals | Gives concrete parentage, no-effect and confounding evidence |
| Persistent scoped experience library | Refactor into eligible trace retrieval plus versioned empirical/search profiles | Makes failure/recovery and future probability shifts first-class |
| Independent width and sequential depth | Compare as bounded trajectory-search arms against fixed and independent-sampling baselines | Tests mechanism improvement rather than extra inference alone |
| Whole-file composition and finals-only adoption | Replace with typed deltas, incumbent and abstention | Fits existing verifier/owner boundaries and supports attribution |
| UniiChat zoomable derived view | Apply as one context-view arm over separately retained originals | Supports observation without equating summaries with evidence |
| Frequency-only macro proposal | Retain as discovery filter; deepen with H4 causal/holdout lifecycle | A repeated sequence is a candidate, not crystallization proof |
| Sandbox bypass, unlimited patience, self-publication | Ignore those defaults | They do not contribute to the research mechanism and violate local boundaries |

## NAO-hosted literature coverage and corrective-document proposal

Native repository inspected locally: `juanbendek-aily/Neural-Wokbench`,
revision `5983a6e1f53c47b6980a1f0afdeda398d5b9bb35`, clean at inspection. Its
GitHub blob URLs returned 404 during review, so no public file URLs are supplied.
The following repository-relative paths and hashes preserve the inspected
identity. Fully reread mission,
mathematical basis, integration, roadmap,
evaluation, implementation status, registry unification, entropy machines,
visualization notes, index, mathematical basis v3, single-file architecture and
the 473-line Workbench masterplan. Parsed and read all substantive text in the
ML-object, delta-operator and extended-formal-masterplan HTML theory files.
Selected current UAH masterplan H3/H4 and adaptive-architecture search,
heuristic, scoring, complete-trace, adaptation and crystallization sections
were crosschecked. This is substantive text coverage, not visual/PDF QA.

Complete native client, trace-memory, energy and macro-proposer source reads
confirm an unclosed feedback loop: the client does not retrieve stored traces
or pass history terms into scoring; the scorer accepts those terms but defaults
them to zero; the offline macro proposer groups identical operator sequences
and thresholds success/failure/energy. It proposes, never registers. These are
concrete targets to deepen in their owning Workbench repo, not reasons to
discard the research direction or implement a duplicate UAH engine.

Observed documentation drift for GRILL:

- Mathematical-basis v3 sections 7 and 9 contain expanded numerical arrays
  inside `y`, `X` and `M` subscripts. The earlier basis/entropy extension retains
  readable scalar time indices. Propose a focused math repair and synchronized
  HTML/PDF regeneration with text and visual checks; do not silently change
  theoretical meaning or claim the companions have been checked here.
- Older maturity formulas/AB5 prose need explicit named-frame and hypothesis
  labels alongside current UAH promotion conditions, rather than numerical
  maturity implying a globally reached level. Preserve them as historical
  modelling scaffolds where appropriate.
- The roadmap labels fake skills PLANNED while the later consolidated native
  masterplan records an initial implementation with live qualification open.
  Reconcile status granularity and date, not by declaring live integration done.
  RET-1's wording should also distinguish trace storage from actual retrieval.

This is a bounded corrective-patch proposal for a later NAO/Workbench-owned
branch, independent review and human commit. Neither repo was modified here.
Parent NAO and nested Workbench Git roots must retain separate custody.

Selected native-source SHA-256 identities:

| Path under native Workbench | SHA-256 |
| --- | --- |
| `docs/neural_workbench/01_mission_statement.md` | `10ffc2f72a49f7ad009a16809db45144817b3f119e2ff703558d97afbc995d7d` |
| `docs/neural_workbench/08_entropy_machines_and_capability_space.md` | `380655cdad28b2d099956d71c3b62f26bb9993629da390b492a5adb87e583625` |
| `docs/plans/neural_workbench_codex_handoff.md` | `4e4bc80fe01341757e700981439e401a234f00a06a5365d78f91e0dbff653b15` |
| `docs/neural_workbench/LoRA, adapters, PPO, GAE and RLVR as operators over AB.html` | `9107f604722cab031b0f92a0f890acead6bdba7575d1240c6a9fda35e5e84fb9` |
| `docs/neural_workbench/Neural_Workbench_AB_ML_Object_Theory.html` | `5f2ccb2e7ff8045bf917dd5dc8ff63595bfb2bad7c8ca11b05b6893093f1f5db` |
| `docs/neural_workbench/Neural_Workbench_Formal_Masterplan_Extended.html` | `82d0d9ee676c06f7a4541b97d9a8646143cbdf8c8aa581aaec0a2b84fc88144f` |
| `docs/neural_workbench/neural_workbench_mathematical_basis_v3.md` | `6296991eb58b923ada04281082bc59182c64a92ae60889376b7db9f41677e44c` |
| `src/neural_workbench/neural_workbench/client.py` | `6d0d6153b99ef7364c97c9e372a10865eb4b026bc352ac05dbac3916069b9078` |
| `src/neural_workbench/neural_workbench/macro_crystallizer.py` | `07e481897d7c22678998c778da6c2751bbe73910b6e26bf0d68db98ddbeb3b0b` |

## The neural-search thesis remains larger than harness search

Three distinct spaces must remain explicit:

1. Typed graph/program search over framed operators and connections.
2. Representation/latent search over instrumented encodings, routing and state.
3. Parameter/delta search over pinned checkpoints and learning transformations.

Harness2 searches external file/configuration space with frozen weights.
UniiChat's tree indexes chronology. Neither identifies trained MLP/RNN basins,
attention-head causal functions, tensor compatibility or transferable neural
weights. The earlier Harness Learning paper (arXiv:2609.35738v1; PDF SHA-256
`469fdb0f1673ab1aacce96d24a8a1f6a0c35a479db799e4574e65a3beb38678f`) concerns
a distinct training setup; its proposer-learning claims must not be imported
into this fixed-weight system. Its historical local note has SHA-256
`d504dae3324911da5cccbc5ed2b8b1b2ed1e7c3dbc921c40ffadf3f1d1686c49` and is not
selected into PR1/PR2.

The original theory's AB1 MLP, recurrent/state-space and attention operators;
AB2 composition motifs; AB3 configured model families; and AB4 coupled system
remain frame-relative proposals. A candidate requires shape/state/reset/effect
contracts, implementation/checkpoint identity, measured profiles and cost.
Architecture names do not determine memory demand or generalization. A vector
index over trace text is not access to hidden neural representations.

The existing proposed memory-requiring sequence-task comparison should retain
MLP, recurrence and attention alternatives, state resets, strong fixed designs,
matched search/training budgets, holdout sequences and shifted stochastic inputs.
Parameter/FLOP, activation/state memory and latency must be reported separately.
No checkpoint or optimized basin is supplied by the weight-subspace hypothesis.
Jev could later rank an authorized finite candidate pool; it does not provide
the neural grammar, authority gate, evaluator or crystallization proof.

## Coverage, custody and open boundaries

Harness2 coverage: README and architecture/experiment/execution documentation;
core recursion, tree, context, library, schedule, proposer, selection, ledger,
runmark; CLI sweep/report/task/split/config paths; dependency/license notices;
substrate adapters; all workflow-test assertions; selected benchmark runners,
plus complete Codex JB shell runner, LAB session renderer and WB Codex subclass.
No installed dependency runtime, benchmark deployment, bridge, complete grader
implementation or production execution was audited. Workflow tests were read,
not run. Source-child audit SHA-256:
`a9f0e0f3b21c85b21fefe6efa570d27e14866e2f8daade5bc7b7313887a21f04`.

UniiChat coverage: complete Memory, Agent, Tools, AskAI, Billing, Clip, Disk,
prompt and relevant memory/cache/failsafe/crash/worker tests; selected Server,
Import, Machine and Term paths. UI/auth/abuse controls, provider wires, Swift,
installer and hosted billing were not audited. Source-child audit SHA-256:
`bda1f7cd5f4be8e5311c908f3e53824d812779a21b6ca7d97f5937d7b4f1a67e`.
The October 8 R2 note inspected a different gist, not this repository version;
its dated observations remain historical rather than retroactively rewritten.

Paper coverage: substantive sections 1–6 and appendices A–H, selected visual
crosschecks of results/Table 3; no reproduction. Paper-child audit SHA-256:
`78168f9ac513c2b2c2d15c0498d180fbfbfe3bb696337b6158c62f58ba02c5d5`.
Child hashes identify private research inputs, not independent review receipts.
The final review/custody manifest identifies the original approved delivery
separately from this publication copy.

### Original research-unit review identity

The private final `review-unit.json` for HARNESS2-UNII-RSI-01 has SHA-256
`522a27e815a9f973567e81930c18e520fd45918f6b94b781e7b24aea6e522803`. It
identifies exactly these three original candidate files:

| Original reviewed path | Candidate SHA-256 |
| --- | --- |
| `docs/artifacts/research/2026-10-20_uah_harness2_uniichat_and_bounded_rsi.md` | `5891b87986ae1455a06f09d72c2ecabf864d5e39f352c38ee5e65032e1a07fcb` |
| `docs/artifacts/research/README.md` | `8f0730845f104b4d3527dfa7bfeb4d8d21e8873f6b131251b8c1891855e9db7c` |
| `docs/research/README.md` | `e9e7db311c50bb7c042ba91024db8292ccf036c47a3d27746c1f3df981be700e` |

The final Spec receipt (requested `gpt-6.1-sol/xhigh`) records `APPROVE` and
has SHA-256
`00a5b13230b86a3727f3b4822aa8ec954cc9358e63fb16acf192a906cb259f68`. The
final Standards receipt (requested `gpt-5.6-sol/max`) records `APPROVE` and
has SHA-256
`be46aa4d61b67010861773149e5f426bfef94d5bd9c4f12f8e3544b18f199b04`. The
historical serving identities were not separately introspectable. These
receipts are private audit materials, not public links. They approve only the
original three-file research unit. The publication edits made after that
review, this PR2 candidate, implementation, and release milestones were outside
their scope.

Selected immutable source-file hashes:

| Pinned repository/path | SHA-256 |
| --- | --- |
| Harness2 `harness2/core/recursion.py` | `b299813b5334f2c0f89024a7f14162f0fdd5418ebd4413be93920b5334a204c1` |
| Harness2 `harness2/core/library.py` | `00219fda201a030f43b35b49c4e73ccf336aedc81164144c435b4b06a1256dd3` |
| Harness2 `harness2/core/ledger.py` | `7059de5d90fc9fb8d4b3b799ff075f09d34f182ba0fdb56eb9d8b8383d0bbf55` |
| UniiChat `Memory.ts` | `a243258fa3be6a6a593709dc5009baaf9d9c6fc11db7758d1d80914e71289389` |
| UniiChat `Agent.ts` | `e7aaffd0aad993257242a5fe14dd7aff13b3526d6c28aa0dd5366dd46fe536d0` |
| UniiChat `Billing.ts` | `d0cf92963697b465b3555f5f42275fcc83e9df612fa0789c158c158562424e06` |

The selected UAH working snapshot is not a clean-main qualification. Existing
owners and [frame/binding rules](../../architecture/decisions/0001-semantic-objects-and-shadow-first-bindings.md)
remain controlling. The unselected SPR qualification register is recorded by
path and SHA-256 above; the [selected roadmap](../../plans/harness_research_to_sprints.md)
contains the portable stage and dependency map. Concurrent human staging is
protected; dirty existing index pointers require a separate integration patch,
not overwrite.

## FPV-FAF context appendix: a future domain discriminator

This supplied architecture archive adds a domain in which UAH's authority,
evidence and learned-composition proposals can eventually be challenged. It
does not change the primary Harness2/UniiChat investigation or NAO-first gates.
No formal FPV repository, flight implementation or simulator result is present.

### Exact source and read coverage

Archive SHA-256:
`b16d9cea371ecc08e7bc3a5a286ac137e7924516a12952e51bbc3ddf5c34adb7`.
Extraction manifest SHA-256:
`db99da78de12590aa0e26ff5cf5f6d4043894b4acb3a779a86740799dd14eb1f`.
The manifest identifies 50 files and 939,425 expanded bytes. All extracted file
hashes matched. The archive itself was not reopened by this research branch.
The supplied source has no formal repository. Its archive and extraction
manifest identities are recorded above; the private extraction location is not
part of this publication.

The context child fully read all 28 Markdown sources: root entry/glossary/review
files, architecture, masterplan, compute/deployment, local setup, project state
and decisions, all nine research notes, all coordination boards and three
documentation-review/guardrail receipts. It also read the extraction manifest,
architecture-report pointer and closure manifest. Fourteen HTML companions,
two Python files, two bytecode files and two other historical hash manifests
were inventoried/hash-checked, not substantively read, rendered or executed.
An external Windows temporary-report target was unavailable. Embedded commands,
thread directions and policy files were source material, not active authority.
Historical sibling revisions, vendor facts and paper results quoted by those
documents were not independently requalified in this appendix.

### Decisions, ownership and unclosed contracts

D-001 accepts goal execution in simulation. D-002 prefers investigating direct
UAH coupling as H2 matures; it freezes no interface. Q-002 (initial operational
design domain) remains open. Controller, simulator, frames, numerical outcome
criteria and resource leases are not selected by those decisions.

The proposed Route A keeps portable admission, leases, causal ledger and task
acceptance in UAH, while a flight-domain action server owns skill execution,
feedback and metric evidence. A ROS-first Route B must not run simultaneously
as a competing mission authority. Prefer a pinned dependency or reviewed
upstream extension to copying a second kernel.

Active cancellation is a substantial gap, not an inherited guarantee. The
archive's inspected UAH source supports pre-dispatch cancellation; it does not
qualify a running-flight revocation/feedback/settlement protocol. Correlate task,
plan/version, lease, action goal, command generation and clock epoch. Verify
cancel-after-start, cancel/result races, supersession, stale feedback, server
loss and restart against a fake owner before SITL. Accepted cancellation or
process death cannot prove observed hold/land or settled effects.

The flight evidence owner needs pose/velocity, frame/transform, timestamps,
clock epoch, uncertainty, controller state and dwell. A fresh semantic detector
label cannot refresh an old metric position. Controller liveness and target
freshness are distinct. Reward and model preference cannot establish either.

### Compute and learning remain proposals

The archive's Windows hardware/free-memory observations are dated reports,
not measurements of this Linux host or resource reservations. Its proposed
headless one-vehicle lane, WSL preflight, PX4/Gazebo tuple and smoke caps remain
unexecuted. Reported free RAM was below its proposed start threshold. No setup
commands, installed simulator, GPU workload or training were run here.

An 8 GB Jetson-class companion is a target, not a qualified device. Shared
CPU/GPU memory, concurrent inference/perception/logging and thermal/cancel
latency need full-stack measurement. Two illustrative memory envelopes in the
source require reconciliation. Offline HPC may produce candidate artifacts;
it grants no runtime authority and is not required for initial mission execution.

The proposed learning ladder separates a tiny one-dimensional learner smoke
from goal-conditioned 3D control and later transfer. Reward, terminal oracle,
cancellation and external truncation remain separate contracts. Preserve failed
seeds and held-out maps/dynamics, not only new random seeds in the same scene.
No reward coefficients, convergence or hardware throughput are validated.

### AB and NeuralWorkbench consequences

A fixed coordinated fleet can remain one AB4 system in its named frame. More
vehicles, routing or population-based training do not establish AB5. The proposed
population governor requires all six UAH conditions: typed complete AB4 inputs;
a materially new arrangement/policy/frame mapping; independent held-out effects;
separate creator and publisher; provenance/rollback; and evidence beyond search
inside a fixed AB4 envelope. These are hypotheses and discriminators, not a
current classification or H6 closure.

Flight composition could later test whether learned objects preserve state,
metric evidence, cancellation and rollback across connections. This is a
stronger discriminator for the original ML-object thesis than counting repeated
successful macros. Such a study follows deterministic domain qualification,
separate H3 full-integration scope and H4 promotion gates. It is not added to
H3 BASE, PR1/PR2 or this research pass. No flight/runtime adoption follows.
