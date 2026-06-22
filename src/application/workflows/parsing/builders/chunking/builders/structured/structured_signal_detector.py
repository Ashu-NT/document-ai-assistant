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
        title = self._normalize(document_title)
        if any(marker in title for marker in self.markers):
            return True

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
        return " ".join(str(value or "").strip().lower().split())
