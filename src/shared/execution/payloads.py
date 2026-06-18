from typing import Any


def build_failure_payload(exc: Exception) -> dict[str, Any]:
    return {
        "error_type": exc.__class__.__name__,
        "error_message": str(exc),
    }