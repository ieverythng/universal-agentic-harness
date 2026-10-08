# Independent R5 native primary probe declaration

Declared 2026-10-08 before reading new implementation or tests.

Frozen files:
- src/ab_harness_synthetic/__init__.py: 14f9b4c6a84029250aa9c1602f320c167e51f7eb1bc4932cf479ec300ddab83d
- src/ab_harness_synthetic/notes.py: bed451276c769cacb10befaac54c8347932ac9c70471f834e1d878c5b3277642
- tests/test_synthetic_notes_owner.py: 2391e2273d9c97cf43871025fbcee4e0b1c2df35ec460e0453a005cbe6391e36

Inputs fixed before implementation inspection:
1. Public positive: accepted TaskIngressAuthority start and complete CompiledTask fixture; source text "review note\n"; matching native write then designated closure read and returned callback.
2. Byte controls: empty text; "é\n"; Unicode decomposed equivalent; missing/further newline; carriage-return newline; invalid UTF-8 and lone surrogate rejection.
3. Schema-valid wrong text; narrated write/no actual mutation; pre-existing exact content without a native write.
4. Missing source, foreign environment/task/trace or compiled ID; source bytes tampered after freeze; body/source hash tampering and body association with an independently compiled task.
5. Historical good write then wrong bytes or deletion before closure; retain both full source and closure observed bodies.
6. Replayed/aliased operation IDs and duplicate write/verify operations, in both entity orders, with no false occurrence or closure.
7. Closing owner writes attempted inside callback; reentrant check/write; callback exception before/after attempted write, including BaseException; callback_completed is false if callback fails.
8. Two tasks/oracles and two owners: shared and separate operation IDs, foreign receipts/oracles and cross-order association checks.
9. Reconstruction from serialized/frozen source and recorded assessment after live-file alteration; no current reread pretending to be historical state.

Baseline: the new package and new test file are absent. Package import must be unavailable. Existing copied core dependencies must match after. No baseline implementation or native parity will be fabricated.

Initial execution before reading new implementation: run unchanged public ingress suite plus copied new owner test suite. This is a control only; independent probes remain required.

Out of scope: UAH execute port, receipts/terminal acceptance/full-chain qualification/authenticated commits, producer authentication, arbitrary module/process tampering, external concurrent filesystem atomicity, live providers, source repairs.
