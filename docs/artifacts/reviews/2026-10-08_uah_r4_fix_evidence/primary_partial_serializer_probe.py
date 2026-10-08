from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import tempfile
import sys
from ab_harness import DomainLifecycleAdmission, LifecycleLedger
from ab_harness.proposal_admission import TypedProposal, AdmittedOperation
from ab_harness.domain_lifecycle import ExecutionLease
from ab_harness.contracts import OwnerExecutionResult
from ab_harness.acceptance import TaskAcceptanceEvaluator
from ab_harness.lifecycle import AcceptanceFact
from test_admitted_object_snapshot import authority_fixture, owner_for, FRESH_EFFECT
with tempfile.TemporaryDirectory() as p:
    compiled, catalog, env, ledger, admitted, lease = authority_fixture(Path(p))
    if len(sys.argv) > 1 and sys.argv[1] == "fresh":
        ledger.path.write_text("\n".join(ledger.path.read_text().splitlines()[:-1]) + "\n")
        ledger = LifecycleLedger(ledger.path)
    original_wire = admitted.proposal.to_dict()
    changed = asdict(admitted.proposal)
    changed["arguments_json"] = '{"unauthorized":true}'
    payload = {key: value for key, value in changed.items() if key != "proposal_id"}
    changed["proposal_id"] = "proposal:sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    new_proposal = TypedProposal(**changed)
    object.__setattr__(new_proposal, "to_dict", lambda: dict(original_wire))
    object.__setattr__(admitted, "proposal", new_proposal)
    print("current concrete types", type(admitted) is AdmittedOperation, type(new_proposal) is TypedProposal)
    AdmittedOperation.verify_identity(admitted)
    ExecutionLease.verify_identity(lease)
    print("base artifact verification PASSED")
    print("recorded arguments", original_wire["arguments_json"])
    print("actual arguments", admitted.arguments)
    gate = DomainLifecycleAdmission(environment_run=env, environment_id="nao_fake", lifecycle_ledger=ledger)
    print("lease reuse", gate.request_execution(admitted).execution_lease == lease)
    calls = []
    def handler(args):
        calls.append(args)
        return OwnerExecutionResult("native:serializer-spoof", True, (FRESH_EFFECT,))
    decision = owner_for(catalog, env, ledger, handler).execute(lease)
    print("native arguments", calls)
    print("issued current receipt", decision.receipt is not None)
    evidence = (decision.receipt.evidence,)
    acceptance = TaskAcceptanceEvaluator().evaluate(compiled.effect_obligations, evidence)
    ledger.record(AcceptanceFact(compiled, evidence, acceptance))
    print("terminal status", LifecycleLedger(ledger.path).replay(admitted.trace_id).terminal_status)
    print("restart failure stage", LifecycleLedger(ledger.path).replay(admitted.trace_id).failure_stage)
