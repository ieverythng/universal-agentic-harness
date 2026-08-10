"""Validated bindings between semantic AB objects and environment APIs."""

from __future__ import annotations

from collections import defaultdict

from ab_harness.contracts import ABImplementationBinding, ABObjectView
from ab_harness.registry import RegistrySnapshot


class BindingCatalog:
    """Read-only, fail-closed view of reviewed and candidate bindings."""

    def __init__(
        self,
        registry: RegistrySnapshot,
        bindings: tuple[ABImplementationBinding, ...],
    ) -> None:
        self._registry = registry
        self._by_object: dict[str, list[ABImplementationBinding]] = defaultdict(list)
        binding_ids: set[str] = set()

        for binding in bindings:
            item = registry.get(binding.object_id)
            if item is None:
                raise ValueError('binding references unknown AB object: %s' % binding.object_id)
            if binding.binding_id in binding_ids:
                raise ValueError('duplicate binding id: %s' % binding.binding_id)
            binding_ids.add(binding.binding_id)
            self._by_object[binding.object_id].append(binding)

    def object_for(self, object_id: str) -> ABObjectView | None:
        return self._registry.get(object_id)

    def bindings_for(self, object_id: str) -> tuple[ABImplementationBinding, ...]:
        return tuple(self._by_object.get(object_id, ()))

    def resolve(
        self,
        object_id: str,
        *,
        runtime_mode: str,
        environment_id: str | None = None,
    ) -> ABImplementationBinding:
        approved = tuple(
            binding
            for binding in self.bindings_for(object_id)
            if binding.status == 'approved'
            and (environment_id is None or binding.environment_id == environment_id)
        )
        if not approved:
            raise LookupError('no approved binding for AB object: %s' % object_id)

        compatible = tuple(
            binding for binding in approved if runtime_mode in binding.runtime_modes
        )
        if not compatible:
            raise LookupError(
                'no approved binding for runtime mode %s: %s'
                % (runtime_mode, object_id)
            )
        if len(compatible) != 1:
            raise LookupError(
                'ambiguous approved bindings for AB object %s in runtime mode %s'
                % (object_id, runtime_mode)
            )
        return compatible[0]
