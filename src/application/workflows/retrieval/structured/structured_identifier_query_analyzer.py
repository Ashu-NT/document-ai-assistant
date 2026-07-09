from __future__ import annotations

from src.application.workflows.shared.identifier_type_markers import (
    IDENTIFIER_TYPE_MARKERS,
)
from src.application.workflows.shared.identifier_value_pattern import (
    contains_identifier_value,
)
from src.domain.common import IdentifierType

_IDENTIFIER_INVENTORY_VERBS = (
    "list",
    "show",
    "display",
    "enumerate",
    "provide",
    "give me",
    "find all",
)


class StructuredIdentifierQueryAnalyzer:
    def looks_like_inventory_query(self, query_text: str | None) -> bool:
        normalized = self._normalized(query_text)
        if not normalized:
            return False
        if contains_identifier_value(normalized):
            return False
        if not any(marker in normalized for marker in _IDENTIFIER_INVENTORY_VERBS):
            return False
        return any(
            marker in normalized
            for markers in IDENTIFIER_TYPE_MARKERS.values()
            for marker in markers
        )

    def requested_identifier_types(
        self,
        query_text: str | None,
    ) -> list[IdentifierType]:
        normalized = self._normalized(query_text)
        requested: list[IdentifierType] = []
        for identifier_type, markers in IDENTIFIER_TYPE_MARKERS.items():
            if any(marker in normalized for marker in markers):
                requested.append(identifier_type)
        return requested

    @staticmethod
    def contains_identifier_value(query_text: str | None) -> bool:
        return contains_identifier_value(query_text)

    @staticmethod
    def _normalized(query_text: str | None) -> str:
        return " ".join((query_text or "").strip().lower().split())
