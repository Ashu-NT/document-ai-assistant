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

SIGNAL_CATEGORY_TO_STRATEGY: dict[str, RetrievalStrategy] = {
    "identifier": RetrievalStrategy.IDENTIFIER_LOOKUP,
    "table": RetrievalStrategy.TABLE_LOOKUP,
    "maintenance": RetrievalStrategy.MAINTENANCE_LOOKUP,
    "procedure": RetrievalStrategy.PROCEDURE_LOOKUP,
    "specification": RetrievalStrategy.TECHNICAL_SPECIFICATION,
    "troubleshooting": RetrievalStrategy.TROUBLESHOOTING_LOOKUP,
    "certification": RetrievalStrategy.CERTIFICATION_LOOKUP,
    "drawing": RetrievalStrategy.DRAWING_LOOKUP,
    "figure": RetrievalStrategy.FIGURE_LOOKUP,
    "section": RetrievalStrategy.SECTION_LOOKUP,
    "document_exploration": RetrievalStrategy.DOCUMENT_EXPLORATION,
}

MULTI_PRIMARY_STRATEGIES: set[RetrievalStrategy] = {
    RetrievalStrategy.TECHNICAL_SPECIFICATION,
    RetrievalStrategy.MAINTENANCE_LOOKUP,
    RetrievalStrategy.PROCEDURE_LOOKUP,
    RetrievalStrategy.TROUBLESHOOTING_LOOKUP,
    RetrievalStrategy.CERTIFICATION_LOOKUP,
    RetrievalStrategy.DRAWING_LOOKUP,
    RetrievalStrategy.FIGURE_LOOKUP,
    RetrievalStrategy.SECTION_LOOKUP,
}
