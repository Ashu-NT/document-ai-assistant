import copy

from src.application.workflows.classification import (
    DocumentTypeDecision,
    PostClassificationChunkFinalizationWorkflow,
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
from src.domain.common import ChunkType, DocumentType
from src.domain.document import DocumentChunk, GeneratedQuestion
from src.shared.execution import ActionResult


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
    ) -> list[GeneratedQuestion]:
        self.calls.append([chunk.chunk_id for chunk in chunks])
        return [
            GeneratedQuestion(
                question_id=f"question_{index:03d}",
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                question=f"Question for {chunk.chunk_id}?",
            )
            for index, chunk in enumerate(chunks, start=1)
        ]


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

    def embed_and_store_chunks(self, chunks: list[DocumentChunk], activity_context=None):
        self.operations.append("embed")
        self.calls.append([chunk.chunk_id for chunk in chunks])
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
    graph_chunk_builder = FakeGraphChunkBuilder(rechunked_chunks)
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
        rechunked_chunks=[detail_chunk],
        provisional_profile=ChunkingProfile.MANUAL,
    )

    result = workflow.finalize(graph.document.document_id)

    assert list(result.chunks) == ["chunk_overview", "chunk_detail"]
    assert question_service.calls == [["chunk_detail"]]
    assert registration_service.replace_calls[0].questions
    assert vector_store.delete_calls == [graph.document.document_id]
    assert embedding_workflow.calls == [["chunk_overview", "chunk_detail"]]
    assert graph_chunk_builder.calls == []
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
