# ARCH-02 provenance and NAO-first seam research handoff

Date: 2026-10-08. Source-only lane began at 18:34 UTC; hard bound 18:54 UTC.
Status: source-only research recording the human-selected fail-closed label
policy. The decision is accepted; implementation repair, fresh review and release
evidence remain separate work. No evaluator/reviewer interface is implemented.
Owner: Observatory owns read-only projection conformance. Evaluator/review
owners would own measurement production and gate decisions. The human/GRILL
owns normative decisions; DEV owns the separately authorized repair and canonical
contract/status updates. RESEARCH owns only this dated handoff.
Affected boundary: O1 supporting H0/H1 inspection and H2 NAO parity. No H0/H1/H2
exit, measured capability, live effect, or H3+ promotion is established here.

The two research lanes read local primary source and existing receipts. They ran
no probe, test, model, network, provider, simulator or native effect. The first
draft was written immediately before receipt of an exclusive commit HOLD;
shared writes then stopped. GRILL subsequently reported the commit boundary
released. Root integrated the draft after clearance. Only this research artifact
is owned by this pass. No source, skill, Git, dashboard, Notion or context
mutation is part of the pass. Root documentation checks are recorded separately
below; they are not new NAO qualification or measurement evidence.

## Decision-bearing result

The human selected rejecting requested `measured` and `reviewed` labels in the
current O1 API for both ledger and raw-event sources until a separately selected,
owner-enforced evaluation/review evidence contract exists. Preserve recorded
ledger, synthetic and conceptual views, including incomplete explicitly
synthetic illustrations. Preserve enum vocabulary and target definitions. This
records the accepted decision, not a claim that the correction has landed.

The label-policy question is resolved. A real bound-evidence interface remains
deferred, rather than a prerequisite to correcting unsupported claims. Silent
downgrade was a possible response but is not recommended: it hides an unmet
caller expectation and needs an explicit
requested-versus-effective-label diagnostic contract.

The [completed accounting/NAO-first note](2026-10-08_uah_review_commit_accounting_and_nao_first.md)
is reused for integration order and evidence boundaries. It is research, not
accepted replacement of H0/H1 synthetic exit coverage.

## Current source facts

The owning [Observatory contract](../../architecture/observatory_contract.md)
sections 1 and 6 reserve measurement truth to evaluator-produced results under
frozen configuration and reviewed truth to acceptance through the applicable
gate. Metrics are keyed by the complete content-addressed configuration, not a
model-family name. O1 is never an evidence issuer or execution/policy authority.
Its current narrower API accepts a ledger or event collection with one label;
complete configuration/comparison views remain absent. Section 7 explicitly
says the complete O1 exit is unmet.

Complete `src/ab_harness/observatory.py` was read, including its consumers:

- `ObservatoryDataLabel` at lines 22-29 defines five classes. Its docstring says
  one provenance label applies to every value in a projection.
- `project_observatory` at lines 225-242 defaults `LifecycleLedger` to recorded,
  raw `Iterable[TraceEvent]` to synthetic, and rejects only a raw requested
  recorded label. Enum conversion accepts requested measured/reviewed labels
  in both branches. No evaluator, frozen configuration, review decision,
  producer authentication, freshness, or scope evidence is an API argument.
- Falsey `data_label` values currently select the default through `data_label
  or ...`. The narrow proposal should not silently expand into unrelated input
  validation policy.
- Constructor reconstruction at line 242 checks existing event shape/content
  identity and detaches supplied values. It does not establish that an
  evaluator/reviewer produced them. `TraceEvent`'s relevant constructor,
  identity, export code at `lifecycle.py:83-277` and ledger export at `:707-710`
  were read. The hash payload binds event content; callers can construct
  self-consistent content. Hashes and issuer-name strings are not producer
  authentication.
- `_project_trace` at lines 298-334 derives status from explicit terminal event
  kinds and copies the projection label to every trace. This permits an
  illustrative synthetic terminal event without requiring ledger causal
  completeness. It is not a new claim of effect truth.
- `_graph_payload` emits that same global label at line 364. HTML summary
  and trace badges consume it at lines 487, 525 and 648. The public renderer at
  lines 280-295 always obtains its projection through `project_observatory`.
  A local admission check at that shared seam would cover render, JSON and HTML
  consumers without adding policy to templates.
- A collection may contain multiple environments/tasks/traces, but there is
  still only one label. Internal lineage checks do not prove homogeneous data
  origin. One measured metric or reviewed trace could not justify upgrading
  all unrelated values in a mixed projection.

Source: [Observatory implementation](../../../src/ab_harness/observatory.py),
[event and ledger owner](../../../src/ab_harness/lifecycle.py),
[public Observatory tests](../../../tests/test_observatory.py),
[raw identity tests](../../../tests/test_observatory_raw_identity.py).

The inspected current `test_projection_preserves_the_declared_data_label` at
`tests/test_observatory.py:182-197` parametrizes only synthetic and conceptual.
It does not contain measured/reviewed controls. The raw identity suite explicitly
preserves a valid incomplete synthetic terminal illustration at lines 120-127.
Implementation acceptance of measured/reviewed is established by source and
historical receipts below, not by claiming that current tests exercise it.
The recorded-canary renderer passes its ledger without a requested label;
the H1 example uses an explicit synthetic label. Those examples must retain
their declared meaning, not acquire inferred qualification from their titles.

## Existing historical executed evidence, not rerun here

The [October 5 ARCH-02 finding](../reviews/2026-10-05_uah_h0_h1_independent_review.md)
at lines 277-294 records a fabricated but content-valid terminal event with no
task start, obligations, evaluator configuration, or review decision. Projection
and graph reported measured/reviewed plus accepted; file-backed ledger reload
rejected the missing task start. The finding classifies unsupported provenance
escalation, not incomplete explicitly synthetic illustrations, as the failure.

The exact [saved original probe](../reviews/2026-10-05_uah_review_repros/observatory_probes.py)
was read in full. It constructs self-hashed v1/v2 events, requests all labels
from empty iterable and empty ledger sources, checks terminal hash round-trip,
requests measured/reviewed on a terminal-only iterable, contrasts raw projection
with ledger reload, and includes actor/HTML controls. The probe's zero exit is
not a passing contract result: its `show` helper catches and prints exceptions.
The [R0 receipt](../reviews/2026-10-08_uah_r0_baseline_and_skill_handoff.md)
at lines 54-75 records the later historical rerun reproducing ARCH-02.

The [O1 constructor correction receipt](../reviews/2026-10-08_uah_o1_conformance_fix.md)
and both [primary](../reviews/2026-10-08_uah_o1_conformance_fix_primary_review.md)
and [second](../reviews/2026-10-08_uah_o1_conformance_fix_second_review.md)
reviews approve identity, versioned shape, and detachment at their exact frozen
bytes. They expressly exclude measured/reviewed provenance, causal qualification,
and complete O1 release closure. The receipt retains the earlier identity-only
CHANGES verdict rather than rewriting it. Its later integration account records
the changed lifecycle dependency separately and says constructor/schema/identity
contracts were unchanged. These are historical tested receipts, not fresh
checks performed by this research lane.

The [follow-up index](../reviews/2026-10-08_uah_review_followup_status.md)
continues to mark ARCH-02 open and separate from stale-event identity. Neither
two prior O1 approvals nor a current matching source hash closes ARCH-02.

## Smallest alternatives

| Route | What it would establish | Scope and consequence |
| --- | --- | --- |
| Reject unsupported measured/reviewed requests | Current O1 cannot claim measurement or review from caller metadata | Human-selected narrow correction, implementation open; both source branches, no evidence issuer, no new schema/interface or ledger authority |
| Downgrade to source-supported label | Unsupported requests cannot produce upgraded output | Requires explicit diagnostics and agreed mapping; ledger could retain recorded, raw could retain synthetic, but requested conceptual meaning must not be erased; silent relabeling conceals the mismatch |
| Bind real evaluator/reviewer evidence | Qualify exact result and scope under frozen configuration and gate | Deferred design; must establish authorized producer, reviewer policy, exact coverage and replay validation before permitting upgrade; no such implementation is delivered here |

Rejecting measured/reviewed in today's API is a temporary unsupported-operation
policy, not a claim that those classes are permanently forbidden. Retaining
enum vocabulary need not add a new interface. A future accepted evidence route
must consume authentic owner decisions; O1 must not issue them itself.

## Deferred evaluator/reviewer provenance work

Status: not implemented and not accepted as a concrete interface. Evaluator
owners produce measurements; the independent review/gate owner accepts exact
results; Observatory owns read-only consumption. DEV owns a future scoped
implementation only after human/GRILL selects the contract. It is deferred
because the current projection takes no evaluator/reviewer evidence and applies
one global label to all values. Removing unsupported claims needs neither an
evidence issuer inside O1 nor a speculative generic resolver.

Reopen when a real evaluator result and independent gate decision have a
concrete consumer requiring measured/reviewed display, an owner-reviewed scope
contract, and discriminating replay/holdout controls. Required linkage includes
the frozen complete configuration, evaluator identity/authority, source corpus
or event bodies, metric definition and exact result bytes. An independent gate
decision must bind that same result and configuration. Define coverage, revision
and current-use freshness, uncovered/mixed populations, and immutable historical
display explicitly. Replay must verify bindings without model/evaluator/owner
reinvocation or a second trace store. Hash equality alone is not issuer authority.
No field layout or per-record projection architecture is selected here.

For a future binding route, the minimum questions are semantic obligations,
not selected field names or an adopted architecture:

- Which authority permits this evaluator/reviewer to issue this class of result?
  A recomputed digest or caller-supplied issuer ID cannot answer this.
- Which exact result body, metric definition, frozen complete configuration,
  evaluation corpus/split and run scope are covered? A review must bind the
  measured result and applicable gate decision, not merely a trace title or
  agent family. An implementation APPROVE report is not automatically a
  gate-accepted measurement.
- What current revision/activation and validity policy applies? Historical
  evidence may remain readable while being insufficient for a new claim;
  elapsed time alone need not invalidate an immutable historical measurement.
- How are mixed synthetic/recorded/evaluated values represented without
  upgrading uncovered values? The current global label cannot express this.
- How do reload and replay verify exact evidence and scope without reinvoking
  evaluator, model or owner, granting execution, or creating a second trace store?

## Proposed discriminating controls, not executed

These controls are a proposed public-seam repair/review handoff. The rejection
policy is accepted; the full matrix is not a separately accepted test contract
and does not expand this pass's authority.

| Family | Required distinction for the selected fail-closed route |
| --- | --- |
| Both source branches | Valid ledger and tuple/generator raw sources reject unsupported measured/reviewed; ledger validity alone is not evaluation provenance |
| Enum/string and empties | Both enum and string upgrades reject, including empty ledger/iterable; `None` and existing falsey-default behavior retain their current defaults unless separately changed |
| Public consumers | Projection and renderer cannot emit upgraded labels in trace badges, summary, graph JSON, or retained projection |
| Protected controls | Ledger default/explicit recorded remains recorded; raw default/explicit synthetic and conceptual remain usable; raw recorded still rejects; unknown labels retain existing error behavior |
| Fabrication | Correctly recomputed self-hashes, invented issuer names, evaluator-like fields in event data, or imported APPROVE text confer no upgrade |
| Wrong scope | An authentic future receipt for another result/configuration/environment/task/trace cannot certify this projection; every claimed covered value must match |
| Stale evidence | Changed covered body/revision or policy-expired current-use proof rejects; historical display remains distinct from current qualification |
| Mixed projections | Reviewed/evaluated subset cannot upgrade synthetic, conceptual, raw, or unrelated ledger members; reject global upgrade until coverage can be represented honestly |
| Restart/replay | Reloaded ledger label behavior and event/digest identities remain stable; no evaluator, model, native owner or provider is reinvoked |
| Read-only boundary | File bytes, ledger events, authority state and source objects remain unchanged through successful and rejected requests; no append/write/dispatch interface is added |
| Illustration compatibility | Content-valid incomplete terminal illustrations remain explicitly synthetic; retain existing actor shape, stale-ID, lineage, ordering, escaping and snapshot-detachment controls |

Wrong-scope and stale-evidence bindings are future-route controls. Under the
selected current rejection route they cannot confer an upgrade at all;
adding an unused generic evidence resolver just to test them would exceed the
narrow correction.

## NAO-first coverage and remaining qualification

NAO-first is the selected integration order, not an accepted substitute for
H0/H1 synthetic exits or an H2 qualification result. The current recorded
qualifier composes typed ingress, compilation, generic admission, lease,
in-process fixture owner, acceptance and replay. Its model budget is zero;
ReadyActor, PromptCompiler and ModelInvocationAuthority are not composed in
that canary. Candidate native seam pointers are not owner-approved mappings.
O1 consumes the ledger and cannot repair missing native lineage or authenticate
raw ingress. The human also selected the authority-bound ledger-command route
for SPEC-02; DEV's separate repair remains distinct from this source audit.

| Seam | Source-inspected coverage | Remaining qualification |
| --- | --- | --- |
| Scenarios | Native fake engine has deterministic modes, ambiguity and unavailable-backend cases | Freeze native source-shaped fixtures and explicit legacy/shadow/uah comparisons; configuration alone is not a result |
| Lineage | Native ingress carries request/goal; plan and feedback carry goal/plan/version/step | Retain original request and explicit request→goal→plan/version→step join; normalizers may generate absent IDs, so supplied IDs must be frozen before normalization |
| Admission | Native orchestrator owns PlannerGate and dispatch; generic UAH gates exist | Compose actual PlannerHandoff→native gate→admitted planner request; current strict UAH parser rejects native metadata, dependencies and failure policies |
| Owner result | Native fake find_object uses target/target_kind, target_found and fake_find_object evidence; UAH fixture uses label=cup | Owner-review an adapter outside core, retain exact source result and normalized evidence, preserve fake origin; a literal detector-backed effect string proves no detector freshness or physical effect |
| Acceptance | UAH evaluator records acceptance from declared obligations | Native last-feedback completion metrics do not establish acceptance; expected clarification/failure can pass while completed=false |
| Replay | Generic ledger receipts and terminal digests replay | Retain native bodies, transform revision and full lineage; restart comparison must avoid owner/model reinvocation |
| Actor/model | Separate readiness, prompt and fake-provider tests exist | Compose that chain in a separately bounded subsequent unit; recorded JSON is not inference |
| H2 parity | Narrow recorded/fake canary exists | Frozen authority modes, disagreement report, multi-actor/report_result, failure/replan/supersede and no-duplicate-speech evidence remain open |

Primary sources:
[UAH qualifier](/home/juanbeck/universal-agentic-harness/src/ab_harness_nao/qualification.py:143),
[canary](/home/juanbeck/universal-agentic-harness/src/ab_harness_nao/smoke.py:146),
[candidate seams](/home/juanbeck/universal-agentic-harness/src/ab_harness_nao/contracts.py:27),
[native planner contracts](/home/juanbeck/nao-ros4hri-bridge/src/planner_common/planner_common/contracts.py:1834),
[fake engine](/home/juanbeck/nao-ros4hri-bridge/src/fake_skills/fake_skills/engine.py:101),
[fake find_object](/home/juanbeck/nao-ros4hri-bridge/src/fake_skills/fake_skills/skills/find_object.py:11),
[metrics summarizer](/home/juanbeck/nao-ros4hri-bridge/scripts/summarize_validation_traces.py:54).
Request ID is not present in every native payload; do not fabricate it in plan
or feedback. Preserve the ingress and provenance join instead.

Historical captures remain scoped. The May 27 report records four PASS traces,
including clarification, without duplicate utterance in those captures. June
19 metrics retain three correlated/seven uncorrelated traces, one completed,
completion rate 0.333 and median 6.152 seconds. June 17 retains two correlated/
six uncorrelated and none completed. The May 27 ambiguous raw ingress lacks
request_id and its plan contains removed fields; it is historical evidence, not
a current canonical fixture. No capture was rerun here. Sources:
[May 27 report](/home/juanbeck/nao-ros4hri-bridge/docs/traces/trace_report_2026-05-27_prompt_hardening.md:34),
[June 19 metrics](/home/juanbeck/nao-ros4hri-bridge/docs/artifacts/fake_skill_validation_metrics_20260619_022011.json:104),
[June 17 metrics](/home/juanbeck/nao-ros4hri-bridge/docs/artifacts/fake_skill_validation_metrics_20260617_001558.json:84).

The July 28 freeze review records its own test counts and software provenance.
It does not qualify current hardware effects. Promotion docs distinguish fake,
real-route dry-run and physical execution, with live checks still pending.
Current launch docs say perform_motion defaults real even for simulator
profiles. No launch is authorized by this research. Sources:
[freeze review](/home/juanbeck/nao-ros4hri-bridge/docs/artifacts/v1_freeze_commit_review_2026-07-28.md:69),
[promotion plan](/home/juanbeck/nao-ros4hri-bridge/docs/plans/fake_to_real_skill_promotion_2026-07-01.md:139),
[launch safety](/home/juanbeck/nao-ros4hri-bridge/docs/launch_profiles.md:17).

Unchanged [masterplan](../../plans/universal_agentic_harness_masterplan.md)
exits: H0 requires complete synthetic lifecycle replay (825–833); H1 requires
reconstructable success, invalid proposal, unavailable tool, timeout,
cancellation, retry exhaustion, stale evidence and false completion (878–880).
NAO-first does not substitute automatically (1622–1628). H2 retains core
prerequisites and explicit authority-mode parity (91–115, 142–173).

Smallest next proposed proof, after reviewed ingress correction: one supplied-ID
native find_object request/plan and owner-reviewed mapping outside core. Freeze
raw/normalized bodies and transform hashes. Compare valid target, malformed or
out-of-scope input, unavailable owner and ambiguity. Per case cap one environment
activation, one operation, one fake-owner call, zero retries/model/network/robot
calls and 60 seconds. Require zero shadow dispatch and identical restart lineage,
evidence, acceptance and digest without reinvocation. Actor/prompt/fake-provider
composition is subsequent work. Wider failure and H2 exits remain required.

## Finite workflow adoption proposal and instruction-gap decision

Reuse the completed accounting proposal and example JSON; do not mint another
review protocol or worker schema. The next proposed adoption unit is one section
in `docs/agents/uah_review_workflow.md` defining reviewed-body versus actual
index/commit-body equivalence, dependency drift and uncovered bytes. DEV owns
that separate docs-only unit. Preserve REVIEW.md byte identity, independent
Standards/Spec reports and verdicts, introduced regressions versus inherited
debt, incomplete-run state, unknown actual backend identity, and second-model
coverage of high-risk seams. Requested model settings are not backend attestation.

Freeze exact-before and candidate docs plus dependencies, use the existing JSON
only as a research example, and run applicable link/format/claim checks with
independent review. Controls should distinguish approved-but-uncommitted,
committed CHANGES, extra unreviewed bytes, and changed dependencies. No commit,
external tracker or runtime reviewer implementation follows from this proposal.
The previous note's unknown commit SHA remains historically true; the newly
observed commit belongs in a later accounting event, not a rewritten receipt.

No instruction edit is recommended. Guardrails already own trace/identity and
qualification boundaries; the iteration loop already requires bounded stops,
concurrent-commit refreeze and independent evidence gates; REVIEW requires every
label to be true for every covered record. ARCH-02 demonstrates implementation
nonconformance, not a measured instruction gap. A future demonstrated gap needs
one exact skill target/objective, baseline failure, train cases, independently
withheld holdouts and acceptance before a bounded SkillOpt edit. No improvement
claim, skill freshness edit or REVIEW change is delivered here.

## Inspected bytes and concurrent-dirty limits

Initial HEAD observed: `28fab5e7f2c244d86a64c371f2118017999b2387`. A later read
observed concurrent HEAD `06f5a29daef9bb877fb08b6c6ee47d870df94d71`; this pass did
not perform that Git mutation or infer operator identity from metadata.
The five current source/test/contract hashes below still matched on the lane's
later read. This was a dirty-tree inspection, not an atomic repository or
indexed-tree freeze. Relevant status
changed between reads (tests appeared staged-added in the first observation,
then untracked in the later observation). Existing staged/unstaged/untracked
changes belong to their owners and were not rewritten. A matching individual
hash proves byte equality only, not producer identity, whole-tree coherence,
review applicability after dependency drift, or release qualification.

SHA-256 observations at 18:36:07 UTC:

| Path | SHA-256 |
| --- | --- |
| `src/ab_harness/observatory.py` | `313798f6e660f913622695dd8c19d52c0ab269c71dbc6eab1e6a5472d26236fe` |
| `src/ab_harness/lifecycle.py` | `ef1cbd9d69c25735f94d14cd7df892ad97f1f0485c407f0b172d13d56e10b6d1` |
| `tests/test_observatory.py` | `491e95bf7305d0c50179bd5cf1ef94aaf87aa03994142b4b22d804815406cf92` |
| `tests/test_observatory_raw_identity.py` | `d20059458b6fe87e1e7ac8bdf0a7307aed2f26d71244009e22c861a3e6bc3b2a` |
| `docs/architecture/observatory_contract.md` | `ecb2da3a9fb2aa7f6daa18de03ea6d89be5a999e4be5924d4d90acad77526dc6` |
| October 5 original `observatory_probes.py` | `5720943e20e2ed4ebd941bbfda339798cb5a298924de3406536cf692cac4e49d` |
| October 5 independent review | `ed47f05d5655d533c0f00f04db3d9675634757d7b0bc7041d65dbab7add3c4b3` |
| October 8 O1 conformance receipt | `4295c1b6327a5a98048aa9b273680c137c5d00c84d79a9e950c41e453b839f9c` |
| October 8 O1 primary review | `8776ef2a9d440970e44d2bcccc35f0df8b12f227f8fbf43f1c4805ed708f016e` |
| October 8 O1 second review | `e058f357c1eed55d4fd7d32adb3abfc9f7bf639c92dc554a73559504d1d336eb` |
| Prior accounting/NAO-first note | `404e58757afa34ac586b5b8fd09ae57af72a0e4e1dd744d7a0293ffdb0b346e5` |

The Observatory source and raw-identity test hashes equal the reviewed O1
conformance hashes. The current lifecycle hash equals the receipt's later
integrated dependency, not its earlier isolated-review dependency. This lane
does not rerun that dependency comparison or adopt prior test outcomes as fresh
evidence. Source facts above apply to inspected bytes; DEV must refreeze the
affected sources/dependencies and obtain fresh focused review for any repair.

NAO HEAD inspected: `81b14ef1fa5fc795f46aad90f022e8fbd38e2472`; peeled v1.0.0:
`ebffe93a74be4e013ce0f60fdfc41268dba73fc3`. Qualifier, canary, seam contract and
native planner-contract hashes match the previous accounting note's observations.
Native summarizer SHA-256:
`32907e4006db1e5d52c450d6e5a02c56d6b0c159176b1d1d77902856e81edff4`;
fake engine: `11ec3e05d0032b248665d33bb5647986ae4992d768bcdd2a2efd672387de846d`;
fake find_object: `f6b2c0717815f30224d038a9abd3b49abbf25c5ec10d0946739ea1da68cb4ad0`.

## Root documentation validation

At 18:42 UTC root ran the required documentation checks after publication:

- `.venv/bin/python scripts/render_agentic_harness_docs.py --check`: passed,
  12 metadata records. This artifact is outside the canonical HTML manifest.
- `git diff --check`: passed. Because this artifact is untracked, an explicit
  file check also verified its EOF, trailing whitespace and 27 local links.
- `./scripts/run_precommit.sh`: merge-conflict, YAML, EOF, whitespace, Ruff and
  generated-doc synchronization checks passed. Source suite reported 530 passed
  and two failures in test_agent_runtime_example.py:39 and
  test_observatory.py:498. Both compare committed O1 examples against rendered
  output and differ on blank-line whitespace. The earlier research pass recorded
  the same two failures; no source/example correction was made by RESEARCH.

The hook also reported files modified during its source-test stage. DEV was
working concurrently; this is not an atomic tree check and does not attribute
those modifications to the tests or an operator. Source Observatory, lifecycle
and owning contract hashes still matched the table at the subsequent root read.
REVIEW.md SHA-256 remained
`8a1890c212e0f233eeb224d5d11a954d169228c85b949c2f072916f308fa763a`;
guardrails and iteration-loop skill hashes matched the prior pass. No skill or
REVIEW edit ran. Root made no staging/commit or other Git mutation.

These are newly executed shared-tree documentation/tooling results, not fresh
NAO, model, measurement or physical qualification. The two source-only lanes ran
no runtime probes. No independent implementation APPROVE or release gate is
issued by this handoff. The full repository suite is not green.
