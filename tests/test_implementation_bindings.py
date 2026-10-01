from pathlib import Path

import pytest

from ab_harness import ABImplementationBinding
from ab_harness import BindingCatalog
from ab_harness import RegistrySnapshot


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "tests" / "fixtures" / "ab_registry.json"


def _registry() -> RegistrySnapshot:
    return RegistrySnapshot.from_json_file(REGISTRY)


def _binding(
    *,
    object_id: str = "find_object",
    implementation_owner: str = "object_finder",
    locator: str = "fake_nao.skills:find_object",
    status: str = "approved",
) -> ABImplementationBinding:
    return ABImplementationBinding(
        binding_id="nao_fake.find_object.v1",
        object_id=object_id,
        environment_id="nao_fake",
        implementation_owner=implementation_owner,
        interface_kind="python_method",
        locator=locator,
        source_revision="fixture-rev-1",
        input_schema_ref="schema://find_object/input/v1",
        output_schema_ref="schema://find_object/result/v1",
        evidence_adapter="fake_nao.evidence:fresh_detection",
        runtime_modes=("shadow", "fake"),
        status=status,
    )


def test_binding_is_a_replaceable_pointer_to_a_stable_semantic_object():
    registry = _registry()
    original = BindingCatalog(registry, (_binding(),))
    replacement = BindingCatalog(
        registry,
        (_binding(locator="future_nao.skills:find_object"),),
    )

    assert original.resolve("find_object", runtime_mode="fake").locator == (
        "fake_nao.skills:find_object"
    )
    assert replacement.resolve("find_object", runtime_mode="fake").locator == (
        "future_nao.skills:find_object"
    )
    assert original.object_for("find_object") == replacement.object_for("find_object")


def test_binding_catalog_rejects_a_pointer_to_an_unknown_ab_object():
    with pytest.raises(ValueError, match="unknown AB object"):
        BindingCatalog(_registry(), (_binding(object_id="invented_skill"),))


def test_candidate_binding_is_visible_but_cannot_be_resolved_for_use():
    catalog = BindingCatalog(_registry(), (_binding(status="candidate"),))

    assert catalog.bindings_for("find_object")[0].status == "candidate"
    with pytest.raises(LookupError, match="no approved binding"):
        catalog.resolve("find_object", runtime_mode="fake")


def test_runtime_mode_is_part_of_binding_resolution():
    catalog = BindingCatalog(_registry(), (_binding(),))

    with pytest.raises(LookupError, match="runtime mode"):
        catalog.resolve("find_object", runtime_mode="live")


def test_ab0_contract_binding_does_not_change_admission_owner():
    binding = _binding(
        object_id="/planner/request",
        implementation_owner="planner_common",
    )
    catalog = BindingCatalog(_registry(), (binding,))

    assert catalog.object_for("/planner/request").owner_package == "nao_orchestrator"
    assert catalog.bindings_for("/planner/request")[0].implementation_owner == (
        "planner_common"
    )
