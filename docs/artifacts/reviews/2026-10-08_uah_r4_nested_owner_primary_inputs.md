# Independent primary review inputs (declared before execution and code reading)

Declared at 2026-10-08 16:09 UTC. The review compares the supplied four
exact-before source copies with the frozen current five-file candidate. It does
not inspect writer receipts, earlier reviews, rationale, or interrupted output.

Predeclared inputs:

1. A valid proposal with one owner-issued operation, then two operations in each
   order; canonicalization, admission, dispatch, receipt validation, and replay
   must agree on actual concrete fields.
2. Empty and missing nested fields, valid nested object, stale nested identity,
   stale outer identity, and both stale together. Rejection must happen before
   owner dispatch or ledger authority changes.
3. A supplied artifact whose instance serializer or identity verifier disagrees
   with its actual fields. Authority must follow actual fields, not an overridden
   instance method. Test each method separately and in combination.
4. Actual operation fields or owner IDs changed while instance methods return
   earlier valid serialized or verified data. Test before admission, after
   admission, and immediately before dispatch.
5. A callback that mutates the caller-owned admitted operation or nested evidence
   while dispatch is in progress. The operation actually executed, the receipt,
   and append-only replay must retain one coherent identity and owner.
6. Valid historical ledger events and read-only replay/snapshot operations must
   remain accepted without rewriting data or minting new execution authority.

Initial public control: execute the current public two-stage admission and
nested-owner test modules in a throwaway copy before reading their source or the
implementation diff. Run the same control against exact-before source files
with all unaffected files copied identically, then build independent focused
probes of the inputs above.

Scope excludes process security and arbitrary module replacement. Public
instance methods and supplied concrete artifact fields are in scope. No stage,
commit, push, provider call, or source edit is authorized.
