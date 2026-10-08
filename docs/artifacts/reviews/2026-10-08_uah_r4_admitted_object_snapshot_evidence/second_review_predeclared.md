# R4 independent second-review probes, declared before source/diff

Initial execution: existing public `tests/test_two_stage_admission.py` on both isolated current and exact-before source copies, without reading that test or implementation first.

Adversarial inputs:
1. Admit an unchanged registered semantic object and dispatch it through owner execution; require a successful owner receipt and replay-equivalent events.
2. Remove admitted-object snapshot bytes, remove version, use empty snapshot bytes, and alter only the snapshot version; require fail-closed active use.
3. Modify a nested operation/object identity and recompute its nested/event identity while retaining the original outer admission ID; require outer identity rejection.
4. Pair a snapshot with the wrong frame, object ID, action schema, or summary metadata; reject each mismatch independently and when combined.
5. Submit genuine historical v2 metadata for read-only replay, then attempt active admission/leasing/dispatch; permit only the intended historical replay path.
6. Change the current object catalog before dispatch, and mutate it during dispatch; reject unauthorized effects or receipt/task success.
7. Mutate caller-owned object/summary/schema dictionaries after admission, after lease issuance, and after execution; immutable authority evidence must not change.
8. Alter implementation binding revision without altering the admitted semantic object; preserve the declared valid unchanged/revised-binding controls, and reject incompatible bindings.
9. Execute two operations against distinct objects in both orders, including one valid and one drifted object; no unrelated-object authorization or aggregate false success.

No runtime edits, writer receipt/rationale, or other reviewer material will be read. Base comparison is exact-before supplied files, not a guessed Git merge-base. Backend model identity is not directly observable from these tools and will not be claimed as verified.
