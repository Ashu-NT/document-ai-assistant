from __future__ import annotations

import re

from src.application.langgraph.research.models import ResearchGoalType
from src.application.langgraph.research.policies import ResearchPolicy, ResearchTaskPolicy
from src.application.langgraph.research.validation.research_task_validator import (
    ResearchTaskValidator,
)
from src.application.validation.common import ValidationResult, Validator


class ResearchPlanValidator(Validator):
    def __init__(
        self,
        *,
        policy: ResearchPolicy | None = None,
        task_policy: ResearchTaskPolicy | None = None,
    ) -> None:
        self.policy = policy or ResearchPolicy()
        self.task_policy = task_policy or ResearchTaskPolicy()
        self.task_validator = ResearchTaskValidator(policy=self.task_policy)

    def validate(self, value) -> ValidationResult:
        result = ValidationResult()
        tasks = list(getattr(value, "tasks", []))
        goal = getattr(value, "goal", None)
        max_iterations = getattr(value, "max_iterations", 0)

        if goal is None:
            result.add_issue("goal", "Research plan goal is required.", "research.plan.goal.required")
            return result

        if getattr(goal, "goal_type", None) not in set(ResearchGoalType):
            result.add_issue("goal.goal_type", "Research goal type is invalid.", "research.plan.goal_type.invalid")

        if len(tasks) == 0:
            result.add_issue("tasks", "Research plan must contain at least one task.", "research.plan.tasks.required")
        if len(tasks) > self.policy.max_tasks:
            result.add_issue("tasks", "Research plan exceeds the maximum allowed task count.", "research.plan.tasks.too_many")

        if self.policy.require_document_scope and getattr(goal, "requires_document", False) and not getattr(goal, "document_id", None):
            result.add_issue("goal.document_id", "Research plan requires a selected document.", "research.plan.document_id.required")

        seen_ids: set[str] = set()
        available_dependencies: set[str] = set()
        for index, task in enumerate(tasks):
            task_validation = self.task_validator.validate(task)
            for issue in task_validation.issues:
                result.add_issue(
                    f"tasks[{index}].{issue.field}",
                    issue.message,
                    issue.code,
                )
            task_id = getattr(task, "task_id", None)
            if not task_id:
                result.add_issue(f"tasks[{index}].task_id", "Research task_id is required.", "research.plan.task_id.required")
            elif task_id in seen_ids:
                result.add_issue(f"tasks[{index}].task_id", "Duplicate research task_id is not allowed.", "research.plan.task_id.duplicate")
            else:
                seen_ids.add(task_id)

            for dependency in list(getattr(task, "depends_on", [])):
                if dependency not in available_dependencies:
                    result.add_issue(
                        f"tasks[{index}].depends_on",
                        "Research task dependency must reference an earlier task.",
                        "research.plan.depends_on.invalid",
                    )
            if task_id:
                available_dependencies.add(task_id)

        if not isinstance(max_iterations, int) or max_iterations < 0 or max_iterations > self.policy.max_iterations:
            result.add_issue(
                "max_iterations",
                "Research plan max_iterations is outside the allowed range.",
                "research.plan.max_iterations.invalid",
            )
        self._validate_goal_specific_rules(
            goal_type=getattr(goal, "goal_type", None),
            tasks=tasks,
            result=result,
        )
        return result

    def _validate_goal_specific_rules(
        self,
        *,
        goal_type,
        tasks: list[object],
        result: ValidationResult,
    ) -> None:
        if goal_type != ResearchGoalType.COMPARISON:
            return

        required_tasks = [
            task
            for task in tasks
            if getattr(task, "required", True)
        ]
        if len(required_tasks) < 2:
            result.add_issue(
                "tasks",
                "Comparison research plans must contain at least two required tasks.",
                "research.plan.comparison.tasks.required",
            )
            return

        themes = {
            theme
            for theme in (
                self._task_theme(task)
                for task in required_tasks
            )
            if theme
        }
        if len(themes) < 2:
            result.add_issue(
                "tasks",
                "Comparison research plans must cover at least two distinct task themes.",
                "research.plan.comparison.themes.required",
            )

    def _task_theme(self, task: object) -> str | None:
        for candidate in (
            getattr(task, "expected_evidence_type", None),
            getattr(task, "strategy_hint", None),
            getattr(task, "title", None),
            getattr(task, "question", None),
        ):
            if not isinstance(candidate, str):
                continue
            normalized = self._normalize_theme(candidate)
            if normalized:
                return normalized
        return None

    @staticmethod
    def _normalize_theme(value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", " ", value.strip().lower())
        return " ".join(normalized.split())
