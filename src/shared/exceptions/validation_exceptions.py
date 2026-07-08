from src.shared.exceptions.base import ApplicationError


class ValidationError(ApplicationError):
    """Base class for validation errors."""


class SchemaValidationError(ValidationError):
    """Raised when structured data fails schema validation."""