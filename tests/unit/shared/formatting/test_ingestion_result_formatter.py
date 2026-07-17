from src.application.workflows.ingestion import IngestionResult, IngestionStatus
from src.shared.formatting.ingestion_result_formatter import (
    build_ingestion_json_payload,
    print_ingestion_result,
)


def test_build_ingestion_json_payload_includes_runtime_profiles() -> None:
    result = IngestionResult(
        status=IngestionStatus.COMPLETE,
        document_id="doc_001",
        diagnostics={
            "ingestion_runtime_profile": "structural_only",
            "requested_runtime_profile": "auto",
        },
    )

    payload = build_ingestion_json_payload(result)

    assert payload["runtime_profile"] == "structural_only"
    assert payload["requested_runtime_profile"] == "auto"


def test_print_ingestion_result_shows_runtime_profile(capsys) -> None:
    result = IngestionResult(
        status=IngestionStatus.COMPLETE,
        diagnostics={
            "ingestion_runtime_profile": "semantic_enriched",
            "extraction_skipped": False,
        },
    )

    print_ingestion_result(result)

    output = capsys.readouterr().out
    assert "Runtime Profile  : semantic_enriched" in output
    assert "Extraction       : enabled" in output
