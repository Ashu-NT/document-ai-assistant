from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RawParsedDocument:
    file_path: str
    title: str | None
    page_count: int | None
    raw_document: Any
    parser_name: str
    parser_version: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
