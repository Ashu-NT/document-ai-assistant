from src.shared.exceptions.base import ApplicationError


class DomainError(ApplicationError):
    """Raised when a domain invariant is violated."""


class InvalidDocumentGraphError(DomainError):
    """Raised when the document graph is inconsistent."""


class InvalidIdentifierError(DomainError):
    """Raised when an identifier is invalid."""