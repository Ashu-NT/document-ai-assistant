from tests.unit.application.workflows.classification._test_post_classification_chunk_finalization_workflow_support import *  # noqa: F401,F403

from src.application.workflows.parsing.builders.chunking.policies.profile.structural_profile_inference_cache import (
    load_structural_profile_inference,
    store_structural_profile_inference,
)


def _build_workflow_with_inferer_spy(
    *,
    graph,
    classification,
    decision: DocumentTypeDecision,
    rechunked_chunks: list[DocumentChunk],
    provisional_profile: ChunkingProfile,
):
    inferer = FakeStructuralProfileInferer(make_inference(provisional_profile))
    workflow = PostClassificationChunkFinalizationWorkflow(
        document_lookup_service=FakeDocumentLookupService(graph),
        document_registration_service=FakeDocumentRegistrationService([]),
        classification_service=FakeClassificationService(classification),
        question_generation_service=FakeQuestionGenerationService(),
        embedding_workflow=FakeEmbeddingWorkflow([]),
        vector_store=FakeVectorStore([]),
        graph_chunk_builder=FakeGraphChunkBuilder(rechunked_chunks),
        chunking_profile_inferer=inferer,
        chunking_policy_resolver=FakeChunkingPolicyResolver(provisional_profile),
        document_type_resolver=FakeDocumentTypeResolver(decision),
        enable_question_generation=False,
    )
    return workflow, inferer


def test_finalization_reuses_cached_structural_inference_instead_of_recomputing(
    sample_document_graph,
    sample_document_classification,
    sample_chunk,
) -> None:
    graph = copy.deepcopy(sample_document_graph)
    graph.replace_chunks([sample_chunk])
    cached_inference = make_inference(ChunkingProfile.MANUAL)
    store_structural_profile_inference(graph.document.metadata, cached_inference)
    decision = DocumentTypeDecision(
        effective_document_type=DocumentType.MANUAL,
        effective_chunking_profile=ChunkingProfile.MANUAL,
        confidence=0.9,
        reasons=["cached"],
        should_rechunk=False,
    )
    workflow, inferer = _build_workflow_with_inferer_spy(
        graph=graph,
        classification=sample_document_classification,
        decision=decision,
        rechunked_chunks=[sample_chunk],
        provisional_profile=ChunkingProfile.MANUAL,
    )

    workflow.finalize(graph.document.document_id)

    assert inferer.calls == []


def test_finalization_computes_and_caches_structural_inference_when_none_cached(
    sample_document_graph,
    sample_document_classification,
    sample_chunk,
) -> None:
    graph = copy.deepcopy(sample_document_graph)
    graph.replace_chunks([sample_chunk])
    assert load_structural_profile_inference(graph.document.metadata) is None
    decision = DocumentTypeDecision(
        effective_document_type=DocumentType.MANUAL,
        effective_chunking_profile=ChunkingProfile.MANUAL,
        confidence=0.9,
        reasons=["computed fresh"],
        should_rechunk=False,
    )
    workflow, inferer = _build_workflow_with_inferer_spy(
        graph=graph,
        classification=sample_document_classification,
        decision=decision,
        rechunked_chunks=[sample_chunk],
        provisional_profile=ChunkingProfile.MANUAL,
    )

    workflow.finalize(graph.document.document_id)

    assert len(inferer.calls) == 1
    assert load_structural_profile_inference(graph.document.metadata) is not None
