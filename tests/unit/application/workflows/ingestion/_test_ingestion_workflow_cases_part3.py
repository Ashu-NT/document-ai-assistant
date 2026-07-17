from tests.unit.application.workflows.ingestion._test_ingestion_workflow_support import *  # noqa: F401,F403

def test_retry_extraction_retries_only_saved_unresolved_chunks(
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
    sample_chunk,
) -> None:
    second_chunk = sample_chunk.__class__(
        chunk_id="chunk_002",
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content="Previously unresolved chunk content.",
        chunk_type=sample_chunk.chunk_type,
        section_path=list(sample_chunk.section_path),
        element_ids=list(sample_chunk.element_ids),
        table_ids=list(sample_chunk.table_ids),
        picture_ids=list(sample_chunk.picture_ids),
        source=sample_chunk.source,
        sequence_number=sample_chunk.sequence_number,
        chunk_index=sample_chunk.chunk_index,
        chunk_total=sample_chunk.chunk_total,
        embedding_text=sample_chunk.embedding_text,
    )
    graph_with_two_chunks = copy.deepcopy(sample_document_graph)
    graph_with_two_chunks.replace_chunks([sample_chunk, second_chunk])
    prior_result = copy.deepcopy(sample_extraction_result)
    prior_result.unresolved_chunk_ids = ["chunk_002"]
    prior_result.attempted_chunk_ids = ["chunk_001", "chunk_002"]
    prior_result.source_chunk_ids = ["chunk_001"]
    extraction_service = SimpleNamespace(
        get_document_extraction_result=lambda document_id: prior_result
    )
    extraction_workflow = FakeExtractionWorkflow(
        sample_extraction_result,
        extraction_service=extraction_service,
    )
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        extraction_workflow=extraction_workflow,
        document_lookup_service=FakeDocumentLookupService(graph_with_two_chunks),
    )

    result = workflow.retry_extraction(graph_with_two_chunks.document.document_id)

    assert result.status == IngestionStatus.EXTRACTED
    assert extraction_workflow.calls[0]["chunks"] == [second_chunk]
    assert extraction_workflow.calls[0]["base_result"] == prior_result

def test_ingestion_workflow_skips_semantic_linking_when_not_configured(
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
        IngestionRequest(file_path=str(input_file), run_quality_checks=False)
    )

    assert result.status == IngestionStatus.COMPLETE
    extraction_completed = next(
        event
        for event in event_service.events
        if event.event_type == "ingestion.stage.completed"
        and event.stage == IngestionStage.EXTRACTION.value
    )
    assert extraction_completed.payload["semantic_relationship_count"] is None

def test_ingestion_workflow_invokes_semantic_linking_after_extraction_is_saved(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nmanual")
    extraction_workflow = FakeExtractionWorkflow(sample_extraction_result)
    semantic_linking_workflow = FakeSemanticLinkingWorkflow(relationships=["r1", "r2"])
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        extraction_workflow=extraction_workflow,
        semantic_linking_workflow=semantic_linking_workflow,
    )

    result = workflow.run(
        IngestionRequest(file_path=str(input_file), run_quality_checks=False)
    )

    # Linking must reload by document_id after extraction has been saved,
    # not run against the in-memory extraction result.
    assert semantic_linking_workflow.calls == [result.document_id]
    assert extraction_workflow.calls[0]["document_id"] == result.document_id

def test_ingestion_workflow_reports_semantic_relationship_count_on_extraction_stage(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nmanual")
    event_service = FakeEventService()
    semantic_linking_workflow = FakeSemanticLinkingWorkflow(relationships=["r1", "r2", "r3"])
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        event_service=event_service,
        semantic_linking_workflow=semantic_linking_workflow,
    )

    workflow.run(
        IngestionRequest(file_path=str(input_file), run_quality_checks=False)
    )

    extraction_completed = next(
        event
        for event in event_service.events
        if event.event_type == "ingestion.stage.completed"
        and event.stage == IngestionStage.EXTRACTION.value
    )
    assert extraction_completed.payload["semantic_relationship_count"] == 3

def test_ingestion_workflow_persists_extraction_model_before_extraction_failure(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nextract-failure")
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        extraction_workflow=FailingExtractionWorkflow(),
    )

    with pytest.raises(Exception):
        workflow.run(
            IngestionRequest(
                file_path=str(input_file),
                run_quality_checks=False,
            )
        )

    assert any(
        run.extraction_model == "extract-test"
        for run in workflow.unit_of_work.ingestion_runs.updated
    )
    assert workflow.unit_of_work.ingestion_runs.updated[-1].status == IngestionStatus.FAILED

def test_ingestion_workflow_rejects_zero_final_chunks_before_extraction_and_embedding(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nmanual")
    empty_final_graph = copy.deepcopy(sample_document_graph)
    empty_final_graph.replace_chunks([])
    event_service = FakeEventService()
    extraction_workflow = FakeExtractionWorkflow(sample_extraction_result)
    embedding_workflow = FakeEmbeddingWorkflow()
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        event_service=event_service,
        extraction_workflow=extraction_workflow,
        embedding_workflow=embedding_workflow,
        post_classification_chunk_finalization_workflow=(
            FakePostClassificationChunkFinalizationWorkflow(empty_final_graph)
        ),
    )

    with pytest.raises(Exception) as exc_info:
        workflow.run(
            IngestionRequest(
                file_path=str(input_file),
                run_quality_checks=False,
            )
        )

    assert "contains no chunks" in str(exc_info.value)
    assert extraction_workflow.calls == []
    assert embedding_workflow.embed_calls == []
    assert embedding_workflow.store_calls == []
    assert not any(
        event.event_type == "ingestion.stage.completed"
        and event.stage == IngestionStage.FINALIZATION.value
        for event in event_service.events
    )
