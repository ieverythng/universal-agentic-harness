import json

from ab_harness_nao.cli import main
from ab_harness_nao.smoke import run_smoke


def test_smoke_runs_accept_reject_and_workbench_canaries():
    report = run_smoke()

    assert report["status"] == "passed"
    assert report["configuration"]["configuration_id"].startswith(
        "uah-config:sha256:"
    )
    assert report["checks"] == {
        "accepted_path": True,
        "rejected_path": True,
        "workbench_support_retrieved": True,
        "workbench_counterexample_retrieved": True,
    }
    assert report["accepted_case"]["evidence_owner"] == "object_finder"
    assert report["rejected_case"]["failure_stage"] == "planner_gate"
    assert report["workbench_candidate"]["status"] == "candidate"


def test_module_cli_prints_machine_readable_smoke_report(capsys):
    exit_code = main()

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "passed"
