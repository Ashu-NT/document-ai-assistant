from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategy,
    RetrievalStrategyDecision,
)
from src.application.langgraph.retrieval_strategy.policies import RetrievalStrategyPolicy
from src.application.langgraph.retrieval_strategy.validation import (
    RetrievalStrategyValidator,
)


def test_retrieval_strategy_validator_falls_back_to_general_hybrid_for_invalid_top_k() -> None:
    validator = RetrievalStrategyValidator()
    decision = RetrievalStrategyDecision(
        primary_strategy=RetrievalStrategy.TABLE_LOOKUP,
        confidence=0.9,
        reason="table query",
        query="show table",
        top_k=999,
    )

    validated = validator.validate(
        decision,
        context=RetrievalContext(query_text="show table", top_k=5),
        policy=RetrievalStrategyPolicy(max_top_k=15),
    )

    assert validated.primary_strategy == RetrievalStrategy.GENERAL_HYBRID
    assert validated.top_k == 15


def test_retrieval_strategy_validator_preserves_document_scope() -> None:
    validator = RetrievalStrategyValidator()
    decision = RetrievalStrategyDecision(
        primary_strategy=RetrievalStrategy.IDENTIFIER_LOOKUP,
        confidence=0.9,
        reason="identifier query",
        query="part number",
        document_id="doc-other",
        top_k=5,
    )

    validated = validator.validate(
        decision,
        context=RetrievalContext(query_text="part number", document_id="doc-1"),
        policy=RetrievalStrategyPolicy(preserve_document_scope=True),
    )

    assert validated.document_id == "doc-1"
    assert validated.primary_strategy == RetrievalStrategy.GENERAL_HYBRID
