from __future__ import annotations

from collections.abc import Iterable

from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.planning.plan_policy import PlanPolicy
from src.application.langgraph.routing import RouteDecision
from src.application.langgraph.state import AgentState

PLANNING_PROMPT_VERSION = "v1"

_TOOL_HINTS: dict[str, str] = {
    "list_documents": "List available documents in the corpus.",
    "find_document": "Resolve a document by query_text or document_id.",
    "document_details": "Get metadata/details for the current document.",
    "explore_document": "Explore section-level content for a selected document.",
    "retrieve_chunks": "Retrieve evidence chunks for a query.",
    "retrieve_identifiers": (
        "Search for specific identifiers such as part numbers, serial numbers, model numbers, "
        "certificate numbers, drawing numbers, component codes, or manufacturer names. "
        "Args: identifier_value (str, required), "
        "identifier_type (optional: 'part_number'|'serial_number'|'model_number'|"
        "'certificate_number'|'drawing_number'|'component_code'|'manufacturer_name'), "
        "document_id (optional, to scope to a single document)."
    ),
    "answer_question": "Answer a question using the existing QA workflow.",
    "run_quality_gate": "Run an evaluation quality gate.",
    "retrieval_trace": "Trace retrieval behavior for a query.",
}


class PlanPromptBuilder:
    def build(
        self,
        *,
        user_input: str,
        state: AgentState,
        route_decision: RouteDecision,
        tool_registry: ToolRegistry,
        policy: PlanPolicy,
    ) -> str:
        selected_document_id = state.get("selected_document_id")
        selected_document_title = state.get("selected_document_title")
        pending_clarification = state.get("pending_clarification")
        recent_history = self._history_summary(state.get("history", []))
        tool_lines = self._available_tool_lines(tool_registry, policy)

        return "\n".join(
            [
                "You are a planning component for a safe enterprise document agent.",
                "Return JSON only. Do not include markdown fences. Do not include explanations outside JSON.",
                f"Planning prompt version: {PLANNING_PROMPT_VERSION}",
                "",
                "Rules:",
                f"- Use only these allowed tools: {', '.join(tool_lines.keys()) or 'none'}",
                f"- Keep the plan to at most {policy.max_steps} steps.",
                "- Do not invent tools.",
                "- Do not propose ingestion, delete, or reingestion operations.",
                "- Prefer the selected document when one is already available.",
                "- If document choice is ambiguous, propose a clarification-friendly plan using find_document first.",
                "- Every step must include step_id, tool_name, description, args, output_key, depends_on, required.",
                "- Use query_text for retrieval and document lookup text.",
                "- Use question for answer_question.",
                "- Use document_id only when it is explicit and safe.",
                "",
                f"User request: {user_input}",
                f"Current route: {route_decision.route_type.value}",
                f"Route reason: {route_decision.reason}",
                f"Route confidence: {route_decision.confidence}",
                f"Selected document id: {selected_document_id or 'none'}",
                f"Selected document title: {selected_document_title or 'none'}",
                f"Pending clarification: {self._pending_clarification_text(pending_clarification)}",
                f"Recent conversation summary: {recent_history}",
                "",
                "Allowed tools:",
                *[
                    f"- {tool_name}: {description}"
                    for tool_name, description in tool_lines.items()
                ],
                "",
                "Expected JSON schema:",
                "{",
                '  "goal": "string",',
                '  "requires_document": true,',
                '  "reason": "string",',
                '  "steps": [',
                "    {",
                '      "step_id": "step_1",',
                '      "tool_name": "find_document",',
                '      "description": "Find the requested document",',
                '      "args": {"query_text": "pressure transmitter"},',
                '      "output_key": "document_lookup",',
                '      "depends_on": [],',
                '      "required": true',
                "    }",
                "  ]",
                "}",
            ]
        )

    def _available_tool_lines(
        self,
        tool_registry: ToolRegistry,
        policy: PlanPolicy,
    ) -> dict[str, str]:
        available = {}
        for tool_name in sorted(policy.allowed_tools):
            if tool_registry.get(tool_name) is None:
                continue
            available[tool_name] = _TOOL_HINTS.get(tool_name, "No description available.")
        return available

    @staticmethod
    def _pending_clarification_text(pending: object) -> str:
        if isinstance(pending, dict) and pending:
            kind = pending.get("kind") or "unknown"
            route = pending.get("route") or "unknown"
            return f"kind={kind}, route={route}"
        return "none"

    @staticmethod
    def _history_summary(history: Iterable[dict[str, object]]) -> str:
        summaries: list[str] = []
        for item in list(history)[-4:]:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            content = item.get("content")
            if not isinstance(role, str) or not isinstance(content, str):
                continue
            normalized = " ".join(content.split())
            if len(normalized) > 120:
                normalized = normalized[:117] + "..."
            summaries.append(f"{role}: {normalized}")
        return " | ".join(summaries) if summaries else "none"
