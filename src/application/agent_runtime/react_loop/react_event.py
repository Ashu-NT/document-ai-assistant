from enum import StrEnum


class ReactEvent(StrEnum):
    USER_INPUT = "user_input"
    THOUGHT_SUMMARY = "thought_summary"
    PLAN = "plan"
    RESEARCH_PLAN = "research_plan"
    RETRIEVAL_STRATEGY = "retrieval_strategy"
    ACTION = "action"
    OBSERVATION = "observation"
    REFLECTION = "reflection"
    SAFETY_BLOCK = "safety_block"
    FINAL_ANSWER = "final_answer"
    ERROR = "error"
