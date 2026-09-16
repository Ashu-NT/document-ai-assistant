from src.application.workflows.parsing.builders.document_graph.graph_chunk_builder import (
    GraphChunkBuilder,
)
from src.application.workflows.parsing.builders.chunking.builders.section_chunk.section_chunk_build_result import (
    SectionChunkBuildResult,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)
from src.domain.common import ChunkType
from src.domain.document import Document, DocumentGraph, DocumentHashes
from src.shared.ids import IdGenerator


class _StubSectionChunkBuilder:
    def __init__(self, payloads: list[ChunkPayload], structural_inference=None) -> None:
        self._payloads = payloads
        self._structural_inference = structural_inference

    def build_document_chunk_payloads(
        self, **_kwargs: object
    ) -> SectionChunkBuildResult:
        return SectionChunkBuildResult(
            payloads=self._payloads,
            structural_inference=self._structural_inference,
        )


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

    result = builder.build_chunks(graph=_make_graph(), sections=[])

    assert len(result.chunks) == 1
    chunk = result.chunks[0]
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

    result = builder.build_chunks(graph=_make_graph(), sections=[])

    chunk = result.chunks[0]
    assert chunk.table_shape is None
    assert chunk.table_structure_quality is None
    assert chunk.header_paths == []
    assert chunk.axis_summary == {}


def test_build_chunks_returns_structural_inference_explicitly_instead_of_via_attribute() -> (
    None
):
    """Regression test for the concurrent-parsing fix: the structural
    inference computed while building chunk payloads must come back as
    part of build_chunks()'s return value, not be read off a
    `last_structural_profile_inference` instance attribute afterward - a
    shared builder instance reused across concurrent build_chunks() calls
    could have that attribute overwritten before a caller read it back."""
    sentinel_inference = object()
    builder = GraphChunkBuilder(
        id_generator=IdGenerator(),
        section_chunk_builder=_StubSectionChunkBuilder(
            [_make_payload()], structural_inference=sentinel_inference
        ),
    )

    result = builder.build_chunks(graph=_make_graph(), sections=[])

    assert result.structural_inference is sentinel_inference
    assert not hasattr(builder, "last_structural_profile_inference")
