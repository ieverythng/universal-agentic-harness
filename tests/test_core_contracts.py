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
