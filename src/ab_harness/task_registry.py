"""Environment-scoped task lineage projected from the common ledger."""

from __future__ import annotations

from dataclasses import dataclass

from ab_harness.lifecycle import LifecycleLedger
from ab_harness.lifecycle import TaskIngressFact
from ab_harness.lifecycle import TaskStartedFact


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


class DuplicateEnvironmentIngressError(ValueError):
    """Raised when a task-bearing ingress was already recorded."""

    def __init__(self, lineage: TaskLineage) -> None:
        super().__init__(lineage.starting_environment_ingress_id)
        self.lineage = lineage


class TaskAlreadyRegisteredError(ValueError):
    """Raised when a second ingress tries to start the same task."""

    def __init__(self, lineage: TaskLineage) -> None:
        super().__init__(lineage.task_id)
        self.lineage = lineage


class UnknownTaskError(KeyError):
    """Raised when existing-task ingress has no environment-scoped lineage."""


class TaskTerminalError(ValueError):
    """Raised when ingress targets a task with a terminal judgment."""

    def __init__(self, lineage: TaskLineage, status: str) -> None:
        super().__init__(status)
        self.lineage = lineage
        self.status = status


class EnvironmentTaskRegistry:
    """Route task ingress through lineage projected from one lifecycle ledger."""

    def __init__(self, ledger: LifecycleLedger | None = None) -> None:
        self.ledger = ledger or LifecycleLedger()
        self._lineage_by_ingress: dict[tuple[str, str], TaskLineage] = {}
        self._lineage_by_task: dict[tuple[str, str], TaskLineage] = {}
        self._refresh_projection()

    def _record_policy_start(self, lineage: TaskLineage) -> None:
        """Record a start already classified by the frozen ingress policy."""

        self._refresh_projection()
        self._reject_existing_start(lineage)
        try:
            self.ledger.record(
                TaskStartedFact(
                    environment_run_id=lineage.environment_run_id,
                    task_id=lineage.task_id,
                    trace_id=lineage.trace_id,
                    environment_ingress_id=lineage.starting_environment_ingress_id,
                    ingress_artifact_id=lineage.starting_ingress_artifact_id,
                    decision_id=lineage.starting_decision_id,
                    domain_contract_pack_revision=(
                        lineage.domain_contract_pack_revision
                    ),
                )
            )
        except ValueError:
            self._refresh_projection()
            self._reject_existing_start(lineage)
            raise
        ingress_key = (
            lineage.environment_run_id,
            lineage.starting_environment_ingress_id,
        )
        task_key = (lineage.environment_run_id, lineage.task_id)
        self._lineage_by_ingress[ingress_key] = lineage
        self._lineage_by_task[task_key] = lineage

    def _reject_existing_start(self, lineage: TaskLineage) -> None:
        ingress_key = (
            lineage.environment_run_id,
            lineage.starting_environment_ingress_id,
        )
        existing = self._lineage_by_ingress.get(ingress_key)
        if existing is not None:
            raise DuplicateEnvironmentIngressError(existing)
        task_key = (lineage.environment_run_id, lineage.task_id)
        existing = self._lineage_by_task.get(task_key)
        if existing is not None:
            raise TaskAlreadyRegisteredError(existing)

    def register_existing_ingress(
        self,
        *,
        environment_run_id: str,
        environment_ingress_id: str,
        ingress_artifact_id: str,
        decision_id: str,
        domain_contract_pack_revision: str,
        task_id: str,
        trace_id: str,
        ingress_action: str,
    ) -> TaskLineage:
        self._refresh_projection()
        ingress_key = (environment_run_id, environment_ingress_id)
        existing = self._lineage_by_ingress.get(ingress_key)
        if existing is not None:
            raise DuplicateEnvironmentIngressError(existing)
        task_key = (environment_run_id, task_id)
        try:
            lineage = self._lineage_by_task[task_key]
        except KeyError as exc:
            raise UnknownTaskError(task_id) from exc
        terminal_status = self.ledger.replay(lineage.trace_id).terminal_status
        if terminal_status is not None:
            raise TaskTerminalError(lineage, terminal_status)
        if lineage.trace_id != trace_id:
            raise ValueError("existing-task ingress trace does not match lineage")
        if lineage.domain_contract_pack_revision != domain_contract_pack_revision:
            raise ValueError("existing-task ingress contract revision does not match")
        fact = TaskIngressFact(
            environment_run_id=environment_run_id,
            task_id=task_id,
            trace_id=lineage.trace_id,
            environment_ingress_id=environment_ingress_id,
            ingress_artifact_id=ingress_artifact_id,
            decision_id=decision_id,
            domain_contract_pack_revision=domain_contract_pack_revision,
            action=ingress_action,
        )
        try:
            self.ledger.record(fact)
        except ValueError:
            self._refresh_projection()
            existing = self._lineage_by_ingress.get(ingress_key)
            if existing is not None:
                raise DuplicateEnvironmentIngressError(existing) from None
            raise
        self._lineage_by_ingress[ingress_key] = lineage
        return lineage

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

        self._refresh_projection()
        lineage = self._lineage_by_ingress.get(
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
        return lineage

    def _refresh_projection(self) -> None:
        self._lineage_by_ingress.clear()
        self._lineage_by_task.clear()
        for event in self.ledger.events():
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
                if ingress_key in self._lineage_by_ingress:
                    raise ValueError("duplicate task-start ingress in lifecycle ledger")
                if task_key in self._lineage_by_task:
                    raise ValueError("duplicate task lineage in lifecycle ledger")
                self._lineage_by_ingress[ingress_key] = lineage
                self._lineage_by_task[task_key] = lineage
            elif event.event_type in {"task_resumed", "task_notified"}:
                ingress_id = str(event.data["environment_ingress_id"])
                task_key = (event.environment_run_id, event.task_id)
                try:
                    lineage = self._lineage_by_task[task_key]
                except KeyError as exc:
                    raise ValueError(
                        "existing-task ingress precedes task start"
                    ) from exc
                ingress_key = (event.environment_run_id, ingress_id)
                if ingress_key in self._lineage_by_ingress:
                    raise ValueError("duplicate task ingress in lifecycle ledger")
                self._lineage_by_ingress[ingress_key] = lineage
