from dataclasses import replace

import pytest

from ab_harness import EnvironmentRunAttestation
from ab_harness import EnvironmentRunRegistry
from ab_harness import EnvironmentProfile
from ab_harness import EnvironmentProfileRegistry


def _profile() -> EnvironmentProfile:
    return EnvironmentProfile(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_id='domain-pack:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        native_runtime_revision='synthetic-runtime:v1',
        environment_owner_id='synthetic.runtime.owner',
        required_interface_ids=('synthetic.request', 'synthetic.feedback'),
        agent_handle_ids=('handle:synthetic.worker.primary',),
    )


def test_environment_profile_registry_preserves_the_frozen_profile():
    profile = _profile()
    registry = EnvironmentProfileRegistry((profile,))

    assert registry.get(profile.environment_profile_id) == profile


def test_duplicate_environment_profile_id_is_rejected():
    profile = _profile()

    with pytest.raises(ValueError, match='environment profile already registered'):
        EnvironmentProfileRegistry((profile, profile))


@pytest.mark.parametrize(
    'field_name',
    (
        'environment_profile_id',
        'domain_contract_pack_id',
        'domain_contract_pack_revision',
        'native_runtime_revision',
        'environment_owner_id',
    ),
)
def test_environment_profile_requires_complete_authority_lineage(field_name):
    profile = replace(_profile(), **{field_name: ''})

    with pytest.raises(ValueError, match='profile fields must not be empty'):
        EnvironmentProfileRegistry((profile,))


def _attestation() -> EnvironmentRunAttestation:
    return EnvironmentRunAttestation(
        environment_run_id='environment-run:synthetic:001',
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        native_runtime_revision='synthetic-runtime:v1',
        environment_owner_id='synthetic.runtime.owner',
        attestation_id='environment-attestation:sha256:001',
        started_at='2026-09-09T12:00:00Z',
        readiness_evidence_refs=('artifact:readiness:001',),
    )


def _registry() -> EnvironmentRunRegistry:
    profiles = EnvironmentProfileRegistry((_profile(),))
    return EnvironmentRunRegistry(profiles)


def test_owner_attestation_registers_one_retrievable_active_environment_run():
    attestation = _attestation()
    registry = _registry()

    environment_run = registry.register(attestation)

    assert environment_run.environment_run_id == attestation.environment_run_id
    assert environment_run.status == 'active'
    assert environment_run.attestation == attestation
    assert registry.get(attestation.environment_run_id) == environment_run


def test_unknown_environment_profile_cannot_activate_a_run():
    registry = EnvironmentRunRegistry(EnvironmentProfileRegistry(()))

    with pytest.raises(ValueError, match='unknown environment profile'):
        registry.register(_attestation())


@pytest.mark.parametrize(
    'field_name,replacement',
    (
        ('domain_contract_pack_revision', 'sha256:other-pack'),
        ('native_runtime_revision', 'synthetic-runtime:v2'),
        ('environment_owner_id', 'other.runtime.owner'),
    ),
)
def test_attestation_must_match_the_frozen_environment_profile(
    field_name, replacement
):
    registry = _registry()
    attestation = replace(_attestation(), **{field_name: replacement})

    with pytest.raises(
        ValueError, match='environment run attestation does not match profile'
    ):
        registry.register(attestation)


def test_duplicate_environment_run_id_is_rejected_without_replacing_the_run():
    registry = _registry()
    original = registry.register(_attestation())

    with pytest.raises(ValueError, match='environment run already registered'):
        registry.register(_attestation())

    assert registry.get(original.environment_run_id) is original


def test_attestation_identity_cannot_be_reused_for_another_environment_run():
    registry = _registry()
    registry.register(_attestation())
    replayed = replace(
        _attestation(), environment_run_id='environment-run:synthetic:002'
    )

    with pytest.raises(ValueError, match='attestation already registered'):
        registry.register(replayed)

    with pytest.raises(KeyError):
        registry.get(replayed.environment_run_id)


def test_attestation_without_readiness_evidence_cannot_activate_a_run():
    registry = _registry()
    attestation = replace(_attestation(), readiness_evidence_refs=())

    with pytest.raises(ValueError, match='readiness evidence'):
        registry.register(attestation)

    with pytest.raises(KeyError):
        registry.get(attestation.environment_run_id)


@pytest.mark.parametrize(
    'field_name',
    (
        'environment_run_id',
        'environment_profile_id',
        'domain_contract_pack_revision',
        'native_runtime_revision',
        'environment_owner_id',
        'attestation_id',
        'started_at',
    ),
)
def test_attestation_requires_complete_activation_lineage(field_name):
    registry = _registry()
    attestation = replace(_attestation(), **{field_name: ''})

    with pytest.raises(ValueError, match='attestation fields must not be empty'):
        registry.register(attestation)
