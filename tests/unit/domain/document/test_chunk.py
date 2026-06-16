from src.domain.common import ChunkType
from src.domain.document import DocumentChunk


def test_chunk_statistics_are_created_from_content() -> None:
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        section_id="sec_001",
        content="Replace hydraulic filter every 1000 operating hours.",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
    )

    assert chunk.statistics is not None
    assert chunk.statistics.char_count == len(chunk.content)
    assert chunk.statistics.token_count_estimate is not None
    assert chunk.statistics.token_count_estimate > 0


def test_chunk_knows_if_embedding_text_exists() -> None:
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        section_id="sec_001",
        content="Replace hydraulic filter.",
        embedding_text="Section: Maintenance\nReplace hydraulic filter.",
    )

    assert chunk.has_embedding_text()


def test_chunk_without_embedding_text_returns_false() -> None:
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        section_id="sec_001",
        content="Replace hydraulic filter.",
    )

    assert not chunk.has_embedding_text()