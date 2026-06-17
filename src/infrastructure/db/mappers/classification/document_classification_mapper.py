from src.domain.classification import ClassificationResult, DocumentClassification
from src.domain.common import DocumentType
from src.infrastructure.db.mappers.classification.classification_result_mapper import (
    ClassificationResultMapper,
)
from src.infrastructure.db.orm_models import DocumentClassificationORM


class DocumentClassificationMapper:
    @staticmethod
    def to_orm(classification: DocumentClassification) -> DocumentClassificationORM:
        result = classification.result or ClassificationResult(
            classification_id=f"classification_{classification.document_id}",
            document_id=classification.document_id,
            predicted_label=classification.document_type.value,
            confidence_score=None,
        )

        common = ClassificationResultMapper.extract_common_fields(result)

        return DocumentClassificationORM(
            id=result.classification_id,
            document_id=classification.document_id,
            document_type=classification.document_type.value,
            **common,
        )

    @staticmethod
    def to_domain(orm: DocumentClassificationORM) -> DocumentClassification:
        result = ClassificationResultMapper.from_orm_fields(
            classification_id=orm.id,
            document_id=orm.document_id,
            predicted_label=orm.predicted_label,
            confidence_score=orm.confidence_score,
            rationale=orm.rationale,
            evidence_json=orm.evidence_json,
            model_name=orm.model_name,
            model_type=orm.model_type,
            prompt_version=orm.prompt_version,
        )

        return DocumentClassification(
            document_id=orm.document_id,
            document_type=DocumentType(orm.document_type),
            result=result,
        )