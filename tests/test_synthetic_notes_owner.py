import json

import pytest

from ab_harness_synthetic import ExactNoteOracle, NativeNotesOwner, NoteObservation
from test_prompt_compiler import _inputs


def test_native_note_write_and_closure_are_distinct_actual_observations(tmp_path):
    task = _inputs()["compiled_task"]
    oracle = ExactNoteOracle.issue(
        task, expected_text="Requested note\n", owner_id="notes"
    )
    owner = NativeNotesOwner(tmp_path, task=task, oracle=oracle, owner_id="notes")

    write = owner.write_note("operation:write", "Requested note\n")
    recorded = []
    closure = owner.finalize("operation:verify", recorded.append)

    assert write.observed_bytes == b"Requested note\n"
    assert write.owner_result().observed_effects == ("note_written",)
    assert closure.owner_result().observed_effects == ("note_content_matches",)
    assert write.observation_id != closure.observation_id
    assert recorded == [closure]
    assert owner.phase == "callback_completed"


@pytest.fixture
def native_owner(tmp_path):
    task = _inputs()["compiled_task"]
    oracle = ExactNoteOracle.issue(task, expected_text="Café\n", owner_id="notes")
    return NativeNotesOwner(
        tmp_path, task=task, oracle=oracle, owner_id="notes"
    ), oracle


@pytest.mark.parametrize(
    "text", ("wrong", "Café", "Café\r\n", "\ufeffCafé\n", "Cafe\u0301\n")
)
def test_native_occurrence_does_not_prove_wrong_current_content(native_owner, text):
    owner, _ = native_owner
    write = owner.write_note("write:wrong", text)
    closure = owner.finalize("verify:wrong", lambda _: None)
    assert write.owner_result().observed_effects == ("note_written",)
    assert not closure.owner_result().succeeded
    assert closure.owner_result().observed_effects == ()


def test_missing_mutation_cannot_supply_write_or_closure_effects(native_owner):
    owner, _ = native_owner
    closure = owner.finalize("verify:missing", lambda _: None)
    assert closure.observed_bytes is None
    assert not closure.owner_result().succeeded
    assert closure.owner_result().observed_effects == ()


def test_overwrite_preserves_historical_write_and_fails_closure(native_owner, tmp_path):
    owner, _ = native_owner
    write = owner.write_note("write:correct", "Café\n")
    (tmp_path / "note.txt").write_bytes(b"replacement")
    closure = owner.finalize("verify:changed", lambda _: None)
    assert write.observed_bytes == "Café\n".encode()
    assert write.owner_result().succeeded
    assert not closure.owner_result().succeeded


def test_owner_writes_are_fenced_between_read_and_callback_completion(native_owner):
    owner, _ = native_owner
    owner.write_note("write:correct", "Café\n")

    def attempt_write(observation):
        assert owner.phase == "closing"
        with pytest.raises(ValueError, match="fenced"):
            owner.write_note("write:intervening", "wrong")
        assert observation.owner_result().succeeded

    closure = owner.finalize("verify:fenced", attempt_write)
    assert closure.owner_result().succeeded
    with pytest.raises(ValueError, match="fenced"):
        owner.write_note("write:after", "wrong")
    with pytest.raises(ValueError, match="once"):
        owner.finalize("verify:repeat", lambda _: None)


def test_failed_callback_is_not_completed_closure(native_owner):
    owner, _ = native_owner
    owner.write_note("write:correct", "Café\n")

    def fail(_):
        raise RuntimeError("unconfirmed commit")

    with pytest.raises(RuntimeError, match="unconfirmed"):
        owner.finalize("verify:failed", fail)
    assert owner.phase == "callback_failed"
    with pytest.raises(ValueError, match="fenced"):
        owner.write_note("write:after_failure", "wrong")


def test_retained_observation_reconstructs_without_live_file(native_owner, tmp_path):
    owner, oracle = native_owner
    owner.write_note("write:correct", "Café\n")
    closure = owner.finalize("verify:correct", lambda _: None)
    oracle_body = json.loads(json.dumps(oracle.to_dict()))
    observation_body = json.loads(json.dumps(closure.to_dict()))
    (tmp_path / "note.txt").unlink()
    restored_oracle = ExactNoteOracle.from_dict(
        oracle_body, expected_id=oracle.oracle_id
    )
    restored = NoteObservation.from_dict(
        observation_body, oracle=restored_oracle, expected_id=closure.observation_id
    )
    assert restored.owner_result() == closure.owner_result()


@pytest.mark.parametrize(
    "field,value",
    (
        ("expected_text", "wrong"),
        ("owner_id", "foreign"),
        ("evaluator_version", "other"),
        ("compiled_task_json", "{}"),
        ("oracle_id", ""),
    ),
)
def test_oracle_source_cannot_change_under_original_reference(
    native_owner, field, value
):
    _, oracle = native_owner
    body = oracle.to_dict()
    body[field] = value
    with pytest.raises(ValueError):
        ExactNoteOracle.from_dict(body, expected_id=oracle.oracle_id)


def test_missing_retained_source_is_an_explicit_error(native_owner):
    _, oracle = native_owner
    body = oracle.to_dict()
    del body["expected_text"]
    with pytest.raises(ValueError, match="missing"):
        ExactNoteOracle.from_dict(body, expected_id=oracle.oracle_id)


def test_foreign_owner_and_task_cannot_reuse_oracle(native_owner, tmp_path):
    _, oracle = native_owner
    task = _inputs()["compiled_task"]
    with pytest.raises(ValueError, match="belong"):
        NativeNotesOwner(tmp_path, task=task, oracle=oracle, owner_id="foreign")
    foreign = _inputs(prohibited_effects=("unrelated",))["compiled_task"]
    with pytest.raises(ValueError, match="belong"):
        NativeNotesOwner(tmp_path, task=foreign, oracle=oracle, owner_id="notes")


def test_expected_source_is_detached_before_native_actions(native_owner):
    owner, oracle = native_owner
    object.__setattr__(oracle, "expected_text", "wrong")
    owner.write_note("write:correct", "Café\n")
    assert owner.finalize("verify:correct", lambda _: None).owner_result().succeeded


def test_repeated_or_unnamed_native_operations_do_not_mutate(native_owner, tmp_path):
    owner, _ = native_owner
    owner.write_note("write:once", "Café\n")
    for operation_id in ("write:once", ""):
        with pytest.raises(ValueError):
            owner.write_note(operation_id, "wrong")
    assert (tmp_path / "note.txt").read_bytes() == "Café\n".encode()


def test_owner_rejects_preexisting_symlink(native_owner, tmp_path):
    owner, _ = native_owner
    external = tmp_path / "other.txt"
    external.write_text("untouched")
    (tmp_path / "note.txt").symlink_to(external)
    with pytest.raises(ValueError, match="symlink"):
        owner.write_note("write:link", "wrong")
    assert external.read_text() == "untouched"


def test_empty_text_is_an_exact_supported_source(tmp_path):
    task = _inputs()["compiled_task"]
    oracle = ExactNoteOracle.issue(task, expected_text="", owner_id="notes")
    owner = NativeNotesOwner(tmp_path, task=task, oracle=oracle, owner_id="notes")
    owner.write_note("write:empty", "")
    assert owner.finalize("verify:empty", lambda _: None).owner_result().succeeded
