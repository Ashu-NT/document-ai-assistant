from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.planning.execution_plan import ExecutionPlan
from src.application.langgraph.planning.plan_policy import PlanPolicy
from src.application.langgraph.state import AgentState

_SAFE_TOOL_NAME_RE = re.compile(r"^[a-z_][a-z0-9_]*$")
_SCOPED_TOOLS = {"answer_question", "explore_document", "document_details"}
_RETRIEVAL_TOOLS = {"retrieve_chunks", "retrieval_trace"}
_MUTATING_TOOL_MARKERS = ("ingest", "delete", "reingest", "remove", "replace")
_UNSAFE_TOOL_MARKERS = (
    "bash",
    "cmd",
    "curl",
    "docling",
    "llmservice",
    "powershell",
    "python",
    "qdrant",
    "repo",
    "repository",
    "shell",
    "sqlalchemy",
    "wget",
)
_KNOWN_ARGS: dict[str, set[str]] = {
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
class PlanValidationResult:
    success: bool
    validated_plan: ExecutionPlan | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)


class PlanValidator:
    def validate(
        self,
        plan: ExecutionPlan,
        *,
        policy: PlanPolicy,
        tool_registry: ToolRegistry,
        state: AgentState,
    ) -> PlanValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        seen_step_ids: set[str] = set()
        seen_output_keys: set[str] = set()
        previous_step_ids: set[str] = set()
        previous_output_keys: set[str] = set()
        has_document_resolution = bool(
            plan.document_id or state.get("document_id") or state.get("selected_document_id")
        )

        if plan.step_count > policy.max_steps:
            errors.append(
                f"Plan exceeds the maximum allowed step count ({policy.max_steps})."
            )

        for step in plan.steps:
            if step.step_id in seen_step_ids:
                errors.append(f"Duplicate step_id '{step.step_id}' is not allowed.")
            seen_step_ids.add(step.step_id)

            if step.output_key in seen_output_keys:
                errors.append(f"Duplicate output_key '{step.output_key}' is not allowed.")
            seen_output_keys.add(step.output_key)

            if not _SAFE_TOOL_NAME_RE.fullmatch(step.tool_name):
                errors.append(f"Tool name '{step.tool_name}' is not safe.")
            if any(marker in step.tool_name for marker in _UNSAFE_TOOL_MARKERS):
                errors.append(f"Tool name '{step.tool_name}' refers to unsafe infrastructure.")

            if step.tool_name in policy.blocked_tools:
                errors.append(f"Tool '{step.tool_name}' is blocked by plan policy.")
            if step.tool_name not in policy.allowed_tools:
                errors.append(f"Tool '{step.tool_name}' is not allowed by plan policy.")
            if tool_registry.get(step.tool_name) is None:
                errors.append(f"Tool '{step.tool_name}' is not available in the ToolRegistry.")

            if not policy.allow_mutating_tools and self._looks_mutating(step.tool_name):
                errors.append(f"Tool '{step.tool_name}' looks mutating and is not allowed.")

            serialized_args = json.dumps(step.args, default=str)
            if len(serialized_args) > policy.max_tool_arg_chars:
                errors.append(
                    f"Tool '{step.tool_name}' exceeds the maximum allowed argument size."
                )

            if not isinstance(step.args, dict):
                errors.append(f"Tool '{step.tool_name}' must have object args.")

            self._validate_required_args(step.tool_name, step.args, errors)
            self._validate_dependencies(
                step.depends_on,
                previous_step_ids,
                previous_output_keys,
                errors,
            )
            self._validate_document_scope(
                step_tool_name=step.tool_name,
                step_args=step.args,
                policy=policy,
                state=state,
                has_document_resolution=has_document_resolution,
                errors=errors,
                warnings=warnings,
            )
            self._validate_document_mismatch(step, state, errors)

            if step.tool_name == "find_document":
                has_document_resolution = True
            previous_step_ids.add(step.step_id)
            previous_output_keys.add(step.output_key)

        return PlanValidationResult(
            success=not errors,
            validated_plan=plan if not errors else None,
            errors=errors,
            warnings=warnings,
            diagnostics={
                "step_count": plan.step_count,
                "plan_source": plan.source,
            },
        )

    @staticmethod
    def _looks_mutating(tool_name: str) -> bool:
        return any(marker in tool_name for marker in _MUTATING_TOOL_MARKERS)

    def _validate_required_args(
        self,
        tool_name: str,
        args: dict[str, Any],
        errors: list[str],
    ) -> None:
        if tool_name == "find_document":
            if not (args.get("query_text") or args.get("query") or args.get("document_id")):
                errors.append("Tool 'find_document' requires query_text or document_id.")
        elif tool_name == "retrieve_chunks" and not (
            args.get("query_text") or args.get("question")
        ):
            errors.append("Tool 'retrieve_chunks' requires query_text or question.")
        elif tool_name == "answer_question" and not args.get("question"):
            errors.append("Tool 'answer_question' requires question.")
        elif tool_name == "retrieval_trace" and not args.get("query_text"):
            errors.append("Tool 'retrieval_trace' requires query_text.")
        unknown_args = set(args.keys()) - _KNOWN_ARGS.get(tool_name, set())
        if unknown_args:
            errors.append(
                f"Tool '{tool_name}' contains unsupported args: {', '.join(sorted(unknown_args))}."
            )

    @staticmethod
    def _validate_dependencies(
        depends_on: list[str],
        previous_step_ids: set[str],
        previous_output_keys: set[str],
        errors: list[str],
    ) -> None:
        for dependency in depends_on:
            if dependency not in previous_step_ids and dependency not in previous_output_keys:
                errors.append(
                    "Dependency "
                    f"'{dependency}' must reference an existing previous step_id or output_key."
                )

    def _validate_document_scope(
        self,
        *,
        step_tool_name: str,
        step_args: dict[str, Any],
        policy: PlanPolicy,
        state: AgentState,
        has_document_resolution: bool,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        if step_tool_name in _SCOPED_TOOLS:
            if not policy.require_document_scope_for_qa:
                return
            if not (
                step_args.get("document_id")
                or has_document_resolution
                or state.get("document_query")
            ):
                errors.append(
                    f"Tool '{step_tool_name}' requires a document-scoped plan."
                )
            return

        if step_tool_name in _RETRIEVAL_TOOLS and not policy.allow_corpus_wide_retrieval:
            if not (
                step_args.get("document_id")
                or has_document_resolution
                or state.get("document_query")
            ):
                errors.append(
                    f"Tool '{step_tool_name}' requires document scope under the current policy."
                )
            return

        if step_tool_name in _RETRIEVAL_TOOLS and not (
            step_args.get("document_id")
            or has_document_resolution
            or state.get("document_query")
        ):
            warnings.append(
                f"Tool '{step_tool_name}' will run corpus-wide because no document scope is resolved."
            )

    @staticmethod
    def _validate_document_mismatch(
        step,
        state: AgentState,
        errors: list[str],
    ) -> None:
        explicit_request_document_id = state.get("document_id")
        selected_document_id = state.get("selected_document_id")
        requested_document_id = step.args.get("document_id")
        if not isinstance(requested_document_id, str) or not requested_document_id:
            return
        if explicit_request_document_id:
            return
        if selected_document_id and requested_document_id != selected_document_id:
            errors.append(
                "Plan step document_id does not match the selected document and was not explicitly requested."
            )
