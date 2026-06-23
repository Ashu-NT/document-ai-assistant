from dataclasses import dataclass, field


def _default_min_retrieval_score() -> float:
    try:
        from src.config.settings import retrieval_settings
        return retrieval_settings.min_retrieval_score
    except Exception:
        return 0.50


def _default_relevance_score_threshold() -> float:
    try:
        from src.config.settings import retrieval_settings
        return retrieval_settings.relevance_score_threshold
    except Exception:
        return 0.40


@dataclass(slots=True, frozen=True)
class RetrievalGuardrailPolicy:
    min_retrieval_score: float = field(default_factory=_default_min_retrieval_score)
    min_evidence_chunks: int = 1
    min_procedure_evidence_chunks: int = 1
    min_specification_evidence_chunks: int = 1
    min_safety_evidence_chunks: int = 1
    identifier_evidence_required: bool = True
    relevance_score_threshold: float = field(
        default_factory=_default_relevance_score_threshold
    )
