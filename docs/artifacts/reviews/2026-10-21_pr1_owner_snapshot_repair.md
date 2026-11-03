# PR1 owner snapshot repair

Scope: PR1 migration repair. Acceptance requires exact whole-unit independent
review; this note does not establish that acceptance.
This repair does not close H0, H1, O1 or H2. It adds no execution authority.

## Cause and correction

The integration exposed a repeated mismatch between content identity and Python
object behavior. A frozen dataclass prevents ordinary field assignment, but does
not detach a caller-owned collection or make an instance method an authoritative
verifier. Checking one object and later reading another representation can leave
the check disconnected from the value used to make a decision.

Each affected artifact owner therefore reconstructs its concrete declared data,
checks the original content identity, and returns a detached snapshot. Consumers
use that snapshot for the rest of the operation. Export is a consumer too: it
must not pair an old identity with changed wire content. Snapshotting protects
against later caller mutation; it does not authenticate a producer or grant
permissions. The existing lifecycle ledger remains the only lifecycle writer.

| Artifact | Owning correction | Public observations |
| --- | --- | --- |
| CompiledTask | Concrete verified copy for all selected consumers and export; detach compiler publication from registry objects | Altered intent, effect requirements, prohibitions and budgets reject before proposal/admission, ledger progress or timeout recording; restart stays nonterminal |
| DomainContractPack | Concrete snapshot includes nested ingress/effect rules; compilation and export consume it | Removed prohibition under the old revision rejects; legitimate revision and compiler identity remain stable; mutation during a registry callback cannot change compiled policy |
| EnvironmentIngress / TaskIngressDecision | Concrete snapshots preserve and compare the originally issued identities | Altered lineage cannot create a task-start fact; valid ingress retains its established identity |
| EnvironmentProfile | Publication and retrieval isolate declared immutable authority collections | Caller roster mutation cannot change the published handle permissions |

The first TRUST-07 changes protected compiled-task lifecycle consumers but left
the public exporter uncovered. The whole integration review also found earlier
domain-pack, ingress and profile defects. An approval of a narrow delta did not
approve the full main-to-candidate integration. Existing green tests exercised
ordinary valid flows and some individual mutation routes; they did not establish
the full consumer contract.

## Development and review lessons

For subsequent repairs, enumerate the concrete artifact's real consumers before
editing: issuance, export, storage, admission, decision and replay where present.
Pair each reproduced mutation mechanism with a valid public control. Cover both
method substitution and nested aliases, including changes made after publication
or during a collaborator callback. A detached value must be the value consumed,
not merely an extra check beside continued reads from the original object.

The regression tests use public interfaces and observable rejection, unchanged
ledger events and restart results. They supplement the existing valid required,
best-effort, timeout, legacy-identity and recorded NAO controls. They do not claim
to enumerate every possible Python representation or qualify a live controller.
The static-eligibility mutation control targets the published compiled object;
mutating a separate registry object no longer changes that detached publication.

Freeze the complete outgoing file set before independent review. Give reviewers
the main-to-final diff, including required fixtures, modes and deletions. A fix
delta approval is evidence about that delta only. Test-runner failures must be
compared with the baseline and disclosed; neither a green test count nor a
historical approval substitutes for the exact final verdict.

This is a migration-specific implementation and process record. REVIEW.md retains
review ownership. Complete shared static eligibility/binding resolution is a
separate H0 follow-up. Internal event-family cohesion remains an evidence-led
design candidate; no global codec or artifact framework is introduced here.
