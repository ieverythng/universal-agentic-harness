from ab_harness.configuration import ConfigurationIdentity


def _configuration(**changes) -> ConfigurationIdentity:
    values = {
        "model_id": "recorded-fixture",
        "model_revision": "fixture-v1",
        "model_format": "recorded-json",
        "runtime_id": "ab_harness.recorded",
        "runtime_revision": "0.1.0",
        "runtime_parameters": (("mode", "deterministic"),),
        "harness_version": "0.1.0",
        "adapter_version": "nao-shadow-v1",
        "prompt_hash": "sha256:none",
        "registry_version": "sha256:fixture",
        "environment_id": "nao_fake",
        "environment_revision": "fixture-v1",
        "task_suite_version": "uah-smoke-v1",
        "evaluator_version": "owner-evidence-v1",
    }
    values.update(changes)
    return ConfigurationIdentity(**values)


def test_configuration_id_is_stable_and_content_addressed():
    first = _configuration()
    repeated = _configuration()

    assert first.configuration_id == repeated.configuration_id
    assert first.configuration_id.startswith("uah-config:sha256:")
    assert first.to_dict()["configuration_id"] == first.configuration_id


def test_runtime_or_registry_change_produces_a_new_configuration_id():
    baseline = _configuration()
    kv4 = _configuration(runtime_parameters=(("kv", "q4_0"),))
    registry_change = _configuration(registry_version="sha256:changed")

    assert baseline.configuration_id != kv4.configuration_id
    assert baseline.configuration_id != registry_change.configuration_id
