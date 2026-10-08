# Root checks for the frozen ingress candidate

Date: 2026-10-08. Source freeze 18:47:51 UTC. Current input:
`/tmp/uah-ingress-candidate-frozen`; actual dirty before input:
`/tmp/uah-ingress-before-checkout`. Root reconstructed the before tree from HEAD,
the complete pre-edit binary diff and exact affected before bytes. Scope hashes
are in `round_frozen.sha256`; original HEAD is `06f5a29`.

## Comparable checks

`PYTHONPATH=<candidate>/src` and `GIT_WORK_TREE=<candidate>` select the candidate,
with `GIT_DIR` pointing at the repository metadata for the cache-helper tests.
The existing repository Python environment supplies dependencies. No provider
or native environment is invoked.

- Full frozen candidate `python -m pytest -q`: **548 passed**, 13.45 seconds.
  Both O1 HTML examples were regenerated for command-provenance event IDs.
- Frozen candidate `./scripts/run_precommit.sh`: **failed**. The whitespace hook
  trims four blank lines in the two generated O1 examples; subsequent source
  tests report **546 passed, 2 failed** (exact generated-example equality).
  Ruff and canonical documentation checks pass. The formatter changes were
  confined to the disposable candidate checkout, not copied into source.
- Before this repair both public O1 `--check` commands already reported stale
  examples. That baseline does not waive the final hygiene gate. New marker
  identities also require new examples; regeneration alone cannot make their
  formatting stable across the hooks.
- Shared frozen source/doc hashes still match `round_frozen.sha256` after the
  disposable hook run. Shared `git diff --check` reports the same four generated
  whitespace lines. No historical evidence manifest is rewritten.

The pre-hook 548-pass result is not a successful final hook result or release
sign-off. Fixture/rendering hygiene requires a separately scoped correction.
Fresh independent reviews remain separate from these writer/root controls.

## Review-snapshot restoration

The root hook run mistakenly used the frozen review checkout itself, rather
than a second disposable copy. Its whitespace hook changed the two frozen O1
HTML files. Both reviewers were notified when their subsequent integrity
checks identified that drift. The other fifteen scoped hashes remained intact.
This was a root validation error, not unexplained concurrent author drift.

The altered bytes were retained in `/tmp/uah-ingress-hook-altered-artifacts/`:
canary SHA256 `904fbb15820df865895f482fa8dbfe5d7914e5c3d9026ade13efad0972d0640f`,
H1 SHA256 `456cfcee2251dbd6f01815a6165b676632cd3426c4fdbf5bd17d207fa1887f31`.
Root regenerated the original artifacts using only the unchanged frozen
renderer and frozen source. All seventeen original manifest entries then
passed. The original manifest was not edited. Review applicability requires
each reviewer to recheck that restored exact-byte target before verdict.
No further hooks run on that review checkout.

The separate human-authorized commit candidate fixes the formatting issue by
removing literal indentation before an optional template interpolation, not by
normalizing raw payload whitespace. Its new regression and two regenerated
examples are outside the restored ingress review snapshot.

## Separate human-selected commit request

The human subsequently requested a commit of nine selected research, renderer,
agent and domain-pack paths with corresponding tests. A delegated exact-index
export found missing unchecked lifecycle actor APIs, model allocator and
Observatory modules. Narrow candidate controls yielded 95 passes and 29
failures; runtime-example collection also failed. Canonical docs passed.
The subagent retained diagnosis at `/tmp/uah-selected-commit-eEh1hf/receipt.md`.
It performed no primary index mutation, source fix, commit or push. This blocked
commit attempt neither changes the ingress scope nor supplies runtime approval.
