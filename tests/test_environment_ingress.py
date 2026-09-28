from dataclasses import replace

import pytest

from ab_harness import EnvironmentIngress
from ab_harness import EnvironmentProfile
from ab_harness import EnvironmentProfileRegistry
from ab_harness import EnvironmentRunAttestation
from ab_harness import EnvironmentRunRegistry
from ab_harness import EnvironmentTaskRegistry
from ab_harness import TaskIngressPolicy
from ab_harness import TaskIngressRule
from ab_harness import TaskLineage


def _active_environment_run(
    environment_run_id='environment-run:synthetic:001',
    attestation_id='environment-attestation:sha256:001',
):
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
            environment_run_id=environment_run_id,
            environment_profile_id=profile.environment_profile_id,
            domain_contract_pack_revision=profile.domain_contract_pack_revision,
            native_runtime_revision=profile.native_runtime_revision,
            environment_owner_id=profile.environment_owner_id,
            attestation_id=attestation_id,
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


def test_new_task_preserves_domain_identity_and_receives_a_uah_trace():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id='environment-ingress:synthetic:task-001',
        environment_run_id=environment_run.environment_run_id,
        binding_id='binding:synthetic.request:v1',
        ingress_type='user_request',
        payload_artifact_id='artifact:sha256:request-001',
        native_lineage=(('goal_id', 'goal:bring-cup:001'),),
        observed_at='2026-09-13T09:00:00Z',
    )
    policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        task_registry=EnvironmentTaskRegistry(),
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.request:v1',
                ingress_type='user_request',
                action='start_task',
                task_id_lineage_key='goal_id',
            ),
        ),
    )

    decision = policy.classify(environment_run, ingress)

    assert decision.action == 'start_task'
    assert decision.reason_code == 'matched_rule'
    assert decision.domain_contract_pack_revision == 'sha256:domain-pack-revision'
    assert decision.task_id == 'goal:bring-cup:001'
    assert decision.trace_id == (
        'trace:sha256:'
        '9665443f9db9073cc24dbebb5d288bd0cf928157f1509d8d8f83d8c0f578de9e'
    )


def test_new_task_without_the_domain_identity_is_rejected():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id='environment-ingress:synthetic:task-missing',
        environment_run_id=environment_run.environment_run_id,
        binding_id='binding:synthetic.request:v1',
        ingress_type='user_request',
        payload_artifact_id='artifact:sha256:request-missing',
        native_lineage=(('request_id', 'request:001'),),
        observed_at='2026-09-13T09:00:01Z',
    )
    policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        task_registry=EnvironmentTaskRegistry(),
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.request:v1',
                ingress_type='user_request',
                action='start_task',
                task_id_lineage_key='goal_id',
            ),
        ),
    )

    decision = policy.classify(environment_run, ingress)

    assert decision.action == 'reject'
    assert decision.reason_code == 'missing_task_identity'
    assert decision.task_id is None
    assert decision.trace_id is None


def test_replayed_start_ingress_is_rejected_with_its_registered_lineage():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id='environment-ingress:synthetic:replayed-start',
        environment_run_id=environment_run.environment_run_id,
        binding_id='binding:synthetic.request:v1',
        ingress_type='user_request',
        payload_artifact_id='artifact:sha256:replayed-start',
        native_lineage=(('goal_id', 'goal:replayed-start'),),
        observed_at='2026-09-13T10:00:00Z',
    )
    registry = EnvironmentTaskRegistry()
    policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        task_registry=registry,
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.request:v1',
                ingress_type='user_request',
                action='start_task',
                task_id_lineage_key='goal_id',
            ),
        ),
    )

    first = policy.classify(environment_run, ingress)
    replay = policy.classify(environment_run, ingress)

    assert first.action == 'start_task'
    assert replay.action == 'reject'
    assert replay.reason_code == 'duplicate_environment_ingress'
    assert replay.task_id == first.task_id
    assert replay.trace_id == first.trace_id


def test_second_start_for_a_registered_domain_task_is_rejected():
    environment_run = _active_environment_run()
    first_ingress = EnvironmentIngress(
        environment_ingress_id='environment-ingress:synthetic:first-start',
        environment_run_id=environment_run.environment_run_id,
        binding_id='binding:synthetic.request:v1',
        ingress_type='user_request',
        payload_artifact_id='artifact:sha256:first-start',
        native_lineage=(('goal_id', 'goal:one-activation'),),
        observed_at='2026-09-13T10:01:00Z',
    )
    second_ingress = replace(
        first_ingress,
        environment_ingress_id='environment-ingress:synthetic:second-start',
        payload_artifact_id='artifact:sha256:second-start',
        observed_at='2026-09-13T10:01:01Z',
    )
    policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        task_registry=EnvironmentTaskRegistry(),
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.request:v1',
                ingress_type='user_request',
                action='start_task',
                task_id_lineage_key='goal_id',
            ),
        ),
    )

    first = policy.classify(environment_run, first_ingress)
    duplicate_start = policy.classify(environment_run, second_ingress)

    assert first.action == 'start_task'
    assert duplicate_start.action == 'reject'
    assert duplicate_start.reason_code == 'task_already_registered'
    assert duplicate_start.task_id == first.task_id
    assert duplicate_start.trace_id == first.trace_id


@pytest.mark.parametrize(
    'action,ingress_type',
    (
        ('resume_task', 'resume_request'),
        ('notify_task', 'task_notification'),
    ),
)
def test_registered_task_receives_existing_task_ingress_with_its_trace(
    action, ingress_type
):
    environment_run = _active_environment_run()
    registry = EnvironmentTaskRegistry()
    start_policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        task_registry=registry,
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.request:v1',
                ingress_type='user_request',
                action='start_task',
                task_id_lineage_key='goal_id',
            ),
        ),
    )
    started = start_policy.classify(
        environment_run,
        EnvironmentIngress(
            environment_ingress_id='environment-ingress:synthetic:start-resume',
            environment_run_id=environment_run.environment_run_id,
            binding_id='binding:synthetic.request:v1',
            ingress_type='user_request',
            payload_artifact_id='artifact:sha256:start-resume',
            native_lineage=(('goal_id', 'goal:resume-me'),),
            observed_at='2026-09-13T10:00:00Z',
        ),
    )
    existing_task_policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        task_registry=registry,
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.feedback:v1',
                ingress_type=ingress_type,
                action=action,
                task_id_lineage_key='goal_id',
            ),
        ),
    )

    associated = existing_task_policy.classify(
        environment_run,
        EnvironmentIngress(
            environment_ingress_id='environment-ingress:synthetic:resume',
            environment_run_id=environment_run.environment_run_id,
            binding_id='binding:synthetic.feedback:v1',
            ingress_type=ingress_type,
            payload_artifact_id='artifact:sha256:resume',
            native_lineage=(('goal_id', 'goal:resume-me'),),
            observed_at='2026-09-13T12:01:00Z',
        ),
    )

    assert associated.action == action
    assert associated.reason_code == 'matched_registered_task'
    assert associated.task_id == started.task_id
    assert associated.trace_id == started.trace_id


def test_existing_task_ingress_for_an_unknown_task_is_rejected():
    environment_run = _active_environment_run()
    policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        task_registry=EnvironmentTaskRegistry(),
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.feedback:v1',
                ingress_type='resume_request',
                action='resume_task',
                task_id_lineage_key='goal_id',
            ),
        ),
    )

    decision = policy.classify(
        environment_run,
        EnvironmentIngress(
            environment_ingress_id='environment-ingress:synthetic:unknown-task',
            environment_run_id=environment_run.environment_run_id,
            binding_id='binding:synthetic.feedback:v1',
            ingress_type='resume_request',
            payload_artifact_id='artifact:sha256:unknown-task',
            native_lineage=(('goal_id', 'goal:not-registered'),),
            observed_at='2026-09-13T12:02:00Z',
        ),
    )

    assert decision.action == 'reject'
    assert decision.reason_code == 'unknown_task_identity'
    assert decision.task_id is None
    assert decision.trace_id is None


def test_existing_task_ingress_cannot_cross_environment_runs():
    first_run = _active_environment_run()
    second_run = _active_environment_run(
        environment_run_id='environment-run:synthetic:002',
        attestation_id='environment-attestation:sha256:002',
    )
    registry = EnvironmentTaskRegistry()
    start_policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        task_registry=registry,
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.request:v1',
                ingress_type='user_request',
                action='start_task',
                task_id_lineage_key='goal_id',
            ),
        ),
    )
    start_policy.classify(
        first_run,
        EnvironmentIngress(
            environment_ingress_id='environment-ingress:synthetic:first-run',
            environment_run_id=first_run.environment_run_id,
            binding_id='binding:synthetic.request:v1',
            ingress_type='user_request',
            payload_artifact_id='artifact:sha256:first-run',
            native_lineage=(('goal_id', 'goal:run-scoped'),),
            observed_at='2026-09-13T12:03:00Z',
        ),
    )
    resume_policy = TaskIngressPolicy(
        environment_profile_id='environment-profile:synthetic:v1',
        domain_contract_pack_revision='sha256:domain-pack-revision',
        task_registry=registry,
        rules=(
            TaskIngressRule(
                binding_id='binding:synthetic.feedback:v1',
                ingress_type='resume_request',
                action='resume_task',
                task_id_lineage_key='goal_id',
            ),
        ),
    )

    decision = resume_policy.classify(
        second_run,
        EnvironmentIngress(
            environment_ingress_id='environment-ingress:synthetic:second-run',
            environment_run_id=second_run.environment_run_id,
            binding_id='binding:synthetic.feedback:v1',
            ingress_type='resume_request',
            payload_artifact_id='artifact:sha256:second-run',
            native_lineage=(('goal_id', 'goal:run-scoped'),),
            observed_at='2026-09-13T12:03:01Z',
        ),
    )

    assert decision.action == 'reject'
    assert decision.reason_code == 'unknown_task_identity'
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


def test_environment_ingress_rejects_duplicate_native_lineage_keys():
    with pytest.raises(ValueError, match='native lineage keys must be unique'):
        EnvironmentIngress(
            environment_ingress_id='environment-ingress:synthetic:duplicate',
            environment_run_id='environment-run:synthetic:001',
            binding_id='binding:synthetic.request:v1',
            ingress_type='user_request',
            payload_artifact_id='artifact:sha256:request-duplicate',
            native_lineage=(
                ('goal_id', 'goal:001'),
                ('goal_id', 'goal:002'),
            ),
            observed_at='2026-09-13T09:00:02Z',
        )


def test_environment_ingress_rejects_empty_native_lineage_values():
    with pytest.raises(ValueError, match='native lineage fields must not be empty'):
        EnvironmentIngress(
            environment_ingress_id='environment-ingress:synthetic:empty-lineage',
            environment_run_id='environment-run:synthetic:001',
            binding_id='binding:synthetic.request:v1',
            ingress_type='user_request',
            payload_artifact_id='artifact:sha256:request-empty-lineage',
            native_lineage=(('goal_id', ''),),
            observed_at='2026-09-13T09:00:03Z',
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


def test_start_task_rule_requires_a_domain_identity_lineage_key():
    with pytest.raises(ValueError, match='task-bearing rule requires'):
        TaskIngressRule(
            binding_id='binding:synthetic.request:v1',
            ingress_type='user_request',
            action='start_task',
        )


@pytest.mark.parametrize(
    'action', ('start_task', 'resume_task', 'notify_task')
)
def test_task_bearing_actions_require_a_task_registry(action):
    rule = TaskIngressRule(
        binding_id='binding:synthetic.request:v1',
        ingress_type='user_request',
        action=action,
        task_id_lineage_key='goal_id',
    )

    with pytest.raises(ValueError, match='requires a task registry'):
        TaskIngressPolicy(
            environment_profile_id='environment-profile:synthetic:v1',
            domain_contract_pack_revision='sha256:domain-pack-revision',
            rules=(rule,),
        )


def test_task_lineage_requires_complete_identity():
    with pytest.raises(ValueError, match='task lineage fields must not be empty'):
        TaskLineage(
            environment_run_id='environment-run:synthetic:001',
            task_id='',
            trace_id='trace:sha256:complete',
            starting_environment_ingress_id='environment-ingress:synthetic:001',
        )


def test_ingress_rule_rejects_an_unknown_action():
    with pytest.raises(ValueError, match='invalid ingress action'):
        TaskIngressRule(
            binding_id='binding:synthetic.observation:v1',
            ingress_type='observation',
            action='invoke_model',
        )
