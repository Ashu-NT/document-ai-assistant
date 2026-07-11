from tests.unit.application.workflows.ingestion._test_ingestion_workflow_support import *  # noqa: F401,F403

def test_reingest_replaces_extraction_and_deletes_stale_vectors_for_existing_document(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nmanual")
    existing_graph = copy.deepcopy(sample_document_graph)
    existing_graph.document.file_path = str(input_file)
    document_id = existing_graph.document.document_id

    document_lookup_service = FakeDocumentLookupService(existing_graph)
    document_registration_service = FakeDocumentRegistrationService()
    extraction_workflow = FakeExtractionWorkflow(sample_extraction_result)
    embedding_workflow = FakeEmbeddingWorkflow()
    parsing_workflow = FakeParsingWorkflow(sample_document_graph)

    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        parsing_workflow=parsing_workflow,
        document_registration_service=document_registration_service,
        extraction_workflow=extraction_workflow,
        embedding_workflow=embedding_workflow,
        document_lookup_service=document_lookup_service,
    )

    result = workflow.reingest(
        ReingestionRequest(document_id=document_id, run_quality_checks=False)
    )

    assert result.status == IngestionStatus.COMPLETE
    assert result.document_id == document_id
    assert document_lookup_service.calls == [document_id]

    # Parsing must be told to reuse the existing document identity.
    assert parsing_workflow.calls[0]["document_id"] == document_id
    assert parsing_workflow.calls[0]["file_path"] == str(input_file)

    # Registration must use the delete-then-merge replace path, not a plain
    # additive merge, so stale sections/elements/chunks cannot survive.
    assert document_registration_service.calls == []
    assert len(document_registration_service.replace_calls) == 1

    # Extraction must replace prior rows atomically instead of appending.
    assert extraction_workflow.calls[0]["replace_existing"] is True

    # Stale vectors must be deleted before the new ones are stored.
    assert embedding_workflow.delete_calls == [document_id]
    assert embedding_workflow.store_calls

def test_run_uses_additive_registration_and_save_when_not_reingesting(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nmanual")
    document_registration_service = FakeDocumentRegistrationService()
    extraction_workflow = FakeExtractionWorkflow(sample_extraction_result)
    embedding_workflow = FakeEmbeddingWorkflow()
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        document_registration_service=document_registration_service,
        extraction_workflow=extraction_workflow,
        embedding_workflow=embedding_workflow,
    )

    workflow.run(
        IngestionRequest(file_path=str(input_file), run_quality_checks=False)
    )

    assert len(document_registration_service.calls) == 1
    assert document_registration_service.replace_calls == []
    assert extraction_workflow.calls[0]["replace_existing"] is False
    assert extraction_workflow.calls[0]["sections"] == sample_document_graph.sections
    assert embedding_workflow.delete_calls == []

def test_retry_extraction_raises_when_document_lookup_service_not_wired(
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
        workflow.retry_extraction("doc_001")

def test_retry_extraction_raises_when_document_does_not_exist(
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
        workflow.retry_extraction("doc_missing")

def test_retry_extraction_reextracts_in_place_without_reparsing(
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    document_id = sample_document_graph.document.document_id
    extraction_workflow = FakeExtractionWorkflow(sample_extraction_result)
    document_registration_service = FakeDocumentRegistrationService()
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        extraction_workflow=extraction_workflow,
        document_registration_service=document_registration_service,
        document_lookup_service=FakeDocumentLookupService(sample_document_graph),
    )

    result = workflow.retry_extraction(document_id)

    assert result.status == IngestionStatus.EXTRACTED
    assert result.document_id == document_id
    assert len(extraction_workflow.calls) == 1
    assert extraction_workflow.calls[0]["document_id"] == document_id
    assert extraction_workflow.calls[0]["replace_existing"] is True
    # Retrying extraction must never re-parse or re-register the document.
    assert document_registration_service.calls == []
    assert document_registration_service.replace_calls == []
    assert workflow.unit_of_work.commit_count >= 1

def test_retry_extraction_forwards_progress_callback_and_emits_stage_messages(
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    document_id = sample_document_graph.document.document_id
    extraction_workflow = FakeExtractionWorkflow(sample_extraction_result)
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        extraction_workflow=extraction_workflow,
        document_lookup_service=FakeDocumentLookupService(sample_document_graph),
    )
    messages: list[str] = []

    workflow.retry_extraction(document_id, progress_callback=messages.append)

    assert extraction_workflow.calls[0]["progress_callback"] is not None
    assert messages == [
        "Extraction started.",
        "Extraction completed.",
    ]

def test_retry_extraction_invokes_semantic_linking_workflow(
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    document_id = sample_document_graph.document.document_id
    semantic_linking_workflow = FakeSemanticLinkingWorkflow(relationships=["r1", "r2"])
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        document_lookup_service=FakeDocumentLookupService(sample_document_graph),
        semantic_linking_workflow=semantic_linking_workflow,
    )

    result = workflow.retry_extraction(document_id)

    assert semantic_linking_workflow.calls == [document_id]
    assert result.diagnostics["semantic_relationship_count"] == 2

def test_retry_extraction_recovers_missing_chunks_by_rerunning_finalization(
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
    sample_chunk,
) -> None:
    chunkless_graph = copy.deepcopy(sample_document_graph)
    chunkless_graph.replace_chunks([])
    recovered_graph = copy.deepcopy(sample_document_graph)
    recovered_chunk = sample_chunk.__class__(
        chunk_id="chunk_recovered",
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content="Recovered chunk content.",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
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
    recovered_graph.replace_chunks([recovered_chunk])
    extraction_workflow = FakeExtractionWorkflow(sample_extraction_result)
    finalization_workflow = FakePostClassificationChunkFinalizationWorkflow(
        recovered_graph
    )
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        extraction_workflow=extraction_workflow,
        document_lookup_service=FakeDocumentLookupService(chunkless_graph),
        post_classification_chunk_finalization_workflow=finalization_workflow,
    )
    messages: list[str] = []

    result = workflow.retry_extraction(
        chunkless_graph.document.document_id,
        progress_callback=messages.append,
    )

    assert result.status == IngestionStatus.EXTRACTED
    assert finalization_workflow.calls == [
        {
            "document_id": chunkless_graph.document.document_id,
            "embed_final_chunks": False,
            "enable_question_generation": None,
        }
    ]
    assert extraction_workflow.calls[0]["chunks"] == [recovered_chunk]
    assert any(
        "Rebuilding final chunk set in place before retrying extraction"
        in message
        for message in messages
    )
