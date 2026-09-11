"""Registration of owner-attested native environment activations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ab_harness.environment_profiles import EnvironmentProfileRegistry


@dataclass(frozen=True)
class EnvironmentRunAttestation:
    """Readiness statement issued by the owner of a native environment."""

    environment_run_id: str
    environment_profile_id: str
    domain_contract_pack_revision: str
    native_runtime_revision: str
    environment_owner_id: str
    attestation_id: str
    started_at: str
    readiness_evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class EnvironmentRun:
    """One native activation admitted into the UAH lifecycle."""

    attestation: EnvironmentRunAttestation
    status: Literal['active'] = 'active'

    @property
    def environment_run_id(self) -> str:
        return self.attestation.environment_run_id


class EnvironmentRunRegistry:
    """Keep admitted environment activations separate from native startup."""

    def __init__(self, profiles: EnvironmentProfileRegistry) -> None:
        self._profiles = profiles
        self._runs: dict[str, EnvironmentRun] = {}
        self._attestation_ids: set[str] = set()

    def register(self, attestation: EnvironmentRunAttestation) -> EnvironmentRun:
        self._validate_attestation(attestation)
        if attestation.environment_run_id in self._runs:
            raise ValueError(
                'environment run already registered: %s'
                % attestation.environment_run_id
            )
        if attestation.attestation_id in self._attestation_ids:
            raise ValueError(
                'environment run attestation already registered: %s'
                % attestation.attestation_id
            )
        environment_run = EnvironmentRun(attestation=attestation)
        self._runs[environment_run.environment_run_id] = environment_run
        self._attestation_ids.add(attestation.attestation_id)
        return environment_run

    def get(self, environment_run_id: str) -> EnvironmentRun:
        return self._runs[environment_run_id]

    def _validate_attestation(self, attestation: EnvironmentRunAttestation) -> None:
        required = {
            'environment_run_id': attestation.environment_run_id,
            'environment_profile_id': attestation.environment_profile_id,
            'domain_contract_pack_revision': (
                attestation.domain_contract_pack_revision
            ),
            'native_runtime_revision': attestation.native_runtime_revision,
            'environment_owner_id': attestation.environment_owner_id,
            'attestation_id': attestation.attestation_id,
            'started_at': attestation.started_at,
        }
        missing = tuple(name for name, value in required.items() if not value.strip())
        if missing:
            raise ValueError(
                'attestation fields must not be empty: %s' % ', '.join(missing)
            )
        if not attestation.readiness_evidence_refs or any(
            not reference.strip() for reference in attestation.readiness_evidence_refs
        ):
            raise ValueError('environment run attestation requires readiness evidence')
        try:
            profile = self._profiles.get(attestation.environment_profile_id)
        except KeyError as exc:
            raise ValueError(
                'unknown environment profile: %s'
                % attestation.environment_profile_id
            ) from exc
        expected = {
            'domain_contract_pack_revision': profile.domain_contract_pack_revision,
            'native_runtime_revision': profile.native_runtime_revision,
            'environment_owner_id': profile.environment_owner_id,
        }
        mismatched = tuple(
            field_name
            for field_name, expected_value in expected.items()
            if getattr(attestation, field_name) != expected_value
        )
        if mismatched:
            raise ValueError(
                'environment run attestation does not match profile: %s'
                % ', '.join(mismatched)
            )
