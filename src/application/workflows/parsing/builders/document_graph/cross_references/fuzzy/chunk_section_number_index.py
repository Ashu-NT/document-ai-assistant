from __future__ import annotations

import re
from collections import defaultdict

from src.domain.document.entities.chunk import DocumentChunk

_LEADING_SECTION_NUMBER_PATTERN = re.compile(r"^(\d+(?:\.\d+)*)\b")


def extract_leading_section_number(section_path_part: str) -> str | None:
    match = _LEADING_SECTION_NUMBER_PATTERN.match(section_path_part.strip())
    return match.group(1) if match else None


class ChunkSectionNumberIndex:
    """Maps each distinct numbered section-path prefix (e.g. "6.7.1",
    extracted from a section title like "6.7.1 Lubrication oil") to every
    chunk under that section, built once per document so
    `ChunkSectionReferenceResolver` doesn't re-scan every chunk for each
    detected section reference in the document."""

    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self._chunks_by_label: dict[str, list[DocumentChunk]] = defaultdict(list)

        for chunk in chunks:
            seen_labels_for_chunk: set[str] = set()
            for part in chunk.section_path:
                label = extract_leading_section_number(part)
                if label and label not in seen_labels_for_chunk:
                    seen_labels_for_chunk.add(label)
                    self._chunks_by_label[label].append(chunk)

    def exact_match(self, label: str) -> list[DocumentChunk]:
        return list(self._chunks_by_label.get(label, ()))

    def descendant_matches(self, label: str) -> list[DocumentChunk]:
        prefix = f"{label}."
        seen_chunk_ids: set[str] = set()
        descendants: list[DocumentChunk] = []

        for candidate_label, chunks in self._chunks_by_label.items():
            if not candidate_label.startswith(prefix):
                continue
            for chunk in chunks:
                if chunk.chunk_id in seen_chunk_ids:
                    continue
                seen_chunk_ids.add(chunk.chunk_id)
                descendants.append(chunk)

        return descendants


__all__ = ["ChunkSectionNumberIndex", "extract_leading_section_number"]
