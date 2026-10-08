"""Execute-before-reading public control for R5 independent second review."""

from tempfile import TemporaryDirectory
from pathlib import Path
from test_prompt_compiler import _inputs
from ab_harness_synthetic import ExactNoteOracle, NativeNotesOwner

task = _inputs()["compiled_task"]
oracle = ExactNoteOracle.issue(task, expected_text="review note\n", owner_id="review-owner")
with TemporaryDirectory(prefix="uah-r5-second-control-") as temporary:
    owner = NativeNotesOwner(Path(temporary), task=task, oracle=oracle, owner_id="review-owner")
    written = owner.write_note("review-write", "review note\n")
    callback_values = []
    observed = owner.finalize("review-verify", lambda value: callback_values.append(value))
    assert written.observed_bytes == b"review note\n"
    assert observed.observed_bytes == b"review note\n"
    assert written.to_dict() != observed.to_dict()
    assert callback_values == [observed]
    print("INITIAL PUBLIC VALID CONTROL PASS")
    print("phase:", owner.phase)
    print("write:", written.to_dict())
    print("closure:", observed.to_dict())
