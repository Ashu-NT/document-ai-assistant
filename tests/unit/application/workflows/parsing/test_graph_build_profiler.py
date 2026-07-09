from src.application.workflows.parsing.profiling import GraphBuildProfiler


def test_graph_build_profiler_records_stage_metrics() -> None:
    messages: list[str] = []
    profiler = GraphBuildProfiler(progress_callback=messages.append)

    with profiler.measure(
        name="section_builder.resolve_hierarchy",
        input_counts={"headers": 10},
    ) as stage:
        stage.output_counts["resolved_headers"] = 10
        stage.operations["strategy"] = "layout_heuristic"

    assert len(profiler.stage_metrics) == 1
    metric = profiler.stage_metrics[0]
    assert metric.name == "section_builder.resolve_hierarchy"
    assert metric.input_counts["headers"] == 10
    assert metric.output_counts["resolved_headers"] == 10
    assert metric.operations["strategy"] == "layout_heuristic"
    assert metric.elapsed_seconds >= 0
    assert messages
