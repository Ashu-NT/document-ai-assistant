import copy

import threading

import pytest

from src.application.workflows.classification import (
    DocumentTypeDecision,
    PostClassificationChunkFinalizationWorkflow,
)

from src.application.workflows.parsing.builders.document_graph.graph_chunk_builder import (
    GraphChunkBuilder,
)

from src.application.workflows.parsing.builders.chunking.builders.section_chunk.section_chunk_builder import (
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
        self.saved_chunk_classifications: list = []

    def get_document_classification(self, document_id: str):
        self.calls.append(document_id)
        return self.classification

    def save_chunk_classification(self, classification, activity_context=None):
        self.saved_chunk_classifications.append(classification)

    def save_chunk_classifications(self, classifications, activity_context=None):
        self.saved_chunk_classifications.extend(classifications)

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
        self._lock = threading.Lock()

    def classify_chunk_without_saving(self, chunk: DocumentChunk, activity_context=None):
        with self._lock:
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

__all__ = [name for name in globals() if not name.startswith("__")]
