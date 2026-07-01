import copy

import pytest

from src.application.workflows.classification import (
    DocumentTypeDecision,
    PostClassificationChunkFinalizationWorkflow,
)
from src.application.workflows.parsing.builders.document_graph.graph_chunk_builder import (
    GraphChunkBuilder,
)
from src.application.workflows.parsing.builders.chunking.builders.section_chunk_builder import (
    SectionChunkBuilder,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_inference import (
    ChunkingProfileInference,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_statistics import (
    ChunkingProfileStatistics,
)
from src.application.workflows.parsing.builders.chunking.policies.document_chunking_policy import (
    DocumentChunkingPolicy,
)
from src.domain.assets import AssetMetadata, PictureAsset, TableAsset
from src.domain.common import ChunkType, DocumentType, ElementType, ParserMetadata
from src.domain.document import DocumentChunk, DocumentGraph, DocumentSection, GeneratedQuestion
from src.domain.elements import CanonicalElement
from src.shared.exceptions import ApplicationError
from src.shared.execution import ActionResult
from src.shared.ids import IdGenerator


class FakeDocumentLookupService:
    def __init__(self, graph) -> None:
        self.graph = graph
        self.calls: list[str] = []

    def get_document_graph(self, document_id: str, activity_context=None):
        self.calls.append(document_id)
        return self.graph


class FakeClassificationService:
    def __init__(self, classification) -> None:
        self.classification = classification
        self.calls: list[str] = []

    def get_document_classification(self, document_id: str):
        self.calls.append(document_id)
        return self.classification


class FakeQuestionGenerationService:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def generate_for_chunks(
        self,
        chunks: list[DocumentChunk],
        max_questions_per_chunk: int = 5,
        activity_context=None,
        progress_callback=None,
    ) -> list[GeneratedQuestion]:
        self.calls.append([chunk.chunk_id for chunk in chunks])
        if progress_callback is not None:
            progress_callback(
                f"question generation called for {len(chunks)} chunk(s)"
            )
        return [
            GeneratedQuestion(
                question_id=f"question_{index:03d}",
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                question=f"Question for {chunk.chunk_id}?",
            )
            for index, chunk in enumerate(chunks, start=1)
        ]


class FakeChunkClassificationWorkflow:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def classify_chunk(self, chunk: DocumentChunk, activity_context=None):
        self.calls.append(chunk.chunk_id)
        return None


class FakeDocumentRegistrationService:
    def __init__(self, operations: list[str]) -> None:
        self.operations = operations
        self.replace_calls = []

    def replace_document_chunk_artifacts(
        self,
        document_graph,
        activity_context=None,
    ) -> ActionResult:
        self.operations.append("replace")
        self.replace_calls.append(copy.deepcopy(document_graph))
        return ActionResult(
            entity_type="document",
            entity_id=document_graph.document.document_id,
        )


class FakeVectorStore:
    def __init__(self, operations: list[str]) -> None:
        self.operations = operations
        self.delete_calls: list[str] = []

    def delete_document_vectors(self, document_id: str) -> None:
        self.operations.append("delete_vectors")
        self.delete_calls.append(document_id)


class FakeEmbeddingWorkflow:
    def __init__(self, operations: list[str]) -> None:
        self.operations = operations
        self.calls: list[list[str]] = []

    def embed_and_store_chunks(
        self,
        chunks: list[DocumentChunk],
        activity_context=None,
        progress_callback=None,
    ):
        self.operations.append("embed")
        self.calls.append([chunk.chunk_id for chunk in chunks])
        if progress_callback is not None:
            progress_callback(f"embedding called for {len(chunks)} chunk(s)")
        return []


class FakeGraphChunkBuilder:
    def __init__(self, rechunked_chunks: list[DocumentChunk]) -> None:
        self.rechunked_chunks = rechunked_chunks
        self.calls: list[dict] = []

    def build_chunks(self, **kwargs) -> list[DocumentChunk]:
        self.calls.append(kwargs)
        return self.rechunked_chunks


class FakeChunkingProfileInferer:
    def __init__(self, inference: ChunkingProfileInference) -> None:
        self.inference = inference

    def infer_result(self, **kwargs) -> ChunkingProfileInference:
        return self.inference


class FakeChunkingPolicyResolver:
    def __init__(self, profile_name: ChunkingProfile) -> None:
        self.profile_name = profile_name

    def resolve(self, **kwargs) -> DocumentChunkingPolicy:
        return DocumentChunkingPolicy(
            profile_name=self.profile_name,
            max_chunk_tokens=200,
            chunk_overlap=20,
            same_topic_merge_tokens=90,
            intro_context_tokens=120,
            asset_context_window=1,
            asset_context_max_tokens=72,
            include_picture_chunks=self.profile_name
            not in {ChunkingProfile.DATASHEET, ChunkingProfile.CERTIFICATE},
        )


class FakeDocumentTypeResolver:
    def __init__(self, decision: DocumentTypeDecision) -> None:
        self.decision = decision

    def resolve(self, **kwargs) -> DocumentTypeDecision:
        return self.decision


def clone_chunk(
    sample_chunk,
    *,
    chunk_id: str,
    content: str,
    chunk_type: ChunkType,
) -> DocumentChunk:
    return sample_chunk.__class__(
        chunk_id=chunk_id,
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content=content,
        chunk_type=chunk_type,
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


def make_inference(profile: ChunkingProfile) -> ChunkingProfileInference:
    return ChunkingProfileInference(
        selected_profile=profile,
        confidence=0.81,
        scores={profile: 4.0},
        reasons={profile: [f"{profile.value} signal"]},
        statistics=ChunkingProfileStatistics(),
    )


def make_workflow(
    *,
    graph,
    classification,
    decision: DocumentTypeDecision,
    rechunked_chunks: list[DocumentChunk],
    provisional_profile: ChunkingProfile,
    chunk_classification_workflow: FakeChunkClassificationWorkflow | None = None,
    enable_chunk_classification: bool = False,
    enable_question_generation: bool = True,
    graph_chunk_builder=None,
) -> tuple[
    PostClassificationChunkFinalizationWorkflow,
    FakeQuestionGenerationService,
    FakeChunkClassificationWorkflow | None,
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
        chunk_classification_workflow=chunk_classification_workflow,
        question_generation_service=question_generation_service,
        embedding_workflow=embedding_workflow,
        vector_store=vector_store,
        graph_chunk_builder=graph_chunk_builder,
        chunking_profile_inferer=FakeChunkingProfileInferer(
            make_inference(provisional_profile)
        ),
        chunking_policy_resolver=FakeChunkingPolicyResolver(provisional_profile),
        document_type_resolver=FakeDocumentTypeResolver(decision),
        enable_chunk_classification=enable_chunk_classification,
        enable_question_generation=enable_question_generation,
    )
    return (
        workflow,
        question_generation_service,
        chunk_classification_workflow,
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
        _,
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
        _,
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
    workflow, _, _, _, _, embedding_workflow, graph_chunk_builder, _ = make_workflow(
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
    workflow, _, _, _, _, _, _, _ = make_workflow(
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
    assert chunk_workflow.calls == ["chunk_a", "chunk_b"]
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
