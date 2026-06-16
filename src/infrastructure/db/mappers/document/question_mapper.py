from src.domain.common import ModelProcessingMetadata
from src.domain.document.entities import GeneratedQuestion
from src.infrastructure.db.orm_models import GeneratedQuestionORM


class GeneratedQuestionMapper:
    @staticmethod
    def to_orm(question: GeneratedQuestion) -> GeneratedQuestionORM:
        return GeneratedQuestionORM(
            id=question.question_id,
            document_id=question.document_id,
            chunk_id=question.chunk_id,
            question=question.question,
            is_active=question.is_active,
            model_name=(
                question.processing_metadata.model_name
                if question.processing_metadata
                else None
            ),
            confidence_score=(
                question.processing_metadata.confidence
                if question.processing_metadata
                else None
            ),
            created_at=question.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: GeneratedQuestionORM) -> GeneratedQuestion:
        processing_metadata = None

        if orm.model_name or orm.confidence_score is not None:
            processing_metadata = ModelProcessingMetadata(
                model_name=orm.model_name or "unknown",
                model_type="question_generation",
                confidence=orm.confidence_score,
            )

        return GeneratedQuestion(
            question_id=orm.id,
            document_id=orm.document_id,
            chunk_id=orm.chunk_id,
            question=orm.question,
            is_active=orm.is_active,
            processing_metadata=processing_metadata,
        )