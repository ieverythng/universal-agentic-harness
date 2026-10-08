"""Independent current/exact-before active-authority comparison.

Run generate using the isolated exact-before source/test paths, then inspect
using the isolated current paths. Pass an isolated output directory as argument
one and generate/inspect as argument two. For inspect, argument three is the
retained proposal_admission.py.before path. This modifies only the output ledger.
"""

import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import sys

from ab_harness import DomainLifecycleAdmission, LifecycleLedger
from ab_harness.contracts import EffectEvidence, OwnerExecutionResult
from ab_harness.environment import ExecutionReceipt
from ab_harness.proposal_admission import AdmittedOperation
from test_admitted_object_snapshot import (
    FRESH_EFFECT,
    authority_fixture,
    owner_for,
)


def outcome(call):
    try:
        return {"outcome": "accepted", "value": call()}
    except Exception as exc:
        return {
            "outcome": "rejected",
            "error": type(exc).__name__,
            "message": str(exc),
        }


directory = Path(sys.argv[1])
directory.mkdir(exist_ok=True)
if sys.argv[2] == "generate":
    _, _, _, ledger, admitted, _ = authority_fixture(directory)
    (directory / "old_admitted.json").write_text(json.dumps(admitted.to_dict()))
    records = ledger.path.read_text().splitlines()
    (directory / "old-leased.jsonl").write_text("\n".join(records) + "\n")
    ledger.path.write_text("\n".join(records[:-1]) + "\n")
    print(
        json.dumps(
            {
                "old_schema": admitted.schema_version,
                "events": len(ledger.events()),
                "path": str(ledger.path),
            }
        )
    )
else:
    compiled, catalog, environment, _, admitted, _ = authority_fixture(
        directory / "current-control"
    )
    historical = LifecycleLedger(directory / "lifecycle.jsonl")
    result = {
        "historical_read": outcome(
            lambda: {
                "events": len(historical.events()),
                "stage": historical.replay(compiled.trace_id).failure_stage,
            }
        )
    }
    old_wire = json.loads((directory / "old_admitted.json").read_text())
    result["current_deserialize_old"] = outcome(
        lambda: AdmittedOperation.from_dict(old_wire).schema_version
    )
    result["current_artifact_against_old_authority"] = outcome(
        lambda: DomainLifecycleAdmission(
            environment_run=environment,
            environment_id="nao_fake",
            lifecycle_ledger=historical,
        ).request_execution(admitted).accepted
    )
    spec = importlib.util.spec_from_file_location(
        "review_exact_old_proposal_admission", sys.argv[3],
        loader=SourceFileLoader("review_exact_old_proposal_admission", sys.argv[3]),
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    values = dict(old_wire)
    values["proposal"] = module.TypedProposal(**values["proposal"])
    values["effect_obligation_ids"] = tuple(values["effect_obligation_ids"])
    old_admitted = module.AdmittedOperation(**values)
    authority = DomainLifecycleAdmission(
        environment_run=environment,
        environment_id="nao_fake",
        lifecycle_ledger=historical,
    )
    result["exact_old_object_lease_request"] = outcome(
        lambda: authority.request_execution(old_admitted).accepted
    )
    if result["exact_old_object_lease_request"]["outcome"] == "accepted":
        lease = authority.request_execution(old_admitted).execution_lease
        owner_result = OwnerExecutionResult(
            "native:old-review", True, (FRESH_EFFECT,)
        )
        evidence = EffectEvidence(
            "native:old-review", "find_object", old_admitted.binding_id,
            "nao_fake", "object_finder", True, (FRESH_EFFECT,),
        )
        result["exact_old_object_evidence_issue"] = outcome(
            lambda: ExecutionReceipt.issue(
                lease=lease, owner_result=owner_result, evidence=evidence
            ).schema_version
        )
        result["exact_old_object_dispatch"] = outcome(
            lambda: owner_for(
                catalog, environment, historical, lambda _arguments: owner_result
            ).execute(lease).accepted
        )
        receipt = ExecutionReceipt.issue(
            lease=lease, owner_result=owner_result, evidence=evidence
        )
        historical.start_execution(lease)
        result["exact_old_object_complete_evidence"] = outcome(
            lambda: len(historical.complete_execution(receipt).events)
        )
        result["exact_old_object_replay"] = outcome(
            lambda: len(LifecycleLedger(historical.path).events())
        )
    print(json.dumps(result, sort_keys=True, indent=2))
