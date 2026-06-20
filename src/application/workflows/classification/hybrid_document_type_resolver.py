from src.application.workflows.classification.document_type_decision import (
    DocumentTypeDecision,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_inference import (
    ChunkingProfileInference,
)
from src.domain.classification import DocumentClassification
from src.domain.common import DocumentType


class HybridDocumentTypeResolver:
    def __init__(
        self,
        *,
        strong_model_threshold: float = 0.80,
        strong_structural_threshold: float = 0.75,
        weak_signal_threshold: float = 0.55,
    ) -> None:
        self.strong_model_threshold = strong_model_threshold
        self.strong_structural_threshold = strong_structural_threshold
        self.weak_signal_threshold = weak_signal_threshold

    def resolve(
        self,
        *,
        parser_title_hint: DocumentType | None,
        structural_inference: ChunkingProfileInference,
        classification: DocumentClassification | None,
        provisional_chunking_profile: ChunkingProfile | None = None,
    ) -> DocumentTypeDecision:
        parser_hint = parser_title_hint or DocumentType.UNKNOWN
        model_type = (
            classification.document_type
            if classification is not None
            else DocumentType.UNKNOWN
        )
        model_confidence = (
            classification.result.confidence_score
            if classification is not None and classification.result is not None
            else 0.0
        )
        structural_profile = structural_inference.selected_profile
        structural_type = self._document_type_for_profile(structural_profile)
        structural_confidence = structural_inference.confidence
        reasons: list[str] = []

        if self._is_strong(model_confidence, self.strong_model_threshold) and (
            self._is_strong(structural_confidence, self.strong_structural_threshold)
            and model_type not in {DocumentType.UNKNOWN}
            and structural_type not in {DocumentType.UNKNOWN}
            and model_type != structural_type
        ):
            effective_document_type = self._resolve_conflict_document_type(
                parser_hint=parser_hint,
                model_type=model_type,
                structural_type=structural_type,
            )
            effective_profile = ChunkingProfile.DEFAULT
            confidence = min(model_confidence, structural_confidence)
            reasons.append(
                "Strong model and structural signals disagreed; default chunking profile selected for safety."
            )
        elif (
            model_type != DocumentType.UNKNOWN
            and self._is_strong(model_confidence, self.strong_model_threshold)
            and (
                structural_type == DocumentType.UNKNOWN
                or self._is_weak(structural_confidence)
            )
        ):
            effective_document_type = model_type
            effective_profile = self._profile_for_document_type(model_type)
            confidence = model_confidence
            reasons.append("Strong model classification overrode weak structural evidence.")
        elif (
            structural_type != DocumentType.UNKNOWN
            and self._is_strong(structural_confidence, self.strong_structural_threshold)
            and (
                model_type == DocumentType.UNKNOWN
                or self._is_weak(model_confidence)
            )
        ):
            effective_document_type = structural_type
            effective_profile = structural_profile
            confidence = structural_confidence
            reasons.append("Strong structural evidence overrode weak model classification.")
        elif model_type != DocumentType.UNKNOWN and model_confidence >= structural_confidence:
            effective_document_type = model_type
            effective_profile = self._profile_for_document_type(model_type)
            confidence = model_confidence
            reasons.append("Model classification chosen as the strongest available signal.")
        elif structural_type != DocumentType.UNKNOWN:
            effective_document_type = structural_type
            effective_profile = structural_profile
            confidence = structural_confidence
            reasons.append("Structural inference chosen as the strongest available signal.")
        elif parser_hint != DocumentType.UNKNOWN:
            effective_document_type = parser_hint
            effective_profile = self._profile_for_document_type(parser_hint)
            confidence = max(model_confidence, structural_confidence)
            reasons.append("Parser/title hint used as the remaining tie-breaker.")
        else:
            effective_document_type = DocumentType.UNKNOWN
            effective_profile = ChunkingProfile.DEFAULT
            confidence = max(model_confidence, structural_confidence)
            reasons.append("No strong document-type signal was available; default profile selected.")

        if parser_hint != DocumentType.UNKNOWN and parser_hint == effective_document_type:
            reasons.append("Parser/title hint aligned with the final document type.")
        if model_type != DocumentType.UNKNOWN and model_type == effective_document_type:
            reasons.append("Saved model classification aligned with the final document type.")
        if structural_type != DocumentType.UNKNOWN and structural_type == effective_document_type:
            reasons.append("Structural profile inference aligned with the final document type.")

        should_rechunk = (
            provisional_chunking_profile is not None
            and provisional_chunking_profile != effective_profile
        )
        if should_rechunk:
            reasons.append(
                f"Chunking profile changed from {provisional_chunking_profile.value} to {effective_profile.value}."
            )

        return DocumentTypeDecision(
            effective_document_type=effective_document_type,
            effective_chunking_profile=effective_profile,
            confidence=round(confidence, 3),
            reasons=reasons,
            should_rechunk=should_rechunk,
        )

    @staticmethod
    def _is_strong(value: float, threshold: float) -> bool:
        return value >= threshold

    def _is_weak(self, value: float) -> bool:
        return value <= self.weak_signal_threshold

    @staticmethod
    def _resolve_conflict_document_type(
        *,
        parser_hint: DocumentType,
        model_type: DocumentType,
        structural_type: DocumentType,
    ) -> DocumentType:
        if parser_hint == model_type:
            return model_type
        if parser_hint == structural_type:
            return structural_type
        return model_type

    @staticmethod
    def _document_type_for_profile(profile: ChunkingProfile) -> DocumentType:
        if profile == ChunkingProfile.MANUAL:
            return DocumentType.MANUAL
        if profile == ChunkingProfile.DATASHEET:
            return DocumentType.DATASHEET
        if profile == ChunkingProfile.DRAWING:
            return DocumentType.DRAWING
        if profile == ChunkingProfile.REPORT:
            return DocumentType.REPORT
        return DocumentType.UNKNOWN

    @staticmethod
    def _profile_for_document_type(document_type: DocumentType) -> ChunkingProfile:
        if document_type == DocumentType.MANUAL:
            return ChunkingProfile.MANUAL
        if document_type == DocumentType.DATASHEET:
            return ChunkingProfile.DATASHEET
        if document_type == DocumentType.DRAWING:
            return ChunkingProfile.DRAWING
        if document_type == DocumentType.REPORT:
            return ChunkingProfile.REPORT
        return ChunkingProfile.DEFAULT
