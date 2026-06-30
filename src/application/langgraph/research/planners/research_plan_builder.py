from __future__ import annotations

from src.application.langgraph.research.models import (
    ResearchGoal,
    ResearchGoalType,
    ResearchOutputType,
    ResearchPlan,
    ResearchTask,
)
from src.application.langgraph.research.policies import ResearchPolicy
from src.shared.ids import IdGenerator


class ResearchPlanBuilder:
    def __init__(self, *, id_generator: IdGenerator | None = None) -> None:
        self.id_generator = id_generator or IdGenerator()

    def build_goal(
        self,
        *,
        user_input: str,
        document_id: str | None,
        document_title: str | None,
    ) -> ResearchGoal:
        goal_type = self._infer_goal_type(user_input)
        output_type = self._output_type(goal_type)
        return ResearchGoal(
            goal_id=self.id_generator.new_id("research_goal"),
            user_input=user_input.strip(),
            goal_type=goal_type,
            document_id=document_id,
            document_title=document_title,
            requires_document=True,
            requires_cross_section_reasoning=goal_type
            in {
                ResearchGoalType.COMPARISON,
                ResearchGoalType.CHECKLIST,
                ResearchGoalType.AUDIT,
                ResearchGoalType.GAP_ANALYSIS,
                ResearchGoalType.REPORT,
            },
            requires_multi_strategy_retrieval=goal_type
            in {
                ResearchGoalType.COMPARISON,
                ResearchGoalType.REPORT,
                ResearchGoalType.GAP_ANALYSIS,
                ResearchGoalType.AUDIT,
            },
            expected_output_type=output_type,
            diagnostics={"goal_type_reason": goal_type.value},
        )

    def build_plan(
        self,
        *,
        goal: ResearchGoal,
        tasks: list[ResearchTask],
        reason: str,
        source: str,
        policy: ResearchPolicy,
    ) -> ResearchPlan:
        return ResearchPlan(
            plan_id=self.id_generator.new_id("research_plan"),
            goal=goal,
            tasks=tasks[: policy.max_tasks],
            reason=reason,
            source=source,
            requires_document=goal.requires_document,
            max_iterations=policy.max_iterations,
            diagnostics={"task_count": len(tasks)},
        )

    def build_task(
        self,
        *,
        title: str,
        question: str,
        strategy_hint: str | None,
        answer_intent_hint: str | None,
        document_id: str | None,
        required: bool = True,
        depends_on: list[str] | None = None,
        expected_evidence_type: str | None = None,
        max_results: int = 5,
    ) -> ResearchTask:
        return ResearchTask(
            task_id=self.id_generator.new_id("research_task"),
            title=title,
            question=question,
            strategy_hint=strategy_hint,
            answer_intent_hint=answer_intent_hint,
            document_id=document_id,
            required=required,
            depends_on=list(depends_on or []),
            expected_evidence_type=expected_evidence_type,
            max_results=max_results,
        )

    @staticmethod
    def _infer_goal_type(user_input: str) -> ResearchGoalType:
        normalized = user_input.lower()
        if "compare" in normalized or "cross-check" in normalized:
            return ResearchGoalType.COMPARISON
        if "checklist" in normalized:
            return ResearchGoalType.CHECKLIST
        if "missing evidence" in normalized or "identify missing" in normalized:
            return ResearchGoalType.GAP_ANALYSIS
        if "audit" in normalized:
            return ResearchGoalType.AUDIT
        if "report" in normalized:
            return ResearchGoalType.REPORT
        if "evidence supports" in normalized:
            return ResearchGoalType.EVIDENCE_REVIEW
        if "summarize all" in normalized or "find every" in normalized:
            return ResearchGoalType.SUMMARY
        return ResearchGoalType.GENERAL_RESEARCH

    @staticmethod
    def _output_type(goal_type: ResearchGoalType) -> ResearchOutputType:
        mapping = {
            ResearchGoalType.COMPARISON: ResearchOutputType.COMPARISON,
            ResearchGoalType.SUMMARY: ResearchOutputType.SUMMARY,
            ResearchGoalType.CHECKLIST: ResearchOutputType.CHECKLIST,
            ResearchGoalType.AUDIT: ResearchOutputType.AUDIT,
            ResearchGoalType.EVIDENCE_REVIEW: ResearchOutputType.EVIDENCE_REVIEW,
            ResearchGoalType.GAP_ANALYSIS: ResearchOutputType.EVIDENCE_REVIEW,
            ResearchGoalType.REPORT: ResearchOutputType.REPORT,
            ResearchGoalType.GENERAL_RESEARCH: ResearchOutputType.REPORT,
        }
        return mapping[goal_type]
