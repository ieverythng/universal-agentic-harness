"""Frozen, content-addressed rules owned by an onboarded domain."""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
import hashlib
import json
from typing import Literal


IngressAction = Literal[
    "state_update", "start_task", "resume_task", "notify_task", "reject"
]
DOMAIN_CONTRACT_PACK_SCHEMA = "uah.domain_contract_pack/v1"


def _required_strings(values: dict[str, str], contract: str) -> None:
    missing = tuple(name for name, value in values.items() if not value.strip())
    if missing:
        raise ValueError(
            "%s fields must not be empty: %s" % (contract, ", ".join(missing))
        )


@dataclass(frozen=True)
class TaskIngressRule:
    """Domain-owned mapping from one normalized ingress type to an action."""

    binding_id: str
    ingress_type: str
    action: IngressAction
    task_id_lineage_key: str | None = None

    def __post_init__(self) -> None:
        _required_strings(
            {"binding_id": self.binding_id, "ingress_type": self.ingress_type},
            "ingress rule",
        )
        if self.action not in {
            "state_update",
            "start_task",
            "resume_task",
            "notify_task",
            "reject",
        }:
            raise ValueError("invalid ingress action: %s" % self.action)
        if self.action in {"start_task", "resume_task", "notify_task"} and (
            self.task_id_lineage_key is None or not self.task_id_lineage_key.strip()
        ):
            raise ValueError("task-bearing rule requires a task identity lineage key")


@dataclass(frozen=True)
class DomainEffectRule:
    """Domain-owned mapping from one semantic effect to its evidence owner."""

    effect_id: str
    object_id: str
    evidence_owner: str
    failure_policy: str

    def __post_init__(self) -> None:
        _required_strings(
            {
                "effect_id": self.effect_id,
                "object_id": self.object_id,
                "evidence_owner": self.evidence_owner,
            },
            "domain effect rule",
        )
        if self.failure_policy not in {"terminal", "retryable"}:
            raise ValueError("invalid domain failure policy: %s" % self.failure_policy)


def _pack_payload(
    *,
    domain_contract_pack_id: str,
    frame_id: str,
    registry_version: str,
    allowed_role_ids: tuple[str, ...],
    supported_task_type_ids: tuple[str, ...],
    ingress_rules: tuple[TaskIngressRule, ...],
    effect_rules: tuple[DomainEffectRule, ...],
    prohibited_effects: tuple[str, ...],
) -> dict[str, object]:
    return {
        "schema_version": DOMAIN_CONTRACT_PACK_SCHEMA,
        "domain_contract_pack_id": domain_contract_pack_id,
        "frame_id": frame_id,
        "registry_version": registry_version,
        "allowed_role_ids": allowed_role_ids,
        "supported_task_type_ids": supported_task_type_ids,
        "ingress_rules": tuple(asdict(item) for item in ingress_rules),
        "effect_rules": tuple(asdict(item) for item in effect_rules),
        "prohibited_effects": prohibited_effects,
    }


def _pack_revision(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:%s" % hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class DomainContractPack:
    """Reviewed domain rules whose revision binds every routing and effect rule."""

    domain_contract_pack_id: str
    revision: str
    frame_id: str
    registry_version: str
    allowed_role_ids: tuple[str, ...]
    supported_task_type_ids: tuple[str, ...]
    ingress_rules: tuple[TaskIngressRule, ...]
    effect_rules: tuple[DomainEffectRule, ...]
    prohibited_effects: tuple[str, ...] = ()

    @classmethod
    def issue(
        cls,
        *,
        domain_contract_pack_id: str,
        frame_id: str,
        registry_version: str,
        allowed_role_ids: tuple[str, ...],
        supported_task_type_ids: tuple[str, ...],
        ingress_rules: tuple[TaskIngressRule, ...],
        effect_rules: tuple[DomainEffectRule, ...],
        prohibited_effects: tuple[str, ...] = (),
    ) -> DomainContractPack:
        collections = (
            allowed_role_ids,
            supported_task_type_ids,
            ingress_rules,
            effect_rules,
            prohibited_effects,
        )
        if any(not isinstance(items, tuple) for items in collections):
            raise TypeError("domain contract collections must be tuples")
        allowed_role_ids = tuple(sorted(allowed_role_ids))
        supported_task_type_ids = tuple(sorted(supported_task_type_ids))
        ingress_rules = tuple(
            sorted(
                ingress_rules,
                key=lambda item: (
                    item.binding_id,
                    item.ingress_type,
                    item.action,
                    item.task_id_lineage_key or "",
                ),
            )
        )
        effect_rules = tuple(
            sorted(
                effect_rules,
                key=lambda item: (
                    item.effect_id,
                    item.object_id,
                    item.evidence_owner,
                    item.failure_policy,
                ),
            )
        )
        prohibited_effects = tuple(sorted(prohibited_effects))
        payload = _pack_payload(
            domain_contract_pack_id=domain_contract_pack_id,
            frame_id=frame_id,
            registry_version=registry_version,
            allowed_role_ids=allowed_role_ids,
            supported_task_type_ids=supported_task_type_ids,
            ingress_rules=ingress_rules,
            effect_rules=effect_rules,
            prohibited_effects=prohibited_effects,
        )
        return cls(
            domain_contract_pack_id=domain_contract_pack_id,
            revision=_pack_revision(payload),
            frame_id=frame_id,
            registry_version=registry_version,
            allowed_role_ids=allowed_role_ids,
            supported_task_type_ids=supported_task_type_ids,
            ingress_rules=ingress_rules,
            effect_rules=effect_rules,
            prohibited_effects=prohibited_effects,
        )

    def __post_init__(self) -> None:
        collections = (
            self.allowed_role_ids,
            self.supported_task_type_ids,
            self.ingress_rules,
            self.effect_rules,
            self.prohibited_effects,
        )
        if any(not isinstance(items, tuple) for items in collections):
            raise TypeError("domain contract collections must be tuples")
        _required_strings(
            {
                "domain_contract_pack_id": self.domain_contract_pack_id,
                "revision": self.revision,
                "frame_id": self.frame_id,
                "registry_version": self.registry_version,
            },
            "domain contract pack",
        )
        if not self.allowed_role_ids:
            raise ValueError("domain contract pack requires an allowed role")
        if not self.supported_task_type_ids:
            raise ValueError("domain contract pack requires a supported task type")
        if not self.ingress_rules:
            raise ValueError("domain contract pack requires an ingress rule")
        if not self.effect_rules:
            raise ValueError("domain contract pack requires an effect rule")
        if self.allowed_role_ids != tuple(sorted(self.allowed_role_ids)):
            raise ValueError("domain contract roles must use canonical order")
        if self.supported_task_type_ids != tuple(sorted(self.supported_task_type_ids)):
            raise ValueError("domain contract task types must use canonical order")
        if self.prohibited_effects != tuple(sorted(self.prohibited_effects)):
            raise ValueError("domain contract prohibitions must use canonical order")
        canonical_ingress = tuple(
            sorted(
                self.ingress_rules,
                key=lambda item: (
                    item.binding_id,
                    item.ingress_type,
                    item.action,
                    item.task_id_lineage_key or "",
                ),
            )
        )
        if self.ingress_rules != canonical_ingress:
            raise ValueError("domain ingress rules must use canonical order")
        canonical_effects = tuple(
            sorted(
                self.effect_rules,
                key=lambda item: (
                    item.effect_id,
                    item.object_id,
                    item.evidence_owner,
                    item.failure_policy,
                ),
            )
        )
        if self.effect_rules != canonical_effects:
            raise ValueError("domain effect rules must use canonical order")
        self._reject_duplicates(
            "domain effect rules", tuple(item.effect_id for item in self.effect_rules)
        )
        self._reject_duplicates("domain roles", self.allowed_role_ids)
        self._reject_duplicates("domain task types", self.supported_task_type_ids)
        self._reject_duplicates("domain prohibitions", self.prohibited_effects)
        self._reject_duplicates(
            "domain ingress rules",
            tuple(
                "%s\0%s" % (item.binding_id, item.ingress_type)
                for item in self.ingress_rules
            ),
        )
        self.verify_identity()

    def verify_identity(self) -> None:
        """Recheck covered content before another owner consumes this pack."""
        payload = _pack_payload(
            domain_contract_pack_id=self.domain_contract_pack_id,
            frame_id=self.frame_id,
            registry_version=self.registry_version,
            allowed_role_ids=self.allowed_role_ids,
            supported_task_type_ids=self.supported_task_type_ids,
            ingress_rules=self.ingress_rules,
            effect_rules=self.effect_rules,
            prohibited_effects=self.prohibited_effects,
        )
        if self.revision != _pack_revision(payload):
            raise ValueError("domain contract pack revision does not match content")

    @staticmethod
    def _reject_duplicates(label: str, identities: tuple[str, ...]) -> None:
        seen: set[str] = set()
        duplicates: list[str] = []
        for identity in identities:
            if identity in seen and identity not in duplicates:
                duplicates.append(identity)
            seen.add(identity)
        if duplicates:
            raise ValueError("duplicate %s: %s" % (label, ", ".join(duplicates)))

    def to_dict(self) -> dict[str, object]:
        return {
            "revision": self.revision,
            **_pack_payload(
                domain_contract_pack_id=self.domain_contract_pack_id,
                frame_id=self.frame_id,
                registry_version=self.registry_version,
                allowed_role_ids=self.allowed_role_ids,
                supported_task_type_ids=self.supported_task_type_ids,
                ingress_rules=self.ingress_rules,
                effect_rules=self.effect_rules,
                prohibited_effects=self.prohibited_effects,
            ),
        }
