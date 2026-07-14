import pytest

pytest.importorskip("qdrant_client")

from qdrant_client.http.models import models

from src.infrastructure.retrieval.vector.qdrant_payload_mapper import (
    QdrantPayloadMapper,
)


def test_to_retrieved_chunk_attaches_citation_from_payload() -> None:
    point = models.ScoredPoint(
        id="point_001",
        version=1,
        score=0.91,
        payload={
            "chunk_id": "chunk_001",
            "document_id": "doc_001",
            "section_id": "sec_001",
            "section_path": ["7 Components", "Spare Parts List"],
            "chunk_type": "spare_parts_table",
            "content": "Filter A00103",
            "page_start": 85,
            "page_end": 87,
        },
    )

    chunk = QdrantPayloadMapper.to_retrieved_chunk(point)

    assert chunk.citation is not None
    assert chunk.citation.chunk_id == "chunk_001"
    assert chunk.citation.document_id == "doc_001"
    assert chunk.citation.section_title == "Spare Parts List"
    assert chunk.citation.source.page_start == 85
    assert chunk.citation.source.page_end == 87

