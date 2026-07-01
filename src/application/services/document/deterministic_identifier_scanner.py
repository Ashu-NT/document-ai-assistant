from __future__ import annotations

import re

from src.domain.common.enums import IdentifierType
from src.domain.common.value_objects import normalize_identifier
from src.domain.document import DocumentGraph
from src.domain.document.entities.identifier import Identifier
from src.shared.ids import IdGenerator, IdPrefix

_DRAWING_RE = re.compile(r"\b(?:DRG|DWG)[-\s]?\d{3,}\b", re.IGNORECASE)
_CERT_RE = re.compile(r"\b(?:CERT|ISO|EN|IEC|ATEX)\s*[-\s]?\d{3,}\b", re.IGNORECASE)
_SERIAL_RE = re.compile(r"\bSN-\d{3,}[A-Z0-9-]*\b", re.IGNORECASE)
_GENERIC_PART_RE = re.compile(r"\b[A-Z]{2,5}-\d{2,6}[A-Z0-9-]*\b")

# Specific patterns run first and claim their values exclusively.
_SPECIFIC_PATTERNS: tuple[tuple[re.Pattern[str], IdentifierType], ...] = (
    (_DRAWING_RE, IdentifierType.DRAWING_NUMBER),
    (_CERT_RE, IdentifierType.CERTIFICATE_NUMBER),
    (_SERIAL_RE, IdentifierType.SERIAL_NUMBER),
)

# Generic patterns run second and only match values not claimed by specific patterns.
_GENERIC_PATTERNS: tuple[tuple[re.Pattern[str], IdentifierType], ...] = (
    (_GENERIC_PART_RE, IdentifierType.PART_NUMBER),
)


class DeterministicIdentifierScanner:
    """Regex-based scanner that promotes identifiers found in chunk text.

    Runs in two passes to prevent double-classification: specific patterns
    (drawing, certificate, serial) run first and exclusively own their matches;
    the generic part number pattern only fires for values not already claimed.
    """

    def scan(
        self,
        document_graph: DocumentGraph,
        id_generator: IdGenerator,
        *,
        existing_normalized: set[tuple[str, str]] | None = None,
    ) -> list[Identifier]:
        seen: set[tuple[str, str]] = set(existing_normalized or [])
        claimed_values: set[str] = {norm for norm, _ in (existing_normalized or set())}
        identifiers: list[Identifier] = []
        document_id = document_graph.document.document_id

        # Pass 1: specific patterns — claim values exclusively.
        for chunk in document_graph.chunks.values():
            for pattern, identifier_type in _SPECIFIC_PATTERNS:
                for match in pattern.finditer(chunk.content):
                    raw = match.group(0).strip()
                    normalized = normalize_identifier(raw)
                    if not normalized:
                        continue
                    claimed_values.add(normalized)
                    key = (normalized, identifier_type.value)
                    if key in seen:
                        continue
                    seen.add(key)
                    identifiers.append(
                        self._make_identifier(
                            document_id=document_id,
                            raw=raw,
                            identifier_type=identifier_type,
                            chunk=chunk,
                            id_generator=id_generator,
                        )
                    )

        # Pass 2: generic patterns — skip values already claimed above.
        for chunk in document_graph.chunks.values():
            for pattern, identifier_type in _GENERIC_PATTERNS:
                for match in pattern.finditer(chunk.content):
                    raw = match.group(0).strip()
                    normalized = normalize_identifier(raw)
                    if not normalized or normalized in claimed_values:
                        continue
                    claimed_values.add(normalized)
                    key = (normalized, identifier_type.value)
                    if key in seen:
                        continue
                    seen.add(key)
                    identifiers.append(
                        self._make_identifier(
                            document_id=document_id,
                            raw=raw,
                            identifier_type=identifier_type,
                            chunk=chunk,
                            id_generator=id_generator,
                        )
                    )

        return identifiers

    @staticmethod
    def _make_identifier(
        *,
        document_id: str,
        raw: str,
        identifier_type: IdentifierType,
        chunk,
        id_generator: IdGenerator,
    ) -> Identifier:
        return Identifier(
            identifier_id=id_generator.new_id(IdPrefix.IDENTIFIER),
            document_id=document_id,
            raw_value=raw,
            identifier_type=identifier_type,
            chunk_id=chunk.chunk_id,
            section_id=chunk.section_id,
            page_start=chunk.source.page_start,
            page_end=chunk.source.page_end,
        )
