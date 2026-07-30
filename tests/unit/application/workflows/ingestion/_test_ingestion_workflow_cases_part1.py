from tests.unit.application.workflows.ingestion._test_ingestion_workflow_support import *  # noqa: F401,F403


def test_ingestion_workflow_warns_on_low_parse_confidence(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
    monkeypatch,
) -> None:
    from src.config.settings import ingestion_settings

    monkeypatch.setattr(ingestion_settings, "low_confidence_parse_threshold", 0.5)
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nmanual")
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        parsing_workflow=FakeParsingWorkflow(
            sample_document_graph,
            parse_confidence=0.1,
        ),
    )

    result = workflow.run(
        IngestionRequest(
            file_path=str(input_file),
            document_type=DocumentType.MANUAL.value,
            run_quality_checks=False,
            requested_by="user_001",
        )
    )

    assert any("Low parse confidence" in warning for warning in result.warnings)

def test_ingestion_workflow_persists_run_and_emits_stage_events(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nmanual")
    event_service = FakeEventService()
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        event_service=event_service,
    )

    result = workflow.run(
        IngestionRequest(
            file_path=str(input_file),
            document_type=DocumentType.MANUAL.value,
            generate_questions=True,
            run_quality_checks=False,
            requested_by="user_001",
        )
    )

    assert result.status == IngestionStatus.COMPLETE
    assert result.document_id == sample_document_graph.document.document_id
    assert result.vector_count == 1
    assert result.generated_question_count == len(sample_document_graph.questions)
    assert result.current_stage == IngestionStage.COMPLETE
    assert "parser warning" in result.warnings

    stored_statuses = [
        workflow.unit_of_work.ingestion_runs.created[0].status,
        *[run.status for run in workflow.unit_of_work.ingestion_runs.updated],
    ]
    assert stored_statuses == [
        IngestionStatus.PENDING,
        IngestionStatus.PARSING,
        IngestionStatus.REGISTERED,
        IngestionStatus.CLASSIFIED,
        IngestionStatus.FINALIZED,
        IngestionStatus.EXTRACTED,
        IngestionStatus.EMBEDDED,
        IngestionStatus.INDEXED,
        IngestionStatus.COMPLETE,
    ]

    assert [
        event.event_type for event in event_service.events
    ] == [
        "ingestion.started",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.completed",
    ]
    assert workflow.post_classification_chunk_finalization_workflow.calls == [
        {
            "document_id": sample_document_graph.document.document_id,
            "embed_final_chunks": False,
            "enable_question_generation": True,
        }
    ]

def test_ingestion_workflow_forwards_enable_ocr_to_parsing_workflow(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nmanual")
    parsing_workflow = FakeParsingWorkflow(sample_document_graph)
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        parsing_workflow=parsing_workflow,
    )

    workflow.run(
        IngestionRequest(
            file_path=str(input_file),
            enable_ocr=True,
            run_quality_checks=False,
        )
    )

    assert parsing_workflow.calls[0]["enable_ocr_override"] is True

def test_ingestion_workflow_defaults_enable_ocr_override_to_none(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nmanual")
    parsing_workflow = FakeParsingWorkflow(sample_document_graph)
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        parsing_workflow=parsing_workflow,
    )

    workflow.run(
        IngestionRequest(
            file_path=str(input_file),
            run_quality_checks=False,
        )
    )

    assert parsing_workflow.calls[0]["enable_ocr_override"] is None

def test_ingestion_workflow_skips_duplicate_documents(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nduplicate")
    duplicate_service = FakeDuplicateDetectionService(
        file_duplicate_document_id="doc_existing"
    )
    event_service = FakeEventService()
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        duplicate_service=duplicate_service,
        event_service=event_service,
    )

    result = workflow.run(
        IngestionRequest(
            file_path=str(input_file),
            run_quality_checks=False,
        )
    )

    assert result.status == IngestionStatus.SKIPPED_FILE_DUPLICATE
    assert result.duplicate_of_document_id == "doc_existing"
    assert workflow.parsing_workflow.calls == []
    assert workflow.unit_of_work.ingestion_runs.updated[-1].status == (
        IngestionStatus.SKIPPED_FILE_DUPLICATE
    )
    assert event_service.events[-1].event_type == "ingestion.skipped_duplicate"

def test_ingestion_workflow_marks_run_failed_and_emits_failed_event(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nbroken")
    event_service = FakeEventService()
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        parsing_workflow=FailingParsingWorkflow(),
        event_service=event_service,
    )

    with pytest.raises(DocumentParsingError):
        workflow.run(
            IngestionRequest(
                file_path=str(input_file),
                run_quality_checks=False,
            )
        )

    assert workflow.unit_of_work.rollback_count == 1
    assert workflow.unit_of_work.ingestion_runs.updated[-1].status == (
        IngestionStatus.FAILED
    )
    failed_event = event_service.events[-1]
    assert failed_event.event_type == "ingestion.failed"
    assert failed_event.stage == IngestionStage.PARSING.value

def test_reingestion_raises_when_document_lookup_service_not_wired(
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
    )

    with pytest.raises(ReingestionNotSupportedError):
        workflow.reingest(ReingestionRequest(document_id="doc_001"))

def test_reingest_raises_when_document_does_not_exist(
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        document_lookup_service=FakeDocumentLookupService(graph=None),
    )

    with pytest.raises(DocumentNotFoundForReingestionError):
        workflow.reingest(ReingestionRequest(document_id="doc_missing"))
