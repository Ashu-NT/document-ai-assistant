from src.application.workflows.retrieval.structured import (
    StructuredEvidenceQueryAnalyzer,
)

_QUERY_ANALYZER = StructuredEvidenceQueryAnalyzer()


def detect_structured_entity_type(normalized_input: str) -> str | None:
    """Detects when a question is asking for a structured-entity detail
    field (e.g. a manufacturer's website, a spare part's quantity) rather
    than just the bare identifying value. Shared between DeterministicPlanner
    and the direct-answer graph nodes so both routes use identical
    detection logic."""
    analysis = _QUERY_ANALYZER.analyze(query_text=normalized_input)
    if analysis.detail_entity_type is None:
        return None
    return analysis.detail_entity_type.value
