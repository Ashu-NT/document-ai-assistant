from __future__ import annotations

from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)
from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategyDecision,
)
from src.application.langgraph.retrieval_strategy.services.retrieval_strategy_response_schema import (
    RetrievalStrategyResponsePayload,
)
from pydantic import ValidationError
from src.shared.exceptions import SchemaValidationError
from src.shared.llm.json_response import (
    is_json_validation_error,
    strip_code_fences_if_wrapped,
)


class RetrievalStrategyJsonParser:
    def parse(
        self,
        raw_response: str,
        *,
        context: RetrievalContext,
        default_top_k: int,
    ) -> RetrievalStrategyDecision:
        payload = self._parse_payload(raw_response)
        return RetrievalStrategyDecision(
            primary_strategy=RetrievalStrategy(payload.primary_strategy),
            secondary_strategies=[
                RetrievalStrategy(strategy)
                for strategy in payload.secondary_strategies
            ],
            confidence=payload.confidence,
            reason=payload.reason,
            document_id=context.effective_document_id,
            query=context.query_text,
            rewritten_query=payload.rewritten_query,
            top_k=payload.top_k or default_top_k,
            diagnostics={"raw_response": raw_response},
        )

    @staticmethod
    def _parse_payload(raw_response: str) -> RetrievalStrategyResponsePayload:
        candidate = strip_code_fences_if_wrapped(raw_response)
        try:
            return RetrievalStrategyResponsePayload.model_validate_json(candidate)
        except ValidationError as exc:
            if is_json_validation_error(exc):
                raise SchemaValidationError(
                    "Malformed retrieval strategy response JSON.",
                    details={"raw_response": raw_response},
                ) from exc
            raise SchemaValidationError(
                "Retrieval strategy response failed schema validation.",
                details={"raw_response": raw_response, "errors": exc.errors()},
            ) from exc
