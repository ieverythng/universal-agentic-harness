# Research note: Jev and System One decision models in UAH

**Date:** 2026-09-22  
**Status:** Research input, not a canonical plan or implementation claim  
**Scope:** TypeSafe Jev and RLCD, local substitutes, schema-scaling behavior,
Neural Workbench search, skill routing, domain onboarding, and a bounded UAH
experiment.

## Executive decision

Jev is a strong conceptual fit for UAH, but only as an untrusted decision and
ranking component. It should not become an admission gate, environment owner,
evidence source, or registry authority.

The most useful integration pattern is:

```text
deterministic task and policy projection
  -> closed set of legal candidates
  -> System One ranking and uncertainty estimates
  -> deterministic validation and risk policy
  -> existing UAH proposal, admission, lease, execution, and evidence lifecycle
```

This pattern is relevant to H3 Neural Workbench candidate selection, trace
reranking, skill routing, and candidate-only domain onboarding. It does not
replace candidate generation. Jev does not generate text, schemas, code, pulse
graphs, operation arguments, or unseen labels.

The recommended next step is an isolated shadow experiment after the current
H0-H1 closure work, with two interchangeable lanes:

1. the hosted, pinned `jev-1.13.0` API, if access is granted;
2. local decision-model baselines, beginning with GLiClass Edge and the
   independent Open Jev reproduction.

No TypeSafe SDK should enter `src/ab_harness`. Any later production adapter must
live outside the portable semantic core and satisfy a provider-neutral decision
port.

## 1. What Jev is

TypeSafe describes Jev as its first System One model. A request contains one
shared `state` and a map of typed questions. The response contains typed answers
and probability distributions rather than generated prose
([introduction](https://docs.typesafe.ai/introduction),
[System One](https://docs.typesafe.ai/concepts/system-one)).

The public interface exposes three primitives:

| Primitive | Meaning | Returned value |
| --- | --- | --- |
| `Choice` | Select one item from a closed set of at most 255 options | selected option, full distribution, derived confidence |
| `Score` | Place the state on an ordered rubric of 2 to 10 levels | probability-weighted score, level distribution, derived confidence |
| `Noul` | Estimate whether one proposition is true | probability of yes |

The exact request and response contracts are documented in the
[API reference](https://docs.typesafe.ai/api). `Choice` and `Score` confidence
is a statistic derived from the returned distribution. TypeSafe does not
publish its formula. `Noul` has no separate confidence field
([confidence documentation](https://docs.typesafe.ai/confidence)).

The current stable model is `jev-1.13.0`. The `jev-latest` alias currently
resolves to that revision, but aliases can move. UAH qualification would need to
pin the versioned identifier and record the resolved response model
([models](https://docs.typesafe.ai/models)).

## 2. Public availability and service contract

The documented endpoint is:

```text
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer <API_KEY>
```

An API key is required. TypeSafe publishes Python and JavaScript SDKs, while
the launch announcement still describes access as early access
([quick start](https://docs.typesafe.ai/introduction/quickstart),
[launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)).
The public console is reachable, but immediate entitlement for a new account
has not been verified in this research pass.

The current published service envelope is:

| Property | Published value |
| --- | --- |
| Input price | $0.042 per million tokens |
| Output price | free |
| Request context | 64,000 tokens total |
| State plus longest question | 32,000 tokens |
| Choice cardinality | at most 255 options |
| Input modality | text, represented as a string, object, or array |
| Rate limits | 250,000 tokens/s and 1,200 requests/min |
| Vendor-reported end-to-end latency | 70 to 500 ms |

TypeSafe states that rate limits can change while the service scales. The
latency range and the larger speed and cost comparisons are vendor-reported,
not UAH measurements
([models](https://docs.typesafe.ai/models),
[launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)).

TypeSafe states that customer requests and responses are not used for model
training. Zero-data-retention service is described as an enterprise option.
This does not remove the need for a UAH data-classification and redaction policy
before traces, repository content, credentials, or private environment state
are sent to the hosted service
([legal documentation](https://docs.typesafe.ai/legal)).

## 3. What is and is not known about RLCD

RLCD expands to Reinforcement Learning for Calibrated Decisions. TypeSafe
describes it as post-training a pretrained language model to return decisions
and probabilities whose frequencies reflect observed correctness. Calibration
is a population property. A single answer assigned probability 0.9 can still be
wrong
([AI primer](https://docs.typesafe.ai/introduction/machine-learning-primer)).

The reviewed first-party material does not disclose:

- the reward or loss function;
- the reinforcement-learning algorithm;
- the base checkpoint or parameter count;
- the training and calibration datasets;
- held-out ECE, Brier, log-loss, or reliability results;
- architecture, numerical precision, serving topology, or accelerator type;
- ablations separating architecture, sampling, data, and RLCD.

RLCD is therefore an interesting research direction and product claim, not yet
a reproducible training method for this project. UAH should test the returned
probabilities on its own distributions instead of treating the training label
as evidence of calibration.

## 4. Claims that require narrower interpretation

TypeSafe says Jev cannot hallucinate. The defensible interpretation is
structural: a closed `Choice` cannot return a value outside its declared option
set, and the service owns the response shape. It does not follow that the chosen
option is semantically correct. TypeSafe's own documentation records literal
misreadings, sensitivity to irrelevant context, adversarial-state effects, and
inconsistency between separately phrased questions
([Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13)).

The launch post reports workflow gains as large as 193.6 times faster and 444.6
times cheaper. TypeSafe also states that these results are probably near the
high end of real-world gains, that its model-capabilities team authored the
workflows, and that the reference answers are averages from large external
models rather than independent ground truth. These results motivate an
experiment but do not establish UAH performance
([launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)).

The documented Jev 1.13 failure modes are directly relevant to UAH:

- counting, arithmetic, dates, and structural invariants belong in code;
- long irrelevant state reduces accuracy;
- multiple layers of indirection reduce accuracy;
- adversarial text in state can steer an answer;
- separately asked questions do not obey expected probability identities;
- generation should be delegated to another model or deterministic code.

These limitations support UAH's bounded projections and deterministic gates.
They rule out using Jev as a universal verifier.

## 5. Why the UAH architecture is a good fit

UAH already separates model proposals from execution authority:

```text
model or worker adapter
  -> typed proposal
  -> deterministic semantic admission
  -> environment-owned execution
  -> owner-issued effect evidence
```

Jev can improve the first arrow when the answer space is already known. It
cannot replace any later arrow. Runtime discovery is still not authorization,
and a calibrated preference over candidates is still not effect evidence.

The existing `WorkbenchRequest` already supplies a closed frame, registry
revision, projected object identifiers, current candidates, constraints, and a
search budget. A decision model can rank a Workbench candidate portfolio
without changing `WorkbenchEnginePort` in an initial in-process experiment.
The engine would retain candidate provenance and add the decision result to its
score vector. `WorkbenchCandidateBatch` would remain a candidate-only artifact.

This avoids introducing a TypeSafe-specific concept into the AB ontology. A
System One model is a model adapter or learned selector, not an abstraction
frame, AB level, admitted operation, or environment owner.

## 6. Facet-by-facet incorporation map

| Project facet | Useful System One role | Required boundary |
| --- | --- | --- |
| H0-H1 semantic core | None in the runtime path | Finish deterministic contracts and lifecycle without a model dependency |
| H2 NAO qualification | Shadow-rank already legal planner operations or recorded proposals | No dispatch or gate authority; compare against the same fixture and owner evidence |
| H3 candidate portfolio | Rank verified pulse candidates and estimate candidate-specific dimensions | Hard constraints and graph validity run before learned ranking |
| H3 trace retrieval | Rerank a deterministic or embedding shortlist for support, transferability, or counterexample value | Never send the full unbounded trace store; preserve both support and opposition |
| H3 uncertainty | Supply raw distributions for a candidate prior or search policy | Recalibrate on UAH data; do not equate provider confidence with task correctness |
| H3 recovery | Choose among predeclared recovery branches | Branch set remains inside the active control band and owner policy |
| H4 crystallization | Prioritize fragments, counterfactuals, and review cases | Cannot publish, promote, or satisfy a promotion gate |
| Skill routing | Rank task-relevant skills and reject the shortlist when none fits | The selected skill remains a proposal and passes ordinary scope and permission checks |
| Provider or model routing | Choose among instances that already passed deterministic eligibility and capacity checks | Cannot override privacy, placement, resource, or role-admission policy |
| Domain onboarding | Classify and rank candidate frames, object kinds, owners, mappings, and review risks | Generation or extraction proposes new values; owner review activates nothing automatically |
| Failure analysis | Propose an observed failure class and review priority | Trace labels do not prove root cause; controlled replay remains necessary |
| Observatory | Display distributions, thresholds, abstentions, and model provenance | Read-only presentation has no admission or execution authority |

### 6.1 Neural Workbench search

Jev is better suited to selection than generation. A candidate portfolio should
still be created by distinct mechanisms:

```text
deterministic templates
+ model-generated candidates
+ retrieved and adapted traces
+ local graph mutations
+ reviewed recovery variants
```

After deterministic verification, one batched decision request can ask:

- a `Choice` over the remaining candidate identifiers;
- a `Noul` for whether each candidate is grounded by the supplied state;
- a `Noul` for whether each candidate needs escalation or more evidence;
- a `Score` on a concrete ordinal risk or reversibility rubric.

UAH should retain the full distributions as features in the score vector. A
deployment-specific policy can combine them with observed latency, cost,
capability posteriors, and the existing symbolic energy terms. The model's top
choice should not directly replace the Pareto and hard-constraint stages.

### 6.2 Trace-space search and entropy

A large trace store should use two stages:

```text
deterministic metadata and object overlap, or a local embedding index
  -> bounded support and counterexample shortlist
  -> System One relevance and transferability judgments
  -> beam or top-k search over typed candidate edges
```

For one `Choice` distribution `p`, the Workbench may compute
`-sum(p_i * log(p_i))` locally. This is entropy of the model's selection policy
for that question. It is not automatically world-state uncertainty or a
calibrated probability of task success. UAH's existing entropy proxy must
remain separately named until correlation with terminal acceptance is shown.

TypeSafe publishes a hierarchical-classification cookbook that applies parallel
beam search to `Choice` probabilities. Its four examples favored width-three
beam search over greedy traversal, but four examples are illustrative rather
than statistical evidence
([hierarchical classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification)).
The algorithmic pattern is relevant to AB graphs and large skill catalogs even
though its reported accuracy cannot be transferred to UAH.

### 6.3 Skill selection

TypeSafe's skill-suggestion cookbook is unusually close to the UAH use case. It
ranks 182 Hermes skills in one wide `Choice`, retains three, then re-reads the
shortlist with full descriptions and asks both a relative `Choice` and absolute
`Noul` fit questions. On 488 TypeSafe-authored requests, the reported wrong
skill-load rate fell from 16.8% to 7.3%, while needless loading on no-fit turns
fell from 9.8% to 4.0%
([skill-suggestion cookbook](https://docs.typesafe.ai/cookbooks/skill_suggestion)).

Those examples were generated from the skills and are easier than ordinary user
requests, so the numbers should not be treated as a general benchmark. The
two-stage design is still a strong starting point:

1. apply deterministic role, frame, task, permission, and availability filters;
2. rank the remaining skill summaries;
3. inspect the top few full contracts;
4. ask absolute fit questions so all candidates may be rejected;
5. pass the selected identifier through the normal UAH proposal and gate path.

### 6.4 Domain onboarding

The `uah-domain-onboarding` workflow needs generative and deterministic stages.
Jev can participate only after a candidate set exists.

Good uses include:

- classify an inspected surface as an API, event, topic, skill, effect
  primitive, evidence adapter, or unresolved item;
- rank plausible owner packages from a discovered roster;
- choose among candidate existing schema mappings;
- score review risk on a concrete rubric;
- identify which source excerpt is most relevant to one candidate contract;
- route a rejected candidate to a bounded repair operation.

Bad uses include:

- inventing an AB frame or object identifier from nothing;
- writing a new input or output schema;
- asserting that a binding is safe or authorized;
- creating effect evidence;
- activating a `DomainContractPack`.

The resulting pipeline is:

```text
source inspection and extraction
  -> generated or enumerated candidate values
  -> System One classification and ranking
  -> deterministic schema, graph, and ownership validation
  -> replay and counterexamples
  -> human and domain-owner review
```

## 7. Schema size and hardware scaling

### 7.1 Hosted Jev

No Jev weights, parameter count, architecture description, precision, model
card repository, or self-hosting path was found in the reviewed first-party
material. Local Jev RAM, VRAM, and compute pressure therefore cannot be
estimated responsibly.

For the hosted service, schema growth has three observable effects:

1. option and question descriptions add input tokens, so cost grows with their
   encoded length;
2. every request remains subject to the 64k total and 32k state-plus-longest-
   question limits;
3. `Choice` stops at 255 options.

TypeSafe states that questions are evaluated in parallel and that adding them
barely changes response time. A first-party 13-question example reported 0.27 s
batched versus 2.71 s across sequential requests
([parallel-questions cookbook](https://docs.typesafe.ai/cookbooks/parallel_questions)).
High-cardinality choice is not free. TypeSafe says choices above the native
cardinality used by its Wikiracing demonstration require a two-stage scoring
and explicit-choice procedure and can slow down
([launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)).
UAH should measure latency at its own state length, option count, question
count, and concurrency rather than extrapolating from these examples.

### 7.2 Local dynamic-label classifiers

GLiClass is an Apache-2.0 zero-shot classification family that accepts dynamic
labels and processes them in one forward pass. Its published V3 variants are:

| Variant | Parameters | Published weight size | A6000 average examples/s |
| --- | ---: | ---: | ---: |
| Edge | 32.7M | 131 MB | 97.29 |
| Modern Base | 151M | 606 MB | 54.46 |
| Base | 187M | 746 MB | 51.61 |
| Large | 439M | 1.75 GB | 25.22 |

The vendor tested 64, 256, and 512-token inputs with 1 through 128 labels. Edge
declined from 103.81 to 82.64 examples/s, Base from 49.42 to 45.94, and Large
from 19.05 to 17.60. The compared cross-encoder classifiers lost throughput
approximately in proportion to label count. These are A6000 measurements and
do not establish CPU performance
([GLiClass repository](https://github.com/Knowledgator/GLiClass),
[V3 model card](https://huggingface.co/knowledgator/gliclass-edge-v3.0),
[paper](https://arxiv.org/abs/2508.07662)).

This makes GLiClass the most practical first local ranker when the candidate set
changes per request. Its output scores are not established as Jev-equivalent
calibrated probabilities. Calibration must be fitted and measured on a frozen
UAH holdout.

### 7.3 Independent Open Jev reproduction

`com-kotobalabs/open-jev-deberta-v3-large` is an independent Apache-2.0 model,
not TypeSafe Jev. It reproduces the Jev-shaped state plus typed-question
interface in one encoder pass. The checkpoint contains about 0.4B parameters
and a 1.76 GB F32 bundle. Its model card reports a 512-token total context with
state truncated to 256 tokens, 1.8 s for four questions on an M1 Max CPU, and
28 ms for ten questions on an H100 in BF16
([model card](https://huggingface.co/com-kotobalabs/open-jev-deberta-v3-large)).

The reported in-domain accuracy is 0.854 and the reported new-question/new-
option-set accuracy is 0.690. The model card explicitly warns that it partially
reads questions, is English-only, covers three source domains, and is
overconfident out of distribution. Its short context is a serious constraint
for trace and domain-contract tasks. It is nevertheless the best contract-
fidelity local experiment found in this pass because it natively exposes
`Choice`, `Score`, and `Noul` distributions.

### 7.4 Other controls

| Candidate | Best role | Scaling limitation |
| --- | --- | --- |
| ModernBERT or DeBERTa NLI zero-shot model | Simple dynamic-label accuracy baseline | Typically evaluates state-label pairs, so work grows approximately with label count |
| SetFit | Stable, domain-specific skill or operation taxonomy after labeled traces accumulate | Classification head must be retrained when the schema changes materially |
| TypeSafe System One adapter plus a local LLM | Contract-level comparison against an existing local OpenAI-compatible server | Still autoregressive; generated probabilities are not calibrated by construction |
| Small constrained-output LLM | Candidate generation plus valid JSON | Grammar guarantees shape, not truth, and output cost remains autoregressive |

TypeSafe publishes an MIT-licensed
[System One adapter](https://github.com/typesafe-ai/system-one-adapter-python)
that implements the same high-level primitives over OpenAI-compatible or
Anthropic model endpoints. It provides a useful control, not a local RLCD
implementation.

### 7.5 This workstation

The current development machine reports:

```text
CPU: AMD Ryzen 5 5600H, 6 cores / 12 threads, AVX2
RAM: 7.2 GiB total, about 1.1 GiB available during inspection
GPU: no NVIDIA device visible to nvidia-smi
```

GLiClass Edge should be the first local smoke candidate because its published
F32 weight artifact is 131 MB. GLiClass Base is plausible after freeing memory,
but runtime allocations and Python/PyTorch overhead must be measured. The 1.76
GB F32 Open Jev bundle is likely to force material memory pressure in the
current desktop workload. A quantized ONNX build may fit more comfortably, but
its accuracy and latency require a separate configuration identity and test.
These are capacity estimates, not measured UAH results.

## 8. Proposed provider-neutral seam

Do not add `Choice`, `Score`, and `Noul` as TypeSafe-owned runtime semantics.
Define a small provider-neutral decision contract when H3 is ready:

```text
DecisionBatchRequest
  request_id
  configuration_id
  state artifact or bounded state payload
  questions: ChoiceQuestion | OrdinalQuestion | BinaryQuestion
  timeout and token budget

DecisionBatchResult
  resolved model and adapter revision
  answer distributions
  latency and usage
  request and response hashes
  status: candidate
```

Every option should use a stable identifier plus a description. The adapter
must validate that returned question identifiers, answer types, and probability
keys match the request exactly. Non-finite values, missing options, unknown
options, and invalid distributions fail closed.

Provider implementations would remain outside `src/ab_harness`:

```text
ab_harness core
  owns provider-neutral request/result contracts and trace identity

Neural Workbench
  owns candidate construction, score-vector use, search, and adaptation

provider adapter
  owns TypeSafe HTTP/SDK or local model invocation
```

The first experiment does not require a new public core contract. A private
adapter inside an experimental Workbench engine can validate the design before
the protocol is frozen.

## 9. Experiment design

### 9.1 Arms

Compare the following under identical candidate sets and frozen labels:

1. current deterministic overlap and symbolic-energy baseline;
2. hosted `jev-1.13.0`;
3. GLiClass Edge;
4. GLiClass Base, if memory permits;
5. independent Open Jev, preferably F32 and one quantized ONNX configuration;
6. a ModernBERT-base NLI cross-encoder control;
7. the System One adapter over one already-supported local small LLM.

Each model, quantization, runtime, prompt/question pack, registry revision, and
threshold profile is a separate `ConfigurationIdentity`.

### 9.2 Task slices

Use replayed and synthetic cases that expose the relevant seams:

- select a legal planner operation from a task projection;
- reject a turn for which no projected skill fits;
- rank 3, 8, 16, 32, 64, 128, and, where supported, 255 candidates;
- rerank supporting and counterexample trace shortlists;
- choose between recovery, clarification, inspection, and escalation;
- classify candidate domain surfaces and owner mappings;
- rank Workbench pulse candidates after deterministic verification;
- traverse a hierarchical skill or AB-object catalog with greedy and beam
  search;
- preserve behavior under option reordering and paraphrased descriptions;
- resist irrelevant context and adversarial instructions embedded in state.

The current NAO fixture contains only ten registry objects. It is useful for
contract correctness but too small to establish the value of learned routing.
The scaling suite needs controlled expanded catalogs and labeled no-fit cases.

### 9.3 Metrics

Measure:

- top-1 accuracy and top-k recall;
- valid-candidate recall before and after any shortlist stage;
- Brier score, negative log loss, ECE, and reliability diagrams;
- selective accuracy and risk as coverage changes;
- no-fit precision and recall;
- schema-valid response rate;
- p50 and p95 cold and warm latency;
- input tokens and hosted cost;
- peak resident RAM and VRAM;
- throughput under intended concurrency;
- sensitivity to option count, description length, and state length;
- regression by task family, operation risk, and failure mode.

For path search, report both terminal path accuracy and per-edge calibration.
For crystallization support, report forward gain and backward regression on
previously promoted behavior separately.

### 9.4 Failure and fallback policy

Shadow mode records provider failure and continues with the existing baseline.
A later gated mode must declare its failure behavior explicitly:

- malformed response: reject the decision result;
- timeout, `429`, or `529`: bounded retry according to policy, then the named
  deterministic baseline or escalation;
- low confidence or flat distribution: retain more candidates, inspect more
  evidence, ask for clarification, or escalate;
- state or schema beyond the qualified envelope: do not call the model;
- model revision drift: invalidate the prior threshold calibration.

There must be no silent provider substitution in qualification results.

## 10. Promotion criteria

The decision-model seam should progress from experiment to H3 shadow use only
if it:

- improves top-k candidate quality over deterministic retrieval;
- preserves scope, permission, and evidence completeness;
- demonstrates calibrated or conservatively recalibrated probabilities on an
  untouched UAH holdout;
- rejects no-fit cases at an acceptable selective-risk threshold;
- remains inside declared latency and resource budgets;
- exposes complete configuration and decision provenance;
- degrades safely when the provider or local runtime is unavailable;
- passes adversarial-state, irrelevant-context, and schema-order tests.

It should become authoritative in candidate ranking only after shadow replay
shows no unacceptable regression. It should never become authoritative for
semantic admission, permission, owner execution, effect evidence, task
acceptance, or H4 promotion.

## 11. Recommended implementation sequence

1. Preserve the current H0-H1 implementation queue. Do not add a provider
   dependency to the core.
2. Create an experimental decision-batch fixture format under H3 research.
3. Build the deterministic baseline and metrics before acquiring an API key.
4. Run GLiClass Edge locally on the routing and candidate-ranking slices.
5. Run the independent Open Jev model on short-state contract-fidelity cases.
6. Request TypeSafe access and add pinned `jev-1.13.0` as another adapter, not
   a privileged reference answer.
7. Compare flat choice, shortlist-and-rerank, and hierarchical beam search.
8. If the result survives holdout and robustness tests, freeze a
   provider-neutral H3 decision port and add it to the Workbench protocol.
9. Reuse the same seam in candidate-only domain onboarding and skill routing.
10. Consider SetFit or another small supervised classifier only after stable
    schemas and enough owner-labeled traces exist.

## 12. Bottom line

Jev's interface matches a central UAH hypothesis: many agent decisions should
be closed, typed, probabilistic proposals embedded in deterministic software.
The highest-value near-term use is a cheap learned selector over legal
Workbench candidates, skills, traces, and onboarding mappings.

The public evidence does not support stronger claims. Jev is not locally
available, its hardware requirements and RLCD mechanics are undisclosed, and
its probabilities require domain-specific validation. Open substitutes make
the experiment possible now. GLiClass Edge is the practical local starting
point on this machine, while the independent Open Jev model is the closest
available contract-level reproduction. Both must remain behind UAH's existing
quarantine, replay, holdout, owner-review, provenance, and rollback gates.
