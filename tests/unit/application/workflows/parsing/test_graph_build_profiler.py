import logging

import pytest

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


def test_graph_build_profiler_logs_stage_completion_even_when_disabled(caplog) -> None:
    """The heavy GraphBuildStageMetric history stays opt-in (`enabled`), but
    basic stage-completion logging must fire regardless - this is what
    makes a real corpus run observable without turning profiling on."""
    profiler = GraphBuildProfiler.disabled()
    profiler.document_id = "doc_disabled_logging"

    logger_name = "src.application.workflows.parsing.profiling.graph_build_profiler"
    with caplog.at_level("INFO", logger=logger_name):
        with profiler.measure(
            name="document_graph_builder.add_sections",
            input_counts={"sections": 3},
        ) as stage:
            stage.output_counts["graph_sections"] = 3

    assert profiler.stage_metrics == []  # heavy history stays off
    assert len(caplog.records) == 1
    message = caplog.records[0].getMessage()
    assert "stage=document_graph_builder.add_sections" in message
    assert "status=ok" in message
    assert "document_id=doc_disabled_logging" in message
    assert "sections=3" in message
    assert "graph_sections=3" in message


def test_graph_build_profiler_logs_error_and_reraises_on_stage_exception(caplog) -> None:
    profiler = GraphBuildProfiler.disabled()
    logger_name = "src.application.workflows.parsing.profiling.graph_build_profiler"

    with caplog.at_level("DEBUG", logger=logger_name):
        with pytest.raises(ValueError, match="bad stage"):
            with profiler.measure(name="failing_stage"):
                raise ValueError("bad stage")

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.ERROR
    message = record.getMessage()
    assert "stage=failing_stage" in message
    assert "status=failed" in message
    assert "error=bad stage" in message


def test_graph_build_profiler_output_counts_do_not_collide_with_fixed_log_fields(
    caplog,
) -> None:
    """document_graph_builder.py sets stage.output_counts["document_id"] -
    this must never crash or shadow the profiler's own document_id."""
    profiler = GraphBuildProfiler.disabled()
    profiler.document_id = "doc_real"
    logger_name = "src.application.workflows.parsing.profiling.graph_build_profiler"

    with caplog.at_level("INFO", logger=logger_name):
        with profiler.measure(name="initialize_document") as stage:
            stage.output_counts["document_id"] = "doc_from_output_counts"

    message = caplog.records[0].getMessage()
    assert "document_id=doc_real" in message
    assert "doc_from_output_counts" not in message


def test_graph_build_profiler_aggregates_repeated_nested_stages(caplog) -> None:
    profiler = GraphBuildProfiler(document_id="doc_aggregate")
    logger_name = "src.application.workflows.parsing.profiling.graph_build_profiler"

    with caplog.at_level("INFO", logger=logger_name):
        for _ in range(3):
            with profiler.aggregate(
                name="chunk_fragment_builder.ordinary_elements",
                input_counts={"sections": 1, "elements": 2},
            ) as stage:
                stage.output_counts["fragments"] = 1

        assert caplog.records == []
        profiler.flush_aggregates()

    assert len(caplog.records) == 1
    message = caplog.records[0].getMessage()
    assert "stage=chunk_fragment_builder.ordinary_elements" in message
    assert "invocations=3" in message
    assert "sections=3" in message
    assert "elements=6" in message
    assert "fragments=3" in message
    assert profiler.stage_metrics[-1].operations["invocations"] == 3


def test_graph_build_profiler_flush_clears_aggregate_batch(caplog) -> None:
    profiler = GraphBuildProfiler.disabled()
    logger_name = "src.application.workflows.parsing.profiling.graph_build_profiler"

    with caplog.at_level("INFO", logger=logger_name):
        with profiler.aggregate(name="nested"):
            pass
        profiler.flush_aggregates()
        profiler.flush_aggregates()

    assert len(caplog.records) == 1
