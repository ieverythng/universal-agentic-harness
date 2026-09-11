"""Frozen contracts for reusable native environment configurations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentProfile:
    """Pinned domain and runtime authority for environment activations."""

    environment_profile_id: str
    domain_contract_pack_id: str
    domain_contract_pack_revision: str
    native_runtime_revision: str
    environment_owner_id: str
    required_interface_ids: tuple[str, ...]
    agent_handle_ids: tuple[str, ...] = ()


class EnvironmentProfileRegistry:
    """Read-only lookup for reviewed environment profiles."""

    def __init__(self, profiles: tuple[EnvironmentProfile, ...]) -> None:
        self._profiles: dict[str, EnvironmentProfile] = {}
        for profile in profiles:
            self._validate(profile)
            if profile.environment_profile_id in self._profiles:
                raise ValueError(
                    'environment profile already registered: %s'
                    % profile.environment_profile_id
                )
            self._profiles[profile.environment_profile_id] = profile

    def get(self, environment_profile_id: str) -> EnvironmentProfile:
        return self._profiles[environment_profile_id]

    @staticmethod
    def _validate(profile: EnvironmentProfile) -> None:
        required = {
            'environment_profile_id': profile.environment_profile_id,
            'domain_contract_pack_id': profile.domain_contract_pack_id,
            'domain_contract_pack_revision': profile.domain_contract_pack_revision,
            'native_runtime_revision': profile.native_runtime_revision,
            'environment_owner_id': profile.environment_owner_id,
        }
        missing = tuple(name for name, value in required.items() if not value.strip())
        if missing:
            raise ValueError(
                'environment profile fields must not be empty: %s'
                % ', '.join(missing)
            )
