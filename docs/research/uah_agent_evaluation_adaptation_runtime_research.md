# Research note: evaluation, bounded adaptation, and local-inference trade-offs for UAH

**Date:** 2026-07-30  
**Status:** Research input, not a canonical plan or implementation claim  
**Scope:** Primary sources relevant to boot, promotion, and runtime evaluation; failure attribution; bounded adaptation; and local model/runtime memory-context trade-offs.

## Executive finding

The defensible evaluation unit is not the model alone. It is the versioned
model-harness-environment configuration:

```text
model weights + quantization + inference runtime/build/flags
+ chat template and sampling/reasoning policy
+ UAH kernel + adapter + AB registry/projection + context/memory policy
+ tool/environment versions + evaluator + frozen task distribution
```

The literature supports execution-based, stateful, trajectory-aware evaluation
and shows that interface, environment, and evaluator defects can materially
change a score. It does **not** establish that the AB model or Neural Workbench
improves agent performance. That remains a UAH hypothesis requiring controlled
ablation.

A practical lifecycle is therefore:

1. **Boot qualification:** prove identity, readiness, resource headroom,
   protocol/schema behavior, and a few deterministic safety/structured-output
   canaries. Boot success proves operability, not general capability.
2. **Promotion qualification:** run repeated, held-out, execution-based tasks
   with regression and safety gates. Promote one immutable configuration, not a
   model name.
3. **Runtime evaluation:** retain end-to-end traces, monitor outcome and
   resource distributions, sample cases for review, and trigger degradation,
   quarantine, or rollback. Runtime observations may inform candidates; they
   must not rewrite trusted policy or publish AB objects directly.

## Sourced findings

### 1. Agent evaluations need environments, trajectories, and effect evidence

- [AgentBench](https://arxiv.org/abs/2308.03688) evaluates agents across eight
  interactive environments rather than reducing agent ability to isolated
  question answering.
- [WebArena](https://arxiv.org/abs/2307.13854) provides reproducible,
  fully-functional websites and evaluates the functional correctness of
  long-horizon task completion.
- [SWE-bench](https://github.com/SWE-bench/SWE-bench) evaluates patches in
  reproducible Docker environments. Its harness distinguishes tests that should
  change from fail to pass from tests that must remain passing; this separates
  task resolution from regression avoidance.
- [ToolSandbox](https://github.com/apple/ToolSandbox) stores world-state
  snapshots at every turn and scores an arbitrary trajectory against an ordered
  milestone DAG. Its guardrail similarity can require protected state to remain
  unchanged, while insufficient-information cases test whether an agent claims
  effects it cannot produce.
- [AgentBoard](https://proceedings.neurips.cc/paper_files/paper/2024/file/877b40688e330a0e2a3fc24084208dfa-Paper-Datasets_and_Benchmarks_Track.pdf)
  adds progress-rate and multi-faceted trajectory analysis because terminal
  success alone provides little diagnostic information.
- [τ-bench](https://arxiv.org/abs/2406.12045) compares final database state with
  the annotated goal state and introduces `pass^k` to expose reliability across
  repeated trials, not only best-case success.
- OpenAI's current
  [agent evaluation guidance](https://developers.openai.com/api/docs/guides/agent-evals)
  recommends traces containing model calls, tool calls, guardrails, and
  handoffs for debugging, then repeatable datasets and eval runs for comparison.

**Source-backed conclusion:** terminal text and a single pass rate are
insufficient for an agentic harness. Evaluation needs initial state, action and
observation history, intermediate milestones, protected-state minefields, and
authoritative terminal state.

### 2. Model, harness, environment, and evaluator failure are confounded unless isolated

- [SWE-agent](https://arxiv.org/abs/2405.15793) experimentally shows that the
  agent-computer interface changes agent behavior and software-engineering
  performance. A score therefore reflects more than model weights.
- The original
  [SWE-bench Verified analysis](https://openai.com/index/introducing-swe-bench-verified/)
  documented underspecified tasks, overly specific tests, and environment setup
  failures that could reject a valid solution. A later
  [OpenAI audit](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/)
  found residual test defects and benchmark contamination severe enough that
  OpenAI stopped recommending the benchmark for frontier capability tracking.
- [HELM](https://arxiv.org/abs/2211.09110) makes scenario, adaptation, and
  metrics explicit and publishes raw prompts and completions, supporting
  transparent comparison instead of a context-free score.
- [OpenTelemetry's GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/)
  define common attributes for model usage, cache use, tool definitions, calls,
  arguments, and results. The specification also warns that tool arguments and
  results may contain sensitive information.
- OpenAI's
  [evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
  recommend scoped tests at each stage, production-shaped task distributions,
  comprehensive logging, automated scoring where possible, human calibration,
  and continuous evaluation on every change.

**Source-backed conclusion:** UAH should report a system configuration result
and retain enough trace evidence to distinguish at least interface, environment,
evaluator, and model-associated failures. Exact causal attribution still
requires controlled reruns or interventions; a trace label alone does not prove
cause.

### 3. Evaluation is a lifecycle, not a one-time benchmark

- OpenAI's evaluation guidance explicitly describes continuous evaluation on
  every change, mining logs for new cases, and monitoring nondeterminism in
  production ([source](https://developers.openai.com/api/docs/guides/evaluation-best-practices)).
- NIST's AI RMF states that risk management should be continuous across the
  lifecycle. Its Manage 4.1 outcome includes post-deployment monitoring,
  override, decommissioning, incident response, recovery, and change management
  ([AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/)).
- Current OpenAI long-horizon deployment experience likewise argues that
  pre-deployment tests must be paired with trajectory monitoring, intervention,
  pause, and rollback capabilities
  ([source](https://openai.com/index/safety-alignment-long-horizon-models/)).
- The current `llama-server` exposes separate operational signals: `/health`
  distinguishes loading from ready, `/slots` reports context and per-slot
  processing state, and opt-in `/metrics` exports prompt/decode throughput and
  queue activity
  ([server documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)).

**Source-backed conclusion:** readiness, promotion evidence, and deployed
monitoring answer different questions and should not share one undifferentiated
“eval passed” state.

### 4. Continual learning requires explicit stability evidence

- [Gradient Episodic Memory](https://arxiv.org/abs/1706.08840) constrains
  learning on a new task so that loss on stored prior-task examples does not
  increase, while permitting positive transfer.
- [Experience Replay for Continual Learning](https://proceedings.neurips.cc/paper_files/paper/2019/hash/fa7cdfad1a5aaf8370ebeda47a1ff1c3-Abstract.html)
  uses replay and behavioral cloning to balance plasticity with preservation of
  prior behavior and demonstrates that replay can reduce catastrophic
  forgetting.
- [A-GEM](https://arxiv.org/abs/1812.00420) adds an efficiency focus and a more
  realistic protocol in which hyperparameters are selected on a small,
  disjoint set of tasks rather than on the learning/evaluation stream.
- [Safely Interruptible Agents](https://ora.ox.ac.uk/objects/uuid%3A17c0e095-4e13-47fc-bace-64ec46134a3f)
  formalizes the requirement that a learning agent not learn to seek or avoid
  interruption and uses off-policy properties to preserve interruptibility.

**Source-backed conclusion:** “learn from every successful run” is not a safe
continual-learning protocol. New experience must be assessed against prior
experience, disjoint holdouts, and interruption/control properties.

These papers study learned policies and neural systems, not UAH registry
promotion. Applying their results to trace retrieval, heuristic updates, or AB
object promotion is an architectural analogy and must be tested independently.

### 5. Local-model efficiency is a quality-constrained system trade-off

- [MLPerf Inference rules](https://github.com/mlcommons/inference_policies/blob/master/inference_rules.adoc)
  define a run over the system under test, including pre/post-processing, and
  require both latency and quality conditions for the relevant scenario. This
  is a useful precedent for rejecting throughput-only model selection.
- Upstream [llama.cpp](https://github.com/ggml-org/llama.cpp) supports multiple
  weight quantizations and CPU/GPU hybrid inference. Its
  [server options](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
  independently control context size, logical and physical batch sizes,
  parallel slots, continuous batching, flash attention, KV offload, and K/V
  cache types. These parameters can change memory, first-token latency,
  throughput, and concurrency without changing the named model.
- Prism's Ternary Bonsai 27B
  [model card](https://huggingface.co/prism-ml/Ternary-Bonsai-27B-gguf)
  reports a roughly 7.2 GB resident language-model pack, about 14.7 GB peak at
  100K context with uncompressed KV, and about 10.1 GB with its 4-bit KV path.
  These are vendor measurements, not UAH-verified results.
- Prism's
  [KV-cache documentation](https://github.com/PrismML-Eng/Bonsai-demo/blob/main/KV-CACHE.md)
  says 4-bit K/V cache reduces cache memory substantially but can lose accuracy
  without a model-specific mean-centering calibration.
- Prism's
  [speculative-decoding documentation](https://github.com/PrismML-Eng/Bonsai-demo/blob/main/SPECULATIVE.md)
  says its current speculative server path uses one slot and disables
  cross-request prompt-cache reuse, requiring conversation re-prefill on every
  request.
- The Bonsai model card explicitly lists long-horizon, multi-file,
  run-test-repair agentic coding as a limitation of the current release
  ([model card](https://huggingface.co/prism-ml/Ternary-Bonsai-27B-gguf)).

**Source-backed conclusion:** Bonsai's memory advantage creates an important
candidate operating point, but it does not establish agentic parity. KV
quantization, speculative decoding, context length, caching, concurrency, and
thinking policy must each be evaluated as part of the configuration.

## Proposed implications for UAH

Everything in this section is a proposal derived from the sources and the
repository's current H0/H1 boundaries. It is not an implemented feature or a
validated research result.

### A. Three gates with different authority

| Gate | Question | Minimum proposed evidence | Authority |
| --- | --- | --- | --- |
| Boot | Is this exact configuration safe and usable enough to accept work? | hashes/versions; server and dependency readiness; effective context and slot count; memory headroom; schema/tool canary; one accepted and one rejected AB case | May admit the immutable configuration to a bounded runtime role |
| Promotion | Is the candidate better enough on its intended task distribution without unacceptable regressions? | frozen train/dev/holdout ledger; repeated trials; milestone and terminal effects; minefields; capability/harness/runtime failure slices; latency-memory-quality Pareto comparison; owner review; rollback target | May publish a reviewed configuration or AB object version |
| Runtime | Is the promoted configuration still behaving within its envelope? | sampled traces; deterministic effect checks; failure and retry rates; resource/latency drift; scope violations; stale evidence; tool/environment health | May continue, degrade, quarantine, interrupt, or roll back; never self-promote |

Boot should be short and deterministic. Expensive stochastic agent suites belong
at promotion or scheduled qualification, not every process start. A boot gate
may reuse a previously signed promotion record only when every identity field
still matches.

### B. Failure-attribution record

Record one primary observed failure class plus evidence, without pretending
that observation proves root cause:

| Class | Example observable |
| --- | --- |
| `runtime_preflight` | wrong model/quant/build/flags, load failure, insufficient headroom |
| `transport_or_provider` | timeout, malformed stream, proxy field dropped, wrong endpoint/model alias |
| `context_projection` | required registry object or fresh evidence absent/truncated |
| `model_proposal` | invalid typed output, wrong tool/arguments, fabricated effect, instruction miss |
| `gate_or_harness` | valid proposal rejected, invalid proposal admitted, retry/state-machine defect |
| `environment_owner` | tool or simulator failed after a valid admitted action |
| `evidence_closure` | action occurred but authoritative success observation is missing or stale |
| `evaluator` | ambiguous task, broken fixture, nondeterministic or overly specific acceptance test |
| `resource_budget` | context, memory, latency, concurrency, or energy budget exceeded |

Use controlled replays to sharpen attribution:

- replay the same recorded proposal with the model removed to test gate,
  adapter, environment, and evaluator paths;
- hold harness/environment fixed and swap only the model configuration;
- hold model/environment fixed and ablate AB projection, memory retrieval, or
  retry policy one at a time;
- inject known tool, transport, stale-evidence, and evaluator faults and require
  the trace to localize them.

### C. Bounded Neural Workbench adaptation

Permit online updates only to explicitly untrusted, reversible state:

- append traces and artifacts;
- update a capability posterior or retrieval score within declared bounds;
- retrieve both supporting and counterexample traces;
- generate candidate pulses, context deltas, recovery hints, or AB2+
  crystallization proposals in quarantine.

Do not permit online updates to:

- model weights or executable harness code;
- canonical AB definitions, effect signatures, permissions, or environment
  ownership;
- promotion thresholds, holdout membership, evaluator logic, or rollback
  targets;
- the trusted runtime registry.

A candidate should pass replay over supporting **and opposing** traces,
regression on prior promoted behavior, a disjoint holdout, adversarial
minefields, resource budgets, provenance review, owner approval, and a tested
rollback before publication. Report forward gain and backward regression
separately; aggregate success can hide catastrophic loss on an older slice.

### D. First UAH model-harness experiment

Use the existing Watson/Bonsai evidence only as a starting hypothesis. Run a
paired matrix in a ROS-free NAO emulator:

```text
models:
  Watson control
  Ternary Bonsai challenger

harness modes:
  flat/static task prompt
  AB task projection + deterministic output gate
  AB projection + trace retrieval (success only)
  AB projection + trace retrieval (success + failures/counterexamples)

task slices:
  chatbot response and planner handoff
  valid AB1 proposal
  direct AB0 and out-of-projection rejection
  stale observation and false-completion minefields
  tool failure, retry, cancellation, and recovery
  strict structured output
  long-context evidence retrieval
```

Run each stochastic case multiple times and report both success rate and
reliability across repeats. Use environment state/effect checks as the primary
grader; reserve LLM judges for qualities without deterministic observables and
label them separately.

### E. Quality-constrained runtime optimization

Freeze the task/eval suite before tuning. For every candidate, record:

```text
model/GGUF hash, quant format, runtime repository + commit + build flags,
server flags, chat template, reasoning/sampling policy, context allocation,
batch/ubatch, slots/concurrency, KV types/calibration, cache state,
harness/adapter/registry/prompt hashes, driver/hardware identity
```

Measure cold and warm first-token latency, prompt throughput at several fixed
lengths, sustained decode throughput, peak and minimum-free RAM/VRAM, request
failure rate, queueing under intended concurrency, structured/tool correctness,
long-context retrieval, and full workflow success. Treat speed or capacity as
eligible for promotion only after hard correctness, safety, scope, and evidence
gates pass.

For Bonsai specifically, test FP16 versus calibrated 4-bit KV as separate
configurations. Test speculative decoding as a separate short-context,
single-slot experiment because its documented cache/concurrency behavior
changes the workload. Do not infer production suitability from model size or a
single throughput measurement.

## Recommended acceptance statements

Use narrow claims:

- “Configuration X passed the UAH boot contract for role R on environment E.”
- “Configuration X improved the quality-cost frontier on frozen suite S.”
- “AB projection reduced scope violations under this model-harness-environment
  matrix.”
- “The Workbench proposal passed replay, counterexample, holdout, review, and
  rollback gates.”

Avoid:

- “Model X is an AB2/AB4 model.”
- “Boot eval proves general agent capability.”
- “Runtime discovery proves authorization.”
- “More context, lower memory, or faster decode proves agentic quality.”
- “Trace retrieval or prompt updates constitute safe continual learning.”

## Research limits

- The cited benchmarks cover important but partial task distributions; none
  proves cross-domain universality.
- Public benchmark contamination and evaluator defects can invalidate apparent
  progress.
- Vendor memory and speed figures require reproduction on the intended hardware
  and exact runtime commit.
- Continual-learning algorithms do not directly validate symbolic registry
  promotion or retrieval-only adaptation.
- No primary source reviewed here validates the AB coordinate system,
  Neural Workbench energy/entropy terms, or an AB2 crystallization gate. Those
  remain project-specific hypotheses.

