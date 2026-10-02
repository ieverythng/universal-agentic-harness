"""Strict canonical JSON and SHA-256 mechanics for authority artifacts."""

from __future__ import annotations

import hashlib
import json


def canonical_json(payload: object) -> str:
    """Encode one finite JSON value with the frozen UAH byte contract."""

    return json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def content_id(namespace: str, payload: object) -> str:
    """Return the namespaced SHA-256 identity of canonical JSON content."""

    encoded = canonical_json(payload).encode("utf-8")
    return "%s:sha256:%s" % (namespace, hashlib.sha256(encoded).hexdigest())
