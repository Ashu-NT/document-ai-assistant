import copy

from src.application.workflows.classification.prompt_builders import (
    DocumentGraphClassificationSummaryBuilder,
)


def test_summary_builder_includes_representative_graph_content(
    sample_document_graph,
) -> None:
    builder = DocumentGraphClassificationSummaryBuilder()

    summary = builder.build(sample_document_graph)

    assert "Representative section paths:" in summary
    assert "Maintenance Schedule" in summary
    assert "Representative chunk previews:" in summary
    assert "Replace hydraulic filter every 1000 operating hours." in summary
    assert "Table signals:" in summary
    assert "Spare parts table" in summary
    assert "Picture signals:" in summary
    assert "Exploded view of hydraulic pump" in summary


def test_summary_builder_falls_back_to_elements_when_chunks_are_missing(
    sample_document_graph,
) -> None:
    builder = DocumentGraphClassificationSummaryBuilder()
    document_graph = copy.deepcopy(sample_document_graph)
    document_graph.chunks = {}

    summary = builder.build(document_graph)

    assert "Representative element previews:" in summary
    assert "Replace hydraulic filter every 1000 operating hours." in summary
