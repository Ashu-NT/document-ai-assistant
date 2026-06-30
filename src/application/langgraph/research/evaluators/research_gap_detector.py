from __future__ import annotations

from src.application.langgraph.research.models import (
    ResearchGap,
    ResearchGapSeverity,
)
from src.application.langgraph.research.models.research_goal import ResearchGoalType
from src.shared.ids import IdGenerator


class ResearchGapDetector:
    def __init__(self, *, id_generator: IdGenerator | None = None) -> None:
        self.id_generator = id_generator or IdGenerator()

    def detect(self, result, *, coverage: dict) -> list[ResearchGap]:
        gaps: list[ResearchGap] = []
        task_result_map = {task_result.task_id: task_result for task_result in result.task_results}

        for task in result.plan.tasks:
            task_result = task_result_map.get(task.task_id)
            if task.required and (task_result is None or not task_result.evidence):
                gaps.append(
                    ResearchGap(
                        gap_id=self.id_generator.new_id("research_gap"),
                        description=f"Required task '{task.title}' did not return evidence.",
                        severity=ResearchGapSeverity.HIGH,
                        related_task_id=task.task_id,
                        suggested_followup_query=task.question,
                        suggested_strategy=task.strategy_hint,
                        can_retry=True,
                    )
                )

        if (
            result.goal.goal_type == ResearchGoalType.COMPARISON
            and sum(1 for task_result in result.task_results if task_result.evidence) < 2
        ):
            gaps.append(
                ResearchGap(
                    gap_id=self.id_generator.new_id("research_gap"),
                    description="Comparison evidence is one-sided.",
                    severity=ResearchGapSeverity.HIGH,
                    related_task_id=None,
                    suggested_followup_query=result.goal.user_input,
                    suggested_strategy=None,
                    can_retry=True,
                )
            )

        if result.goal.requires_cross_section_reasoning and coverage.get("section_count", 0) <= 1:
            gaps.append(
                ResearchGap(
                    gap_id=self.id_generator.new_id("research_gap"),
                    description="Evidence came from too few sections for cross-section reasoning.",
                    severity=ResearchGapSeverity.MEDIUM,
                    related_task_id=None,
                    suggested_followup_query=result.goal.user_input,
                    suggested_strategy=None,
                    can_retry=True,
                )
            )

        if result.goal.goal_type == ResearchGoalType.CHECKLIST:
            safety_hits = sum(
                1
                for task in result.plan.tasks
                if "safety" in task.title.lower()
                and task_result_map.get(task.task_id) is not None
                and task_result_map[task.task_id].evidence
            )
            if safety_hits == 0:
                gaps.append(
                    ResearchGap(
                        gap_id=self.id_generator.new_id("research_gap"),
                        description="Checklist evidence is missing safety support.",
                        severity=ResearchGapSeverity.MEDIUM,
                        related_task_id=None,
                        suggested_followup_query="What safety warnings apply to this checklist request?",
                        suggested_strategy=None,
                        can_retry=True,
                    )
                )

        return gaps
