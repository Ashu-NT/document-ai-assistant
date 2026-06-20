import json
from pathlib import Path

import pytest

from src.application.evaluation import (
    RetrievalBenchmarkCorpusManifest,
    RetrievalBenchmarkCorpusManifestLoader,
)
from src.shared.exceptions import SchemaValidationError


def test_manifest_loader_reads_manifest_json(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "truth_set_path": "TestDoc/retrieval_truth_set.md",
                "input_directory": "TestDoc",
                "generated_at": "2026-06-20T00:00:00+00:00",
                "document_count": 1,
                "documents": [
                    {
                        "document_alias": "manual_fwc12",
                        "document_id": "doc_manual",
                        "file_name": "manual.pdf",
                        "file_path": "TestDoc/manual.pdf",
                        "file_hash": "file_hash",
                        "content_hash": "content_hash",
                        "document_type": "manual",
                        "page_count": 10,
                        "section_count": 4,
                        "element_count": 12,
                        "chunk_count": 8,
                        "question_count": 7,
                        "classification_label": "manual",
                        "classification_confidence": 0.93,
                        "embedding_model": "BAAI/bge-small-en-v1.5",
                        "vector_collection": "documents",
                        "seed_status": "seeded_new",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    manifest = RetrievalBenchmarkCorpusManifestLoader().load(manifest_path)

    assert isinstance(manifest, RetrievalBenchmarkCorpusManifest)
    assert manifest.document_count == 1
    assert manifest.documents[0].document_alias == "manual_fwc12"
    assert manifest.documents[0].file_path == Path("TestDoc/manual.pdf")


def test_manifest_loader_fails_fast_for_missing_required_fields(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "truth_set_path": "TestDoc/retrieval_truth_set.md",
                "documents": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(SchemaValidationError) as exc_info:
        RetrievalBenchmarkCorpusManifestLoader().load(manifest_path)

    assert exc_info.value.details is not None
    assert exc_info.value.details["missing_fields"] == [
        "input_directory",
        "generated_at",
    ]
