from __future__ import annotations

from src.application.langgraph.research.models import ResearchGoalType, ResearchPlan
from src.application.langgraph.research.planners.concept_extractor import (
    resolve_concepts,
)
from src.application.langgraph.research.planners.research_goal_output_mapper import (
    output_type_for_goal,
    plan_reason,
)
from src.application.langgraph.research.planners.research_plan_builder import (
    ResearchPlanBuilder,
)
from src.application.langgraph.research.planners.task_builders.checklist_task_builder import (
    build_checklist_tasks,
)
from src.application.langgraph.research.planners.task_builders.comparison_task_builder import (
    build_comparison_tasks,
)
from src.application.langgraph.research.planners.task_builders.evidence_review_task_builder import (
    build_evidence_review_tasks,
)
from src.application.langgraph.research.planners.task_builders.general_task_builder import (
    build_general_tasks,
)
from src.application.langgraph.research.policies import ResearchPolicy
from src.application.langgraph.strategy_advisor.advisor_models import (
    StrategyAdvisorIntent,
    StrategyAdvisorProposal,
)


class DeterministicResearchPlanner:
    def __init__(self, *, plan_builder: ResearchPlanBuilder | None = None) -> None:
        self.plan_builder = plan_builder or ResearchPlanBuilder()

    def plan(
        self,
        *,
        user_input: str,
        document_id: str | None,
        document_title: str | None,
        policy: ResearchPolicy,
        advisor_proposal: StrategyAdvisorProposal | None = None,
    ) -> ResearchPlan:
        goal = self.plan_builder.build_goal(
            user_input=user_input,
            document_id=document_id,
            document_title=document_title,
        )
        self._apply_goal_overrides(goal, advisor_proposal=advisor_proposal)
        concepts = resolve_concepts(
            user_input=user_input,
            goal_type=goal.goal_type,
            advisor_proposal=advisor_proposal,
        )
        goal.requires_cross_section_reasoning = goal.goal_type in {
            ResearchGoalType.COMPARISON,
            ResearchGoalType.CHECKLIST,
            ResearchGoalType.AUDIT,
            ResearchGoalType.GAP_ANALYSIS,
            ResearchGoalType.REPORT,
        }
        goal.requires_multi_strategy_retrieval = len(concepts) > 1 or goal.goal_type in {
            ResearchGoalType.COMPARISON,
            ResearchGoalType.REPORT,
            ResearchGoalType.GAP_ANALYSIS,
            ResearchGoalType.AUDIT,
        }
        goal.expected_output_type = output_type_for_goal(goal.goal_type)
        goal.diagnostics.update(
            {
                "concepts": list(concepts),
                "advisor_intent": (
                    advisor_proposal.intent.value
                    if advisor_proposal is not None
                    else None
                ),
                "advisor_requires_table": (
                    advisor_proposal.requires_table
                    if advisor_proposal is not None
                    else False
                ),
            }
        )
        tasks = self._tasks_for_goal(
            goal=goal,
            concepts=concepts,
            policy=policy,
            advisor_proposal=advisor_proposal,
        )
        return self.plan_builder.build_plan(
            goal=goal,
            tasks=tasks,
            reason=plan_reason(goal.goal_type, concepts),
            source="deterministic",
            policy=policy,
        )

    def _apply_goal_overrides(
        self,
        goal,
        *,
        advisor_proposal: StrategyAdvisorProposal | None,
    ) -> None:
        if advisor_proposal is None:
            return
        mapping = {
            StrategyAdvisorIntent.COMPARISON: ResearchGoalType.COMPARISON,
            StrategyAdvisorIntent.SUMMARY: ResearchGoalType.SUMMARY,
            StrategyAdvisorIntent.CHECKLIST: ResearchGoalType.CHECKLIST,
            StrategyAdvisorIntent.REPORT: ResearchGoalType.REPORT,
            StrategyAdvisorIntent.EVIDENCE_REVIEW: ResearchGoalType.EVIDENCE_REVIEW,
            StrategyAdvisorIntent.GENERAL_LOOKUP: goal.goal_type,
        }
        if advisor_proposal.comparison:
            goal.goal_type = ResearchGoalType.COMPARISON
            return
        goal.goal_type = mapping.get(advisor_proposal.intent, goal.goal_type)

    def _tasks_for_goal(
        self,
        *,
        goal,
        concepts: list[str],
        policy: ResearchPolicy,
        advisor_proposal: StrategyAdvisorProposal | None,
    ) -> list:
        if goal.goal_type == ResearchGoalType.COMPARISON:
            return build_comparison_tasks(
                plan_builder=self.plan_builder,
                goal=goal,
                concepts=concepts,
                policy=policy,
                advisor_proposal=advisor_proposal,
            )
        if goal.goal_type == ResearchGoalType.CHECKLIST:
            return build_checklist_tasks(
                plan_builder=self.plan_builder,
                goal=goal,
                concepts=concepts,
                policy=policy,
            )
        if goal.goal_type in {
            ResearchGoalType.GAP_ANALYSIS,
            ResearchGoalType.EVIDENCE_REVIEW,
        }:
            return build_evidence_review_tasks(
                plan_builder=self.plan_builder,
                goal=goal,
                concepts=concepts,
                policy=policy,
            )
        return build_general_tasks(
            plan_builder=self.plan_builder,
            goal=goal,
            concepts=concepts,
            policy=policy,
            advisor_proposal=advisor_proposal,
        )
