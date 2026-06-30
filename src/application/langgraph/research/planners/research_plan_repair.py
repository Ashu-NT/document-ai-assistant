from __future__ import annotations

from dataclasses import replace

from src.application.langgraph.research.models import ResearchPlan, ResearchTask
from src.application.langgraph.research.policies import ResearchPolicy
from src.application.langgraph.retrieval_strategy import (
    CLI_RETRIEVAL_STRATEGY_ALIASES,
)
from src.application.langgraph.retrieval_strategy.models import RetrievalStrategy

_UNSAFE_MUTATION_MARKERS = ("delete", "reingest", "ingest", "remove", "replace")


class ResearchPlanRepair:
    def repair(
        self,
        plan: ResearchPlan,
        *,
        document_id: str | None,
        policy: ResearchPolicy,
    ) -> tuple[ResearchPlan, dict]:
        changes: list[str] = []
        repaired_tasks: list[ResearchTask] = []
        allowed_strategies = {strategy.value for strategy in RetrievalStrategy}

        for task in plan.tasks:
            lowered = f"{task.title} {task.question}".lower()
            if any(marker in lowered for marker in _UNSAFE_MUTATION_MARKERS):
                if task.required:
                    return plan, {"changes": changes, "errors": ["Unsafe required research task cannot be repaired."]}
                changes.append(f"Removed unsafe optional task '{task.task_id}'.")
                continue

            strategy_hint = task.strategy_hint
            if isinstance(strategy_hint, str):
                normalized = strategy_hint.strip()
                alias_match = CLI_RETRIEVAL_STRATEGY_ALIASES.get(normalized.lower())
                if alias_match is not None:
                    strategy_hint = alias_match.value
                    changes.append(f"Normalized strategy hint '{task.strategy_hint}' to '{strategy_hint}'.")
                elif normalized.upper() in allowed_strategies:
                    strategy_hint = normalized.upper()
                elif task.required:
                    return plan, {
                        "changes": changes,
                        "errors": [f"Unknown required strategy hint '{task.strategy_hint}' cannot be repaired."],
                    }
                else:
                    changes.append(f"Removed optional task '{task.task_id}' with unknown strategy hint.")
                    continue

            resolved_document_id = task.document_id or document_id
            if resolved_document_id and task.document_id is None:
                changes.append(f"Added selected document_id to task '{task.task_id}'.")

            repaired_tasks.append(
                replace(
                    task,
                    strategy_hint=strategy_hint,
                    document_id=resolved_document_id,
                )
            )

        if len(repaired_tasks) > policy.max_tasks:
            kept_tasks = repaired_tasks[: policy.max_tasks]
            dropped_required = any(task.required for task in repaired_tasks[policy.max_tasks :])
            if dropped_required:
                return plan, {
                    "changes": changes,
                    "errors": ["Required trailing research tasks cannot be dropped to satisfy max_tasks."],
                }
            dropped_ids = [task.task_id for task in repaired_tasks[policy.max_tasks :]]
            changes.append(
                "Dropped optional research tasks to satisfy max_tasks: "
                + ", ".join(dropped_ids)
            )
            repaired_tasks = kept_tasks

        return replace(plan, tasks=repaired_tasks, source="repaired"), {"changes": changes, "errors": []}
