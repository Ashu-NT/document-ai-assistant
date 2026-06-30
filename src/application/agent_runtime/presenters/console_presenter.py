from __future__ import annotations

from typing import Any

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.policies.demo_visibility_policy import (
    DemoVisibilityPolicy,
)
from src.application.agent_runtime.react_loop.react_presenter import ReactPresenter
from src.application.agent_runtime.react_loop.react_trace import ReactTrace


class ConsolePresenter:
    def __init__(self, react_presenter: ReactPresenter | None = None) -> None:
        self.react_presenter = react_presenter or ReactPresenter()

    def render_command_result(
        self,
        result: CommandResult,
        *,
        session,
        policy: DemoVisibilityPolicy,
    ) -> str:
        render_as = result.render_as
        if render_as == "help":
            return _render_help(result.data)
        if render_as == "documents":
            return _render_documents(result.data.get("documents", []))
        if render_as == "document_selected":
            return _render_document_selected(result.data.get("selected_document"), session)
        if render_as == "current_document":
            return _render_current_document(result.data.get("document_name"))
        if render_as == "history":
            return _render_history(result.data.get("turns", []))
        if render_as == "trace":
            trace = result.data.get("trace")
            if isinstance(trace, ReactTrace):
                return self.react_presenter.render(trace, policy=policy)
        if render_as == "context":
            return _render_context_chunks(
                result.data.get("context_chunks", []),
                policy=policy,
            )
        if render_as == "status":
            return _render_key_values("Runtime Status", result.data)
        if render_as == "settings":
            return _render_key_values("Runtime Settings", result.data)
        if render_as == "export":
            return _render_export(result.data)
        return result.message

    def render_graph_result(
        self,
        *,
        user_input: str,
        result,
        react_trace: ReactTrace | None,
        session,
        policy: DemoVisibilityPolicy,
        show_react: bool,
    ) -> str:
        lines = [
            "User Request",
            "------------",
            _console_safe_text(user_input),
            "",
        ]
        if show_react and react_trace is not None:
            trace_text = self.react_presenter.render(react_trace, policy=policy)
            if trace_text:
                lines.extend([trace_text, ""])
        lines.extend(
            [
                "Final Answer",
                "------------",
                _console_safe_text((result.data or {}).get("answer") or result.response_text or ""),
                "",
            ]
        )
        footer = _render_status_footer(result, session=session)
        if footer:
            lines.append(footer)
        return "\n".join(line for line in lines if line is not None).rstrip()


def _render_help(data: dict[str, Any]) -> str:
    groups = data.get("groups", {})
    examples = data.get("examples", [])
    lines: list[str] = []
    command_width = _help_command_width(groups)
    for group_name, commands in groups.items():
        lines.extend([group_name, "-" * len(group_name)])
        for command in commands:
            if isinstance(command, dict):
                command_text = str(command.get("command") or "").strip()
                description = str(command.get("description") or "").strip()
                if command_text and description:
                    lines.append(
                        f"{command_text.ljust(command_width)} -- {description}"
                    )
                    continue
                if command_text:
                    lines.append(command_text)
                    continue
            lines.append(str(command))
        lines.append("")
    if examples:
        lines.extend(["Examples", "--------"])
        for example in examples:
            lines.append(f"- {example}")
    return "\n".join(lines).rstrip()


def _help_command_width(groups: dict[str, Any]) -> int:
    width = 0
    for commands in groups.values():
        if not isinstance(commands, list):
            continue
        for command in commands:
            if not isinstance(command, dict):
                width = max(width, len(str(command)))
                continue
            command_text = str(command.get("command") or "").strip()
            width = max(width, len(command_text))
    return max(width, 18)


def _render_documents(documents: list[dict[str, Any]]) -> str:
    lines = ["Indexed Documents", ""]
    if not documents:
        lines.append("No indexed documents were found.")
        return "\n".join(lines)
    for index, document in enumerate(documents, start=1):
        title = (
            document.get("display_name")
            or document.get("title")
            or document.get("file_name")
            or f"Document {index}"
        )
        lines.append(f"{index}. {title}")
    return "\n".join(lines)


def _render_document_selected(selected_document: Any, session) -> str:
    document_name = None
    if isinstance(selected_document, dict):
        document_name = selected_document.get("title") or selected_document.get("file_name")
    if not document_name:
        document_name = session.selected_document.display_name
    lines = [
        "[ok] Selected document",
        "",
        str(document_name or "-"),
        "",
        "All following questions will use this document.",
    ]
    return "\n".join(lines)


def _render_current_document(document_name: str | None) -> str:
    if not document_name:
        return "No document is currently selected."
    return "\n".join(
        [
            "Current document:",
            str(document_name),
        ]
    )


def _render_history(turns: list[Any]) -> str:
    lines = ["Conversation History", ""]
    for index, turn in enumerate(turns, start=1):
        role = getattr(turn, "role", "unknown")
        content = getattr(turn, "content", "")
        lines.append(f"{index}. {str(role).title()}: {_preview_text(content, 140)}")
    return "\n".join(lines).rstrip()


def _render_key_values(title: str, payload: dict[str, Any]) -> str:
    lines = [title, "-" * len(title)]
    for key, value in payload.items():
        if value is None:
            continue
        if isinstance(value, str) and not value:
            continue
        if isinstance(value, list) and not value:
            continue
        label = str(key).replace("_", " ").title()
        lines.append(f"{label}: {value}")
    return "\n".join(lines)


def _render_export(payload: dict[str, Any]) -> str:
    lines = ["Trace saved:"]
    markdown_path = payload.get("markdown_path")
    json_path = payload.get("json_path")
    if markdown_path:
        lines.append(f"- Markdown: {markdown_path}")
    if json_path:
        lines.append(f"- JSON: {json_path}")
    return "\n".join(lines)


def _render_context_chunks(
    context_chunks: list[dict[str, Any]],
    *,
    policy: DemoVisibilityPolicy,
) -> str:
    lines = ["Retrieved Context", "-----------------"]
    if not context_chunks:
        lines.append("No context chunks available.")
        return "\n".join(lines)
    for index, chunk in enumerate(context_chunks, start=1):
        if not isinstance(chunk, dict):
            continue
        title = _chunk_label(chunk)
        chunk_type = str(chunk.get("chunk_type") or "unknown")
        document_title = str(chunk.get("document_title") or "-")
        section_text = _section_path_text(chunk.get("section_path"))
        pages = _page_range_label(chunk)
        score = chunk.get("score")
        score_text = f"{float(score):.4f}" if isinstance(score, int | float) else "-"
        lines.append(f"[{index}] {title} | {chunk_type}")
        lines.append(f"  document: {document_title}")
        if section_text:
            lines.append(f"  section:  {section_text}")
        if pages:
            lines.append(f"  pages:    {pages}")
        if score_text != "-":
            lines.append(f"  score:    {score_text}")
        lines.append(
            f"  content:  {_preview_text(chunk.get('content'), policy.max_observation_chars)}"
        )
        if policy.show_internal_ids and chunk.get("document_id"):
            lines.append(f"  document_id: {chunk.get('document_id')}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _render_status_footer(result, *, session) -> str:
    data = result.data or {}
    fields = []
    if session.selected_document.display_name:
        fields.append(("Document", session.selected_document.display_name))
    if result.route:
        fields.append(("Route", result.route))
        fields.append(("Mode", _route_mode_label(result.route)))
    strategy = _strategy_label(data)
    if strategy:
        fields.append(("Strategy", strategy))
    reflection = data.get("reflection_decision") or _reflection_decision(data)
    if reflection:
        fields.append(("Reflection", reflection))
    source_count = len(data.get("citations", []) or [])
    if source_count:
        fields.append(("Sources", source_count))
    elapsed_seconds = _elapsed_seconds(result.trace or [])
    if elapsed_seconds is not None:
        fields.append(("Elapsed", f"{elapsed_seconds:.1f} s"))
    if not fields:
        return ""
    lines = ["--------------------------------------------------"]
    for label, value in fields:
        if value in {None, ""}:
            continue
        lines.append(f"{label:<11}: {value}")
    lines.append("--------------------------------------------------")
    return "\n".join(lines)


def _route_mode_label(route: str) -> str:
    mapping = {
        "deep_research": "Deep Research",
        "planned_task": "Planned Task",
        "answer_question": "Question Answering",
        "retrieve_evidence": "Evidence Retrieval",
        "out_of_scope": "Scope Redirect",
        "blocked_action": "Safety Block",
    }
    return mapping.get(route, route.replace("_", " ").title())


def _strategy_label(data: dict[str, Any]) -> str | None:
    decision = data.get("retrieval_strategy_decision")
    if isinstance(decision, dict):
        primary = decision.get("primary_strategy")
        secondaries = decision.get("secondary_strategies") or []
        if primary and secondaries:
            return f"{primary} + {', '.join(str(item) for item in secondaries)}"
        if primary:
            return str(primary)
    research_plan = data.get("research_plan")
    if isinstance(research_plan, dict):
        tasks = research_plan.get("tasks") or []
        hints = []
        for task in tasks:
            if not isinstance(task, dict):
                continue
            hint = task.get("strategy_hint")
            if isinstance(hint, str) and hint not in hints:
                hints.append(hint)
        if hints:
            return " + ".join(hints[:2])
    return None


def _reflection_decision(data: dict[str, Any]) -> str | None:
    reflection_result = data.get("reflection_result")
    if not isinstance(reflection_result, dict):
        return None
    decision = (reflection_result.get("decision") or {}).get("decision")
    if isinstance(decision, str) and decision:
        return decision
    return None


def _elapsed_seconds(trace_entries: list[dict[str, Any]]) -> float | None:
    if not trace_entries:
        return None
    total_ms = 0.0
    for entry in trace_entries:
        if not isinstance(entry, dict):
            continue
        elapsed = entry.get("elapsed_ms")
        if isinstance(elapsed, int | float):
            total_ms += float(elapsed)
    if total_ms <= 0:
        return None
    return total_ms / 1000.0


def _chunk_label(chunk: dict[str, Any]) -> str:
    title = chunk.get("section_title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    path = chunk.get("section_path") or []
    if isinstance(path, list) and path:
        return str(path[-1])
    return str(chunk.get("chunk_type") or "Chunk")


def _section_path_text(section_path: Any) -> str:
    if not isinstance(section_path, list) or not section_path:
        return ""
    tail = [str(part) for part in section_path[-2:]]
    return " -> ".join(tail)


def _page_range_label(chunk: dict[str, Any]) -> str:
    source = chunk.get("source") or {}
    if not isinstance(source, dict):
        return ""
    page_start = source.get("page_start")
    page_end = source.get("page_end")
    if page_start is None:
        return ""
    if page_end is None or page_start == page_end:
        return f"p.{page_start}"
    return f"pp.{page_start}-{page_end}"


def _preview_text(value: Any, limit: int) -> str:
    text = str(value or "").strip()
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def _console_safe_text(value: str) -> str:
    return value.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
