# Independent second ingress review

Review received through GRILL from its fresh `ingress_independent_second` child
on 2026-10-08. Requested model: gpt-6-astra/max, fork without writer history.
The report below applies only to the restored original 17-path freeze.

1 of the 1 found so far. **NIT [P3]: Update the remaining current-state descriptions of raw task-start writes.** The change at [lifecycle.py:596](/tmp/uah-ingress-candidate-frozen/src/ab_harness/lifecycle.py:596) correctly rejects caller-created `TaskStartedFact` values, but [CONTEXT.md:281](/tmp/uah-ingress-candidate-frozen/CONTEXT.md:281) and [observatory_contract.md:249](/tmp/uah-ingress-candidate-frozen/docs/architecture/observatory_contract.md:249) still describe those writes as currently accepted.

Reproduction: construct a `TaskStartedFact` from a genuine decision and pass it to a new ledger's public `record()` method. Before accepts it and permits matching compilation; candidate raises `ValueError: new starts require an authority-bound task-start command`. Expected documentation should distinguish this implemented candidate behavior from pending review or release closure. Actual prose still describes the previous behavior. This is an optional documentation correction.

**No introduced blocking source defects found.**

Reviewed the original 17-path manifest against `/tmp/uah-ingress-before-checkout` and `/tmp/uah-ingress-candidate-frozen`, including the complete scoped diffs and relevant compiler, ingress, replay, adapter, and Observatory consumers. Input families were declared before implementation inspection; initial paired executions preceded source reading.

Execution evidence:

- Initial six-file targeted comparison: before **173 passed, 1 existing Observatory HTML failure**; candidate **190 passed**.
- Final full-suite comparison: before **530 passed, 2 existing Observatory HTML failures**; restored candidate **548 passed**. Commands used the original repository venv, each snapshot's cwd and `PYTHONPATH`, disabled bytecode writes and pytest's cache provider, and supplied the documented Git environment.
- **31 paired public probes** covered valid compilation, raw starts, altered lineage, missing/null/empty inputs, Unicode, duplicate identities, both entity orders, dates, and restart.
- Additional paired probes covered captured-command transfer/repetition and four exported-event representations. Candidate-specific tests rejected forged capabilities, altered decisions/ingress/environment runs, and a different ledger instance using the same path.
- Two-process contention tests covered identical ingress, distinct ingress for the same task, and independent tasks. Both versions retained correct rejection reasons and contiguous sequencing.
- A genuine **26-event before-generated ledger** replayed identically in the candidate across three traces, preserving event IDs, statuses, and the two available terminal digests. Duplicate, reversed, missing-middle, and truncated histories remained rejected in both versions.
- Scoped Ruff checks passed. Documentation renderer checks passed for both snapshots. All **17 original manifest hashes** passed after restoration and again after the final suite.

All five design principles:

| Principle | Assessment |
|---|---|
| Separation of concerns | **OK.** Ingress admission remains with `TaskIngressAuthority`; durable writes and replay remain with `LifecycleLedger`; the registry remains a read-only projection. |
| Programming by intention | **OK.** Command validation and fresh-compilation provenance checks express the trust boundary explicitly. |
| Encapsulation | **OK.** Raw facts and exported events cannot obtain command authority; capability and ledger-affinity checks reject the tested substitutions. |
| High cohesion | **OK.** Start-policy validation stays with ingress authority, while persistence and replay validation stay with the ledger. |
| Low coupling | **OK.** The change remains within portable core contracts and introduces no provider, ROS, or native-runtime dependency. |

The bounded **H0/H1 ingress correction** preserves historical replay while withholding fresh compilation authority from unmarked starts. Invalid-calendar and timezone-free ingress timestamps remain accepted in both snapshots; that is pre-existing debt. Numeric unit conversions and new numeric upper bounds are not exposed by this delta.

The freeze incident remains part of this review's evidence: all 17 hashes initially matched; at **18:56:40 UTC**, the two candidate Observatory HTML files failed their original hashes while the other 15 remained unchanged. DEV subsequently reported a formatting-hook mutation at 18:52 UTC. I independently confirmed restoration to the original manifest, equality with renderer output, and successful final testing. The intermediate results obtained during artifact drift do not establish the restored candidate's status. This verdict applies exclusively to the original, restored 17-path candidate; later live-worktree changes and integration checks remain outside it.

Requested second-review configuration was **gpt-6-astra/max**. Backend identity and effort were not independently attested. I made no shared-source edits, Git writes, or live-provider calls.

Full-suite logs are [before](/tmp/uah-independent-second-before-full.log) and [candidate](/tmp/uah-independent-second-candidate-full.log). Reproduction scripts are [public probes](/tmp/uah-independent-second-probes.py), [command boundaries](/tmp/uah-independent-second-boundaries.py), and [process contention](/tmp/uah-independent-second-process.py).

VERDICT: APPROVE
