# UAH H2 Commit and Operational Readiness Review

**Review date:** 2026-08-17<br>
**Reviewed range:** `5de73a5...71ae872`<br>
**Commits:** `6708af9` and `71ae872`<br>
**Seven-day follow-up commit:** `8582ab9` (2026-09-01)<br>
**UAH branch:** `feat/pre-commit-queue`<br>
**NAO qualification boundary:** annotated tag `v1.0.0`, peeled commit
`ebffe93a74be4e013ce0f60fdfc41268dba73fc3` on the
`feat/TFM-LLM_planner` development line<br>
**Architecture reconciliation:** 2026-09-03<br>
**Frame-access reconciliation:** 2026-09-04<br>
**Agent-handle reconciliation:** 2026-09-06<br>
**Environment and task-closure reconciliation:** 2026-09-08<br>
**Review status:** H0 synthetic proof accepted with corrections required; H1 and H2 not qualified

## 1. Decision

The two commits contain a useful portable contract proof. They do not close the
then-active dated H2 launch contract. The current package can be installed in a clean
Python environment, executes one deterministic recorded success and one
out-of-projection rejection, and preserves the basic rule that an environment
owner issues effect evidence. The package does not yet implement the complete
H1 lifecycle, typed operation admission, model-free lifecycle replay, a provider
adapter, or NAO planner parity.

The current release label should therefore remain **H0 synthetic proof with one
partial H1 vertical slice**. It should not be labeled `UAH core qualified`,
`UAH H2 NAO planner qualified`, or `UAH H2 model qualified` under the definitions
in the [masterplan](../../plans/universal_agentic_harness_masterplan.md).

The shortest route to an operational Linux test is:

1. close the typed proposal and lifecycle/replay seam in UAH;
2. compile package-owned golden fixtures from the immutable NAO `v1.0.0`
   baseline and record its peeled commit in every parity artifact;
3. implement the provider-neutral model port and an Ollama adapter;
4. run recorded and fake-owner NAO parity under an explicit authority mode;
5. run the ROS fake stack on this PC, then defer live robot authority to the
   operator and robot environment.

## 2. Review Basis

### 2.1 Governing documents

- [Universal Agentic Harness masterplan](../../plans/universal_agentic_harness_masterplan.md)
- [Universal Agentic Harness development log](../../plans/universal_agentic_harness_development_log.md)
- [H2 and NeuralWorkbench design decision](../decisions/2026-08-04_uah_h2_neural_workbench_grill.md)
- [Domain initialization and AB coupling](../../plans/domain_initialization_and_ab_coupling.md)
- [Watson and local-inference seams](../../architecture/watson_inference_seams.md)
- [Root domain model](../../../CONTEXT.md)
- [Repository agent guide](../../../AGENTS.md)

The masterplan and development log are internally clear that H1 lifecycle and
H2 planner parity are incomplete. This review uses their hard gates rather than
the target date as the completion criterion.

### 2.2 Reproduced evidence

| Probe | Result | Interpretation |
| --- | --- | --- |
| `git diff 5de73a5...HEAD` | 55 files, 9,566 insertions, 4,301 deletions | The range is large because it includes generated HTML, moved documents, binary design artifacts, source, and tests. |
| `python scripts/render_agentic_harness_docs.py` | Pass, no diff before this review was added | Canonical Markdown and generated HTML were synchronized. |
| `python -m pytest` in the uninstalled checkout | Collection failed with eight `ModuleNotFoundError: ab_harness` errors | The mandated source-check command assumes prior installation or `PYTHONPATH=src`. |
| `PYTHONPATH=src python -m pytest` | 42 passed | Existing behavior tests pass against the source tree. |
| Clean archive, fresh venv, `pip install ".[test]"`, `python -m pytest` | 42 passed | The package is installable and its clean-install test gate passes. |
| Freshly installed `python -m ab_harness smoke` | Pass | The recorded smoke surface is reproducible after installation. |
| `git submodule status` | No entries | `.gitmodules` exists, but no Neural Workbench gitlink is committed. |
| Core import audit | Standard library and `ab_harness` imports only | The portable source boundary remains free of ROS, NAO, and provider SDK imports. |
| `git diff --check 5de73a5...HEAD` | One Markdown hard-break warning | No source whitespace faults; the development-log purpose line uses two trailing spaces. |

No coverage tool is installed in the current environment, so this review does
not make a numeric coverage claim. Passing test counts are not treated as proof
of untested lifecycle or parity behavior.

## 3. Current Release Position

| Release requirement | Current evidence | State |
| --- | --- | --- |
| Portable install | Clean archive installed into a fresh venv | Green |
| ROS/provider isolation | Core import audit contains no forbidden dependencies | Green |
| Frame-relative AB semantics | Registry, projection, and role tests pass | Green for the H0 slice |
| Approved binding resolution | Candidate quarantine, runtime mode, environment, and owner checks are tested | Partial, because schema and evidence adapter fields can be empty |
| Typed admitted operation | Gate checks output type, object reach, AB level, and effect-claim authority | Red, because step arguments and operation schema are not admitted as a typed value |
| Complete H1 lifecycle | No compile-to-terminal event grammar or runtime state machine | Red |
| Model-free replay | Recorded payloads can be supplied again, but no lifecycle ledger is reconstructed | Red |
| Failure suite | Out-of-projection and failed owner cases exist | Partial; stale evidence, timeout, cancellation, retry exhaustion, unavailable binding, and false completion are absent |
| Configuration identity | Stable digest over the implemented fields | Partial; the manifest omits required model/runtime resource and provider-capability fields |
| Provider/model port | No provider-neutral request/result protocol in `src/ab_harness` | Red |
| Ollama qualification | Local endpoint exists, but UAH cannot call or characterize it | Red |
| NAO ingress/egress adapter | Candidate pointers and dictionary adapters exist | Red; no `PlannerRequest` normalization, lineage, feedback egress, or parity runner |
| Explicit `legacy | uah | shadow` authority | Declared only in documents | Red |
| NAO parity report | No golden fixture run or disagreement classifier | Red |
| O1 Observatory | Contract document only | Red for implementation |
| Workbench quarantine | In-memory retrieval remains candidate-only | Green for the narrow optional seam |
| Neural Workbench repository pin | `.gitmodules` declaration without gitlink | Red |
| Documentation synchronization | Renderer is deterministic and current companions match | Green |

## 4. Commit `6708af9`: Documentation Reorganization and New Seams

### 4.1 Accepted changes

The repository reorganization is coherent. Canonical Markdown now lives under
`docs/plans`, `docs/architecture`, and `docs/artifacts`; the old
`docs/agentic_harness/*.html` files are small redirects. The shared theme paths
resolve from the new locations, and rerendering produced no unexpected changes.
`docs/README.md` provides a useful navigation and ownership summary.

The masterplan and development log correctly retain the following limitations:

- complete H0 schemas and lifecycle traces are not implemented;
- the H1 failure suite is incomplete;
- no NAO shadow-mode adapter has run;
- the Watson/Bonsai runner has not started;
- live NAO authority is excluded from H2 qualification.

Those statements are consistent with the source inspected in `71ae872`.

### 4.2 Critical correction: the submodule is not pinned

`.gitmodules` declares `src/Neural-Wokbench` and names a branch, but commit
`6708af9` does not add a gitlink at that path. `git submodule status` is empty,
and `git ls-tree HEAD src/Neural-Wokbench` returns no entry. A fresh clone cannot
retrieve the companion repository from this commit.

The following statements were factually incorrect before this review's
documentation correction:

- `README.md` calls the companion a commit-pinned submodule;
- `docs/README.md` calls it a commit-pinned companion repository;
- the development dashboard marks the repository boundary green;
- the masterplan adversarial audit marks the independent submodule pin complete.

Required correction: add the actual gitlink at a reviewed immutable revision,
or change all four claims to state that only a proposed submodule configuration
exists. A `branch = ...` entry is update guidance, not a revision pin.

### 4.3 Status taxonomy drift

The root README lists configuration identity, Workbench retrieval, and the smoke
CLI under “H0 proves.” The masterplan assigns configuration identity to H0-H1,
the smoke surface to v0-H1, and Workbench behavior to the H2-H3 seam with H3
authority. Grouping all three under H0 weakens the required separation between
implemented H0 claims and later roadmap work.

Required correction: divide the README status into at least:

- implemented H0 contract proof;
- partial H1 operational slice;
- optional quarantined H2-H3 protocol scaffolding.

### 4.4 Date and status maintenance

The masterplan status still described the dated launch contract as active, and
the development log still reported the state as of its original architecture
freeze. The gate had elapsed without H2 completion. Current status should use
ordered evidence gates and identify any future target only after the missing
gates have owners.

### 4.5 Scope sequencing

This commit adds the Workbench protocol decision, Observatory contract, domain
initialization plan, system-design DOCX, and associated generated assets. These
are relevant designs, but H3 and presentation work arrived before the release
critical H1 lifecycle and H2 planner parity slices. This is not a boundary
violation by itself. It is sequencing debt because the launch-critical queue
remained unimplemented.

### 4.6 File-group disposition

| File group | Disposition | Review note |
| --- | --- | --- |
| `.gitignore` | Accept | Ignores generated local artifacts and temporary Office files. |
| `.gitmodules` | Reject as a completed pin | Configuration exists without the required gitlink. |
| Root and docs READMEs | Accept with corrections | Navigation is improved; H0 taxonomy and submodule claims need correction. |
| Canonical plan and architecture Markdown | Accept as design record | The plans are detailed and mostly explicit about incomplete gates. |
| Generated HTML | Accept | Current renderer reproduces it. Generated changes should not receive independent semantic review. |
| Legacy HTML redirects | Accept | The user-facing paths continue to resolve to canonical documents. |
| System-design DOCX and PNG | Retain as artifacts | They do not constitute runtime or parity evidence. |

## 5. Commit `71ae872`: Main Harness Settings for H0-H1

### 5.1 Binding catalog, `bindings.py:11-67`

Accepted behavior:

- construction rejects bindings to unknown AB objects;
- binding IDs are unique inside a catalog;
- only `approved` bindings resolve;
- environment and runtime mode participate in resolution;
- ambiguous approved bindings fail closed.

Required changes:

- `ABImplementationBinding.__post_init__` validates identifiers, owner, locator,
  and revision, but permits empty `input_schema_ref`, `output_schema_ref`, and
  `evidence_adapter`. This contradicts the root domain model, which defines all
  three as recorded binding properties.
- Empty or duplicate runtime-mode strings are accepted. A binding can therefore
  be syntactically approved while lacking a usable contract for schema parity.
- Approval is represented by an unrestricted string and is not associated with
  review provenance, approval revision, or rollback target.

### 5.2 Configuration identity, `configuration.py:10-72`

Accepted behavior:

- serialization is deterministic;
- runtime-parameter order does not affect the digest;
- duplicate runtime-parameter names are rejected;
- registry and runtime changes alter the configuration ID.

Required changes:

- runtime parameter names and values can be empty because validation checks the
  outer dictionary rather than each pair;
- the contract cannot require quantization, effective context, KV settings,
  batch/concurrency, cache policy, provider protocol, endpoint capability, or
  resource headroom;
- prompt identity is a single caller-provided string and does not prove which
  projection, system prompt, or structured-output schema was used;
- the smoke configuration uses only `mode=deterministic`, so “complete
  configuration identity: Green” is too strong for model-qualified H2.

The current type is adequate for the recorded smoke fixture. It is not yet the
complete model-harness-environment manifest described by the H2 boot gate.

### 5.3 Environment owner, `environment.py:12-85`

Accepted behavior:

- AB0 objects cannot dispatch;
- catalog resolution occurs before handler lookup;
- the executable AB1 implementation owner must match the semantic owner;
- handlers must return `OwnerExecutionResult`;
- successful executions with declared success observables must return evidence;
- undeclared observables are rejected.

Required changes:

- the binding input schema is not applied to arguments before the handler runs;
- the output schema and named evidence adapter are recorded but never invoked;
- evidence has no observation time, freshness horizon, execution ID, or lineage;
- there is no timeout, cancellation, retry, idempotency, or owner-unavailable
  result grammar;
- a failed result may still carry success observables. Closure currently ignores
  them, but the invalid combination is not rejected.

### 5.4 NAO compatibility declarations, `nao_h0.py:13-163`

Accepted behavior:

- chatbot and planner roles remain separate;
- both roles have frame-relative control bands;
- effect claims remain disabled;
- all inspected ROS and Python seams remain candidate bindings;
- AB0 interface declarations remain non-callable through the registry;
- the planner parser collects referenced skill names for reachability checks.

Boundary verification against the immutable NAO `v1.0.0` baseline
(`ebffe93a74be4e013ce0f60fdfc41268dba73fc3`)
found `PlannerGate.decide`, `PlannerRequest`, `ExecutionFeedback`,
`PlannerDialogueAct`, `SceneSummary`, and `PlannerNode._publish_decision` at the
declared module locations. The chatbot publisher belongs to a nested/separate
chatbot repository and was not proven by the top-level NAO ref.

Required changes:

- no persisted binding catalog records the reviewed NAO revision;
- source revisions are arbitrary function arguments rather than verified object
  IDs;
- schema references are locator strings, not compiled fixtures or hashes;
- the declared modes are `shadow` and `cooperative`, while the H2 decision uses
  explicit `legacy`, `uah`, and `shadow` authority modes;
- `planner_output` and `_skill_steps` duplicate raw plan parsing and can drift.

### 5.5 Qualification path, `qualification.py:17-179`

This file contains the highest-risk implementation issue in the reviewed range.

The gate evaluates an `AgentOutput` constructed from `planner_payload`, but the
gate validates only output type, referenced object reach, AB level, and claimed
effects. After acceptance, `_skill_steps(planner_payload)` reparses the original
raw dictionary and sends its unvalidated argument dictionaries to the owner.
There is no typed admitted operation whose exact value is passed from gate to
dispatch.

This breaks the intended sequence:

```text
model output -> typed proposal -> deterministic admission -> exact admitted operation -> owner
```

The implemented sequence is:

```text
raw dictionary -> object-name summary -> reachability decision
raw dictionary -> second parser -> owner arguments
```

The two parsers currently select the same skill names, so the existing rejection
test prevents an out-of-projection name from dispatching. They do not validate
argument shape, required arguments, step IDs, duplicate IDs, plan lineage, or
mutation between admission and dispatch.

The class name also overstates replay. It accepts two fixture dictionaries but
does not reconstruct a persisted lifecycle. The chatbot payload and planner
payload are gated independently. No `PlannerRequest` output from the chatbot
stage becomes the planner input, so the test does not prove chatbot-to-planner
lineage.

Required correction: introduce one immutable typed proposal containing
normalized operations and lineage. The gate returns an admitted value or a
rejection. Dispatch consumes only the admitted value. Record lifecycle events
for compilation, proposal, gate, dispatch, evidence, and terminal decision,
then replay those events without invoking the model.

### 5.6 Smoke and CLI, `smoke.py:19-203`, `cli.py:12-25`

Accepted behavior:

- output is machine-readable JSON;
- success depends on all four canaries;
- the command exits nonzero when the aggregate status fails;
- identities are deterministic across repeated clean-install runs;
- the rejection canary does not reach the mounted owner;
- Workbench retrieval returns support and counterexample provenance.

Limitations:

- registry and fixtures are compiled into `smoke.py`, so the command cannot
  qualify a supplied registry, suite, model manifest, or environment;
- no malformed structured-output canary exists;
- no stale evidence or owner-unavailable canary exists;
- the command does not emit lifecycle events or a replay artifact;
- the command labels its adapter `nao-shadow-v1` without exercising a NAO
  compatibility adapter or an explicit authority router;
- the rejected report includes `passed: false`, which is the case outcome rather
  than the expected-canary outcome. This is valid but easy for consumers to
  misread.

### 5.7 Workbench memory, `workbench.py:10-174`

Accepted behavior:

- experiences are immutable dataclasses;
- trace IDs are unique;
- success and failure states are constrained;
- retrieval is deterministic and bounded per outcome;
- missing support or counterexamples become explicit gaps;
- the result remains `candidate` and has no promotion or write path.

Limitations:

- trace, task, configuration, registry, and object identifiers are not checked
  for non-empty values;
- retrieval mixes registry and configuration versions and reports the mixture
  after selection rather than constraining compatibility before selection;
- overlap ranking has no freshness, evidence validity, task-suite, or failure
  attribution compatibility gate;
- storage is in memory, not append-only or replay-addressed.

These are acceptable for a quarantined H3-facing sketch, but they prevent using
the result as operational context in H2.

### 5.8 Workbench protocol, `workbench_protocol.py:11-293`

Accepted behavior:

- request, candidate batch, and observation payloads reject non-JSON values;
- request IDs correlate responses;
- duplicate candidate IDs are rejected;
- unsupported handshakes fail closed by default;
- the unsafe version override disables proposals and remains observation-only;
- candidates have a fixed `candidate` status.

Required changes:

- `observe()` checks the `observe` capability but does not require the
  observation protocol to match the engine descriptor. A mismatched observation
  reaches the engine even when the normal proposal path would fail closed;
- proposal responses are not checked to ensure `engine_version` and
  `source_revision` match the descriptor captured during handshake;
- descriptors do not reject duplicate, empty, or unknown capability names;
- `activation_mode='gated'` is allowed without a defined activation authority;
- empty candidate collections are allowed without an explicit no-candidate
  reason;
- JSON-compatible dictionaries remain structurally untyped at the protocol
  boundary.

### 5.9 Tests, `tests/`

The tests are concise and exercise public classes rather than private methods.
The strongest cases prove candidate quarantine, wrong-owner rejection, AB0
non-callability, out-of-projection no-dispatch, failed evidence closure,
deterministic retrieval, and protocol mismatch behavior.

Missing high-value cases:

- admitted operation arguments match the exact normalized value checked by the
  gate;
- malformed or missing step arguments reject before owner dispatch;
- chatbot handoff lineage becomes planner request lineage;
- stale evidence, timeout, cancellation, retry exhaustion, unavailable owner,
  and false completion;
- replay equivalence from a persisted event ledger;
- binding schema/evidence fields reject empty values;
- runtime parameter names and values reject empty strings;
- observation protocol mismatch fails closed;
- response engine identity mismatch fails closed;
- clean source-check ergonomics for the mandated `python -m pytest` command.

### 5.10 Documentation tooling

The renderer changes correctly cover the reorganized canonical documents and
legacy redirects. `create_uah_system_design_docx.py` is presentation tooling and
does not provide H1 lifecycle or H2 parity evidence. It can remain in the
repository, but its maintenance should not precede the release-critical runtime
slices.

## 6. Standards and Specification Axes

### 6.1 Standards findings

Hard findings:

1. H0 claims in the root README include H1 and H3-facing work, contrary to the
   repository requirement to keep H0 implementation claims distinct.
2. Approved bindings may omit schemas and an evidence adapter, contrary to the
   root domain definition.
3. Raw planner arguments are dispatched after a summary gate rather than as the
   exact typed operation admitted by the deterministic gate.
4. Documentation claims a pinned submodule that is absent from the Git tree.

Design-smell findings:

- plan-step parsing is duplicated between `nao_h0.py` and `qualification.py`;
- content-address construction repeats across configuration, Workbench memory,
  and Workbench protocol modules;
- authority-bearing states use unrestricted strings across several modules.

### 6.2 Specification findings

Missing or partial requirements:

1. full planner ingress/egress and fake/simulated parity;
2. explicit `legacy | uah | shadow` routing and disagreement classification;
3. provider-neutral model port and Ollama/runtime preflight;
4. lifecycle ledger, replay, and O1 renderer;
5. source-schema parity artifacts for NAO candidate bindings.

Implemented-looking requirements that need correction:

1. chatbot and planner fixtures have no handoff lineage;
2. complete configuration identity is not complete for a served model;
3. binding validation does not require all contract fields;
4. Neural Workbench is configured in `.gitmodules` but not commit-pinned.

Scope introduced ahead of the critical path:

- Workbench memory and protocol;
- Observatory contract;
- domain initialization design;
- system-design Office artifacts.

These assets can remain, but they must not displace H1 lifecycle and H2 planner
parity in the next implementation queue.

## 7. NAO and Ollama Readiness on This Linux PC

### 7.1 Local runtime inventory

| Component | Observed state on 2026-08-17 | Consequence |
| --- | --- | --- |
| Ollama executable | `/snap/bin/ollama`, version `0.32.5` | Provider process is available. |
| Ollama `127.0.0.1:11434` | Listening; `/api/tags` returns HTTP 200 | One real provider endpoint can be probed now. |
| Model inventory | Eleven cloud-backed manifests; no local-weight model observed | Endpoint tests may depend on Ollama cloud authorization and network availability. |
| Ollama `127.0.0.1:11435` | Not listening | Split chatbot/planner endpoint profile is not ready. |
| OpenAI-compatible `127.0.0.1:8001` | Not listening | Hermes-style local gateway is unavailable. |
| Lab endpoint `127.0.0.1:8004` | Not listening locally | Current NAO default lab route is unavailable from localhost. |
| ROS 2 | Jazzy exists under `/opt/ros/jazzy`; not sourced in the default shell | ROS commands work after sourcing the distribution. |
| Built NAO packages | `planner_llm`, `nao_orchestrator`, and `fake_skills` resolve after sourcing the existing install | Independent NAO fake-stack tests are feasible. |

The Ollama inventory probe did not invoke a model. A scored model request should
wait for a frozen manifest, suite, and failure-attribution record.

### 7.2 NAO revision boundary

The NAO qualification baseline is the annotated `v1.0.0` tag, which peels to
`ebffe93a74be4e013ce0f60fdfc41268dba73fc3`. The tag belongs to the
`feat/TFM-LLM_planner` development line and is the immutable source for H2
contracts, fixtures, and parity evidence. The moving branch head may advance
without changing that qualification input.

The earlier review inspected `refactor/deslop_repo` as a prospective cleanup
boundary. That branch is not the H2 source of truth and its worktree state must
not enter UAH fixtures or compatibility claims. The imported deslop skill is a
development workflow aid only. NAO remains the semantic and execution owner.

### 7.3 Distance from meaningful tests

Three distinct tests should not be conflated:

| Test | Can run now? | Missing UAH work |
| --- | --- | --- |
| Independent NAO provider readiness against Ollama | Yes, through the existing `planner_llm` live provider seam after selecting a model and accepting cloud use | None for the NAO-only probe; it does not qualify UAH. |
| Independent NAO ROS fake-stack test | Technically feasible after sourcing Jazzy and rebuilding a clean selected NAO revision | It remains NAO evidence only. |
| UAH-integrated H2 NAO planner parity | No | Typed admitted operation, lifecycle ledger/replay, NAO adapter, frozen fixtures, explicit authority mode, and parity evaluator. |

The PC is not blocked by the absence of the robot. H2 explicitly permits
recorded and fake/simulated closure. The blockers are software contracts and a
fixture suite derived from the frozen NAO boundary, not hardware.

## 8. Architecture Reconciliation on 2026-09-03

The design grill resolved the vocabulary that was still ambiguous in the
reviewed commits. The canonical diagrams and complete node ownership table are
in the [foundation](../../architecture/universal_agentic_harness_foundation.md).

| Concern | Resolved contract |
| --- | --- |
| Reusable role | `role_configuration_id` identifies the model-independent role, model admission profile, primary frame, auxiliary allowlists, capability packs, control bands, budgets and authority policy. |
| Concrete agent | `agent_id` identifies the immutable embodiment composed from role, model configuration, prompt pack, harness build and adapter revisions. Changing any member creates a new agent. |
| Stable agent handle | `agent_handle_id` resolves through an immutable revision to one active agent with the same required role configuration, fidelity evidence and rollback lineage. |
| Activation | `agent_run_id` identifies one bounded activation of an unchanged agent. |
| Environment activation | `environment_run_id` identifies one owner-attested native activation. It groups ingress, attached agent runs, tasks, traces, and native evidence. |
| Environment ingress | `EnvironmentIngress` is immutable input; deterministic `TaskIngressPolicy` assigns state-update, start, resume, notify, or reject semantics before any model call. |
| Domain work | `task_id` is a domain-owned work instance with explicit domain type and native lineage. It is not a domain name or a model turn. |
| Causal trace | `trace_id` identifies one causally connected workflow and may contain operations from several actor agent runs. Environment, task, and actor traces are read-only projections over one ledger. |
| Operation | `operation_id` identifies one frame-relative AB-object lifecycle. Same-frame refinement uses `decomposes_to`; cross-frame work uses `delegates_to`. |
| Task closure | `EffectObligation` marks effects required or best-effort. `TaskAcceptance` is derived from owner evidence and preserves best-effort deficits without erasing successful operations. |
| Trace memory | `VerifiedTraceDigest` is a deterministic, model-free projection for Observatory and future Workbench retrieval. |
| Model surface | `InteractionModuleCompiler` creates a closed task projection. `PromptCompiler` presents that same projection with the UAH kernel, role contract, minimal domain policy, task state and typed output schemas. |
| Execution authority | UAH semantic admission creates an immutable `AdmittedOperation`; domain lifecycle admission may issue an `ExecutionLease`; only the environment owner executes and issues effect evidence. |
| Observatory | Mandatory kernel events preserve raw output, proposal, admission, lease, result and evidence as separate artifacts. Agent-visible trace inspection is a distinct read-only frame projection. |
| Additional frames | Roles may authorize substantial auxiliary frames, but each task receives only a bounded projection. Access is limited by `inspect_only`, `direct_proposal`, or `delegate_only`; effect-bearing cross-frame work defaults to delegation. |

The current verification after these documentation and renderer changes is
`PYTHONPATH=src python -m pytest`: 44 passed. The plain uninstalled invocation
still fails during collection because the repository uses a `src` layout
without configuring that path for direct test discovery.

## 9. Recommended Implementation Queue

All source changes below should use vertical red-green TDD slices. Tests must
observe public seams and must not mock UAH internals.

### Slice 1: typed operation admission

**Proposed public seam:** a planner adapter parses raw output into an immutable
`TypedProposal`; the gate returns an immutable `AdmittedOperation`; the
environment owner executes that exact value after domain lifecycle admission.

First failing behavior: malformed or missing `find_object.label` is rejected
before owner dispatch, while a valid normalized operation reaches the owner
unchanged.

### Slice 2: lifecycle ledger and replay

**Proposed public seam:** one runtime entry point returns an append-only sequence
of versioned events and a terminal decision; replay consumes those events
without a model and reaches the same decision.

First failing behavior: recorded success and one stale-evidence counterexample
produce compile-to-terminal events and replay identically.

### Slice 3: complete binding and configuration contracts

**Proposed public seams:** `ABImplementationBinding` construction and a
configuration-manifest loader.

First failing behaviors: approved bindings reject missing schema/evidence
fields, and served-model manifests reject missing provider, quantization,
context, or endpoint-capability identity.

### Slice 4: frozen NAO compatibility adapter

**Proposed public seam:** pure JSON-compatible normalization functions map the
selected NAO `PlannerRequest`, planner decision, execution feedback, and
dialogue act into UAH types without importing ROS into `src/ab_harness`.

First failing behavior: package-owned golden fixtures from NAO `v1.0.0`
round-trip with goal, plan, version, step, and evidence lineage intact.

### Slice 5: explicit parity runner

**Proposed public seam:** a parity evaluator receives normalized legacy and UAH
results under a declared authority mode and emits classified agreements and
disagreements.

First failing behavior: no qualification run starts without exactly one of
`legacy`, `uah`, or `shadow`; silent fallback is a hard failure.

### Slice 6: provider-neutral model port and Ollama adapter

**Proposed public seam:** an immutable model request/result protocol plus a boot
preflight that records endpoint protocol, model digest, structured-output
behavior, context/resource settings, latency, and failure attribution.

First failing behavior: a recorded provider returns a typed planner proposal;
an unavailable endpoint returns `transport_or_provider` without changing the
semantic gate. The live Ollama canary follows only after the recorded adapter
case is green.

### Slice 7: Linux ROS fake-stack parity

Build the selected NAO revision cleanly, run the explicit shadow profile with
fake skills, and capture request, proposal, gate, dispatch, feedback, dialogue,
evidence, and terminal events. Compare against the frozen legacy output and
review every disagreement before any UAH authority is enabled.

## 10. Proposed TDD Seams Requiring Owner Confirmation

No implementation test should be written until these public seams are accepted:

1. `TaskAcceptanceEvaluator.evaluate(effect_obligations, evidence_set)` to an
   immutable `TaskAcceptance`;
2. owner-attested environment registration and deterministic ingress
   classification;
3. `TypedProposal` to `AdmittedOperation` to domain lease and owner execution;
4. runtime execution to lifecycle ledger, deterministic digest, and model-free
   replay;
5. binding construction and configuration-manifest loading;
6. pure NAO contract normalization at a frozen revision, including explicit
   `report_result` delegation;
7. explicit authority-mode parity evaluation;
8. provider-neutral model request/result and boot preflight.

The refined recommendation for the first seam is the pure
`TaskAcceptanceEvaluator`. It is smaller than the complete execution path,
forces the newly accepted required-versus-best-effort semantics into an
observable public contract, and has no provider, storage, ROS, or scheduler
dependency. The next tracer should register a synthetic environment run and
classify one ingress before reconnecting the existing proposal and fake-owner
path. This order still requires owner confirmation before the first test is
written.

## 11. Seven-day Follow-up: Commit `8582ab9`

### 11.1 Scope and release effect

Commit `8582ab9` adds the deslop-refactor skill, the review document and its
generated HTML, glossary refinements, and renderer registration for this
review. It changes no `src/ab_harness` runtime file and adds no runtime test.
Its correct release effect is therefore documentation and development-workflow
hardening. It does not advance an H0, H1, or H2 implementation gate.

The commit is internally reproducible: the review Markdown is registered in
`DOCS`, its HTML companion is generated by the shared renderer, and the skill
uses progressive references rather than placing the full upstream material in
`SKILL.md`.

### 11.2 Deslop skill review

The skill interface is appropriately narrow. It asks for scope before edits,
distinguishes first-party from generated and vendored code, prioritizes
behavior-preserving changes, and requires focused validation. Its stop
conditions guard against cosmetic churn and speculative abstractions. These
rules agree with the H0-H2 requirement to preserve domain ownership and tested
behavior.

One provenance defect remains. The files
`references/upstream-deslop.md` and
`references/upstream-addtodeslop.md` are described as vendored from
`Theta-Tech-AI/llm-public-utils`, but the committed artifacts record no source
URL, exact upstream revision, retrieval date, or license. The larger reference
is more than three thousand lines, so repository-level provenance is required
before redistribution can be treated as resolved. This does not affect UAH
runtime behavior, but it is a release hygiene and reproducibility risk.

Required correction: add a small provenance record containing the upstream
repository URL, immutable revision, original paths, retrieval date, local
adaptation status, and applicable license. If redistribution terms cannot be
verified, retain the condensed original operating manual and replace the
vendored copies with source pointers.

### 11.3 Domain-language changes

The added glossary terms correctly separate reusable role configuration,
concrete agent embodiment, bounded activation, task, trace, and operation. The
later architecture grill further separated stable handle identity and hardware
allocation. Those later refinements do not invalidate the commit, but they mean
the glossary in `8582ab9` should not be read independently of the current
`CONTEXT.md`.

The strongest semantic correction is that a model change creates a new
`agent_id`, while an approved stable `agent_handle_id` may later resolve to that
new embodiment through a versioned revision. Model allocation selects runtime
capacity for an already resolved agent and cannot redefine the role or agent.

### 11.4 Standards axis

Hard finding:

1. Vendored upstream reference material lacks immutable provenance and license
   evidence.

Judgement findings:

1. The commit contains three separable concerns (workflow skill import, domain
   glossary changes, and review publication). This is a possible divergent
   change at commit granularity. Future commits should keep workflow imports
   separate from architecture decisions so rollback and review remain narrow.
2. The `feat:` subject overstates runtime effect. A `docs:` or `chore:` subject
   would better describe a commit with no harness implementation change.

No source-code smell is reported because the commit does not change runtime
source. Generated HTML is reviewed only for synchronization and rendering, not
as an independent semantic implementation.

### 11.5 Specification axis

Implemented as requested:

1. The NAO deslop workflow was brought into this repository as a reusable
   Codex skill with a condensed operating manual.
2. A detailed commit and operational-readiness review was published in both
   canonical Markdown and generated HTML.
3. Domain language for role, agent, run, trace, and operation was recorded.

Partial or missing:

1. The commit did not restore the declared NeuralWorkbench gitlink.
2. It did not implement the typed proposal-to-admitted-operation seam selected
   by the review.
3. It did not close lifecycle replay, provider preflight, or NAO parity.
4. The imported upstream material lacks the provenance required for a stable
   repository dependency.

The commit is accepted as documentation and workflow scaffolding after the
provenance correction. It must not be counted as H2 progress.

## 12. Current Pre-commit Queue Review on 2026-09-08

The current queue modifies domain language, the foundation, adaptive Workbench
theory, the Observatory contract, the canonical masterplan and development log,
their generated HTML companions, this review, and one renderer regression test.
It changes no runtime source.

### 12.1 File-group disposition

| File group | Disposition | Review basis |
| --- | --- | --- |
| `CONTEXT.md` | Accept | Registration, startup, Workbench search, typed action memory, and crystallization now have distinct owners and release boundaries. |
| Foundation and masterplan | Accept | The original H0-H6 product spine remains canonical; identity and model allocation are staged inside it rather than replacing it. |
| Adaptive Workbench document | Accept | The pinned code is identified as a deterministic symbolic bootstrap, while the target portfolio includes generated and retrieved/adapted candidates. Training is not claimed as an H3 prerequisite. |
| Observatory contract | Accept | Registration, handle, run, lease, preflight, invocation, operation, and evidence events remain separate and reconstructable. |
| Development log | Accept | The existing recorded NAO path is correctly labeled an H0 contract slice; H0-H2 prerequisites and exit evidence are explicit. |
| Legacy documentation paths | Accept | `docs/agentic_harness/*.html` remains redirect-only; canonical Markdown exists only under `docs/plans` and `docs/architecture`. |
| Generated HTML | Accept | Regenerated from canonical Markdown and receives no independent semantic edits. |
| Renderer regression test | Accept | It checks that every legacy page resolves to its declared canonical target and that no competing legacy Markdown exists. |

### 12.2 Standards axis

No new repository-standard violation remains in the queue. Added prose contains
no em dash, marketing claim, global AB-level claim, or H3 implementation claim.
Core dependency boundaries are unaffected because `src/ab_harness` is
unchanged. The generated documents are synchronized and whitespace checks pass.

The open provenance finding for the already committed deslop references remains
outside this queue. It is recorded rather than hidden.

### 12.3 Specification axis

The queue records the decisions reached during the architecture grill:

1. role configuration, immutable agent embodiment, stable handle, run, task,
   trace, operation, provider pool, instance, lease, and invocation remain
   separate identities;
2. registration is declarative, while startup is the first capacity-reserving
   and model-probing transition;
3. H2 remains the first cooperative NAO demonstration against the immutable
   `v1.0.0` planner baseline and chatbot revision `a2ecca796`;
4. NeuralWorkbench is the H3 candidate-and-memory engine rather than an
   abstraction frame or execution authority;
5. H4 retains crystallization quarantine and reviewed promotion;
6. the development log has one canonical source and legacy redirects only.
7. environment profile/run, ingress, attached agent run, task, trace, operation,
   lease, and invocation have separate lifetimes;
8. task closure uses required and best-effort effect obligations;
9. one multi-actor trace records explicit cross-frame delegation and yields a
   deterministic `VerifiedTraceDigest`.

The queue intentionally does not implement the H0-H2 runtime contracts while
the design grill remains active. It is ready to stage as an architecture and
review checkpoint, not as an H2 implementation milestone.

### 12.4 Verification

`python scripts/render_agentic_harness_docs.py`, `git diff --check`, and
`PYTHONPATH=src python -m pytest -q` pass. The current source-aware suite reports
45 passed tests. The revised Workbench SVG was rendered separately and checked
for readable nodes, non-overlapping labels, and visible separation between
context output and shadow proposal output.

## 13. NAO Source-resolution Addendum on 2026-09-08

The latest grill requested that UAH recover behavior from the existing NAO
chatbot, planner, and orchestrator rather than reproduce their policy from the
documentation alone. The following read-only checks were therefore performed:

| Source seam | Observed behavior | UAH implication |
| --- | --- | --- |
| Chatbot `DialogueTurnEngine.execute_turn` | Injected history, cancellation, staged routing, prompt/model query, immutable result and trace hooks | Preserve as domain behavior behind `EnvironmentIngress` and prompt/model adapters; do not place routing policy in core. |
| Chatbot planner request adapter | Maps grounded turn output and history to request kind, goal, parent and supersession lineage | Normalize through a NAO adapter while preserving native IDs. |
| Planner supervisor | Goal-keyed state, cancellation, supersession, clarification, replanning, stale plan/version checks | Retain as the NAO lifecycle owner below UAH semantic admission. |
| Orchestrator planner gate | Deterministic readiness, admission and ownership checks | Retain as domain lifecycle admission; do not duplicate it in UAH. |
| Orchestrator `report_result` | Collects execution results, invokes a bounded chatbot system turn, validates text, then dispatches communication | Represent one AB1 planner operation with a typed cross-frame chatbot delegation and native communication evidence. |

The focused baselines passed 112 chatbot turn-engine tests and 41 planner
supervisor/gate tests. These are NAO source-preservation checks, not UAH H2
qualification.

The intended NeuralWorkbench revision `e76ba7e` currently describes
`report_result` through an older same-frame decomposition. The NAO `v1.0.0`
runtime remains authoritative. H2 must publish a reviewed DomainContractPack
revision that pins the NAO runtime, chatbot source, semantic registry, adapter,
and conformance report. Live mutable registry synchronization is rejected.

## 14. Release Recommendation

Retain both commits on the pre-commit review branch after applying documentation
corrections. Do not merge them to `main` as an H2 release in their current form.
The clean-install smoke result supports preserving the implementation as an H0
baseline. Source changes should begin only after the first TDD seam and the
immutable NAO revision are confirmed through the design grill.
