from src.shared.exceptions import IngestionError


class IngestionWorkflowError(IngestionError):
    """Raised when a document ingestion workflow fails unexpectedly."""


class IngestionDependencyError(IngestionWorkflowError):
    """Raised when an ingestion dependency is unavailable or misconfigured."""


class IngestionStorageError(IngestionWorkflowError):
    """Raised when ingestion storage orchestration cannot complete safely."""


class IngestionIndexingError(IngestionWorkflowError):
    """Raised when ingestion vector indexing cannot complete safely."""


class ReingestionNotSupportedError(IngestionWorkflowError):
    """Raised when safe reingestion is not supported by the current repo."""


class DeleteDocumentNotSupportedError(IngestionWorkflowError):
    """Raised when safe document deletion is not supported by the current repo."""
