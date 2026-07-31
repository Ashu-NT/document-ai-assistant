from typing import Callable

from src.application.contracts.retrieval import VectorStore
from src.application.services.classification import ClassificationService
from src.application.services.document import (
    DocumentLookupService,
    DocumentRegistrationService,
)
from src.application.services.question_generation import QuestionGenerationService
from src.application.workflows.classification.chunk_type_classification_workflow import (
    ChunkTypeClassificationWorkflow,
)
from src.application.workflows.classification.classification_workflow_settings import (
    default_enable_question_generation,
)
from src.application.workflows.classification.finalization.asset_fallback_chunk_recovery import (
    AssetFallbackChunkRecovery,
)
from src.application.workflows.classification.finalization.final_chunk_classification_runner import (
    FinalChunkClassificationRunner,
)
from src.application.workflows.classification.finalization.final_chunk_resolver import (
    FinalChunkResolver,
)
from src.application.workflows.classification.finalization.final_question_generation_runner import (
    FinalQuestionGenerationRunner,
)
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
from src.domain.document import DocumentGraph, DocumentSection
from src.domain.document.value_objects import DocumentStatistics
from src.shared.activity import ActivityContext
from src.shared.exceptions import ApplicationError
from src.shared.execution import tracked_action
from src.shared.progress.progress_emitter import emit_progress


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
        chunk_type_classification_workflow: ChunkTypeClassificationWorkflow | None = None,
        chunking_profile_inferer: ChunkingProfileInferer | None = None,
        chunking_policy_resolver: DocumentChunkingPolicyResolver | None = None,
        document_type_resolver: HybridDocumentTypeResolver | None = None,
        enable_question_generation: bool | None = None,
    ) -> None:
        self.document_lookup_service = document_lookup_service
        self.document_registration_service = document_registration_service
        self.classification_service = classification_service
        self.question_generation_service = question_generation_service
        self.embedding_workflow = embedding_workflow
        self.vector_store = vector_store
        self.graph_chunk_builder = graph_chunk_builder
        self.chunk_type_classification_workflow = chunk_type_classification_workflow
        self.chunking_profile_inferer = (
            chunking_profile_inferer or ChunkingProfileInferer()
        )
        self.chunking_policy_resolver = (
            chunking_policy_resolver or DocumentChunkingPolicyResolver()
        )
        self.document_type_resolver = (
            document_type_resolver or HybridDocumentTypeResolver()
        )
        self.enable_question_generation = (
            enable_question_generation
            if enable_question_generation is not None
            else default_enable_question_generation()
        )

        asset_fallback_recovery = AssetFallbackChunkRecovery(
            graph_chunk_builder=graph_chunk_builder,
        )
        self._final_chunk_resolver = FinalChunkResolver(
            graph_chunk_builder=graph_chunk_builder,
            asset_fallback_recovery=asset_fallback_recovery,
        )
        self._chunk_classification_runner = FinalChunkClassificationRunner(
            classification_service=classification_service,
            chunk_type_classification_workflow=chunk_type_classification_workflow,
        )
        self._question_generation_runner = FinalQuestionGenerationRunner(
            question_generation_service=question_generation_service,
            enable_question_generation=self.enable_question_generation,
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
        embed_final_chunks: bool = True,
        enable_question_generation: bool | None = None,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> DocumentGraph:
        emit_progress(
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

        emit_progress(
            progress_callback,
            "Loading saved document classification...",
        )
        classification = self.classification_service.get_document_classification(
            document_id
        )
        if classification is None:
            emit_progress(
                progress_callback,
                "No saved document classification found; falling back to "
                "structural inference only.",
            )

        emit_progress(
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
        emit_progress(
            progress_callback,
            (
                "Chunking decision resolved: "
                f"document_type={decision.effective_document_type.value}, "
                f"profile={decision.effective_chunking_profile.value}, "
                f"should_rechunk={'yes' if decision.should_rechunk else 'no'}."
            ),
        )

        effective_policy = self.chunking_policy_resolver.resolve(
            document_title=graph.document.title,
            document_type=decision.effective_document_type,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
            chunking_profile_override=decision.effective_chunking_profile,
        )
        final_chunks, final_chunk_mode = self._final_chunk_resolver.resolve(
            graph=graph,
            sections=sections,
            decision=decision,
            effective_include_picture_chunks=effective_policy.include_picture_chunks,
            progress_callback=progress_callback,
        )
        emit_progress(
            progress_callback,
            self._final_chunk_resolver.progress_message(final_chunk_mode),
        )
        emit_progress(
            progress_callback,
            f"Final chunk set contains {len(final_chunks)} chunk(s).",
        )
        self._chunk_classification_runner.classify_chunk_types_if_enabled(
            chunks=final_chunks,
            progress_callback=progress_callback,
        )
        graph.document.document_type = decision.effective_document_type
        graph.replace_chunks(final_chunks)
        graph.clear_chunk_dependents()
        self._question_generation_runner.generate_if_enabled(
            graph=graph,
            max_questions_per_chunk=max_questions_per_chunk,
            enable_question_generation=enable_question_generation,
            activity_context=activity_context,
            progress_callback=progress_callback,
        )
        graph.document.statistics = DocumentStatistics(
            page_count=graph.document.statistics.page_count,
            element_count=len(graph.elements),
            section_count=len(graph.sections),
            chunk_count=len(graph.chunks),
            table_count=len(graph.tables),
            picture_count=len(graph.pictures),
        )

        if embed_final_chunks:
            emit_progress(
                progress_callback,
                "Deleting existing vectors for this document...",
            )
            self.vector_store.delete_document_vectors(document_id)
        emit_progress(
            progress_callback,
            "Persisting final chunk artifacts to the document repository...",
        )
        self.document_registration_service.replace_document_chunk_artifacts(
            graph,
            activity_context=activity_context,
        )
        if embed_final_chunks:
            emit_progress(
                progress_callback,
                f"Embedding and storing {len(final_chunks)} final chunk(s)...",
            )
            self.embedding_workflow.embed_and_store_chunks(
                final_chunks,
                activity_context=activity_context,
                progress_callback=progress_callback,
            )
        else:
            emit_progress(
                progress_callback,
                "Skipping final embedding because the caller will embed and index later.",
            )
        emit_progress(
            progress_callback,
            "Post-classification chunk finalization completed.",
        )

        return graph

    @staticmethod
    def _ordered_sections(graph: DocumentGraph) -> list[DocumentSection]:
        return sorted(
            graph.sections.values(),
            key=lambda section: section.sequence_number or 0,
        )
