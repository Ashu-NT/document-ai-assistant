from __future__ import annotations

from dataclasses import dataclass

from src.application.services.document import DuplicateDetectionService
from src.application.workflows.ingestion.models.ingestion_request import IngestionRequest


@dataclass(frozen=True)
class DuplicateCheckOutcome:
    duplicate_document_id: str | None = None
    stale_document_id: str | None = None


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
        current_parser_version: str | None = None,
    ) -> DuplicateCheckOutcome:
        from src.config.settings import duplicate_detection_settings

        if request.force:
            return DuplicateCheckOutcome()

        if not duplicate_detection_settings.enable_file_hash_check:
            return DuplicateCheckOutcome()

        result = self.duplicate_detection_service.check_file_hash(
            file_hash,
            activity_context=activity_context,
            current_parser_version=current_parser_version,
        )
        return DuplicateCheckOutcome(
            duplicate_document_id=result.payload.get("existing_document_id"),
            stale_document_id=result.payload.get("stale_document_id"),
        )

    def check_content_hash_duplicate(
        self,
        *,
        request: IngestionRequest,
        content_hash: str,
        activity_context,
        current_parser_version: str | None = None,
    ) -> DuplicateCheckOutcome:
        from src.config.settings import duplicate_detection_settings

        if request.force:
            return DuplicateCheckOutcome()

        if not duplicate_detection_settings.enable_content_hash_check:
            return DuplicateCheckOutcome()

        result = self.duplicate_detection_service.check_content_hash(
            content_hash,
            activity_context=activity_context,
            current_parser_version=current_parser_version,
        )
        return DuplicateCheckOutcome(
            duplicate_document_id=result.payload.get("existing_document_id"),
            stale_document_id=result.payload.get("stale_document_id"),
        )
