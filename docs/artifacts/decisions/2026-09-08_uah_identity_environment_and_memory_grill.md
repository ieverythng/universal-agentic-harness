# UAH Identity, Environment, and Memory Design Grill

**Date:** 2026-09-08
**Status:** Architecture decisions accepted; grill closed; first TDD seam implemented
**Scope:** H0-H2 contracts, with H3-H5 compatibility seams only

## 1. Purpose

This record captures the decisions made after the H2 commit review. It keeps
the original H0-H6 delivery spine intact while resolving agent identity,
hardware allocation, environment activation, multi-actor traces, task closure,
Observatory, and NeuralWorkbench ownership.

## 2. Role, Agent, and Runtime Identity

**Question:** Does changing the model change the role configuration or the
agent?

**Decision:** `AgentRoleConfiguration` is model-independent. It freezes the
role's primary abstraction frame, approved additional frame projections,
capability packs, authority, budgets, bindings, and model-admission profile.
`AgentManifest` combines that role with a model configuration, prompt pack,
harness build, and adapter revisions. Changing any member creates a new
`agent_id`.

**Question:** How do stable names such as Watson or NAO planner survive model
changes?

**Decision:** `agent_handle_id` is a stable routed name. Each immutable handle
revision selects one `agent_id`, preserves the required role, cites fidelity
evidence, and retains rollback lineage. A handle is not the agent and does not
own memory.

```text
role_configuration_id
  + model_configuration_id
  + prompt_pack_id
  + harness_build_id
  + adapter revisions
  -> agent_id
  -> immutable agent_handle_revision_id
  -> stable agent_handle_id
```

## 3. Provider and Hardware Allocation

**Question:** Can one loaded model process embody several logical agents?

**Decision:** Yes, when the hardware and provider isolation contracts permit
it. The provider process is a computational resource; the harness owns logical
agent identity. Separate agents retain distinct runs, prompts, frame
projections, task state, and authority even when they share an equivalent
model instance.

```text
provider_pool_id
  -> model_instance_id
  -> model_lease_id
  -> model_invocation_id
```

Registration does not reserve hardware or invoke a model. An explicit startup
or invocation request acquires a lease after capacity and freshness checks.
`ModelAllocator` may choose an equivalent instance of the declared model
configuration. It cannot silently substitute another model configuration.

H1 supplies a fixed-instance lease interface. H2 uses fixed NAO provider
profiles. Dynamic pools, eviction, arbitration, multi-agent scheduling, and
fidelity-gated rebinding begin in H3.

## 4. Environment Activation and Continuous Agents

**Question:** What groups a running NAO container, its chatbot and planner, and
the tasks they process?

**Decision:** `EnvironmentProfile` is the reusable native-runtime contract.
`environment_run_id` identifies one owner-attested activation. It groups native
ingress, attached agent runs, tasks, traces, and native evidence.

```text
EnvironmentProfile
  -> EnvironmentRunAttestation
  -> environment_run_id
       -> chatbot agent_run_id
       -> planner agent_run_id
       -> task_id
            -> trace_id
                 -> operation graph
```

Each `agent_run_id` attaches to exactly one environment run and may process
many stimuli, tasks, model leases, and model invocations. A run may enter
standby without holding a model. A normal turn creates an invocation, not a new
agent run. Restart, terminal failure, explicit detach, or changed embodiment
creates a new run.

The environment owner starts native infrastructure and issues readiness
evidence. UAH validates and registers the attestation. It does not claim native
readiness from discovery alone.

## 5. Environment Ingress and Task Association

**Question:** Does every incoming user message or runtime event create a new
task or model call?

**Decision:** No. Approved bindings normalize input into immutable
`EnvironmentIngress`. Deterministic `TaskIngressPolicy` classifies each item as
an environment state update, new task, resumed task, notification to an
existing task, or rejection. A model may interpret admitted task content but
cannot rewrite the assigned task or trace lineage.

Domain task IDs retain native meaning. NAO goal, request, plan, version, and
step IDs cross the UAH boundary unchanged. UAH identities supplement this
lineage rather than reconstructing or replacing it.

## 6. Trace, Actor, and Operation Graph

**Question:** Is `trace_id` equivalent to a chat session or one agent's log?

**Decision:** No. It identifies one causal workflow and may contain operations
from several actor agent runs. Environment, task, chatbot, planner, role, and
handle views are read-only projections over one append-only ledger.

Every operation is anchored to exactly one frame-relative AB object. Internal
complexity or cross-frame delegation does not promote its AB level.

- `decomposes_to` refines an operation inside the same frame.
- `delegates_to` crosses into another frame through a typed role or handle,
  closed input artifact, expected output artifact, and authority boundary.
- `continues_with` records ordered workflow progression without claiming
  decomposition.

## 7. NAO `report_result`

**Question:** Is `report_result` AB2 because it verifies evidence, calls the
chatbot, and dispatches speech?

**Decision:** It remains AB1 in the planner runtime frame because it is one
planner-visible semantic operation. It verifies execution evidence, delegates
grounded response composition to the chatbot agent run in the dialogue frame,
then returns to the native communication owner. The delegated model text can
produce a typed report artifact but cannot prove navigation, manipulation, or
speech effects.

The NAO `v1.0.0` runtime and pinned chatbot source are authoritative. The
intended NeuralWorkbench revision contains an older same-frame decomposition.
H2 must correct that drift through an owner-reviewed, content-addressed
DomainContractPack revision. Live mutable registry synchronization is rejected.

## 8. Task Effects and Terminal Acceptance

**Question:** How should the harness represent an operation whose primary
effect succeeds but whose final spoken report fails?

**Decision:** Tasks declare typed `EffectObligation` values before execution.
Each is `required` or `best_effort` and names its evidence contract, owner, and
freshness policy. A pure evaluator derives `TaskAcceptance` from these
obligations and owner-issued evidence.

```text
all required satisfied              -> accepted
all required satisfied,
best-effort deficit recorded         -> accepted_with_deficit
required effect still obtainable     -> suspended
required effect terminally failed    -> rejected
```

An operation retains its own result. A later reporting failure cannot
retroactively turn successful navigation or manipulation into failure. Model
text and an event named `execution_feedback` are not terminal proof by
themselves.

## 9. Observatory and Verified Memory

**Question:** Should Observatory and NeuralWorkbench be one frame or service?

**Decision:** No. Observatory renders immutable facts and read-only projections.
NeuralWorkbench consumes evidence to retrieve experience, compare candidates,
and change future candidate priors. Workbench cannot mutate the ledger, and
Observatory does not construct memory or candidates.

`VerifiedTraceDigest` is a deterministic, model-free projection of lifecycle,
operation, evidence, and obligation events. It is the trusted compact unit for
Observatory and future Workbench retrieval. `memory_policy_id` limits which
digests a role may inspect by domain, environment profile, frame, role, task,
object, outcome, and approved handle lineage.

Model-authored reflection is excluded from the trusted digest. H3 may later
create reflection candidates under Workbench quarantine.

## 10. NeuralWorkbench Intervention

**Question:** Must full Workbench search run on every interaction?

**Decision:** No. H2 freezes the attachment seams only. H3 may perform a cheap,
deterministic task-root retrieval according to `memory_policy_id`. Empty memory
returns no candidate. Full `ConsultWorkbench` search is explicit or triggered
by deterministic policy based on task complexity, uncertainty, failure,
recovery need, and budget. It does not run by default for every trivial AB0 or
AB1 operation.

Workbench remains the muscle-memory engine: retrieved and adapted traces,
host-model multi-trajectory candidates, deterministic verification and
scoring, then H4 crystallization quarantine. It is not merely deterministic
lookup and does not require learned retrieval for its first implementation.

## 11. Domain Onboarding Boundary

**Question:** Does every domain require a new UAH kernel package?

**Decision:** No. Domain onboarding produces a declarative, content-addressed
DomainContractPack containing frames, objects, role projections, bindings,
evidence rules, prompt policy, environment profile, and qualification cases.
A custom adapter is permitted only for irreducible native semantics. NAO may
need a ROS-free normalization and parity adapter, while ROS imports and native
lifecycle ownership remain in the NAO repository.

Assisted onboarding may propose pack content and apply SkillOpt, TDD, and
deslop workflows. It cannot approve its own semantic objects or bindings.

## 12. Delivery Spine

- **H0:** freeze the complete identity, environment, ingress, operation-edge,
  obligation, acceptance, trace, and provider grammar.
- **H1:** implement registries, deterministic ingress, attached run lifecycle,
  standby, fixed-instance leases, PromptCompiler, admission, obligation
  evaluation, append-only replay, O1, and deterministic trace digests.
- **H2:** register the NAO environment, fixed chatbot/planner handles and
  providers, preserve native lifecycle owners, implement planner parity and
  `report_result` delegation, then run recorded and fake/sim qualification.
- **H3:** add hardware-aware provider pools and the first retrieval/search
  NeuralWorkbench.
- **H4:** add crystallization and reviewed promotion.
- **H5:** federate local and remote provider pools with conformance tests.
- **H6:** retain AB5 policy-foundry research as optional.

## 13. TDD Seam Confirmed on 2026-09-09

The owner confirmed the public seam and closed the architecture grill:

```text
TaskAcceptanceEvaluator.evaluate(
    effect_obligations,
    evidence_set,
) -> TaskAcceptance
```

The first red-green slices now distinguish required-effect failure from a
best-effort deficit using the same immutable evidence grammar. Duplicate
obligation identities and empty obligation sets fail closed. The evaluator is
also connected additively to the recorded NAO qualification result while the
legacy `required_observables` compatibility field remains available.

The next seam is owner-attested synthetic environment registration and
deterministic ingress classification. It should then connect the existing
proposal, admission, fake-owner, acceptance, and replay path into a complete
tracer.

## 14. Evidence and Limits

The architecture was checked against NAO tag `v1.0.0`, chatbot revision
`a2ecca796...`, and intended NeuralWorkbench revision `e76ba7e`. Focused
read-only baselines passed 112 chatbot turn-engine tests and 41 planner
supervisor/gate tests. These results constrain compatibility but do not qualify
UAH H2. `EffectObligation`, `TaskAcceptance`, and the pure acceptance evaluator
are now implemented. No TaskSpec obligation compiler, environment registry,
task-ingress policy, multi-actor ledger, `report_result` adapter, or Workbench
retrieval policy is implemented at this checkpoint.
