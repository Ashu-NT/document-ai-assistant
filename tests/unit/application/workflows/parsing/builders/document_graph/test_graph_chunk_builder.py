from src.application.workflows.parsing.builders.document_graph.graph_chunk_builder import (
    GraphChunkBuilder,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)
from src.domain.common import ChunkType
from src.domain.document import Document, DocumentGraph, DocumentHashes
from src.shared.ids import IdGenerator


class _StubSectionChunkBuilder:
    def __init__(self, payloads: list[ChunkPayload]) -> None:
        self._payloads = payloads

    def build_document_chunk_payloads(self, **_kwargs: object) -> list[ChunkPayload]:
        return self._payloads


def _make_graph() -> DocumentGraph:
    return DocumentGraph(
        document=Document(
            document_id="doc_001",
            file_name="manual.pdf",
            file_path="data/input/manual.pdf",
            hashes=DocumentHashes(file_hash="hash_1", content_hash="content_1"),
        )
    )


def _make_payload(**overrides: object) -> ChunkPayload:
    defaults: dict = {
        "section_id": "sec_001",
        "section_path": ["Specifications"],
        "content": "| Parameter | Value |",
        "chunk_type": ChunkType.TECHNICAL_SPECIFICATION,
        "embedding_text": "| Parameter | Value |",
        "table_ids": ["table_001"],
    }
    defaults.update(overrides)
    return ChunkPayload(**defaults)


def test_build_chunks_forwards_table_structure_fields_from_payload() -> None:
    payload = _make_payload(
        table_shape="specification_matrix",
        table_structure_quality=0.91,
        header_paths=[["Parameter"], ["Value"]],
        axis_summary={"rows": "parameter", "columns": "value"},
    )
    builder = GraphChunkBuilder(
        id_generator=IdGenerator(),
        section_chunk_builder=_StubSectionChunkBuilder([payload]),
    )

    chunks = builder.build_chunks(graph=_make_graph(), sections=[])

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.table_shape == "specification_matrix"
    assert chunk.table_structure_quality == 0.91
    assert chunk.header_paths == [["Parameter"], ["Value"]]
    assert chunk.axis_summary == {"rows": "parameter", "columns": "value"}


def test_build_chunks_defaults_table_structure_fields_when_payload_has_none() -> None:
    payload = _make_payload()
    builder = GraphChunkBuilder(
        id_generator=IdGenerator(),
        section_chunk_builder=_StubSectionChunkBuilder([payload]),
    )

    chunks = builder.build_chunks(graph=_make_graph(), sections=[])

    chunk = chunks[0]
    assert chunk.table_shape is None
    assert chunk.table_structure_quality is None
    assert chunk.header_paths == []
    assert chunk.axis_summary == {}
