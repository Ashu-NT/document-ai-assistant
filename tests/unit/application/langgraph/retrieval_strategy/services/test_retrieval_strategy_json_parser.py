import pytest

from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategy,
)
from src.application.langgraph.retrieval_strategy.services.retrieval_strategy_json_parser import (
    RetrievalStrategyJsonParser,
)
from src.shared.exceptions import SchemaValidationError


def test_retrieval_strategy_json_parser_parses_valid_json() -> None:
    parser = RetrievalStrategyJsonParser()

    decision = parser.parse(
        """```json
        {
          "primary_strategy": "IDENTIFIER_LOOKUP",
          "secondary_strategies": ["TABLE_LOOKUP"],
          "confidence": 0.93,
          "reason": "The query is identifier-heavy and may need table evidence.",
          "rewritten_query": "serial number or part number",
          "top_k": 7
        }
        ```""",
        context=RetrievalContext(query_text="find serial number"),
        default_top_k=5,
    )

    assert decision.primary_strategy == RetrievalStrategy.IDENTIFIER_LOOKUP
    assert decision.secondary_strategies == [RetrievalStrategy.TABLE_LOOKUP]
    assert decision.rewritten_query == "serial number or part number"
    assert decision.top_k == 7


def test_retrieval_strategy_json_parser_rejects_non_json_response() -> None:
    parser = RetrievalStrategyJsonParser()

    with pytest.raises(SchemaValidationError):
        parser.parse(
            "Primary strategy should be identifier lookup.",
            context=RetrievalContext(query_text="find serial number"),
            default_top_k=5,
        )
