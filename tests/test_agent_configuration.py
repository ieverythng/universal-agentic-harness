from dataclasses import FrozenInstanceError
import json

import pytest

from ab_harness.agent_configuration import AgentRoleConfiguration
from ab_harness.agent_configuration import AgentRoleConfigurationRegistry
from ab_harness.agent_configuration import ModelConfiguration
from ab_harness.agent_configuration import ModelConfigurationRegistry
from ab_harness.agent_configuration import RegistrationPreflight
from ab_harness.agent_configuration import RegistrationPreflightResult
from ab_harness.agent_identity import AgentManifest
from ab_harness.contracts import ABControlBand, AbstractionFrame, AgentRoleSpec


def _role(**overrides):
    values = {
        "role": AgentRoleSpec(
            "synthetic.worker", ("operation",), ABControlBand(1, 1, 1)
        ),
        "primary_frame": AbstractionFrame(
            "synthetic", "test_workspace", "one verified mutation", "registry:v1"
        ),
        "domain_contract_pack_id": "synthetic.pack",
        "domain_contract_pack_revision": "sha256:pack-v1",
        "projected_object_ids": ("object:patch", "object:read"),
        "required_model_capabilities": ("structured_output",),
        "minimum_context_tokens": 4096,
        "allowed_provider_kinds": ("recorded", "openai_compatible"),
    }
    values.update(overrides)
    return AgentRoleConfiguration(**values)


def test_role_configuration_is_model_independent_frozen_and_round_trips():
    role = _role()
    registry = AgentRoleConfigurationRegistry()
    registry.register(role)

    restored = AgentRoleConfiguration.from_dict(role.to_dict())

    assert restored == role
    assert registry.get(role.role_configuration_id) is role
    assert role.role_configuration_id.startswith("role-configuration:sha256:")
    assert "model_configuration_id" not in role.to_dict()
    with pytest.raises(FrozenInstanceError):
        role.minimum_context_tokens = 2048


@pytest.mark.parametrize(
    "overrides",
    (
        {"domain_contract_pack_revision": ""},
        {"projected_object_ids": ("object:read", "object:read")},
        {"projected_object_ids": ("*",)},
        {"minimum_context_tokens": True},
        {"minimum_context_tokens": 0},
        {"required_model_capabilities": ("",)},
        {"primary_frame": AbstractionFrame("", "workspace", "atomic", "v1")},
        {"role": AgentRoleSpec("worker", ("operation",), ABControlBand(1, 1, 1), True)},
    ),
)
def test_role_configuration_rejects_invalid_authority_scope(overrides):
    with pytest.raises(ValueError):
        _role(**overrides)


def _model(**overrides):
    values = {
        "provider_kind": "recorded",
        "endpoint_ref": "deployment:synthetic.primary",
        "model_artifact": "synthetic-model",
        "model_revision": "model:v1",
        "capabilities": ("structured_output", "tool_calling"),
        "max_context_tokens": 8192,
        "decoding_settings": (("temperature", 0.0), ("seed", 42)),
    }
    values.update(overrides)
    return ModelConfiguration(**values)


def test_model_configuration_round_trips_canonical_declared_parameters():
    model = _model()
    registry = ModelConfigurationRegistry()
    registry.register(model)

    restored = ModelConfiguration.from_dict(model.to_dict())
    reordered = _model(
        capabilities=tuple(reversed(model.capabilities)),
        decoding_settings=tuple(reversed(model.decoding_settings)),
    )

    assert restored == model == reordered
    assert registry.get(model.model_configuration_id) is model
    assert model.model_configuration_id.startswith("model-configuration:sha256:")
    assert (
        _model(model_revision="model:v2").model_configuration_id
        != model.model_configuration_id
    )


@pytest.mark.parametrize(
    "overrides",
    (
        {"endpoint_ref": "https://user:password@example.com/v1"},
        {"max_context_tokens": True},
        {"max_context_tokens": 0},
        {"capabilities": ("structured_output", "structured_output")},
        {"decoding_settings": (("temperature", float("nan")),)},
        {"decoding_settings": (("temperature", float("inf")),)},
        {"decoding_settings": (("temperature", {"value": 0}),)},
        {"decoding_settings": (("temperature", 0), ("temperature", 1))},
        {"decoding_settings": (("api_key", "secret"),)},
    ),
)
def test_model_configuration_rejects_credentials_mutable_or_invalid_settings(overrides):
    with pytest.raises(ValueError):
        _model(**overrides)


def _manifest(role, model):
    return AgentManifest(
        role_configuration_id=role.role_configuration_id,
        model_configuration_id=model.model_configuration_id,
        prompt_pack_id="prompt:synthetic.worker:v1",
        harness_build_id="git:build-v1",
        adapter_revisions=(("synthetic", "adapter:v1"),),
    )


def test_registration_preflight_accepts_declared_compatible_manifest_without_runtime():
    roles = AgentRoleConfigurationRegistry()
    models = ModelConfigurationRegistry()
    role = roles.register(_role())
    model = models.register(_model())
    manifest = _manifest(role, model)

    result = RegistrationPreflight(roles, models).evaluate(manifest)

    assert result.accepted
    assert result.reasons == ()
    assert result.agent_id == manifest.agent_id
    assert result.role_configuration_id == role.role_configuration_id
    assert result.model_configuration_id == model.model_configuration_id
    assert RegistrationPreflightResult.from_dict(result.to_dict()) == result


def test_registration_preflight_reports_all_declared_incompatibilities_deterministically():
    roles = AgentRoleConfigurationRegistry()
    models = ModelConfigurationRegistry()
    role = roles.register(
        _role(required_model_capabilities=("tool_calling", "structured_output"))
    )
    model = models.register(
        _model(provider_kind="unapproved", capabilities=(), max_context_tokens=2048)
    )

    result = RegistrationPreflight(roles, models).evaluate(_manifest(role, model))

    assert not result.accepted
    assert result.reasons == (
        "insufficient_context",
        "missing_model_capability:structured_output",
        "missing_model_capability:tool_calling",
        "provider_not_allowed",
    )
    assert RegistrationPreflightResult.from_dict(result.to_dict()) == result


def test_registration_preflight_rejects_unknown_role_and_model_references():
    manifest = _manifest(_role(), _model())
    result = RegistrationPreflight(
        AgentRoleConfigurationRegistry(), ModelConfigurationRegistry()
    ).evaluate(manifest)

    assert not result.accepted
    assert result.reasons == (
        "unknown_model_configuration",
        "unknown_role_configuration",
    )


@pytest.mark.parametrize("factory", (_role, _model))
def test_configuration_registries_reject_duplicate_unknown_and_tampered_content(
    factory,
):
    configuration = factory()
    is_role = isinstance(configuration, AgentRoleConfiguration)
    registry = (
        AgentRoleConfigurationRegistry() if is_role else ModelConfigurationRegistry()
    )
    identity = (
        configuration.role_configuration_id
        if is_role
        else configuration.model_configuration_id
    )
    registry.register(configuration)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(factory())
    with pytest.raises(KeyError):
        registry.get("unknown")
    field = "minimum_context_tokens" if is_role else "max_context_tokens"
    object.__setattr__(configuration, field, 2048)
    with pytest.raises(ValueError, match="identity does not match"):
        registry.get(identity)


@pytest.mark.parametrize("factory", (_role, _model))
def test_configuration_deserialization_checks_complete_shape_and_nested_identity(
    factory,
):
    configuration = factory()
    deserialize = type(configuration).from_dict
    payload = json.loads(json.dumps(configuration.to_dict()))
    assert deserialize(payload) == configuration
    identity_field = (
        "role_configuration_id" if factory is _role else "model_configuration_id"
    )
    del payload[identity_field]
    with pytest.raises(ValueError, match="invalid"):
        deserialize(payload)
    payload = configuration.to_dict()
    payload["unknown"] = "ignored-policy"
    with pytest.raises(ValueError, match="invalid"):
        deserialize(payload)


def test_configuration_freezes_caller_owned_sequences_before_publication():
    projected_objects = ["object:read"]
    output_types = ["operation"]
    settings = [["temperature", 0.0]]
    role = _role(
        projected_object_ids=projected_objects,
        role=AgentRoleSpec("worker", output_types, ABControlBand(1, 1, 1)),
    )
    model = _model(decoding_settings=settings)

    projected_objects.append("object:delete")
    output_types.append("unrestricted")
    settings[0][1] = 1.0

    role.verify_identity()
    model.verify_identity()
    assert role.projected_object_ids == ("object:read",)
    assert role.role.allowed_output_types == ("operation",)
    assert model.decoding_settings == (("temperature", 0.0),)


def test_registration_preflight_artifact_rejects_forged_or_contradictory_result():
    roles = AgentRoleConfigurationRegistry()
    models = ModelConfigurationRegistry()
    role = roles.register(_role())
    model = models.register(_model())
    result = RegistrationPreflight(roles, models).evaluate(_manifest(role, model))
    payload = result.to_dict()
    payload["accepted"] = False
    payload["reasons"] = ("insufficient_context",)

    with pytest.raises(ValueError, match="identity does not match"):
        RegistrationPreflightResult.from_dict(payload)
    object.__setattr__(result, "model_configuration_id", "model:substituted")
    with pytest.raises(ValueError, match="identity does not match"):
        result.verify_identity()
    with pytest.raises(ValueError, match="requires reasons"):
        RegistrationPreflightResult(
            agent_id="agent:worker",
            role_configuration_id="role:worker",
            model_configuration_id="model:worker",
            accepted=False,
        )
