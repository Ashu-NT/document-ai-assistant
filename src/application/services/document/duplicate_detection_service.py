from dataclasses import dataclass

from src.application.contracts.document import DocumentRepository
from src.shared.activity import ActivityContext
from src.shared.execution import ActionResult, tracked_action


@dataclass(frozen=True)
class DuplicateDetectionResult:
    is_duplicate: bool
    duplicate_type: str | None = None
    existing_document_id: str | None = None


class DuplicateDetectionService:
    def __init__(self, document_repository: DocumentRepository) -> None:
        self.document_repository = document_repository

    @tracked_action(
        action="document.duplicate_check",
        entity_type="document",
        activity=True,
        audit=False,
        event=True,
    )
    def check_file_hash(
        self,
        file_hash: str,
        activity_context: ActivityContext | None = None,
    ) -> ActionResult:
        existing_document_id = self.document_repository.find_document_id_by_file_hash(
            file_hash
        )

        result = DuplicateDetectionResult(
            is_duplicate=existing_document_id is not None,
            duplicate_type="file_hash" if existing_document_id else None,
            existing_document_id=existing_document_id,
        )

        return ActionResult(
            entity_type="document",
            entity_id=existing_document_id,
            message="File duplicate check completed.",
            payload={
                "is_duplicate": result.is_duplicate,
                "duplicate_type": result.duplicate_type,
                "existing_document_id": result.existing_document_id,
                "cache_candidate": True,
            },
        )

    @tracked_action(
        action="document.content_duplicate_check",
        entity_type="document",
        activity=True,
        audit=False,
        event=True,
    )
    def check_content_hash(
        self,
        content_hash: str,
        activity_context: ActivityContext | None = None,
    ) -> ActionResult:
        existing_document_id = (
            self.document_repository.find_document_id_by_content_hash(content_hash)
        )

        result = DuplicateDetectionResult(
            is_duplicate=existing_document_id is not None,
            duplicate_type="content_hash" if existing_document_id else None,
            existing_document_id=existing_document_id,
        )

        return ActionResult(
            entity_type="document",
            entity_id=existing_document_id,
            message="Content duplicate check completed.",
            payload={
                "is_duplicate": result.is_duplicate,
                "duplicate_type": result.duplicate_type,
                "existing_document_id": result.existing_document_id,
                "cache_candidate": True,
            },
        )