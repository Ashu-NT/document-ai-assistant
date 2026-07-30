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

    def _split_duplicate_from_stale(
        self,
        existing_document_id: str | None,
        current_parser_version: str | None,
    ) -> tuple[str | None, str | None]:
        """Returns (duplicate_document_id, stale_document_id).

        A hash match parsed with a different parser version than the one
        running now is neither a true duplicate (do not skip it) nor a
        fresh document (do not orphan the stale row) - the caller is
        expected to redirect it into a reingest of stale_document_id so the
        stale content is replaced in place.
        """
        if existing_document_id is None or current_parser_version is None:
            return existing_document_id, None

        stored_parser_version = (
            self.document_repository.find_parser_version_by_document_id(
                existing_document_id
            )
        )
        if stored_parser_version != current_parser_version:
            return None, existing_document_id
        return existing_document_id, None

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
        current_parser_version: str | None = None,
    ) -> ActionResult:
        existing_document_id = self.document_repository.find_document_id_by_file_hash(
            file_hash
        )
        existing_document_id, stale_document_id = self._split_duplicate_from_stale(
            existing_document_id, current_parser_version
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
                "stale_document_id": stale_document_id,
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
        current_parser_version: str | None = None,
    ) -> ActionResult:
        existing_document_id = (
            self.document_repository.find_document_id_by_content_hash(content_hash)
        )
        existing_document_id, stale_document_id = self._split_duplicate_from_stale(
            existing_document_id, current_parser_version
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
                "stale_document_id": stale_document_id,
                "cache_candidate": True,
            },
        )