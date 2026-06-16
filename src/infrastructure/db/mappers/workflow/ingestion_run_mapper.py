from src.domain.common import IngestionStatus
from src.domain.workflows import IngestionRun
from src.infrastructure.db.orm_models import IngestionRunORM


class IngestionRunMapper:
    @staticmethod
    def to_orm(run: IngestionRun) -> IngestionRunORM:
        return IngestionRunORM(
            id=run.run_id,
            document_id=run.document_id,
            file_path=run.file_path,
            file_hash=run.file_hash,
            content_hash=run.content_hash,
            status=run.status.value,
            started_at=run.started_at,
            finished_at=run.finished_at,
            error_message=run.error_message,
            parser_name=run.parser_name,
            parser_version=run.parser_version,
            embedding_model=run.embedding_model,
            classification_model=run.classification_model,
            question_generation_model=run.question_generation_model,
            extraction_model=run.extraction_model,
            created_at=run.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: IngestionRunORM) -> IngestionRun:
        return IngestionRun(
            run_id=orm.id,
            document_id=orm.document_id,
            file_path=orm.file_path,
            file_hash=orm.file_hash,
            content_hash=orm.content_hash,
            status=IngestionStatus(orm.status),
            started_at=orm.started_at,
            finished_at=orm.finished_at,
            error_message=orm.error_message,
            parser_name=orm.parser_name,
            parser_version=orm.parser_version,
            embedding_model=orm.embedding_model,
            classification_model=orm.classification_model,
            question_generation_model=orm.question_generation_model,
            extraction_model=orm.extraction_model,
        )