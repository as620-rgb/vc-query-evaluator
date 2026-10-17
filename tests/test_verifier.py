from types import SimpleNamespace
from verifier.task import verify_task


def test_verify_rag_gold():
    mock_agent_output = SimpleNamespace(
        start_node="company:doordash",
        target_companies=["Instacart", "Airbnb"],
        traversal_paths=[
            [
                SimpleNamespace(hop=1, from_node="company:doordash", relation="BELONGS_TO_BATCH", to_node="batch:s13"),
                SimpleNamespace(hop=2, from_node="batch:s13", relation="REV_BELONGS_TO_BATCH", to_node="company:instacart")
            ]
        ],
        reasoning_summary="Found 2 related companies.",
        total_hops_executed=2
    )

    result = verify_task(task_input={}, agent_output=mock_agent_output, workspace_path=".")
    assert result["score"] == 1.0


def test_verify_rag_broken():
    mock_broken_output = SimpleNamespace(
        start_node="company:doordash",
        target_companies=[],
        traversal_paths=[],
        reasoning_summary="No paths",
        total_hops_executed=1
    )

    result = verify_task(task_input={}, agent_output=mock_broken_output, workspace_path=".")
    assert result["score"] == 0.0
