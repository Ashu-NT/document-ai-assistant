from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)
from src.domain.retrieval import RetrievalQuery

if TYPE_CHECKING:
    from src.application.langgraph.strategy_advisor.advisor_models import (
        StrategyAdvisorProposal,
    )


@dataclass(slots=True)
class RetrievalContext:
    query_text: str
    route: str | None = None
    document_id: str | None = None
    selected_document_id: str | None = None
    document_title: str | None = None
    selected_document_title: str | None = None
    top_k: int = 5
    answer_intent: str | None = None
    retry_reason: str | None = None
    retry_query: str | None = None
    requested_strategy: RetrievalStrategy | None = None
    use_llm_selector: bool = False
    analyzed_query: RetrievalQuery | None = None
    strategy_advisor_proposal: StrategyAdvisorProposal | None = None

    @property
    def effective_document_id(self) -> str | None:
        return self.document_id or self.selected_document_id

    @property
    def effective_document_title(self) -> str | None:
        return self.document_title or self.selected_document_title
