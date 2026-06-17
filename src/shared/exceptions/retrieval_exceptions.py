from src.shared.exceptions.base import ApplicationError


class RetrievalError(ApplicationError):
    """Base class for retrieval errors."""


class NoEvidenceFoundError(RetrievalError):
    """Raised when retrieval finds no usable evidence."""


class CitationError(RetrievalError):
    """Raised when citation validation fails."""