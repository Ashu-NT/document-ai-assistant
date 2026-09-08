from __future__ import annotations

import re
from collections import defaultdict

from src.domain.document.entities.chunk import DocumentChunk

_ANNEX_LABEL = r"(\d+(?:\.\d+)*|[A-Za-z])"
_ANNEX_NUMBER_PATTERN = re.compile(
    rf"^\s*(?:\d+(?:\.\d+)*\s+)?annex\s*{_ANNEX_LABEL}\b",
    re.IGNORECASE | re.MULTILINE,
)
_APPENDIX_NUMBER_PATTERN = re.compile(
    rf"^\s*(?:\d+(?:\.\d+)*\s+)?appendix\s*{_ANNEX_LABEL}\b",
    re.IGNORECASE | re.MULTILINE,
)


class ChunkAnnexNumberIndex:
    """Maps each distinct annex/appendix label mentioned in chunk content
    (e.g. "2" from "8.2 Annex 2 Sensors", "B" from "Appendix B") to every
    chunk mentioning it, built once per document so
    `ChunkAnnexReferenceResolver` doesn't re-scan every chunk for each
    detected annex/appendix reference. Unlike `ChunkSectionNumberIndex`,
    this is content-based, not section-hierarchy-based -- annex/appendix
    sub-numbering routinely isn't recognized as its own section heading."""

    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self._chunks_by_label: dict[str, list[DocumentChunk]] = defaultdict(list)

        for chunk in chunks:
            if not chunk.content:
                continue
            seen_labels_for_chunk: set[str] = set()
            for pattern in (_ANNEX_NUMBER_PATTERN, _APPENDIX_NUMBER_PATTERN):
                for match in pattern.finditer(chunk.content):
                    label = match.group(1)
                    if label not in seen_labels_for_chunk:
                        seen_labels_for_chunk.add(label)
                        self._chunks_by_label[label].append(chunk)

    def matches(self, label: str) -> list[DocumentChunk]:
        return list(self._chunks_by_label.get(label, ()))


__all__ = ["ChunkAnnexNumberIndex"]
