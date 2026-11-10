# SM-001: interrupted hook publication

**Date:** 2026-11-10. **Sprint:** SPR-11. **Owner:** repository tooling.
**State:** reproduced research finding; no repair or release closure.
**Source:** main `d9eb84a`, unchanged setup/guard/cache bytes on coordination
commit `71a448fa25dd607818d03c29f4b398eeb6a41adb`.
**Affected gate:** developer validation tooling; no H0/H1/O1/H2 qualification.

## Contract and public behavior

REVIEW.md section 6 states: “Installing a hook must not disable hooks already
in place.” The public interface is `./scripts/setup_dev_tools.sh`, followed
by ordinary `git push` and rerunning that same setup command. The script moves
the installed pre-push hook to `pre-push.pre-commit` before publishing the UAH
guard with `install`. An external install-only failure injected at that point
leaves no active `pre-push` hook. This is a tested command-failure cut point,
not a claim that every power-loss or concurrent setup schedule is covered.

## Frozen four-case results

| Case | Expected contract or question | Observed result |
| --- | --- | --- |
| Intact independent setup, then rerun | Preserve executable guard/delegate/legacy chain; reject unchecked push and allow checked push. | Both setup calls exit 0; no-cache local push exits 1; checked local push exits 0 and calls the legacy marker. |
| Failure after delegate move, before guard publication | Existing hook enforcement should remain available through installation failure. Measure recovery without assuming it. | Injected `install` exits 73. Active `pre-push` is absent; delegate and legacy bytes remain executable. Unchecked push to a disposable local bare remote succeeds, without the legacy marker. Ordinary setup rerun exits 1, refusing the existing delegate. |
| Shared Git common directory | Distinguish prohibited caller setup from automatic script enforcement. | Setup exits 0 and rewrites common hooks. This deliberately violates caller policy in a disposable fixture; it is not a compliant private setup or a new authority bypass claim. |
| Per-worktree hooksPath candidate | Determine whether real pre-commit supports this isolation configuration. | Real pre-commit refuses installation (exit 1); common and local hook bytes stay unchanged. Successful hook-local installation is `not_scored`. |

The probe copies exact setup/guard/cache sources, controls package installation
as the existing fixture does, and uses real pre-commit 4.7.0 with local-only
hooks. All Git commits, worktree creation and pushes occur in disposable test
repositories. No GitHub push, network package install, active-user hook edit,
provider call or production script edit occurs. Existing cache tests:12 passed
in 14.70 seconds. Those tests passing does not cover this new failure schedule.

## Mechanism and next owner scope

The move and publication are separate filesystem operations. Preserved delegate
bytes do not enforce pushes when Git has no active hook entry point. Rerun's
existing-delegate refusal protects bytes but does not recover this partial
installation. This single cut point supports a preservation/recovery defect;
it does not establish a general concurrency, crash-durability or platform result.

A future bounded DEV scope can test local setup publication and partial-state
recovery while preserving the intact chain and original legacy hook. Keep the
behavior local to the existing script; a new installer module fails the deletion
test. No interface or repair is selected here. Whether to add script-enforced
shared-metadata refusal is a separate human policy decision. Private setup continues to require an independent Git common directory or
proven hook-local isolation, as AGENTS.md already specifies.

PR2 human merge, a fresh actual-main freeze, finite DEV dispatch, public red
and valid control, full hooks, fresh independent review and collision-safe
unstaged handoff remain implementation gates. Human sprint/product staging,
commits, pushes and releases remain unchanged.

## Exact private evidence

Evidence root: `/home/juanbeck/uah-experiments/orca-state-machines-20261110/hook-probe/`.
Executed `probe.py --output <fresh-private-path>` retains command output and
fixture hook hashes. `report.md`, `results.json`, `probe.py` and
`artifact-hashes.json` are private; raw fixtures/logs are not product inputs.
Research report SHA-256:
`8918532cc2acbcbdf6fe43bed1bfa827e2f4e2f5a77fc189a88328ef223d5e6f`.
Probe SHA-256:
`dcb47abe3659907f3a89cd87730b109ff92bcd8ea92d164c90beec8a825a5f64`.
This note records observed behavior and proposed routing; it grants no runtime,
Git, review or release authority.
