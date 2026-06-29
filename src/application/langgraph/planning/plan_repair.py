from __future__ import annotations

from dataclasses import dataclass, field

from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.planning.execution_plan import ExecutionPlan
from src.application.langgraph.planning.plan_policy import PlanPolicy
from src.application.langgraph.planning.plan_step import PlanStep
from src.application.langgraph.state import AgentState

_TOOL_NAME_RENAMES = {
    "retrieve_evidence": "retrieve_chunks",
    "ask_question": "answer_question",
    "lookup_document": "find_document",
}
_ALLOWED_ARGS: dict[str, set[str]] = {
    "list_documents": set(),
    "find_document": {"document_id", "query_text", "query"},
    "document_details": {"document_id"},
    "explore_document": {"document_id"},
    "retrieve_chunks": {"document_id", "query_text", "question", "top_k"},
    "answer_question": {"document_id", "question", "top_k"},
    "run_quality_gate": {"report_path", "thresholds_path"},
    "retrieval_trace": {"document_id", "query_text", "top_k", "write_output"},
}


@dataclass(slots=True, frozen=True)
class PlanRepairResult:
    repaired: bool
    plan: ExecutionPlan | None = None
    changes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class PlanRepair:
    def repair(
        self,
        plan: ExecutionPlan,
        *,
        policy: PlanPolicy,
        tool_registry: ToolRegistry,
        state: AgentState,
    ) -> PlanRepairResult:
        changes: list[str] = []
        repaired_steps: list[PlanStep] = []

        if any(
            blocked in step.tool_name and step.required
            for blocked in ("delete", "ingest", "reingest")
            for step in plan.steps
        ):
            return PlanRepairResult(
                repaired=False,
                errors=[
                    "Unsafe ingest/delete/reingest plans cannot be repaired deterministically."
                ],
            )

        for step in plan.steps:
            tool_name = _TOOL_NAME_RENAMES.get(step.tool_name, step.tool_name)
            if tool_name != step.tool_name:
                changes.append(f"Renamed tool '{step.tool_name}' to '{tool_name}'.")

            if tool_name in policy.blocked_tools and step.required:
                return PlanRepairResult(
                    repaired=False,
                    errors=[f"Blocked required step '{step.step_id}' cannot be repaired safely."],
                )
            if tool_name in policy.blocked_tools and not step.required:
                changes.append(f"Removed blocked optional step '{step.step_id}'.")
                continue

            args = dict(step.args)
            if tool_name == "find_document":
                query_value = args.pop("query", None)
                if query_value and "query_text" not in args:
                    args["query_text"] = query_value
                    changes.append("Normalized find_document arg 'query' to 'query_text'.")

            allowed_args = _ALLOWED_ARGS.get(tool_name)
            if allowed_args is not None:
                removed = sorted(set(args.keys()) - allowed_args)
                for key in removed:
                    args.pop(key, None)
                if removed:
                    changes.append(
                        f"Removed unsupported args from '{tool_name}': {', '.join(removed)}."
                    )

            if tool_name == "retrieve_chunks" and not (
                args.get("query_text") or args.get("question")
            ):
                fallback_query = state.get("question") or state.get("user_input")
                if isinstance(fallback_query, str) and fallback_query:
                    args["query_text"] = fallback_query
                    changes.append(
                        f"Added fallback query_text to '{tool_name}' step '{step.step_id}'."
                    )

            if tool_name == "retrieval_trace" and not args.get("query_text"):
                fallback_query = state.get("question") or state.get("user_input")
                if isinstance(fallback_query, str) and fallback_query:
                    args["query_text"] = fallback_query
                    changes.append(
                        f"Added fallback query_text to '{tool_name}' step '{step.step_id}'."
                    )

            if tool_name == "answer_question" and not args.get("question"):
                fallback_question = state.get("question") or state.get("user_input")
                if isinstance(fallback_question, str) and fallback_question:
                    args["question"] = fallback_question
                    changes.append(
                        f"Added fallback question to '{tool_name}' step '{step.step_id}'."
                    )

            if (
                tool_name
                in {
                    "retrieve_chunks",
                    "answer_question",
                    "explore_document",
                    "document_details",
                    "retrieval_trace",
                }
                and "document_id" not in args
            ):
                selected_document_id = state.get("selected_document_id") or state.get("document_id")
                if selected_document_id:
                    args["document_id"] = selected_document_id
                    changes.append(
                        f"Added selected document_id to '{tool_name}' step '{step.step_id}'."
                    )

            if tool_registry.get(tool_name) is None:
                if step.required:
                    return PlanRepairResult(
                        repaired=False,
                        errors=[
                            f"Required step '{step.step_id}' uses unavailable tool '{tool_name}'."
                        ],
                    )
                changes.append(
                    f"Removed optional step '{step.step_id}' because tool '{tool_name}' is unavailable."
                )
                continue

            repaired_steps.append(
                PlanStep(
                    step_id=step.step_id,
                    tool_name=tool_name,
                    description=step.description,
                    input_key=step.input_key,
                    output_key=step.output_key,
                    args=args,
                    depends_on=list(step.depends_on),
                    required=step.required,
                    source="repaired",
                )
            )

        if len(repaired_steps) > policy.max_steps:
            truncated: list[PlanStep] = []
            for step in repaired_steps:
                if len(truncated) >= policy.max_steps:
                    if step.required:
                        return PlanRepairResult(
                            repaired=False,
                            errors=["Plan exceeds max_steps and required trailing steps cannot be dropped."],
                        )
                    changes.append(f"Dropped optional trailing step '{step.step_id}' to satisfy max_steps.")
                    continue
                truncated.append(step)
            repaired_steps = truncated

        if repaired_steps == plan.steps:
            return PlanRepairResult(repaired=False, plan=plan, changes=changes)

        return PlanRepairResult(
            repaired=True,
            plan=ExecutionPlan(
                plan_id=plan.plan_id,
                goal=plan.goal,
                steps=repaired_steps,
                reason=plan.reason,
                source="repaired",
                requires_document=plan.requires_document,
                document_id=plan.document_id,
                document_title=plan.document_title,
                diagnostics=dict(plan.diagnostics),
            ),
            changes=changes,
        )
