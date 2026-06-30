from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)

CLI_RETRIEVAL_STRATEGY_ALIASES: dict[str, RetrievalStrategy | None] = {
    "auto": None,
    "hybrid": RetrievalStrategy.GENERAL_HYBRID,
    "identifier": RetrievalStrategy.IDENTIFIER_LOOKUP,
    "table": RetrievalStrategy.TABLE_LOOKUP,
    "section": RetrievalStrategy.SECTION_LOOKUP,
    "figure": RetrievalStrategy.FIGURE_LOOKUP,
    "maintenance": RetrievalStrategy.MAINTENANCE_LOOKUP,
    "procedure": RetrievalStrategy.PROCEDURE_LOOKUP,
    "specification": RetrievalStrategy.TECHNICAL_SPECIFICATION,
    "troubleshooting": RetrievalStrategy.TROUBLESHOOTING_LOOKUP,
    "certification": RetrievalStrategy.CERTIFICATION_LOOKUP,
    "drawing": RetrievalStrategy.DRAWING_LOOKUP,
}
