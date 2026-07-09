from unittest.mock import MagicMock

from src.application.reporting.document_parsing.chunking import (
    ChunkDistributionStatsCalculator,
)


def _make_chunk(chunk_id, chunk_type="general", section_path=None):
    chunk = MagicMock()
    chunk.chunk_id = chunk_id
    chunk.chunk_type = chunk_type
    chunk.section_path = section_path or ["Section 1"]
    chunk.content = "Some chunk content here."
    return chunk


def _make_result(document_id="doc1", chunk_count=5):
    result = MagicMock()
    result.document_id = document_id
    chunks = {f"c{i}": _make_chunk(f"c{i}") for i in range(chunk_count)}
    result.document_graph.chunks = chunks
    return result


def test_calculate_reports_total_and_type_distribution() -> None:
    calculator = ChunkDistributionStatsCalculator()
    payload = calculator.calculate(_make_result(chunk_count=3))

    assert payload["document_id"] == "doc1"
    assert payload["total_chunks"] == 3
    assert "type_distribution" in payload


def test_calculate_reports_section_path_coverage() -> None:
    calculator = ChunkDistributionStatsCalculator()
    payload = calculator.calculate(_make_result(chunk_count=2))

    assert payload["chunks_with_section_path"] == 2
    assert payload["chunks_without_section_path"] == 0


def test_calculate_handles_zero_chunks() -> None:
    calculator = ChunkDistributionStatsCalculator()
    payload = calculator.calculate(_make_result(chunk_count=0))

    assert payload["total_chunks"] == 0
    assert payload["avg_content_length_chars"] == 0
