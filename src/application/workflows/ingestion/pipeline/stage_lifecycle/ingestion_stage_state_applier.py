from __future__ import annotations

from src.domain.workflow import IngestionRun


class IngestionStageStateApplier:
    @staticmethod
    def apply_parsing(
        ingestion_run: IngestionRun,
        parsing_stage_result,
    ) -> str:
        parsing_result = parsing_stage_result.parsing_result
        ingestion_run.document_id = parsing_result.document_id
        ingestion_run.parser_name = parsing_stage_result.parser_name
        ingestion_run.parser_version = parsing_stage_result.parser_version
        ingestion_run.content_hash = parsing_stage_result.content_hash
        return parsing_stage_result.content_hash

    @staticmethod
    def apply_classification(
        ingestion_run: IngestionRun,
        classification_stage_result,
    ) -> None:
        ingestion_run.classification_model = (
            classification_stage_result.classification_model
        )

    @staticmethod
    def apply_finalization(
        ingestion_run: IngestionRun,
        *,
        finalization_stage_result,
        extraction_enabled: bool,
        extraction_model: str | None,
    ) -> None:
        ingestion_run.question_generation_model = (
            finalization_stage_result.question_generation_model
        )
        ingestion_run.extraction_model = (
            extraction_model if extraction_enabled else None
        )

    @staticmethod
    def apply_embedding(
        ingestion_run: IngestionRun,
        vector_stage_result,
    ) -> None:
        ingestion_run.embedding_model = vector_stage_result.embedding_model
