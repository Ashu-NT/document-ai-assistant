from __future__ import annotations

from src.application.langgraph.research.models import (
    ResearchGoalType,
    ResearchPlan,
)
from src.application.langgraph.research.planners.research_plan_builder import (
    ResearchPlanBuilder,
)
from src.application.langgraph.research.policies import ResearchPolicy
from src.application.langgraph.retrieval_strategy.models import RetrievalStrategy


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
    ) -> ResearchPlan:
        goal = self.plan_builder.build_goal(
            user_input=user_input,
            document_id=document_id,
            document_title=document_title,
        )
        tasks = self._tasks_for_goal(goal, policy=policy)
        return self.plan_builder.build_plan(
            goal=goal,
            tasks=tasks,
            reason=self._reason(goal.goal_type),
            source="deterministic",
            policy=policy,
        )

    def _tasks_for_goal(self, goal, *, policy: ResearchPolicy):
        build = self.plan_builder.build_task
        document_id = goal.document_id
        user_input = goal.user_input.lower()

        if goal.goal_type == ResearchGoalType.COMPARISON:
            topics = self._comparison_topics(user_input)
            return [
                build(
                    title=f"Collect {title}",
                    question=question,
                    strategy_hint=strategy.value,
                    answer_intent_hint="comparison",
                    document_id=document_id,
                    expected_evidence_type=title.lower(),
                    max_results=policy.max_evidence_per_task,
                )
                for title, question, strategy in topics
            ]

        if goal.goal_type == ResearchGoalType.SUMMARY and "maintenance" in user_input:
            return [
                build(
                    title="Collect maintenance tasks",
                    question="What maintenance tasks are described across the document?",
                    strategy_hint=RetrievalStrategy.MAINTENANCE_LOOKUP.value,
                    answer_intent_hint="maintenance_summary",
                    document_id=document_id,
                    expected_evidence_type="maintenance",
                    max_results=policy.max_evidence_per_task,
                ),
                build(
                    title="Collect maintenance intervals",
                    question="What maintenance intervals or inspection intervals are described?",
                    strategy_hint=RetrievalStrategy.MAINTENANCE_LOOKUP.value,
                    answer_intent_hint="maintenance_summary",
                    document_id=document_id,
                    expected_evidence_type="interval",
                    max_results=policy.max_evidence_per_task,
                ),
                build(
                    title="Collect lubrication and inspection tasks",
                    question="What lubrication, inspection, or service tasks are described?",
                    strategy_hint=RetrievalStrategy.MAINTENANCE_LOOKUP.value,
                    answer_intent_hint="maintenance_summary",
                    document_id=document_id,
                    expected_evidence_type="maintenance_detail",
                    max_results=policy.max_evidence_per_task,
                ),
            ]

        if goal.goal_type == ResearchGoalType.CHECKLIST:
            return [
                build(
                    title="Collect commissioning procedures",
                    question="What startup or commissioning procedures are described?",
                    strategy_hint=RetrievalStrategy.PROCEDURE_LOOKUP.value,
                    answer_intent_hint="checklist",
                    document_id=document_id,
                    expected_evidence_type="procedure",
                    max_results=policy.max_evidence_per_task,
                ),
                build(
                    title="Collect safety warnings",
                    question="What safety warnings or prerequisites apply to commissioning?",
                    strategy_hint=RetrievalStrategy.MAINTENANCE_LOOKUP.value,
                    answer_intent_hint="checklist",
                    document_id=document_id,
                    expected_evidence_type="safety",
                    max_results=policy.max_evidence_per_task,
                ),
                build(
                    title="Collect prerequisites",
                    question="What prerequisites or preparatory checks are required before operation?",
                    strategy_hint=RetrievalStrategy.SECTION_LOOKUP.value,
                    answer_intent_hint="checklist",
                    document_id=document_id,
                    expected_evidence_type="prerequisite",
                    max_results=policy.max_evidence_per_task,
                ),
            ]

        if goal.goal_type in {ResearchGoalType.GAP_ANALYSIS, ResearchGoalType.EVIDENCE_REVIEW}:
            return [
                build(
                    title="Collect primary evidence",
                    question=goal.user_input,
                    strategy_hint=RetrievalStrategy.GENERAL_HYBRID.value,
                    answer_intent_hint="evidence_review",
                    document_id=document_id,
                    expected_evidence_type="claim_evidence",
                    max_results=policy.max_evidence_per_task,
                ),
                build(
                    title="Collect potentially missing or contradicting sections",
                    question=f"What sections are related to this request but do not provide direct evidence: {goal.user_input}",
                    strategy_hint=RetrievalStrategy.SECTION_LOOKUP.value,
                    answer_intent_hint="evidence_review",
                    document_id=document_id,
                    required=False,
                    expected_evidence_type="gap_probe",
                    max_results=max(3, policy.max_evidence_per_task // 2),
                ),
            ]

        if goal.goal_type == ResearchGoalType.REPORT and "maintenance" in user_input:
            return [
                build(
                    title="Collect maintenance tasks",
                    question="What maintenance tasks are described across the document?",
                    strategy_hint=RetrievalStrategy.MAINTENANCE_LOOKUP.value,
                    answer_intent_hint="maintenance_report",
                    document_id=document_id,
                    expected_evidence_type="maintenance",
                    max_results=policy.max_evidence_per_task,
                ),
                build(
                    title="Collect maintenance intervals",
                    question="What maintenance intervals or inspection intervals are specified?",
                    strategy_hint=RetrievalStrategy.MAINTENANCE_LOOKUP.value,
                    answer_intent_hint="maintenance_report",
                    document_id=document_id,
                    expected_evidence_type="interval",
                    max_results=policy.max_evidence_per_task,
                ),
                build(
                    title="Collect safety notes",
                    question="What safety warnings or safety notes relate to maintenance?",
                    strategy_hint=RetrievalStrategy.MAINTENANCE_LOOKUP.value,
                    answer_intent_hint="maintenance_report",
                    document_id=document_id,
                    expected_evidence_type="safety",
                    max_results=policy.max_evidence_per_task,
                ),
            ]

        return [
            build(
                title="Collect overview evidence",
                question=goal.user_input,
                strategy_hint=RetrievalStrategy.DOCUMENT_EXPLORATION.value,
                answer_intent_hint="research",
                document_id=document_id,
                expected_evidence_type="overview",
                max_results=policy.max_evidence_per_task,
            ),
            build(
                title="Collect direct evidence",
                question=goal.user_input,
                strategy_hint=RetrievalStrategy.GENERAL_HYBRID.value,
                answer_intent_hint="research",
                document_id=document_id,
                expected_evidence_type="direct_evidence",
                max_results=policy.max_evidence_per_task,
            ),
        ]

    @staticmethod
    def _comparison_topics(user_input: str) -> list[tuple[str, str, RetrievalStrategy]]:
        topics: list[tuple[str, str, RetrievalStrategy]] = []
        if "maintenance" in user_input:
            topics.append(
                (
                    "maintenance tasks",
                    "What maintenance tasks and intervals are described in this document?",
                    RetrievalStrategy.MAINTENANCE_LOOKUP,
                )
            )
        if "specification" in user_input or "operating limit" in user_input:
            topics.append(
                (
                    "technical specifications",
                    "What technical specifications or operating limits are described in this document?",
                    RetrievalStrategy.TECHNICAL_SPECIFICATION,
                )
            )
        if "safety" in user_input or "warning" in user_input:
            topics.append(
                (
                    "safety warnings",
                    "What safety warnings are described in this document?",
                    RetrievalStrategy.SECTION_LOOKUP,
                )
            )
        if "certificate" in user_input:
            topics.append(
                (
                    "certificate evidence",
                    "What certification or certificate evidence is described in this document?",
                    RetrievalStrategy.CERTIFICATION_LOOKUP,
                )
            )
        if not topics:
            topics = [
                (
                    "primary evidence",
                    f"What evidence is available for: {user_input}",
                    RetrievalStrategy.GENERAL_HYBRID,
                ),
                (
                    "related sections",
                    f"What related sections expand on: {user_input}",
                    RetrievalStrategy.SECTION_LOOKUP,
                ),
            ]
        return topics[:2]

    @staticmethod
    def _reason(goal_type: ResearchGoalType) -> str:
        return {
            ResearchGoalType.COMPARISON: "The request compares multiple evidence themes and needs cross-section retrieval.",
            ResearchGoalType.SUMMARY: "The request asks for a document-wide summary across many sections.",
            ResearchGoalType.CHECKLIST: "The request asks for a checklist assembled from procedures, prerequisites, and safety evidence.",
            ResearchGoalType.AUDIT: "The request requires structured cross-section evidence review.",
            ResearchGoalType.EVIDENCE_REVIEW: "The request asks for supporting evidence and missing evidence analysis.",
            ResearchGoalType.GAP_ANALYSIS: "The request explicitly asks to identify missing evidence.",
            ResearchGoalType.REPORT: "The request asks for a structured research report.",
            ResearchGoalType.GENERAL_RESEARCH: "The request needs broader document research than single-turn QA.",
        }[goal_type]
