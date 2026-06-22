import re

from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    GENERIC_STRUCTURED_MARKERS,
)


class StructuredSignalDetector:
    def __init__(
        self,
        *,
        markers: tuple[str, ...] | None = None,
    ) -> None:
        self.markers = markers or GENERIC_STRUCTURED_MARKERS

    def has_structured_markers(
        self,
        *,
        document_title: str | None,
        values: list[str],
    ) -> bool:
        haystacks = [
            self._normalize(value)
            for value in values
            if self._normalize(value)
        ]
        return any(
            marker in haystack
            for marker in self.markers
            for haystack in haystacks
        )

    @staticmethod
    def _normalize(value: str | None) -> str:
        normalized = re.sub(r"[\W_]+", " ", str(value or ""), flags=re.UNICODE)
        return " ".join(normalized.strip().lower().split())
