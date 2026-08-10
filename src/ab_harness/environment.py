"""Portable environment-owner adapter used by the synthetic H1 runtime."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from ab_harness.bindings import BindingCatalog
from ab_harness.contracts import EffectEvidence, OwnerExecutionResult


class InProcessEnvironmentOwner:
    """Mount approved Python-method bindings without importing a domain stack."""

    def __init__(
        self,
        *,
        environment_id: str,
        catalog: BindingCatalog,
        handlers: Mapping[str, Callable[[dict[str, Any]], OwnerExecutionResult]],
    ) -> None:
        self.environment_id = environment_id
        self._catalog = catalog
        self._handlers = dict(handlers)

    def execute(
        self,
        *,
        object_id: str,
        arguments: dict[str, Any],
        runtime_mode: str,
    ) -> EffectEvidence:
        item = self._catalog.object_for(object_id)
        if item is None:
            raise ValueError('unknown AB object: %s' % object_id)
        if not item.runtime_callable:
            raise ValueError('AB object is not runtime callable: %s' % object_id)

        binding = self._catalog.resolve(
            object_id,
            runtime_mode=runtime_mode,
            environment_id=self.environment_id,
        )
        if binding.implementation_owner != item.owner_package:
            raise ValueError(
                'binding implementation owner does not own executable AB object: %s'
                % binding.binding_id
            )
        if binding.interface_kind != 'python_method':
            raise ValueError(
                'binding is not an in-process Python method: %s' % binding.binding_id
            )

        handler = self._handlers.get(binding.locator)
        if handler is None:
            raise LookupError('binding locator is not mounted: %s' % binding.locator)
        result = handler(dict(arguments))
        if not isinstance(result, OwnerExecutionResult):
            raise TypeError('environment handler must return OwnerExecutionResult')
        if not result.evidence_ref.strip():
            raise ValueError('environment owner returned evidence without a reference')

        undeclared = tuple(
            effect
            for effect in result.observed_effects
            if effect not in item.observable_success
        )
        if undeclared:
            raise ValueError(
                'environment owner returned undeclared observables: %s'
                % ', '.join(undeclared)
            )
        if result.succeeded and item.observable_success and not result.observed_effects:
            raise ValueError('successful execution requires declared effect evidence')

        return EffectEvidence(
            evidence_ref=result.evidence_ref,
            object_id=object_id,
            binding_id=binding.binding_id,
            environment_id=self.environment_id,
            owner=item.owner_package,
            succeeded=result.succeeded,
            observed_effects=result.observed_effects,
            payload=dict(result.payload),
        )
