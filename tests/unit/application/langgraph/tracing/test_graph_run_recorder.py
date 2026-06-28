from src.application.langgraph.tracing import GraphRunRecorder


def test_graph_run_recorder_records_node_timings() -> None:
    recorder = GraphRunRecorder()

    token = recorder.start_node("route_request", route="list_documents")
    trace_entry = recorder.finish_node(token, success=True)

    assert trace_entry["node_name"] == "route_request"
    assert trace_entry["elapsed_ms"] >= 0
    assert trace_entry["success"] is True
