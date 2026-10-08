# Exact execution record

Date: 2026-10-08. Native-only R5 independent reviewer.
Temporary snapshot: /tmp/uah-r5-native-primary-Lte2MA
The current src and tests were copied once into after; those copies were copied into before and only src/ab_harness_synthetic and tests/test_synthetic_notes_owner.py were removed from before.
All note workspace mutations occurred in tempfile.TemporaryDirectory under the temporary snapshot. No production workspace note was written.

## Initial execution before implementation/test inspection

Command:
PYTHONPATH=/tmp/uah-r5-native-primary-Lte2MA/after/src .venv/bin/python -m pytest /tmp/uah-r5-native-primary-Lte2MA/after/tests/test_environment_ingress.py /tmp/uah-r5-native-primary-Lte2MA/after/tests/test_synthetic_notes_owner.py -q --disable-warnings --basetemp=/tmp/uah-r5-native-primary-Lte2MA/pytest-control

Result: 50 passed in 0.22s. The copied positive test performs actual native write_note and finalize after _inputs builds a public TaskIngressAuthority decision and CompiledTask. Its implementation was read only after this execution.

The first baseline import probe using PYTHONPATH found the real checkout through the editable install. That result was invalid baseline evidence and was discarded.

## Isolated absent-package baseline

Command:
.venv/bin/python -S -c 'import sys, importlib.util; sys.path[:] = ["/tmp/uah-r5-native-primary-Lte2MA/before/src", "/home/juanbeck/universal-agentic-harness/.venv/lib/python3.12/site-packages"] + [p for p in sys.path if p and "universal-agentic-harness" not in p]; print(importlib.util.find_spec("ab_harness_synthetic")); import pytest; raise SystemExit(pytest.main(["/tmp/uah-r5-native-primary-Lte2MA/before/tests/test_environment_ingress.py", "-q", "--basetemp=/tmp/uah-r5-native-primary-Lte2MA/pytest-before"]))'

Result:
None
28 passed in 0.14s.

The -S baseline disables editable .pth processing; only copied core and explicitly supplied dependencies are present. No native implementation exists on before, so no native behavioral parity is claimed.

Command:
diff -qr /tmp/uah-r5-native-primary-Lte2MA/before/src /tmp/uah-r5-native-primary-Lte2MA/after/src

Result at initial copied control, before execution artifacts appeared:
Only in /tmp/uah-r5-native-primary-Lte2MA/after/src: ab_harness_synthetic
Exit status 1, expected for the addition.

## Independent probes

48 fixed-control and adversarial cases, 42 PASS and 6 FAIL. Five failures are variants of one nested compiled-body/hash mechanism; one is same-workspace native-owner fencing. probe_output.txt is unabridged output from an unchanged exact rerun for preservation. First run and rerun agree.

Exact command:
.venv/bin/python -S -c 'import sys, runpy; sys.path.insert(0,"/home/juanbeck/universal-agentic-harness/.venv/lib/python3.12/site-packages"); runpy.run_path("/tmp/uah-r5-native-primary-Lte2MA/probe.py", run_name="__main__")'

The executable probe starts with copied src/tests; imports the unchanged public fixture helper only for valid setup; and builds independently distinct A/B public TaskIngressAuthority task starts for multi-entity controls. The exact script is retained as probe.txt to avoid adding an unrelated Python source file to the repository. To replay it, copy that text to probe.py beside the before/after temporary snapshots, then execute the recorded command with the new temporary path.

Exit status 0 belongs to the probe reporter, not to a successful gate: its explicit FAIL count is 6.

## Frozen hashes verified before and after probes

src/ab_harness_synthetic/__init__.py 14f9b4c6a84029250aa9c1602f320c167e51f7eb1bc4932cf479ec300ddab83d
src/ab_harness_synthetic/notes.py bed451276c769cacb10befaac54c8347932ac9c70471f834e1d878c5b3277642
tests/test_synthetic_notes_owner.py 2391e2273d9c97cf43871025fbcee4e0b1c2df35ec460e0453a005cbe6391e36

Live and copied scoped files matched at both checks. Core source was never changed. The root agent owns setup/precommit/renderer integration checks; this reviewer did not run them or imply they pass.
