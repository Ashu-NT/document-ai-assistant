from src.shared.exceptions.base import ApplicationError


class IngestionError(ApplicationError):
    """Base class for ingestion errors."""


class FileHashError(IngestionError):
    """Raised when file hashing fails."""


class DocumentParsingError(IngestionError):
    """Raised when PDF parsing fails."""


class DocumentParsingTimeoutError(DocumentParsingError):
    """Raised when PDF parsing exceeds the configured timeout."""


class DocumentNormalizationError(IngestionError):
    """Raised when normalization fails."""


class ChunkingError(IngestionError):
    """Raised when chunking fails."""