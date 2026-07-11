from __future__ import annotations

from typing import Any

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.common.chunk_label_formatter import chunk_display_title
from src.application.agent_runtime.common.page_label_formatter import format_page_range_label
from src.application.agent_runtime.policies.demo_visibility_policy import (
    DemoVisibilityPolicy,
)
from src.application.agent_runtime.react_loop.react_presenter import ReactPresenter
from src.application.agent_runtime.react_loop.react_trace import ReactTrace
from src.shared.text.text_preview import preview_text


def render_command_result(
    result: CommandResult,
    *,
    session,
    policy: DemoVisibilityPolicy,
    react_presenter: ReactPresenter,
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
            return react_presenter.render(trace, policy=policy)
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
        lines.append(f"{index}. {str(role).title()}: {preview_text(content, 140)}")
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
        title = chunk_display_title(chunk, fallback="Chunk")
        chunk_type = str(chunk.get("chunk_type") or "unknown")
        document_title = str(chunk.get("document_title") or "-")
        section_text = _section_path_text(chunk.get("section_path"))
        pages = format_page_range_label(chunk.get("source"))
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
            f"  content:  {preview_text(chunk.get('content'), policy.max_observation_chars)}"
        )
        if policy.show_internal_ids and chunk.get("document_id"):
            lines.append(f"  document_id: {chunk.get('document_id')}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _section_path_text(section_path: Any) -> str:
    if not isinstance(section_path, list) or not section_path:
        return ""
    tail = [str(part) for part in section_path[-2:]]
    return " -> ".join(tail)
