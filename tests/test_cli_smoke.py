import json

from ab_harness_nao.cli import main
from ab_harness_nao.smoke import run_smoke


def test_smoke_runs_accept_reject_and_replay_canaries():
    report = run_smoke()

    assert report["status"] == "passed"
    assert report["configuration"]["configuration_id"].startswith(
        "uah-config:sha256:"
    )
    assert report["checks"] == {
        "accepted_path": True,
        "rejected_path": True,
        "terminal_counterexample": True,
        "verified_trace_digest": True,
    }
    assert report["accepted_case"]["evidence_owner"] == "object_finder"
    assert report["rejected_case"]["failure_stage"] == "semantic_admission"
    assert report["counterexample_case"] == {
        "passed": False,
        "failure_stage": "evidence_closure",
        "acceptance_status": "rejected",
        "missing_observables": ["fresh detector-backed result returned"],
    }
    assert report["verified_trace_digest"].startswith(
        "verified-trace-digest:sha256:"
    )


def test_module_cli_prints_machine_readable_smoke_report(capsys):
    exit_code = main()

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "passed"
