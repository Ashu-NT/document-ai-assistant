from enum import StrEnum


class EvaluationCorpusTier(StrEnum):
    """Which regression tier a golden corpus document belongs to.

    Deliberately orthogonal to execution speed/LLM-usage (fast vs. slow/e2e
    pytest markers already cover that axis) - this is purely about corpus
    SIZE/PURPOSE: CORE is the small, fast, diagnostically-focused
    regression set; CHALLENGE is large/heterogeneous real-world documents
    used to stress-test realistic behavior. A CORE document can still be
    evaluated in a slow/e2e-marked test, and a CHALLENGE document could in
    principle be fast if cached - the two concepts are independent.

    CORE is the default for every existing entry, so the original 10-
    document corpus needed zero fixture changes to adopt this concept.
    """

    CORE = "core"
    CHALLENGE = "challenge"


__all__ = ["EvaluationCorpusTier"]
