# R4-FIX independent second review

Date: 2026-10-08. Report saved at 17:50:26 Europe/Madrid, before the 17:52:52 hard stop.

Scope: the frozen changes to `proposal_admission.py`, `domain_lifecycle.py`,
`environment.py`, `lifecycle.py`, and `tests/test_admission_active_provenance.py`.
Comparison: supplied exact-before source copies, not Git HEAD. Concurrent O1 and
documentation changes are outside this runtime attribution.

Reviewer was a fresh agent and did not write the repair. Requested reviewer
configuration was `gpt-6-astra` at `max`; the executing backend is not observable
from this review, so distinct-model execution is not independently attested.
`REVIEW.md` was read first. Attack classes were saved in
`2026-10-08_uah_r4_fix_second_review_inputs.md` before source, changed tests, or
diffs were inspected. The initial unread public control executed successfully:
`tests/test_two_stage_admission.py`, 48 passed. No writer receipt, writer
rationale, or other review report was read.

## Standards

No BLOCKING or NIT finding in this bounded repair. The UAH guardrails skill
directed the review to the H0 authority chain, retaining H1/H2 qualification as
separate claims. The code-review skill supplied separate Standards and Spec
axes. This reviewer performed both axes within the assigned independent review;
no additional reviewer was delegated.

All required design principles:

1. Separation of concerns: OK. Artifact identity remains owned by the artifact;
   recorded active provenance remains a ledger concern. Environment owners
   retain effect validation and native dispatch ownership.
2. Programming by intention: OK. `require_current_admission` and
   `_require_current_event_authority` explicitly name the distinction between
   current authority and historical replay.
3. Encapsulation: OK. Consumers call the ledger's current-admission requirement
   instead of constructing a second authoritative admission store. Concrete
   verifier calls prevent foreign or older implementations from defining the
   current validation contract.
4. High cohesion: OK. The new reducer state is derived while replaying the same
   semantic-admission events it qualifies. No independent writable store was
   introduced.
5. Low coupling: OK. Portable core boundaries are unchanged. The change adds no
   provider, ROS, NAO, runtime-product, UI, or template dependency.

## Spec

No BLOCKING or NIT finding in the frozen R4-FIX scope.

The active-write reducer checks only staged events, while historical reload
remains readable. A full verified current admission is required for active
domain, execution, evidence, and tool-budget facts. Successful current task
acceptance cannot use historical-only issued evidence. This is not inferred
from a schema-shaped alias or body fragment: the complete current artifact is
parsed and its lineage checked.

`ExecutionReceipt.issue` remains a pure artifact constructor. Constructing a
valid receipt from a current lease does not establish recorded authority. The
actual ledger refuses missing admission, missing lease, foreign lineage, and
historical-only provenance. This separation is consistent with the task; no
new stateful constructor API is required.

## Executed paired evidence

Isolated runtime roots were
`/tmp/uah-r4fix-second-review-whD4rLxd/current` and
`/tmp/uah-r4fix-second-review-whD4rLxd/before`. Each contains copied source and
tests. The before root replaces the four runtime modules and prior snapshot test
with the supplied exact-before copies. Imported module and fixture paths were
printed and verified to point inside each respective root.

Durable independent probes:
`2026-10-08_uah_r4_fix_second_probe.py` (80 cases).
Durable paired results:
`2026-10-08_uah_r4_fix_second_current.xml` and
`2026-10-08_uah_r4_fix_second_before.xml`.

| Execution | Current | Exact-before |
| --- | --- | --- |
| Public two-stage admission control plus 80 independent cases | 128 passed | 112 passed, 16 failed |
| Changed provenance tests plus admitted-object snapshot tests, repository runtime | 48 passed | Not used as independent comparative evidence |

The 16 failures are expected rejection assertions that the old implementation
violates. They are repaired mechanisms, not findings against the current bytes.

| Independent input and expected boundary | Exact-before actual | Current actual |
| --- | --- | --- |
| Remove all three semantic markers/body, preserve admission and lease, rehash event IDs and causal references; reject active lease, start, raw start, owner dispatch, completion, raw receipt, and acceptance | All seven routes accepted | All seven reject before durable mutation or native dispatch |
| Remove each of the six nonempty proper subsets of body/snapshot/schema markers; reject incomplete wire | Rejects | Rejects for every route |
| Genuine archived v2 artifact, constructed using its old concrete class and validated by the real old verifier; reject current lease, start, receipt | Three routes accepted | Three reject |
| Forwarding foreign object with a no-op verifier, including nested in a concrete current lease; reject current lease, receipt, start, dispatch | Four routes accepted | Four reject |
| Remove all semantic markers and change frame metadata, keeping admission/lease and rehashing the stream; reject start and owner dispatch | Two routes accepted | Two reject |
| Current valid receipt with separately absent recorded admission or lease | Rejected at ledger/owner boundary | Rejected, no durable mutation |
| Self-consistent, rehashed current receipt with foreign admission, lease, environment, task, trace, operation, object, or owner | All eight rejected | All eight rejected |
| Current full artifact JSON round trip, restart, exact idempotent lease, two concurrent independent ledger writers, accepted closure and digest | Passes; one native call | Passes; one native call |
| Changed binding source revision after admission | Rejected before native call | Rejected before native call |
| Genuine completed v2 fixture with no current semantic markers | Historical accepted replay and unchanged bytes | Historical accepted replay and unchanged bytes |

The genuine historical digest remains
`verified-trace-digest:sha256:f9f65439cc22226974386beb322d01cf5290632f3b9cfde23d30284001d72441`.
The competing-writer control used two threads with separate file-backed ledger
instances. It was not a multi-host or distributed-lock test.

Reproduce either paired run from its isolated root:

```bash
PYTHONPATH=src:tests /home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest -q tests/test_two_stage_admission.py /home/juanbeck/universal-agentic-harness/docs/artifacts/reviews/2026-10-08_uah_r4_fix_second_probe.py --tb=short
```

Additional checks executed: Ruff check on the durable probe, Ruff formatting of
that probe, documentation renderer `--check` (12 metadata records), and
`git diff --check`. No source, hook, Git configuration, or provider was changed.
The full hook suite was not independently rerun by this reviewer; the parent
reported its post-freeze run, which is not substituted for review evidence here.

## Frozen identities and limits

Current source hashes were verified before inspection and after the paired run:

```text
ae9cf6134e0d9fb3fa17ccf191e63a139222ab1661306d3e13d387d3e2be34c5 proposal_admission.py
2ed2f0068b5ded25cd190850feed941f8be78a22157a07fbb0b6d42260ec7de0 domain_lifecycle.py
4cedae9add9c50618e064964da8f3ad2c78f696969b9c9d2e5e593af32a19eaa environment.py
b35641d97b8d915df358e880de73400386395e8b3525a41cae99e329b04176ee lifecycle.py
ad585953067804b3f30b184c57520d7646428fc84fca17797cdd4afdb716540e test_admission_active_provenance.py
```

Exact-before runtime hashes:

```text
7b52d38ebda8e377c4100494ed6d40bc2a027485da031afbee01a5a90ee2e86c proposal_admission.py
ce472670140e418ba67c11736d70e240d9511b25584de7e638e36cac245c5aa3 domain_lifecycle.py
d754415fe07e301da635706c5a9af218c507e35126a400b82b2d9a609ba5c0b7 environment.py
2b3d80aa559257d0c6bb7165c73b7fe52d79319ba46cdab4736737b18be725a4 lifecycle.py
```

This approval is limited to the two R4-FIX mechanisms and their exercised
consumers. It does not close raw task-start provenance, native effect truth,
stale-evidence policy, provider integration, O1 changes, or H0/H1/H2 release
qualification. Arbitrary external file writers are not made authenticated by
the marker-removal probes. No admission body is invented for old history.

The next useful qualification is a process-level race across a legacy-only
ledger and current lease creation, followed by the wider owner-evidence suite;
neither is asserted as performed here.

Standards: 0 findings. Spec: 0 findings. No blocking issue found within either axis.

VERDICT: APPROVE
