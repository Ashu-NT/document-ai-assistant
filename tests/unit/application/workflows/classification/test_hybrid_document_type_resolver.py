from src.application.workflows.classification import HybridDocumentTypeResolver
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_inference import (
    ChunkingProfileInference,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_statistics import (
    ChunkingProfileStatistics,
)
from src.domain.classification import ClassificationResult, DocumentClassification
from src.domain.common import DocumentType, ModelProcessingMetadata


def make_inference(
    *,
    profile: ChunkingProfile,
    confidence: float,
) -> ChunkingProfileInference:
    return ChunkingProfileInference(
        selected_profile=profile,
        confidence=confidence,
        scores={profile: confidence},
        reasons={profile: [f"{profile.value} signal"]},
        statistics=ChunkingProfileStatistics(),
    )


def make_document_classification(
    *,
    document_type: DocumentType,
    confidence: float,
) -> DocumentClassification:
    return DocumentClassification(
        document_id="doc_001",
        document_type=document_type,
        result=ClassificationResult(
            classification_id="classification_001",
            document_id="doc_001",
            predicted_label=document_type.value,
            confidence_score=confidence,
            rationale="classification rationale",
            evidence=["evidence"],
            processing_metadata=ModelProcessingMetadata(
                model_name="qwen3:8b",
                model_type="document_classification",
                confidence=confidence,
                prompt_version="v1",
            ),
        ),
    )


def test_hybrid_document_type_resolver_uses_structural_fallback_when_model_missing() -> None:
    resolver = HybridDocumentTypeResolver()

    decision = resolver.resolve(
        parser_title_hint=DocumentType.UNKNOWN,
        structural_inference=make_inference(
            profile=ChunkingProfile.MANUAL,
            confidence=0.82,
        ),
        classification=None,
        provisional_chunking_profile=ChunkingProfile.DEFAULT,
    )

    assert decision.effective_document_type == DocumentType.MANUAL
    assert decision.effective_chunking_profile == ChunkingProfile.MANUAL
    assert decision.should_rechunk is True


def test_hybrid_document_type_resolver_lets_model_win_when_structural_signal_is_weak() -> None:
    resolver = HybridDocumentTypeResolver()

    decision = resolver.resolve(
        parser_title_hint=DocumentType.UNKNOWN,
        structural_inference=make_inference(
            profile=ChunkingProfile.MANUAL,
            confidence=0.5,
        ),
        classification=make_document_classification(
            document_type=DocumentType.DATASHEET,
            confidence=0.91,
        ),
        provisional_chunking_profile=ChunkingProfile.MANUAL,
    )

    assert decision.effective_document_type == DocumentType.DATASHEET
    assert decision.effective_chunking_profile == ChunkingProfile.DATASHEET


def test_hybrid_document_type_resolver_lets_structural_signal_win_when_model_is_weak() -> None:
    resolver = HybridDocumentTypeResolver()

    decision = resolver.resolve(
        parser_title_hint=DocumentType.UNKNOWN,
        structural_inference=make_inference(
            profile=ChunkingProfile.MANUAL,
            confidence=0.83,
        ),
        classification=make_document_classification(
            document_type=DocumentType.DATASHEET,
            confidence=0.52,
        ),
        provisional_chunking_profile=ChunkingProfile.DATASHEET,
    )

    assert decision.effective_document_type == DocumentType.MANUAL
    assert decision.effective_chunking_profile == ChunkingProfile.MANUAL


def test_hybrid_document_type_resolver_uses_default_profile_for_strong_conflict() -> None:
    resolver = HybridDocumentTypeResolver()

    decision = resolver.resolve(
        parser_title_hint=DocumentType.UNKNOWN,
        structural_inference=make_inference(
            profile=ChunkingProfile.MANUAL,
            confidence=0.8,
        ),
        classification=make_document_classification(
            document_type=DocumentType.DATASHEET,
            confidence=0.9,
        ),
        provisional_chunking_profile=ChunkingProfile.MANUAL,
    )

    assert decision.effective_chunking_profile == ChunkingProfile.DEFAULT
    assert decision.should_rechunk is True


def test_hybrid_document_type_resolver_computes_should_rechunk_from_provisional_profile() -> None:
    resolver = HybridDocumentTypeResolver()

    decision = resolver.resolve(
        parser_title_hint=DocumentType.UNKNOWN,
        structural_inference=make_inference(
            profile=ChunkingProfile.MANUAL,
            confidence=0.84,
        ),
        classification=make_document_classification(
            document_type=DocumentType.MANUAL,
            confidence=0.9,
        ),
        provisional_chunking_profile=ChunkingProfile.DEFAULT,
    )

    assert decision.effective_chunking_profile == ChunkingProfile.MANUAL
    assert decision.should_rechunk is True
