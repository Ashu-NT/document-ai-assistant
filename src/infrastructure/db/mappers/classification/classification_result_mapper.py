import json

from src.domain.classification import ClassificationResult
from src.domain.common import ModelProcessingMetadata


class ClassificationResultMapper:
    @staticmethod
    def extract_common_fields(result: ClassificationResult) -> dict:
        metadata = result.processing_metadata

        return {
            "predicted_label": result.predicted_label,
            "confidence_score": result.confidence_score,
            "rationale": result.rationale,
            "evidence_json": json.dumps(result.evidence),
            "model_name": metadata.model_name if metadata else None,
            "model_type": metadata.model_type if metadata else None,
            "prompt_version": metadata.prompt_version if metadata else None,
            "created_at": result.audit.created_at,
        }

    @staticmethod
    def from_orm_fields(
        *,
        classification_id: str,
        document_id: str,
        predicted_label: str,
        confidence_score: float | None,
        rationale: str | None,
        evidence_json: str | None,
        model_name: str | None,
        model_type: str | None,
        prompt_version: str | None,
    ) -> ClassificationResult:
        processing_metadata = None

        if model_name or model_type or prompt_version:
            processing_metadata = ModelProcessingMetadata(
                model_name=model_name or "unknown",
                model_type=model_type or "classification",
                confidence=confidence_score,
                prompt_version=prompt_version,
            )

        return ClassificationResult(
            classification_id=classification_id,
            document_id=document_id,
            predicted_label=predicted_label,
            confidence_score=confidence_score,
            rationale=rationale,
            evidence=json.loads(evidence_json or "[]"),
            processing_metadata=processing_metadata,
        )