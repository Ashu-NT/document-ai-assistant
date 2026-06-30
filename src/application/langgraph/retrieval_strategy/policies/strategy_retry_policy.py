from __future__ import annotations

from dataclasses import dataclass

from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)


@dataclass(slots=True)
class StrategyRetryPolicy:
    def recommend(
        self,
        *,
        retry_reason: str | None,
        retry_query: str | None,
        initial_primary_strategy: RetrievalStrategy | None,
    ) -> list[RetrievalStrategy]:
        haystack = " ".join(
            value.strip().lower()
            for value in (retry_reason or "", retry_query or "")
            if value and value.strip()
        )
        if any(marker in haystack for marker in ("table", "schedule", "matrix", "row", "column")):
            return [
                RetrievalStrategy.TABLE_LOOKUP,
                RetrievalStrategy.MAINTENANCE_LOOKUP,
            ]
        if any(
            marker in haystack
            for marker in ("identifier", "part number", "serial number", "model", "drawing number")
        ):
            return [
                RetrievalStrategy.IDENTIFIER_LOOKUP,
                RetrievalStrategy.GENERAL_HYBRID,
            ]
        if any(marker in haystack for marker in ("maintenance", "interval", "service", "inspection")):
            return [
                RetrievalStrategy.MAINTENANCE_LOOKUP,
                RetrievalStrategy.TABLE_LOOKUP,
            ]
        if any(marker in haystack for marker in ("procedure", "steps", "install", "replace")):
            return [RetrievalStrategy.PROCEDURE_LOOKUP]
        if any(marker in haystack for marker in ("fault", "error", "alarm", "remedy")):
            return [RetrievalStrategy.TROUBLESHOOTING_LOOKUP]
        if any(marker in haystack for marker in ("drawing", "figure", "diagram", "schematic")):
            return [RetrievalStrategy.DRAWING_LOOKUP]
        if initial_primary_strategy is not None:
            return [initial_primary_strategy]
        return [RetrievalStrategy.GENERAL_HYBRID]
