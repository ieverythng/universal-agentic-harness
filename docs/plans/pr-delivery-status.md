# PR delivery status

**Current snapshot:** 2026-10-28 12:13 UTC, before the fresh PR2 review. This records
publication and readiness states; it is not a release qualification or
milestone closure.

## PR1: merged baseline

| State | Evidence |
| --- | --- |
| Public pull request | [PR #1](https://github.com/ieverythng/universal-agentic-harness/pull/1), merged into `main` on October 28, 2026. |
| Merge commit | `d9eb84a04099431d774f459792bcd16524ab54ce`, tree `f611dfbb9f8b6dfc5cd8800bef8e2fe3879fa3aa`. This is the verified `main` base for the current documentation candidate. |
| Published source | PR1 head `61301d731e801c5c160f45c8d121520c81d155df`, with the same tree as the merge commit. |
| Local independent review | Spec requested `gpt-6.1-sol/xhigh` and Standards requested `gpt-5.6-sol/xhigh`; both returned `APPROVE` for the exact 137-state baseline (127 present paths and 10 absences). Reviewed tree: `fc198f4c297e54b00e6653dad0bbb856b6b8054d`. |
| Local audit identifiers | Manifest SHA-256 `1ae0517bc6a75b370aa63ac65235465e5be6506f403fefd5a67bf35d779d1e29`; patch SHA-256 `ad7229c630a867e874307c3795440a5d5f5c669f7938518ecaed742b77bfb882`. These identify local review artifacts, which are not published receipts. |
| Human commit additions | The published commit also includes `uv.lock` and `docs/coordination/README.md`, outside the 137-state review manifest. |
| Hosted CI | The head-associated pull-request run reported that `test (3.10)`, `test (3.12)`, and `test (3.13)` passed. Its workflow checked synthetic merge commit `b7ef095c8599db7ee20b432d2ae5a57376a5d966`; that commit has the same tree as the published PR1 head. [Public CI run](https://github.com/ieverythng/universal-agentic-harness/actions/runs/39704657812). |
| Post-merge main CI | The push run on merge commit `d9eb84a04099431d774f459792bcd16524ab54ce` reported success with all three required jobs complete. [Public main run](https://github.com/ieverythng/universal-agentic-harness/actions/runs/40683070828). |

## PR2: documentation candidate readiness

No PR2 has been opened as of this snapshot. The twelve-path documentation
candidate is based on the merged `main` commit above. The fresh independent
review pair is pending at this snapshot. No PR2 hosted CI or merge outcome is
claimed. Publication remains subject to the review, checks, and human staging
authority recorded in the repository guidance.

The Markdown pull request template is a static scaffold. GitHub makes it
available to prefill new descriptions after it is present on the default
branch; it does not execute checks or generate review content.

## Release boundary

The `v0.1` reviewed migration baseline provides partial H0/H1 evidence and
closes neither milestone. No `v0.1` tag has been created or authorized; a tag
remains under human consideration. H0, H1, O1, and H2 remain open. H6 remains
research only. Release targets are listed in the
[release process](../RELEASING.md) and [masterplan](universal_agentic_harness_masterplan.md).

## Historical snapshot: 2026-10-22 01:16:50 UTC

At this snapshot, PR1 was open and unmerged. Its head was
`61301d731e801c5c160f45c8d121520c81d155df`, tree
`f611dfbb9f8b6dfc5cd8800bef8e2fe3879fa3aa`, and parent and remote `main` were
`eddfa6d28ebcc6f2967c0568a6ed2d29eccf665e`. The exact 137-state local review
baseline described above had two `APPROVE` verdicts. The published commit also
contained the two human additions listed above. The head-associated hosted CI
run reported all three required jobs passed; its pull-request workflow checked
synthetic merge `b7ef095c8599db7ee20b432d2ae5a57376a5d966`, whose tree matched
the published PR1 head. [Public CI run](https://github.com/ieverythng/universal-agentic-harness/actions/runs/39704657812).

The PR2 packet at that time was based prospectively on PR1 while it remained
unmerged. After PR1 merged, the documentation candidate was refrozen against
actual `main`. This historical snapshot does not report a PR2 verdict, hosted
CI result, or merge state.
