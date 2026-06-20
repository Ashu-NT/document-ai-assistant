from typing import Callable

from src.application.contracts.retrieval import VectorStore
from src.application.services.classification import ClassificationService
from src.application.services.document import (
    DocumentLookupService,
    DocumentRegistrationService,
)
from src.application.services.question_generation import QuestionGenerationService
from src.application.workflows.classification.hybrid_document_type_resolver import (
    HybridDocumentTypeResolver,
)
from src.application.workflows.embedding import EmbeddingWorkflow
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_inferer import (
    ChunkingProfileInferer,
)
from src.application.workflows.parsing.builders.chunking.policies.document_chunking_policy_resolver import (
    DocumentChunkingPolicyResolver,
)
from src.application.workflows.parsing.builders.document_graph.graph_chunk_builder import (
    GraphChunkBuilder,
)
from src.domain.common import ChunkType
from src.domain.document import DocumentChunk, DocumentGraph, DocumentSection
from src.domain.document.value_objects import DocumentStatistics
from src.shared.activity import ActivityContext
from src.shared.exceptions import ApplicationError
from src.shared.execution import tracked_action


class PostClassificationChunkFinalizationWorkflow:
    def __init__(
        self,
        *,
        document_lookup_service: DocumentLookupService,
        document_registration_service: DocumentRegistrationService,
        classification_service: ClassificationService,
        question_generation_service: QuestionGenerationService,
        embedding_workflow: EmbeddingWorkflow,
        vector_store: VectorStore,
        graph_chunk_builder: GraphChunkBuilder,
        chunking_profile_inferer: ChunkingProfileInferer | None = None,
        chunking_policy_resolver: DocumentChunkingPolicyResolver | None = None,
        document_type_resolver: HybridDocumentTypeResolver | None = None,
    ) -> None:
        self.document_lookup_service = document_lookup_service
        self.document_registration_service = document_registration_service
        self.classification_service = classification_service
        self.question_generation_service = question_generation_service
        self.embedding_workflow = embedding_workflow
        self.vector_store = vector_store
        self.graph_chunk_builder = graph_chunk_builder
        self.chunking_profile_inferer = (
            chunking_profile_inferer or ChunkingProfileInferer()
        )
        self.chunking_policy_resolver = (
            chunking_policy_resolver or DocumentChunkingPolicyResolver()
        )
        self.document_type_resolver = (
            document_type_resolver or HybridDocumentTypeResolver()
        )

    @tracked_action(
        action="classification.chunk_finalization_completed",
        entity_type="document",
        activity=True,
        audit=False,
        event=False,
    )
    def finalize(
        self,
        document_id: str,
        *,
        max_questions_per_chunk: int = 5,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> DocumentGraph:
        self._emit_progress(
            progress_callback,
            f"Loading persisted document graph for {document_id}...",
        )
        graph = self.document_lookup_service.get_document_graph(
            document_id,
            activity_context=activity_context,
        )
        if graph is None:
            raise ApplicationError(
                "Document graph not found for post-classification finalization.",
                details={"document_id": document_id},
            )

        self._emit_progress(
            progress_callback,
            "Loading saved document classification...",
        )
        classification = self.classification_service.get_document_classification(
            document_id
        )
        if classification is None:
            raise ApplicationError(
                "Document classification not found for post-classification finalization.",
                details={"document_id": document_id},
            )

        self._emit_progress(
            progress_callback,
            "Resolving final document type and chunking policy...",
        )
        sections = self._ordered_sections(graph)
        section_elements_by_id = {
            section.section_id: graph.get_section_elements(section.section_id)
            for section in sections
        }
        structural_inference = self.chunking_profile_inferer.infer_result(
            document_title=graph.document.title,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
        )
        provisional_policy = self.chunking_policy_resolver.resolve(
            document_title=graph.document.title,
            document_type=graph.document.document_type,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
        )
        decision = self.document_type_resolver.resolve(
            parser_title_hint=graph.document.document_type,
            structural_inference=structural_inference,
            classification=classification,
            provisional_chunking_profile=provisional_policy.profile_name,
        )
        self._emit_progress(
            progress_callback,
            (
                "Chunking decision resolved: "
                f"document_type={decision.effective_document_type.value}, "
                f"profile={decision.effective_chunking_profile.value}, "
                f"should_rechunk={'yes' if decision.should_rechunk else 'no'}."
            ),
        )

        self._emit_progress(
            progress_callback,
            "Building final chunk set..." if decision.should_rechunk
            else "Reusing stored final chunk set...",
        )
        final_chunks = self._final_chunks(
            graph=graph,
            sections=sections,
            decision=decision,
        )
        self._emit_progress(
            progress_callback,
            f"Final chunk set contains {len(final_chunks)} chunk(s).",
        )
        graph.document.document_type = decision.effective_document_type
        graph.replace_chunks(final_chunks)
        graph.clear_chunk_dependents()
        questionable_chunks = [
            chunk
            for chunk in final_chunks
            if chunk.chunk_type != ChunkType.OVERVIEW
        ]
        self._emit_progress(
            progress_callback,
            f"Generating questions for {len(questionable_chunks)} chunk(s)...",
        )
        graph.replace_questions(
            self.question_generation_service.generate_for_chunks(
                questionable_chunks,
                max_questions_per_chunk=max_questions_per_chunk,
                activity_context=activity_context,
                progress_callback=progress_callback,
            )
        )
        self._emit_progress(
            progress_callback,
            f"Generated {len(graph.questions)} question(s) for final chunk set.",
        )
        graph.document.statistics = DocumentStatistics(
            page_count=graph.document.statistics.page_count,
            element_count=len(graph.elements),
            section_count=len(graph.sections),
            chunk_count=len(graph.chunks),
            table_count=len(graph.tables),
            picture_count=len(graph.pictures),
        )

        self._emit_progress(
            progress_callback,
            "Deleting existing vectors for this document...",
        )
        self.vector_store.delete_document_vectors(document_id)
        self._emit_progress(
            progress_callback,
            "Persisting final chunk artifacts to the document repository...",
        )
        self.document_registration_service.replace_document_chunk_artifacts(
            graph,
            activity_context=activity_context,
        )
        self._emit_progress(
            progress_callback,
            f"Embedding and storing {len(final_chunks)} final chunk(s)...",
        )
        self.embedding_workflow.embed_and_store_chunks(
            final_chunks,
            activity_context=activity_context,
            progress_callback=progress_callback,
        )
        self._emit_progress(
            progress_callback,
            "Post-classification chunk finalization completed.",
        )

        return graph

    def _final_chunks(
        self,
        *,
        graph: DocumentGraph,
        sections: list[DocumentSection],
        decision,
    ) -> list[DocumentChunk]:
        if not decision.should_rechunk:
            return sorted(
                graph.chunks.values(),
                key=lambda chunk: chunk.sequence_number,
            )

        return self.graph_chunk_builder.build_chunks(
            graph=graph,
            sections=sections,
            document_type_override=decision.effective_document_type,
            chunking_profile_override=decision.effective_chunking_profile,
        )

    @staticmethod
    def _ordered_sections(graph: DocumentGraph) -> list[DocumentSection]:
        return sorted(
            graph.sections.values(),
            key=lambda section: section.sequence_number or 0,
        )

    @staticmethod
    def _emit_progress(
        progress_callback: Callable[[str], None] | None,
        message: str,
    ) -> None:
        if progress_callback is not None:
            progress_callback(message)
