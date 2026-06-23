from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SafetyGuardrailPolicy:
    block_ungrounded_safety_answers: bool = True
    min_safety_evidence_chunks: int = 1
    require_safety_source_citation: bool = True
