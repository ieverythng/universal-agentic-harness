from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, BrokenBarrierError

import pytest

from ab_harness import EnvironmentIngress
from ab_harness import DomainContractPack
from ab_harness import DomainEffectRule
from ab_harness import EnvironmentProfile
from ab_harness import EnvironmentProfileRegistry
from ab_harness import EnvironmentRunAttestation
from ab_harness import EnvironmentRunRegistry
from ab_harness import EnvironmentTaskRegistry
from ab_harness import LifecycleLedger
from ab_harness import TaskIngressRule
from ab_harness import TaskIngressDecision
from ab_harness import TaskLineage
from ab_harness.task_ingress_authority import TaskIngressAuthority


DOMAIN_PACK = DomainContractPack.issue(
    domain_contract_pack_id="domain-pack:synthetic:v1",
    frame_id="synthetic_runtime",
    registry_version="sha256:synthetic-registry",
    allowed_role_ids=("synthetic_agent",),
    supported_task_type_ids=("synthetic_task",),
    ingress_rules=(
        TaskIngressRule(
            binding_id="binding:synthetic.observation:v1",
            ingress_type="observation",
            action="state_update",
        ),
        TaskIngressRule(
            binding_id="binding:synthetic.request:v1",
            ingress_type="user_request",
            action="start_task",
            task_id_lineage_key="goal_id",
        ),
        TaskIngressRule(
            binding_id="binding:synthetic.feedback:v1",
            ingress_type="resume_request",
            action="resume_task",
            task_id_lineage_key="goal_id",
        ),
        TaskIngressRule(
            binding_id="binding:synthetic.feedback:v1",
            ingress_type="task_notification",
            action="notify_task",
            task_id_lineage_key="goal_id",
        ),
        TaskIngressRule(
            binding_id="binding:synthetic.unknown:v1",
            ingress_type="observation",
            action="state_update",
        ),
    ),
    effect_rules=(
        DomainEffectRule(
            effect_id="synthetic effect observed",
            object_id="synthetic_action",
            evidence_owner="synthetic.runtime.owner",
            failure_policy="terminal",
        ),
    ),
)
OTHER_DOMAIN_PACK = DomainContractPack.issue(
    domain_contract_pack_id=DOMAIN_PACK.domain_contract_pack_id,
    frame_id=DOMAIN_PACK.frame_id,
    registry_version=DOMAIN_PACK.registry_version,
    allowed_role_ids=DOMAIN_PACK.allowed_role_ids,
    supported_task_type_ids=DOMAIN_PACK.supported_task_type_ids,
    ingress_rules=DOMAIN_PACK.ingress_rules,
    effect_rules=DOMAIN_PACK.effect_rules,
    prohibited_effects=("another_effect",),
)


def _pack_with_rules(rules):
    return DomainContractPack.issue(
        domain_contract_pack_id=DOMAIN_PACK.domain_contract_pack_id,
        frame_id=DOMAIN_PACK.frame_id,
        registry_version=DOMAIN_PACK.registry_version,
        allowed_role_ids=DOMAIN_PACK.allowed_role_ids,
        supported_task_type_ids=DOMAIN_PACK.supported_task_type_ids,
        ingress_rules=rules,
        effect_rules=DOMAIN_PACK.effect_rules,
    )


def _active_environment_run(
    environment_run_id="environment-run:synthetic:001",
    attestation_id="environment-attestation:sha256:001",
    domain_contract_pack_revision=DOMAIN_PACK.revision,
):
    profile = EnvironmentProfile(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack_id="domain-pack:synthetic:v1",
        domain_contract_pack_revision=domain_contract_pack_revision,
        native_runtime_revision="synthetic-runtime:v1",
        environment_owner_id="synthetic.runtime.owner",
        required_interface_ids=("synthetic.observation",),
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
            started_at="2026-09-11T09:00:00Z",
            readiness_evidence_refs=("artifact:readiness:001",),
        )
    )


def test_normalized_observation_is_classified_as_an_environment_state_update():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:synthetic:001",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:synthetic.observation:v1",
        ingress_type="observation",
        payload_artifact_id="artifact:sha256:observation-001",
        native_lineage=(("observation_id", "native-observation-001"),),
        observed_at="2026-09-11T09:00:01Z",
    )
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
    )

    decision = authority.admit(environment_run, ingress)

    assert decision.environment_ingress_id == ingress.environment_ingress_id
    assert decision.environment_run_id == environment_run.environment_run_id
    assert decision.action == "state_update"
    assert decision.reason_code == "matched_rule"
    assert decision.task_id is None
    assert decision.trace_id is None


def test_new_task_preserves_domain_identity_and_receives_a_uah_trace():
    environment_run = _active_environment_run()
    ledger = LifecycleLedger()
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:synthetic:task-001",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:synthetic.request:v1",
        ingress_type="user_request",
        payload_artifact_id="artifact:sha256:request-001",
        native_lineage=(("goal_id", "goal:bring-cup:001"),),
        observed_at="2026-09-13T09:00:00Z",
    )
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=ledger,
    )

    decision = authority.admit(environment_run, ingress)

    assert decision.action == "start_task"
    assert decision.reason_code == "matched_rule"
    assert decision.domain_contract_pack_revision == DOMAIN_PACK.revision
    assert decision.task_id == "goal:bring-cup:001"
    assert decision.trace_id == (
        "trace:sha256:9665443f9db9073cc24dbebb5d288bd0cf928157f1509d8d8f83d8c0f578de9e"
    )
    assert decision.decision_id.startswith("task-ingress-decision:sha256:")
    assert (
        EnvironmentTaskRegistry(ledger)
        .require_start(
            environment_run_id=decision.environment_run_id,
            environment_ingress_id=decision.environment_ingress_id,
            ingress_artifact_id=decision.environment_ingress_artifact_id,
            decision_id=decision.decision_id,
            domain_contract_pack_revision=decision.domain_contract_pack_revision,
            task_id=decision.task_id,
            trace_id=decision.trace_id,
        )
        .starting_decision_id
        == decision.decision_id
    )


def test_task_ingress_decision_detects_post_construction_content_changes():
    decision = TaskIngressDecision(
        environment_ingress_id="environment-ingress:test",
        environment_ingress_artifact_id="environment-ingress:sha256:test",
        environment_run_id="environment-run:test",
        action="state_update",
        reason_code="matched_rule",
    )
    object.__setattr__(decision, "reason_code", "tampered")

    with pytest.raises(ValueError, match="identity does not match"):
        decision.to_dict()


def test_task_ingress_decision_verified_copy_rejects_shadowed_identity_method():
    decision = TaskIngressDecision(
        environment_ingress_id="environment-ingress:verified-copy",
        environment_ingress_artifact_id="environment-ingress:sha256:verified-copy",
        environment_run_id="environment-run:verified-copy",
        action="state_update",
        reason_code="matched_rule",
    )
    snapshot = TaskIngressDecision.verified_copy(decision)

    assert snapshot is not decision
    assert snapshot.decision_id == decision.decision_id
    object.__setattr__(decision, "reason_code", "forged")
    object.__setattr__(decision, "verify_identity", lambda: None)

    with pytest.raises(ValueError, match="identity does not match"):
        TaskIngressDecision.verified_copy(decision)


def test_environment_ingress_verified_copy_rejects_shadowed_identity_payload():
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:verified-copy",
        environment_run_id="environment-run:synthetic:001",
        binding_id="binding:synthetic.observation:v1",
        ingress_type="observation",
        payload_artifact_id="artifact:verified-copy",
        native_lineage=(("observation_id", "observation:verified-copy"),),
        observed_at="2026-10-21T09:00:00Z",
    )
    snapshot = EnvironmentIngress.verified_copy(ingress)
    original_payload = EnvironmentIngress._identity_payload(ingress)

    assert snapshot is not ingress
    assert snapshot.ingress_artifact_id == ingress.ingress_artifact_id
    object.__setattr__(ingress, "binding_id", "binding:synthetic.request:v1")
    object.__setattr__(ingress, "ingress_type", "user_request")
    object.__setattr__(ingress, "native_lineage", (("goal_id", "task:forged"),))
    object.__setattr__(ingress, "_identity_payload", lambda: original_payload)
    object.__setattr__(ingress, "verify_identity", lambda: None)

    with pytest.raises(ValueError, match="identity does not match"):
        EnvironmentIngress.verified_copy(ingress)


def test_environment_ingress_verified_copy_requires_the_concrete_owner_class():
    class DerivedEnvironmentIngress(EnvironmentIngress):
        pass

    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:derived",
        environment_run_id="environment-run:synthetic:001",
        binding_id="binding:synthetic.observation:v1",
        ingress_type="observation",
        payload_artifact_id="artifact:derived",
        native_lineage=(("observation_id", "observation:derived"),),
        observed_at="2026-10-21T09:00:00Z",
    )

    with pytest.raises(TypeError, match="concrete owner type"):
        DerivedEnvironmentIngress.verified_copy(ingress)


def test_environment_ingress_to_dict_uses_a_verified_snapshot():
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:verified-export",
        environment_run_id="environment-run:synthetic:001",
        binding_id="binding:synthetic.observation:v1",
        ingress_type="observation",
        payload_artifact_id="artifact:verified-export",
        native_lineage=(("observation_id", "observation:verified-export"),),
        observed_at="2026-10-21T09:00:01Z",
    )
    original_id = ingress.ingress_artifact_id
    object.__setattr__(ingress, "payload_artifact_id", "artifact:changed")
    object.__setattr__(ingress, "verify_identity", lambda: None)

    with pytest.raises(ValueError, match="identity does not match"):
        ingress.to_dict()

    assert ingress.ingress_artifact_id == original_id


def test_ingress_policy_rejects_post_construction_content_changes():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:synthetic:tampered",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:synthetic.request:v1",
        ingress_type="user_request",
        payload_artifact_id="artifact:sha256:request-tampered",
        native_lineage=(("goal_id", "goal:original"),),
        observed_at="2026-09-13T09:00:00Z",
    )
    object.__setattr__(
        ingress,
        "native_lineage",
        (("goal_id", "goal:tampered-after-hashing"),),
    )
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
    )

    with pytest.raises(ValueError, match="ingress identity does not match"):
        authority.admit(environment_run, ingress)


def test_authority_freezes_rule_values_at_construction():
    start_rule = TaskIngressRule(
        binding_id="binding:synthetic.request:v1",
        ingress_type="user_request",
        action="start_task",
        task_id_lineage_key="goal_id",
    )
    domain_pack = _pack_with_rules((start_rule,))
    environment_run = _active_environment_run(
        domain_contract_pack_revision=domain_pack.revision,
    )
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=domain_pack,
    )
    object.__setattr__(start_rule, "action", "state_update")

    decision = authority.admit(
        environment_run,
        EnvironmentIngress(
            environment_ingress_id="environment-ingress:synthetic:frozen-rule",
            environment_run_id=environment_run.environment_run_id,
            binding_id="binding:synthetic.request:v1",
            ingress_type="user_request",
            payload_artifact_id="artifact:sha256:frozen-rule",
            native_lineage=(("goal_id", "goal:frozen-rule"),),
            observed_at="2026-09-13T09:00:00Z",
        ),
    )

    assert decision.action == "start_task"
    assert decision.domain_contract_pack_revision == domain_pack.revision


def test_new_task_without_the_domain_identity_is_rejected():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:synthetic:task-missing",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:synthetic.request:v1",
        ingress_type="user_request",
        payload_artifact_id="artifact:sha256:request-missing",
        native_lineage=(("request_id", "request:001"),),
        observed_at="2026-09-13T09:00:01Z",
    )
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
    )

    decision = authority.admit(environment_run, ingress)

    assert decision.action == "reject"
    assert decision.reason_code == "missing_task_identity"
    assert decision.task_id is None
    assert decision.trace_id is None


def test_replayed_start_ingress_is_rejected_with_its_registered_lineage():
    environment_run = _active_environment_run()
    ledger = LifecycleLedger()
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:synthetic:replayed-start",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:synthetic.request:v1",
        ingress_type="user_request",
        payload_artifact_id="artifact:sha256:replayed-start",
        native_lineage=(("goal_id", "goal:replayed-start"),),
        observed_at="2026-09-13T10:00:00Z",
    )
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=ledger,
    )

    first = authority.admit(environment_run, ingress)
    replay = authority.admit(environment_run, ingress)

    assert first.action == "start_task"
    assert replay.action == "reject"
    assert replay.reason_code == "duplicate_environment_ingress"
    assert replay.task_id == first.task_id
    assert replay.trace_id == first.trace_id


def test_duplicate_start_is_rejected_across_stale_registry_instances(tmp_path):
    environment_run = _active_environment_run()
    path = tmp_path / "shared-lifecycle.jsonl"
    first_authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=LifecycleLedger(path),
    )
    stale_authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=LifecycleLedger(path),
    )
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:synthetic:shared-start",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:synthetic.request:v1",
        ingress_type="user_request",
        payload_artifact_id="artifact:sha256:shared-start",
        native_lineage=(("goal_id", "goal:shared-start"),),
        observed_at="2026-09-13T10:00:00Z",
    )

    first = first_authority.admit(environment_run, ingress)
    duplicate = stale_authority.admit(environment_run, ingress)

    assert first.action == "start_task"
    assert duplicate.action == "reject"
    assert duplicate.reason_code == "duplicate_environment_ingress"
    assert duplicate.task_id == first.task_id
    assert duplicate.trace_id == first.trace_id
    assert (
        EnvironmentTaskRegistry(LifecycleLedger(path))
        .require_start(
            environment_run_id=first.environment_run_id,
            environment_ingress_id=first.environment_ingress_id,
            ingress_artifact_id=first.environment_ingress_artifact_id,
            decision_id=first.decision_id,
            domain_contract_pack_revision=first.domain_contract_pack_revision,
            task_id=first.task_id,
            trace_id=first.trace_id,
        )
        .starting_decision_id
        == first.decision_id
    )


@pytest.mark.parametrize("same_ingress", (True, False))
def test_task_start_commands_remain_atomic_across_cooperating_writers(tmp_path, same_ingress):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    run = _active_environment_run()
    path = tmp_path / "atomic-starts.jsonl"
    authorities = [TaskIngressAuthority(
        environment_profile_id=run.attestation.environment_profile_id,
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=LifecycleLedger(path),
    ) for _ in range(2)]
    barrier = Barrier(2)

    def request(index):
        suffix = "shared" if same_ingress else str(index)
        ingress = EnvironmentIngress(
            environment_ingress_id="ingress:atomic:" + suffix,
            environment_run_id=run.environment_run_id,
            binding_id="binding:synthetic.request:v1",
            ingress_type="user_request",
            payload_artifact_id="artifact:atomic:" + suffix,
            native_lineage=(("goal_id", "task:atomic:" + suffix),),
            observed_at="2026-10-08T18:00:00Z",
        )
        barrier.wait()
        return authorities[index].admit(run, ingress)

    with ThreadPoolExecutor(max_workers=2) as pool:
        decisions = list(pool.map(request, range(2)))
    events = LifecycleLedger(path).events()
    assert sorted(decision.action for decision in decisions) == (
        ["reject", "start_task"] if same_ingress else ["start_task", "start_task"]
    )
    assert len(events) == (1 if same_ingress else 2)
    assert [event.sequence for event in events] == list(range(1, len(events) + 1))
    for decision in decisions:
        if decision.action == "start_task":
            assert EnvironmentTaskRegistry(LifecycleLedger(path)).require_start(
                environment_run_id=decision.environment_run_id,
                environment_ingress_id=decision.environment_ingress_id,
                ingress_artifact_id=decision.environment_ingress_artifact_id,
                decision_id=decision.decision_id,
                domain_contract_pack_revision=decision.domain_contract_pack_revision,
                task_id=decision.task_id,
                trace_id=decision.trace_id,
            ).task_id == decision.task_id


def test_rejected_or_mutated_start_ingress_records_no_authoritative_start():
    run = _active_environment_run()
    ledger = LifecycleLedger()
    authority = TaskIngressAuthority(
        environment_profile_id=run.attestation.environment_profile_id,
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=ledger,
    )
    ingress = EnvironmentIngress(
        environment_ingress_id="ingress:rejected-start",
        environment_run_id=run.environment_run_id,
        binding_id="binding:unreviewed-request",
        ingress_type="user_request",
        payload_artifact_id="artifact:rejected-start",
        native_lineage=(("goal_id", "task:rejected-start"),),
        observed_at="2026-10-08T18:00:00Z",
    )
    assert authority.admit(run, ingress).action == "reject"
    object.__setattr__(ingress, "binding_id", "binding:synthetic.request:v1")
    with pytest.raises(ValueError, match="identity does not match content"):
        authority.admit(run, ingress)
    assert ledger.events() == ()


def test_shadowed_ingress_verifier_cannot_admit_or_replay_a_forged_task_start(
    tmp_path,
):
    environment_run = _active_environment_run()
    ledger_path = tmp_path / "forged-ingress-start.jsonl"
    ledger = LifecycleLedger(ledger_path)
    authority = TaskIngressAuthority(
        environment_profile_id=environment_run.attestation.environment_profile_id,
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=ledger,
    )
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:forged-start",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:synthetic.observation:v1",
        ingress_type="observation",
        payload_artifact_id="artifact:forged-start",
        native_lineage=(("observation_id", "observation:legitimate"),),
        observed_at="2026-10-21T09:00:02Z",
    )
    original_ingress_artifact_id = ingress.ingress_artifact_id
    original_identity_payload = EnvironmentIngress._identity_payload(ingress)
    object.__setattr__(ingress, "binding_id", "binding:synthetic.request:v1")
    object.__setattr__(ingress, "ingress_type", "user_request")
    object.__setattr__(ingress, "native_lineage", (("goal_id", "task:forged"),))
    object.__setattr__(ingress, "_identity_payload", lambda: original_identity_payload)
    object.__setattr__(ingress, "verify_identity", lambda: None)

    with pytest.raises(ValueError, match="identity does not match"):
        authority.admit(environment_run, ingress)

    assert ingress.ingress_artifact_id == original_ingress_artifact_id
    assert ledger.events() == ()
    assert LifecycleLedger(ledger_path).events() == ()


def test_task_ingress_authority_rejects_stale_domain_policy_before_freezing():
    domain = _pack_with_rules(tuple(replace(rule) for rule in DOMAIN_PACK.ingress_rules))
    object.__setattr__(domain.ingress_rules[1], "binding_id", "binding:unreviewed")
    with pytest.raises(
        ValueError,
        match="revision does not match content|domain ingress rules must use canonical order",
    ):
        TaskIngressAuthority(
            environment_profile_id="environment-profile:synthetic:v1",
            domain_contract_pack=domain,
        )


def test_second_start_for_a_registered_domain_task_is_rejected():
    environment_run = _active_environment_run()
    ledger = LifecycleLedger()
    first_ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:synthetic:first-start",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:synthetic.request:v1",
        ingress_type="user_request",
        payload_artifact_id="artifact:sha256:first-start",
        native_lineage=(("goal_id", "goal:one-activation"),),
        observed_at="2026-09-13T10:01:00Z",
    )
    second_ingress = replace(
        first_ingress,
        environment_ingress_id="environment-ingress:synthetic:second-start",
        payload_artifact_id="artifact:sha256:second-start",
        observed_at="2026-09-13T10:01:01Z",
    )
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=ledger,
    )

    first = authority.admit(environment_run, first_ingress)
    duplicate_start = authority.admit(environment_run, second_ingress)

    assert first.action == "start_task"
    assert duplicate_start.action == "reject"
    assert duplicate_start.reason_code == "task_already_registered"
    assert duplicate_start.task_id == first.task_id
    assert duplicate_start.trace_id == first.trace_id


@pytest.mark.parametrize(
    "action,ingress_type",
    (
        ("resume_task", "resume_request"),
        ("notify_task", "task_notification"),
    ),
)
def test_registered_task_receives_existing_task_ingress_with_its_trace(
    action, ingress_type
):
    environment_run = _active_environment_run()
    ledger = LifecycleLedger()
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=ledger,
    )
    started = authority.admit(
        environment_run,
        EnvironmentIngress(
            environment_ingress_id="environment-ingress:synthetic:start-resume",
            environment_run_id=environment_run.environment_run_id,
            binding_id="binding:synthetic.request:v1",
            ingress_type="user_request",
            payload_artifact_id="artifact:sha256:start-resume",
            native_lineage=(("goal_id", "goal:resume-me"),),
            observed_at="2026-09-13T10:00:00Z",
        ),
    )

    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:synthetic:resume",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:synthetic.feedback:v1",
        ingress_type=ingress_type,
        payload_artifact_id="artifact:sha256:resume",
        native_lineage=(("goal_id", "goal:resume-me"),),
        observed_at="2026-09-13T12:01:00Z",
    )
    associated = authority.admit(environment_run, ingress)

    assert associated.action == action
    assert associated.reason_code == "matched_registered_task"
    assert associated.task_id == started.task_id
    assert associated.trace_id == started.trace_id
    assert associated.domain_contract_pack_revision == DOMAIN_PACK.revision
    recorded = ledger.events()[-1]
    assert recorded.artifact_refs == (
        ingress.ingress_artifact_id,
        associated.decision_id,
        DOMAIN_PACK.revision,
    )


def test_replayed_existing_task_ingress_is_rejected_through_the_authority():
    environment_run = _active_environment_run()
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
    )
    authority.admit(
        environment_run,
        EnvironmentIngress(
            environment_ingress_id="environment-ingress:synthetic:start-replay",
            environment_run_id=environment_run.environment_run_id,
            binding_id="binding:synthetic.request:v1",
            ingress_type="user_request",
            payload_artifact_id="artifact:sha256:start-replay",
            native_lineage=(("goal_id", "goal:replay-existing"),),
            observed_at="2026-09-13T12:00:00Z",
        ),
    )
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:synthetic:resume-replay",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:synthetic.feedback:v1",
        ingress_type="resume_request",
        payload_artifact_id="artifact:sha256:resume-replay",
        native_lineage=(("goal_id", "goal:replay-existing"),),
        observed_at="2026-09-13T12:01:00Z",
    )

    accepted = authority.admit(environment_run, ingress)
    replay = authority.admit(environment_run, ingress)

    assert accepted.action == "resume_task"
    assert replay.action == "reject"
    assert replay.reason_code == "duplicate_environment_ingress"
    assert replay.task_id == accepted.task_id
    assert replay.trace_id == accepted.trace_id


def test_existing_task_ingress_is_admitted_after_authority_restart(tmp_path):
    environment_run = _active_environment_run()
    path = tmp_path / "restart-lifecycle.jsonl"
    first_authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=LifecycleLedger(path),
    )
    started = first_authority.admit(
        environment_run,
        EnvironmentIngress(
            environment_ingress_id="environment-ingress:synthetic:start-restart",
            environment_run_id=environment_run.environment_run_id,
            binding_id="binding:synthetic.request:v1",
            ingress_type="user_request",
            payload_artifact_id="artifact:sha256:start-restart",
            native_lineage=(("goal_id", "goal:restart-existing"),),
            observed_at="2026-09-13T12:00:00Z",
        ),
    )
    restarted_authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=LifecycleLedger(path),
    )

    resumed = restarted_authority.admit(
        environment_run,
        EnvironmentIngress(
            environment_ingress_id="environment-ingress:synthetic:resume-restart",
            environment_run_id=environment_run.environment_run_id,
            binding_id="binding:synthetic.feedback:v1",
            ingress_type="resume_request",
            payload_artifact_id="artifact:sha256:resume-restart",
            native_lineage=(("goal_id", "goal:restart-existing"),),
            observed_at="2026-09-13T12:01:00Z",
        ),
    )

    assert resumed.action == "resume_task"
    assert resumed.task_id == started.task_id
    assert resumed.trace_id == started.trace_id


def test_existing_task_ingress_for_an_unknown_task_is_rejected():
    environment_run = _active_environment_run()
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
    )

    decision = authority.admit(
        environment_run,
        EnvironmentIngress(
            environment_ingress_id="environment-ingress:synthetic:unknown-task",
            environment_run_id=environment_run.environment_run_id,
            binding_id="binding:synthetic.feedback:v1",
            ingress_type="resume_request",
            payload_artifact_id="artifact:sha256:unknown-task",
            native_lineage=(("goal_id", "goal:not-registered"),),
            observed_at="2026-09-13T12:02:00Z",
        ),
    )

    assert decision.action == "reject"
    assert decision.reason_code == "unknown_task_identity"
    assert decision.task_id is None
    assert decision.trace_id is None


def test_existing_task_ingress_cannot_cross_environment_runs():
    first_run = _active_environment_run()
    second_run = _active_environment_run(
        environment_run_id="environment-run:synthetic:002",
        attestation_id="environment-attestation:sha256:002",
    )
    ledger = LifecycleLedger()
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=ledger,
    )
    authority.admit(
        first_run,
        EnvironmentIngress(
            environment_ingress_id="environment-ingress:synthetic:first-run",
            environment_run_id=first_run.environment_run_id,
            binding_id="binding:synthetic.request:v1",
            ingress_type="user_request",
            payload_artifact_id="artifact:sha256:first-run",
            native_lineage=(("goal_id", "goal:run-scoped"),),
            observed_at="2026-09-13T12:03:00Z",
        ),
    )
    decision = authority.admit(
        second_run,
        EnvironmentIngress(
            environment_ingress_id="environment-ingress:synthetic:second-run",
            environment_run_id=second_run.environment_run_id,
            binding_id="binding:synthetic.feedback:v1",
            ingress_type="resume_request",
            payload_artifact_id="artifact:sha256:second-run",
            native_lineage=(("goal_id", "goal:run-scoped"),),
            observed_at="2026-09-13T12:03:01Z",
        ),
    )

    assert decision.action == "reject"
    assert decision.reason_code == "unknown_task_identity"
    assert decision.task_id is None
    assert decision.trace_id is None


def test_ingress_from_another_environment_run_is_rejected():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:synthetic:002",
        environment_run_id="environment-run:synthetic:other",
        binding_id="binding:synthetic.observation:v1",
        ingress_type="observation",
        payload_artifact_id="artifact:sha256:observation-002",
        native_lineage=(),
        observed_at="2026-09-11T09:00:02Z",
    )
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
    )

    decision = authority.admit(environment_run, ingress)

    assert decision.action == "reject"
    assert decision.reason_code == "environment_run_mismatch"


def test_ingress_without_a_frozen_rule_is_rejected():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:synthetic:003",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:synthetic.unknown:v1",
        ingress_type="unknown_event",
        payload_artifact_id="artifact:sha256:unknown-003",
        native_lineage=(),
        observed_at="2026-09-11T09:00:03Z",
    )
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
    )

    decision = authority.admit(environment_run, ingress)

    assert decision.action == "reject"
    assert decision.reason_code == "unsupported_ingress_type"


def test_duplicate_ingress_rule_is_rejected():
    rule = TaskIngressRule(
        binding_id="binding:synthetic.observation:v1",
        ingress_type="observation",
        action="state_update",
    )

    with pytest.raises(ValueError, match="duplicate domain ingress rules"):
        _pack_with_rules((rule, rule))


def test_environment_ingress_requires_an_identity():
    with pytest.raises(ValueError, match="ingress fields must not be empty"):
        EnvironmentIngress(
            environment_ingress_id="",
            environment_run_id="environment-run:synthetic:001",
            binding_id="binding:synthetic.observation:v1",
            ingress_type="observation",
            payload_artifact_id="artifact:sha256:observation-004",
            native_lineage=(),
            observed_at="2026-09-11T09:00:04Z",
        )


def test_environment_ingress_rejects_mutable_native_lineage():
    with pytest.raises(TypeError, match="native lineage must be an immutable tuple"):
        EnvironmentIngress(
            environment_ingress_id="environment-ingress:synthetic:mutable",
            environment_run_id="environment-run:synthetic:001",
            binding_id="binding:synthetic.observation:v1",
            ingress_type="observation",
            payload_artifact_id="artifact:sha256:observation-mutable",
            native_lineage=[("observation_id", "native-observation-mutable")],
            observed_at="2026-09-11T09:00:04Z",
        )


def test_environment_ingress_rejects_duplicate_native_lineage_keys():
    with pytest.raises(ValueError, match="native lineage keys must be unique"):
        EnvironmentIngress(
            environment_ingress_id="environment-ingress:synthetic:duplicate",
            environment_run_id="environment-run:synthetic:001",
            binding_id="binding:synthetic.request:v1",
            ingress_type="user_request",
            payload_artifact_id="artifact:sha256:request-duplicate",
            native_lineage=(
                ("goal_id", "goal:001"),
                ("goal_id", "goal:002"),
            ),
            observed_at="2026-09-13T09:00:02Z",
        )


def test_environment_ingress_rejects_empty_native_lineage_values():
    with pytest.raises(ValueError, match="native lineage fields must not be empty"):
        EnvironmentIngress(
            environment_ingress_id="environment-ingress:synthetic:empty-lineage",
            environment_run_id="environment-run:synthetic:001",
            binding_id="binding:synthetic.request:v1",
            ingress_type="user_request",
            payload_artifact_id="artifact:sha256:request-empty-lineage",
            native_lineage=(("goal_id", ""),),
            observed_at="2026-09-13T09:00:03Z",
        )


def test_unconfigured_binding_cannot_reuse_an_allowed_ingress_type():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:synthetic:005",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:unconfigured.observation:v1",
        ingress_type="observation",
        payload_artifact_id="artifact:sha256:observation-005",
        native_lineage=(),
        observed_at="2026-09-11T09:00:05Z",
    )
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
    )

    decision = authority.admit(environment_run, ingress)

    assert decision.action == "reject"
    assert decision.reason_code == "unsupported_ingress_binding"


def test_policy_for_another_environment_profile_cannot_classify_ingress():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:synthetic:006",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:synthetic.observation:v1",
        ingress_type="observation",
        payload_artifact_id="artifact:sha256:observation-006",
        native_lineage=(),
        observed_at="2026-09-11T09:00:06Z",
    )
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:other:v1",
        domain_contract_pack=DOMAIN_PACK,
    )

    decision = authority.admit(environment_run, ingress)

    assert decision.action == "reject"
    assert decision.reason_code == "policy_environment_profile_mismatch"


def test_policy_from_another_domain_contract_revision_is_rejected():
    environment_run = _active_environment_run()
    ingress = EnvironmentIngress(
        environment_ingress_id="environment-ingress:synthetic:007",
        environment_run_id=environment_run.environment_run_id,
        binding_id="binding:synthetic.observation:v1",
        ingress_type="observation",
        payload_artifact_id="artifact:sha256:observation-007",
        native_lineage=(),
        observed_at="2026-09-11T09:00:07Z",
    )
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=OTHER_DOMAIN_PACK,
    )

    decision = authority.admit(environment_run, ingress)

    assert decision.action == "reject"
    assert decision.reason_code == "policy_contract_revision_mismatch"


def test_start_task_rule_requires_a_domain_identity_lineage_key():
    with pytest.raises(ValueError, match="task-bearing rule requires"):
        TaskIngressRule(
            binding_id="binding:synthetic.request:v1",
            ingress_type="user_request",
            action="start_task",
        )


def test_task_lineage_requires_complete_identity():
    with pytest.raises(ValueError, match="task lineage fields must not be empty"):
        TaskLineage(
            environment_run_id="environment-run:synthetic:001",
            task_id="",
            trace_id="trace:sha256:complete",
            starting_environment_ingress_id="environment-ingress:synthetic:001",
            starting_ingress_artifact_id="environment-ingress:sha256:complete",
            starting_decision_id="task-ingress-decision:sha256:complete",
            domain_contract_pack_revision="sha256:complete",
        )


def test_ingress_rule_rejects_an_unknown_action():
    with pytest.raises(ValueError, match="invalid ingress action"):
        TaskIngressRule(
            binding_id="binding:synthetic.observation:v1",
            ingress_type="observation",
            action="invoke_model",
        )


def test_default_in_memory_ledger_serializes_concurrent_public_task_starts():
    environment_run = _active_environment_run()
    writers_reached_clock = Barrier(2)

    def clock():
        try:
            writers_reached_clock.wait(timeout=0.25)
        except BrokenBarrierError:
            pass
        return "2026-09-11T09:01:00Z"

    ledger = LifecycleLedger(clock=clock)

    def admit(index):
        ingress = EnvironmentIngress(
            environment_ingress_id=f"environment-ingress:concurrent:{index}",
            environment_run_id=environment_run.environment_run_id,
            binding_id="binding:synthetic.request:v1",
            ingress_type="user_request",
            payload_artifact_id=f"artifact:sha256:concurrent-{index}",
            native_lineage=(("goal_id", f"goal:concurrent:{index}"),),
            observed_at="2026-09-11T09:01:00Z",
        )
        authority = TaskIngressAuthority(
            environment_profile_id="environment-profile:synthetic:v1",
            domain_contract_pack=DOMAIN_PACK,
            lifecycle_ledger=ledger,
        )
        return authority.admit(environment_run, ingress)

    with ThreadPoolExecutor(max_workers=2) as executor:
        decisions = tuple(executor.map(admit, (1, 2)))

    assert tuple(decision.action for decision in decisions) == (
        "start_task",
        "start_task",
    )
    events = ledger.events()
    assert tuple(event.sequence for event in events) == (1, 2)
    for decision in decisions:
        assert ledger.replay(decision.trace_id).events[0].event_type == "task_started"


def test_shared_registry_keeps_concurrent_read_projections_isolated():
    environment_run = _active_environment_run()
    ledger = LifecycleLedger()
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=ledger,
    )
    decision = authority.admit(
        environment_run,
        EnvironmentIngress(
            environment_ingress_id="environment-ingress:projection:seed",
            environment_run_id=environment_run.environment_run_id,
            binding_id="binding:synthetic.request:v1",
            ingress_type="user_request",
            payload_artifact_id="artifact:sha256:projection-seed",
            native_lineage=(("goal_id", "goal:projection:seed"),),
            observed_at="2026-09-11T09:01:00Z",
        ),
    )
    registry = EnvironmentTaskRegistry(ledger)
    readers_ready = Barrier(2)

    def read_lineage():
        readers_ready.wait(timeout=2)
        return registry.lineage_for_task(
            environment_run_id=environment_run.environment_run_id,
            task_id="goal:projection:seed",
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        lineages = tuple(executor.map(lambda _index: read_lineage(), range(2)))

    assert all(lineage is not None for lineage in lineages)
    assert {lineage.trace_id for lineage in lineages} == {decision.trace_id}


def test_shared_authority_admits_distinct_tasks_without_projection_races():
    environment_run = _active_environment_run()
    ledger = LifecycleLedger()
    authority = TaskIngressAuthority(
        environment_profile_id="environment-profile:synthetic:v1",
        domain_contract_pack=DOMAIN_PACK,
        lifecycle_ledger=ledger,
    )
    ingress_reads_ready = Barrier(2)

    def admit(index):
        ingress_reads_ready.wait(timeout=2)
        ingress = EnvironmentIngress(
            environment_ingress_id=f"environment-ingress:shared:{index}",
            environment_run_id=environment_run.environment_run_id,
            binding_id="binding:synthetic.request:v1",
            ingress_type="user_request",
            payload_artifact_id=f"artifact:sha256:shared-{index}",
            native_lineage=(("goal_id", f"goal:shared:{index}"),),
            observed_at="2026-09-11T09:01:00Z",
        )
        return authority.admit(environment_run, ingress)

    with ThreadPoolExecutor(max_workers=2) as executor:
        decisions = tuple(executor.map(admit, (1, 2)))

    assert tuple(decision.action for decision in decisions) == (
        "start_task",
        "start_task",
    )
    starts = tuple(event for event in ledger.events() if event.event_type == "task_started")
    assert len(starts) == 2
    assert {event.task_id for event in starts} == {"goal:shared:1", "goal:shared:2"}
