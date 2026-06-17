class ApplicationError(Exception):
    """Base class for all expected application errors."""

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}