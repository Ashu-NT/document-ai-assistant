from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ResearchSynthesisPolicy:
    preferred_format: str = "markdown"
    include_references: bool = True
    include_gaps: bool = True
    include_evidence_table: bool = True
    checklist_prefix: str = "[ ]"
