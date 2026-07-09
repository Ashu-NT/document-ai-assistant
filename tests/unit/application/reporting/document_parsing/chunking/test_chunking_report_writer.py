import json
from unittest.mock import MagicMock

from src.application.reporting.document_parsing.chunking import ChunkingReportWriter


def _make_chunk(chunk_id):
    chunk = MagicMock()
    chunk.chunk_id = chunk_id
    chunk.chunk_type = "general"
    chunk.section_path = ["Section 1"]
    chunk.content = "Some chunk content here."
    return chunk


def _make_result(document_id="doc1", chunk_count=3):
    result = MagicMock()
    result.document_id = document_id
    result.document_graph.chunks = {
        f"c{i}": _make_chunk(f"c{i}") for i in range(chunk_count)
    }
    return result


def test_write_creates_json_file_with_expected_fields(tmp_path) -> None:
    writer = ChunkingReportWriter(output_dir=tmp_path)
    path = writer.write(_make_result(chunk_count=3))

    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["total_chunks"] == 3
    assert "type_distribution" in data


def test_write_filename_contains_document_id(tmp_path) -> None:
    writer = ChunkingReportWriter(output_dir=tmp_path)
    path = writer.write(_make_result(document_id="docXYZ"))

    assert "docXYZ" in path.name


def test_write_creates_output_directory(tmp_path) -> None:
    nested = tmp_path / "a" / "b"
    writer = ChunkingReportWriter(output_dir=nested)
    writer.write(_make_result())

    assert nested.exists()
