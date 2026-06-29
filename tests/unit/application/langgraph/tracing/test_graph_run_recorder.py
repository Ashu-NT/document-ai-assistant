from src.application.langgraph.tracing import GraphRunRecorder


def test_graph_run_recorder_records_node_timings() -> None:
    recorder = GraphRunRecorder()

    token = recorder.start_node(
        "plan_step",
        route="planned_task",
        tool_name="answer_question",
        plan_id="plan_1",
        plan_goal="compare specifications and maintenance tasks",
        step_id="step_1",
        selected_document_id="doc-42",
    )
    trace_entry = recorder.finish_node(
        token,
        success=True,
        fallback_reason="not_used",
    )

    assert trace_entry["node_name"] == "plan_step"
    assert trace_entry["elapsed_ms"] >= 0
    assert trace_entry["success"] is True
    assert trace_entry["plan_id"] == "plan_1"
    assert trace_entry["step_id"] == "step_1"
    assert trace_entry["selected_document_id"] == "doc-42"
    assert trace_entry["fallback_reason"] == "not_used"
