from dataclasses import dataclass, field

from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)


@dataclass(slots=True)
class StrategyPriorityPolicy:
    ordered_strategies: tuple[RetrievalStrategy, ...] = field(
        default_factory=lambda: (
            RetrievalStrategy.IDENTIFIER_LOOKUP,
            RetrievalStrategy.TABLE_LOOKUP,
            RetrievalStrategy.TECHNICAL_SPECIFICATION,
            RetrievalStrategy.MAINTENANCE_LOOKUP,
            RetrievalStrategy.PROCEDURE_LOOKUP,
            RetrievalStrategy.TROUBLESHOOTING_LOOKUP,
            RetrievalStrategy.CERTIFICATION_LOOKUP,
            RetrievalStrategy.DRAWING_LOOKUP,
            RetrievalStrategy.FIGURE_LOOKUP,
            RetrievalStrategy.SECTION_LOOKUP,
            RetrievalStrategy.DOCUMENT_EXPLORATION,
            RetrievalStrategy.GENERAL_HYBRID,
        )
    )

    def sort(self, strategies: list[RetrievalStrategy]) -> list[RetrievalStrategy]:
        rank = {strategy: index for index, strategy in enumerate(self.ordered_strategies)}
        return sorted(strategies, key=lambda item: rank.get(item, len(rank)))
