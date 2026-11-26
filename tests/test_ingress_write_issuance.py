"""Public write-crossing controls using real commands, never private state."""

import pytest

from ab_harness import LifecycleLedger
from ab_harness.lifecycle import AcceptanceFact
from test_ingress_authority_boundary import CASES
from test_ingress_authority_boundary import acceptance_feedback, acceptance_fixture
from test_ingress_authority_boundary import authority_for, feedback, start_task


@pytest.mark.parametrize("action,ingress_type,event_type", CASES)
def test_actual_issued_ingress_command_is_affine_to_exact_ledger(
    tmp_path, monkeypatch, action, ingress_type, event_type
):
    origin_path = tmp_path / "origin.jsonl"
    origin, issuer, run, start = start_task(origin_path)
    destination_path = tmp_path / "destination.jsonl"
    destination, _, _, destination_start = start_task(destination_path)
    prefix = destination_path.read_bytes()
    assert prefix == origin_path.read_bytes()
    assert destination_start == start
    commands = []
    record = origin.record

    def observe_record(command, **kwargs):
        commands.append(command)
        return record(command, **kwargs)

    monkeypatch.setattr(origin, "record", observe_record)
    ingress = feedback(run, action, ingress_type)
    admitted = issuer.admit(run, ingress)
    assert admitted.action == action
    assert admitted.reason_code == "matched_registered_task"
    assert origin.events()[-1].event_type == event_type
    assert len(commands) == 1
    # Treat the actual public record input as opaque: no private type/fields.
    with pytest.raises(ValueError, match="authority-bound"):
        destination.record(commands[0])
    assert destination_path.read_bytes() == prefix
    assert LifecycleLedger(destination_path).events() == destination.events()
    assert len(destination.events()) == 1


@pytest.mark.parametrize("action,ingress_type,event_type", CASES)
def test_authentic_acceptance_wins_after_issuer_reads_nonterminal_prefix(
    tmp_path, monkeypatch, action, ingress_type, event_type
):
    reference_path = tmp_path / "accepted-reference.jsonl"
    acceptance_facts = []
    record = LifecycleLedger.record

    def observe_acceptance(ledger, fact, **kwargs):
        commit = record(ledger, fact, **kwargs)
        if isinstance(fact, AcceptanceFact):
            acceptance_facts.append(fact)
        return commit

    with monkeypatch.context() as observation:
        observation.setattr(LifecycleLedger, "record", observe_acceptance)
        reference, run, pack, start, compiled = acceptance_fixture(
            reference_path, "accepted"
        )
    assert len(acceptance_facts) == 1
    accepted = reference.events()[-1]
    assert accepted.event_type == "terminal_task_accepted"
    assert accepted.commit_size == accepted.commit_index
    acceptance_size = accepted.commit_size
    # NEW current synthetic trace: copy the authentic pre-acceptance commit prefix.
    # No historical fixture or reference stream is altered or rehashed.
    complete = reference_path.read_bytes()
    prefix = b"".join(complete.splitlines(keepends=True)[:-acceptance_size])
    path = tmp_path / "interleaved.jsonl"
    path.write_bytes(prefix)
    ledger = LifecycleLedger(path)
    assert ledger.events() == reference.events()[:-acceptance_size]
    assert ledger.replay(compiled.trace_id).terminal_status is None
    terminal_writer = LifecycleLedger(path, clock=lambda: accepted.recorded_at)
    issuer = authority_for(ledger, run, pack)
    ingress = acceptance_feedback(run, start, action, ingress_type)
    write_crossings = []
    terminal_bytes = []

    def acceptance_before_ingress(command, **kwargs):
        # admit has already checked the genuine nonterminal task when it calls record.
        write_crossings.append(command)
        assert path.read_bytes() == prefix
        assert ledger.replay(compiled.trace_id).terminal_status is None
        terminal_writer.record(acceptance_facts[0])
        terminal_bytes.append(path.read_bytes())
        return record(ledger, command, **kwargs)

    monkeypatch.setattr(ledger, "record", acceptance_before_ingress)
    decision = issuer.admit(run, ingress)
    assert len(write_crossings) == 1
    assert decision.action == "reject"
    assert decision.reason_code == "task_terminal"
    assert decision.task_status == "accepted"
    assert (decision.task_id, decision.trace_id) == (start.task_id, start.trace_id)
    assert path.read_bytes() == terminal_bytes[0]
    assert path.read_bytes().startswith(prefix)
    assert ledger.events() == reference.events()
    assert not any(event.event_type == event_type for event in ledger.events())
    assert LifecycleLedger(path).replay(compiled.trace_id).terminal_status == "accepted"
    assert reference_path.read_bytes() == complete
