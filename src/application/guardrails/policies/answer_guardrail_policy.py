from dataclasses import dataclass, field


def _default_min_claim_support_score() -> float:
    try:
        from src.config.settings import guardrail_settings
        return guardrail_settings.min_claim_support_score
    except Exception:
        return 0.60


@dataclass(slots=True, frozen=True)
class AnswerGuardrailPolicy:
    require_citations: bool = True
    block_unsupported_claims: bool = True
    block_unsupported_suggestions: bool = True
    min_claim_support_score: float = field(
        default_factory=_default_min_claim_support_score
    )
