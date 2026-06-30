from __future__ import annotations

import json

from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategy,
    RetrievalStrategyDecision,
)
from src.shared.exceptions import SchemaValidationError


class RetrievalStrategyJsonParser:
    def parse(
        self,
        raw_response: str,
        *,
        context: RetrievalContext,
        default_top_k: int,
    ) -> RetrievalStrategyDecision:
        payload = self._extract_payload(raw_response)
        primary_strategy = RetrievalStrategy(str(payload["primary_strategy"]).strip())
        secondary = [
            RetrievalStrategy(str(item).strip())
            for item in payload.get("secondary_strategies", [])
        ]
        return RetrievalStrategyDecision(
            primary_strategy=primary_strategy,
            secondary_strategies=secondary,
            confidence=float(payload.get("confidence", 0.0)),
            reason=str(payload.get("reason") or "").strip(),
            document_id=context.effective_document_id,
            query=context.query_text,
            rewritten_query=str(payload.get("rewritten_query") or "").strip() or None,
            top_k=int(payload.get("top_k") or default_top_k),
            diagnostics={"raw_response": raw_response},
        )

    @staticmethod
    def _extract_payload(raw_response: str) -> dict[str, object]:
        candidate = raw_response.strip()
        if candidate.startswith("```"):
            candidate = candidate.strip("`")
            if candidate.lower().startswith("json"):
                candidate = candidate[4:].strip()
        start_index = candidate.find("{")
        end_index = candidate.rfind("}")
        if start_index < 0 or end_index < 0 or end_index <= start_index:
            raise SchemaValidationError(
                "Malformed retrieval strategy response JSON.",
                details={"raw_response": raw_response},
            )
        try:
            payload = json.loads(candidate[start_index : end_index + 1])
        except json.JSONDecodeError as exc:
            raise SchemaValidationError(
                "Malformed retrieval strategy response JSON.",
                details={"raw_response": raw_response},
            ) from exc
        if not isinstance(payload, dict):
            raise SchemaValidationError(
                "Retrieval strategy response must decode to a JSON object.",
                details={"raw_response": raw_response},
            )
        if "primary_strategy" not in payload:
            raise SchemaValidationError(
                "Retrieval strategy response must include primary_strategy.",
                details={"raw_response": raw_response},
            )
        return payload
