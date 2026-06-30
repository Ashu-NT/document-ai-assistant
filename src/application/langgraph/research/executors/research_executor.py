from __future__ import annotations

from src.application.langgraph.research.models import ResearchResult
from src.application.langgraph.research.executors.research_task_executor import (
    ResearchTaskExecutor,
)


class ResearchExecutor:
    def __init__(
        self,
        *,
        task_executor: ResearchTaskExecutor | None = None,
    ) -> None:
        self.task_executor = task_executor or ResearchTaskExecutor()

    def execute(
        self,
        plan,
        *,
        tool_registry,
        current_result: ResearchResult | None = None,
        use_llm_strategy: bool = False,
    ) -> ResearchResult:
        completed_task_ids = {
            task_result.task_id for task_result in (current_result.task_results if current_result else [])
        }
        task_results = list(current_result.task_results) if current_result else []
        evidence = list(current_result.evidence) if current_result else []
        errors = list(current_result.errors) if current_result else []

        successful_task_ids = {
            task_result.task_id
            for task_result in task_results
            if task_result.success
        }
        for task in plan.tasks:
            if task.task_id in completed_task_ids:
                continue
            if any(dependency not in successful_task_ids for dependency in task.depends_on):
                result = self._dependency_failure(task.task_id)
            else:
                result = self.task_executor.execute(
                    task,
                    route="deep_research",
                    document_title=plan.goal.document_title,
                    tool_registry=tool_registry,
                    use_llm_strategy=use_llm_strategy,
                )
            task_results.append(result)
            evidence.extend(result.evidence)
            if result.success:
                successful_task_ids.add(task.task_id)
                continue
            errors.extend(result.errors or [f"{task.task_id}_failed"])
            if task.required:
                return ResearchResult(
                    success=False,
                    goal=plan.goal,
                    plan=plan,
                    task_results=task_results,
                    evidence=evidence,
                    gaps=list(current_result.gaps) if current_result else [],
                    iterations=current_result.iterations if current_result else 0,
                    errors=errors,
                    diagnostics={"failed_task_id": task.task_id},
                )

        return ResearchResult(
            success=True,
            goal=plan.goal,
            plan=plan,
            task_results=task_results,
            evidence=evidence,
            gaps=list(current_result.gaps) if current_result else [],
            iterations=current_result.iterations if current_result else 0,
            errors=errors,
            diagnostics={"executed_task_count": len(task_results)},
        )

    @staticmethod
    def _dependency_failure(task_id: str):
        from src.application.langgraph.research.models import ResearchTaskResult

        return ResearchTaskResult(
            task_id=task_id,
            success=False,
            errors=["research_task_dependency_failed"],
        )
