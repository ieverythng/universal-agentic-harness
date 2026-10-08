# UAH independent review and trace iteration

**Status:** Local review workflow; UAH-hosted reviewers are not implemented  
**Date:** 2026-10-05  
**Review contract:** [REVIEW.md](../../REVIEW.md)

The [2026-10-05 review](../artifacts/reviews/2026-10-05_uah_h0_h1_independent_review.md)
records the initial independent findings and executable counterexamples.

## Ownership and evidence

`REVIEW.md` is copied unchanged from iTrader. It owns reviewer independence,
predeclared probes, design-principle reporting, and the final verdict format.
The UAH guardrails and accepted architecture govern semantic authority. Similar
hashing syntax across artifacts is not duplicated policy and does not justify
a shared codec. Runtime proposals, environment effects, and review conclusions
retain separate owners.

The H0 contract spine and the bounded H1/O1 implementations are under review.
An approved implementation review does not close H0, H1, O1, or H2 unless the
corresponding exit evidence is present. Passing fake-provider tests does not
qualify a live endpoint or model performance. Observatory consumes the common
ledger through read-only projections; it does not approve operations or fixes.

## Freeze one review round

Record the base and head commit IDs, current branch, commit list, complete dirty
file list (including untracked files), content hashes, governing docs, and exact
validation commands. Do not create a commit or change branches for convenience.
Record deleted paths separately. Report changes made during the review and
invalidate findings affected by such changes before issuing a final verdict.

Use three independently declared scopes:

1. Standards: repository guidance, interface locality, tests, tooling, and churn.
2. Spec: typed admission, authority, identity, execution, evidence, and replay.
3. Architecture and Observatory: source/doc consistency, truthful projections,
   and deepening candidates supported by caller friction.

Use fresh reviewers with no writer conversation history. Pass repository,
scope, and review contract, not an explanation intended to justify the code.
High-risk gates receive a second reviewer on a different model. Record actual
model settings and any fallback. No issue tracker is configured for this
workflow; findings stay in dated repository artifacts until the user chooses
an external destination.

## Execute and track findings

Reviewers declare adversarial inputs before reading the implementation. They
exercise public interfaces with synthetic domains and temporary ledgers, then
compare with the base. When a seam did not exist at the base, record it as
unavailable rather than inventing a parity result. Never mutate real domain
state or call a live provider as an incidental review step.

Keep Standards and Spec reports separate. Give confirmed findings stable IDs,
`BLOCKING` or `NIT`, affected release and owner, exact source lines, governing
rule, input, expected outcome, actual outcome, and a reproducible command.
Distinguish a reproduced defect from a coverage gap or architectural judgment.
Record all five design principles and preserve each independent verdict.

## Trace review, repair, and retest

When a repair is authorized, freeze one discriminating failure and a known-good
control. Start with the narrow agreed public seam: task compilation, admission,
lease-only execution, ledger replay, model invocation, or Observatory rendering.
Use TDD for one correction at a time. Patch the owning module, rerun the failing
probe and protected control, and compare the recorded trace and digest where
the behavior permits it. Do not make expected output follow the new code merely
to obtain a green test.

Widen to affected suites, full source tests, both Observatory example freshness
checks, `./scripts/run_precommit.sh`, and `git diff --check`. Update canonical
Markdown when behavior or status changes and regenerate its listed HTML pair.
Return every fix to a fresh focused reviewer. Keep original finding IDs and
record the revision or dirty-file hashes reviewed for closure. The writer's
self-check never replaces independent review. Commit and push only on request.

For later model-performance investigations, freeze the role, model, prompt pack,
registry, environment, task suite, resource limits, and provider configuration.
Compare same-loadout controls and label measured versus synthetic evidence.
A better outcome does not excuse broken admission, lineage, or effect ownership.

## Deferred automation

The current H1 provider port does not implement a software-review worker or a
reviewer-spawning interface. A future UAH-hosted reviewer would need a reviewed
read-only role, bounded tool projection, isolated context, provider allocation,
and its own invocation and trace evidence. Its verdict remains advisory to the
human owner and cannot mutate the ledger or promote a Workbench candidate.

Run a bounded SkillOpt-style iteration (baseline -> mutate -> holdout gate -> accept/reject log) before finalizing major wording changes.
