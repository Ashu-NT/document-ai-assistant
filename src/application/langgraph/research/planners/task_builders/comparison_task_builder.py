from __future__ import annotations

from src.application.langgraph.research.planners.concept_extractor import (
    concept_list_text,
)
from src.application.langgraph.research.planners.concept_strategy_mapper import (
    requires_table,
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
from src.application.langgraph.strategy_advisor.models.advisor_models import (
    StrategyAdvisorProposal,
)


def build_comparison_tasks(
    *,
    plan_builder: ResearchPlanBuilder,
    goal,
    concepts: list[str],
    policy: ResearchPolicy,
    advisor_proposal: StrategyAdvisorProposal | None,
) -> list:
    tasks = [
        build_concept_task(
            plan_builder=plan_builder,
            goal=goal,
            concept=concept,
            question=f"What evidence in this document describes {concept}?",
            strategy=strategy_for_concept(concept),
            answer_intent="comparison",
            max_results=policy.max_evidence_per_task,
        )
        for concept in concepts
    ]
    concept_text = concept_list_text(concepts)
    tasks.append(
        plan_builder.build_task(
            title="Collect overlap evidence",
            question=f"What shared requirements, overlaps, or relationships connect {concept_text} in this document?",
            strategy_hint=RetrievalStrategy.GENERAL_HYBRID.value,
            answer_intent_hint="comparison",
            document_id=goal.document_id,
            required=False,
            expected_evidence_type="overlap",
            max_results=policy.max_evidence_per_task,
            diagnostics={"concept_role": "overlap"},
        )
    )
    tasks.append(
        plan_builder.build_task(
            title="Collect distinguishing evidence",
            question=f"What differences distinguish {concept_text} in this document?",
            strategy_hint=RetrievalStrategy.GENERAL_HYBRID.value,
            answer_intent_hint="comparison",
            document_id=goal.document_id,
            required=False,
            expected_evidence_type="difference",
            max_results=policy.max_evidence_per_task,
            diagnostics={"concept_role": "difference"},
        )
    )
    if requires_table(concepts, advisor_proposal):
        tasks.append(
            plan_builder.build_task(
                title="Collect structured comparison evidence",
                question=f"What tables, schedules, or structured rows compare {concept_text}?",
                strategy_hint=RetrievalStrategy.TABLE_LOOKUP.value,
                answer_intent_hint="comparison",
                document_id=goal.document_id,
                required=False,
                expected_evidence_type="comparison_table",
                max_results=max(4, policy.max_evidence_per_task // 2),
                diagnostics={"concept_role": "table_support"},
            )
        )
    return tasks
