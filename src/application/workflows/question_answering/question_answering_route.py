from enum import StrEnum


class QuestionAnsweringRoute(StrEnum):
    DOCUMENT_EXPLORATION = "document_exploration"
    RETRIEVAL_QA = "retrieval_qa"
    BLOCKED_BY_GUARDRAIL = "blocked_by_guardrail"
    NEEDS_CLARIFICATION = "needs_clarification"
