"""SPR02 public budget entry contract; no source repair or private ledger writes."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Barrier

import pytest

from ab_harness import DomainLifecycleAdmission, TaskBudgets
from ab_harness.contracts import OwnerExecutionResult
from ab_harness.environment import InProcessEnvironmentOwner
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.runtime_controls import TaskBudgetAuthority
from test_model_invocation import _RecordedProvider, _authority, _invocation_fixture
from test_two_stage_admission import (
    _admission_fixture,
    _prepared_execution_lease,
    _proposal,
    _semantic_admission,
)


class ReadObservedLedger(LifecycleLedger):
    """Observe only the public read seam, without touching ledger internals."""

    def __init__(self, path):
        super().__init__(path)
        self.read_calls = 0

    def events(self):
        self.read_calls += 1
        return super().events()


class SynchronizedReadLedger(LifecycleLedger):
    """Force two initial public snapshots before either consumer can append."""

    def __init__(self, path, barrier):
        super().__init__(path)
        self.barrier = barrier
        self.first_read = True

    def events(self):
        events = super().events()
        if self.first_read:
            self.first_read = False
            self.barrier.wait(timeout=10)
        return events


@dataclass
class BudgetCase:
    ledger: LifecycleLedger
    trace_id: str
    resource: str
    existing: str
    fresh: str
    third: str
    calls: object

    def request(self, subject, units=1):
        return dict(
            trace_id=self.trace_id,
            resource=self.resource,
            subject_id=subject,
            units=units,
        )

    def call_count(self):
        return self.calls.calls if self.resource == "model_call" else len(self.calls)


def _grants(ledger, resource):
    return tuple(
        event
        for event in ledger.events()
        if event.event_type == "budget_granted" and event.data["resource"] == resource
    )


def _debit(ledger, resource):
    return sum(event.data["units"] for event in _grants(ledger, resource))


def _decision(authority, method, request):
    result = getattr(authority, method)(**request)
    return result.decision if method == "assess" else result


@pytest.fixture(params=("model_call", "tool_call"))
def budget_case(request, tmp_path):
    """Each case first proves one genuine admitted/ready fake dispatch."""
    if request.param == "model_call":
        ledger, _, lease, prompt = _invocation_fixture(tmp_path, model_calls=2)
        provider = _RecordedProvider(ledger)
        authority = _authority(ledger, provider, clock=lambda: "2026-10-04T10:00:02Z")
        output = authority.invoke(lease, prompt, invocation_id="unit:positive")
        assert output.output["arguments"] == {"text": "hello"}
        assert provider.calls == 1
        assert ledger.replay_agent_run(lease.agent_run_id).status == "ready"
        case = BudgetCase(
            ledger,
            prompt.trace_id,
            request.param,
            "unit:positive",
            "unit:fresh",
            "unit:third",
            provider,
        )
    else:
        compiled, catalog, run = _admission_fixture(
            budgets=TaskBudgets(
                wall_time_seconds=90, model_calls=2, tool_calls=2, retry_attempts=0
            )
        )
        ledger = LifecycleLedger(tmp_path / "tool.jsonl")
        first = _prepared_execution_lease(
            ledger=ledger,
            compiled=compiled,
            catalog=catalog,
            environment_run=run,
            operation_id="unit:positive",
        )
        for subject in ("unit:fresh", "unit:third"):
            proposal = _proposal(compiled, operation_id=subject)
            ledger.record(proposal)
            admitted = (
                _semantic_admission(catalog)
                .admit(compiled, proposal)
                .admitted_operation
            )
            assert admitted is not None
            ledger.record(admitted)
            decision = DomainLifecycleAdmission(
                environment_run=run,
                environment_id="nao_fake",
                lifecycle_ledger=ledger,
            ).request_execution(admitted)
            assert decision.execution_lease is not None
        calls = []

        def handler(arguments):
            events = ledger.events()
            assert events[-1].event_type == "execution_started"
            assert events[-2].event_type == "budget_granted"
            assert events[-1].commit_id == events[-2].commit_id
            calls.append(arguments)
            return OwnerExecutionResult(
                evidence_ref="fake-nao://evidence/unit-boundary",
                succeeded=True,
                observed_effects=("fresh detector-backed result returned",),
            )

        owner = InProcessEnvironmentOwner(
            environment_id="nao_fake",
            environment_run=run,
            catalog=catalog,
            lifecycle_ledger=ledger,
            handlers={"fake_nao.skills:find_object": handler},
        )
        assert owner.execute(first).accepted
        assert calls == [{"label": "cup"}]
        case = BudgetCase(
            ledger,
            compiled.trace_id,
            request.param,
            "unit:positive",
            "unit:fresh",
            "unit:third",
            calls,
        )
    assert _debit(case.ledger, case.resource) == 1
    assert len(_grants(case.ledger, case.resource)) == 1
    return case


def test_genuine_positive_dispatch_is_debited_once(budget_case):
    case = budget_case
    decision = TaskBudgetAuthority(case.ledger).consume(**case.request(case.existing))
    assert decision.outcome == "granted"
    assert (decision.units, decision.consumed_before, decision.consumed_after) == (
        1,
        0,
        1,
    )
    assert case.call_count() == 1
    assert _debit(case.ledger, case.resource) == 1


@pytest.mark.parametrize("method", ("assess", "consume"))
@pytest.mark.parametrize("existing", (False, True), ids=("fresh", "existing"))
@pytest.mark.parametrize("units", (True, 1.0), ids=("bool", "float"))
def test_malformed_units_reject_before_public_ledger_lookup(
    budget_case, method, existing, units
):
    case = budget_case
    ledger = ReadObservedLedger(case.ledger.path)
    authority = TaskBudgetAuthority(ledger)
    subject = case.existing if existing else case.fresh
    positive = _decision(authority, method="assess", request=case.request(subject))
    assert positive.outcome == "granted"
    assert positive.units == 1
    assert ledger.read_calls > 0  # The spy observes a genuine valid lookup.
    before_events = ledger.events()
    before_bytes = ledger.path.read_bytes()
    reads_before = ledger.read_calls
    error = None
    result = None
    try:
        result = _decision(authority, method, case.request(subject, units))
    except ValueError as caught:
        error = caught
    reads_after = ledger.read_calls
    assert ledger.path.read_bytes() == before_bytes
    assert ledger.events() == before_events
    assert _debit(ledger, case.resource) == 1
    assert case.call_count() == 1
    assert error is not None, (
        "malformed units returned a decision; exact-1 identity reused="
        f"{result.decision_id == positive.decision_id}; no additional debit"
    )
    assert reads_after == reads_before, "malformed units reached public ledger lookup"


@pytest.mark.parametrize("method", ("assess", "consume"))
@pytest.mark.parametrize("units", (2, 0, -1))
def test_changed_existing_units_reject_without_append_or_extra_debit(
    budget_case, method, units
):
    case = budget_case
    authority = TaskBudgetAuthority(case.ledger)
    positive = _decision(authority, method, case.request(case.existing))
    assert positive.outcome == "granted"
    before = case.ledger.events(), case.ledger.path.read_bytes()
    with pytest.raises(ValueError):
        _decision(authority, method, case.request(case.existing, units))
    assert (case.ledger.events(), case.ledger.path.read_bytes()) == before
    assert _debit(case.ledger, case.resource) == 1
    assert case.call_count() == 1


@pytest.mark.parametrize("method", ("assess", "consume"))
def test_exact_one_reuses_decision_and_debit_after_file_reopen(budget_case, method):
    case = budget_case
    original = TaskBudgetAuthority(case.ledger).consume(**case.request(case.existing))
    before = case.ledger.events(), case.ledger.path.read_bytes()
    reopened = LifecycleLedger(case.ledger.path)
    replayed = _decision(
        TaskBudgetAuthority(reopened), method, case.request(case.existing)
    )
    assert replayed.decision_id == original.decision_id
    assert replayed.to_dict() == original.to_dict()
    assert (reopened.events(), reopened.path.read_bytes()) == before
    assert _debit(reopened, case.resource) == 1
    assert case.call_count() == 1


def test_valid_exact_limit_then_exhaustion_preserves_debit(budget_case):
    case = budget_case
    authority = TaskBudgetAuthority(case.ledger)
    before = case.ledger.events(), case.ledger.path.read_bytes()
    at_limit = authority.assess(**case.request(case.fresh))
    assert not at_limit.already_recorded
    assert at_limit.decision.outcome == "granted"
    assert (at_limit.decision.consumed_before, at_limit.decision.consumed_after) == (
        1,
        2,
    )
    assert (case.ledger.events(), case.ledger.path.read_bytes()) == before
    granted = authority.consume(**case.request(case.fresh))
    assert granted.decision_id == at_limit.decision.decision_id
    assert granted.limit == 2
    exhausted = authority.consume(**case.request(case.third))
    assert exhausted.outcome == "exhausted"
    assert (exhausted.consumed_before, exhausted.consumed_after) == (2, 2)
    before = case.ledger.events(), case.ledger.path.read_bytes()
    reopened = LifecycleLedger(case.ledger.path)
    replayed = TaskBudgetAuthority(reopened).consume(**case.request(case.third))
    assert replayed.decision_id == exhausted.decision_id
    assert (reopened.events(), reopened.path.read_bytes()) == before
    assert len(_grants(reopened, case.resource)) == 2
    assert _debit(reopened, case.resource) == 2
    assert case.call_count() == 1


def test_synchronized_public_duplicate_consumers_record_one_winning_grant(budget_case):
    case = budget_case
    barrier = Barrier(2)
    ledgers = [SynchronizedReadLedger(case.ledger.path, barrier) for _ in range(2)]

    def consume(ledger):
        return TaskBudgetAuthority(ledger).consume(**case.request(case.fresh))

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(consume, ledger) for ledger in ledgers]
        decisions = [future.result(timeout=15) for future in futures]
    assert decisions[0].decision_id == decisions[1].decision_id
    assert decisions[0].outcome == "granted"
    reopened = LifecycleLedger(case.ledger.path)
    fresh_grants = [
        event
        for event in _grants(reopened, case.resource)
        if event.data["subject_id"] == case.fresh
    ]
    assert len(fresh_grants) == 1
    assert len(_grants(reopened, case.resource)) == 2
    assert _debit(reopened, case.resource) == 2
    assert case.call_count() == 1
