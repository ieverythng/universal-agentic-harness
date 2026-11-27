from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from ab_harness.domain_lifecycle import DomainLifecycleAdmission
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.runtime_controls import BudgetDecision
from ab_harness.runtime_controls import TaskBudgetAuthority

from test_two_stage_admission import _admission_fixture
from test_two_stage_admission import _record_task_start
from test_two_stage_admission import _proposal
from test_two_stage_admission import _semantic_admission


@pytest.mark.parametrize(
    "field", ("units", "limit", "consumed_before", "consumed_after")
)
@pytest.mark.parametrize("value", (True, 1.0))
def test_budget_artifact_requires_integer_quantities(field, value):
    fields = dict(
        compiled_task_id="compiled:synthetic",
        environment_run_id="environment:synthetic",
        task_id="task:synthetic",
        trace_id="trace:synthetic",
        resource="model_call",
        subject_id="invocation:synthetic",
        units=1,
        limit=3,
        consumed_before=0,
        consumed_after=1,
        outcome="granted",
        reason_code="within_budget",
    )
    fields[field] = value
    if field == "consumed_before":
        fields["consumed_after"] = 2
    with pytest.raises(ValueError, match="finite integer"):
        BudgetDecision.issue(**fields)


def _budget_fixture(tmp_path, file_backed, resource):
    compiled, catalog, environment_run = _admission_fixture()
    path = tmp_path / "budget.jsonl" if file_backed else None
    ledger = LifecycleLedger(path)
    _record_task_start(ledger, compiled)
    ledger.record(compiled)
    subject_id = "subject:exact-one"
    if resource == "tool_call":
        proposal = _proposal(compiled, operation_id=subject_id)
        ledger.record(proposal)
        admitted = _semantic_admission(catalog).admit(
            compiled, proposal
        ).admitted_operation
        assert admitted is not None
        ledger.record(admitted)
        lease = DomainLifecycleAdmission(
            environment_run=environment_run,
            environment_id="nao_fake",
            lifecycle_ledger=ledger,
        ).request_execution(admitted).execution_lease
        assert lease is not None
    request = dict(
        trace_id=compiled.trace_id, resource=resource, subject_id=subject_id
    )
    return ledger, path, request


@pytest.mark.parametrize("file_backed", (False, True))
@pytest.mark.parametrize("resource", ("model_call", "tool_call"))
@pytest.mark.parametrize("method", ("assess", "consume"))
@pytest.mark.parametrize("existing", (False, True))
@pytest.mark.parametrize("units", (True, 1.0))
def test_budget_entry_rejects_numeric_aliases_without_reuse_or_append(
    tmp_path, file_backed, resource, method, existing, units
):
    ledger, path, request = _budget_fixture(tmp_path, file_backed, resource)
    authority = TaskBudgetAuthority(ledger)
    if existing:
        granted = authority.consume(**request, units=1)
        assert (granted.outcome, granted.consumed_after) == ("granted", 1)
    before = ledger.events()
    before_bytes = path.read_bytes() if path else None

    with pytest.raises(ValueError):
        getattr(authority, method)(**request, units=units)

    assert ledger.events() == before
    if path:
        assert path.read_bytes() == before_bytes
        assert LifecycleLedger(path).events() == before


@pytest.mark.parametrize("resource", ("model_call", "tool_call"))
@pytest.mark.parametrize("method", ("assess", "consume"))
@pytest.mark.parametrize("units", (True, 1.0, 0, -1))
def test_bad_budget_quantity_rejects_before_file_ledger_lookup(
    tmp_path, resource, method, units
):
    path = tmp_path / "unreadable-ledger.jsonl"
    ledger = LifecycleLedger(path)
    path.write_bytes(b"not a lifecycle event\n")
    before = path.read_bytes()

    with pytest.raises(ValueError, match="positive integers"):
        getattr(TaskBudgetAuthority(ledger), method)(
            trace_id="trace:absent", resource=resource, subject_id="subject:absent",
            units=units,
        )

    assert path.read_bytes() == before


@pytest.mark.parametrize("resource", ("model_call", "tool_call"))
@pytest.mark.parametrize("method", ("assess", "consume"))
@pytest.mark.parametrize("units", (0, -1, 2))
def test_budget_subject_rejects_nonpositive_or_changed_units_without_append(
    tmp_path, resource, method, units
):
    ledger, path, request = _budget_fixture(tmp_path, True, resource)
    authority = TaskBudgetAuthority(ledger)
    granted = authority.consume(**request, units=1)
    before = path.read_bytes()
    before_events = ledger.events()

    with pytest.raises(ValueError):
        getattr(authority, method)(**request, units=units)

    assert path.read_bytes() == before
    assert ledger.events() == before_events
    assert authority.consume(**request, units=1).decision_id == granted.decision_id
    assert path.read_bytes() == before


@pytest.mark.parametrize("resource", ("model_call", "tool_call"))
def test_exact_budget_reuse_after_reload_preserves_one_identity_and_debit(
    tmp_path, resource
):
    ledger, path, request = _budget_fixture(tmp_path, True, resource)
    granted = TaskBudgetAuthority(ledger).consume(**request, units=1)
    before = path.read_bytes()
    reopened = LifecycleLedger(path)
    authority = TaskBudgetAuthority(reopened)

    assessment = authority.assess(**request, units=1)
    repeated = authority.consume(**request, units=1)

    assert assessment.already_recorded
    assert assessment.decision == repeated == granted
    assert repeated.consumed_after == 1
    assert path.read_bytes() == before
    grants = [e for e in reopened.events() if e.event_type == "budget_granted"]
    assert len(grants) == 1
    assert grants[0].data["decision_id"] == granted.decision_id


@pytest.mark.parametrize("resource", ("model_call", "tool_call"))
def test_competing_consumers_preserve_single_budget_identity_and_debit(
    tmp_path, resource
):
    ledger, path, request = _budget_fixture(tmp_path, True, resource)
    peers = [TaskBudgetAuthority(LifecycleLedger(path)) for _ in range(2)]
    barrier = Barrier(2)

    def consume(authority):
        barrier.wait(timeout=5)
        return authority.consume(**request, units=1)

    with ThreadPoolExecutor(max_workers=2) as pool:
        decisions = tuple(pool.map(consume, peers))

    assert decisions[0] == decisions[1]
    assert decisions[0].consumed_after == 1
    reopened = LifecycleLedger(path)
    grants = [e for e in reopened.events() if e.event_type == "budget_granted"]
    assert len(grants) == 1
    assert grants[0].data["decision_id"] == decisions[0].decision_id
    before = path.read_bytes()
    assert TaskBudgetAuthority(reopened).consume(**request, units=1) == decisions[0]
    assert path.read_bytes() == before
