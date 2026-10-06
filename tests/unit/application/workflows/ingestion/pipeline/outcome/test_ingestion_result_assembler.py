from types import SimpleNamespace

from src.application.workflows.ingestion.models.ingestion_request import IngestionRequest
from src.application.workflows.ingestion.models.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.models.ingestion_status import IngestionStatus
from src.application.workflows.ingestion.pipeline.outcome.ingestion_result_assembler import (
    build_success_result,
)
from src.domain.extraction import ExtractionResult
from src.domain.workflow import IngestionRun


def _make_final_graph() -> SimpleNamespace:
    document = SimpleNamespace(
        document_id="doc_1",
        file_path="/tmp/doc.pdf",
        title="Sample Manual",
        document_type=SimpleNamespace(value="manual"),
        hashes=SimpleNamespace(file_hash="hash_1", content_hash="content_hash_1"),
        statistics=SimpleNamespace(
            page_count=10,
            section_count=5,
            element_count=20,
            chunk_count=8,
            table_count=1,
            picture_count=0,
            identifier_count=2,
        ),
    )
    return SimpleNamespace(document=document, questions=[])


def _make_request() -> IngestionRequest:
    return IngestionRequest(file_path="/tmp/doc.pdf")


def _make_extraction_result(*, attempted_chunk_ids, unresolved_chunk_ids) -> ExtractionResult:
    return ExtractionResult(
        extraction_id="extraction_1",
        document_id="doc_1",
        attempted_chunk_ids=attempted_chunk_ids,
        unresolved_chunk_ids=unresolved_chunk_ids,
    )


def _build(*, extraction_result) -> "object":
    return build_success_result(
        request=_make_request(),
        ingestion_run=IngestionRun(run_id="run_1", document_id="doc_1"),
        final_graph=_make_final_graph(),
        embedded_chunks=[],
        file_name="doc.pdf",
        warnings=[],
        correlation_id="corr_1",
        quality_diagnostics={},
        extraction_result=extraction_result,
        extraction_skipped=False,
        runtime_diagnostics={},
    )


def test_complete_extraction_surfaces_completeness_status_without_a_warning() -> None:
    extraction_result = _make_extraction_result(
        attempted_chunk_ids=["chunk_1", "chunk_2"],
        unresolved_chunk_ids=[],
    )

    result = _build(extraction_result=extraction_result)

    assert result.status is IngestionStatus.COMPLETE
    assert result.current_stage is IngestionStage.COMPLETE
    assert result.diagnostics["extraction_completeness_status"] == "complete"
    assert result.warnings == []


def test_partial_extraction_adds_a_warning_and_surfaces_completeness_status() -> None:
    extraction_result = _make_extraction_result(
        attempted_chunk_ids=["chunk_1", "chunk_2"],
        unresolved_chunk_ids=["chunk_2"],
    )

    result = _build(extraction_result=extraction_result)

    # Overall ingestion still completed (parsing/classification/indexing did
    # finish) - extraction completeness is a narrower, separate signal.
    assert result.status is IngestionStatus.COMPLETE
    assert result.diagnostics["extraction_completeness_status"] == "partial"
    assert result.diagnostics["extraction_unresolved_chunk_count"] == 1
    assert len(result.warnings) == 1
    assert "partial" in result.warnings[0]
    assert "chunk_2" in result.warnings[0]


def test_failed_extraction_adds_a_warning_and_surfaces_completeness_status() -> None:
    extraction_result = _make_extraction_result(
        attempted_chunk_ids=["chunk_1"],
        unresolved_chunk_ids=["chunk_1"],
    )

    result = _build(extraction_result=extraction_result)

    assert result.diagnostics["extraction_completeness_status"] == "failed"
    assert len(result.warnings) == 1
    assert "failed" in result.warnings[0]


def test_caller_supplied_warnings_are_preserved_alongside_the_new_one() -> None:
    extraction_result = _make_extraction_result(
        attempted_chunk_ids=["chunk_1", "chunk_2"],
        unresolved_chunk_ids=["chunk_2"],
    )

    result = build_success_result(
        request=_make_request(),
        ingestion_run=IngestionRun(run_id="run_1", document_id="doc_1"),
        final_graph=_make_final_graph(),
        embedded_chunks=[],
        file_name="doc.pdf",
        warnings=["some earlier warning"],
        correlation_id="corr_1",
        quality_diagnostics={},
        extraction_result=extraction_result,
        extraction_skipped=False,
        runtime_diagnostics={},
    )

    assert result.warnings[0] == "some earlier warning"
    assert len(result.warnings) == 2


def test_no_extraction_result_means_no_completeness_diagnostics_or_warning() -> None:
    result = _build(extraction_result=None)

    assert "extraction_completeness_status" not in result.diagnostics
    assert result.warnings == []
