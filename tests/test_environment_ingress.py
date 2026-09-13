import pytest

from ab_harness import EnvironmentIngress
from ab_harness import EnvironmentProfile
from ab_harness import EnvironmentProfileRegistry
from ab_harness import EnvironmentRunAttestation
from ab_harness import EnvironmentRunRegistry
from ab_harness import TaskIngressPolicy
from ab_harness import TaskIngressRule


def _active_environment_run():
    profile = EnvironmentProfile(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_id='domain-pack:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        native_runtime_revision='synthetic-runtime:v1',
        environment_owner_id='synthetic.runtime.owner',
        required_interface_ids=('synthetic.observation',),
    )
    runs = EnvironmentRunRegistry(EnvironmentProfileRegistry((profile,)))
    return runs.register(
        EnvironmentRunAttestation(
            environment_run_id='environment-run:synthetic:001',
            environment_profile_id=profile.environment_profile_id,
            domain_contract_pack_revision=profile.domain_contract_pack_revision,
            native_runtime_revision=profile.native_runtime_revision,
            environment_owner_id=profile.environment_owner_id,
            attestation_id='environment-attestation:sha256:001',
            started_at='2026-09-11T09:00:00Z',
            readiness_evidence_refs=('artifact:readiness:001',),
        )
    )


def test_normalized_observation_is_classified_as_an_environment_state_update():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id='environment-ingress:synthetic:001',
        environment_run_id=environment_run.environment_run_id,
        binding_id='binding:synthetic.observation:v1',
        ingress_type='observation',
        payload_artifact_id='artifact:sha256:observation-001',
        native_lineage=(('observation_id', 'native-observation-001'),),
        observed_at='2026-09-11T09:00:01Z',
    )
    policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.observation:v1',
                ingress_type='observation',
                action='state_update',
            ),
        ),
    )

    decision = policy.classify(environment_run, ingress)

    assert decision.environment_ingress_id == ingress.environment_ingress_id
    assert decision.environment_run_id == environment_run.environment_run_id
    assert decision.action == 'state_update'
    assert decision.reason_code == 'matched_rule'
    assert decision.task_id is None
    assert decision.trace_id is None


def test_ingress_from_another_environment_run_is_rejected():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id='environment-ingress:synthetic:002',
        environment_run_id='environment-run:synthetic:other',
        binding_id='binding:synthetic.observation:v1',
        ingress_type='observation',
        payload_artifact_id='artifact:sha256:observation-002',
        native_lineage=(),
        observed_at='2026-09-11T09:00:02Z',
    )
    policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.observation:v1',
                ingress_type='observation',
                action='state_update',
            ),
        ),
    )

    decision = policy.classify(environment_run, ingress)

    assert decision.action == 'reject'
    assert decision.reason_code == 'environment_run_mismatch'


def test_ingress_without_a_frozen_rule_is_rejected():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id='environment-ingress:synthetic:003',
        environment_run_id=environment_run.environment_run_id,
        binding_id='binding:synthetic.unknown:v1',
        ingress_type='unknown_event',
        payload_artifact_id='artifact:sha256:unknown-003',
        native_lineage=(),
        observed_at='2026-09-11T09:00:03Z',
    )
    policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.unknown:v1',
                ingress_type='observation',
                action='state_update',
            ),
        ),
    )

    decision = policy.classify(environment_run, ingress)

    assert decision.action == 'reject'
    assert decision.reason_code == 'unsupported_ingress_type'


def test_duplicate_ingress_rule_is_rejected():
    rule = TaskIngressRule(
        binding_id='binding:synthetic.observation:v1',
        ingress_type='observation',
        action='state_update',
    )

    with pytest.raises(ValueError, match='ingress rule already registered'):
        TaskIngressPolicy(
            environment_profile_id='environment-profile:synthetic:v1',
            domain_contract_pack_revision='sha256:domain-pack-revision',
            rules=(rule, rule),
        )


def test_environment_ingress_requires_an_identity():
    with pytest.raises(ValueError, match='ingress fields must not be empty'):
        EnvironmentIngress(
            environment_ingress_id='',
            environment_run_id='environment-run:synthetic:001',
            binding_id='binding:synthetic.observation:v1',
            ingress_type='observation',
            payload_artifact_id='artifact:sha256:observation-004',
            native_lineage=(),
            observed_at='2026-09-11T09:00:04Z',
        )


def test_environment_ingress_rejects_mutable_native_lineage():
    with pytest.raises(TypeError, match='native lineage must be an immutable tuple'):
        EnvironmentIngress(
            environment_ingress_id='environment-ingress:synthetic:mutable',
            environment_run_id='environment-run:synthetic:001',
            binding_id='binding:synthetic.observation:v1',
            ingress_type='observation',
            payload_artifact_id='artifact:sha256:observation-mutable',
            native_lineage=[('observation_id', 'native-observation-mutable')],
            observed_at='2026-09-11T09:00:04Z',
        )


def test_unconfigured_binding_cannot_reuse_an_allowed_ingress_type():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id='environment-ingress:synthetic:005',
        environment_run_id=environment_run.environment_run_id,
        binding_id='binding:unconfigured.observation:v1',
        ingress_type='observation',
        payload_artifact_id='artifact:sha256:observation-005',
        native_lineage=(),
        observed_at='2026-09-11T09:00:05Z',
    )
    policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.observation:v1',
                ingress_type='observation',
                action='state_update',
            ),
        ),
    )

    decision = policy.classify(environment_run, ingress)

    assert decision.action == 'reject'
    assert decision.reason_code == 'unsupported_ingress_binding'


def test_policy_for_another_environment_profile_cannot_classify_ingress():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id='environment-ingress:synthetic:006',
        environment_run_id=environment_run.environment_run_id,
        binding_id='binding:synthetic.observation:v1',
        ingress_type='observation',
        payload_artifact_id='artifact:sha256:observation-006',
        native_lineage=(),
        observed_at='2026-09-11T09:00:06Z',
    )
    policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:other:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.observation:v1',
                ingress_type='observation',
                action='state_update',
            ),
        ),
    )

    decision = policy.classify(environment_run, ingress)

    assert decision.action == 'reject'
    assert decision.reason_code == 'policy_environment_profile_mismatch'


def test_policy_from_another_domain_contract_revision_is_rejected():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id='environment-ingress:synthetic:007',
        environment_run_id=environment_run.environment_run_id,
        binding_id='binding:synthetic.observation:v1',
        ingress_type='observation',
        payload_artifact_id='artifact:sha256:observation-007',
        native_lineage=(),
        observed_at='2026-09-11T09:00:07Z',
    )
    policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:other-domain-pack',
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.observation:v1',
                ingress_type='observation',
                action='state_update',
            ),
        ),
    )

    decision = policy.classify(environment_run, ingress)

    assert decision.action == 'reject'
    assert decision.reason_code == 'policy_contract_revision_mismatch'


def test_task_bearing_rule_is_rejected_until_task_lineage_is_available():
    rule = TaskIngressRule(
        binding_id='binding:synthetic.request:v1',
        ingress_type='user_request',
        action='start_task',
    )

    with pytest.raises(ValueError, match='task-bearing ingress action'):
        TaskIngressPolicy(
            environment_profile_id='environment-profile:synthetic:v1',
            domain_contract_pack_revision='sha256:domain-pack-revision',
            rules=(rule,),
        )


def test_ingress_rule_rejects_an_unknown_action():
    with pytest.raises(ValueError, match='invalid ingress action'):
        TaskIngressRule(
            binding_id='binding:synthetic.observation:v1',
            ingress_type='observation',
            action='invoke_model',
        )
