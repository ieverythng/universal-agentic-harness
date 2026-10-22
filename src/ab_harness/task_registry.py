"""Environment-scoped task lineage projected from the common ledger."""

from __future__ import annotations

from dataclasses import dataclass

from ab_harness.lifecycle import LifecycleLedger
from ab_harness.lifecycle import TraceEvent


@dataclass(frozen=True)
class TaskLineage:
    """Immutable identity assigned to one domain task in an environment run."""

    environment_run_id: str
    task_id: str
    trace_id: str
    starting_environment_ingress_id: str
    starting_ingress_artifact_id: str
    starting_decision_id: str
    domain_contract_pack_revision: str

    def __post_init__(self) -> None:
        required = {
            "environment_run_id": self.environment_run_id,
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "starting_environment_ingress_id": self.starting_environment_ingress_id,
            "starting_ingress_artifact_id": self.starting_ingress_artifact_id,
            "starting_decision_id": self.starting_decision_id,
            "domain_contract_pack_revision": self.domain_contract_pack_revision,
        }
        missing = tuple(name for name, value in required.items() if not value.strip())
        if missing:
            raise ValueError(
                "task lineage fields must not be empty: %s" % ", ".join(missing)
            )


class EnvironmentTaskRegistry:
    """Read task lineage projected from one lifecycle ledger."""

    def __init__(self, ledger: LifecycleLedger | None = None) -> None:
        if ledger is not None and type(ledger) is not LifecycleLedger:
            raise TypeError("task registry requires a concrete lifecycle ledger")
        self._ledger = LifecycleLedger() if ledger is None else ledger

    def lineage_for_ingress(
        self,
        *,
        environment_run_id: str,
        environment_ingress_id: str,
    ) -> TaskLineage | None:
        """Return refreshed lineage for one task-bearing ingress, if recorded."""

        lineage_by_ingress, _lineage_by_task = (
            EnvironmentTaskRegistry._project_ledger(self)
        )
        return lineage_by_ingress.get(
            (environment_run_id, environment_ingress_id)
        )

    def lineage_for_task(
        self,
        *,
        environment_run_id: str,
        task_id: str,
    ) -> TaskLineage | None:
        """Return refreshed lineage for one environment-scoped task, if known."""

        _lineage_by_ingress, lineage_by_task = (
            EnvironmentTaskRegistry._project_ledger(self)
        )
        return lineage_by_task.get((environment_run_id, task_id))

    def terminal_status(self, lineage: TaskLineage) -> str | None:
        """Return the replay-derived terminal status for recorded lineage."""

        ledger = EnvironmentTaskRegistry._concrete_ledger(self)
        return LifecycleLedger.replay(ledger, lineage.trace_id).terminal_status

    def require_start(
        self,
        *,
        environment_run_id: str,
        environment_ingress_id: str,
        ingress_artifact_id: str,
        decision_id: str,
        domain_contract_pack_revision: str,
        task_id: str,
        trace_id: str,
    ) -> TaskLineage:
        """Return the recorded start lineage or reject caller-authored authority."""

        events = EnvironmentTaskRegistry._validated_events(self)
        lineage_by_ingress, _lineage_by_task = (
            EnvironmentTaskRegistry._project_events(events)
        )
        lineage = lineage_by_ingress.get(
            (environment_run_id, environment_ingress_id)
        )
        if lineage is None:
            raise ValueError("task-start ingress is not recorded in lifecycle ledger")
        if lineage.starting_environment_ingress_id != environment_ingress_id:
            raise ValueError("recorded ingress is not the task-start ingress")
        if lineage.starting_ingress_artifact_id != ingress_artifact_id:
            raise ValueError("recorded task-start ingress artifact does not match")
        if lineage.starting_decision_id != decision_id:
            raise ValueError("recorded task-start decision does not match")
        if lineage.domain_contract_pack_revision != domain_contract_pack_revision:
            raise ValueError("recorded task-start contract revision does not match")
        if lineage.task_id != task_id or lineage.trace_id != trace_id:
            raise ValueError("task-start ingress lineage does not match decision")
        LifecycleLedger.require_authoritative_task_start_in_snapshot(
            events,
            trace_id=trace_id,
            decision_id=decision_id,
        )
        return lineage

    def _project_ledger(
        self,
    ) -> tuple[
        dict[tuple[str, str], TaskLineage],
        dict[tuple[str, str], TaskLineage],
    ]:
        """Build one caller-owned projection from a consistent ledger snapshot."""

        return EnvironmentTaskRegistry._project_events(
            EnvironmentTaskRegistry._validated_events(self)
        )

    @staticmethod
    def _concrete_ledger(registry: EnvironmentTaskRegistry) -> LifecycleLedger:
        ledger = registry._ledger
        if type(ledger) is not LifecycleLedger:
            raise TypeError("task registry requires a concrete lifecycle ledger")
        return ledger

    @staticmethod
    def _validated_events(
        registry: EnvironmentTaskRegistry,
    ) -> tuple[TraceEvent, ...]:
        """Read the owner-validated ledger snapshot without virtual dispatch."""

        ledger = EnvironmentTaskRegistry._concrete_ledger(registry)
        return LifecycleLedger.validated_events(ledger)

    @staticmethod
    def _project_events(
        events: tuple[TraceEvent, ...],
    ) -> tuple[
        dict[tuple[str, str], TaskLineage],
        dict[tuple[str, str], TaskLineage],
    ]:
        """Build fresh lineage maps from one owner-validated event snapshot."""

        lineage_by_ingress: dict[tuple[str, str], TaskLineage] = {}
        lineage_by_task: dict[tuple[str, str], TaskLineage] = {}
        for event in events:
            if event.event_type == "task_started":
                ingress_id = str(event.data["environment_ingress_id"])
                lineage = TaskLineage(
                    environment_run_id=event.environment_run_id,
                    task_id=event.task_id,
                    trace_id=event.trace_id,
                    starting_environment_ingress_id=ingress_id,
                    starting_ingress_artifact_id=str(event.data["ingress_artifact_id"]),
                    starting_decision_id=str(event.data["decision_id"]),
                    domain_contract_pack_revision=str(
                        event.data["domain_contract_pack_revision"]
                    ),
                )
                ingress_key = (event.environment_run_id, ingress_id)
                task_key = (event.environment_run_id, event.task_id)
                if ingress_key in lineage_by_ingress:
                    raise ValueError("duplicate task-start ingress in lifecycle ledger")
                if task_key in lineage_by_task:
                    raise ValueError("duplicate task lineage in lifecycle ledger")
                lineage_by_ingress[ingress_key] = lineage
                lineage_by_task[task_key] = lineage
            elif event.event_type in {"task_resumed", "task_notified"}:
                ingress_id = str(event.data["environment_ingress_id"])
                task_key = (event.environment_run_id, event.task_id)
                try:
                    lineage = lineage_by_task[task_key]
                except KeyError as exc:
                    raise ValueError(
                        "existing-task ingress precedes task start"
                    ) from exc
                ingress_key = (event.environment_run_id, ingress_id)
                if ingress_key in lineage_by_ingress:
                    raise ValueError("duplicate task ingress in lifecycle ledger")
                lineage_by_ingress[ingress_key] = lineage
        return lineage_by_ingress, lineage_by_task
