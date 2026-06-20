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

        if (
            self._is_known_type(model_type)
            and self._is_known_type(structural_type)
            and model_type == structural_type
        ):
            effective_document_type = model_type
            effective_profile = self._profile_for_document_type(model_type)
            confidence = self._agreement_confidence(
                model_confidence=model_confidence,
                structural_confidence=structural_confidence,
            )
            reasons.append(
                "Model classification and structural inference agreed on the same document type."
            )
        elif (
            self._is_known_type(model_type)
            and self._is_known_type(structural_type)
            and model_type != structural_type
            and self._is_strong(model_confidence, self.strong_model_threshold)
            and self._is_strong(
                structural_confidence,
                self.strong_structural_threshold,
            )
        ):
            effective_document_type = model_type
            effective_profile = self._profile_for_document_type(model_type)
            confidence = model_confidence
            reasons.append(
                "Model classification and structural inference conflicted at high confidence; model classification was selected."
            )
            reasons.append(
                "Conflict flagged: strong structural evidence disagreed with the selected model classification."
            )
        elif (
            self._is_known_type(model_type)
            and self._is_known_type(structural_type)
            and model_type != structural_type
            and self._is_strong(model_confidence, self.strong_model_threshold)
        ):
            effective_document_type = model_type
            effective_profile = self._profile_for_document_type(model_type)
            confidence = model_confidence
            reasons.append(
                "High-confidence model classification overrode a different structural inference."
            )
        elif structural_type != DocumentType.UNKNOWN:
            if (
                self._is_known_type(structural_type)
                and self._is_strong(
                    structural_confidence,
                    self.strong_structural_threshold,
                )
                and (
                    not self._is_known_type(model_type)
                    or self._is_weak(model_confidence)
                )
            ):
                effective_document_type = structural_type
                effective_profile = structural_profile
                confidence = structural_confidence
                reasons.append(
                    "High-confidence structural inference overrode a missing or low-confidence model classification."
                )
            elif (
                self._is_known_type(model_type)
                and self._is_known_type(structural_type)
                and model_type != structural_type
                and self._is_weak(model_confidence)
                and self._is_weak(structural_confidence)
            ):
                effective_document_type = DocumentType.UNKNOWN
                effective_profile = ChunkingProfile.DEFAULT
                confidence = max(model_confidence, structural_confidence)
                reasons.append(
                    "Model classification and structural inference disagreed at low confidence; default profile selected."
                )
            elif (
                self._is_known_type(model_type)
                and self._is_known_type(structural_type)
                and model_type != structural_type
            ):
                effective_document_type = DocumentType.UNKNOWN
                effective_profile = ChunkingProfile.DEFAULT
                confidence = max(model_confidence, structural_confidence)
                reasons.append(
                    "Model classification and structural inference disagreed without a decisive high-confidence winner; default profile selected."
                )
            else:
                effective_document_type = DocumentType.UNKNOWN
                effective_profile = ChunkingProfile.DEFAULT
                confidence = max(model_confidence, structural_confidence)
                reasons.append(
                    "Structural inference was available but not at decisive high confidence; default profile selected."
                )
        elif (
            self._is_known_type(model_type)
            and self._is_strong(model_confidence, self.strong_model_threshold)
        ):
            effective_document_type = model_type
            effective_profile = self._profile_for_document_type(model_type)
            confidence = model_confidence
            reasons.append(
                "Available high-confidence model classification was used because no competing structural signal was available."
            )
        else:
            effective_document_type = DocumentType.UNKNOWN
            effective_profile = ChunkingProfile.DEFAULT
            confidence = max(model_confidence, structural_confidence)
            if parser_title_hint not in {None, DocumentType.UNKNOWN}:
                reasons.append(
                    "Parser/title hint was available but not used because no decisive high-confidence signal was present."
                )
            reasons.append(
                "No decisive high-confidence document-type signal was available; default profile selected."
            )

        if (
            parser_title_hint not in {None, DocumentType.UNKNOWN}
            and parser_title_hint == effective_document_type
        ):
            reasons.append("Parser/title hint aligned with the final document type.")
        if self._is_known_type(model_type) and model_type == effective_document_type:
            reasons.append("Saved model classification aligned with the final document type.")
        if (
            self._is_known_type(structural_type)
            and structural_type == effective_document_type
        ):
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
    def _is_known_type(document_type: DocumentType) -> bool:
        return document_type != DocumentType.UNKNOWN

    @staticmethod
    def _is_strong(value: float, threshold: float) -> bool:
        return value >= threshold

    def _is_weak(self, value: float) -> bool:
        return value <= self.weak_signal_threshold

    @staticmethod
    def _agreement_confidence(
        *,
        model_confidence: float,
        structural_confidence: float,
    ) -> float:
        higher_confidence = max(model_confidence, structural_confidence)
        lower_confidence = min(model_confidence, structural_confidence)
        boost = (1 - higher_confidence) * lower_confidence * 0.35
        return min(0.99, higher_confidence + boost)

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
