"""Historical inspection is not current authority; see fixture provenance.md.

Only scratch copies are opened by the ledger. Altered streams below are explicitly
adversarial current inputs, never evidence of recovered historical behavior.
These checks detect retained current provenance, not universal history forgery:
fully stripped/rehashed records can match old shapes under trusted file custody.
"""

import hashlib
import json
from pathlib import Path

import pytest

from ab_harness.domain_lifecycle import ExecutionLease
from ab_harness.lifecycle import ExecutionStartedFact
from ab_harness.lifecycle import LifecycleLedger
from ab_harness.lifecycle import TaskStartedFact
from ab_harness.lifecycle import TraceEvent
from ab_harness.observatory import project_observatory
from ab_harness.proposal_admission import AdmittedOperation
from ab_harness.runtime_controls import TaskBudgetAuthority
from ab_harness.task_registry import EnvironmentTaskRegistry


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "historical_replay"
CASES = (
    (
        "baseline-public-ledger.jsonl",
        2303,
        2,
        "3fa6f142bc300f87b9653f8db7fadbdcae73223e7e29cd48e6880316ce91b5e5",
        None,
        None,
    ),
    (
        "base-accepted.jsonl",
        12370,
        10,
        "4c0b970c1d2d0687745e9f2acf84b028b885f82bfd29f51b12218e7ddfb4f0b9",
        "accepted",
        "verified-trace-digest:sha256:c10fb8218a46f99184db39d0dd99dbb26c350a339a64836e57165f72ce501a3d",
    ),
    (
        "base-nao-ledger.jsonl",
        12372,
        10,
        "1994743080033c29ec7e93f5714e30da83373c52d32e8e4d2fe509261c609de7",
        "accepted",
        None,
    ),
    (
        "current-nao-ledger.jsonl",
        16617,
        11,
        "dfef58c0a4827e2f584e9b23184ed4c458f717a0215ae68ec591e1b33baf43b3",
        "accepted",
        "verified-trace-digest:sha256:c26202fdaa0218e3fcb85fade644a386596fad117b0282c8f0088544a12fec27",
    ),
    (
        "new-nov11-pinned-old-execution-failed.jsonl",
        8326,
        7,
        "f6e006bb49ff66537b550125ac6e1146ad203646ae7ef15b29e8fb113855a601",
        None,
        None,
    ),
)
HISTORICAL = tuple(case[0] for case in (*CASES[:3], CASES[4]))
CURRENT = CASES[3][0]


def fixture_bytes(name):
    case = next(case for case in CASES if case[0] == name)
    data = (FIXTURES / name).read_bytes()
    assert len(data) == case[1]
    assert hashlib.sha256(data).hexdigest() == case[3]
    return data


def scratch_copy(tmp_path, name):
    data = fixture_bytes(name)
    path = tmp_path / name
    path.write_bytes(data)
    return path, data


@pytest.mark.parametrize(
    "name,size,count,sha,status,digest_id", CASES, ids=[case[0] for case in CASES]
)
def test_original_history_survives_two_restarts_and_observatory(
    tmp_path, name, size, count, sha, status, digest_id
):
    path, original = scratch_copy(tmp_path, name)
    rows = [json.loads(line) for line in original.splitlines()]
    trace_id = rows[0]["trace_id"]
    previous_digest = None
    try:
        for opening in range(3):
            ledger = LifecycleLedger(path)
            events = ledger.events()
            assert len(events) == count
            assert [event.to_dict() for event in events] == rows
            assert [event.event_id for event in events] == [
                row["event_id"] for row in rows
            ]
            assert [event.data_json for event in events] == [
                row["data_json"] for row in rows
            ]
            assert all(event.agent_run_id is None for event in events)
            replay = ledger.replay(trace_id)
            assert replay.events == events
            assert replay.terminal_status == status
            digest = replay.verified_trace_digest
            if status is None:
                assert digest is None
            else:
                assert digest is not None
                if digest_id is not None:
                    assert digest.digest_id == digest_id
                if opening:
                    assert digest.to_dict() == previous_digest
                previous_digest = digest.to_dict()
            view = project_observatory(ledger).trace(trace_id)
            assert view.events == events
            assert view.status.value == (status or "open")
            assert path.read_bytes() == original
    finally:
        assert path.read_bytes() == original
        assert fixture_bytes(name) == original


@pytest.mark.parametrize("name", [case[0] for case in CASES])
def test_authentic_start_prefix_does_not_infer_fresh_compile_authority(tmp_path, name):
    original = fixture_bytes(name)
    first_line = original.splitlines(keepends=True)[0]
    path = tmp_path / "start-prefix.jsonl"
    path.write_bytes(first_line)
    ledger = LifecycleLedger(path)
    start = ledger.events()[0]
    data = start.data
    registry = EnvironmentTaskRegistry(ledger)
    assert (
        registry.lineage_for_task(
            environment_run_id=start.environment_run_id, task_id=start.task_id
        )
        is not None
    )
    fields = dict(
        environment_run_id=start.environment_run_id,
        environment_ingress_id=data["environment_ingress_id"],
        ingress_artifact_id=data["ingress_artifact_id"],
        decision_id=data["decision_id"],
        domain_contract_pack_revision=data["domain_contract_pack_revision"],
        task_id=start.task_id,
        trace_id=start.trace_id,
    )
    if name == CURRENT:
        assert registry.require_start(**fields).trace_id == start.trace_id
    else:
        with pytest.raises(ValueError, match="authoritative task-start provenance"):
            registry.require_start(**fields)
    assert path.read_bytes() == first_line
    assert fixture_bytes(name) == original


@pytest.mark.parametrize("name", HISTORICAL)
@pytest.mark.parametrize("resource", ("model_call", "tool_call"))
def test_unavailable_historical_budget_cannot_be_assessed_or_consumed(
    tmp_path, name, resource
):
    path, original = scratch_copy(tmp_path, name)
    try:
        ledger = LifecycleLedger(path)
        trace_id = ledger.events()[0].trace_id
        authority = TaskBudgetAuthority(ledger)
        for operation in (authority.assess, authority.consume):
            with pytest.raises(
                ValueError, match="budget|policy|historical|legacy|unavailable"
            ):
                operation(
                    trace_id=trace_id, resource=resource, subject_id="fresh:unavailable"
                )
            assert path.read_bytes() == original
            assert len(ledger.events()) == len(original.splitlines())
    finally:
        assert path.read_bytes() == original


def current_lease(rows):
    admission = AdmittedOperation.from_dict(
        json.loads(rows[3]["data_json"])["admitted_operation"]
    )
    leased = json.loads(rows[4]["data_json"])
    return ExecutionLease(
        execution_lease_id=leased["execution_lease_id"],
        admitted_operation=admission,
        lease_owner_id=leased["lease_owner_id"],
        environment_attestation_id=rows[4]["artifact_refs"][2],
    )


def test_current_active_execution_still_requires_its_budget_grant(tmp_path):
    original = fixture_bytes(CURRENT)
    lines = original.splitlines(keepends=True)
    path = tmp_path / "current-before-dispatch.jsonl"
    prefix = b"".join(lines[:5])
    path.write_bytes(prefix)
    ledger = LifecycleLedger(path)
    rows = [json.loads(line) for line in lines]
    lease = current_lease(rows)
    with pytest.raises(ValueError, match="budget"):
        ledger.record(ExecutionStartedFact(lease))
    assert path.read_bytes() == prefix
    assert len(ledger.events()) == 5
    commit = ledger.start_execution(lease)
    assert [event.event_type for event in commit.events] == [
        "budget_granted",
        "execution_started",
    ]
    assert path.read_bytes().startswith(prefix)
    assert len(LifecycleLedger(path).events()) == 7


def test_current_raw_start_cannot_gain_authority_by_copying_recorded_ids(tmp_path):
    row = json.loads(fixture_bytes(CURRENT).splitlines()[0])
    data = json.loads(row["data_json"])
    path = tmp_path / "raw-start.jsonl"
    ledger = LifecycleLedger(path)
    fact = TaskStartedFact(
        environment_run_id=row["environment_run_id"],
        task_id=row["task_id"],
        trace_id=row["trace_id"],
        environment_ingress_id=data["environment_ingress_id"],
        ingress_artifact_id=data["ingress_artifact_id"],
        decision_id=data["decision_id"],
        domain_contract_pack_revision=data["domain_contract_pack_revision"],
    )
    with pytest.raises(ValueError, match="authority-bound task-start command"):
        ledger.record(fact)
    assert ledger.events() == ()
    assert not path.exists() or path.read_bytes() == b""


def canonical(value):
    return json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":"))


def write_adversarial_rows(path, rows):
    """Rehash scratch input envelopes, not product state or an expected result."""
    offset = 0
    while offset < len(rows):
        first = rows[offset]
        group = rows[offset : offset + first["commit_size"]]
        assert len(group) == first["commit_size"]
        specs = []
        for row in group:
            spec = {
                key: row[key]
                for key in (
                    "event_type",
                    "environment_run_id",
                    "task_id",
                    "trace_id",
                    "operation_id",
                    "artifact_refs",
                )
            }
            spec["data"] = json.loads(row["data_json"])
            specs.append(spec)
        payload = dict(
            first_sequence=first["sequence"],
            recorded_at=first["recorded_at"],
            specs=specs,
        )
        commit_id = (
            "lifecycle-commit:sha256:"
            + hashlib.sha256(canonical(payload).encode()).hexdigest()
        )
        for row in group:
            row["commit_id"] = commit_id
        offset += len(group)
    renamed = {}
    for row in rows:
        old_id = row.pop("event_id")
        row["parent_event_id"] = renamed.get(
            row["parent_event_id"], row["parent_event_id"]
        )
        row["event_id"] = (
            "trace-event:sha256:" + hashlib.sha256(canonical(row).encode()).hexdigest()
        )
        renamed[old_id] = row["event_id"]
        TraceEvent.from_dict(row).verify_identity()
    path.write_text("".join(canonical(row) + "\n" for row in rows), encoding="utf-8")
    return path.read_bytes()


@pytest.mark.parametrize(
    "attack", ("stripped-current-budgets", "forged-current-marker", "mixed-provenance")
)
def test_current_or_mixed_provenance_cannot_downgrade_to_unbudgeted_history(
    tmp_path, attack
):
    if attack == "forged-current-marker":
        rows = [json.loads(line) for line in fixture_bytes(HISTORICAL[0]).splitlines()]
        data = json.loads(rows[0]["data_json"])
        data["task_start_authority"] = "uah.task_ingress_authority/v1"
        rows[0]["data_json"] = canonical(data)
    else:
        rows = [json.loads(line) for line in fixture_bytes(CURRENT).splitlines()[:4]]
        if attack == "stripped-current-budgets":
            data = json.loads(rows[1]["data_json"])
            del data["budgets"]
            rows[1]["data_json"] = canonical(data)
        else:
            data = json.loads(rows[0]["data_json"])
            del data["task_start_authority"]
            rows[0]["data_json"] = canonical(data)
            data = json.loads(rows[1]["data_json"])
            del data["budgets"]
            rows[1]["data_json"] = canonical(data)
    path = tmp_path / "adversarial-current.jsonl"
    before = write_adversarial_rows(path, rows)
    with pytest.raises(ValueError, match="budget|provenance|historical|legacy|current"):
        LifecycleLedger(path)
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "attack",
    (
        "event-hash",
        "duplicate-name",
        "missing-newline",
        "invalid-utf8",
        "incomplete-commit",
    ),
)
def test_corrupt_current_control_is_rejected_without_rewriting(tmp_path, attack):
    original = fixture_bytes(CURRENT)
    if attack == "event-hash":
        damaged = original.replace(b"find_the_cup", b"find_the_cap", 1)
    elif attack == "duplicate-name":
        damaged = original.replace(b'"sequence":1,', b'"sequence":1,"sequence":1,', 1)
    elif attack == "missing-newline":
        damaged = original[:-1]
    elif attack == "invalid-utf8":
        damaged = b"\xff" + original
    else:
        damaged = b"".join(original.splitlines(keepends=True)[:-1])
    assert damaged != original
    path = tmp_path / "corrupt.jsonl"
    path.write_bytes(damaged)
    with pytest.raises(ValueError):
        LifecycleLedger(path)
    assert path.read_bytes() == damaged


@pytest.mark.parametrize("name", (CURRENT, CASES[4][0]))
def test_rehashed_unchanged_control_preserves_exact_bytes(tmp_path, name):
    original = fixture_bytes(name)
    rows = [json.loads(line) for line in original.splitlines()]
    path = tmp_path / "rehashed-control.jsonl"
    assert write_adversarial_rows(path, rows) == original
    assert len(LifecycleLedger(path).validated_events()) == len(rows)


def test_rehashed_unchanged_current_control_remains_accepted(tmp_path):
    original = fixture_bytes(CURRENT)
    rows = [json.loads(line) for line in original.splitlines()]
    path = tmp_path / "rehashed-current-control.jsonl"
    assert write_adversarial_rows(path, rows) == original
    replay = LifecycleLedger(path).replay(rows[0]["trace_id"])
    assert replay.terminal_status == "accepted"
    assert replay.verified_trace_digest.digest_id == CASES[3][5]


@pytest.mark.parametrize(
    "missing", ("failure_id", "retry_disposition", "failure_code", "failure_stage")
)
def test_new_current_failure_cannot_downgrade_to_incomplete_history(tmp_path, missing):
    # A newly produced current failure, NOT a recovered historical failure.
    lines = fixture_bytes(CURRENT).splitlines(keepends=True)
    path = tmp_path / "new-current-failure.jsonl"
    path.write_bytes(b"".join(lines[:7]))
    ledger = LifecycleLedger(path)
    lease = current_lease([json.loads(line) for line in lines])
    ledger.fail_execution(lease, RuntimeError("bounded current test failure"))
    replay = LifecycleLedger(path).replay(lease.admitted_operation.trace_id)
    assert replay.failure_stage == "execution"
    assert replay.terminal_status is None
    rows = [event.to_dict() for event in replay.events]
    assert rows[-1]["event_type"] == "execution_failed"
    data = json.loads(rows[-1]["data_json"])
    assert data["retry_disposition"] == "terminal"
    del data[missing]
    rows[-1]["data_json"] = canonical(data)
    damaged = tmp_path / "incomplete-current-failure.jsonl"
    before = write_adversarial_rows(damaged, rows)
    with pytest.raises(ValueError, match="failure"):
        LifecycleLedger(damaged)
    assert damaged.read_bytes() == before


@pytest.mark.parametrize("style", ("astra-retained-old", "sol-modern-only"))
@pytest.mark.parametrize("disposition", ("retryable", "terminal"))
def test_unavailable_historical_policy_rejects_current_failure_form(
    tmp_path, style, disposition
):
    rows = [json.loads(line) for line in fixture_bytes(CASES[4][0]).splitlines()]
    data = json.loads(rows[-1]["data_json"])
    data.update(
        failure_id="execution-failure:sha256:" + "1" * 64,
        failure_code="RuntimeError",
        failure_stage="native_execution",
        retry_disposition=disposition,
    )
    if style == "sol-modern-only":
        del data["failure_type"]
        rows[-1]["artifact_refs"] = [
            data["execution_lease_id"], data["failure_id"], data["failure_ref"]
        ]
    rows[-1]["data_json"] = canonical(data)
    path = tmp_path / "mixed-failure.jsonl"
    before = write_adversarial_rows(path, rows)
    with pytest.raises(ValueError, match="historical|policy|unavailable"):
        LifecycleLedger(path)
    assert path.read_bytes() == before


@pytest.mark.parametrize("reverse", (False, True))
def test_independent_old_failure_and_current_trace_can_share_ledger(tmp_path, reverse):
    names = (CASES[4][0], CURRENT)
    if reverse:
        names = tuple(reversed(names))
    rows = [
        json.loads(line)
        for name in names
        for line in fixture_bytes(name).splitlines()
    ]
    for sequence, row in enumerate(rows, start=1):
        row["sequence"] = sequence
    path = tmp_path / "independent-generations.jsonl"
    before = write_adversarial_rows(path, rows)
    for _opening in range(3):
        ledger = LifecycleLedger(path)
        assert len(ledger.validated_events()) == 18
        for name, status in ((CASES[4][0], None), (CURRENT, "accepted")):
            trace_id = json.loads(fixture_bytes(name).splitlines()[0])["trace_id"]
            replay = ledger.replay(trace_id)
            assert replay.terminal_status == status
            if status is None:
                assert replay.failure_stage == "execution"
                assert replay.verified_trace_digest is None
            else:
                assert replay.verified_trace_digest is not None
        assert path.read_bytes() == before


def test_genuine_current_failure_survives_two_restarts(tmp_path):
    lines = fixture_bytes(CURRENT).splitlines(keepends=True)
    path = tmp_path / "genuine-current-failure.jsonl"
    path.write_bytes(b"".join(lines[:7]))
    lease = current_lease([json.loads(line) for line in lines])
    LifecycleLedger(path).fail_execution(lease, RuntimeError("current failure control"))
    original = path.read_bytes()
    rows = [json.loads(line) for line in original.splitlines()]
    for _opening in range(3):
        ledger = LifecycleLedger(path)
        assert [event.to_dict() for event in ledger.validated_events()] == rows
        replay = ledger.replay(lease.admitted_operation.trace_id)
        assert replay.failure_stage == "execution"
        assert replay.terminal_status is None
        assert replay.verified_trace_digest is None
        assert replay.events[-1].data["retry_disposition"] == "terminal"
        view = project_observatory(ledger).trace(lease.admitted_operation.trace_id)
        assert view.status.value == "open"
        assert path.read_bytes() == original


# TODO: issuer containment for BOTH resume/notify needs independently proven
# public expected-rejection cases paired with legitimate admit controls. Source
# risk alone is not an exploit. No issuer-hardening implementation is selected.
# N7 is new Nov11 pinned-old-producer output, never recovered October history.
# Provider/dispatch/effect/retry and retained-time failure qualification remain open.


@pytest.mark.parametrize("attack", ("unknown-marker", "null-marker"))
def test_legacy_compile_requires_unmarked_original_event_generation(tmp_path, attack):
    rows = [json.loads(line) for line in fixture_bytes(HISTORICAL[0]).splitlines()]
    if attack == "unknown-marker":
        data = json.loads(rows[0]["data_json"])
        data["task_start_authority"] = "counterfeit:authority"
        rows[0]["data_json"] = canonical(data)
    else:
        data = json.loads(rows[0]["data_json"])
        data["task_start_authority"] = None
        rows[0]["data_json"] = canonical(data)
    path = tmp_path / "false-legacy-generation.jsonl"
    before = write_adversarial_rows(path, rows)
    with pytest.raises(ValueError, match="budget|provenance|historical|authority"):
        LifecycleLedger(path)
    assert path.read_bytes() == before


def test_new_nov11_old_failure_retains_failure_without_task_or_retry_judgment(tmp_path):
    name = CASES[4][0]
    path, original = scratch_copy(tmp_path, name)
    for _opening in range(3):
        ledger = LifecycleLedger(path)
        replay = ledger.replay("trace:sha256:ebe71dfb76298c1ff515df001cef1c23c7cdc948323aa2e4c8394d2f000cd9b4")
        assert replay.failure_stage == "execution"
        assert replay.terminal_status is None
        assert replay.verified_trace_digest is None
        failure = replay.events[-1]
        assert failure.data == {
            "execution_lease_id": "execution-lease:sha256:3387105a8149eac4daeebd1d1bdf22c9f34dc3c7dc0f3d801d29473ac395edc4",
            "failure_ref": "execution-failure:sha256:55b0a7e88e07decab221bdc7cabe8dde890193f663bf5a3607165fbd3204e664",
            "failure_type": "RuntimeError",
        }
        assert not any(event.event_type.startswith("retry_") for event in replay.events)
        assert path.read_bytes() == original
