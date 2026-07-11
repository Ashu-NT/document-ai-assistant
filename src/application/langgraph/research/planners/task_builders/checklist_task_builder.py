from __future__ import annotations

from src.application.langgraph.research.planners.concept_extractor import (
    concept_list_text,
)
from src.application.langgraph.research.planners.concept_strategy_mapper import (
    strategy_for_concept,
)
from src.application.langgraph.research.planners.research_plan_builder import (
    ResearchPlanBuilder,
)
from src.application.langgraph.research.planners.task_builders.concept_task_builder import (
    build_concept_task,
)
from src.application.langgraph.research.policies import ResearchPolicy
from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)


def build_checklist_tasks(
    *,
    plan_builder: ResearchPlanBuilder,
    goal,
    concepts: list[str],
    policy: ResearchPolicy,
) -> list:
    tasks = [
        build_concept_task(
            plan_builder=plan_builder,
            goal=goal,
            concept=concept,
            question=f"What steps, checks, or requirements are described for {concept}?",
            strategy=strategy_for_concept(concept),
            answer_intent="checklist",
            max_results=policy.max_evidence_per_task,
        )
        for concept in concepts
    ]
    concept_text = concept_list_text(concepts)
    tasks.append(
        plan_builder.build_task(
            title="Collect safety warnings",
            question=f"What safety warnings or prerequisites apply to {concept_text}?",
            strategy_hint=RetrievalStrategy.SECTION_LOOKUP.value,
            answer_intent_hint="checklist",
            document_id=goal.document_id,
            required=False,
            expected_evidence_type="safety",
            max_results=policy.max_evidence_per_task,
            diagnostics={"concept_role": "safety"},
        )
    )
    tasks.append(
        plan_builder.build_task(
            title="Collect prerequisites",
            question=f"What prerequisite checks or preparation steps are required for {concept_text}?",
            strategy_hint=RetrievalStrategy.PROCEDURE_LOOKUP.value,
            answer_intent_hint="checklist",
            document_id=goal.document_id,
            required=False,
            expected_evidence_type="prerequisite",
            max_results=policy.max_evidence_per_task,
            diagnostics={"concept_role": "prerequisite"},
        )
    )
    return tasks
