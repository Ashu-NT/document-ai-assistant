from dataclasses import dataclass


@dataclass(slots=True)
class ReflectionPolicy:
    enabled: bool = False
    max_reflection_attempts: int = 1
    max_retrieval_retries: int = 1
    allow_retrieval_retry: bool = True
    allow_clarification: bool = True
    allow_answer_regeneration: bool = True
    require_document_scope: bool = True
    require_grounding: bool = True
    minimum_answer_quality_score: float = 0.80
    minimum_evidence_quality_score: float = 0.75
    minimum_grounding_score: float = 0.90
