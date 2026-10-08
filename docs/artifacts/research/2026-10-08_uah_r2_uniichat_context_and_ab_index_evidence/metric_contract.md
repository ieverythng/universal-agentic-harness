# Proposed context metric contract v0

Status: preregistration proposal, not implemented evaluator or observed results.
Scope: the four R2 cards. Corpus/labels/model identities remain unresolved.
Thresholds in cards are screening hypotheses, not release/promotion gates.

## Identity and scoring unit

A query is one frozen task/question with an exact eligible candidate set and
oracle labels. Source candidates have immutable IDs and raw-source digests.
The eligibility mask is applied before ranking and covers full source ancestry.
Raw facts and required counterexamples are labelled before model output.

All reported retrieval fractions are macro averages over the frozen queries,
with per-query values also retained. Never micro-average after observing which
method benefits. Compare arms on identical queries, candidate sets and budget.
Queries with an empty relevant set enter no-fit metrics, not recall denominators.
Unavailable source is a gap; it cannot be relabelled irrelevant.

A relevant set may contain multiple correct sources. Support and opposition
have distinct frozen label sets. Required evidence/counterexample coverage is
a zero-loss countersafety gate, independent of average relevance uplift.

## Retrieval and provenance

- Top-k: k=4 for System One; use min(4, eligible candidate count) when smaller.
  Top-k recall per nonempty query is |selected ∩ relevant| / |relevant|.
- Support/counterexample recall: the same formula on the corresponding frozen
  label set. Empty label sets are excluded and their count is reported.
- Required-reference recall: coverage of explicitly required raw references;
  a missing required reference fails countersafety despite macro gains.
- Exact-fact recovery: fraction of frozen query facts recovered with correct
  value, negation, attribution and raw citation under the deterministic oracle.
- False recall: returned answer facts unsupported or contradicted by the raw
  oracle / all returned answer facts. Empty answers are explicit abstention.
- Source resolution/citation accuracy: exact source digest and cited span match
  / all selected or cited references respectively. Missing references fail.
- Correction precedence: frozen corrected-fact queries whose answer respects
  the source/authority/time oracle / all corrected-fact queries.
- Cross-frame false match: selected references outside the declared exact frame
  or read scope / all selected references. Any nonzero value fails the arm.
- No-fit precision/recall: binary classification on truly empty-relevance queries.
  Report confusion counts; undefined denominators remain null, never zero.
- Unauthorized disclosure: count of any denied raw-source bytes or ancestry
  exposed. Any nonzero count stops the run.

## Probabilities and calibration

A ranker's Choice distribution is not automatically a probability that each
source is relevant. Calibration requires a separately frozen probability oracle.
For uniquely labelled diagnostic queries, use one class per eligible candidate
plus no-fit, with exactly one ground-truth class. Brier score is the sum across
classes of (p_j - y_j)^2, macro averaged over queries; log loss is
-log(max(p_true, 0.000001)), in nats.

Multiple-relevance ranking queries do not enter these categorical calibration
metrics. Their retrieval oracle remains set-valued. A separate binary
per-candidate relevance classifier could have its own calibration contract,
but that is not implied by a Choice answer distribution.

ECE uses 10 equal-mass bins on top-choice confidence versus uniquely labelled
top-choice correctness, recording bin boundaries and sample counts. Fewer than
100 unique diagnostic queries produces descriptive bins only. Repeated order
permutations are correlated controls, not new independent calibration samples.
The bounded 36-query screen therefore cannot qualify calibration. Reaching a
sample minimum alone would not qualify it either. Missing, nonfinite, negative or non-normalized
probabilities produce explicit invalid/unknown status and no score.

Abstention is no-fit only when the model chooses the frozen no-fit label.
Timeout/invalid output is a separate failure, never a correct no-fit decision.
A confidence statistic without documented probability semantics is not scored.

## Permutations, resources and latency

Each System One query uses original order and two frozen permutations; compare
chosen immutable candidate IDs after mapping back. Disagreement is disagreeing
paired selections / all valid permutation pairs. Preserve invalid-output counts.
At most 36 queries × 3 orders =108 classifier calls for one selected classifier
arm. Deterministic control uses the same corpus; multiple classifier arms require
a new bounded authorization and card revision.

Selected bytes are UTF-8 rendered context bytes excluding transport wrappers;
transport bytes and exact model-input tokens are separate fields. Input-token
counts are null until the production template/tokenizer is qualified.
Zoom count is total traversal tool calls per query; summary calls include retries.

Latency is client monotonic elapsed milliseconds for one completed selection or
classifier request, including network time but excluding separately reported
queue wait. p95 is the nearest-rank 95th percentile of successful requests;
report sample count, all failures and total wall time alongside it. This is a
small-screen descriptive statistic, not an SLO qualification.

RSS/VRAM are incremental peak MiB above a recorded pre-run baseline with the
measurement method named. Cloud serving VRAM is unknown unless provided by its
owner; local proxy memory is not cloud inference memory.
Cost in USD needs actual provider usage and tariff identity; no undocumented
free-tier assumption or inferred cache hit becomes zero cost.

## Split and acceptance discipline

Freeze exact fixture/oracle/partition bytes and SHA-256 before tuning. Each card
has its own reserved development/holdout seeds; whole task families and raw
summary ancestry must be disjoint. Upstream winner selection uses development
only. Downstream configuration is frozen before opening a fresh holdout.

Pick the primary hierarchy criterion (recovery uplift or byte reduction with
no loss) before running the screen. Do not switch criteria after holdout access.
Report paired query deltas and scope/counterexample failures. A 12-query holdout
can screen a hypothesis; it cannot establish broad deployment capability.
Independent repeat/owner review/promotion requires a separate qualified gate.
