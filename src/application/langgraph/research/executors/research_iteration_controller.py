from __future__ import annotations

from src.application.langgraph.research.models import ResearchGap, ResearchTask
from src.application.langgraph.research.policies import (
    ResearchIterationPolicy,
    ResearchPolicy,
)
from src.shared.ids import IdGenerator


class ResearchIterationController:
    def __init__(self, *, id_generator: IdGenerator | None = None) -> None:
        self.id_generator = id_generator or IdGenerator()

    def build_followup_tasks(
        self,
        result,
        gaps: list[ResearchGap],
        *,
        iteration_policy: ResearchIterationPolicy,
        research_policy: ResearchPolicy,
    ) -> list[ResearchTask]:
        if not research_policy.allow_followup_research:
            return []
        if not iteration_policy.allow_followup_research:
            return []
        if result.iterations >= iteration_policy.max_iterations:
            return []

        tasks: list[ResearchTask] = []
        for gap in gaps:
            if not gap.can_retry or not gap.suggested_followup_query:
                continue
            tasks.append(
                ResearchTask(
                    task_id=self.id_generator.new_id("research_task"),
                    title=f"Follow-up research: {gap.description}",
                    question=gap.suggested_followup_query,
                    strategy_hint=gap.suggested_strategy,
                    answer_intent_hint="followup_research",
                    document_id=result.goal.document_id,
                    required=False,
                    depends_on=[gap.related_task_id] if gap.related_task_id else [],
                    expected_evidence_type="followup",
                    max_results=research_policy.max_evidence_per_task,
                    diagnostics={"followup_for_gap_id": gap.gap_id},
                )
            )
            if len(tasks) >= iteration_policy.max_followup_tasks:
                break
        return tasks
