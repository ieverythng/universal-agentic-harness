"""Executable residual: raw iterable O1 projection does not verify stale identity."""

import json

from ab_harness.lifecycle import LifecycleLedger, TaskIngressFact, TaskStartedFact
from ab_harness.observatory import project_observatory, render_observatory


def main():
    ledger = LifecycleLedger(clock=lambda: "2026-10-08T14:40:00Z")
    lineage = dict(
        environment_run_id="environment-run:r3-residual",
        task_id="task:r3-residual",
        trace_id="trace:r3-residual",
        domain_contract_pack_revision="sha256:r3-synthetic-domain",
    )
    ledger.record(TaskStartedFact(
        **lineage, environment_ingress_id="ingress:r3-start",
        ingress_artifact_id="artifact:r3-start", decision_id="decision:r3-start",
    ))
    ledger.record(TaskIngressFact(
        **lineage, environment_ingress_id="ingress:r3-resume",
        ingress_artifact_id="artifact:r3-resume", decision_id="decision:r3-resume",
        action="resume_task",
    ))
    events = ledger.events()
    control = project_observatory(events).traces[0].status.value
    stale_id = events[-1].event_id
    object.__setattr__(events[-1], "event_type", "terminal_task_accepted")
    residual = project_observatory(events).traces[0].status.value
    ledger_status = project_observatory(ledger).traces[0].status.value
    try:
        render_observatory(events)
    except ValueError as error:
        render_rejected = "identity does not match" in str(error)
    else:
        render_rejected = False
    assert control == ledger_status == "open"
    assert residual == "accepted" and events[-1].event_id == stale_id
    assert render_rejected
    print(json.dumps(dict(
        probe_id="R3-O1-RAW-ITERABLE-IDENTITY", control_status=control,
        mutated_raw_projection_status=residual, ledger_status=ledger_status,
        foreign_render_rejected=render_rejected, stale_event_id=stale_id,
        limitation="raw iterable projection only; no ARCH-02 label change",
    ), sort_keys=True))


if __name__ == "__main__":
    main()
