from __future__ import annotations

import re

from src.application.langgraph.retrieval_strategy.constants.retrieval_signal_terms import (
    ANSWER_INTENT_TO_CATEGORY,
    CERTIFICATION_TERMS,
    CHUNK_TYPE_TO_CATEGORY,
    DRAWING_TERMS,
    FIGURE_TERMS,
    IDENTIFIER_TERMS,
    MAINTENANCE_TERMS,
    PROCEDURE_TERMS,
    SECTION_TERMS,
    SPECIFICATION_TERMS,
    TABLE_TERMS,
    TROUBLESHOOTING_TERMS,
)
from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategySignal,
)
from src.application.workflows.shared.identifier_value_pattern import (
    IDENTIFIER_VALUE_PATTERN,
)


class RetrievalSignalExtractor:
    def extract(self, context: RetrievalContext) -> list[RetrievalStrategySignal]:
        query_text = (
            context.analyzed_query.effective_query()
            if context.analyzed_query is not None
            else context.query_text
        ).lower()
        signals: list[RetrievalStrategySignal] = []
        self._append_keyword_signals(signals, query_text)
        self._append_maintenance_interval_table_signal(signals, query_text)
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
        self._score_terms(signals, query_text, "identifier", IDENTIFIER_TERMS, 3.5)
        self._score_terms(signals, query_text, "specification", SPECIFICATION_TERMS, 2.5)
        self._score_terms(signals, query_text, "maintenance", MAINTENANCE_TERMS, 3.0)
        self._score_terms(signals, query_text, "procedure", PROCEDURE_TERMS, 3.0)
        self._score_terms(signals, query_text, "troubleshooting", TROUBLESHOOTING_TERMS, 3.0)
        self._score_terms(signals, query_text, "certification", CERTIFICATION_TERMS, 3.0)
        self._score_terms(signals, query_text, "drawing", DRAWING_TERMS, 2.5)
        self._score_terms(signals, query_text, "figure", FIGURE_TERMS, 2.5)
        self._score_terms(signals, query_text, "table", TABLE_TERMS, 2.5)
        self._score_terms(signals, query_text, "section", SECTION_TERMS, 2.0)

    @staticmethod
    def _append_maintenance_interval_table_signal(
        signals: list[RetrievalStrategySignal],
        query_text: str,
    ) -> None:
        has_maintenance_scope = any(
            term in query_text
            for term in ("maintenance", "service", "inspection", "preventive maintenance")
        )
        has_interval_language = any(
            term in query_text
            for term in (
                "interval",
                "schedule",
                "daily",
                "weekly",
                "monthly",
                "quarterly",
                "annual",
                "annually",
            )
        )
        if not (has_maintenance_scope and has_interval_language):
            return
        signals.append(
            RetrievalStrategySignal(
                category="table",
                value="maintenance_interval_table_bias",
                score=2.5,
            )
        )

    def _append_identifier_signals(
        self,
        signals: list[RetrievalStrategySignal],
        context: RetrievalContext,
    ) -> None:
        query_text = context.query_text
        for match in IDENTIFIER_VALUE_PATTERN.findall(query_text):
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
            category = CHUNK_TYPE_TO_CATEGORY.get(chunk_type)
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
        category = ANSWER_INTENT_TO_CATEGORY.get(intent)
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
        self._append_maintenance_interval_table_signal(signals, retry_text)

    @staticmethod
    def _score_terms(
        signals: list[RetrievalStrategySignal],
        query_text: str,
        category: str,
        terms: tuple[str, ...],
        score: float,
    ) -> None:
        for term in terms:
            if _matches_term(query_text, term):
                signals.append(
                    RetrievalStrategySignal(
                        category=category,
                        value=term,
                        score=score,
                    )
                )


def _matches_term(query_text: str, term: str) -> bool:
    normalized_term = term.strip().lower()
    if not normalized_term:
        return False
    return re.search(
        rf"(?<!\w){re.escape(normalized_term)}(?!\w)",
        query_text,
    ) is not None
