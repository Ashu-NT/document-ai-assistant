from tests.unit.application.workflows.classification._test_post_classification_chunk_finalization_workflow_support_part1 import *  # noqa: F401,F403

def make_workflow(
    *,
    graph,
    classification,
    decision: DocumentTypeDecision,
    rechunked_chunks: list[DocumentChunk],
    provisional_profile: ChunkingProfile,
    enable_question_generation: bool = True,
    graph_chunk_builder=None,
) -> tuple[
    PostClassificationChunkFinalizationWorkflow,
    FakeQuestionGenerationService,
    FakeDocumentRegistrationService,
    FakeVectorStore,
    FakeEmbeddingWorkflow,
    FakeGraphChunkBuilder,
    list[str],
]:
    operations: list[str] = []
    question_generation_service = FakeQuestionGenerationService()
    registration_service = FakeDocumentRegistrationService(operations)
    vector_store = FakeVectorStore(operations)
    embedding_workflow = FakeEmbeddingWorkflow(operations)
    graph_chunk_builder = graph_chunk_builder or FakeGraphChunkBuilder(rechunked_chunks)
    workflow = PostClassificationChunkFinalizationWorkflow(
        document_lookup_service=FakeDocumentLookupService(graph),
        document_registration_service=registration_service,
        classification_service=FakeClassificationService(classification),
        question_generation_service=question_generation_service,
        embedding_workflow=embedding_workflow,
        vector_store=vector_store,
        graph_chunk_builder=graph_chunk_builder,
        chunking_profile_inferer=FakeChunkingProfileInferer(
            make_inference(provisional_profile)
        ),
        chunking_policy_resolver=FakeChunkingPolicyResolver(provisional_profile),
        document_type_resolver=FakeDocumentTypeResolver(decision),
        enable_question_generation=enable_question_generation,
    )
    return (
        workflow,
        question_generation_service,
        registration_service,
        vector_store,
        embedding_workflow,
        graph_chunk_builder,
        operations,
    )

def make_asset_element(
    *,
    element_id: str,
    document_id: str,
    section_id: str,
    element_type: ElementType,
    page: int,
    table_id: str | None = None,
    picture_id: str | None = None,
    text: str | None = None,
    extra: dict | None = None,
) -> CanonicalElement:
    from src.domain.common import SourceLocation

    return CanonicalElement(
        element_id=element_id,
        document_id=document_id,
        element_type=element_type,
        text=text,
        parent_section_id=section_id,
        reading_order=page,
        source=SourceLocation(page_start=page, page_end=page),
        table_id=table_id,
        picture_id=picture_id,
        parser_metadata=ParserMetadata(
            parser_name="docling",
            raw_source_type=element_type.value,
            extra=extra or {},
        ),
    )

def make_asset_heavy_datasheet_graph(sample_document) -> DocumentGraph:
    from src.domain.common import SourceLocation

    document = copy.deepcopy(sample_document)
    document.title = "Deck fillers datasheet"
    document.document_type = DocumentType.DATASHEET
    graph = DocumentGraph(document=document)
    section = DocumentSection(
        section_id="sec_asset",
        document_id=document.document_id,
        title="Technical Data",
        level=1,
        section_path=["Technical Data"],
        source=SourceLocation(page_start=1, page_end=1),
        element_ids=[],
        sequence_number=1,
    )
    graph.add_section(section)
    table_element = make_asset_element(
        element_id="el_table_001",
        document_id=document.document_id,
        section_id=section.section_id,
        element_type=ElementType.TABLE,
        table_id="table_001",
        page=1,
        extra={
            "markdown": "| Order Code | Size |\n|---|---|\n| DF-100 | DN100 |",
            "caption": "Ordering information",
            "row_count": 2,
            "column_count": 2,
        },
    )
    picture_element = make_asset_element(
        element_id="el_picture_001",
        document_id=document.document_id,
        section_id=section.section_id,
        element_type=ElementType.PICTURE,
        picture_id="picture_001",
        page=1,
        extra={
            "caption": "Deck filler dimensions",
            "ocr_text": "DN100 hose connection deck filler",
            "image_path": "outputs/images/deck_filler.png",
        },
    )
    for element in (table_element, picture_element):
        graph.add_element(element)
        section.element_ids.append(element.element_id)

    graph.tables["table_001"] = TableAsset(
        table_id="table_001",
        document_id=document.document_id,
        parent_section_id=section.section_id,
        markdown="| Order Code | Size |\n|---|---|\n| DF-100 | DN100 |",
        metadata=AssetMetadata(caption="Ordering information"),
    )
    graph.pictures["picture_001"] = PictureAsset(
        picture_id="picture_001",
        document_id=document.document_id,
        parent_section_id=section.section_id,
        image_path="outputs/images/deck_filler.png",
        ocr_text="DN100 hose connection deck filler",
        metadata=AssetMetadata(caption="Deck filler dimensions"),
    )
    graph.replace_chunks([])
    return graph

__all__ = [name for name in globals() if not name.startswith("__")]
