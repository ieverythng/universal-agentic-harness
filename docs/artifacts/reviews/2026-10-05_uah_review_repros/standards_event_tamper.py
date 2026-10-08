import json


try:
    from ab_harness.lifecycle import LifecycleLedger, TaskStartedFact, TaskIngressFact
    from ab_harness.observatory import render_observatory
except ImportError:
    print("BASELINE_UNAVAILABLE: LifecycleLedger/Observatory")
else:
    ledger = LifecycleLedger(clock=lambda: "2026-10-05T12:00:00Z")
    ledger.record(
        TaskStartedFact(
            "env:synthetic",
            "task:synthetic",
            "trace:synthetic",
            "ingress:start",
            "artifact:ingress:start",
            "decision:start",
            "revision:synthetic",
        )
    )
    ledger.record(
        TaskIngressFact(
            "env:synthetic",
            "task:synthetic",
            "trace:synthetic",
            "ingress:resume",
            "artifact:ingress:resume",
            "decision:resume",
            "revision:synthetic",
            "resume_task",
        )
    )
    event = ledger.events()[-1]
    old_id = event.event_id
    object.__setattr__(event, "event_type", "terminal_task_accepted")
    try:
        rendered = render_observatory(ledger)
    except Exception as exc:
        print(json.dumps({"render_result": type(exc).__name__, "message": str(exc)}))
    else:
        print(
            json.dumps(
                {
                    "render_result": "accepted",
                    "displayed_status": rendered.projection.traces[0].status.value,
                    "data_label": rendered.projection.data_label.value,
                    "event_identity_unchanged": rendered.projection.events[-1].event_id
                    == old_id,
                }
            )
        )
    try:
        ledger.replay("trace:synthetic")
    except Exception as exc:
        print(
            json.dumps(
                {"ledger_replay_result": type(exc).__name__, "message": str(exc)}
            )
        )
