from tests.unit.application.workflows.classification._test_post_classification_chunk_finalization_workflow_support import *  # noqa: F401,F403

def test_final_chunks_falls_back_to_stored_chunks_when_rebuild_and_asset_fallback_are_empty(
    sample_document,
    sample_document_classification,
    sample_chunk,
) -> None:
    from src.domain.common import SourceLocation

    document = copy.deepcopy(sample_document)
    document.title = "Datasheet with prior chunks"
    document.document_type = DocumentType.DATASHEET
    graph = DocumentGraph(document=document)
    section = DocumentSection(
        section_id="sec_prior",
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

    stored_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_stored_001",
        content="Previously extracted datasheet content.",
        chunk_type=ChunkType.GENERAL,
    )
    graph.replace_chunks([stored_chunk])

    classification = copy.deepcopy(sample_document_classification)
    classification.document_type = DocumentType.DATASHEET
    classification.result.predicted_label = DocumentType.DATASHEET.value
    decision = DocumentTypeDecision(
        effective_document_type=DocumentType.DATASHEET,
        effective_chunking_profile=ChunkingProfile.DATASHEET,
        confidence=0.85,
        reasons=["rebuild produced nothing"],
        should_rechunk=False,
    )
    workflow, _, _, _, _, _, _ = make_workflow(
        graph=graph,
        classification=classification,
        decision=decision,
        rechunked_chunks=[],
        provisional_profile=ChunkingProfile.DATASHEET,
        enable_question_generation=False,
    )
    progress_messages: list[str] = []

    result = workflow.finalize(
        graph.document.document_id,
        progress_callback=progress_messages.append,
    )

    assert list(result.chunks.keys()) == ["chunk_stored_001"]
    assert any(
        "falling back to 1 previously stored chunk" in message
        for message in progress_messages
    )
