from src.shared.exceptions import ApplicationError


class GraphError(ApplicationError):
    """Raised when the LangGraph application layer cannot proceed safely."""
