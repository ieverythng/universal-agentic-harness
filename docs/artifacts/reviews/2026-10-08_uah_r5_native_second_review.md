# R5 native-owner foundation: independent second review

Date: 2026-10-08. Scope: H1 owner-local synthetic notes foundation only.
Authoritative owner: `ab_harness_synthetic.NativeNotesOwner` for the temporary
note and its native observations. No UAH terminal acceptance, execution port,
authenticated producer, common constraint language, full-chain replay, or H1
qualification is reviewed or asserted here.

The reviewer did not write the implementation and did not read the writer's
receipt, rationale, or other reviews. The parent reports that this reviewer was
requested as `gpt-6-astra` / `max`, distinct from the primary review's
`gpt-6.1-sol` / `max`. Those are accepted tool-request settings; the running
backend and effective reasoning effort are not independently observable here.

## Frozen comparison and method

HEAD is `28fab5e7f2c244d86a64c371f2118017999b2387`, branch
`feat/pre-commit-queue`. This is a three-file new-feature review against the
recorded dirty-before state, not a claim that the unrelated dirty tree equals
HEAD. There is no review commit range. The exact-before manifest is
`2026-10-08_uah_r5_owner_local_evidence/dirty_before.sha256`; it contains none of
the three new paths. Scope hashes were checked at opening and closing:

| Path | SHA-256 |
| --- | --- |
| `src/ab_harness_synthetic/__init__.py` | `14f9b4c6a84029250aa9c1602f320c167e51f7eb1bc4932cf479ec300ddab83d` |
| `src/ab_harness_synthetic/notes.py` | `bed451276c769cacb10befaac54c8347932ac9c70471f834e1d878c5b3277642` |
| `tests/test_synthetic_notes_owner.py` | `2391e2273d9c97cf43871025fbcee4e0b1c2df35ec460e0453a005cbe6391e36` |

Inputs were saved in
[predeclared_inputs.md](2026-10-08_uah_r5_native_second_evidence/predeclared_inputs.md)
before implementation or test-source inspection. The first public valid control
ran against a throwaway copy at 19:01 Europe/Madrid, before reading
`notes.py` or its tests. It issued an oracle from the existing public-ingress
compiled-task fixture, wrote `review note\n`, finalized, and verified distinct
write/content observations. It passed with `callback_completed`.

Before/current throwaway copies retain identical core dependencies; the before
copy excludes only the new package and test. The baseline manifest's applicable
core hashes pass, and recursive comparisons of copied core and NAO source trees
are identical. The initial before import accidentally reached the repository's
editable installation. That result is discarded. Repeating with Python `-S`
and explicit site-package paths disabled the editable import mechanism and
returned `ModuleNotFoundError: No module named 'ab_harness_synthetic'`. Native
feature behavior is therefore unavailable before, not a passing parity test.
No stub implementation was invented.

Governing documents read: `REVIEW.md`, `AGENTS.md`, `CONTEXT.md`, UAH guardrails,
the code-review skill, the relevant current/target masterplan and foundation
sections, ADR 0001, current development-log status, the local review workflow,
and `docs/plans/synthetic_notes_integration_contract.md`.

## Standards

The new package remains outside the portable kernel and imports only its
existing typed compiled-task/result contracts. There is no lifecycle writer,
TaskSpec extension, provider dependency, or generic policy subsystem. The two
artifact identity routines have different semantic contracts; their similar
hashing form is not a separate duplication finding. No optional style nit is
reported.

All five required principles:

| Principle | Assessment |
| --- | --- |
| Separation of concerns | OK: oracle identity, native observations, and filesystem actions remain domain-local; acceptance is not implemented here. |
| Programming by intention | OK: write occurrence and closure content are distinct, and callback phase does not name a terminal task outcome. |
| Encapsulation | Violation, `notes.py:197-202`, `notes.py:234-236`: workspace ownership is neither exclusive across public owner instances nor protected against a preexisting hardlink. See findings 1 and 2. |
| High cohesion | OK: the implementation is confined to one note domain and its retained evidence bodies. |
| Low coupling | OK: no reverse dependency from the portable kernel or dependency on provider/runtime products is introduced. |

These are two native-boundary defects, not two different semantic-policy
implementations. The confirmed encapsulation violations are also the Spec
findings below; no additional Standards-only finding is claimed.

## Spec

### 1 of the 2 found so far. BLOCKING R5-N2-01: overlapping public owners bypass the closure fence

Location: `src/ab_harness_synthetic/notes.py:194-202`, `notes.py:213-218`,
`notes.py:242-260`.

The integration contract requires the synthetic owner/coordinator to fence
permitted workspace mutations from its designated final read through the
callback boundary, including an injected owner write. Each constructor instead
creates an independent lock and phase for the same workspace. It neither
rejects overlapping ownership nor coordinates those instances.

Input: construct two `NativeNotesOwner` objects with the same workspace, task,
oracle and owner ID. Write the expected text through one. Inside that owner's
finalization callback, start a thread that writes `wrong` through the other.

Expected: the overlapping owner is refused, its write is fenced, or closure
cannot retain a successful content assessment after that permitted mutation.

Actual: the second public write completes before the callback returns; the
captured closure result reports `note_content_matches` while the live file is
`wrong`. The first owner finishes at `callback_completed`. This reproduced in
both construction orders. No external filesystem process or direct file write
participates in this counterexample. The same-instance concurrent-write control
does reject, showing that the defect is the ownership/fence boundary rather
than failure of the single-instance lock.

This does not demonstrate accepted UAH terminal success: there is no acceptance
port in this slice. It demonstrates a violation of the promised owner-mediated
fence before that future integration can rely on the observation. A repair must
make the one-owner-per-workspace precondition enforceable or coordinate all
permitted native mutations at the workspace boundary.

### 2 of the 2 found so far. BLOCKING R5-N2-02: an existing hardlink redirects the owner's mutation outside its workspace

Location: `src/ab_harness_synthetic/notes.py:217-218`, `notes.py:234-236`.

The declared native effect is a write to the fixture-owned temporary workspace.
The ownership check rejects symbolic links but accepts a multiply linked inode;
`Path.write_bytes` truncates and rewrites that existing inode.

Input: create `owned/note.txt` as a hardlink to a sibling temporary
`not-owned.txt` containing `untouched`; construct the owner for `owned` and call
`write_note("write-hardlink", "review note\n")`.

Expected: the nonexclusive file is rejected, or the write replaces the note
entry without modifying the outside-workspace inode.

Actual: the sibling becomes `review note\n`; its inode remains shared with the
note, and a successful `note_written` observation is returned. The symbolic-link
control rejects and preserves the target. All files were temporary and the
hardlink existed before construction, so this is not an arbitrary concurrent
filesystem-writer attack. The public native method itself performs the outside
mutation. Path ownership must cover preexisting inode aliases before a write is
allowed to prove only the declared workspace effect.

## Reproduction and executed evidence

From the repository root, the minimal finding reproduction is:

```bash
PYTHONPATH=src:tests .venv/bin/python docs/artifacts/reviews/2026-10-08_uah_r5_native_second_evidence/boundary_repros.py
```

The actual review runs used `/tmp/uah-r5-native-second/current/src`, its copied
tests, and the virtual environment's site-packages in `PYTHONPATH`, with
`.venv/bin/python -S`, to avoid editable-install fallback. The retained
[boundary output](2026-10-08_uah_r5_native_second_evidence/boundary_repros.txt)
records both owner orders and the independent hardlink mutation. The larger
[public probe](2026-10-08_uah_r5_native_second_evidence/probes.py) and
[output](2026-10-08_uah_r5_native_second_evidence/probes.txt) contain 20 named
cases: 18 pass and the two findings fail their expected boundary assertions.
Its identity case exercises 27 separate rejected inputs.

Successful controls include exact/wrong/empty text, composed versus decomposed
Unicode, CRLF/LF/trailing newline, BOM, NUL, invalid UTF-8 source/native bytes,
missing file versus empty file, preexisting exact content without a write
receipt, foreign owner/task/source and changed lineage, missing/tampered
observation bodies, caller and export aliases, duplicate operations, callback
mutation and exception, and a concurrent writer through the same owner.
Complete source and closure bodies reconstruct their assessment after deleting
the current file. Historical write success remains separate from failed content
matching. Missing/wrong content can still reach `callback_completed`, correctly
meaning callback return only, never acceptance.

Executed pytest commands selected the copied
`tests/test_prompt_compiler.py`, `tests/test_task_compiler.py`, and, for current
only, `tests/test_synthetic_notes_owner.py`, with `-q -p no:cacheprovider -c
/dev/null`:

| Control | Result |
| --- | --- |
| Before unchanged core | 60 passed |
| Current same core plus new owner suite | 82 passed (60 core, 22 new) |
| Before new-feature import under isolated Python | Unavailable, expected `ModuleNotFoundError` |
| Initial current public control before implementation read | Passed |

The earlier pytest attempts passed with a harmless `/dev` cache warning; the
isolated reruns disabled the cache and passed without it. Raw results,
predeclared inputs, dirty-tree inventory, dependency checks and final scope
hashes are retained under
`docs/artifacts/reviews/2026-10-08_uah_r5_native_second_evidence/`.

No implementation, Git state, provider configuration, or owning-plan documents
were changed. The parent owns repository hooks and document synchronization.
Authenticated observation production, terminal commit, external hostile writers,
full-chain restart and release-wide qualification remain outside this review.

Summary: two confirmed BLOCKING Spec findings, also reflected in the Standards
encapsulation assessment; zero NITs. The bounded owner-local foundation requires
changes. No additional repair round was run.

VERDICT: CHANGES
