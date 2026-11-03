import json

import pytest

from ab_harness import ABControlBand
from ab_harness import ABObjectView
from ab_harness import AbstractionFrame
from ab_harness import AgentRoleSpec
from ab_harness import InteractionProjector
from ab_harness import RegistrySnapshot


def test_control_band_rejects_invalid_ordering():
    with pytest.raises(ValueError, match="invalid AB control band ordering"):
        ABControlBand(2, 1, 3)


def test_projection_rejects_object_above_inspection_band(tmp_path):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "objects": [
                    {
                        "object_id": "policy_foundry",
                        "ab_level": 5,
                        "kind": "system",
                        "category": "research",
                        "owner_package": "workbench",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    registry = RegistrySnapshot.from_json_file(registry_path)
    role = AgentRoleSpec("worker", ("proposal",), ABControlBand(0, 1, 2))
    frame = AbstractionFrame("test", "fixture", "AB1 is callable", registry.version)

    with pytest.raises(ValueError, match="outside inspectable control band"):
        InteractionProjector(registry).compile(
            task_id="bounded",
            role=role,
            frame=frame,
            requested_object_ids=("policy_foundry",),
        )


def test_registry_version_tracks_exact_content(tmp_path):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text('{"objects": []}\n', encoding="utf-8")
    first = RegistrySnapshot.from_json_file(registry_path)
    registry_path.write_text('{"objects":[]}\n', encoding="utf-8")
    second = RegistrySnapshot.from_json_file(registry_path)

    assert first.version.startswith("sha256:")
    assert first.version != second.version


def test_registry_snapshot_rejects_duplicate_object_identity():
    first = ABObjectView("same_object", 0, "primitive", "test", "owner_a")
    second = ABObjectView("same_object", 1, "skill", "test", "owner_b")

    with pytest.raises(ValueError, match="duplicate AB object id: same_object"):
        RegistrySnapshot(
            (first, second),
            source="fixture:duplicate",
            version="sha256:duplicate",
        )


@pytest.mark.parametrize(
    ("metadata", "expected"),
    (
        ({}, False),
        ({"runtime_callable": False}, False),
        ({"runtime_callable": True}, True),
    ),
)
def test_registry_runtime_callable_preserves_boolean_defaults_and_controls(
    tmp_path, metadata, expected
):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "objects": [
                    {
                        "object_id": "inspectable",
                        "ab_level": 1,
                        "kind": "skill",
                        "category": "test",
                        "owner_package": "fixture",
                        "metadata": metadata,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    registry = RegistrySnapshot.from_json_file(registry_path)

    assert registry.get("inspectable").runtime_callable is expected


@pytest.mark.parametrize("malformed", ("false", 0, 1, None, []))
def test_registry_rejects_non_boolean_runtime_callable(tmp_path, malformed):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "objects": [
                    {
                        "object_id": "must-not-be-coercible",
                        "ab_level": 1,
                        "kind": "skill",
                        "category": "test",
                        "owner_package": "fixture",
                        "metadata": {"runtime_callable": malformed},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="runtime_callable must be a boolean"):
        RegistrySnapshot.from_json_file(registry_path)


def test_registry_rejects_duplicate_runtime_callable_member(tmp_path):
    registry_path = tmp_path / "duplicate-runtime-callable.json"
    registry_path.write_text(
        '{"objects":[{"object_id":"duplicate","ab_level":1,'
        '"kind":"skill","category":"test","owner_package":"fixture",'
        '"metadata":{"runtime_callable":false,"runtime_callable":true}}]}',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate JSON object key"):
        RegistrySnapshot.from_json_file(registry_path)


@pytest.mark.parametrize("malformed", ("false", 0, 1, None))
def test_ab_object_view_rejects_non_boolean_runtime_callable(malformed):
    with pytest.raises(ValueError, match="runtime_callable must be a boolean"):
        ABObjectView(
            "must-not-be-coercible",
            1,
            "skill",
            "test",
            "fixture",
            runtime_callable=malformed,
        )


def test_projection_rejects_mutated_non_boolean_runtime_callable():
    item = ABObjectView("known_object", 0, "primitive", "test", "owner")
    registry = RegistrySnapshot(
        (item,),
        source="fixture:registry",
        version="sha256:registry",
    )
    role = AgentRoleSpec("worker", ("proposal",), ABControlBand(0, 0, 0))
    frame = AbstractionFrame("test", "fixture", "AB0 is atomic", registry.version)
    object.__setattr__(item, "runtime_callable", "false")
    try:
        with pytest.raises(ValueError, match="runtime_callable must be a boolean"):
            InteractionProjector(registry).compile(
                task_id="malformed-callability",
                role=role,
                frame=frame,
                requested_object_ids=(item.object_id,),
            )
    finally:
        object.__setattr__(item, "runtime_callable", False)


def test_projection_rejects_a_frame_from_another_registry():
    item = ABObjectView("known_object", 0, "primitive", "test", "owner")
    registry = RegistrySnapshot(
        (item,),
        source="fixture:registry",
        version="sha256:registry-a",
    )
    role = AgentRoleSpec("worker", ("proposal",), ABControlBand(0, 0, 0))
    frame = AbstractionFrame("test", "fixture", "AB0 is atomic", "sha256:registry-b")

    with pytest.raises(ValueError, match="frame registry version does not match"):
        InteractionProjector(registry).compile(
            task_id="registry-mismatch",
            role=role,
            frame=frame,
            requested_object_ids=(item.object_id,),
        )
