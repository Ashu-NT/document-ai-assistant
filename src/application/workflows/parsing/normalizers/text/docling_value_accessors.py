from typing import Any

from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)


def get_value(value: Any, name: str) -> Any:
    if value is None:
        return None

    if isinstance(value, dict):
        return value.get(name)

    return getattr(value, name, None)


def clean_text(value: Any) -> str | None:
    if value is None:
        return None

    text = repair_docling_text(str(value)).strip()
    return text or None
