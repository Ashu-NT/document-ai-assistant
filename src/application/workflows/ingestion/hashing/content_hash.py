from __future__ import annotations

import hashlib
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.document.aggregates.document_graph import DocumentGraph


def _normalize_text(text: str | None) -> str:
    if not text:
        return ""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def compute_content_hash_from_graph(document_graph: "DocumentGraph") -> str:
    """Stable SHA-256 hash over normalized element content in reading order.

    Excludes volatile fields: generated IDs, timestamps, file path, parser metadata.
    Includes: element type, normalized text, page start.
    """
    parts: list[str] = []
    elements = sorted(
        document_graph.elements.values(),
        key=lambda e: (e.reading_order or 0),
    )
    for element in elements:
        element_type = (
            element.element_type.value
            if hasattr(element.element_type, "value")
            else str(element.element_type)
        )
        text = _normalize_text(element.text)
        page = str(element.source.page_start) if element.source and element.source.page_start is not None else ""
        parts.append(f"{element_type}\t{page}\t{text}")

    combined = "\n".join(parts)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()
