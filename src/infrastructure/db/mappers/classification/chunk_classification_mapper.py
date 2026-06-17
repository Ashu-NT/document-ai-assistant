from src.domain.classification import ChunkClassification, ClassificationResult
from src.domain.common import ChunkType
from src.infrastructure.db.mappers.classification.classification_result_mapper import (
    ClassificationResultMapper,
)
from src.infrastructure.db.orm_models import ChunkClassificationORM


class ChunkClassificationMapper:
    @staticmethod
    def to_orm(classification: ChunkClassification) -> ChunkClassificationORM:
        result = classification.result or ClassificationResult(
            classification_id=f"classification_{classification.chunk_id}",
            document_id=classification.document_id,
            predicted_label=classification.chunk_type.value,
            confidence_score=None,
        )

        common = ClassificationResultMapper.extract_common_fields(result)

        return ChunkClassificationORM(
            id=result.classification_id,
            chunk_id=classification.chunk_id,
            document_id=classification.document_id,
            chunk_type=classification.chunk_type.value,
            **common,
        )

    @staticmethod
    def to_domain(orm: ChunkClassificationORM) -> ChunkClassification:
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

        return ChunkClassification(
            chunk_id=orm.chunk_id,
            document_id=orm.document_id,
            chunk_type=ChunkType(orm.chunk_type),
            result=result,
        )