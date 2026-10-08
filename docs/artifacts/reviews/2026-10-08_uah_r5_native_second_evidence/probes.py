"""Independent predeclared R5 public probes; all native effects stay in temp dirs."""

import copy
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event, Thread

from ab_harness_synthetic import ExactNoteOracle, NativeNotesOwner, NoteObservation
from test_prompt_compiler import _inputs


def rejected(action):
    try:
        action()
    except (ValueError, UnicodeError, TypeError) as error:
        return type(error).__name__ + ": " + str(error)
    raise AssertionError("input accepted unexpectedly")


def setup(path, expected="review note\n"):
    task = _inputs()["compiled_task"]
    oracle = ExactNoteOracle.issue(task, expected_text=expected, owner_id="notes")
    owner = NativeNotesOwner(path, task=task, oracle=oracle, owner_id="notes")
    return task, oracle, owner


results = []


def run(name, action):
    with TemporaryDirectory(prefix="uah-r5-second-probe-") as directory:
        try:
            detail = action(Path(directory))
            results.append({"name": name, "status": "PASS", "detail": detail})
        except Exception as error:
            results.append({"name": name, "status": "FAIL", "detail": repr(error)})


def content(path, expected, actual):
    _, _, owner = setup(path, expected)
    written = owner.write_note("write", actual)
    closure = owner.finalize("verify", lambda value: None)
    assert written.owner_result().observed_effects == ("note_written",)
    assert closure.owner_result().succeeded == (expected.encode() == actual.encode())
    assert closure.owner_result().observed_effects == (
        ("note_content_matches",) if expected == actual else ()
    )
    return {"expected": expected, "actual": actual, "closure_matches": closure.owner_result().succeeded}


for label, expected, actual in (
    ("exact", "review note\n", "review note\n"),
    ("wrong", "review note\n", "wrong\n"),
    ("empty", "", ""),
    ("unicode_exact", "Café\n", "Café\n"),
    ("unicode_decomposed", "Café\n", "Cafe\u0301\n"),
    ("newline_crlf", "review note\n", "review note\r\n"),
    ("newline_missing", "review note\n", "review note"),
    ("newline_extra", "review note\n", "review note\n\n"),
    ("bom", "review note\n", "\ufeffreview note\n"),
    ("nul", "review note\n", "review\x00note\n"),
):
    run(label, lambda path, expected=expected, actual=actual: content(path, expected, actual))


def missing(path):
    _, _, owner = setup(path, "")
    observation = owner.finalize("verify", lambda value: None)
    assert observation.observed_bytes is None
    assert not observation.owner_result().succeeded
    assert owner.phase == "callback_completed"
    return "Absent file differs from an empty file; callback completion is not acceptance."


run("missing_empty_oracle", missing)


def preexisting(path):
    _, _, owner = setup(path)
    (path / "note.txt").write_bytes(b"review note\n")
    observation = owner.finalize("verify", lambda value: None)
    assert observation.owner_result().observed_effects == ("note_content_matches",)
    return "Preexisting exact content yields only closure-content effect, no write occurrence."


run("no_owner_write_preexisting_content", preexisting)


def invalid_utf8(path):
    task, _, owner = setup(path)
    source_error = rejected(lambda: ExactNoteOracle.issue(task, expected_text="\ud800", owner_id="notes"))
    write_error = rejected(lambda: owner.write_note("bad-write", "\ud800"))
    owner.write_note("write", "review note\n")
    (path / "note.txt").write_bytes(b"\xff")
    observation = owner.finalize("verify", lambda value: None)
    assert observation.observed_bytes == b"\xff"
    assert not observation.owner_result().succeeded
    return [source_error, write_error, "Invalid native bytes retained and mismatch."]


run("invalid_utf8", invalid_utf8)


def identity(path):
    task, oracle, owner = setup(path)
    observation = owner.write_note("write", "review note\n")
    errors = []
    errors.append(rejected(lambda: NativeNotesOwner(path, task=task, oracle=oracle, owner_id="foreign")))
    other = _inputs(prohibited_effects=("unrelated",))["compiled_task"]
    errors.append(rejected(lambda: NativeNotesOwner(path, task=other, oracle=oracle, owner_id="notes")))
    for field, value in (("expected_text", "wrong"), ("owner_id", "foreign"), ("evaluator_version", "unknown"), ("compiled_task_json", "{}"), ("oracle_id", "")):
        body = oracle.to_dict()
        body[field] = value
        errors.append(rejected(lambda body=body: ExactNoteOracle.from_dict(body, expected_id=oracle.oracle_id)))
    for key in ("environment_run_id", "compiled_task_id"):
        body = oracle.to_dict()
        compiled = json.loads(body["compiled_task_json"])
        compiled[key] = "foreign"
        body["compiled_task_json"] = json.dumps(compiled, sort_keys=True, separators=(",", ":"))
        errors.append(rejected(lambda body=body: ExactNoteOracle.from_dict(body, expected_id=oracle.oracle_id)))
    for key in ("task_id", "trace_id"):
        body = oracle.to_dict()
        compiled = json.loads(body["compiled_task_json"])
        compiled["task_spec"][key] = "foreign"
        body["compiled_task_json"] = json.dumps(compiled, sort_keys=True, separators=(",", ":"))
        errors.append(rejected(lambda body=body: ExactNoteOracle.from_dict(body, expected_id=oracle.oracle_id)))
    for key in oracle.to_dict():
        body = oracle.to_dict()
        del body[key]
        errors.append(rejected(lambda body=body: ExactNoteOracle.from_dict(body, expected_id=oracle.oracle_id)))
    foreign = ExactNoteOracle.issue(task, expected_text="foreign", owner_id="notes")
    errors.append(rejected(lambda: NoteObservation.from_dict(observation.to_dict(), oracle=foreign, expected_id=observation.observation_id)))
    for key in observation.to_dict():
        body = observation.to_dict()
        del body[key]
        errors.append(rejected(lambda body=body: NoteObservation.from_dict(body, oracle=oracle, expected_id=observation.observation_id)))
    for key, value in (("operation_id", "foreign"), ("kind", "closure_content"), ("observed_hex", "77726f6e67"), ("oracle_json", "{}"), ("observation_id", "")):
        body = observation.to_dict()
        body[key] = value
        errors.append(rejected(lambda body=body: NoteObservation.from_dict(body, oracle=oracle, expected_id=observation.observation_id)))
    return {"rejections": len(errors), "messages": errors}


run("task_owner_source_and_observation_identity", identity)


def retained_and_alias(path):
    task, oracle, owner = setup(path)
    original_oracle_body = copy.deepcopy(oracle.to_dict())
    object.__setattr__(oracle, "expected_text", "wrong")
    object.__setattr__(task.task_spec, "goal", "mutated caller goal")
    write = owner.write_note("write", "review note\n")
    closure = owner.finalize("verify", lambda value: None)
    assert closure.owner_result().succeeded
    body = closure.to_dict()
    mutated_export = closure.to_dict()
    mutated_export["observed_hex"] = "00"
    result = closure.owner_result()
    result.payload["observed_hex"] = "00"
    assert closure.owner_result().succeeded
    (path / "note.txt").unlink()
    restored_oracle = ExactNoteOracle.from_dict(original_oracle_body, expected_id=original_oracle_body["oracle_id"])
    restored = NoteObservation.from_dict(body, oracle=restored_oracle, expected_id=closure.observation_id)
    assert restored.owner_result() == closure.owner_result()
    assert write.owner_result().observed_effects == ("note_written",)
    return "Detached caller task/oracle and exports; complete restoration after file deletion."


run("alias_and_reconstruction", retained_and_alias)


def duplicates(path):
    _, _, owner = setup(path)
    owner.write_note("op", "review note\n")
    rejected(lambda: owner.write_note("op", "wrong"))
    rejected(lambda: owner.finalize("op", lambda value: None))
    for identifier in ("", " ", None, 42):
        rejected(lambda identifier=identifier: owner.write_note(identifier, "wrong"))
    assert (path / "note.txt").read_bytes() == b"review note\n"
    owner.finalize("verify", lambda value: None)
    rejected(lambda: owner.finalize("verify-other", lambda value: None))
    return "Duplicate/unnamed write and closure IDs reject without mutation."


run("duplicates_and_operation_names", duplicates)


def callback_states(path):
    _, _, owner = setup(path)
    owner.write_note("write", "review note\n")

    def callback(observation):
        assert owner.phase == "closing"
        rejected(lambda: owner.write_note("intervening", "wrong"))
        rejected(lambda: owner.finalize("recursive", lambda value: None))
        raise RuntimeError("unconfirmed callback")

    try:
        owner.finalize("verify", callback)
    except RuntimeError:
        pass
    else:
        raise AssertionError("callback exception swallowed")
    assert owner.phase == "callback_failed"
    rejected(lambda: owner.write_note("after", "wrong"))
    assert (path / "note.txt").read_bytes() == b"review note\n"
    return "Reentrant mutation/closure rejected; exception preserved; failure remains fenced."


run("callback_mutation_and_failure", callback_states)


def concurrent_same_owner(path):
    _, _, owner = setup(path)
    owner.write_note("write", "review note\n")
    entered, attempting, release = Event(), Event(), Event()
    evidence = []

    def callback(observation):
        entered.set()
        assert release.wait(2)
        evidence.append(observation.owner_result().succeeded)

    def finalize():
        owner.finalize("verify", callback)

    def writer():
        attempting.set()
        evidence.append(rejected(lambda: owner.write_note("intervening", "wrong")))

    closer = Thread(target=finalize)
    closer.start()
    assert entered.wait(2)
    competitor = Thread(target=writer)
    competitor.start()
    assert attempting.wait(2)
    release.set()
    closer.join(2)
    competitor.join(2)
    assert not closer.is_alive() and not competitor.is_alive()
    assert (path / "note.txt").read_bytes() == b"review note\n"
    assert len(evidence) == 2
    return evidence


run("concurrent_same_owner", concurrent_same_owner)


def second_owner(path):
    task, oracle, owner = setup(path)
    competitor = NativeNotesOwner(path, task=task, oracle=oracle, owner_id="notes")
    owner.write_note("write", "review note\n")
    details = {}

    def callback(observation):
        mutation = competitor.write_note("intervening", "wrong")
        details["competitor_write_succeeded"] = mutation.owner_result().succeeded
        details["closure_matches"] = observation.owner_result().succeeded
        details["live_bytes_during_callback"] = (path / "note.txt").read_bytes().hex()

    owner.finalize("verify", callback)
    details["phase"] = owner.phase
    assert (path / "note.txt").read_bytes() == b"review note\n", details
    return details


run("second_owner_same_workspace_fence", second_owner)


def links(path):
    workspace = path / "workspace"
    workspace.mkdir()
    external = path / "outside.txt"
    external.write_bytes(b"untouched")
    _, _, owner = setup(workspace)
    (workspace / "note.txt").symlink_to(external)
    rejected(lambda: owner.write_note("symlink", "wrong"))
    assert external.read_bytes() == b"untouched"
    (workspace / "note.txt").unlink()
    os.link(external, workspace / "note.txt")
    observation = owner.write_note("hardlink", "review note\n")
    assert external.read_bytes() == b"untouched", {
        "outside_bytes": external.read_bytes().hex(),
        "write_succeeded": observation.owner_result().succeeded,
    }


run("preexisting_symlink_and_hardlink", links)

print(json.dumps(results, indent=2, ensure_ascii=True))
print("SUMMARY", len(results), "cases;", sum(item["status"] == "FAIL" for item in results), "failures")
