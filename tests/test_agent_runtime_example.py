from scripts.render_agent_runtime_example import OUTPUT, example_ledger, expected_html

from ab_harness.observatory import ObservatoryDataLabel, project_observatory


def test_synthetic_o1_runtime_example_keeps_two_environments_and_actor_histories_distinct():
    ledger = example_ledger()
    projection = project_observatory(ledger, data_label=ObservatoryDataLabel.SYNTHETIC)

    assert len(projection.environment_runs) == 2
    assert len(projection.agent_runs) == 2
    alpha = projection.environment_run("environment-run:synthetic-notes:alpha")
    beta = projection.environment_run("environment-run:synthetic-notes:beta")
    assert alpha.agent_run_ids == ("agent-run:synthetic-notes:alpha",)
    assert beta.agent_run_ids == ("agent-run:synthetic-notes:beta",)
    assert alpha.task_ids == ("task:synthetic-note",)
    assert beta.task_ids == ()
    event_types = tuple(event.event_type for event in ledger.events())
    assert "model_invocation_completed" in event_types
    assert "startup_preflight_failed" in event_types
    assert event_types.count("model_lease_released") == 2
    assert not set(event_types).intersection(
        {
            "semantic_admission_accepted",
            "domain_admission_leased",
            "execution_started",
            "evidence_issued",
            "terminal_task_accepted",
        }
    )
    assert all(actor.status == "standby" for actor in ledger.agent_runs())
    assert len(projection.traces) == 1
    assert projection.traces[0].status.value == "open"


def test_committed_synthetic_o1_runtime_example_is_current_and_explicitly_labeled():
    rendered = expected_html()

    assert OUTPUT.read_text(encoding="utf-8") == rendered
    assert "synthetic" in rendered
    assert "No live provider, hardware qualification, or H2 effect evidence" in rendered
