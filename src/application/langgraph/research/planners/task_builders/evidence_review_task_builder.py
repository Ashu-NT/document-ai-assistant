from __future__ import annotations

from src.application.langgraph.research.planners.concept_extractor import (
    concept_list_text,
)
from src.application.langgraph.research.planners.research_plan_builder import (
    ResearchPlanBuilder,
)
from src.application.langgraph.research.policies import ResearchPolicy
from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)


def build_evidence_review_tasks(
    *,
    plan_builder: ResearchPlanBuilder,
    goal,
    concepts: list[str],
    policy: ResearchPolicy,
) -> list:
    concept_text = concept_list_text(concepts)
    tasks = [
        plan_builder.build_task(
            title="Collect primary evidence",
            question=goal.user_input,
            strategy_hint=RetrievalStrategy.GENERAL_HYBRID.value,
            answer_intent_hint="evidence_review",
            document_id=goal.document_id,
            expected_evidence_type="claim_evidence",
            max_results=policy.max_evidence_per_task,
            diagnostics={"concepts": list(concepts)},
        ),
        plan_builder.build_task(
            title="Collect related sections",
            question=f"What related sections provide context for {concept_text}?",
            strategy_hint=RetrievalStrategy.SECTION_LOOKUP.value,
            answer_intent_hint="evidence_review",
            document_id=goal.document_id,
            required=False,
            expected_evidence_type="gap_probe",
            max_results=max(3, policy.max_evidence_per_task // 2),
            diagnostics={"concepts": list(concepts), "concept_role": "context"},
        ),
    ]
    return tasks
