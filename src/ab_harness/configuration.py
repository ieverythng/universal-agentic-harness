"""Content-addressed identity for one model-harness-environment configuration."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


@dataclass(frozen=True)
class ConfigurationIdentity:
    model_id: str
    model_revision: str
    model_format: str
    runtime_id: str
    runtime_revision: str
    runtime_parameters: tuple[tuple[str, str], ...]
    harness_version: str
    adapter_version: str
    prompt_hash: str
    registry_version: str
    environment_id: str
    environment_revision: str
    task_suite_version: str
    evaluator_version: str

    def __post_init__(self) -> None:
        values = self._identity_payload()
        missing = tuple(key for key, value in values.items() if not value)
        if missing:
            raise ValueError(
                'configuration identity fields must not be empty: %s'
                % ', '.join(missing)
            )
        parameter_names = tuple(name for name, _ in self.runtime_parameters)
        if len(parameter_names) != len(set(parameter_names)):
            raise ValueError('runtime parameter names must be unique')

    @property
    def configuration_id(self) -> str:
        payload = json.dumps(
            self._identity_payload(),
            sort_keys=True,
            separators=(',', ':'),
        ).encode('utf-8')
        return 'uah-config:sha256:' + hashlib.sha256(payload).hexdigest()

    def to_dict(self) -> dict[str, object]:
        return {
            'configuration_id': self.configuration_id,
            **self._identity_payload(),
        }

    def _identity_payload(self) -> dict[str, object]:
        return {
            'model_id': self.model_id,
            'model_revision': self.model_revision,
            'model_format': self.model_format,
            'runtime_id': self.runtime_id,
            'runtime_revision': self.runtime_revision,
            'runtime_parameters': {
                name: value for name, value in sorted(self.runtime_parameters)
            },
            'harness_version': self.harness_version,
            'adapter_version': self.adapter_version,
            'prompt_hash': self.prompt_hash,
            'registry_version': self.registry_version,
            'environment_id': self.environment_id,
            'environment_revision': self.environment_revision,
            'task_suite_version': self.task_suite_version,
            'evaluator_version': self.evaluator_version,
        }
