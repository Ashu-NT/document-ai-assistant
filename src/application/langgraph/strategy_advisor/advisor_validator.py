from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any

from src.application.langgraph.strategy_advisor.advisor_models import (
    StrategyAdvisorIntent,
    StrategyAdvisorProposal,
    StrategyAdvisorRequest,
)
from src.application.langgraph.routing import RouteType
from src.shared.exceptions import SchemaValidationError

if TYPE_CHECKING:
    from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
        RetrievalStrategy,
    )

_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")
_ALLOWED_KEYS = {
    "intent",
    "route",
    "confidence",
    "concepts",
    "recommended_strategies",
    "comparison",
    "requires_table",
    "reason",
}
_ALLOWED_ROUTES = {
    RouteType.ANSWER_QUESTION.value,
    RouteType.DEEP_RESEARCH.value,
    RouteType.PLANNED_TASK.value,
    RouteType.RETRIEVE_EVIDENCE.value,
    RouteType.DOCUMENT_EXPLORATION.value,
}


class StrategyAdvisorValidator:
    def validate_response(
        self,
        raw_response: str,
        *,
        request: StrategyAdvisorRequest,
    ) -> StrategyAdvisorProposal:
        payload = self._extract_payload(raw_response)
        self._validate_keys(payload)
        intent = StrategyAdvisorIntent(str(payload.get("intent") or "").strip())
        route = str(payload.get("route") or "").strip()
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
        confidence = float(payload.get("confidence") or 0.0)
        if confidence < 0.0 or confidence > 1.0:
            raise SchemaValidationError(
                "Strategy advisor confidence must be between 0 and 1.",
                details={"confidence": confidence},
            )
        concepts = self._validate_concepts(payload.get("concepts"), request.query_text)
        strategies = self._validate_strategies(payload.get("recommended_strategies"))
        comparison = bool(payload.get("comparison"))
        requires_table = bool(payload.get("requires_table"))
        reason = str(payload.get("reason") or "").strip()
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

    @staticmethod
    def _extract_payload(raw_response: str) -> dict[str, Any]:
        candidate = raw_response.strip()
        if candidate.startswith("```"):
            candidate = candidate.strip("`")
            if candidate.lower().startswith("json"):
                candidate = candidate[4:].strip()
        start_index = candidate.find("{")
        end_index = candidate.rfind("}")
        if start_index < 0 or end_index < 0 or end_index <= start_index:
            raise SchemaValidationError(
                "Malformed strategy advisor response JSON.",
                details={"raw_response": raw_response},
            )
        try:
            payload = json.loads(candidate[start_index : end_index + 1])
        except json.JSONDecodeError as exc:
            raise SchemaValidationError(
                "Malformed strategy advisor response JSON.",
                details={"raw_response": raw_response},
            ) from exc
        if not isinstance(payload, dict):
            raise SchemaValidationError(
                "Strategy advisor response must decode to a JSON object.",
                details={"raw_response": raw_response},
            )
        return payload

    @staticmethod
    def _validate_keys(payload: dict[str, Any]) -> None:
        unknown_keys = sorted(set(payload.keys()) - _ALLOWED_KEYS)
        if unknown_keys:
            raise SchemaValidationError(
                "Strategy advisor response contained unsupported keys.",
                details={"unknown_keys": unknown_keys},
            )

    def _validate_concepts(self, raw_concepts: Any, query_text: str) -> list[str]:
        if not isinstance(raw_concepts, list) or not raw_concepts:
            raise SchemaValidationError(
                "Strategy advisor concepts must be a non-empty list.",
                details={"concepts": raw_concepts},
            )
        normalized_query = self._normalize(query_text)
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
            if normalized not in normalized_query:
                raise SchemaValidationError(
                    "Strategy advisor returned a concept not grounded in the user query.",
                    details={"concept": concept, "query_text": query_text},
                )
            seen.add(normalized)
            concepts.append(concept)
        return concepts

    @staticmethod
    def _validate_strategies(raw_strategies: Any) -> list[RetrievalStrategy]:
        from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
            RetrievalStrategy,
        )

        if not isinstance(raw_strategies, list) or not raw_strategies:
            raise SchemaValidationError(
                "Strategy advisor recommended_strategies must be a non-empty list.",
                details={"recommended_strategies": raw_strategies},
            )
        strategies: list[RetrievalStrategy] = []
        seen: set[RetrievalStrategy] = set()
        for item in raw_strategies:
            strategy = RetrievalStrategy(str(item or "").strip())
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
