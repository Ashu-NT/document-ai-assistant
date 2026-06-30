from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ResearchIterationPolicy:
    max_iterations: int = 1
    max_followup_tasks: int = 1
    allow_followup_research: bool = True
