from __future__ import annotations

import re

from src.domain.common.enums import IdentifierType
from src.domain.common.value_objects import normalize_identifier
from src.domain.document import DocumentGraph
from src.domain.document.entities.identifier import Identifier
from src.shared.ids import IdGenerator, IdPrefix

_DRAWING_RE = re.compile(r"\b(?:DRG|DWG)[-\s]?\d{3,}\b", re.IGNORECASE)
_CERT_RE = re.compile(r"\b(?:CERT|ISO|EN|IEC|ATEX)\s*[-\s]?\d{3,}\b", re.IGNORECASE)

_PATTERNS: tuple[tuple[re.Pattern[str], IdentifierType], ...] = (
    (_DRAWING_RE, IdentifierType.DRAWING_NUMBER),
    (_CERT_RE, IdentifierType.COMPONENT_CODE),
)


class DeterministicIdentifierScanner:
    """Regex-based scanner that promotes drawing/certificate identifiers found in chunk content."""

    def scan(
        self,
        document_graph: DocumentGraph,
        id_generator: IdGenerator,
        *,
        existing_normalized: set[tuple[str, str]] | None = None,
    ) -> list[Identifier]:
        seen: set[tuple[str, str]] = set(existing_normalized or [])
        identifiers: list[Identifier] = []
        document_id = document_graph.document.document_id

        for chunk in document_graph.chunks.values():
            for pattern, identifier_type in _PATTERNS:
                for match in pattern.finditer(chunk.content):
                    raw = match.group(0).strip()
                    normalized = normalize_identifier(raw)
                    if not normalized:
                        continue
                    key = (normalized, identifier_type.value)
                    if key in seen:
                        continue
                    seen.add(key)
                    identifiers.append(
                        Identifier(
                            identifier_id=id_generator.new_id(IdPrefix.IDENTIFIER),
                            document_id=document_id,
                            raw_value=raw,
                            identifier_type=identifier_type,
                            chunk_id=chunk.chunk_id,
                            section_id=chunk.section_id,
                            page_start=chunk.source.page_start,
                            page_end=chunk.source.page_end,
                        )
                    )

        return identifiers
