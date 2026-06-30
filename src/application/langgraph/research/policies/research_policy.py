from dataclasses import dataclass

from src.application.langgraph.research.constants import (
    DEFAULT_MAX_RESEARCH_EVIDENCE_PER_TASK,
    DEFAULT_MAX_RESEARCH_ITERATIONS,
    DEFAULT_MAX_RESEARCH_TASKS,
    DEFAULT_MAX_TOTAL_RESEARCH_EVIDENCE,
)


@dataclass(slots=True, frozen=True)
class ResearchPolicy:
    enabled: bool = False
    llm_research_planning_enabled: bool = False
    max_tasks: int = DEFAULT_MAX_RESEARCH_TASKS
    max_iterations: int = DEFAULT_MAX_RESEARCH_ITERATIONS
    max_evidence_per_task: int = DEFAULT_MAX_RESEARCH_EVIDENCE_PER_TASK
    max_total_evidence: int = DEFAULT_MAX_TOTAL_RESEARCH_EVIDENCE
    require_document_scope: bool = True
    allow_followup_research: bool = True
    allow_llm_synthesis: bool = True
    fallback_to_standard_qa: bool = True
