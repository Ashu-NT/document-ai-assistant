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


class DocumentNotFoundForReingestionError(IngestionWorkflowError):
    """Raised when a reingestion request targets a document that does not exist."""


class DocumentNotFoundForDeletionError(IngestionWorkflowError):
    """Raised when a delete request targets a document that does not exist."""


class StaleParserVersionDetected(IngestionWorkflowError):
    """Raised internally when a content-hash duplicate was parsed with an
    older parser version. Signals IngestionWorkflow.run() to redirect into
    reingest() for that document instead of treating this as a duplicate
    (which would skip it) or a fresh document (which would orphan the
    stale row). Callers should catch this and call reingest(), not treat
    it as a failure.
    """
