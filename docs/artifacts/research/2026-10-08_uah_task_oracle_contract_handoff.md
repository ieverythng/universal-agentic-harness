# UAH task-oracle contract alternatives: coordination supplement

Date: 2026-10-08, 16:53 Europe/Madrid.
Status: prepared alternatives retained after R2; no new research round,
implementation or schema acceptance.
Owner: domain environment owns observations and predicates; deterministic task
acceptance evaluates declared obligations. DEV owns implementation/review.
Affected gate: H0/H1 synthetic integration, not H3 memory or H4 promotion.

## Accepted and pending decisions

Direct human GRILL evidence accepts both historical write occurrence and
task-defined exact text or schema satisfaction at closure. Generated semantic
quality remains outside the first suite. A historical receipt is preserved
when later content changes; it does not establish closure-time satisfaction.
No universal TTL or learned completion judge is accepted.

The latest human GRILL reply separately approves a versioned AdmittedOperation
carrying the exact frozen ABObjectView, verified by the owner before dispatch
and evidence. This addresses operation semantics and provenance. DEV's R4
implementation, compatibility and independent review remain pending here.
It does not automatically encode the task's desired content.

The minimal synthetic context archive in R2 remains proposed. Conversation
summaries are not an oracle, task constraint or owner evidence source.

## Existing source facts

TaskSpec has goal text and requested effect IDs, not a typed content predicate.
CompiledTask.to_dict() already serializes the full TaskSpec.
_compiled_task_payload includes asdict(task_spec), so compiled_task_id binds
goal bytes. An additional generic compiled-task store is not necessary merely
to obtain a serializable full body.

The common ledger's task_compiled projection retains compiled_task_id,
domain-pack revision, role/frame/registry and budgets, but not the full goal
or predicate. A content digest proves identity when verified against a body;
it does not guarantee that the body is durably available after restart.

Inspected source hashes at 14:52 UTC:

- task_compiler.py: b11625e4cb5a64f74327e2112a6e182b48e45ce9821135a5af39a9f36f92e9bf
- lifecycle.py: 01a5523a438c6142385df8ffa241e225dfbb0394076082cbd609070c02503f81

Sources: [compiler](../../../src/ab_harness/task_compiler.py),
[ledger](../../../src/ab_harness/lifecycle.py), and the DEV
[integration plan](../../plans/synthetic_notes_integration_contract.md).
Source observations do not certify concurrent ledger repairs.

## Alternatives awaiting GRILL

| Alternative | Smallest useful contract | Provenance/replay obligation | Limitation |
| --- | --- | --- | --- |
| A: reviewed fixture-owner predicate | Freeze exact expected text/schema and task-scoped inputs before the provider/proposal, then check the actual workspace through the owner | Bind environment/task/trace, compiled_task_id, predicate revision and expected-input digest; retain immutable inputs and assessment source artifacts | Qualifies one synthetic fixture only; not a generic cross-domain predicate interface |
| B: portable typed task constraint | Introduce an explicitly reviewed domain constraint covered by compiled identity and delivered to owner assessment | Preserve the typed body or resolvable durable reference, evaluator revision, observation and assessment lineage through the existing lifecycle path | New version/compatibility/authority contract; cannot be inferred as an existing TaskSpec field |

Neither alternative may derive expected text from admitted proposal arguments.
That would let schema-valid wrong output prove itself correct.
Prose parsing of the goal or model-authored success narration cannot become
trusted policy. A mutable dictionary keyed only by task display name is not
durable provenance.

Freeze comparison rules, including encoding/newline behavior for text and the
schema/evaluator revision for structured content. Content identity,
representation validity and task-specific correctness are distinct checks.

Missing predicate/body, mismatched task/environment, changed expected inputs
or ambiguous evaluation must yield an explicit unavailable/rejected/pending
assessment under the reviewed contract, never fabricated success.
Restart must preserve the original historical occurrence and recorded closure
observation/assessment without rereading the current file as past truth.

## Smallest discriminating probes

1. Schema-valid wrong text: historical write may succeed; exact-content
   obligation must not accept.
2. Correct write followed by overwrite: preserve occurrence, fail current content.
3. Replace task-bound expected inputs or evaluator revision: fail identity/provenance.
4. Missing constraint artifact on restart: explicit gap, not presumed satisfaction.
5. Foreign task/environment observation: cannot satisfy either claim.
6. Model says completed without mutation: no owner-issued occurrence evidence.

A fixture-local oracle is a reasonable bounded first control if GRILL chooses A.
B becomes appropriate when an actual second environment needs the same portable
task-constraint seam. That is a proposal, not an accepted choice.
No task-oracle implementation was performed by RESEARCH.

## Coordination status

R2's historical concurrent-red test receipt remains unchanged. Main subsequently
reports a corrected DEV fixture and 388 passing author-suite tests, with
independent R3 gate still pending. This supplement does not independently
reproduce or approve that repair. No further research or live call is scheduled
at the 16:53 snapshot; the later bounded authorization is recorded below.

## Decision update: 2026-10-08, 16:56 Europe/Madrid

This update supersedes the earlier pending-A wording without erasing the
16:53 alternatives record. Direct human GRILL reply approves the owner-local
frozen predicate for the first synthetic suite and a separate synthetic adapter
following the NAO package boundary. A portable constraint language is deferred.
Suggested package naming is DEV's choice; `ab_harness_synthetic` outside
`src/ab_harness` matches the existing `ab_harness_nao` separation.

Bounded local contract/evaluation pass started at 14:56:15 UTC (16:56:15 Madrid),
with target stop 15:06:15 UTC. No web, provider calls, code implementation or
independent-review substitution occurred.

### Task-scoped immutable oracle

Retain the exact expected-source body, not only its hash. Freeze it before any
provider response or proposal. Bind it to environment_run_id, task_id,
trace_id, compiled_task_id, owner identity and predicate/evaluator revision.
The domain fixture must verify both body identity and task association before
evaluation. An explicit fixture-level association is narrower than a portable
compiled constraint and does not make the compiler understand predicate truth.

Current CompiledTask.to_dict() supplies its full TaskSpec; its content identity
covers goal bytes. A goal string is not a typed content predicate. The partial
task_compiled event still does not retain that full body. Reuse retained fixture
artifacts for the expected source, full task and receipt/assessment bodies.
Do not add a mutable task registry, second authority journal or generic store.

Recommended first fixture comparison rule, for DEV to freeze in its owner-local
predicate revision: UTF-8 strict encoding, binary read, exact expected bytes,
no Unicode normalization or newline translation. Explicitly declare whether
the expected text includes its final LF. CRLF, missing/extra LF, BOM and
canonically equivalent but byte-different Unicode are discriminating cases.
These concrete byte conventions are recommendations, not an additional human
decision or portable UAH policy. If the fixture instead chooses decoded-text
or schema comparison, retain that exact evaluator/schema revision and rules;
never substitute it after observing a failing output.

An exact-content predicate must use expected-source inputs, not the model's
arguments as its expected value. A schema-valid string can still be wrong.
A schema-only content task needs its task-defined schema body and deterministic
evaluator revision, distinct from the operation's argument-shape validator.

### Existing evidence/acceptance mechanics

The inspected TaskAcceptanceEvaluator matches object, evidence owner and
observed effect IDs. It does not evaluate payload predicates. Therefore the
synthetic owner must perform the comparison and issue the declared closure
effect only when it passes. Payload annotations alone do not satisfy it.

Freeze two required obligations before execution: historical `note_written`
and a separately declared closure-content effect. The current example declares
only `note_written`, object `write_note`, owner `notes`, in frame
`synthetic_notes`. The additional closure object/effect/binding/domain rule
must be reviewed synthetic-domain configuration, not invented from narration.
If that adds a projected object, freeze the changed domain/registry and role
configuration identities and resulting agent embodiment. Do not silently widen
the existing note_writer role or reuse a stale catalog/manifest.

The current ledger permits one evidence issuance per operation, cannot reject
previously issued evidence, and requires AcceptanceFact to name exactly the
recorded evidence set. A second closure observation therefore cannot replace
the write receipt or silently append another receipt to its operation.
A separately admitted/leased owner read/verify operation is compatible with
the existing grammar and should be tried before proposing a new observation
family. Its final reviewed domain identity is DEV's implementation detail.
Both operations retain the same registered task/trace lineage and distinct
operation/receipt/evidence IDs.

For the first bounded fixture, make one designated closure check after all
planned writes/interference, then accept against that recorded assessment.
Do not issue early successful closure evidence: the evaluator uses any
matching successful effect, not a newest-observation invalidation rule.
Repeated closure checks would require separate reviewed semantics rather than
assuming a later negative result cancels an earlier success.
The first fixture's closure check belongs to an explicitly controlled
single-writer phase immediately before terminal acceptance. It does not prove
perpetual content validity or atomic closure against arbitrary external writers.
Concurrent production environments need a separate owner-defined consistency
boundary; no global TTL or lock policy is introduced here.

A terminal-failure policy can reject a recorded negative closure observation;
absence of required evidence yields suspended under the current evaluator.
Do not manufacture evidence to force a preferred terminal result.
Historical occurrence remains successful when the closure obligation fails.

### Executable acceptance-case recommendations

Names below are proposed pytest cases, not newly implemented tests.

| Case | Owner action and assertion | Expected public outcome |
| --- | --- | --- |
| test_exact_write_and_closure_restart | Write frozen text, issue occurrence; independently read and compare; record closure | Both required obligations satisfied; accepted; replay status/digest identical |
| test_schema_valid_wrong_text | Provider emits legal write arguments with different text | Historical write can succeed; closure fails; task not accepted |
| test_report_without_mutation | Provider narrates success without owner mutation; inspect workspace and receipts | No occurrence proof; closure cannot replace it; no accepted terminal |
| test_overwrite_before_closure | Record successful write, externally change file, then run designated closure read | Preserve write receipt; closure fails; terminal rejection only with valid terminal-failure evidence |
| test_changed_expected_source | Change retained expected body under original digest before check | Identity failure/no valid closure evidence, never rebind expected value |
| test_missing_expected_source | Remove expected body while preserving its ID | Explicit unavailable assessment; required closure remains unproven |
| test_foreign_expected_inputs | Give another environment/task/trace/compiled ID's body | Reject task association before assessment/effect issuance |
| test_missing_evidence | Omit closure evidence; separately try omitting issued evidence from AcceptanceFact | Missing closure stays suspended; incomplete recorded set rejects ledger append |
| test_foreign_evidence | Supply same-looking effect from another owner/binding/task/environment | Normal receipt/ledger lineage fences reject or leave obligation unsatisfied |
| test_encoding_newline_rule | Vary LF/CRLF, BOM, non-ASCII or trailing newline under frozen comparison | Result follows frozen owner rule, not platform text translation |
| test_replay_without_live_reread | After accepted/rejected judgment, remove or change live workspace | Same historical replay status/digest; no dispatch or current-file reread |
| test_retained_assessment_missing | Remove retained predicate/receipt body after terminal commit | Structural ledger replay may remain available; detailed oracle audit reports unavailable, not complete reconstruction |

Foreign task/environment evidence must be tested through receipt and ledger
public boundaries. The standalone acceptance evaluator does not authenticate
all task/environment/binding lineage by itself.

### What can run now and prerequisite boundaries

Executed during this pass: existing tests/test_task_acceptance.py, four tests
passed. A standalone public evaluator matrix also passed six cases: no evidence,
write only and closure only suspended; both accepted; write plus negative
closure rejected; foreign-owner closure suspended. It used illustrative
effect/object labels, not mounted or approved synthetic-domain objects.
It proves evaluator composition only, not owner comparison, ledger integration
or safety of a live environment.

Owner predicate equality, frozen-input identity and byte-rule negatives can be
unit-tested by DEV without models or a new core interface. Recorded/fake public
setup can be prepared now, but end-to-end qualification depends on the reviewed
R4 execution semantic snapshot, ledger-integrity R3 gate and remaining H0
authority gates identified by DEV. These dependencies are not bypassed by a
successful fixture or raw task-start injection. No package-owned integration
tests were implemented or executed by RESEARCH.

Structural restart replay already uses recorded lifecycle outcomes. Detailed
predicate recomputation additionally requires retained expected/evaluator and
observed-source bodies; execution/evidence events do not inline their complete
payloads. Rechecking the live workspace would answer a new state question,
not reconstruct the historical closure observation.

Source pointers: [acceptance](../../../src/ab_harness/acceptance.py),
[contracts](../../../src/ab_harness/contracts.py),
[receipt/owner](../../../src/ab_harness/environment.py),
[example](../../../scripts/render_agent_runtime_example.py).
The accepted owner-local predicate does not add timestamps/expiry or overwrite
event truth. No H1 closure, live model readiness, NAO parity or context-archive
approval follows from this pass.

### Bounded-pass closeout

Pass ended at 2026-10-08T15:03:29Z, within the 10-minute bound.
[Evaluation receipt](2026-10-08_uah_owner_local_oracle_eval.json) retains the
six illustrative cases, four existing test results and inspected source hashes.
Full repository hooks and explicit supplement hooks passed on the observed
dirty tree; they do not approve an owner implementation or close H1.

Wording audit preserved the historical alternatives and changed only the
accepted owner-local decision status. Countercases retained: pending context
archive is not approved; proposed byte rules are not universal policy;
standalone evaluator results are not integration results; earlier R2 concurrent
failure evidence is not rewritten. DEV received the concrete seam constraints
and case matrix. No further pass or provider call is scheduled.

### Closure cutoff clarification within the same bound

Strict current-content-at-closure means the terminal ledger commit, not merely
the earlier successful owner read. The existing owner.execute returns after
recording its receipt; AcceptanceFact is a separate call. The ledger's writer
lock protects lifecycle persistence, not workspace bytes. Intervening mutation
is possible without an additional domain-local control boundary.

Smallest first-suite recommendation: the synthetic owner/coordinator enters an
exclusive closing phase before the final read and retains control of every
permitted workspace mutation through successful terminal commit. Record the
observed bytes/digest and exact expected/evaluator identities, and reject other
permitted writes throughout that phase. Freeze oracle inputs under the same
boundary. This is synthetic-domain coordination, not a second ledger, portable
constraint language, universal TTL or atomic external-filesystem guarantee.

Add test_mutation_between_verify_and_accept and test_write_during_closing_phase.
Inject a change after verify receipt and before AcceptanceFact on an unprotected
control. That path must not qualify current state at terminal, even if the
existing evaluator returns accepted from the earlier success. The protected
arm must fence the permitted mutation until commit. A failed/uncertain commit
must not be relabelled closed; releasing mutation control invalidates any
unqualified claim of uninterrupted state through terminal closure.

Arbitrary external writers outside this ownership boundary remain out of scope.
If exclusivity cannot be established, only the recorded observation is proven,
and the human's terminal-current-content requirement remains unqualified.
Replay uses the recorded outcome/source artifacts, never the later live file.

Final explicit hooks overlapped active R4: one new admitted-object snapshot
counterexample failed, 403 tests passed. The failure is at
tests/test_admitted_object_snapshot.py:80 (no expected object-semantics error).
Earlier hooks passed; the latest shared-tree result is not green and is not
repaired or independently reviewed by RESEARCH. Documentation/JSON hygiene and
generated documentation passed. This clarification adds no new research round.
