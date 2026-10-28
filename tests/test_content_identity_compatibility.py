from ab_harness.agent_identity import AgentManifest
from ab_harness.operation_edges import OperationEdge
from ab_harness.runtime_controls import BudgetDecision
from ab_harness.schema_validation import ArgumentField
from ab_harness.schema_validation import ObjectArgumentSchema


def test_strict_authority_artifact_identities_remain_byte_compatible():
    manifest = AgentManifest(
        role_configuration_id="role:test:v1",
        model_configuration_id="model:test:v1",
        prompt_pack_id="prompt:test:v1",
        harness_build_id="harness:test:v1",
        adapter_revisions=(("zeta", "2"), ("alpha", "1")),
    )
    schema = ObjectArgumentSchema.issue(
        schema_ref="schema:test:v1",
        fields=(
            ArgumentField("count", "integer"),
            ArgumentField("name", "string"),
        ),
        required=("name",),
    )
    edge = OperationEdge.issue(
        environment_run_id="environment-run:test",
        task_id="task:test",
        trace_id="trace:test",
        source_operation_id="operation:source",
        target_operation_id="operation:target",
        relation="decomposes_to",
        source_frame_id="frame:test",
        target_frame_id="frame:test",
    )
    budget = BudgetDecision.issue(
        compiled_task_id="compiled-task:test",
        environment_run_id="environment-run:test",
        task_id="task:test",
        trace_id="trace:test",
        resource="tool_call",
        subject_id="operation:test",
        units=1,
        limit=2,
        consumed_before=0,
        consumed_after=1,
        outcome="granted",
        reason_code="within_budget",
    )

    assert manifest.agent_id == (
        "agent:sha256:cf25e2c9ce30ef8c55faf1b268b87377"
        "01741b45d88be4e0ee1113dfd0347371"
    )
    assert schema.schema_id == (
        "input-schema:sha256:63b74346ae911291477d1ec08bf84f636"
        "2758e9a2c9de1287494a5ff69a5f321"
    )
    assert edge.edge_id == (
        "operation-edge:sha256:2db976fcdc7e6f47311e9295d70e3cde"
        "5ee53c392b3a299f8ac5da9f2b1b92c0"
    )
    assert budget.decision_id == (
        "budget-decision:sha256:59ae22e2ee89b4293019bade46e060ceb"
        "fe3339f06f8007c74621fcb31b4baae"
    )
