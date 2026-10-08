# UAH R1: effect evidence and trace contracts

Date: 2026-10-08. Status: bounded research handoff; no normative decision accepted.

## Target contract

R1 began at approximately 14:01 UTC, separately from R0. Its evidence budget is
five external implementation/specification families across independent passes:
OpenHands SDK, LangGraph, Inspect AI, OpenTelemetry and Ollama. Official
documentation and pinned owning source supply implementation facts, not UAH
effect or lifecycle authority. UAH source and accepted ownership contracts remain
authoritative for UAH semantics. The time target is twenty minutes; R0's run and
verification are separate.

The human approved both a local Ollama server invoking a cloud model and the
personal Watson route through ZeroTier under the same UAH contract. No endpoint,
credential, entitlement, inventory or hardware readiness was inspected here.
Their current live state is `not_scored`. Per-effect freshness and trace retention
policy are pending human decisions. R1 proposes alternatives and distinguishing
fixtures without implementing runtime, prompts, skills or external services.

Harness-generated exploratory traces are the approved default source of
behavioral evidence. They can directly expose deterministic gate outcomes,
call counts, replay behavior and synthetic owner observations. They do not
automatically prove live domain effects, synchronized physical clocks or measured
configuration quality. No second writable trace store, framework authority
import or provider launch is part of R1.

## Baseline evidence

UAH HEAD remained `28fab5e7f2c244d86a64c371f2118017999b2387` at this pass's
inspection. Relevant working-tree content, including dirty content, was:

| Source | SHA-256 |
| --- | --- |
| `src/ab_harness/contracts.py` | `bacb7c0098851ffd4235000005a86dc3d519cf099ee9f9e86633f29e0419047d` |
| `src/ab_harness/lifecycle.py` | `df665eb4d8d5d815451ef99ab36145548813d0be0d5dfb5f3543b4825949b1f6` |
| `src/ab_harness/observatory.py` | `bb3d2b359fec4adeb15619abee12b86bc20734548cccfd3929ab17f9ce7cfcd0` |
| `src/ab_harness/acceptance.py` | `0d26d594f073ef1fc89061703b3149ce670ac8b3e58350d10b15e9f66961ac4a` |
| `src/ab_harness/environment.py` | `55d9a470fe9012b4225a21f6b209dac4d96611b36e3b5e9d8856eaf875b867f8` |
| `src/ab_harness/proposal_admission.py` | `8990fe6b9acbd6fca67a7185f64c7ccf2b3af5f5be5005582cb2d213e206a667` |

[R0](2026-10-08_uah_r0_exit_contracts_and_provider_routes.md) records the current
release gaps, October 5 independent defects and fake-provider test result.
That previous test run is not a new R1 verification or a passed freshness
holdout. No new freshness/control probe or defect reproduction ran in R1;
the final hook run rechecks the existing source-aware suite.

### Local contract map and missing fields

| Owning value or seam | Implemented content | Missing decision-bearing content |
| --- | --- | --- |
| [EffectEvidence](../../src/ab_harness/contracts.py#L142) | Evidence reference, object, binding, environment, owner, success, effects, arbitrary payload | No typed observation time, clock domain, validity mode, expiry, policy revision, supersession or revocation; task/run/operation lineage is outside this value |
| [EffectObligation](../../src/ab_harness/contracts.py#L156) | Effect/object/owner, required or best-effort, terminal or retryable failure | No validity rule or domain clock policy; no declared historical-receipt versus current-state meaning |
| [CompiledTask](../../src/ab_harness/task_compiler.py#L169) | Frozen task/run/trace, domain revision, interaction projection, obligations and prohibited effects | No typed effect validity contract in its obligation members; hashing existing fields cannot supply it |
| [ExecutionReceipt](../../src/ab_harness/environment.py#L83) | Content-addressed result and normalized evidence bound to lease, admission, environment run, task, trace and operation | No explicit effect observation/evaluation clock; receipt identity preserves evidence, not a freshness judgment |
| [Environment owner](../../src/ab_harness/environment.py#L417) | Checks declared observations, nonempty evidence reference, successful result with an observable; issues receipt or rejection | No typed native output validator or freshness decision; payload timestamps would be conventions rather than a common contract |
| [TaskAcceptanceEvaluator](../../src/ab_harness/acceptance.py#L12) | Matches object and owner, then success/effect; derives accepted, deficit, suspended or rejected | Receives EffectEvidence, not receipt lineage or recorded time/policy; cannot currently distinguish durable receipt from expired current-state observation |
| [Ledger evidence reduction](../../src/ab_harness/lifecycle.py#L1992) | Requires terminal operation, matching lease/result and admitted object/binding/owner; one evidence issuance | Operation lineage exists here, so standalone evaluator field gaps are not proof that complete ledger acceptance ignores lineage; effect-clock validity remains absent |
| [TypedProposal](../../src/ab_harness/proposal_admission.py#L82) | Content-addressed operation arguments and task/run/trace lineage, raw-output reference | No explicit completion claim or claim attribution; invocation/actor identity must be resolved through raw-output lineage |
| [Normalized proposal event](../../src/ab_harness/lifecycle.py#L1071) | Proposal/compiled-task/object IDs; artifact references include raw output | Does not inline arguments or full TypedProposal; artifact availability is distinct from recording a reference |
| [TraceEvent](../../src/ab_harness/lifecycle.py#L83) | Recorded time, commit/sequence, parent event, task/run/operation, artifact references and canonical data; scoped actor variant | Recorded time is ledger time, not automatically the time an effect was observed; no provider metrics semantics supplied by the envelope |
| [O1](../../src/ab_harness/observatory.py#L226) | Read-only raw event cards, actor/run/task hierarchy, explicit terminal status, failure stages | Graph event nodes omit `recorded_at` and `artifact_refs`, while raw cards retain them; no typed effect freshness/claim attribution view or complete artifact comparison |

`ProposalNormalizer` rejects model effect claims and requires its strict operation
payload shape ([source](../../src/ab_harness/proposal_admission.py#L393)). This
does not create a separately attributable completion-claim artifact. Untrusted
raw text can also remain inside a raw model output without becoming a proposal.
An explicit trace policy must decide what is retained and who can view it before
O1 expands raw provider content or context.

### Replay and clock qualifications

The ledger's `recorded_at` is captured once per commit by its clock. The event
constructor requires a nonempty string; it does not itself establish a physical
observation clock or validate every timestamp as ISO-8601. The timeout contract
does validate its relevant recorded timestamps and time zones. Ledger sequence
and parents establish recorded causal order, even when wall-clock values are
uncertain. An effect-age comparison requires additional declared clock semantics
([event and commit source](../../src/ab_harness/lifecycle.py) lines 83-170 and
589-640; [timeout source](../../src/ab_harness/runtime_controls.py) lines 470-595).

Current receipt serialization preserves native result and normalized evidence as
distinct values. The corresponding JSONL events retain IDs, effect summaries
and references, not the complete receipt/native payload. Likewise, a normalized
proposal event references the proposal/raw output without inlining arguments.
Structural replay and verified digests are implemented; those facts alone do not
prove that a fresh process can retrieve every original raw artifact. A minimal
new validity judgment must persist enough canonical observation, policy and
assessment inputs in the **existing ledger** to reconstruct that judgment.
Private diagnostics or an unresolved hash reference cannot supply missing effect
proof ([receipt event conversion](../../src/ab_harness/lifecycle.py) lines
1196-1235; [proposal conversion](../../src/ab_harness/lifecycle.py) lines 1068-1098).

The current grammar also rejects evidence issuance after rejection, rejection
after issuance and any event after terminal task judgment. A later expiry
assessment cannot be implemented by retroactively replacing an issued receipt
with `evidence_rejected`. The historical observation remains immutable; a
separate assessment can state whether it supports an obligation at its declared
assessment time. Already terminal task outcomes remain historical judgments,
not claims that the world stays unchanged forever ([reduction](../../src/ab_harness/lifecycle.py)
lines 1576-1609 and 1992-2047).

### Candidate field mapping without a new store

These are decision-bearing concepts, not approved field names or schemas:

| Concept learned or required | Existing UAH carrier | Minimal missing seam and owner |
| --- | --- | --- |
| Request/result correlation | Environment/task/trace/operation, admitted operation, execution lease, receipt/result IDs | Preserve exact owner-issued observation-to-receipt association. Do not substitute a tool-call ID, span ID or same-name effect for UAH authorization. Environment owner. |
| Retry attempt | RetryDecision source/target operations and attempt ordinal; model invocation IDs | Resolve attempts from their exact operation/invocation lineage, without a parallel attempt store or guessed correlation. Runtime/ledger. |
| Historical occurrence versus current state | EffectObligation and domain effect rule | Freeze what the evidence purports to prove and the required validity horizon in the compiled task. Domain policy, pending human choice. |
| Source observation time | Arbitrary native payload today; no common typed clock field | Typed time-or-explicit-unknown, clock identity and source provenance. Environment evidence owner; never default missing source time to capture time. |
| Capture/assessment time | TraceEvent recorded time and recorded timeout observations | Distinct recorded assessment time and basis, with clock comparison/skew proof if needed. Deterministic assessment owner. |
| Freshness disposition | Current evidence issuance/rejection and obligation outcome | An immutable validity judgment tied to observation, policy, obligation and assessment time. No fabricated native failure when evidence is stale or indeterminate. |
| Completion assertion | RawModelOutput/AgentOutput, normalized-proposal rejection | Claimant/source/scope correlation when an assertion exists; absent evidence alone is not proof of a false assertion. Attribution owner. |
| Cancellation uncertainty | Operation cancellation, task timeout and retry facts | Requested stop, owner acknowledgment, late result and uncertain effect remain separate. Task/control and native owners, pending closure policy. |
| Evidence provenance | Current projection-wide O1 data label and ledger artifact references | Preserve synthetic/native/model source and qualification evidence independently. O1 only projects; evaluator/reviewer artifacts justify stronger labels. |

O1 can show raw model output, native return, owner observation, validity at a
recorded assessment time, obligation outcome and task outcome as linked distinct
facts. It must expose unknown clock/provenance or missing artifacts rather than
fill gaps from titles, nearby events or browser wall time. A graph export that
includes existing event timestamps and artifact references would improve
inspection, but does not itself introduce freshness semantics. That change still
requires a projection/version compatibility review.

### Primary implementation comparison

Five families were selected for concrete execution, persistence, evaluation,
clock/correlation and provider contracts. The table records the inspected seam,
not a claim that every subsystem of a framework lacks UAH's semantics.

| Family | Inspection pin | Concrete observation | Authority limit |
| --- | --- | --- | --- |
| OpenHands SDK | v1.53.0, source `54daf056bd863bb46f922a2fe9324dd736b37ff6`, October 5 | Action and observation events correlate tool execution and runtime return. | An observation envelope is not a frozen UAH obligation or effect-owner grant. |
| LangGraph Python | 1.2.14, source `70dd64065bffaa3b6ab61a33f1f020fb54db8efa`, October 6 | Checkpoints and persisted task results support durable graph execution. | Reused graph state/result is not a new observation of current world state. |
| Inspect AI | Source `69ee9ba020a6ecc8c2e76a5a3265ec80d32aab02`, October 8 | Execution results, cancellation/interruptions and scorer records are distinct. | A tool result or solver-written score does not prove domain evidence or independent review. |
| OpenTelemetry specification | Source `1d77cd02d8a2f4ac7d056b3d771126f807e28cba`, October 6; live docs identify 1.61.0 | Trace correlation, span lifecycle and source-versus-observed log timestamps are distinct. | Telemetry status/collection timestamps are not task acceptance or a complete authority journal. |
| Ollama | v0.40.1, source `cf2a313a298066d572c36812e5ad30a21c0db13b` | Generation result/schema capability and cloud/local routes are distinct. | Generation completion is neither operation effect nor task completion. |

OpenHands [v1.53.0](https://github.com/OpenHands/software-agent-sdk/releases/tag/v1.53.0)
uses [ObservationEvent](https://github.com/OpenHands/software-agent-sdk/blob/54daf056bd863bb46f922a2fe9324dd736b37ff6/openhands-sdk/openhands/sdk/event/llm_convertible/observation.py)
to connect an action/tool call to its typed observation. Its
[event base](https://github.com/OpenHands/software-agent-sdk/blob/54daf056bd863bb46f922a2fe9324dd736b37ff6/openhands-sdk/openhands/sdk/event/base.py)
supplies UUID, parent and creation timestamp, with no distinct physical
observation clock in that envelope. The timestamp's default expression uses
local `datetime.now().isoformat()` without attaching a timezone. An event source
label of `environment` is not proof of domain-owner authorization. Its
[conversation state](https://github.com/OpenHands/software-agent-sdk/blob/54daf056bd863bb46f922a2fe9324dd736b37ff6/openhands-sdk/openhands/sdk/conversation/state.py)
detects unmatched actions by action/tool-call correlations, which can expose
unfinished work without claiming it failed safely. The
[terminal observation](https://github.com/OpenHands/software-agent-sdk/blob/54daf056bd863bb46f922a2fe9324dd736b37ff6/openhands-tools/openhands/tools/terminal/definition.py)
records exit/timeout/process information and documents a soft-timeout case where
the command remains running. The [interrupt/pause contract](https://github.com/OpenHands/software-agent-sdk/blob/54daf056bd863bb46f922a2fe9324dd736b37ff6/openhands-sdk/openhands/sdk/event/user_action.py)
separately describes in-flight model interruption and between-step pause. Full
native-process cancellation was not verified in R1. Its exact
[model message](https://github.com/OpenHands/software-agent-sdk/blob/54daf056bd863bb46f922a2fe9324dd736b37ff6/openhands-sdk/openhands/sdk/event/llm_convertible/message.py)
remains separate from tool observations.

LangGraph [Python 1.2.14](https://github.com/langchain-ai/langgraph/releases/tag/1.2.14)
provides [checkpoint](https://github.com/langchain-ai/langgraph/blob/70dd64065bffaa3b6ab61a33f1f020fb54db8efa/libs/checkpoint/langgraph/checkpoint/base/__init__.py)
IDs/timestamps, channel values/versions and pending writes. Its
[creation clock](https://github.com/langchain-ai/langgraph/blob/70dd64065bffaa3b6ab61a33f1f020fb54db8efa/libs/langgraph/langgraph/pregel/_checkpoint.py)
is UTC checkpoint time, not observation time. [ExecutionInfo](https://github.com/langchain-ai/langgraph/blob/70dd64065bffaa3b6ab61a33f1f020fb54db8efa/libs/langgraph/langgraph/runtime.py)
adds thread/run/task/checkpoint namespace and node-attempt metadata.
[Functional task recovery](https://github.com/langchain-ai/langgraph/blob/70dd64065bffaa3b6ab61a33f1f020fb54db8efa/libs/langgraph/langgraph/func/__init__.py)
can reuse completed results without another execution. This preserves historical
execution data, not fresh external state. Its [async retry/timeout implementation](https://github.com/langchain-ai/langgraph/blob/70dd64065bffaa3b6ab61a33f1f020fb54db8efa/libs/langgraph/langgraph/pregel/_retry.py)
cancels the guarded attempt and clears buffered graph writes; **inference:** that
does not prove an external write never occurred. Official
[time travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel)
can re-execute downstream work, and [interrupt resume](https://docs.langchain.com/oss/python/langgraph/interrupts)
restarts the interrupted node. Side effects therefore need explicit idempotency
or separation. UAH audit replay must remain distinct from executing a resumed or
branched workflow. No domain-owner freshness predicate is supplied by these
inspected checkpoint/runtime envelopes.

Inspect's pinned [ToolEvent](https://github.com/UKGovernmentBEIS/inspect_ai/blob/69ee9ba020a6ecc8c2e76a5a3265ec80d32aab02/src/inspect_ai/event/_tool.py)
stores call ID, function/arguments, result/error, completion and message/agent
correlation. Its late-result handling preserves operator cancellation while
retaining forensic result/completion data. This is useful behavior for a
stop/settlement design; it does not prove a native effect was prevented.
[ScoreEvent](https://github.com/UKGovernmentBEIS/inspect_ai/blob/69ee9ba020a6ecc8c2e76a5a3265ec80d32aab02/src/inspect_ai/event/_score.py)
separately records scorer, target, intermediate/final status and score. A score
written by a solver can lack scorer arguments, so mere presence of a passing
score is not independent evaluation. The [sample log](https://github.com/UKGovernmentBEIS/inspect_ai/blob/69ee9ba020a6ecc8c2e76a5a3265ec80d32aab02/src/inspect_ai/log/_log.py)
distinguishes dataset ID, epoch, sample-run UUID, messages, events, output and
scores. Map these explicitly to evaluation metadata, not replacement task,
operation or attempt identities.

Inspect's [BaseEvent](https://github.com/UKGovernmentBEIS/inspect_ai/blob/69ee9ba020a6ecc8c2e76a5a3265ec80d32aab02/src/inspect_ai/event/_base.py)
defaults event time to current UTC. Its [date utility](https://github.com/UKGovernmentBEIS/inspect_ai/blob/69ee9ba020a6ecc8c2e76a5a3265ec80d32aab02/src/inspect_ai/_util/dateutil.py)
normalizes aware dates and interprets naïve legacy dates as UTC. Neither
establishes physical source time or synchronization. Its
[interrupt event](https://github.com/UKGovernmentBEIS/inspect_ai/blob/69ee9ba020a6ecc8c2e76a5a3265ec80d32aab02/src/inspect_ai/event/_interrupt.py)
attributes user/limit/shutdown interruption to an event; its
[branch event](https://github.com/UKGovernmentBEIS/inspect_ai/blob/69ee9ba020a6ecc8c2e76a5a3265ec80d32aab02/src/inspect_ai/event/_branch.py)
can describe replayed execution prefixes. That execution replay differs from
UAH's model-free reconstruction. The inspected event/log schemas supply no
domain-authored expiry predicate or effect-owner attestation.

OpenTelemetry's pinned [logs model](https://github.com/open-telemetry/opentelemetry-specification/blob/1d77cd02d8a2f4ac7d056b3d771126f807e28cba/specification/logs/data-model.md)
distinguishes optional source `Timestamp` from collector `ObservedTimestamp`.
Its single-timestamp export fallback is an interoperability convention, not a
freshness rule. Preserve unknown source time rather than importing collector time
as an observation. The [tracing API](https://github.com/open-telemetry/opentelemetry-specification/blob/1d77cd02d8a2f4ac7d056b3d771126f807e28cba/specification/trace/api.md)
allows custom event times outside a span interval, gives `Ok` precedence over
`Error`, and does not end children when a parent ends. These semantics cannot
define settled UAH work or accepted effects. The [SDK](https://opentelemetry.io/docs/specs/otel/trace/sdk/#additional-span-interfaces)
explicitly places application logic outside stored span data; sampling and limits
also prevent treating an export as a complete authority journal. Trace/span IDs
and links can carry explicit UAH mappings, without conferring delegation,
decomposition or owner authority.

These implementations support separating execution observations, recorded state,
control events, evaluation and telemetry. They do **not** establish a standard
universal TTL or an accepted UAH per-effect validity policy. The historical-effect
versus current-state distinction is a UAH/domain requirement and a reasoned design
inference, not a framework feature claimed by analogy.

### Ollama facts, pinned scope and UAH implications

The latest available release shown by the owning repository on October 8 was
[v0.40.1](https://github.com/ollama/ollama/releases/tag/v0.40.1), with source commit
[`cf2a313a298066d572c36812e5ad30a21c0db13b`](https://github.com/ollama/ollama/commit/cf2a313a298066d572c36812e5ad30a21c0db13b).
This is an available upstream version, not an observed installed version.
Documentation is a live snapshot accessed October 8; the tagged source supplies
an explicit inspection pin.

Ollama's [structured-output documentation](https://docs.ollama.com/capabilities/structured-outputs)
still explicitly excludes cloud structured outputs. For supported local
generation, it accepts a JSON Schema through `format`, recommends including the
schema in the prompt, and demonstrates client validation. Schema transport is a
conditional provider capability. It does not supply UAH admission or evidence.
The approved cloud route therefore remains usable as an experimental proposal
producer with deterministic parsing and validation, without claiming native
schema enforcement.

That experiment still needs a role/configuration whose declared requirements
permit absent provider-side schema enforcement. The existing synthetic example's
`structured_output` requirement must not be satisfied by relabeling plain JSON
generation. Distinguish a harness validation guarantee from provider capability
before qualification; no configuration was changed here.

The [authentication contract](https://docs.ollama.com/api/authentication)
distinguishes unauthenticated loopback API access from a signed-in server's
delegated cloud access. Direct hosted calls require a bearer API key. Local HTTP
transport does not mean local inference or local task-data processing. R1 did
not sign in, inspect account state or select a hosted model. Keys remain external
to immutable UAH artifacts and logs.

The [chat API](https://docs.ollama.com/api/chat) requires `model` and `messages`,
defaults to streaming, and exposes final content plus model, completion reason
and timing/token metrics. Explicit `stream:false` is appropriate for the current
synchronous ProviderPort candidate. Provider-reported completion is completion
of generation. It is not a completed UAH task or observed environment effect.
Keep reasoning, final content and transport failure distinct; empty final content
does not justify substituting reasoning text as an operation.

At [the pinned source](https://github.com/ollama/ollama/blob/cf2a313a298066d572c36812e5ad30a21c0db13b/server/routes.go),
the Generate handler has an explicit cloud-proxy branch and a separate local
generation branch passing `Format` to the runner. This corroborates the runtime
distinction; it is not a proof of installed chat behavior, supported full JSON
Schema features or acknowledged cancellation through the selected route. R1
does not infer cloud schema support from the local request type's `format` field.

## Approach registry

| ID | Mechanism and assumption | Owner | Discriminating probe | Observed evidence | Status and exact gap |
| --- | --- | --- | --- | --- | --- |
| E1 | Per-effect domain validity distinguishes exact-operation durable receipts from expiring current-state observations | Domain effect contract, environment evidence owner and acceptance | Same recorded receipt evaluated at two later clock observations under frozen per-effect rules | Current obligations/evidence have no validity rule; domain ownership established in R0 | candidate; human policy choice, clock basis and supersession remain pending |
| E2 | Every effect has finite TTL, including historical operation receipts | Same owners | A completed note write crosses its TTL before acceptance despite no change to its historical truth | Current evaluator cannot express this distinction | candidate; human has not accepted universal expiry or refresh meaning |
| T1 | Inline bounded canonical observation/assessment inputs in the existing ledger, then read-only O1 projection | Ledger, domain/evidence owners and deployment privacy policy | Restart reproduces the exact assessment; credential sentinel is excluded before persistence under explicit policy | Current ledger supports canonical data but not typed effect assessment | candidate; new fact grammar, bounds/access and compatibility contract pending; no second store |
| T2 | Versioned receipt/evidence contract carries typed observation and assessment input, serialized through the same ledger with explicit redaction provenance | Same owners and transformation owner | Nested mutation, missing original input and redaction must not change the claimed judgment invisibly | Current receipt serialization and event summaries differ | candidate; version migration and replay-sufficient fields pending; hidden/private diagnostics remain non-authoritative |
| O1 | Cloud model through approved local Ollama, prompted operation schema, mandatory deterministic validation | External provider adapter, compiler and admission owners | Recorded cloud-shaped completion passes parse/schema gate but fails wrong owner/prohibited effect gate | Official cloud schema limitation; existing UAH compiler carries schema | candidate; live capability `not_scored`, deterministic gate composition and repair outstanding |
| O2 | Native schema transport when a provider/model has qualified support, followed by the same validation | Same owners | Supported schema case plus unsupported `oneOf`/truncated output fixtures | Ollama local structured output documented, no cloud support | candidate; model/runtime schema subset unqualified |
| O3 | Require native schema enforcement for all providers | Deployment provider policy and role owner | Exclude approved cloud route; test whether that exclusion is intended | Current cloud limitation conflicts with approved experiment scope if treated as universal requirement | rejected as an inferred requirement; only an explicit human policy could impose it |

### Two decision-ready format strategies

Freshness **semantics** E1/E2 and trace **representation** F1/F2 are separate
decisions. An expiry value is meaningless until the owner states what is being
proved and when it must hold.

| Route | Minimal representation | Benefit, assumption and exact cost |
| --- | --- | --- |
| F1, leading minimal candidate | Keep existing historical receipt identities; append typed owner-observation and deterministic assessment facts in the common ledger. Assessment pins observation/receipt, compiled obligation/policy, recorded clock, disposition and reason. | Makes unknown time, reassessment and cancellation uncertainty inspectable without rewriting prior issuance. Requires closed fact/reduction rules and replay-sufficient canonical inputs, not a new writable store. |
| F2, versioned contract candidate | Introduce new evidence/receipt and compiled-obligation schemas containing typed observation/validity inputs; record a complete assessment atomically with obligation judgment in the same ledger. | Strong nested schema validation and a compact judgment commit. More migration work across owner adapters, compiler, acceptance, digests and O1; old versions must keep original bytes and semantics. |

Both require a domain-reviewed policy frozen by compilation, authentic owner
provenance and recorded assessment input. An owner-issued assessment (FR-A in
R0) remains a possible evaluator implementation where a generic predicate cannot
express domain validity; its attested inputs/rule must remain auditable. The
frameworks do not choose this ownership implementation for UAH.

Do not bump `TraceEvent` merely because a new typed fact carries more fields.
The existing envelope already carries lineage, canonical data and references;
a new event family may suffice. If explicit assessment IDs or extra fields are
added to receipt, compiled task, digest or projection schemas, their version and
byte-compatibility contracts need review. Existing v1/v2 records must not acquire
invented observation times, default TTLs or retrospective qualification. Test old
serialized IDs before introducing defaults that change nested `asdict` content.

Trace privacy is orthogonal to effect validity. Persist bounded replay-sufficient
typed inputs in the ledger; expose only authorized projections. If redaction
changes data, preserve explicit transformation provenance and freeze identity
after the allowed transformation. A hidden original or hashed diagnostic is not
an alternative evidence source. Exported framework/telemetry views are read-only
derivatives and must not become a second authority journal.

### Exploratory traces as the default evidence source

Use the approved synthetic-notes environment to generate most early conformance
evidence: actual fixture-owner mutation/inspection, exact invocation count,
negative gate behavior, control facts and restart-equivalent judgments. Keep the
origin visibly synthetic and the experiment exploratory until a frozen evaluator
and evidence manifest establish a specific stronger claim. A passing scorer,
persisted ledger or framework `source=environment` label cannot independently
upgrade the trace to measured or reviewed.

O1's current single projection label does not fully describe mixed provenance.
A real cloud invocation inside a synthetic environment has provider transport
evidence and synthetic environment-effect evidence; neither proves robot parity.
A future projection should expose source origin and qualification evidence as
distinct concepts, without inferring either or creating new writable state.
The October 5 measured/reviewed-label defect remains a DEV prerequisite.

## Discriminating probes and results

The static source map establishes missing typed validity and the distinction
between receipt lineage, effect observation and ledger recording. It does not
establish a passed implementation repair. The official Ollama refresh confirms
cloud schema limits and supplies an available upstream pin. Endpoint readiness,
generation, schema subset, cancellation and account entitlement remain
`not_scored`.

The following fixture-input specification is frozen in this note before runtime
implementation. These are proposed tests, not executed traces. Each run uses
`synthetic_notes`, a temporary owner-managed note store, exact compiled task and
one operation/attempt lineage. A current-content effect is a proposed separate
owner-reviewed effect rule in that frame, not an existing `note_written` meaning
or a new general-purpose frame. Fixture clock C0 is explicitly synthetic UTC,
`T0 = 2026-10-08T14:00:00Z`. A ten-second horizon is a discriminating fixture
parameter, not a recommended global TTL.

| Split / ID | Frozen input or perturbation | Discriminating expected observation |
| --- | --- | --- |
| Train T01 | At T0, one fake invocation proposes the approved write; owner commits text X and independently reads it; receipt and judgment persist. | Valid scoped success and exact call count, no acceptance from provider text alone. |
| Train T02 | Same completed invocation ID and unchanged prompt after file-backed reload. | Return recorded output, no second provider call; preserve original assessment/digest rather than re-observe the world. |
| Train T03 | Owner reports terminal required-effect failure with no invented success observation. | Existing required/best-effort semantics remain visible; failure and native result retain attribution. |
| Negative N01 | Well-formed JSON with wrong object, missing/extra argument, prohibited effect or raw model “done” without a qualifying receipt. | Strict proposal/admission rejection or unsupported-claim attribution; never terminal effect success merely from schema-valid text. |
| Negative N02 | Plausible receipt from another task, operation/attempt, environment activation or owner; changed binding/schema content under old identity. | Fail closed on exact lineage/authority/content, even if the effect name matches. |
| Negative N03 | No source time; naïve time; unknown clock; future observation T0+30 at assessment T0; old observation T0 captured at T0+100. | Preserve distinct unknown/future/old inputs; no default “fresh now.” Disposition/skew follows the selected frozen domain rule. |
| Negative N04 | Expiring observation assessed at T0+10, then T0+10.000001. | Expose the chosen inclusive/exclusive boundary; do not borrow timeout's existing `>` convention without a decision. |
| Negative N05 | Owner write occurs, then timeout/cancel before receipt; delayed native/model result later arrives. | Preserve requested stop, settlement and uncertain effect separately. Do not infer that a timeout prevented the write or permits an unbounded safe retry. |
| Negative N06 | OTel parent ends while child work runs, status is Ok after Error, or telemetry event time is outside its span. | Telemetry conventions cannot bypass UAH settlement, validity or task-acceptance rules. |
| Negative N07 | Synthetic event collection has a solver-authored passing score; caller asks for measured/reviewed label. | Preserve synthetic/exploratory origin unless independent qualification evidence satisfies its own gate. |
| Holdout H01 | After T01, change/delete the note before assessment; assess same historical receipt much later. | Distinguish historical committed occurrence from current-content proof and E1 versus E2. Pending semantics determine the expected outcome. |
| Holdout H02 | Replay frozen judgment under a current clock in year 2099; reorder import/capture clocks but keep recorded sequence and assessment. | Identical recorded judgment/digest; no wall-time revalidation or recapture-induced freshness. |
| Holdout H03 | Different explicitly owner-reviewed effect with a remote clock of unknown offset. | No assumed cross-clock comparability; policy may block/seek evidence rather than invent synchronization. |
| Holdout H04 | Cloud-shaped non-schema response versus schema-capable Watson-shaped response, both recorded fixtures; include truncated and valid-but-wrong output. | Same mandatory deterministic gates; optional transport constraints do not authorize effects or silent repair. No live provider needed. |

Freeze semantic expected outcomes after the human chooses the proof contract,
then implement the train cases without optimizing against held-out cases. A
passing source inspection is not a training result. **No new train, negative or
holdout run passed in R1; no runtime fix was implemented.**

## Adversarial audit

The contribution does not equate provider completion with task acceptance,
loopback with local inference, schema capability with semantic permission or
ledger time with effect observation. It distinguishes missing fields from
demonstrated bypasses and preserves the October 5 review's repair ownership.
Neither freshness nor trace policy is silently selected. No runtime or prompt
mutation was made. The wording iteration uses current source as baseline,
explicit missing-field claims as the mutation, and receipt lineage/provider
cloud scope as adversarial holdouts. This accepts an evidence report only; it
does not accept a new contract or observed implementation gate.

## Decision: accept, reject, or bounded handoff

Decision: **bounded handoff**. The primary implementations provide useful action
correlation, persisted execution, cancellation/late-result separation and clock
vocabulary. They do not resolve UAH's domain validity choice. No freshness or
trace schema is accepted, and H0/H1 remain open.

Two decision-ready semantic alternatives remain:

| Alternative | Consequence and recommendation |
| --- | --- |
| E1, per-effect proof contract | Domain declares historical occurrence or current-state meaning, frozen in the compiled obligation. Historical write evidence need not expire merely with elapsed time; current-state evidence needs explicit validity/re-observation rules. Leading recommendation because it preserves both meanings without substituting one for the other. Exact boundary, clocks, skew and terminal disposition remain pending. |
| E2, finite validity for every evidence item | Require a domain-authored finite horizon even for historical receipts, then explicit owner revalidation when it expires. More uniform age mechanics but requires defining what refreshing a historical fact means. Refresh must not repeat the native mutation merely to renew evidence. No global horizon has been accepted. |

**One next GRILL question:** For the first synthetic `write_note` task, should
acceptance prove that the owner confirmed the requested write occurred, or that
the note still has the requested content when the task closes?

Recommendation: the historical-write contract for this initial run. It matches
the existing `note_written` declaration and isolates ingress, invocation,
admission, native execution, evidence and replay without importing an undeclared
current-state promise. A later current-content requirement needs a separate
owner-reviewed effect/observation and the recorded-time validity matrix. This is
a recommendation to the human, not an accepted per-effect policy.

After that answer, choose F1 versus F2 representation and freeze exact temporal
expectations before DEV implementation. F1 leads for a narrow additive seam;
F2 remains credible where a versioned owner-result contract is already needed.
Both use the current ledger and read-only Observatory. Retention/redaction and
approval/control closure still need their own decisions.

For both approved providers, recommend optional qualified native schema transport
with mandatory deterministic UAH validation. The cloud route must not claim
native schema support. Freeze exact request/output identity and parsing failure
provenance before a composed synthetic run. Provider setup remains secondary.

## Residual risk and next probe

The next implementation probe is DEV's repaired authority path composed through
synthetic notes, after the human selects its proof contract. Use T01-T03 and the
frozen negative/holdout specification. Recorded provider fixtures can isolate
cloud schema absence from UAH output validation without a live request. Do not
resolve missing owner observation/clock facts with telemetry defaults.

Current live entitlement/quota, selected cloud model, active Watson route/build,
hardware capacity, actual schema behavior, clock synchronization, acknowledged
upstream/native cancellation and NAO parity remain `not_scored`. Framework
persistence cannot prove their state. Source inspection did not verify all
framework extensions or native cancellation implementations; the conclusions
are limited to the pinned seams cited above.

### Final validation and run boundary

R1 concluded at approximately 14:15 UTC after a 14:01 UTC start, within its
twenty-minute target. Its only repository content change is this note. It
introduces no runtime, prompt, skill, provider or normative contract mutation.
R0's documented development-tool setup was reused with no additional dependency
installation. `./scripts/run_precommit.sh`, explicit `pre_commit run --files`
covering both new research notes, the direct paired-document renderer `--check`
and `git diff --check` passed. No HTML companion is required for these research
notes outside the canonical render manifest. Hook success is not a passed new
freshness/trace holdout or a release decision.

HEAD remained `28fab5e7f2c244d86a64c371f2118017999b2387`. At 14:14:28 UTC,
the end audit found concurrent DEV drift in three inspected paths:

| Path | Final SHA-256 |
| --- | --- |
| `src/ab_harness/domain_contracts.py` | `b47e522c1184786170df1d9f3bbbfb7398c340e44a7b44a514312a8da17baf1c` |
| `src/ab_harness/task_compiler.py` | `b11625e4cb5a64f74327e2112a6e182b48e45ce9821135a5af39a9f36f92e9bf` |
| `docs/plans/universal_agentic_harness_masterplan.md` | `7aaa9987a21b8bd50d63cb2b05c517b015d49ea0dafeaae7afb6459e2095f108` |

The other eight root-audited source/governing-document hashes remained unchanged.
The research claims concern the frozen inspected content and cited external pins;
R1 does not independently certify newly written DEV repairs. No current
implementation or release status should be inferred solely from the historical
R0 defect table. Concurrent changes and artifacts were preserved.
