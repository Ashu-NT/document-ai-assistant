from src.application.workflows.ingestion.pipeline.stage_lifecycle.ingestion_stage_payload_builder import (
    IngestionStagePayloadBuilder,
)
from src.domain.extraction import ExtractionResult


def _make_extraction_result(*, attempted_chunk_ids, unresolved_chunk_ids) -> ExtractionResult:
    return ExtractionResult(
        extraction_id="extraction_1",
        document_id="doc_1",
        attempted_chunk_ids=attempted_chunk_ids,
        unresolved_chunk_ids=unresolved_chunk_ids,
    )


class _FakeExtractionStageResult:
    deterministic_identifier_count = 0
    semantic_relationship_count = 0


def test_extraction_completed_reports_complete_status() -> None:
    extraction_result = _make_extraction_result(
        attempted_chunk_ids=["chunk_1"], unresolved_chunk_ids=[]
    )

    payload = IngestionStagePayloadBuilder.extraction_completed(
        extraction_result=extraction_result,
        extraction_stage_result=_FakeExtractionStageResult(),
        extraction_enabled=True,
        runtime_diagnostics={},
    )

    assert payload["completeness_status"] == "complete"
    assert payload["unresolved_chunk_count"] == 0


def test_extraction_completed_reports_partial_status() -> None:
    extraction_result = _make_extraction_result(
        attempted_chunk_ids=["chunk_1", "chunk_2"], unresolved_chunk_ids=["chunk_2"]
    )

    payload = IngestionStagePayloadBuilder.extraction_completed(
        extraction_result=extraction_result,
        extraction_stage_result=_FakeExtractionStageResult(),
        extraction_enabled=True,
        runtime_diagnostics={},
    )

    assert payload["completeness_status"] == "partial"
    assert payload["unresolved_chunk_count"] == 1


def test_extraction_completed_reports_none_status_when_extraction_result_is_none() -> None:
    payload = IngestionStagePayloadBuilder.extraction_completed(
        extraction_result=None,
        extraction_stage_result=_FakeExtractionStageResult(),
        extraction_enabled=False,
        runtime_diagnostics={},
    )

    assert payload["completeness_status"] is None
    assert payload["unresolved_chunk_count"] == 0
