# R5 native-owner foundation: independent primary review

Date: 2026-10-08. Scope: only the new `src/ab_harness_synthetic/__init__.py`,
`src/ab_harness_synthetic/notes.py`, and `tests/test_synthetic_notes_owner.py`.
This reviewer did not author the implementation or read writer receipts,
rationale, or other review reports. The requested reviewer model/effort is
not independently observable in this agent; exact model compliance is unverified.

## Governing scope and evidence

This is an H1 synthetic environment-owner foundation review. The domain owner
is `NativeNotesOwner`, not a second UAH admission or lifecycle authority.
`REVIEW.md`, `AGENTS.md`, `CONTEXT.md`, the applicable masterplan/foundation
sections and ADR 0001, the development log, and the synthetic notes integration
contract govern. The review and UAH guardrail skills were used. The parent
assigned this independent native review alongside another review; no additional
agents or review round were opened here.

The frozen SHA-256 values were verified before and after probes:

| File | SHA-256 |
| --- | --- |
| `src/ab_harness_synthetic/__init__.py` | `14f9b4c6a84029250aa9c1602f320c167e51f7eb1bc4932cf479ec300ddab83d` |
| `src/ab_harness_synthetic/notes.py` | `bed451276c769cacb10befaac54c8347932ac9c70471f834e1d878c5b3277642` |
| `tests/test_synthetic_notes_owner.py` | `2391e2273d9c97cf43871025fbcee4e0b1c2df35ec460e0453a005cbe6391e36` |

Inputs were [predeclared](2026-10-08_uah_r5_native_primary_evidence/declaration.md)
before reading the new source or tests. The first execution ran the unchanged
public ingress suite and the copied new owner suite: **50 passed**. After this
run, source inspection confirmed its positive test performs an actual native
write and designated closure read after valid public `TaskIngressAuthority`
setup. The independent literal control `"review note\n"` also passed.

The current `src` and `tests` were copied once into a temporary after tree;
before was copied from that tree and only the new package/test were removed.
The initial baseline import leaked through the editable installation and was
discarded. The corrected `python -S` baseline reported no synthetic package
and **28 unchanged ingress tests passed**. Copied existing core source was
identical. The absent module has no baseline native behavior; no implementation
or parity was invented. The documented dirty snapshot
`2026-10-08_uah_r5_owner_local_evidence/dirty_before.sha256` identifies the
parent's reference state, not a fabricated implementation.

The [independent probe](2026-10-08_uah_r5_native_primary_evidence/probe.txt)
executed **48 cases: 42 PASS, 6 FAIL**. Five failing inputs are variants of one
nested compiled-body identity mechanism; the sixth is the same-workspace
owner-fence mechanism. The reporter exits zero after recording failures, so its
exit status is not a green gate. [Full output](2026-10-08_uah_r5_native_primary_evidence/probe_output.txt)
and [exact commands](2026-10-08_uah_r5_native_primary_evidence/execution.md)
are retained. An unchanged rerun produced the same outcomes for preservation.

## Standards

### BLOCKING: 1 of the 2 found so far. Instance-local state permits a second mutation coordinator for one workspace

Location: `src/ab_harness_synthetic/notes.py:197` and `:200`.
The path identifies one native resource, but each constructor independently
creates its lock, phase and operation-consumption set. Constructor association
checks do not reject another owner for the same workspace. `REVIEW.md` section
5 requires encapsulation and treats a domain with two owners as blocking; the
integration contract requires permitted owner writes to remain fenced from the
designated read through callback completion.

Public reproduction, using a valid public-ingress compiled fixture:

```python
task = _inputs()["compiled_task"]
oracle = ExactNoteOracle.issue(task, expected_text="review note\n", owner_id="notes")
first = NativeNotesOwner(workspace, task=task, oracle=oracle, owner_id="notes")
first.write_note("write", "review note\n")
second = NativeNotesOwner(workspace, task=task, oracle=oracle, owner_id="notes")

def closing(observation):
    assert observation.owner_result().succeeded
    second.write_note("write", "wrong")

closure = first.finalize("closure", closing)
```

Input: two public native-owner instances with the same task, oracle, owner ID
and temporary workspace, in one process, with a second owner-mediated write
inside the first closing callback.

Expected: reject the second coordinator or reject its write while the shared
workspace is closing. Operation replay must not reopen the same native resource.

Actual: the second write is allowed, including reuse of `"write"`.
The first closure remains successful and reaches `callback_completed`, while
`note.txt` contains `b"wrong"`. Exact output:
`{"actual_hex":"77726f6e67","closure_succeeded":true,"phase":"callback_completed","second_write":"allowed"}`.

The callback returned, so `callback_completed` itself is accurate. The failure
is the mutation fence and resource ownership scope. This is not an external
concurrent writer, private attribute modification, semantic owner-ID
impersonation or authenticated-commit claim. A workspace-scoped exclusion or
explicitly exclusive native owner could address it in a separately authorized
repair; no repair was made.

## Spec

### BLOCKING: 2 of the 2 found so far. Retained source reconstruction does not verify the nested compiled-body hash

Location: `src/ab_harness_synthetic/notes.py:40`, `:56`, and `:102`.
The serialized path validates canonical outer keys and four nonempty lineage
strings, then hashes the oracle. It does not validate that the retained
`compiled_task_id` is the content hash of the complete retained compiled
body. Reconstruction consequently accepts an internally inconsistent source.
The governing contract requires complete task/body/environment/trace/compiled-ID
association and retained sources for reconstruction.

Public reproduction:

```python
task = _inputs()["compiled_task"]
body = task.to_dict()
body["task_spec"]["goal"] = "foreign"  # compiled_task_id remains unchanged
canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"))
oracle = ExactNoteOracle(canonical(body), "review note\n", "notes")
restored_oracle = ExactNoteOracle.from_dict(
    oracle.to_dict(), expected_id=oracle.oracle_id
)
observation = NoteObservation(
    canonical(restored_oracle.to_dict()), "closure", "closure_content",
    b"review note\n".hex(),
)
restored = NoteObservation.from_dict(
    observation.to_dict(), oracle=restored_oracle,
    expected_id=observation.observation_id,
)
assert restored.owner_result().succeeded
```

Input: canonical complete serialized compiled source with a changed goal and
the old compiled-task ID. The constructor calculates a new outer oracle ID;
the retained outer references are therefore internally consistent. Equivalent
controls change environment ID, task ID, trace ID, or the compiled ID itself.

Expected: reject the internally invalid nested compiled association before
issuing or reconstructing a verified oracle/observation, even if the outer
artifact has a valid newly calculated hash.

Actual: all five variants construct, serialize and reconstruct successfully;
the reconstructed content result succeeds and supplies
`("note_content_matches",)`.

This is **nested body/hash validation**, not authenticated producer origin.
It does not claim that a party can preserve the original trusted oracle ID
while changing its source: those controls reject. `issue` validates a concrete
CompiledTask, and `NativeNotesOwner.require_task` rejects association with a
different honest concrete task; those controls also pass. No bypass of those
active-owner checks is asserted. The defect is that the public retained-source
boundary accepts an intrinsically inconsistent compiled artifact without a
live task. A future repair must preserve the core schema/identity owner rather
than create a second admission authority.

## Required design principles

1. Separation of concerns: **OK**. Exact content and native note observation
   stay in the domain package; no new UAH lifecycle writer or semantic admission
   path is added.
2. Programming by intention: **OK**. Occurrence and content kinds are distinct;
   phase names distinguish callback return from failure and do not claim
   terminal UAH acceptance.
3. Encapsulation: **VIOLATION**, `notes.py:197` and `:200`.
   Workspace mutation state is per instance rather than per owned resource
   (finding 1).
4. High cohesion: **OK**. Oracle, retained observation and native workspace
   operations each have a focused local purpose.
5. Low coupling: **OK**. The package consumes two portable core contracts;
   core source remains unchanged, with no ROS, NAO, provider SDK or runtime
   product dependency introduced.

## Observed passing behavior and limits

Exact UTF-8 byte controls pass for empty text, composed/decomposed Unicode as
distinct expected sources, embedded NUL and newline preservation. Wrong text,
missing newline, added newline, CRLF, BOM and normalization differences fail
closure content while retaining an actual write occurrence. Lone-surrogate
source/write attempts reject without mutation; invalid current UTF-8 bytes
remain retained and unmatched.

No native write with a missing file supplies no effect. Pre-existing correct
content can supply only `note_content_matches`, never `note_written`; the
foundation does not conflate content with historical occurrence. Correct writes
followed by changed content or deletion retain historical bytes and fail the
separate closure observation. Serialization reconstruction is unchanged after
the live file is restored to different current content.

Missing and tampered source under original references reject. Independent A/B
public tasks and owners reject foreign oracle/observation association in both
orders; same operation IDs on separate task/workspace pairs have distinct
observation IDs. Concrete task/environment/trace/hash tampering, retained
operation/kind/bytes aliases and same-instance duplicate write/closure IDs
reject. Same-instance closing writes and reentrant closure reject. RuntimeError,
KeyboardInterrupt and SystemExit callbacks leave `callback_failed`, never
`callback_completed`. The supplied symlink rejection control passed.

No units or numerical thresholds, date policy, status enum consumers outside
this native module, template/UI logic or external gate exemptions are changed.
No UAH execute port, execution receipt, acceptance event, full-chain restart
qualification, producer authentication, live provider, NAO parity or H1 exit was
tested or claimed. Self-contained observation hashing is not proof that a
native write occurred in an authenticated producer. Arbitrary module/process
tampering and external concurrent filesystem atomicity remain excluded.

The root agent owns setup, hooks and documentation integration checks. This
review did not run or infer their result. No source repair, core change, Git
operation or extra review round occurred. The next discriminating probes are
the two retained reproductions against a separately authorized frozen repair.
No nits were found; the two axes contain two distinct blocking mechanisms.

VERDICT: CHANGES
