from dataclasses import dataclass, field

from src.application.langgraph.retrieval_strategy.models import RetrievalStrategy


@dataclass(slots=True, frozen=True)
class ResearchTaskPolicy:
    max_title_chars: int = 120
    max_question_chars: int = 400
    max_results: int = 10
    require_document_scope: bool = True
    allowed_strategy_hints: set[str] = field(
        default_factory=lambda: {strategy.value for strategy in RetrievalStrategy}
    )
