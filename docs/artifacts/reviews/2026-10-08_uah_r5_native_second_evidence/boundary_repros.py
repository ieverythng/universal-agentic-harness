"""Minimal public reproductions for the R5 second review boundary findings."""

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event, Thread

from ab_harness_synthetic import ExactNoteOracle, NativeNotesOwner
from test_prompt_compiler import _inputs


def new_owner(path, task, oracle):
    return NativeNotesOwner(path, task=task, oracle=oracle, owner_id="notes")


task = _inputs()["compiled_task"]
oracle = ExactNoteOracle.issue(task, expected_text="review note\n", owner_id="notes")
results = []

for reverse_order in (False, True):
    with TemporaryDirectory(prefix="uah-r5-two-owner-") as directory:
        workspace = Path(directory)
        one = new_owner(workspace, task, oracle)
        two = new_owner(workspace, task, oracle)
        closer, writer = (two, one) if reverse_order else (one, two)
        closer.write_note("write-initial", "review note\n")
        wrote = Event()
        detail = {"reverse_construction_order": reverse_order}

        def concurrent_write():
            receipt = writer.write_note("write-during-closure", "wrong")
            detail["write_succeeded"] = receipt.owner_result().succeeded
            wrote.set()

        def callback(observation):
            worker = Thread(target=concurrent_write)
            worker.start()
            detail["second_owner_wrote_before_callback_return"] = wrote.wait(2)
            worker.join(2)
            detail["closure_content_matches"] = observation.owner_result().succeeded
            detail["actual_text_before_callback_return"] = (workspace / "note.txt").read_text()

        closer.finalize("verify", callback)
        detail["phase"] = closer.phase
        detail["terminal_acceptance_asserted"] = False
        results.append(detail)

with TemporaryDirectory(prefix="uah-r5-hardlink-") as directory:
    root = Path(directory)
    workspace = root / "owned"
    workspace.mkdir()
    outside = root / "not-owned.txt"
    outside.write_text("untouched")
    os.link(outside, workspace / "note.txt")
    owner = new_owner(workspace, task, oracle)
    observation = owner.write_note("write-hardlink", "review note\n")
    results.append({
        "case": "preexisting_hardlink",
        "same_inode": outside.stat().st_ino == (workspace / "note.txt").stat().st_ino,
        "outside_text_after_write": outside.read_text(),
        "write_succeeded": observation.owner_result().succeeded,
        "external_concurrent_writer": False,
    })

print(json.dumps(results, indent=2))
