# UAH R0: exit contracts and provider routes

Date: 2026-10-08. Status: bounded research handoff, not an architecture decision.

## Target contract

R0 supplies decision-ready alternatives for remaining H0/H1 contracts and a
minimal provider integration. The investigation budget is approximately twenty
minutes. Source and tests establish implemented behavior; accepted architecture
establishes intended ownership; historical endpoint reports establish only the
facts observed on their recorded dates. Current live provider state is
`not_scored`.

Models remain proposal producers. `ModelInvocationAuthority` owns recorded model
admission and model-call debit; `PromptCompiler` owns task-scoped presentation;
provider adapters own HTTP translation and external configuration. Semantic
admission, domain leases, environment execution, effect evidence and task
acceptance retain their existing owners. No runtime, skill, service or credential
change is part of R0. No provider was invoked or model launched.

The immediate priority is H0/H1 clearance. Jev, learned trace search, dynamic
allocation and live NAO coupling are outside this gate. The proposed freshness
choice currently awaiting the human in GRILL is **domain-declared per-effect
validity, including durable exact-task/operation historical receipts, versus
finite expiry for every effect**. R0 does not record either alternative as an
accepted decision. September's accepted ownership decision already assigns
effect contracts and freshness policy to the domain; representation, time basis
and evaluation semantics remain unresolved.

Later human steering approved **both** a local Ollama server using a cloud model
and the personal Watson model reached through ZeroTier, under the same
provider-neutral UAH contract. Synthetic environments/runs are approved for
fault isolation, with `synthetic_notes` preferred. This approves experiment scope,
not endpoint readiness, cloud schema capability, the per-effect policy or a
runtime implementation. Provider setup remains secondary to H0/H1 repairs.

## Baseline evidence

The provider pass observed UAH HEAD
`28fab5e7f2c244d86a64c371f2118017999b2387`, NAO HEAD
`81b14ef1fa5fc795f46aad90f022e8fbd38e2472`, and ZeroTier proxy HEAD
`6973e9080a0539c910104764a59e2b852b714a81`. UAH has extensive tracked and untracked
dirty content. These identities do not describe the full working tree. Relevant
content hashes at inspection were:

| File | SHA-256 |
| --- | --- |
| `src/ab_harness/model_invocation.py` | `1d26890f50a5a9c325a08a71325eff4dec5c35165a043796c7ea636475d067a5` |
| `src/ab_harness/prompt_compiler.py` | `c76d829b9e6b9e04c6856fcb35ce6f61e26953f881a27cdd3ef79e1016a34b82` |
| `src/ab_harness/agent_configuration.py` | `52e8954f458405ac11414a20003a04044e0756f279416e5b9c287aa1a7e3ab32` |
| `tests/test_model_invocation.py` | `554c5ff8177ea41d6ba9f3603740c90efd7ece273b25c15b5ec76692fb63da71` |
| `tests/test_prompt_compiler.py` | `53b19f5e5d9d8c05d5b328034b54874d58e6e35924aa7b543e672d55f47eb183` |
| NAO `planner_llm/providers.py` | `7a7fb9d43f00461ae7a4a7d3b51485397b91c7505423987150d7e2ec1aff0ff0` |
| ZeroTier `codex_watson_router.py` | `1def1d1e33ffe30f38c3fd8ff0409f0c76a7425eff1d2bb3094b9a7045a30d76` |
| ZeroTier `lucebox_dflash_proxy.py` | `a2106f2b21ad2798d26e78bf6920381bb2afd9d9d9db788d24584a28387306e9` |
| ZeroTier `verify_watson_endpoint.py` | `8dec9e4d2c0342a69415fbb21a8440a099e8a6a1395e5b87b91b05cbba293741` |

The provider-focused command
`.venv/bin/python -m pytest -q tests/test_model_invocation.py tests/test_prompt_compiler.py`
passed 37 tests. It used fake providers and did not contact endpoints. The
[October 5 review](../artifacts/reviews/2026-10-05_uah_h0_h1_independent_review.md)
and its [captured scope](../artifacts/reviews/2026-10-05_uah_h0_h1_review_scope.md)
remain the baseline for independent defects. Passing provider tests does not
resolve those defects.

The root inspection started at 13:46:46 UTC. It found 37 tracked modified paths,
29 untracked paths and no staged changes before this note. The independent exit
and owner-contract passes inspected source without rerunning the October 5
counterexamples. DEV separately owns their reproduction and repair. Relevant
additional frozen hashes were:

| File | SHA-256 |
| --- | --- |
| `docs/plans/universal_agentic_harness_masterplan.md` | `3184b914ffdddfa173e19bcf198b427a46906344de72287ece87632a17bafc53` |
| `docs/architecture/universal_agentic_harness_foundation.md` | `92afbdcd341e7ef9f601123308196acd16c9e83e397ef7dd564f4a9f1dd3e8cc` |
| `docs/architecture/observatory_contract.md` | `a3278fdae131a31e33a98d408b02bebf05437ffe46ce5ad48f2a36f5a8aa593e` |
| `docs/plans/universal_agentic_harness_development_log.md` | `f055d84add885cb42cc41925adba5a4d5846e9030b1107ea222e28d27ddad3b8` |
| `src/ab_harness/lifecycle.py` | `df665eb4d8d5d815451ef99ab36145548813d0be0d5dfb5f3543b4825949b1f6` |
| `src/ab_harness/task_compiler.py` | `980619769fb323a7b8b810ee9befd4b905008a57c88d0730c0bbb7adc891a369` |
| `src/ab_harness/proposal_admission.py` | `8990fe6b9acbd6fca67a7185f64c7ccf2b3af5f5be5005582cb2d213e206a667` |
| `src/ab_harness/domain_contracts.py` | `566809c92677c9460b3bfb417d4dc4c0261fa26387be743ad1951659136691db` |
| `src/ab_harness/contracts.py` | `bacb7c0098851ffd4235000005a86dc3d519cf099ee9f9e86633f29e0419047d` |
| `src/ab_harness/acceptance.py` | `0d26d594f073ef1fc89061703b3149ce670ac8b3e58350d10b15e9f66961ac4a` |
| `src/ab_harness/environment.py` | `55d9a470fe9012b4225a21f6b209dac4d96611b36e3b5e9d8856eaf875b867f8` |
| `src/ab_harness/runtime_controls.py` | `ddf5a85a0722606ddb1e6622f74dbfbaba7eea112f74322600be4c797fea6aa7` |
| `tests/test_two_stage_admission.py` | `1b0861e6a2d86537d888a7deac0bc1bcd6abc63606cb16f3d2979ffd0e3c3f7e` |
| `scripts/render_agent_runtime_example.py` | `43bdefe91a6d21a70d04e7fa16f446e641af865e760919c3fb95d4d7c93b9320` (end audit of existing untracked fixture) |

### Exit criteria, implementation defects and deferred work

The [canonical masterplan](../plans/universal_agentic_harness_masterplan.md)
sections 6 and 16 own the release gate. Its H0 acceptance requires current H0
tests, schema round-trip/version tests, fail-closed permission/evidence tests,
one complete synthetic lifecycle replay and a portable core. Its H1 acceptance
requires a frozen synthetic suite covering success, invalid proposal, unavailable
tool, timeout, cancellation, retry exhaustion, stale evidence and false
completion, with every case reconstructable from events. Neither gate says a
robot is required.

The complete deliverables are broader than those short acceptance sentences.
Do not silently replace them with the smaller implemented subset:

| Obligation and owner | Observed evidence | Exact remaining gap and classification |
| --- | --- | --- |
| Versioned H0 configuration/envelopes, contract owners | TaskSpec/CompiledTask v2 and several identity families serialize | EnvironmentProfile is explicitly nonserializable/non-content-addressed in CONTEXT; strict standalone TaskSpec and ingress/decision reload coverage is incomplete. HarnessSpec/ModelProfile terminology needs an accepted replacement mapping, not an assumed equivalence with role/model configuration. Unimplemented deliverable. |
| Complete AB object/permission/schema contract, registry and semantic admission | Object reach, role output, approved binding, finite arguments and reviewed top-level input types are checked | Native output schema resolution, canonical-alias policy, typed freshness, side-effect/permission vocabulary and full inspect/propose/direct/execute/claim authority contract are not established by the current fields. Unimplemented deliverables. |
| Effect validity and false-completion attribution, domain/evidence/acceptance owners | Receipts preserve result/evidence separately; evaluator derives required/best-effort outcomes | No typed effect clock/validity rule or attributable completion-claim contract. Missing H0 evidence semantics and H1 negative cases. |
| Task control closure, runtime controls and task acceptance | Tool/model-call debit is atomic; cancellation, timeout and retry facts replay | Controls intentionally do not independently terminate tasks; in-flight stop/settlement and approved retry continuation are open. Declared H1 gap, not a newly demonstrated bug. |
| Durable bounded context, context adapter and agent-run owners | Activation, profile, manifest, leases and standby reconstruct after restart | No durable context snapshot selection/persistence contract or compiler input; logical actor continuity is not conversation continuity. H1 gap. |
| Approval/policy and resource accounting, deployment/runtime owners | Fixed role/model declarations and wall/model/tool/retry bounds | Human approval/intervention events and token/cost accounting are absent. H1 deliverables remain open even if a free provider is selected. |
| Strict transport output and runnable loop, external adapter and kernel owners | Fake-provider invocation is tested; normalization/admission and owner execution have separate fixtures | Local/OpenAI-compatible adapter, parse/repair provenance and one composed invocation-to-owner-evidence synthetic run are not established. H1 implementation/conformance gap. |
| O1 read-only evidence surface, Observatory | Static hierarchy, explicit actor cards, controls and operation edges exist | Complete configuration/artifact comparison and stale/false-completion views are incomplete. Full O1 exit also asks for H2 planner parity; distinguish an intermediate H1 inspection milestone. |

Sources: [CONTEXT](../../CONTEXT.md), especially EnvironmentProfile, agent-run,
effect-obligation and lifecycle definitions; [contracts](../../src/ab_harness/contracts.py)
lines 49-75 and 132-184; [schema validation](../../src/ab_harness/schema_validation.py);
[acceptance](../../src/ab_harness/acceptance.py);
[environment](../../src/ab_harness/environment.py) lines 417-524;
[control tests](../../tests/test_two_stage_admission.py) lines 1739-1950;
[O1 contract](../architecture/observatory_contract.md) sections 4 and 7.

The October 5 review has nine BLOCKING observations but seven distinct defect
categories. These need fixes under already accepted contracts, not new permission
to weaken them:

| Distinct defect | Review IDs | Owning seam and required valid control |
| --- | --- | --- |
| Changed/nested domain policy under issued revision | STD-01 / SPEC-01 | Compiler reverifies covered pack content while an unchanged legitimate pack still compiles. |
| Raw caller-authored start authorizes compilation after reload | SPEC-02 | Ingress/common-ledger ownership enforces admitted provenance; legitimate start/resume/notify still replay. |
| Execution catalog contradicts compiled object semantics | SPEC-03 | Semantic admission fences semantic drift separately from replaceable binding identity; a legitimate approved binding still executes. |
| Returned in-memory events alter authority and O1 status | STD-03 / SPEC-04 | Ledger read/reduction boundary preserves verified content; valid in-memory/file-backed budget and O1 paths agree. |
| Prompt exposes operation rejected by static semantic policy | ARCH-01 | PromptCompiler presents semantic-owned eligibility, including prohibited observable effects; valid choices remain available. |
| Unsupported measured/reviewed labels | ARCH-02 | O1 rejects or explicitly downgrades unsupported provenance; genuine recorded input stays inspectable. |
| Untested outgoing commit passes working-tree cache | STD-02 | Tooling gate binds tested outgoing content; no CI bypass was demonstrated. |

Historical rewriting, HTML-only hook coverage and inaccurate budget wording are
the review's three NIT findings. The full finding, source references and saved
probe are in the [review](../artifacts/reviews/2026-10-05_uah_h0_h1_independent_review.md)
and [reproduction README](../artifacts/reviews/2026-10-05_uah_review_repros/README.md).
R0 does not duplicate DEV's reproductions or mark these defects repaired.

Two documentation conflicts require explicit reconciliation. The September 30
[seam note](uah_h0_h1_seam_deepening.md) describes the authority chain as sound
and freshness/false completion as the remaining H0 work. October 5 counterexamples
invalidate that current-state assumption. The architecture is still the intended
contract, while those implementation claims are historical evidence. The
masterplan permits recorded/fake core and H2 qualification without model assets;
the [foundation](../architecture/universal_agentic_harness_foundation.md) calls
live leased invocation the next target. A live request is therefore a separate
qualification target, not a universal prerequisite for synthetic H0/H1 closure.
The local/OpenAI-compatible adapter deliverable still needs implementation and
recorded conformance evidence.

H2 separately owns NAO `report_result` correction, cross-frame delegation and
legacy/uah/shadow planner parity. Dynamic pools, eviction, handle rebinding and
learned retrieval are H3; crystallization/promotion is H4; federation is H5.
Jev is an optional future candidate producer, not a prerequisite. These boundaries
follow [ADR 0001](../architecture/decisions/0001-semantic-objects-and-shadow-first-bindings.md)
and the masterplan. No H1 or H2 closure is claimed.

### Smallest complete synthetic run

Reuse the existing `synthetic_notes` frame and its reviewed declaration pattern
in [render_agent_runtime_example.py](../../scripts/render_agent_runtime_example.py),
not a new general-purpose frame and not NAO's semantic ownership. It has one AB1
object, `write_note`, a notes owner, an explicit `note_written` effect, a request
ingress rule, task compilation, actor attachment, a fixed lease and a synthetic
provider. Its source stops after invocation/release and a second actor's startup
failure. [The corresponding test](../../tests/test_agent_runtime_example.py)
explicitly asserts there is no semantic admission, domain lease, execution,
evidence or terminal acceptance and that its task remains open.

The candidate complete run is one task with one required historical effect:

```text
attested synthetic_notes environment + attached notes actor
  -> admitted request ingress -> frozen CompiledTask
  -> reviewed prompt -> exact ready model lease -> one fake invocation
  -> strict proposal-envelope parsing -> ProposalNormalizer
  -> SemanticAdmission -> DomainLifecycleAdmission -> ExecutionLease
  -> notes owner executes against a temporary in-memory note store
  -> separate validated native result + owner-issued receipt/evidence
  -> deterministic validity/obligation judgment -> explicit task outcome
  -> file-backed reload -> same verified trace digest
```

The fixture's notes owner must actually apply and independently inspect the
temporary mutation before issuing `note_written`; a provider string saying it
wrote a note is insufficient. Mount the existing fake binding and input schema,
reuse public owner/acceptance mechanisms demonstrated by
[two-stage admission tests](../../tests/test_two_stage_admission.py) lines
364-394 and 1295-1345, and start the task through `TaskIngressAuthority`.
Do not copy those tests' raw `TaskStartedFact` shortcut into the new runner: it
is precisely the ingress crossing under review. Reconstruct `AgentOutput` only
from the exact recorded raw artifact under a pinned parser policy; a naked
artifact-ID string does not itself prove that parsed values came from it.

Protect success with negative runs: forbidden operation/arguments cause no
mutation, unavailable binding produces a typed nonterminal failure, successful
native result without required observable cannot close accepted, and stale or
unsupported evidence follows the newly selected validity policy. Timeout,
cancellation, exhaustion and false-completion terminal cases follow GRILL's
contracts, not ad hoc runner inference. No model download or live request is
needed for this deterministic proof. Replacing only the fake port with a
qualified external adapter is a later provider-mediated synthetic run; it still
does not qualify NAO parity or real hardware.

### Implemented provider boundary

`ProviderPort.invoke(request) -> object` is synchronous and contains no timeout,
cancellation, streaming, retry, readiness or inventory method
([source](../../src/ab_harness/model_invocation.py#L302)). The authority verifies
the exact ready actor, lease and recorded task, then atomically records debit and
invocation start before calling the port. Completion captures finite canonical
JSON; it does not validate that JSON against the compiled output schema. Failure
records an exception class and a hashed diagnostic, without exception text.
Completed IDs replay without reinvocation; an unfinished ID refuses automatic
retry ([authority](../../src/ab_harness/model_invocation.py#L343),
[tests](../../tests/test_model_invocation.py#L422)).

An expired lease blocks new calls, but a response arriving after lease expiry is
recorded. `KeyboardInterrupt` leaves an outstanding invocation because the
authority catches `Exception`, not `BaseException`. Task suspension cannot settle
an invocation. These are tested behaviors, not evidence of provider abort or
task-level cancellation ([tests](../../tests/test_model_invocation.py#L561)).

The compiler emits two messages, one system and one user, and a JSON Schema whose
`oneOf` branches fix `object_id`, allowed `output_type`, required arguments and
additional-property policy. It pins reviewed binding fingerprints and argument
schema identities. The adapter should transmit this presentation unchanged or
record an explicit transport transformation; model-family prompt mutation after
compilation would create unrecorded presentation drift
([compiler](../../src/ab_harness/prompt_compiler.py#L298)).

`ModelConfiguration` already records provider kind, opaque endpoint reference,
model artifact/revision, capabilities, context limit and finite scalar decoding
settings. It does not carry URLs or credentials. The request carries the lease's
configuration identity rather than a resolved configuration. A provider therefore
needs an exact configuration lookup and deployment-owned endpoint resolution,
with mismatch rejection rather than mutable default-model selection
([source](../../src/ab_harness/agent_configuration.py#L181)).

### Existing owner implementations

The NAO [planner transports](/home/juanbeck/nao-ros4hri-bridge/src/planner_llm/planner_llm/providers.py)
offer native Ollama `/api/chat` and OpenAI-compatible `/v1/chat/completions` using
`urllib`. They return assistant content as a string, do not pass the UAH compiled
schema, and do not implement `ProviderPort`. Native Ollama forces nonstreaming;
the compatible route relies on its server default. Native Ollama adds a Qwen
no-thinking prefix and can substitute thinking text when final content is empty.
These choices are planner behavior, not an accepted portable UAH transport policy.
The socket timeout is not a separately enforced overall invocation deadline.
There is no explicit retry loop or cancellation handle. Importing this module
into `src/ab_harness` would violate the package boundary.

ZeroTier is the overlay transport, not an inference implementation or readiness
owner. Its protocol provides virtual networking and endpoint authentication,
with documented transport-security qualifications. It does not determine which
model or upstream an HTTP proxy serves
([official protocol](https://docs.zerotier.com/protocol/)).
The relevant owning repository is
[/home/juanbeck/zerotier-llm-proxy](/home/juanbeck/zerotier-llm-proxy).
Its [September 3 repair report](/home/juanbeck/zerotier-llm-proxy/docs/reports/watson-qwen38-endpoint-repair-2026-09-03.md)
reports functioning llama.cpp, LiteLLM and Headroom routes. Its
[September 12 integration report](/home/juanbeck/zerotier-llm-proxy/docs/reports/codex-local-model-integration-2026-09-12.md)
reports successful Codex routing and a separate Windows Ollama inference failure.
Those newer historical observations supersede the July offline diagnosis for
historical status, but do not establish October connectivity or UAH qualification.

The proxy source exposes materially different routes. The
[Codex router](/home/juanbeck/zerotier-llm-proxy/scripts/windows/codex_watson_router.py#L76)
forwards streaming bytes and strips authorization, account and cookie headers
from its local route; its HTTP client has no timeout. The
[DFlash translator](/home/juanbeck/zerotier-llm-proxy/scripts/windows/lucebox_dflash_proxy.py#L236)
converts Chat Completions into Responses, retains only selected request fields,
omits `response_format`, substitutes model aliases and emits synthetic completion
metadata. Its upstream failure path can repeat a POST through curl after an
ambiguous connection failure
([source](/home/juanbeck/zerotier-llm-proxy/scripts/windows/lucebox_dflash_proxy.py#L143)).
These scripts were inspected as alternative implementations; their presence does
not establish which route is active. A route supporting chat does not necessarily
preserve the compiled schema, model identity or single-call accounting.

## Approach registry

The registry records candidates, not approved designs. All live assumptions are
`not_scored` until owner evidence or a permitted probe exists.

### Owner-contract alternatives

The following routes are materially different mechanisms. Their source evidence
is the baseline above; the probes are proposed, not executed fixes. A missing
clock/authority proof blocks qualification, while an undecided design remains a
candidate. None is accepted by R0.

| ID | Mechanism, assumptions and owner | Next probe and expected observation | Status and exact gap |
| --- | --- | --- | --- |
| OV-A | Portable declarative validator for pinned proposal and native-result schemas; assumes a common useful schema subset. Semantic admission owns proposal policy; native owner supplies result semantics. | Wrong result field type, unknown field and changed schema content must reject before evidence issuance, preserving raw result/rejection in replay. | candidate; no result-schema resolver, supported subset or compatibility contract. A generic validator must not infer domain truth. |
| OV-B | Strict external transport parser plus owner-local native-result validator; assumes a pinned parser and owner validator can expose one portable rejection contract. | Identical malformed/extra-field outputs at two adapters and invalid native payload at an owner must yield attributable rejection, not silent repair. | candidate; parser/validator identities, repair provenance and owner-result validator pinning absent. |
| FR-A | Domain owner issues a typed validity judgment with recorded assessment time; core verifies provenance and lineage. Assumes owner time is comparable or its conversion is attested. | Old/future/unknown-clock evidence and a replay under year 2099 must reproduce the recorded temporal judgment. | candidate; no typed judgment, clock provenance or authoritative conversion contract. An opaque owner boolean is insufficient audit evidence. |
| FR-B | Owner supplies observation provenance; deterministic evaluator applies a frozen domain-authored temporal rule using recorded assessment time. Assumes a small portable rule expresses the intended validity. | At-boundary and one-tick-past expiry, incompatible clocks and changed policy must produce the frozen outcome independent of replay wall time. | candidate; time basis, boundary, skew, unknown-time disposition and validity horizon undecided. |
| FR-C | Assign the allocator's 30-second TTL to every effect. Assumes resource/readiness age equals effect validity. | Compare an exact historical write receipt with a current-state observation after 30 seconds. | rejected as inferred policy; no accepted contract equates those semantics. Finite expiry for every effect remains a human choice, but its horizon must be domain-authored, not borrowed. |
| FC-A | Explicit completion assertion pins claimant, raw source, claimed obligations and task lineage; comparison records unsupported claims separately from effect judgment. Runtime attribution owner does not become effect owner. | Claim all obligations complete while one required receipt is absent. Record who claimed what; task disposition follows separate frozen policy. | candidate; claim grammar and unsupported-claim consequence absent. |
| FC-B | Derive attribution from an explicit native result/evidence completion assertion without adding a model completion output. Assumes assertion scope is machine-readable. | Successful operation with only a subset of task effects must remain distinct from a false task-completion assertion. | candidate; ordinary `succeeded=True` has no task-completion scope. Missing evidence alone does not prove a claimant lied. |
| TC-A | Separate task-control disposition and stop -> settle -> terminal barrier. Runtime controls own stop, native/provider owners own settlement, ledger owns grammar. | Cancel while model/native work is outstanding, then receive late output/evidence. Block new work, preserve settlement and emit exactly one scoped terminal disposition. | candidate; stop authority/state, settlement/reconciliation and terminal control digest absent. |
| TC-B | Extend the single acceptance judgment with frozen control-policy inputs. Policy owner maps controls without inventing failed effects. | Optional operation cancellation, exhausted advisory retry and timeout after valid required evidence must follow explicit policy rather than universal rejection. | candidate; evaluator currently accepts only obligations/evidence, not control state. Mapping cancellation to fabricated failed evidence is unacceptable. |
| DC-A | Bounded content-addressed context snapshots in a durable artifact store; ledger references exact source/policy/snapshot; prompt pins it. Context adapter selects, ledger preserves lineage. | Restart in standby and rebuild the same prompt; missing/corrupt blobs or cross-role/environment reuse fail closed. | candidate; artifact durability-before-reference, scope, redaction, freshness and retention undefined. |
| DC-B | Small bounded context content recorded inline as common-ledger facts. Assumes size/privacy allow immutable inline storage. | Restart and competing context updates must reconstruct one ordered scoped snapshot; sensitive-field fixture challenges retention. | candidate; event grammar and confidentiality/bounds absent. All conversation history need not become authority-ledger data. |
| AP-A | Portable approval-required/request/grant/withdraw/consume facts tied to exact operation and implementation identity. Deployment owns authorizer/policy; domain owner enforces. | Changed arguments/binding/task, double use and withdrawal racing dispatch produce exactly one deterministic authorized start or rejection. | candidate; trusted authorizer provenance, policy revision and atomic consumption/revocation grammar absent. A hash is not issuer authentication. |
| AP-B | Native owner maintains approval UI/control and issues a portable attested decision to domain admission. Assumes existing native approval can satisfy a common contract. | Two owner adapters agree on allow/deny/pending; self-authored “approved” payload lacks authority and rejects. | candidate; no local implementation or equivalence proof. UI acknowledgment alone is insufficient. |
| EX-A | Contract inventory maps legacy HarnessSpec/ModelProfile names onto existing pinned artifacts, retaining any unmet fields as open obligations. Contract owners approve mapping. | Round-trip/version matrix and permission/evidence negatives cover every mapped obligation. | candidate; mapping and remaining profile/ingress serialization contracts unreviewed. |
| EX-B | Introduce the original named envelopes and narrow complete authority operations. Assumes a distinct semantic owner/use case justifies new types. | Delete proposed envelope in a fixture: loss of a specific versioned invariant must be demonstrable. | candidate; otherwise creates redundant metadata or parallel authority stores. |

### Temporal semantics requiring a decision

September's [effect decision](../artifacts/decisions/2026-09-08_uah_identity_environment_and_memory_grill.md)
section 8 already fixes domain ownership and required/best-effort obligations.
The current [EffectEvidence/EffectObligation fields](../../src/ab_harness/contracts.py)
have no time or validity rule. [Acceptance](../../src/ab_harness/acceptance.py)
matches object, owner, success and observed effect membership, not time. An effect
label containing “fresh” does not enforce freshness.

The leading proposal is domain-authored **per-effect validity frozen into
CompiledTask**, with owner observations and an explicitly recorded assessment
clock. It is still pending the human. FR-A versus FR-B is a second implementation
choice, independent of whether historical receipts can be durable:

- **Historical occurrence:** an exact lease/task/operation receipt can prove that
  `note_written` occurred. Elapsed time need not erase this fact. It does not prove
  the note still exists, remains unchanged, or belongs to another task.
- **Current state:** “target present now” or “note still contains X” requires a
  domain-defined validity horizon or owner re-observation. A durable occurrence
  receipt cannot substitute for current-state evidence.
- **Validity horizon:** decide whether evidence must be valid at execution,
  evidence admission, task acceptance, or more than one point. A receipt may be
  fresh when issued and stale when a delayed task attempts closure.

Candidate minimum representation: validity mode and policy revision on the
domain effect rule and compiled obligation; owner observation time, clock
identity and source/receipt lineage on evidence; recorded capture and assessment
times on the issued decision. Use typed fields rather than recovering authority
from arbitrary `payload` keys. Exact schema names and versions are unresolved.
Receipt capture time cannot silently substitute for physical observation time.
Cross-clock comparisons require an owner-attested mapping and bounded skew;
“both look like UTC” is not synchronization evidence.

The existing [timeout decision](../../src/ab_harness/runtime_controls.py) lines
470-595 is a useful mechanical precedent: it validates recorded ISO-8601 times,
requires time zones, derives deadline from the frozen wall budget and verifies
the outcome from those times. Equality currently means within budget because
timeout uses `observed > deadline`. That is an observed timeout convention, not
an accepted effect-expiry convention. Effect validity must select its own exact
boundary and unknown/future-time handling.

Proposed adversarial matrix, all awaiting DEV implementation under the selected
contract:

| Input | Required discriminating observation |
| --- | --- |
| Durable exact-operation receipt assessed much later | Historical occurrence remains provable only if its chosen domain validity mode permits it; no current-world-state inference. |
| Current-state evidence at expiry, then one tick later | Outcome exposes the chosen inclusive/exclusive boundary, frozen in policy. |
| Missing time, naïve time zone or unknown clock | No silent freshness. Typed inadmissible/pending/deficit outcome follows frozen policy. Missing live clock readiness is separately `not_scored`. |
| Future observation or clock rollback | Reject or use an explicitly bounded attested skew rule; never obtain unlimited freshness from negative age. |
| Old observation captured recently | Age uses the declared observation basis, not network receipt time. |
| Assessment replayed under a different current clock | Identical judgment/digest; replay never consults wall time. |
| Changed domain validity policy under unchanged revision | Fail closed at compilation/evaluation trust crossing after DEV's content-verification repair. |
| Correct effect from another operation/task/environment | Scope fencing prevents reuse merely because object and owner match. |
| Stale required versus stale best-effort evidence | Rejection of evidence is not proof the native effect failed. Required pending/recovery/terminal impossibility and best-effort deficit need explicit policy. |

### Remaining owner boundaries

Model output and native result are different output contracts. The proposal
envelope has substantial validation already; raw finite JSON capture does not
validate the compiled schema. Native result payloads are currently copied without
resolving `output_schema_ref`. OV-B is the leading minimal route for one adapter:
strict envelope parsing, no silent semantic repair, owner-local result validation
before evidence normalization, and pinned parser/validator provenance. OV-A earns
a common validator only when real consumers establish a useful portable subset.
If repair is disallowed, record parse rejection explicitly; if a repair calls a
model, it is a separate identified, budgeted invocation. Preserve raw response
provenance in either case.

False completion needs an assertion to attribute. The normalizer already rejects
explicit model effect claims, and the evaluator suspends missing required
evidence. Neither implies that every incomplete task is a false-completion claim.
FC-A offers claimant/source/obligation attribution without authorizing a new
completion output type. A forbidden claim can be recorded as a rejection; whether
the task continues is separate policy. FC-B can classify owner assertion mismatch
only after its completion scope is explicit. An operation's successful mutation
remains successful even if its optional report or overall task is incomplete.

For task controls, TC-A is the leading route because existing
[ledger transition rules](../../src/ab_harness/lifecycle.py) reject post-terminal
events and acceptance while a model call is outstanding. Immediate terminal
cancellation would leave no ordinary route to record late output. A stop barrier
must prevent new work, settle or explicitly reconcile existing work, then close
the task. Provider disconnect, native action interruption and observed effect
status are distinct owner facts. The precise runtime/task authority and whether
control termination uses a separate artifact or extended acceptance remain
GRILL choices. No generic coordinator should absorb those owners.

DC-A is a leading context candidate if a durable artifact store is accepted as
an H1 dependency; DC-B is credible for a small nonsensitive synthetic fixture.
Neither imports H3 learned memory. Approval AP-A is a leading portable synthetic
route, with AP-B reserved for domain adapters. It needs authenticated authorizer
provenance, exact scope, explicit denial/withdrawal and atomic dispatch fencing;
a callback or untrusted `approved=True` is insufficient.

### Provider alternatives

| ID | Mechanism and assumptions | Owner | Discriminating probe | Observed evidence | Status and exact gap |
| --- | --- | --- | --- | --- | --- |
| P1 | Native Ollama over loopback with actual local weights and native `format` | Deployment/runtime owner and external provider adapter | Inventory/version and model locality, then recorded HTTP fixture with compiled `oneOf` schema | Official native schema transport; current port can receive parsed JSON | candidate; local model, running server, capacity, installed version and schema subset are `not_scored` |
| P2 | Ollama OpenAI-compatible Chat Completions | Same owners | Compare native and compatible bodies/results on one frozen model, schema and decoding profile | Official subset compatibility and `response_format` support | candidate; same unresolved live facts plus exact schema-envelope compatibility and effective context |
| P3 | Existing ZeroTier Watson route through LiteLLM to llama.cpp, with fixed upstream and no hidden fallback | Network owner separately from gateway and inference owners | Owner-issued route/build/model record; captured request at each hop; strict schema and upstream call-count fixture | Historical repaired route; official gateway/schema behavior; existing HTTP planner seam | candidate; active endpoint, upstream, transformation, retry/fallback policy, memory injection and installed builds are `not_scored` |
| P4 | Reuse existing NAO provider unchanged | NAO planner owner | Pass a `ModelInvocationRequest` and inspect actual body/output | String return, no schema argument, prompt mutation, no UAH lineage lookup | rejected for direct reuse; extract transport behavior outside core only after recorded conformance |
| P5 | Treat client timeout/disconnect as proof that upstream generation stopped | Transport and inference owners | Delayed-response fixture, severed connection, owner-observed upstream request lifetime and replay | Current port has no abort contract; ambiguous translator retry exists | blocked; no acknowledged stop or reconciliation guarantee |
| P6 | Let schema-constrained output stand in for deterministic UAH validation | Proposal/admission owners | Finite but invalid operation, forbidden effect and forged completion fixtures | RawModelOutput accepts finite JSON; compiler's forbidden observable-effect review finding remains open | rejected; transport/schema success cannot establish semantic scope or effect truth |
| P7 | A free-tier hosted provider available under the user's subscription | Account/deployment owner and external adapter | Non-sensitive owner confirmation of entitlement, quota, supported protocol and task-data policy | Human permits this alternative; no account inventory was inspected | candidate; subscription availability, effective quota and compatible API access are `not_scored`; a chat subscription does not establish API entitlement |
| P8 | Local Ollama server invoking an explicitly cloud-backed model, one of the two selected targets | Cloud service and local runtime owners, external adapter | Recorded nonstreaming body/response and strict JSON/proposal negatives without assumed schema support | Human approved this target; official docs exclude current cloud structured outputs | candidate; authenticated availability, exact model, entitlement, data policy and output behavior are `not_scored`; no local-inference or schema-enforcement claim |

### Request and output alternatives

For P1, the candidate body maps compiled messages directly to `messages`, the
resolved artifact to `model`, explicit nonstreaming to `stream:false`, and the
parsed compiler schema to `format`. Native Ollama documents JSON or schema
formats, optional generation options, separate thinking controls, a final
`message` and completion metadata. Native streaming defaults to true; explicit
false returns one JSON response
([chat API](https://docs.ollama.com/api/chat),
[streaming](https://docs.ollama.com/api/streaming)). Parse final
`message.content` as JSON before returning it to the port; do not substitute
reasoning text or strip arbitrary prose to create a valid operation. An
operation's values remain untrusted after parsing.

Ollama's current structured-output documentation recommends passing the same
schema in the prompt and validating the response. It explicitly states that
Ollama Cloud does not currently support structured outputs
([structured outputs](https://docs.ollama.com/capabilities/structured-outputs)).
The UAH compiler already includes its schema in the system message. The compiled
`oneOf`, `const` and additional-property rules still need version-specific
conformance tests; the docs do not establish full JSON Schema equivalence.

For approved P8, schema transport is an optional, explicitly declared provider
capability; deterministic UAH output validation remains mandatory. An adapter may
request a JSON operation through the frozen prompt and omit an unsupported
transport schema only under a recorded capability/configuration policy. It must
not claim cloud schema support, silently strip it or relax admission. A role that
requires provider-side `structured_output` cannot be qualified by relabeling plain
JSON generation as that capability. GRILL must distinguish optional provider
constraints from mandatory parser, argument and semantic validation. Malformed
or prose-only responses produce a typed rejection, not reconstructed effect truth.

P2 and P3 can use a Chat Completions body with explicit `stream:false`, the same
messages and a route-qualified `response_format`. Ollama supports only a subset
of OpenAI's API; its compatible interface does not expose native context-size
selection. Its Responses compatibility is explicitly nonstateful despite a
contradictory feature-list item on that page
([compatibility](https://docs.ollama.com/api/openai-compatibility)).
The minimal experiment therefore need not introduce Responses or provider-owned
conversation state. The precise schema envelope must be checked against the
selected server. llama.cpp's documented `response_format` variants and supported
grammar features differ from assumptions of complete OpenAI equivalence
([server reference](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)).
LiteLLM documents schema support checks and optional client validation; gateway
support depends on the model/provider and does not prove downstream enforcement
([schema reference](https://docs.litellm.ai/docs/completion/json_mode)).

### Timeout, cancellation, redaction and provenance dependencies

A finite client timeout can produce a typed invocation failure. It does not
prove that an upstream stopped generating or restore a model-call debit. Current
authority has no mechanism to interrupt a running synchronous port or reconcile
an outstanding invocation after process interruption. Late responses are
currently recorded. The grill must decide whether the first live canary requires
only bounded client failure or a provider-owner stop/reconciliation contract.
These are materially different acceptance criteria.

LiteLLM documents per-call and deployment timeout controls and retry/fallback
policies. These may produce several upstream attempts under one client call or
serve a different model group. The selected route's effective policies need an
owner record or a fixture that counts upstream POSTs; do not infer zero retries
from UAH's refusal to retry an unfinished invocation
([timeouts](https://docs.litellm.ai/docs/proxy/timeout),
[fallbacks](https://docs.litellm.ai/docs/proxy/reliability)).
The reviewed Ollama API documentation supplies no acknowledged cancellation
endpoint sufficient to claim UAH task closure. Ollama generation source uses a
request-derived cancellation context, which suggests an implementation mechanism
but does not prove cancellation propagation through proxies or the installed
chat server
([source](https://github.com/ollama/ollama/blob/main/server/routes.go)).

Local Ollama does not require API authentication; direct hosted API calls require
a bearer key. Signed-in local servers can serve cloud models, so loopback routing
alone does not establish local inference or privacy
([authentication](https://docs.ollama.com/api/authentication)).
Ollama documents a deployment control for disabling cloud features, but R0 did
not change it
([FAQ](https://docs.ollama.com/faq)). Credentials remain outside configuration,
prompt artifacts, ledger and diagnostics. Current failure hashing prevents
plaintext exception leakage; it does not redact secrets copied into model output
or prompts. Adapter logs, HTTP bodies and gateway memory injection require their
own review. Any redaction that changes semantic task content should occur before
prompt identity is frozen or carry an explicit transformation record.

The minimal provenance record is a candidate, not a new accepted schema: opaque
route identity and adapter revision; exact configuration ID; served model ID plus
artifact/revision or digest when available; inference/gateway versions; effective
context and output controls; schema mode; retry/fallback and timeout policy;
request/response timing and finish reason; deployment declaration of locality and
context transformation. Ollama `/api/tags` supplies model digests and sizes, which
can support model identity without loading a model
([inventory API](https://docs.ollama.com/api/tags)). Advertised identity and
declared capability remain distinct from measured behavior. Current
`RawModelOutput` pins the request lineage but contains no dedicated transport
metrics or served-model provenance fields. Decide whether a separate external
canary artifact suffices before changing a portable artifact.

## Discriminating probes and results

1. **Static request/output seam:** confirmed synchronous finite-JSON port, atomic
   start/debit and exact actor lineage through current source and 37 passing
   focused tests. No live provider score was assigned.
2. **Historical route conflict:** July and September 2 NAO reports describe
   failure; later September 3 and 12 owning-repository reports describe repaired
   Watson and separate Ollama failure. The outcome is date-specific drift,
   not a current endpoint-health finding.
3. **Transformation conflict:** source inspection found omitted schema and
   ambiguous upstream POST retry in the optional DFlash translator. Active route
   selection remains `not_scored`; no gateway config or secrets were loaded.
4. **Next recorded transport fixture:** assert exact compiled message/schema/model
   mapping, malformed and nonfinite output, empty content with reasoning present,
   truncated completion, unknown model, 401/429/5xx, delayed response, ambiguous
   disconnect and single upstream POST. This is DEV work after route selection.
5. **Later connectivity probe:** inventory and version can distinguish discovery
   from inference without loading a model. A subsequent bounded model request
   needs the main GRILL choice and an exact manifest/configuration/readiness
   report. Connectivity proves endpoint availability only. Full qualification
   follows normalization, admission, domain lease, owner result/evidence,
   deterministic acceptance and replay on frozen positive and negative cases.

6. **Synthetic stopping point:** source inspection and the existing example test
   explicitly show an open task after model invocation, with no admission,
   execution, evidence or terminal events. The composed run above is proposed,
   not newly implemented or passed.
7. **Temporal gap:** field inspection confirms no effect observation clock or
   validity rule; timeout uses recorded timestamps and an explicit strict-greater
   deadline. No freshness probe was executed and no TTL decision was accepted.
8. **Control gap:** current tests explicitly assert nonterminal timeout,
   cancellation and exhaustion. This distinguishes an unimplemented task-policy
   contract from a regression against that narrow behavior.

The bounded wording iteration used current source, existing tests and the October
5 review as its baseline. The mutation separated confirmed defects from release
obligations and provider scope from evidence policy. Negative holdouts challenged
historical “sound authority” wording, synthetic invocation as full closure,
recorded labels as measured results, durable receipts as current-state proof and
local Ollama as local inference. The report accepts only those evidence-limited
descriptions; candidate runtime/trace policy remains unaccepted.

## Adversarial audit

R0 preserved package and authority owners, task and actor lineage, frame-relative
AB meaning, and learned-content quarantine. No ROS or provider SDK entered the
portable core; no speech, perception, execution, evidence or completion claim
was generated. The holdout challenged easy reuse of planner transports, loopback
as locality proof, gateway schema preservation, hidden retry, timeout as stop
proof and historical readiness as current qualification. This research wording
is accepted only as a bounded evidence report. Prompt policy and runtime changes
were neither trained nor promoted. The unresolved H0 review defects and H1
closure gaps remain prerequisites for stronger claims.

## Decision: accept, reject, or bounded handoff

Decision: **bounded handoff**. The accepted experiment targets are P8 (Ollama
Cloud through a local server) and P3 (the exact personal Watson route). Other
routes remain comparison mechanisms, not a substitute for those targets. Both
must satisfy the same portable contract, despite different schema capabilities
and locality. Present availability was not measured. Watson can be initialized
by the human when the bounded test is ready; R0 does not boot it. Provider probing
is optional while authority repair is pending.

The first unresolved H0 policy question in main GRILL is freshness representation
and evaluation, still pending. The leading per-effect proposal needs additional
primary implementation evidence before acceptance. A separately bounded R1 is
authorized to compare modern harness evidence/trace contracts with a maximum of
five primary implementations/specifications. R0 itself neither settles the
policy nor expands its run boundary.

Keep the seven known blockers in DEV with protected valid controls and fresh
review. Then resolve these dependencies one substantive question at a time:

| Dependency | One next GRILL question and leading recommendation | Required acceptance evidence |
| --- | --- | --- |
| Effect validity | Can domain-authored per-effect validity distinguish historical receipts from current-state proof, frozen in CompiledTask and assessed at recorded time? Leading proposal, pending R1/human. | Exact clock/provenance, missing/future/boundary/late evidence and replay-under-different-clock negatives. |
| Model/native output | Shall the first slice use a strict pinned transport parser and owner-local native-result validator, with repair forbidden unless separately budgeted? OV-B leads. | Raw-to-parsed lineage, rejected malformed/extra-field output, invalid result payload and preserved valid owner receipt. |
| False completion | Shall an explicit attributable assertion be judged separately from effect acceptance? FC-A leads when model attribution is required. | Claimant/source/obligation correlation; missing evidence does not invent owner failure. |
| Task controls | Shall stop/settle/terminal be a separate task-control disposition rather than immediate evidence rejection? TC-A leads. | Outstanding model/native work, late settlement, no new dispatch and exactly one terminal disposition. |
| Durable context | Shall H1 use bounded artifact snapshots pinned in prompt/ledger, or small inline ledger context? DC-A leads only if durability dependency is accepted. | Restart equivalence, missing/corrupt snapshot rejection, scope/redaction/retention contract. |
| Approval policy | Who authorizes an exact operation, and is approval fenced at lease issuance or atomic dispatch? AP-A leads for portable synthetic proof. | Changed scope, double consumption, denial/withdrawal and dispatch-race cases. |
| Budget/repair accounting | Must the first H1 profile prohibit repair and record token/cost metrics without enforcement, or implement hard limits now? Declare the distinction without silently narrowing H1. | Compiled limits, every extra invocation debited, usage provenance and policy for uncertain usage. |
| Contract inventory | Can existing pinned artifacts replace legacy HarnessSpec/ModelProfile names through a reviewed obligation mapping? EX-A leads if no distinct owner/use case is lost. | Version/round-trip matrix including environment/profile/ingress and fail-closed permission/evidence tests. |
| Qualification labels | Shall synthetic core, adapter conformance, endpoint readiness, provider-mediated synthetic run and H2 parity remain separately labeled? Recommendation: yes. | Each label has its own frozen evidence manifest; no count or connectivity substitution. |

Recommended next grill decisions, in dependency order:

| Dependency | Recommended next decision | Exact evidence needed before implementation acceptance |
| --- | --- | --- |
| Route/locality | Freeze exact P8 cloud model and P3 Watson upstream; do not assume both support provider schema constraints | Fresh owner model inventory, server build, cloud entitlement and route identity |
| Transport scope | Keep the first canary nonstreaming and stateless with the exact compiled prompt/schema | Recorded adapter conformance and no silent prompt/schema transformation |
| Deadline and interruption | State whether bounded client failure is sufficient for the canary; reserve full task closure for the agreed owner settlement policy | Delayed/disconnected upstream fixture, exact timeout policy and no hidden retry |
| Configuration/provenance | Decide whether external qualification metadata satisfies the first experiment or requires an artifact extension | Served identity/effective controls versus declared configuration, replay link |
| Qualification claim | Name connectivity/readiness separately from UAH authority/evidence/replay qualification and NAO H2 parity | Frozen task suite, negative gates, owner-issued effect evidence and deterministic replay |

## Residual risk and next probe

The largest provider uncertainty is the exact active route, not the HTTP request
syntax. Resolve it with a non-sensitive owner declaration and recorded fixture
before any live request. No live state was inferred from source, existing daemon
configuration, old reports or model aliases. The smallest executable next step is
DEV's authority repair/review followed by the complete deterministic synthetic
notes run under the selected evidence/control contract. The next research probe
is R1's primary-source evidence/trace comparison, not a live provider call.

Missing live facts remain `not_scored`: cloud entitlement/quota, Watson active
route/model/build, effective schema support, hardware capacity, actual clock
synchronization, upstream stop propagation, native approval and live NAO parity.
No source/test/documentation inspection upgrades them to measured evidence.

### Final verification and snapshot audit

R0 completed at approximately 14:01 UTC after a 13:46:46 UTC start, within its
twenty-minute bound. HEAD remained
`28fab5e7f2c244d86a64c371f2118017999b2387`; the fourteen inspected core/governing
document hashes in the root's final audit matched the frozen values above.
Source and skill implementation remained unchanged by R0. Concurrent DEV created
additional review/skill artifacts and `uv.lock`; these were preserved, not
attributed to R0. The R0 repository content change is this single research note.

The initial `./scripts/run_precommit.sh` attempt failed because `pre_commit` was
absent from `.venv`. The documented `./scripts/setup_dev_tools.sh` then completed:
editable UAH install, requirements-dev tools and pre-commit/pre-push hook
installation. Effective versions include pre-commit 4.6.2, pytest 9.1.1 and Ruff
0.15.22 (the script replaced existing Ruff 0.16.10 to meet its declared range).
This is validation-infrastructure setup, not evidence-policy qualification. DEV
can reuse this configured environment without concurrent installation.

`./scripts/run_precommit.sh` subsequently passed every configured hook, including
Ruff, the source-aware test suite and generated-document synchronization.
An explicit `pre_commit run --files` on this untracked research note also passed;
`--all-files` alone would not cover a new untracked note. The direct renderer
`--check` and `git diff --check` passed. A passing suite establishes only tested
behavior at its captured content, not H0/H1 release closure. No HTML companion
was added because this research note is outside the canonical paired-document
render manifest.
