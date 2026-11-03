"""Frozen contracts for reusable native environment configurations."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import fields


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
        if type(profiles) is not tuple:
            raise TypeError("environment profiles must be supplied as a tuple")
        self._profiles: dict[str, EnvironmentProfile] = {}
        for profile in profiles:
            snapshot = self._verified_copy(profile)
            if snapshot.environment_profile_id in self._profiles:
                raise ValueError(
                    'environment profile already registered: %s'
                    % snapshot.environment_profile_id
                )
            self._profiles[snapshot.environment_profile_id] = snapshot

    def get(self, environment_profile_id: str) -> EnvironmentProfile:
        return self._verified_copy(self._profiles[environment_profile_id])

    @staticmethod
    def _verified_copy(profile: object) -> EnvironmentProfile:
        if type(profile) is not EnvironmentProfile:
            raise TypeError("environment profile requires its concrete owner type")
        stored = object.__getattribute__(profile, "__dict__")
        names = tuple(item.name for item in fields(EnvironmentProfile))
        if type(stored) is not dict or set(stored) != set(names):
            raise TypeError("environment profile fields must be plain data")
        values = {name: stored[name] for name in names}
        for name in names:
            value = values[name]
            if name in {"required_interface_ids", "agent_handle_ids"}:
                if type(value) is not tuple or any(type(item) is not str for item in value):
                    raise TypeError("environment profile rosters must be tuples of strings")
            elif type(value) is not str:
                raise TypeError("environment profile fields must be plain strings")
        snapshot = EnvironmentProfile(**values)
        EnvironmentProfileRegistry._validate(snapshot)
        return snapshot

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
