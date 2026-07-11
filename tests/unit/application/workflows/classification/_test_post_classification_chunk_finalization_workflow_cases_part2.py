from tests.unit.application.workflows.classification._test_post_classification_chunk_finalization_workflow_support import *  # noqa: F401,F403

def test_post_classification_finalization_skips_question_generation_when_disabled(
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
    (
        workflow,
        question_service,
        _,
        registration_service,
        _,
        embedding_workflow,
        _,
        _,
    ) = make_workflow(
        graph=graph,
        classification=sample_document_classification,
        decision=decision,
        rechunked_chunks=[detail_chunk],
        provisional_profile=ChunkingProfile.MANUAL,
        enable_question_generation=False,
    )
    messages: list[str] = []

    result = workflow.finalize(
        graph.document.document_id,
        progress_callback=messages.append,
    )

    assert question_service.calls == []
    assert result.questions == {}
    assert registration_service.replace_calls[0].questions == {}
    assert embedding_workflow.calls == [["chunk_detail"]]
    assert any(
        "Question generation disabled; skipping final chunk questions."
        in message
        for message in messages
    )

def test_post_classification_finalization_classifies_chunks_when_enabled(
    sample_document_graph,
    sample_document_classification,
    sample_chunk,
) -> None:
    graph = copy.deepcopy(sample_document_graph)
    first_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_a",
        content="Chunk A content.",
        chunk_type=ChunkType.GENERAL,
    )
    second_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_b",
        content="Chunk B content.",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
    )
    graph.replace_chunks([first_chunk, second_chunk])
    decision = DocumentTypeDecision(
        effective_document_type=DocumentType.MANUAL,
        effective_chunking_profile=ChunkingProfile.MANUAL,
        confidence=0.9,
        reasons=["reused provisional chunks"],
        should_rechunk=False,
    )
    chunk_workflow = FakeChunkClassificationWorkflow()
    (
        workflow,
        _,
        returned_chunk_workflow,
        _,
        _,
        _,
        _,
        _,
    ) = make_workflow(
        graph=graph,
        classification=sample_document_classification,
        decision=decision,
        rechunked_chunks=[first_chunk, second_chunk],
        provisional_profile=ChunkingProfile.MANUAL,
        chunk_classification_workflow=chunk_workflow,
        enable_chunk_classification=True,
        enable_question_generation=False,
    )
    messages: list[str] = []

    workflow.finalize(
        graph.document.document_id,
        progress_callback=messages.append,
    )

    assert returned_chunk_workflow is chunk_workflow
    assert sorted(chunk_workflow.calls) == ["chunk_a", "chunk_b"]
    assert any("Classifying 2 final chunk(s)..." in message for message in messages)
    assert any("Classified 2 final chunk(s)." in message for message in messages)

def test_asset_heavy_datasheet_finalization_does_not_produce_zero_chunks(
    sample_document,
    sample_document_classification,
) -> None:
    graph = make_asset_heavy_datasheet_graph(sample_document)
    classification = copy.deepcopy(sample_document_classification)
    classification.document_type = DocumentType.DATASHEET
    classification.result.predicted_label = DocumentType.DATASHEET.value
    decision = DocumentTypeDecision(
        effective_document_type=DocumentType.DATASHEET,
        effective_chunking_profile=ChunkingProfile.DATASHEET,
        confidence=0.91,
        reasons=["asset-heavy datasheet"],
        should_rechunk=False,
    )
    real_graph_chunk_builder = GraphChunkBuilder(
        id_generator=IdGenerator(),
        section_chunk_builder=SectionChunkBuilder(),
    )
    (
        workflow,
        _,
        _,
        _,
        _,
        embedding_workflow,
        _,
        _,
    ) = make_workflow(
        graph=graph,
        classification=classification,
        decision=decision,
        rechunked_chunks=[],
        provisional_profile=ChunkingProfile.DATASHEET,
        enable_question_generation=False,
        graph_chunk_builder=real_graph_chunk_builder,
    )

    result = workflow.finalize(graph.document.document_id)

    assert result.chunks
    assert embedding_workflow.calls
    recovered_chunks = list(result.chunks.values())
    assert any(
        "DF-100" in chunk.content or "DN100" in chunk.content
        for chunk in recovered_chunks
    )
    assert all(chunk.source.page_start == 1 for chunk in recovered_chunks)
    assert any(chunk.table_ids or chunk.picture_ids for chunk in recovered_chunks)

def test_datasheet_policy_allows_asset_fallback_when_no_text_chunks_exist(
    sample_document,
    sample_document_classification,
) -> None:
    graph = make_asset_heavy_datasheet_graph(sample_document)
    graph.tables = {}
    graph.elements.pop("el_table_001")
    graph.sections["sec_asset"].element_ids = ["el_picture_001"]
    classification = copy.deepcopy(sample_document_classification)
    classification.document_type = DocumentType.DATASHEET
    classification.result.predicted_label = DocumentType.DATASHEET.value
    decision = DocumentTypeDecision(
        effective_document_type=DocumentType.DATASHEET,
        effective_chunking_profile=ChunkingProfile.DATASHEET,
        confidence=0.91,
        reasons=["picture-only datasheet"],
        should_rechunk=False,
    )
    real_graph_chunk_builder = GraphChunkBuilder(
        id_generator=IdGenerator(),
        section_chunk_builder=SectionChunkBuilder(),
    )
    workflow, _, _, _, _, _, _, _ = make_workflow(
        graph=graph,
        classification=classification,
        decision=decision,
        rechunked_chunks=[],
        provisional_profile=ChunkingProfile.DATASHEET,
        enable_question_generation=False,
        graph_chunk_builder=real_graph_chunk_builder,
    )

    result = workflow.finalize(graph.document.document_id)

    assert result.chunks
    assert any(
        chunk.chunk_type == ChunkType.DRAWING_REFERENCE
        for chunk in result.chunks.values()
    )

def test_zero_chunk_finalization_raises_clear_error_when_no_asset_evidence_exists(
    sample_document,
    sample_document_classification,
) -> None:
    from src.domain.common import SourceLocation

    document = copy.deepcopy(sample_document)
    document.title = "Blank datasheet"
    document.document_type = DocumentType.DATASHEET
    graph = DocumentGraph(document=document)
    section = DocumentSection(
        section_id="sec_blank",
        document_id=document.document_id,
        title="Technical Data",
        level=1,
        section_path=["Technical Data"],
        source=SourceLocation(page_start=1, page_end=1),
        element_ids=[],
        sequence_number=1,
    )
    graph.add_section(section)
    blank_picture = make_asset_element(
        element_id="el_picture_blank",
        document_id=document.document_id,
        section_id=section.section_id,
        element_type=ElementType.PICTURE,
        picture_id="picture_blank",
        page=1,
        extra={},
    )
    graph.add_element(blank_picture)
    section.element_ids.append(blank_picture.element_id)
    graph.replace_chunks([])
    classification = copy.deepcopy(sample_document_classification)
    classification.document_type = DocumentType.DATASHEET
    classification.result.predicted_label = DocumentType.DATASHEET.value
    decision = DocumentTypeDecision(
        effective_document_type=DocumentType.DATASHEET,
        effective_chunking_profile=ChunkingProfile.DATASHEET,
        confidence=0.8,
        reasons=["no asset evidence"],
        should_rechunk=False,
    )
    real_graph_chunk_builder = GraphChunkBuilder(
        id_generator=IdGenerator(),
        section_chunk_builder=SectionChunkBuilder(),
    )
    workflow, _, _, _, _, _, _, _ = make_workflow(
        graph=graph,
        classification=classification,
        decision=decision,
        rechunked_chunks=[],
        provisional_profile=ChunkingProfile.DATASHEET,
        enable_question_generation=False,
        graph_chunk_builder=real_graph_chunk_builder,
    )

    with pytest.raises(ApplicationError) as exc_info:
        workflow.finalize(graph.document.document_id)

    assert exc_info.value.details["document_type"] == DocumentType.DATASHEET.value
    assert exc_info.value.details["include_picture_chunks"] is False
    assert exc_info.value.details["asset_fallback_attempted"] is True
