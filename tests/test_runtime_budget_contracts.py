import pytest

from ab_harness.runtime_controls import BudgetDecision


@pytest.mark.parametrize(
    "field", ("units", "limit", "consumed_before", "consumed_after")
)
@pytest.mark.parametrize("value", (True, 1.0))
def test_budget_artifact_requires_integer_quantities(field, value):
    fields = dict(
        compiled_task_id="compiled:synthetic",
        environment_run_id="environment:synthetic",
        task_id="task:synthetic",
        trace_id="trace:synthetic",
        resource="model_call",
        subject_id="invocation:synthetic",
        units=1,
        limit=3,
        consumed_before=0,
        consumed_after=1,
        outcome="granted",
        reason_code="within_budget",
    )
    fields[field] = value
    if field == "consumed_before":
        fields["consumed_after"] = 2
    with pytest.raises(ValueError, match="finite integer"):
        BudgetDecision.issue(**fields)
