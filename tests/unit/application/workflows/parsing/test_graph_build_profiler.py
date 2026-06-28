from src.application.workflows.parsing.profiling import (
    GraphBuildProfiler,
    GraphBuildReportWriter,
)


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


def test_graph_build_report_writer_writes_json_and_markdown(tmp_path) -> None:
    writer = GraphBuildReportWriter(tmp_path)
    report_data = {
        "input_document": {
            "file_path": "TestDoc/example.pdf",
            "page_count": 12,
        },
        "counts": {
            "canonical_elements": 100,
            "sections": 8,
            "elements": 100,
            "chunks": 24,
            "tables": 2,
            "pictures": 3,
        },
        "timings": {
            "raw_parse_seconds": 1.0,
            "normalize_seconds": 0.5,
            "graph_build_seconds": 2.0,
            "baseline_graph_build_seconds": 4.0,
            "graph_build_improvement_percent": 50.0,
        },
        "stage_metrics": [
            {
                "name": "section_builder.resolve_hierarchy",
                "started_at_offset_seconds": 0.0,
                "ended_at_offset_seconds": 1.0,
                "elapsed_seconds": 1.0,
                "input_counts": {"headers": 10},
                "output_counts": {"resolved_headers": 10},
                "operations": {},
            }
        ],
        "architecture_map": [
            {
                "name": "section_builder.resolve_hierarchy",
                "owner": "SectionHierarchyResolver",
                "function": "resolve",
                "responsibility": "Resolve hierarchy.",
                "worst_case_complexity": "O(h^2 + n)",
                "complexity_reason": "Header pair heuristics.",
            }
        ],
        "ranked_bottlenecks": [
            {
                "rank": 1,
                "function": "section_builder.resolve_hierarchy",
                "complexity": "O(h^2 + n)",
                "runtime_percent": 50.0,
                "evidence": "elapsed=1.0s",
                "recommendation": "Keep the optimized index.",
            }
        ],
        "operation_profiles": {
            "docling_conversion": {
                "elapsed_seconds": 3.0,
                "cprofile": {
                    "prof_path": "outputs/debug_graph_build/example/docling_conversion.prof",
                    "top_cumulative": [
                        {
                            "calls": 1,
                            "function": "docling_parser.parse",
                            "cumulative_seconds": 3.0,
                            "total_seconds": 0.1,
                        }
                    ],
                    "top_call_count": [],
                    "top_recursive": [],
                },
                "memory": {
                    "current_bytes": 256,
                    "peak_bytes": 4096,
                    "top_allocations": [],
                },
            }
        },
        "cprofile": {
            "prof_path": "outputs/debug_graph_build/example/graph_build.prof",
            "top_cumulative": [
                {
                    "calls": 1,
                    "function": "section_builder.resolve_hierarchy",
                    "cumulative_seconds": 1.0,
                    "total_seconds": 1.0,
                }
            ],
            "top_call_count": [
                {
                    "calls": 10,
                    "function": "chunk_semantic_signal_extractor._marker_hits",
                    "cumulative_seconds": 0.5,
                    "total_seconds": 0.3,
                }
            ],
            "top_recursive": [],
        },
        "memory": {
            "current_bytes": 1024,
            "peak_bytes": 2048,
            "top_allocations": [
                {
                    "trace": "example.py:10",
                    "size_bytes": 512,
                    "count": 2,
                }
            ],
        },
    }

    json_path, markdown_path = writer.write(report_data=report_data)

    assert json_path.exists()
    assert markdown_path.exists()
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "Parsing Pipeline Performance Report" in markdown
    assert "## Operation Profiles" in markdown
    assert "Docling Conversion" in markdown
