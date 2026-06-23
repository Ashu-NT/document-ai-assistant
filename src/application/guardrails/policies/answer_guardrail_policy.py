from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class AnswerGuardrailPolicy:
    require_citations: bool = True
    block_unsupported_claims: bool = True
    block_unsupported_suggestions: bool = True
    min_claim_support_score: float = 0.60
