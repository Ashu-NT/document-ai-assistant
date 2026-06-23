from collections import Counter

import pytest

from src.domain.document import Document, DocumentGraph, DocumentSection
from src.domain.document.value_objects import DocumentStatistics


@pytest.fixture
def sample_document_graph_multi_section(sample_document: Document) -> DocumentGraph:
    """DocumentGraph with three sections inserted out of sequence-number order."""
    graph = DocumentGraph(document=sample_document)
    # Inserted in reverse order — service must sort by sequence_number
    for title, level, seq in [
        ("Troubleshooting", 1, 3),
        ("Installation", 1, 1),
        ("Maintenance", 1, 2),
    ]:
        section = DocumentSection(
            section_id=f"sec_{seq:03d}",
            document_id=sample_document.document_id,
            title=title,
            level=level,
            sequence_number=seq,
        )
        graph.add_section(section)
    return graph


@pytest.fixture
def sample_document_graph_with_stats(sample_document_graph: DocumentGraph) -> DocumentGraph:
    """sample_document_graph with DocumentStatistics populated from actual graph contents."""
    graph = sample_document_graph
    chunk_type_counts = dict(Counter(str(c.chunk_type) for c in graph.chunks.values()))
    graph.document.statistics = DocumentStatistics(
        page_count=graph.document.statistics.page_count,
        element_count=len(graph.elements),
        section_count=len(graph.sections),
        chunk_count=len(graph.chunks),
        table_count=len(graph.tables),
        picture_count=len(graph.pictures),
        identifier_count=len(graph.identifiers),
        chunk_type_counts=chunk_type_counts,
    )
    return graph
