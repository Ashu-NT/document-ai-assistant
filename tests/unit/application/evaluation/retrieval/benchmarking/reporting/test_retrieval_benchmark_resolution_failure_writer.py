import json

from src.application.evaluation import (
    RetrievalBenchmarkResolutionFailureWriter,
)


def test_resolution_failure_writer_writes_json_and_markdown_outputs(tmp_path) -> None:
    writer = RetrievalBenchmarkResolutionFailureWriter()
    json_path = tmp_path / "reports" / "retrieval_report.json"
    markdown_path = tmp_path / "reports" / "retrieval_report.md"
    details = {
        "unresolved_case_ids": ["M-002", "D-001"],
        "diagnostics": [
            {
                "case_id": "M-002",
                "document_alias": "manual_fwc12",
                "file_name": "manual.pdf",
                "message": "No final chunk matched the expected section/page/passage signals.",
                "details": {
                    "expected_page": 1,
                    "expected_section_path": "Title / Cover",
                },
                "candidate_summaries": [
                    {
                        "chunk_id": "chunk_001",
                        "score": 3.333,
                        "passage_overlap": 0.333,
                        "page_start": 45,
                        "page_end": 45,
                        "section_path_text": "7 Components > Spare Parts",
                        "content_preview": "Always state machine serial number.",
                    }
                ],
            }
        ],
    }

    written_json_path = writer.write_json(
        details=details,
        output_path=json_path,
        subset="full",
        truth_set_path="TestDoc/retrieval_truth_set.md",
        manifest_path="outputs/evaluation/retrieval/benchmark_corpus_manifest.json",
    )
    written_markdown_path = writer.write_markdown(
        details=details,
        output_path=markdown_path,
        subset="full",
        truth_set_path="TestDoc/retrieval_truth_set.md",
        manifest_path="outputs/evaluation/retrieval/benchmark_corpus_manifest.json",
    )

    json_payload = json.loads(written_json_path.read_text(encoding="utf-8"))
    markdown = written_markdown_path.read_text(encoding="utf-8")

    assert written_json_path == json_path
    assert written_markdown_path == markdown_path
    assert json_payload["status"] == "resolution_failed"
    assert json_payload["unresolved_case_ids"] == ["M-002", "D-001"]
    assert "Retrieval Benchmark Resolution Failure" in markdown
    assert "`M-002`" in markdown
