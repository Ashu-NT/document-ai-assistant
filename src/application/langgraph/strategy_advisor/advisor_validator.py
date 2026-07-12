from __future__ import annotations

import re
from typing import TYPE_CHECKING

from src.application.langgraph.strategy_advisor.concept_grounding import (
    is_grounded_concept,
)
from src.application.langgraph.strategy_advisor.advisor_models import (
    StrategyAdvisorIntent,
    StrategyAdvisorProposal,
    StrategyAdvisorRequest,
)
from src.application.langgraph.strategy_advisor.strategy_advisor_response_parser import (
    StrategyAdvisorResponseParser,
)
from src.application.langgraph.routing import RouteType
from src.shared.exceptions import SchemaValidationError

if TYPE_CHECKING:
    from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
        RetrievalStrategy,
    )

_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")
_ALLOWED_ROUTES = {
    RouteType.ANSWER_QUESTION.value,
    RouteType.DEEP_RESEARCH.value,
    RouteType.PLANNED_TASK.value,
    RouteType.RETRIEVE_EVIDENCE.value,
    RouteType.DOCUMENT_EXPLORATION.value,
}


class StrategyAdvisorValidator:
    def __init__(self, *, response_parser: StrategyAdvisorResponseParser | None = None) -> None:
        self.response_parser = response_parser or StrategyAdvisorResponseParser()

    def validate_response(
        self,
        raw_response: str,
        *,
        request: StrategyAdvisorRequest,
    ) -> StrategyAdvisorProposal:
        payload = self.response_parser.parse(raw_response)
        intent = payload.intent
        route = payload.route
        if route not in _ALLOWED_ROUTES:
            raise SchemaValidationError(
                "Strategy advisor returned an unsupported route.",
                details={"route": route},
            )
        if request.allowed_routes and route not in set(request.allowed_routes):
            raise SchemaValidationError(
                "Strategy advisor returned a route outside the allowed runtime routes.",
                details={"route": route},
            )
        confidence = payload.confidence
        if confidence < 0.0 or confidence > 1.0:
            raise SchemaValidationError(
                "Strategy advisor confidence must be between 0 and 1.",
                details={"confidence": confidence},
            )
        concepts = self._validate_concepts(payload.concepts, request.query_text)
        strategies = self._validate_strategies(payload.recommended_strategies)
        comparison = payload.comparison
        requires_table = payload.requires_table
        reason = payload.reason
        if not reason:
            raise SchemaValidationError(
                "Strategy advisor reason is required.",
                details={"raw_response": raw_response},
            )
        if comparison and intent != StrategyAdvisorIntent.COMPARISON:
            raise SchemaValidationError(
                "Comparison advisor responses must use comparison intent.",
                details={"intent": intent.value, "comparison": comparison},
            )
        if comparison and len(concepts) < 2:
            raise SchemaValidationError(
                "Comparison advisor responses must preserve at least two concepts.",
                details={"concepts": concepts},
            )
        if comparison and route != RouteType.DEEP_RESEARCH.value:
            raise SchemaValidationError(
                "Comparison advisor responses must recommend the deep_research route.",
                details={"route": route},
            )
        return StrategyAdvisorProposal(
            intent=intent,
            route=route,
            confidence=confidence,
            concepts=concepts,
            recommended_strategies=strategies,
            comparison=comparison,
            requires_table=requires_table,
            reason=reason,
            diagnostics={"raw_response": raw_response},
        )

    def _validate_concepts(self, raw_concepts: list[str], query_text: str) -> list[str]:
        if not raw_concepts:
            raise SchemaValidationError(
                "Strategy advisor concepts must be a non-empty list.",
                details={"concepts": raw_concepts},
            )
        concepts: list[str] = []
        seen: set[str] = set()
        for item in raw_concepts:
            concept = str(item or "").strip()
            normalized = self._normalize(concept)
            if not normalized:
                raise SchemaValidationError(
                    "Strategy advisor concepts must be non-empty strings.",
                    details={"concept": item},
                )
            if normalized in seen:
                raise SchemaValidationError(
                    "Strategy advisor returned duplicated concepts.",
                    details={"concept": concept},
                )
            if not is_grounded_concept(concept=concept, query_text=query_text):
                raise SchemaValidationError(
                    "Strategy advisor returned a concept not grounded in the user query.",
                    details={"concept": concept, "query_text": query_text},
                )
            seen.add(normalized)
            concepts.append(concept)
        return concepts

    @staticmethod
    def _validate_strategies(raw_strategies: list[str]) -> list[RetrievalStrategy]:
        from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
            RetrievalStrategy,
        )

        if not raw_strategies:
            raise SchemaValidationError(
                "Strategy advisor recommended_strategies must be a non-empty list.",
                details={"recommended_strategies": raw_strategies},
            )
        strategies: list[RetrievalStrategy] = []
        seen: set[RetrievalStrategy] = set()
        for item in raw_strategies:
            strategy = RetrievalStrategy(item)
            if strategy == RetrievalStrategy.MULTI_STRATEGY:
                raise SchemaValidationError(
                    "Strategy advisor must recommend concrete strategies, not MULTI_STRATEGY.",
                    details={"recommended_strategy": strategy.value},
                )
            if strategy in seen:
                continue
            seen.add(strategy)
            strategies.append(strategy)
        return strategies

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = _NORMALIZE_RE.sub(" ", value.strip().lower())
        return " ".join(normalized.split())
