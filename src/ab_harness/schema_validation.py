"""Portable argument-schema resolution and validation for semantic admission."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any
from typing import Protocol


OBJECT_ARGUMENT_SCHEMA_VERSION = "uah.object_argument_schema/v1"
_JSON_TYPES = frozenset(
    {"array", "boolean", "integer", "null", "number", "object", "string"}
)


def _content_id(prefix: str, payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "%s:sha256:%s" % (prefix, hashlib.sha256(encoded).hexdigest())


@dataclass(frozen=True)
class ArgumentValidationResult:
    """Deterministic result of resolving and validating one argument object."""

    schema_ref: str
    schema_id: str | None
    violations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.schema_ref.strip():
            raise ValueError("schema reference must not be empty")
        if not isinstance(self.violations, tuple):
            raise TypeError("schema violations must be a tuple")
        if any(not item.strip() for item in self.violations):
            raise ValueError("schema violations must not be empty")
        if self.schema_id is None and not self.violations:
            raise ValueError("unresolved schema validation requires a violation")

    @property
    def accepted(self) -> bool:
        return self.schema_id is not None and not self.violations


class ArgumentSchemaValidator(Protocol):
    """Resolve a schema reference and validate canonical proposal arguments."""

    def validate_arguments(
        self,
        *,
        schema_ref: str,
        arguments: dict[str, Any],
    ) -> ArgumentValidationResult: ...


@dataclass(frozen=True)
class ArgumentField:
    """One named property in the portable object-schema subset."""

    name: str
    value_type: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("argument field name must not be empty")
        if self.value_type not in _JSON_TYPES:
            raise ValueError("unsupported argument field type: %s" % self.value_type)


def _object_schema_payload(
    *,
    schema_ref: str,
    fields: tuple[ArgumentField, ...],
    required: tuple[str, ...],
    allow_additional_properties: bool,
) -> dict[str, object]:
    return {
        "schema_version": OBJECT_ARGUMENT_SCHEMA_VERSION,
        "schema_ref": schema_ref,
        "fields": tuple(
            {"name": field.name, "value_type": field.value_type} for field in fields
        ),
        "required": required,
        "allow_additional_properties": allow_additional_properties,
    }


@dataclass(frozen=True)
class ObjectArgumentSchema:
    """Content-addressed JSON-object schema supported by the core validator."""

    schema_id: str
    schema_ref: str
    fields: tuple[ArgumentField, ...]
    required: tuple[str, ...]
    allow_additional_properties: bool = False
    schema_version: str = OBJECT_ARGUMENT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.fields, tuple) or not isinstance(self.required, tuple):
            raise TypeError("object schema collections must be tuples")
        object.__setattr__(
            self, "fields", tuple(sorted(self.fields, key=lambda f: f.name))
        )
        object.__setattr__(self, "required", tuple(sorted(self.required)))
        self.verify_identity()

    @classmethod
    def issue(
        cls,
        *,
        schema_ref: str,
        fields: tuple[ArgumentField, ...],
        required: tuple[str, ...],
        allow_additional_properties: bool = False,
    ) -> ObjectArgumentSchema:
        canonical_fields = tuple(sorted(fields, key=lambda field: field.name))
        canonical_required = tuple(sorted(required))
        payload = _object_schema_payload(
            schema_ref=schema_ref,
            fields=canonical_fields,
            required=canonical_required,
            allow_additional_properties=allow_additional_properties,
        )
        return cls(
            schema_id=_content_id("input-schema", payload),
            schema_ref=schema_ref,
            fields=canonical_fields,
            required=canonical_required,
            allow_additional_properties=allow_additional_properties,
        )

    def verify_identity(self) -> None:
        if self.schema_version != OBJECT_ARGUMENT_SCHEMA_VERSION:
            raise ValueError("unsupported object argument schema version")
        if not self.schema_ref.strip():
            raise ValueError("schema reference must not be empty")
        if not isinstance(self.fields, tuple) or not isinstance(self.required, tuple):
            raise TypeError("object schema collections must be tuples")
        field_names = tuple(field.name for field in self.fields)
        if len(field_names) != len(set(field_names)):
            raise ValueError("object schema field names must be unique")
        if len(self.required) != len(set(self.required)):
            raise ValueError("required argument names must be unique")
        unknown_required = tuple(
            name for name in self.required if name not in field_names
        )
        if unknown_required:
            raise ValueError(
                "required arguments must have field schemas: %s"
                % ", ".join(unknown_required)
            )
        expected = _content_id(
            "input-schema",
            _object_schema_payload(
                schema_ref=self.schema_ref,
                fields=self.fields,
                required=self.required,
                allow_additional_properties=self.allow_additional_properties,
            ),
        )
        if self.schema_id != expected:
            raise ValueError("schema identity does not match content")


class InMemoryArgumentSchemaRegistry:
    """Resolve and validate reviewed object schemas held in memory."""

    def __init__(self, schemas: tuple[ObjectArgumentSchema, ...]) -> None:
        by_ref: dict[str, ObjectArgumentSchema] = {}
        for schema in schemas:
            schema.verify_identity()
            if schema.schema_ref in by_ref:
                raise ValueError(
                    "duplicate argument schema ref: %s" % schema.schema_ref
                )
            by_ref[schema.schema_ref] = schema
        self._by_ref = by_ref

    def validate_arguments(
        self,
        *,
        schema_ref: str,
        arguments: dict[str, Any],
    ) -> ArgumentValidationResult:
        schema = self._by_ref.get(schema_ref)
        if schema is None:
            return ArgumentValidationResult(
                schema_ref=schema_ref,
                schema_id=None,
                violations=("schema_not_registered",),
            )
        schema.verify_identity()
        fields = {field.name: field for field in schema.fields}
        violations: list[str] = []
        for name in schema.required:
            if name not in arguments:
                violations.append("missing_required_property:%s" % name)
        if not schema.allow_additional_properties:
            violations.extend(
                "unexpected_property:%s" % name
                for name in sorted(set(arguments) - set(fields))
            )
        for name in sorted(set(arguments).intersection(fields)):
            field = fields[name]
            if not _matches_json_type(arguments[name], field.value_type):
                violations.append(
                    "invalid_type:%s:expected_%s" % (name, field.value_type)
                )
        return ArgumentValidationResult(
            schema_ref=schema_ref,
            schema_id=schema.schema_id,
            violations=tuple(violations),
        )


def _matches_json_type(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "string":
        return isinstance(value, str)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    raise ValueError("unsupported JSON type: %s" % expected)
