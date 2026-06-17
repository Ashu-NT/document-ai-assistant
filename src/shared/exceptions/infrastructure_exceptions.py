from src.shared.exceptions.base import ApplicationError


class InfrastructureError(ApplicationError):
    """Base class for infrastructure errors."""


class DatabaseError(InfrastructureError):
    """Raised for database operation failures."""


class VectorStoreError(InfrastructureError):
    """Raised for vector database failures."""


class LLMProviderError(InfrastructureError):
    """Raised for LLM provider failures."""


class OCRProviderError(InfrastructureError):
    """Raised for OCR provider failures."""