from __future__ import annotations

from src.application.services.document import DuplicateDetectionService
from src.application.workflows.ingestion.models.ingestion_request import IngestionRequest


class DuplicateCheckStep:
    """Checks an ingestion request's file-hash/content-hash against already
    registered documents, honoring the request's `force` flag and the
    `duplicate_detection_settings` feature toggles.
    """

    def __init__(self, *, duplicate_detection_service: DuplicateDetectionService) -> None:
        self.duplicate_detection_service = duplicate_detection_service

    def check_file_hash_duplicate(
        self,
        *,
        request: IngestionRequest,
        file_hash: str,
        activity_context,
    ) -> str | None:
        from src.config.settings import duplicate_detection_settings

        if request.force:
            return None

        if not duplicate_detection_settings.enable_file_hash_check:
            return None

        result = self.duplicate_detection_service.check_file_hash(
            file_hash,
            activity_context=activity_context,
        )
        return result.payload.get("existing_document_id")

    def check_content_hash_duplicate(
        self,
        *,
        request: IngestionRequest,
        content_hash: str,
        activity_context,
    ) -> str | None:
        from src.config.settings import duplicate_detection_settings

        if request.force:
            return None

        if not duplicate_detection_settings.enable_content_hash_check:
            return None

        result = self.duplicate_detection_service.check_content_hash(
            content_hash,
            activity_context=activity_context,
        )
        return result.payload.get("existing_document_id")
