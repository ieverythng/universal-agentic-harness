"""Model-independent roles and declared model compatibility for H1 registration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
import re
from typing import TYPE_CHECKING

from ab_harness.contracts import ABControlBand, AbstractionFrame, AgentRoleSpec

if TYPE_CHECKING:
    from ab_harness.agent_identity import AgentManifest


@dataclass(frozen=True)
class AgentRoleConfiguration:
    """Frozen semantic scope and model requirements, without a model selection."""

    role: AgentRoleSpec
    primary_frame: AbstractionFrame
    domain_contract_pack_id: str
    domain_contract_pack_revision: str
    projected_object_ids: tuple[str, ...]
    required_model_capabilities: tuple[str, ...] = ()
    minimum_context_tokens: int = 1
    allowed_provider_kinds: tuple[str, ...] = ()
    role_configuration_id: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.role, AgentRoleSpec) or not isinstance(
            self.primary_frame, AbstractionFrame
        ):
            raise ValueError("role configuration requires a typed role and frame")
        for name, value in asdict(self.primary_frame).items():
            _required_text(value, name)
        _required_text(self.role.role_id, "role_id")
        _required_text(self.domain_contract_pack_id, "domain_contract_pack_id")
        _required_text(
            self.domain_contract_pack_revision, "domain_contract_pack_revision"
        )
        _positive_integer(self.minimum_context_tokens, "minimum_context_tokens")
        if self.role.may_claim_effects is not False:
            raise ValueError("agent roles cannot claim environment effects")
        if not isinstance(self.role.control_band, ABControlBand):
            raise ValueError("role configuration requires a typed control band")
        for level in asdict(self.role.control_band).values():
            if type(level) is not int or level < 0:
                raise ValueError("control band levels must be nonnegative integers")
        output_types = _unique_names(
            self.role.allowed_output_types, "allowed_output_types"
        )
        if not output_types:
            raise ValueError("role must declare allowed output types")
        object.__setattr__(
            self,
            "role",
            AgentRoleSpec(
                self.role.role_id, output_types, self.role.control_band, False
            ),
        )
        for name in (
            "projected_object_ids",
            "required_model_capabilities",
            "allowed_provider_kinds",
        ):
            object.__setattr__(self, name, _unique_names(getattr(self, name), name))
        object.__setattr__(self, "role_configuration_id", self._content_id())

    def _identity_payload(self) -> dict[str, object]:
        return {
            "schema_version": "uah.agent_role_configuration/v1",
            "role": asdict(self.role),
            "primary_frame": asdict(self.primary_frame),
            "domain_contract_pack_id": self.domain_contract_pack_id,
            "domain_contract_pack_revision": self.domain_contract_pack_revision,
            "projected_object_ids": self.projected_object_ids,
            "required_model_capabilities": self.required_model_capabilities,
            "minimum_context_tokens": self.minimum_context_tokens,
            "allowed_provider_kinds": self.allowed_provider_kinds,
        }

    def _content_id(self) -> str:
        encoded = json.dumps(
            self._identity_payload(),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
        return "role-configuration:sha256:" + hashlib.sha256(encoded).hexdigest()

    def verify_identity(self) -> None:
        if self.role_configuration_id != self._content_id():
            raise ValueError("role configuration identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {
            "role_configuration_id": self.role_configuration_id,
            **self._identity_payload(),
        }

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> AgentRoleConfiguration:
        _require_fields(
            value,
            {
                "schema_version",
                "role_configuration_id",
                "role",
                "primary_frame",
                "domain_contract_pack_id",
                "domain_contract_pack_revision",
                "projected_object_ids",
                "required_model_capabilities",
                "minimum_context_tokens",
                "allowed_provider_kinds",
            },
            "role configuration",
        )
        data = dict(value)
        if data.pop("schema_version") != "uah.agent_role_configuration/v1":
            raise ValueError("unsupported role configuration schema")
        identity = data.pop("role_configuration_id")
        try:
            role_data = dict(data.pop("role"))
            _require_fields(
                role_data,
                {
                    "role_id",
                    "allowed_output_types",
                    "control_band",
                    "may_claim_effects",
                },
                "role",
            )
            _require_fields(
                role_data["control_band"],
                {
                    "min_direct_level",
                    "preferred_level",
                    "max_direct_level",
                    "inspect_down_to_level",
                },
                "control band",
            )
            role_data["control_band"] = ABControlBand(**role_data["control_band"])
            data["role"] = AgentRoleSpec(**role_data)
            data["primary_frame"] = AbstractionFrame(**data["primary_frame"])
            configuration = cls(**data)
        except (TypeError, KeyError) as exc:
            raise ValueError("invalid role configuration payload") from exc
        if configuration.role_configuration_id != identity:
            raise ValueError("role configuration identity does not match content")
        return configuration


class AgentRoleConfigurationRegistry:
    """Publish frozen role definitions without allocating runtime resources."""

    def __init__(self) -> None:
        self._configurations: dict[str, AgentRoleConfiguration] = {}

    def register(self, configuration: AgentRoleConfiguration) -> AgentRoleConfiguration:
        configuration.verify_identity()
        identity = configuration.role_configuration_id
        if identity in self._configurations:
            raise ValueError("role configuration already registered: %s" % identity)
        self._configurations[identity] = configuration
        return configuration

    def get(self, role_configuration_id: str) -> AgentRoleConfiguration:
        configuration = self._configurations[role_configuration_id]
        configuration.verify_identity()
        return configuration


@dataclass(frozen=True)
class ModelConfiguration:
    """Declared model behavior pinned independently of a loaded model instance."""

    provider_kind: str
    endpoint_ref: str
    model_artifact: str
    model_revision: str
    capabilities: tuple[str, ...]
    max_context_tokens: int
    decoding_settings: tuple[tuple[str, bool | int | float | None], ...] = ()
    model_configuration_id: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "provider_kind",
            "endpoint_ref",
            "model_artifact",
            "model_revision",
        ):
            _required_text(getattr(self, name), name)
        if not re.fullmatch(r"[A-Za-z0-9_.:-]+", self.endpoint_ref):
            raise ValueError("endpoint_ref must be an opaque deployment reference")
        _positive_integer(self.max_context_tokens, "max_context_tokens")
        object.__setattr__(
            self, "capabilities", _unique_names(self.capabilities, "capabilities")
        )
        if not isinstance(self.decoding_settings, (tuple, list)):
            raise ValueError("decoding_settings must be a sequence of settings")
        settings = []
        for setting in self.decoding_settings:
            if not isinstance(setting, (tuple, list)) or len(setting) != 2:
                raise ValueError("each decoding setting must have a name and value")
            name, value = setting
            _required_text(name, "decoding setting name")
            if type(value) not in (bool, int, float, type(None)):
                raise ValueError(
                    "decoding setting values must be finite numeric or boolean scalars"
                )
            if type(value) is float and not math.isfinite(value):
                raise ValueError("decoding setting values must be finite")
            settings.append((name, value))
        if len(settings) != len({name for name, _ in settings}):
            raise ValueError("decoding setting names must be unique")
        object.__setattr__(self, "decoding_settings", tuple(sorted(settings)))
        object.__setattr__(self, "model_configuration_id", self._content_id())

    def _identity_payload(self) -> dict[str, object]:
        return {
            "schema_version": "uah.model_configuration/v1",
            "provider_kind": self.provider_kind,
            "endpoint_ref": self.endpoint_ref,
            "model_artifact": self.model_artifact,
            "model_revision": self.model_revision,
            "capabilities": self.capabilities,
            "max_context_tokens": self.max_context_tokens,
            "decoding_settings": {
                name: value for name, value in self.decoding_settings
            },
        }

    def _content_id(self) -> str:
        encoded = json.dumps(
            self._identity_payload(),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
        return "model-configuration:sha256:" + hashlib.sha256(encoded).hexdigest()

    def verify_identity(self) -> None:
        if self.model_configuration_id != self._content_id():
            raise ValueError("model configuration identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {
            "model_configuration_id": self.model_configuration_id,
            **self._identity_payload(),
        }

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> ModelConfiguration:
        _require_fields(
            value,
            {
                "schema_version",
                "model_configuration_id",
                "provider_kind",
                "endpoint_ref",
                "model_artifact",
                "model_revision",
                "capabilities",
                "max_context_tokens",
                "decoding_settings",
            },
            "model configuration",
        )
        data = dict(value)
        if data.pop("schema_version") != "uah.model_configuration/v1":
            raise ValueError("unsupported model configuration schema")
        identity = data.pop("model_configuration_id")
        if not isinstance(data["decoding_settings"], dict):
            raise ValueError("invalid model configuration decoding settings")
        data["decoding_settings"] = tuple(data["decoding_settings"].items())
        configuration = cls(**data)
        if configuration.model_configuration_id != identity:
            raise ValueError("model configuration identity does not match content")
        return configuration


class ModelConfigurationRegistry:
    """Register declared model profiles without loading or probing a provider."""

    def __init__(self) -> None:
        self._configurations: dict[str, ModelConfiguration] = {}

    def register(self, configuration: ModelConfiguration) -> ModelConfiguration:
        configuration.verify_identity()
        identity = configuration.model_configuration_id
        if identity in self._configurations:
            raise ValueError("model configuration already registered: %s" % identity)
        self._configurations[identity] = configuration
        return configuration

    def get(self, model_configuration_id: str) -> ModelConfiguration:
        configuration = self._configurations[model_configuration_id]
        configuration.verify_identity()
        return configuration


@dataclass(frozen=True)
class RegistrationPreflightResult:
    """A declared compatibility judgment, without runtime or capability evidence."""

    agent_id: str
    role_configuration_id: str
    model_configuration_id: str
    accepted: bool
    reasons: tuple[str, ...] = ()
    preflight_id: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("agent_id", "role_configuration_id", "model_configuration_id"):
            _required_text(getattr(self, name), name)
        if type(self.accepted) is not bool:
            raise ValueError("accepted must be a boolean")
        reasons = _unique_names(self.reasons, "reasons")
        if self.accepted == bool(reasons):
            raise ValueError(
                "accepted preflight must have no reasons; rejected preflight requires reasons"
            )
        object.__setattr__(self, "reasons", reasons)
        object.__setattr__(self, "preflight_id", self._content_id())

    def _identity_payload(self) -> dict[str, object]:
        return {
            "schema_version": "uah.registration_preflight/v1",
            "agent_id": self.agent_id,
            "role_configuration_id": self.role_configuration_id,
            "model_configuration_id": self.model_configuration_id,
            "accepted": self.accepted,
            "reasons": self.reasons,
        }

    def _content_id(self) -> str:
        encoded = json.dumps(
            self._identity_payload(),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
        return "registration-preflight:sha256:" + hashlib.sha256(encoded).hexdigest()

    def verify_identity(self) -> None:
        if self.preflight_id != self._content_id():
            raise ValueError("registration preflight identity does not match content")

    def to_dict(self) -> dict[str, object]:
        self.verify_identity()
        return {"preflight_id": self.preflight_id, **self._identity_payload()}

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> RegistrationPreflightResult:
        _require_fields(
            value,
            {
                "schema_version",
                "preflight_id",
                "agent_id",
                "role_configuration_id",
                "model_configuration_id",
                "accepted",
                "reasons",
            },
            "registration preflight",
        )
        data = dict(value)
        if data.pop("schema_version") != "uah.registration_preflight/v1":
            raise ValueError("unsupported registration preflight schema")
        identity = data.pop("preflight_id")
        result = cls(**data)
        if result.preflight_id != identity:
            raise ValueError("registration preflight identity does not match content")
        return result


class RegistrationPreflight:
    """Check frozen manifest references against declarations without reserving a model."""

    def __init__(
        self,
        roles: AgentRoleConfigurationRegistry,
        models: ModelConfigurationRegistry,
    ) -> None:
        self._roles = roles
        self._models = models

    def evaluate(self, manifest: AgentManifest) -> RegistrationPreflightResult:
        manifest.verify_identity()
        reasons = []
        try:
            role = self._roles.get(manifest.role_configuration_id)
        except KeyError:
            role = None
            reasons.append("unknown_role_configuration")
        try:
            model = self._models.get(manifest.model_configuration_id)
        except KeyError:
            model = None
            reasons.append("unknown_model_configuration")
        if role is not None and model is not None:
            reasons.extend(
                "missing_model_capability:%s" % capability
                for capability in role.required_model_capabilities
                if capability not in model.capabilities
            )
            if model.max_context_tokens < role.minimum_context_tokens:
                reasons.append("insufficient_context")
            if (
                role.allowed_provider_kinds
                and model.provider_kind not in role.allowed_provider_kinds
            ):
                reasons.append("provider_not_allowed")
        return RegistrationPreflightResult(
            manifest.agent_id,
            manifest.role_configuration_id,
            manifest.model_configuration_id,
            accepted=not reasons,
            reasons=tuple(reasons),
        )


def _required_text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("%s must be a nonempty string" % name)


def _require_fields(value: object, names: set[str], name: str) -> None:
    if not isinstance(value, dict) or set(value) != names:
        raise ValueError("invalid %s fields" % name)


def _positive_integer(value: object, name: str) -> None:
    if type(value) is not int or value <= 0:
        raise ValueError("%s must be a positive integer" % name)


def _unique_names(values: object, name: str) -> tuple[str, ...]:
    if not isinstance(values, (tuple, list)):
        raise ValueError("%s must be a sequence of names" % name)
    for value in values:
        _required_text(value, name)
        if "*" in value:
            raise ValueError("%s cannot contain wildcards" % name)
    if len(values) != len(set(values)):
        raise ValueError("%s must contain unique names" % name)
    return tuple(sorted(values))
