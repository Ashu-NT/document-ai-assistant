from tests.unit.application.workflows.classification._test_post_classification_chunk_finalization_workflow_support import *  # noqa: F401,F403

def test_post_classification_finalization_reuses_chunks_and_runs_questions_and_embeddings_once(
    sample_document_graph,
    sample_document_classification,
    sample_chunk,
) -> None:
    graph = copy.deepcopy(sample_document_graph)
    overview_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_overview",
        content="Overview content.",
        chunk_type=ChunkType.OVERVIEW,
    )
    detail_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_detail",
        content="Detail content.",
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
    )
    graph.replace_chunks([overview_chunk, detail_chunk])
    decision = DocumentTypeDecision(
        effective_document_type=DocumentType.MANUAL,
        effective_chunking_profile=ChunkingProfile.MANUAL,
        confidence=0.9,
        reasons=["reused provisional chunks"],
        should_rechunk=False,
    )
    (
        workflow,
        question_service,
        registration_service,
        vector_store,
        embedding_workflow,
        graph_chunk_builder,
        operations,
    ) = make_workflow(
        graph=graph,
        classification=sample_document_classification,
        decision=decision,
        rechunked_chunks=[overview_chunk, detail_chunk],
        provisional_profile=ChunkingProfile.MANUAL,
        enable_question_generation=True,
    )

    result = workflow.finalize(graph.document.document_id)

    assert list(result.chunks) == ["chunk_overview", "chunk_detail"]
    assert question_service.calls == [["chunk_detail"]]
    assert registration_service.replace_calls[0].questions
    assert vector_store.delete_calls == [graph.document.document_id]
    assert embedding_workflow.calls == [["chunk_overview", "chunk_detail"]]
    assert len(graph_chunk_builder.calls) == 1
    assert operations == ["delete_vectors", "replace", "embed"]


def test_post_classification_finalization_uses_configured_question_limit(
    sample_document_graph,
    sample_document_classification,
    sample_chunk,
    monkeypatch,
) -> None:
    from src.config.settings import ingestion_settings

    graph = copy.deepcopy(sample_document_graph)
    detail_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_detail",
        content="Detail content.",
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
    )
    graph.replace_chunks([detail_chunk])
    decision = DocumentTypeDecision(
        effective_document_type=DocumentType.MANUAL,
        effective_chunking_profile=ChunkingProfile.MANUAL,
        confidence=0.9,
        reasons=["reused provisional chunks"],
        should_rechunk=False,
    )
    workflow, question_service, *_ = make_workflow(
        graph=graph,
        classification=sample_document_classification,
        decision=decision,
        rechunked_chunks=[detail_chunk],
        provisional_profile=ChunkingProfile.MANUAL,
        enable_question_generation=True,
    )
    monkeypatch.setattr(
        ingestion_settings,
        "max_generated_questions_per_chunk",
        7,
    )

    workflow.finalize(graph.document.document_id)

    assert question_service.max_questions_per_chunk_calls == [7]

def test_post_classification_finalization_rechunks_before_questions_and_embeddings(
    sample_document_graph,
    sample_document_classification,
    sample_chunk,
) -> None:
    graph = copy.deepcopy(sample_document_graph)
    provisional_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_provisional",
        content="Provisional content.",
        chunk_type=ChunkType.GENERAL,
    )
    graph.replace_chunks([provisional_chunk])
    final_overview_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_final_overview",
        content="Final overview content.",
        chunk_type=ChunkType.OVERVIEW,
    )
    final_detail_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_final_detail",
        content="Final detail content.",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
    )
    decision = DocumentTypeDecision(
        effective_document_type=DocumentType.DATASHEET,
        effective_chunking_profile=ChunkingProfile.DATASHEET,
        confidence=0.88,
        reasons=["rechunk required"],
        should_rechunk=True,
    )
    (
        workflow,
        question_service,
        registration_service,
        vector_store,
        embedding_workflow,
        graph_chunk_builder,
        operations,
    ) = make_workflow(
        graph=graph,
        classification=sample_document_classification,
        decision=decision,
        rechunked_chunks=[final_overview_chunk, final_detail_chunk],
        provisional_profile=ChunkingProfile.MANUAL,
        enable_question_generation=True,
    )

    result = workflow.finalize(graph.document.document_id)

    assert list(result.chunks) == ["chunk_final_overview", "chunk_final_detail"]
    assert question_service.calls == [["chunk_final_detail"]]
    assert embedding_workflow.calls == [["chunk_final_overview", "chunk_final_detail"]]
    assert list(registration_service.replace_calls[0].chunks) == [
        "chunk_final_overview",
        "chunk_final_detail",
    ]
    assert vector_store.delete_calls == [graph.document.document_id]
    assert len(graph_chunk_builder.calls) == 1
    assert operations == ["delete_vectors", "replace", "embed"]

def test_post_classification_finalization_refreshes_stale_chunk_set_when_builder_output_changes(
    sample_document_graph,
    sample_document_classification,
    sample_chunk,
) -> None:
    graph = copy.deepcopy(sample_document_graph)
    stored_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_stored",
        content="Old combined content.",
        chunk_type=ChunkType.GENERAL,
    )
    graph.replace_chunks([stored_chunk])
    refreshed_chunk_a = clone_chunk(
        sample_chunk,
        chunk_id="chunk_refreshed_a",
        content="Refreshed content A.",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
    )
    refreshed_chunk_b = clone_chunk(
        sample_chunk,
        chunk_id="chunk_refreshed_b",
        content="Refreshed content B.",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
    )
    decision = DocumentTypeDecision(
        effective_document_type=DocumentType.MANUAL,
        effective_chunking_profile=ChunkingProfile.MANUAL,
        confidence=0.9,
        reasons=["stored chunk set is stale"],
        should_rechunk=False,
    )
    (
        workflow,
        question_service,
        _,
        _,
        embedding_workflow,
        graph_chunk_builder,
        _,
    ) = make_workflow(
        graph=graph,
        classification=sample_document_classification,
        decision=decision,
        rechunked_chunks=[refreshed_chunk_a, refreshed_chunk_b],
        provisional_profile=ChunkingProfile.MANUAL,
        enable_question_generation=True,
    )

    result = workflow.finalize(graph.document.document_id)

    assert list(result.chunks) == ["chunk_refreshed_a", "chunk_refreshed_b"]
    assert question_service.calls == [["chunk_refreshed_a", "chunk_refreshed_b"]]
    assert embedding_workflow.calls == [["chunk_refreshed_a", "chunk_refreshed_b"]]
    assert len(graph_chunk_builder.calls) == 1

def test_post_classification_finalization_rebuilds_when_stored_chunk_set_is_empty(
    sample_document_graph,
    sample_document_classification,
    sample_chunk,
) -> None:
    graph = copy.deepcopy(sample_document_graph)
    graph.replace_chunks([])
    rebuilt_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_rebuilt",
        content="Rebuilt content.",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
    )
    decision = DocumentTypeDecision(
        effective_document_type=DocumentType.MANUAL,
        effective_chunking_profile=ChunkingProfile.MANUAL,
        confidence=0.9,
        reasons=["stored chunk set missing"],
        should_rechunk=False,
    )
    workflow, _, _, _, embedding_workflow, graph_chunk_builder, _ = make_workflow(
        graph=graph,
        classification=sample_document_classification,
        decision=decision,
        rechunked_chunks=[rebuilt_chunk],
        provisional_profile=ChunkingProfile.MANUAL,
        enable_question_generation=False,
    )

    result = workflow.finalize(graph.document.document_id)

    assert list(result.chunks) == ["chunk_rebuilt"]
    assert embedding_workflow.calls == [["chunk_rebuilt"]]
    assert len(graph_chunk_builder.calls) == 1

def test_post_classification_finalization_emits_nested_progress_messages(
    sample_document_graph,
    sample_document_classification,
    sample_chunk,
) -> None:
    graph = copy.deepcopy(sample_document_graph)
    detail_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_detail",
        content="Detail content.",
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
    )
    graph.replace_chunks([detail_chunk])
    decision = DocumentTypeDecision(
        effective_document_type=DocumentType.MANUAL,
        effective_chunking_profile=ChunkingProfile.MANUAL,
        confidence=0.9,
        reasons=["reused provisional chunks"],
        should_rechunk=False,
    )
    workflow, _, _, _, _, _, _ = make_workflow(
        graph=graph,
        classification=sample_document_classification,
        decision=decision,
        rechunked_chunks=[detail_chunk],
        provisional_profile=ChunkingProfile.MANUAL,
        enable_question_generation=True,
    )
    messages: list[str] = []

    workflow.finalize(
        graph.document.document_id,
        progress_callback=messages.append,
    )

    assert messages[0] == f"Loading persisted document graph for {graph.document.document_id}..."
    assert any("Chunking decision resolved" in message for message in messages)
    assert any("Generating questions for 1 chunk(s)..." in message for message in messages)
    assert any("question generation called for 1 chunk(s)" in message for message in messages)
    assert any("Deleting existing vectors for this document..." in message for message in messages)
    assert any("embedding called for 1 chunk(s)" in message for message in messages)
    assert messages[-1] == "Post-classification chunk finalization completed."
