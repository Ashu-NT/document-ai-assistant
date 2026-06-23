from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RetrievalGuardrailPolicy:
    min_retrieval_score: float = 0.50
    min_evidence_chunks: int = 1
    min_procedure_evidence_chunks: int = 1
    min_specification_evidence_chunks: int = 1
    min_safety_evidence_chunks: int = 1
    identifier_evidence_required: bool = True
    relevance_score_threshold: float = 0.40
