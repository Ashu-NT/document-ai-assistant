from src.application.reporting.document_parsing.graph_build_profiling import (
    GraphBuildReportMarkdownRenderer,
)

_MINIMAL_REPORT_DATA = {
    "input_document": {"file_path": "TestDoc/example.pdf", "page_count": 12},
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
    },
    "stage_metrics": [],
    "architecture_map": [],
    "ranked_bottlenecks": [],
    "cprofile": {"top_cumulative": [], "top_call_count": []},
    "memory": {"peak_bytes": 0, "current_bytes": 0, "top_allocations": []},
}


def test_render_includes_input_document_and_counts() -> None:
    markdown = GraphBuildReportMarkdownRenderer().render(_MINIMAL_REPORT_DATA)

    assert "# Parsing Pipeline Performance Report" in markdown
    assert "TestDoc/example.pdf" in markdown
    assert "Pages: `12`" in markdown


def test_render_omits_operation_profiles_section_when_absent() -> None:
    markdown = GraphBuildReportMarkdownRenderer().render(_MINIMAL_REPORT_DATA)

    assert "## Operation Profiles" not in markdown


def test_display_operation_name_maps_known_keys() -> None:
    renderer = GraphBuildReportMarkdownRenderer()

    assert renderer._display_operation_name("docling_conversion") == "Docling Conversion"
    assert renderer._display_operation_name("unknown_stage") == "Unknown Stage"
