from enum import StrEnum


class GuardrailDecision(StrEnum):
    ALLOW = "allow"
    BLOCK = "block"
    CLARIFY = "clarify"
    REDIRECT = "redirect"
    WARN = "warn"
    REQUIRE_APPROVAL = "require_approval"
    SAFE_FALLBACK = "safe_fallback"

    ALLOW_WITH_CAUTION = "allow_with_caution"
    NEEDS_CLARIFICATION = "needs_clarification"
    OUT_OF_SCOPE = "out_of_scope"
    NO_EVIDENCE = "no_evidence"
    LOW_CONFIDENCE = "low_confidence"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    CITATION_REQUIRED = "citation_required"
    UNSUPPORTED_CLAIMS = "unsupported_claims"
    SAFETY_BLOCKED = "safety_blocked"
