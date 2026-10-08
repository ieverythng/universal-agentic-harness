---
name: uah-stack-iteration-loop
description: Run a bounded evidence-gated trace, public-test, owner-repair and replay loop for UAH contract, agent-runtime, provider or Observatory regressions. Use for cross-seam stabilization or decision-bearing closure, not local editorial cleanup.
---

# UAH Stack Iteration Loop

Turn an observed failure into a reviewed correction or an exact bounded handoff.
Diagnosis/review-only requests do not authorize repairs or live provider calls.
Apply [UAH guardrails](../uah-guardrails/SKILL.md) and read the owning current
contract. [REVIEW.md](../../../REVIEW.md) owns independent review policy;
[the review workflow](../../../docs/agents/uah_review_workflow.md) owns local
finding tracking. Research and historical traces are evidence, not accepted policy.

## Freeze the round

Record the release gate, owner, target behavior, non-goals, time/run/change budget,
base and HEAD, dirty/untracked/deleted paths and hashes, protected controls and
acceptance gate before editing. Record concurrent user commits or content changes;
refreeze affected evidence rather than overwriting or resetting their work.
For model/runtime comparisons also pin role/model/prompt, frame/registry/bindings,
environment activation, task suite, resources and provider settings without secrets.

Keep implementation conformance, provider connectivity, model quality, owner-proven
effects and H0/H1/H2 qualification as separate claims. Missing evidence is
`not_scored`; a successful diagnostic exit only proves the diagnostic ran.

## Establish the public red gate

Inspect the raw output, proposal, admission, lease, result/evidence and terminal
judgment as separate artifacts when present. Preserve environment/run/task/trace/
operation/invocation lineage and original finding IDs; do not infer absent actors.
Use [TDD](/home/juanbeck/.agents/skills/tdd/SKILL.md) at the narrowest public seam
and retain an untouched valid control. Check expected versus actual behavior,
errors and replay/digest outcomes, not merely status or test counts.

When several causes remain plausible, use the hypothesis protocol from
[seam-hypothesis-audit](/home/juanbeck/nao-ros4hri-bridge/.codex/skills/seam-hypothesis-audit/SKILL.md).
Transfer its investigation method, not ROS-only rules or AB definitions. Keep a
local table of mechanism, owner, assumptions, discriminating probe, observation,
status and exact gap. Distinct routes need distinct mechanisms; blocked routes
reopen only on materially new evidence. If that optional skill is unavailable,
record the gap and use this table without inventing an independent pass.

## Correct the owner, when authorized

Patch the smallest owning seam after the red test fails for the intended reason.
Models propose; semantic admission, domain leasing and effect owners retain their
authority. AB coordinates stay frame-relative. The common ledger remains the sole
public lifecycle writer/replay owner and Observatory remains read-only.
Do not add compatibility paths, generic codecs or file-size-driven extraction
without a demonstrated need. Return normative ownership or policy choices for
human decision rather than converting a hypothesis into a trusted contract.

## Run the comparable probe

Rerun the failure and protected control under the frozen loadout, then affected
suites, full source tests, applicable schema checks, both O1 example freshness
checks, canonical-doc synchronization, `./scripts/run_precommit.sh` and
`git diff --check`. Edit canonical Markdown and regenerate only its listed HTML.
Record exact commands, inputs, evidence references and unresolved gaps.

Choose the comparable path from the claim: recorded replay, synthetic environment,
fake provider, authorized live transport, or native adapter parity. A local
synthetic domain can test H0/H1 mechanics without NAO or provider setup. Live
connectivity cannot replace proposal/admission/lease/evidence/acceptance proof.
An unavailable endpoint is not a failed model benchmark or a reason to invent data.

For skill or prompt edits, lock target/objective/train/holdout/acceptance first and
use [SkillOpt](/home/juanbeck/.codex/skills/skillopt-skill-iteration/SKILL.md).
Run a bounded SkillOpt-style iteration (baseline -> mutate -> holdout gate -> accept/reject log) before finalizing major wording changes.

## Review, decide and stop

For authority, validation, runtime, evidence-browser or decision-bearing closure
changes, apply REVIEW.md after the writer's self-check, including fresh fix review.
This skill adds no reviewer exemption or alternative promotion gate.
Accept a correction only when its frozen gates and independent review agree;
implementation approval does not close a release without its exit evidence.

Stop at the frozen budget, an unresolved decision/dependency, or a new
discriminating failure outside the authorized batch. Return a dated artifact with
baseline, mechanism table, changes, exact results, reviewed revision/hashes,
verdict, residual risk and the next probe. Preserve prior findings as historical
evidence; log closure against the newly reviewed bytes. Never stage, commit or
push unless explicitly requested, and never continue or schedule another round
autonomously. Chat coordination labels are not runtime agent roles.

Adapted from [iTrader's iteration loop](/home/juanbeck/itrader-azr/.codex/skills/itrader-stack-iteration-loop/SKILL.md);
trading metrics and its official-stack invocation are intentionally excluded.
