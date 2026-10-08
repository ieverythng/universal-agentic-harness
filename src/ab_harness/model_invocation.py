"""Provider-neutral calls under exact model leases and recorded task budgets."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Callable, Protocol, TYPE_CHECKING

from ab_harness.model_allocator import ModelLease
from ab_harness.prompt_compiler import CompiledPrompt

if TYPE_CHECKING:
    from ab_harness.lifecycle import LifecycleLedger
    from ab_harness.runtime_controls import BudgetDecision


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise ValueError("model invocation artifacts require finite JSON") from exc


def _identity(prefix: str, value: object) -> str:
    return (
        prefix
        + ":sha256:"
        + hashlib.sha256(_canonical_json(value).encode()).hexdigest()
    )


def _timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ValueError("invocation timestamp must be aware ISO time") from exc
    if parsed.tzinfo is None:
        raise ValueError("invocation timestamp must be aware ISO time")
    return parsed


@dataclass(frozen=True)
class ModelInvocationRequest:
    """One immutable call joining an actor, compiled prompt, and task lineage."""

    invocation_id: str
    lease: ModelLease
    compiled_prompt: CompiledPrompt
    requested_at: str
    task_id: str
    trace_id: str
    request_id: str = field(init=False)

    def __post_init__(self) -> None:
        self.lease.verify_identity()
        self.compiled_prompt.verify_identity()
        for name in ("invocation_id", "task_id", "trace_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError("invocation identities must be nonempty strings")
        if (
            self.compiled_prompt.agent_id != self.lease.agent_id
            or self.compiled_prompt.environment_run_id != self.lease.environment_run_id
            or self.compiled_prompt.task_id != self.task_id
            or self.compiled_prompt.trace_id != self.trace_id
        ):
            raise ValueError("invocation prompt lineage does not match lease and task")
        requested = _timestamp(self.requested_at)
        if (
            not _timestamp(self.lease.acquired_at)
            <= requested
            < _timestamp(self.lease.expires_at)
        ):
            raise ValueError("model invocation requires an unexpired model lease")
        object.__setattr__(
            self, "request_id", _identity("model-invocation-request", self._payload())
        )

    @property
    def agent_run_id(self) -> str:
        return self.lease.agent_run_id

    @property
    def environment_run_id(self) -> str:
        return self.lease.environment_run_id

    @property
    def compiled_task_id(self) -> str:
        return self.compiled_prompt.compiled_task_id

    def _payload(self) -> dict[str, object]:
        return {
            "schema_version": "uah.model_invocation_request/v1",
            "invocation_id": self.invocation_id,
            "lease": self.lease.to_dict(),
            "compiled_prompt": self.compiled_prompt.to_dict(),
            "requested_at": self.requested_at,
            "task_id": self.task_id,
            "trace_id": self.trace_id,
        }

    def verify_identity(self) -> None:
        if self.request_id != _identity("model-invocation-request", self._payload()):
            raise ValueError("model invocation request identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {"request_id": self.request_id, **self._payload()}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> ModelInvocationRequest:
        data = dict(payload)
        identity = data.pop("request_id")
        if data.pop("schema_version") != "uah.model_invocation_request/v1":
            raise ValueError("unsupported model invocation request schema")
        data["lease"] = ModelLease.from_dict(data["lease"])
        data["compiled_prompt"] = CompiledPrompt.from_dict(data["compiled_prompt"])
        result = cls(**data)
        if result.request_id != identity:
            raise ValueError("model invocation request identity does not match content")
        return result


@dataclass(frozen=True)
class RawModelOutput:
    """Canonical provider output with provenance and no execution authority."""

    request: ModelInvocationRequest
    output_json: str
    completed_at: str
    raw_output_artifact_id: str = field(init=False)

    def __post_init__(self) -> None:
        self.request.verify_identity()
        try:
            value = json.loads(self.output_json)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "raw model output must contain canonical finite JSON"
            ) from exc
        if self.output_json != _canonical_json(value):
            raise ValueError("raw model output must contain canonical finite JSON")
        if _timestamp(self.completed_at) < _timestamp(self.request.requested_at):
            raise ValueError("model output predates invocation")
        object.__setattr__(
            self,
            "raw_output_artifact_id",
            _identity("raw-model-output", self._payload()),
        )

    @property
    def invocation_id(self) -> str:
        return self.request.invocation_id

    @property
    def output(self) -> object:
        return json.loads(self.output_json)

    @classmethod
    def capture(
        cls, request: ModelInvocationRequest, value: object, *, completed_at: str
    ) -> RawModelOutput:
        return cls(request, _canonical_json(value), completed_at)

    def _payload(self) -> dict[str, object]:
        return {
            "schema_version": "uah.raw_model_output/v1",
            "request": self.request.to_dict(),
            "output_json": self.output_json,
            "completed_at": self.completed_at,
        }

    def verify_identity(self) -> None:
        if self.raw_output_artifact_id != _identity(
            "raw-model-output", self._payload()
        ):
            raise ValueError("raw model output identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {
            "raw_output_artifact_id": self.raw_output_artifact_id,
            **self._payload(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> RawModelOutput:
        data = dict(payload)
        identity = data.pop("raw_output_artifact_id")
        if data.pop("schema_version") != "uah.raw_model_output/v1":
            raise ValueError("unsupported raw model output schema")
        data["request"] = ModelInvocationRequest.from_dict(data["request"])
        result = cls(**data)
        if result.raw_output_artifact_id != identity:
            raise ValueError("raw model output identity does not match content")
        return result


@dataclass(frozen=True)
class ModelInvocationFailure:
    """Provider failure provenance without exception messages or credentials."""

    request: ModelInvocationRequest
    failure_code: str
    diagnostic_ref: str
    failed_at: str
    failure_id: str = field(init=False)

    def __post_init__(self) -> None:
        self.request.verify_identity()
        if not self.failure_code.isidentifier():
            raise ValueError("invocation failure code must be an exception type")
        if not re.fullmatch(
            r"invocation-diagnostic:sha256:[a-f0-9]{64}", self.diagnostic_ref
        ):
            raise ValueError("invocation diagnostic must be a hashed reference")
        if _timestamp(self.failed_at) < _timestamp(self.request.requested_at):
            raise ValueError("model failure predates invocation")
        object.__setattr__(
            self, "failure_id", _identity("model-invocation-failure", self._payload())
        )

    @property
    def invocation_id(self) -> str:
        return self.request.invocation_id

    @classmethod
    def capture(
        cls, request: ModelInvocationRequest, error: Exception, *, failed_at: str
    ) -> ModelInvocationFailure:
        code = type(error).__name__
        diagnostic = _identity(
            "invocation-diagnostic", {"failure_type": code, "message": str(error)}
        )
        return cls(request, code, diagnostic, failed_at)

    def _payload(self) -> dict[str, object]:
        return {
            "schema_version": "uah.model_invocation_failure/v1",
            "request": self.request.to_dict(),
            "failure_code": self.failure_code,
            "diagnostic_ref": self.diagnostic_ref,
            "failed_at": self.failed_at,
        }

    def verify_identity(self) -> None:
        if self.failure_id != _identity("model-invocation-failure", self._payload()):
            raise ValueError("model invocation failure identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {"failure_id": self.failure_id, **self._payload()}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> ModelInvocationFailure:
        data = dict(payload)
        identity = data.pop("failure_id")
        if data.pop("schema_version") != "uah.model_invocation_failure/v1":
            raise ValueError("unsupported model invocation failure schema")
        data["request"] = ModelInvocationRequest.from_dict(data["request"])
        result = cls(**data)
        if result.failure_id != identity:
            raise ValueError("model invocation failure identity does not match content")
        return result


@dataclass(frozen=True)
class ModelInvocationStarted:
    """Atomic authorization to consume one model call before provider work."""

    request: ModelInvocationRequest
    budget_decision: BudgetDecision

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Recheck exact request and budget pairing at ledger admission."""

        self.request.verify_identity()
        budget = self.budget_decision
        budget.verify_identity()
        if (
            budget.resource != "model_call"
            or type(budget.units) is not int
            or budget.units != 1
            or budget.outcome != "granted"
            or budget.subject_id != self.request.invocation_id
            or budget.compiled_task_id != self.request.compiled_task_id
            or budget.environment_run_id != self.request.environment_run_id
            or budget.task_id != self.request.task_id
            or budget.trace_id != self.request.trace_id
        ):
            raise ValueError(
                "invocation start requires its exact granted model-call budget"
            )


class ProviderPort(Protocol):
    """External model boundary; responses are untrusted JSON values."""

    def invoke(self, request: ModelInvocationRequest) -> object: ...


def invocation_spec(
    fact: ModelInvocationRequest | RawModelOutput | ModelInvocationFailure,
) -> dict[str, object]:
    if isinstance(fact, ModelInvocationRequest):
        request = fact
        event_type = "model_invocation_started"
        artifact_id = request.request_id
        data = {"request": request.to_dict()}
    elif isinstance(fact, RawModelOutput):
        request = fact.request
        event_type = "model_invocation_completed"
        artifact_id = fact.raw_output_artifact_id
        data = fact.to_dict()
    else:
        request = fact.request
        event_type = "model_invocation_failed"
        artifact_id = fact.failure_id
        data = fact.to_dict()
    return {
        "event_type": event_type,
        "environment_run_id": request.environment_run_id,
        "task_id": request.task_id,
        "trace_id": request.trace_id,
        "operation_id": None,
        "event_scope": "task",
        "agent_run_id": request.agent_run_id,
        "artifact_refs": (
            artifact_id,
            request.compiled_prompt.compiled_prompt_id,
            request.lease.model_lease_id,
        ),
        "data": data,
    }


class ModelInvocationAuthority:
    """Record exact admission and budget consumption before calling a provider."""

    def __init__(
        self,
        ledger: LifecycleLedger,
        provider: ProviderPort,
        *,
        clock: Callable[[], str] | None = None,
    ) -> None:
        self.ledger = ledger
        self.provider = provider
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat())

    def invoke(
        self, lease: ModelLease, compiled_prompt: CompiledPrompt, *, invocation_id: str
    ) -> RawModelOutput | ModelInvocationFailure:
        from ab_harness.lifecycle import LifecycleSequenceConflict
        from ab_harness.runtime_controls import (
            BudgetExhaustedError,
            TaskBudgetAuthority,
        )

        lease.verify_identity()
        compiled_prompt.verify_identity()
        for attempt in range(2):
            events = self.ledger.events()
            previous = tuple(
                event
                for event in events
                if event.event_type
                in {
                    "model_invocation_started",
                    "model_invocation_completed",
                    "model_invocation_failed",
                }
                and event.data.get("request", {}).get("invocation_id") == invocation_id
            )
            if previous:
                request = ModelInvocationRequest.from_dict(previous[0].data["request"])
                if request.lease != lease or request.compiled_prompt != compiled_prompt:
                    raise ValueError(
                        "model invocation identity cannot change request content"
                    )
                terminal = next(
                    (
                        event
                        for event in previous
                        if event.event_type
                        in {"model_invocation_completed", "model_invocation_failed"}
                    ),
                    None,
                )
                if terminal is None:
                    raise ValueError(
                        "model invocation already started; automatic retry is forbidden"
                    )
                return (
                    RawModelOutput.from_dict(terminal.data)
                    if terminal.event_type == "model_invocation_completed"
                    else ModelInvocationFailure.from_dict(terminal.data)
                )

            actor = self.ledger.replay_agent_run(lease.agent_run_id)
            if actor.model_lease != lease or actor.status != "ready":
                raise ValueError(
                    "model invocation requires the exact ready active model lease"
                )
            if (
                compiled_prompt.agent_id != actor.manifest.agent_id
                or compiled_prompt.role_configuration_id
                != actor.manifest.role_configuration_id
                or compiled_prompt.prompt_pack_id != actor.manifest.prompt_pack_id
                or compiled_prompt.domain_contract_pack_revision
                != actor.profile.domain_contract_pack_revision
            ):
                raise ValueError(
                    "invocation prompt does not match the frozen actor role"
                )
            compiled = next(
                (
                    event
                    for event in events
                    if event.event_type == "task_compiled"
                    and event.data.get("compiled_task_id")
                    == compiled_prompt.compiled_task_id
                ),
                None,
            )
            if compiled is None or (
                compiled.environment_run_id != lease.environment_run_id
                or compiled.task_id != compiled_prompt.task_id
                or compiled.trace_id != compiled_prompt.trace_id
                or compiled.data["role_id"] != compiled_prompt.role_id
                or compiled.data["frame_id"] != compiled_prompt.frame_id
                or compiled.data["registry_version"] != compiled_prompt.registry_version
                or compiled.data["domain_contract_pack_revision"]
                != compiled_prompt.domain_contract_pack_revision
            ):
                raise ValueError("invocation requires the exact recorded compiled task")
            request = ModelInvocationRequest(
                invocation_id,
                lease,
                compiled_prompt,
                self.clock(),
                compiled_prompt.task_id,
                compiled_prompt.trace_id,
            )
            assessment = TaskBudgetAuthority(self.ledger).assess(
                trace_id=request.trace_id,
                resource="model_call",
                subject_id=invocation_id,
            )
            if assessment.already_recorded:
                if assessment.decision.outcome == "exhausted":
                    raise BudgetExhaustedError("model_call budget exhausted")
                raise ValueError(
                    "invocation budget already consumed without a matching start"
                )
            try:
                if assessment.decision.outcome == "exhausted":
                    self.ledger.record(
                        assessment.decision,
                        expected_sequence=assessment.expected_sequence,
                    )
                    raise BudgetExhaustedError("model_call budget exhausted")
                self.ledger.record(
                    ModelInvocationStarted(request, assessment.decision),
                    expected_sequence=assessment.expected_sequence,
                )
                break
            except LifecycleSequenceConflict:
                if attempt:
                    raise
        try:
            output = RawModelOutput.capture(
                request, self.provider.invoke(request), completed_at=self.clock()
            )
        except Exception as error:
            failure = ModelInvocationFailure.capture(
                request, error, failed_at=self.clock()
            )
            self.ledger.record(failure)
            return failure
        self.ledger.record(output)
        return output
