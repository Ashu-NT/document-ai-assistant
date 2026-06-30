from __future__ import annotations

import re

from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategySignal,
)
from src.domain.common import ChunkType

_IDENTIFIER_PATTERN = re.compile(
    r"\b([A-Z]{1,5}\d{1,6}[A-Z0-9-]*|\d{3,}[A-Z0-9-]+|DN\s*\d+)\b",
    re.IGNORECASE,
)
_IDENTIFIER_TERMS = (
    "part no",
    "part number",
    "serial number",
    "model",
    "order code",
    "tag",
    "certificate number",
    "drawing number",
    "id ",
)
_SPECIFICATION_TERMS = (
    "specification",
    "specs",
    "technical data",
    "pressure",
    "test pressure",
    "design pressure",
    "temperature",
    "voltage",
    "power",
    "capacity",
    "rating",
    "weight",
    "dimension",
    "material",
    "dn",
    "bar",
    "kw",
    " v",
    " a",
    "mm",
)
_MAINTENANCE_TERMS = (
    "maintenance",
    "service",
    "inspection",
    "interval",
    "operating hours",
    "lubrication",
    "oil change",
    "replace filter",
    "preventive maintenance",
    "schedule",
    "daily",
    "weekly",
    "monthly",
    "quarterly",
    "annually",
)
_PROCEDURE_TERMS = (
    "how to",
    "procedure",
    "steps",
    "install",
    "remove",
    "replace",
    "start",
    "stop",
    "operate",
    "commission",
    "dismantle",
    "assemble",
    "configure",
)
_TROUBLESHOOTING_TERMS = (
    "fault",
    "alarm",
    "error",
    "cause",
    "remedy",
    "problem",
    "troubleshoot",
    "failure",
    "symptom",
)
_CERTIFICATION_TERMS = (
    "certificate",
    "certification",
    "inspection",
    "approval",
    "lr",
    "atex",
    "iecex",
    "surveyor",
    "issued",
    "compliance",
    "valid",
)
_DRAWING_TERMS = (
    "drawing",
    "diagram",
    "schematic",
    "layout",
    "dimensions",
    "view",
)
_FIGURE_TERMS = ("figure", "fig.", "image", "picture")
_TABLE_TERMS = ("table", "list", "schedule", "matrix", "row", "column", "values", "data table")
_SECTION_TERMS = ("section", "page", "heading", "chapter", "appendix", "path")


class RetrievalSignalExtractor:
    def extract(self, context: RetrievalContext) -> list[RetrievalStrategySignal]:
        query_text = (
            context.analyzed_query.effective_query()
            if context.analyzed_query is not None
            else context.query_text
        ).lower()
        signals: list[RetrievalStrategySignal] = []
        self._append_keyword_signals(signals, query_text)
        self._append_identifier_signals(signals, context)
        self._append_chunk_type_signals(signals, context)
        self._append_route_signals(signals, context)
        self._append_answer_intent_signals(signals, context)
        self._append_retry_signals(signals, context)
        if context.effective_document_id:
            signals.append(
                RetrievalStrategySignal(
                    category="document_scope",
                    value="selected_document_available",
                    score=1.5,
                )
            )
        if any(marker in query_text for marker in ("compare", " versus ", " vs ", " and ")):
            signals.append(
                RetrievalStrategySignal(
                    category="multi",
                    value="compound_query",
                    score=1.0,
                )
            )
        return signals

    def _append_keyword_signals(
        self,
        signals: list[RetrievalStrategySignal],
        query_text: str,
    ) -> None:
        self._score_terms(signals, query_text, "identifier", _IDENTIFIER_TERMS, 3.5)
        self._score_terms(signals, query_text, "specification", _SPECIFICATION_TERMS, 2.5)
        self._score_terms(signals, query_text, "maintenance", _MAINTENANCE_TERMS, 3.0)
        self._score_terms(signals, query_text, "procedure", _PROCEDURE_TERMS, 3.0)
        self._score_terms(signals, query_text, "troubleshooting", _TROUBLESHOOTING_TERMS, 3.0)
        self._score_terms(signals, query_text, "certification", _CERTIFICATION_TERMS, 3.0)
        self._score_terms(signals, query_text, "drawing", _DRAWING_TERMS, 2.5)
        self._score_terms(signals, query_text, "figure", _FIGURE_TERMS, 2.5)
        self._score_terms(signals, query_text, "table", _TABLE_TERMS, 2.5)
        self._score_terms(signals, query_text, "section", _SECTION_TERMS, 2.0)

    def _append_identifier_signals(
        self,
        signals: list[RetrievalStrategySignal],
        context: RetrievalContext,
    ) -> None:
        query_text = context.query_text
        for match in _IDENTIFIER_PATTERN.findall(query_text):
            value = match[0] if isinstance(match, tuple) else match
            signals.append(
                RetrievalStrategySignal(
                    category="identifier",
                    value=f"pattern:{value}",
                    score=4.0,
                )
            )
        analyzed_query = context.analyzed_query
        if analyzed_query is None:
            return
        for identifier in analyzed_query.detected_identifiers:
            signals.append(
                RetrievalStrategySignal(
                    category="identifier",
                    value=f"detected_identifier:{identifier}",
                    score=4.5,
                )
            )

    def _append_chunk_type_signals(
        self,
        signals: list[RetrievalStrategySignal],
        context: RetrievalContext,
    ) -> None:
        analyzed_query = context.analyzed_query
        if analyzed_query is None:
            return
        for chunk_type in analyzed_query.chunk_types:
            category = _CHUNK_TYPE_TO_CATEGORY.get(chunk_type)
            if category is None:
                continue
            signals.append(
                RetrievalStrategySignal(
                    category=category,
                    value=f"chunk_type:{chunk_type.value}",
                    score=2.0,
                )
            )

    def _append_route_signals(
        self,
        signals: list[RetrievalStrategySignal],
        context: RetrievalContext,
    ) -> None:
        if context.route == "document_exploration":
            signals.append(
                RetrievalStrategySignal(
                    category="document_exploration",
                    value="route:document_exploration",
                    score=5.0,
                )
            )

    def _append_answer_intent_signals(
        self,
        signals: list[RetrievalStrategySignal],
        context: RetrievalContext,
    ) -> None:
        intent = (context.answer_intent or "").strip().lower()
        category = _ANSWER_INTENT_TO_CATEGORY.get(intent)
        if category is None:
            return
        signals.append(
            RetrievalStrategySignal(
                category=category,
                value=f"answer_intent:{intent}",
                score=2.5,
            )
        )

    def _append_retry_signals(
        self,
        signals: list[RetrievalStrategySignal],
        context: RetrievalContext,
    ) -> None:
        retry_text = " ".join(
            value.lower().strip()
            for value in (context.retry_reason or "", context.retry_query or "")
            if value and value.strip()
        )
        if not retry_text:
            return
        self._append_keyword_signals(signals, retry_text)

    @staticmethod
    def _score_terms(
        signals: list[RetrievalStrategySignal],
        query_text: str,
        category: str,
        terms: tuple[str, ...],
        score: float,
    ) -> None:
        for term in terms:
            if term in query_text:
                signals.append(
                    RetrievalStrategySignal(
                        category=category,
                        value=term,
                        score=score,
                    )
                )


_CHUNK_TYPE_TO_CATEGORY: dict[ChunkType, str] = {
    ChunkType.TECHNICAL_SPECIFICATION: "specification",
    ChunkType.SPARE_PARTS_TABLE: "table",
    ChunkType.CERTIFICATION_INFO: "certification",
    ChunkType.MAINTENANCE_INTERVAL: "maintenance",
    ChunkType.MAINTENANCE_PROCEDURE: "procedure",
    ChunkType.OPERATION_INSTRUCTION: "procedure",
    ChunkType.INSTALLATION_INSTRUCTION: "procedure",
    ChunkType.TROUBLESHOOTING: "troubleshooting",
    ChunkType.DRAWING_REFERENCE: "drawing",
    ChunkType.OVERVIEW: "document_exploration",
}

_ANSWER_INTENT_TO_CATEGORY: dict[str, str] = {
    "maintenance_summary": "maintenance",
    "procedure_steps": "procedure",
    "specification_summary": "specification",
    "troubleshooting": "troubleshooting",
    "certification_summary": "certification",
    "identifier_lookup": "identifier",
    "table_summary": "table",
    "document_summary": "document_exploration",
}
