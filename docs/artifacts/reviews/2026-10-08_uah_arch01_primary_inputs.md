# ARCH-01 independent review: predeclared inputs

Declared before reading either implementation or the changed test source.
Review start: 2026-10-08 16:27 UTC. Reviewer did not write the patch.

## Initial public control

Run the current public prompt-compiler tests in isolated current and exact-before
source copies, using identical current tests and all unaffected dependencies.
The tests are executed without reading their source. Record the selected tests,
exit status, and any failures before reading the diff.

## Independent probe inputs

Use the public `PromptCompiler.compile` and `ProposalAdmissionGate.admit` seams.
Begin with one permitted, runtime-callable object in the direct control band,
approved binding and reviewed argument schema, correct role/output type, and a
matching compiled evidence obligation. No live provider or execution owner is
called.

- Effects: no prohibitions; expected-only prohibited effect; observable-only
  prohibited effect; both prohibited; different expected and observable effects;
  an unrelated prohibited effect as permitted control.
- Counts and order: zero offered objects; one object; two permitted objects; one
  permitted plus one forbidden in both orders; expected and observable lists in
  both orders where order has no semantic significance.
- Static restrictions: projected versus unprojected; directly controllable versus
  inspect-only or out-of-band; callable versus non-callable; present versus
  missing compiled obligation; valid and invalid output enum.
- Coherence: output-schema alternatives, rendered object choices, operation
  examples, binding/input-schema fingerprints, and executable versus inspect-only
  labels must agree with the shared static eligibility result.
- Ordered reason codes: simultaneous static violations and earlier lineage,
  role/output, identity, binding, input-schema, and argument failures.
- Stateful checks: compiled identity, proposal/task lineage, schema/argument
  validation, binding catalog/owner/environment/runtime approval, and downstream
  domain-execution authority remain unchanged and independently owned.

All before/current probes use the same fixtures and unaffected dependencies.
Source inspection may suggest additional probes; they will be labelled separately
from this predeclared set.
