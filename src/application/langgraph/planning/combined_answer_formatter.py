from __future__ import annotations

from typing import Any

from src.application.tools.common import ToolResult


def format_combined_answer(*, step, step_outputs: dict[str, dict[str, Any]]) -> ToolResult:
    labels = list(step.args.get("section_labels", []))
    sections: list[str] = []
    for index, dependency in enumerate(step.depends_on):
        label = labels[index] if index < len(labels) else f"Section {index + 1}"
        payload = step_outputs.get(dependency, {}).get("data")
        body = extract_answer_text(payload)
        sections.append(f"{label}:\n{body}")
    body_text = "\n\n".join(sections).strip()
    if body_text:
        summary = "Comparison summary: both sections were answered from the selected document."
        text = f"{body_text}\n\n{summary}"
    else:
        text = "No combined answer could be produced."
    return ToolResult.ok(data={"text": text})


def extract_answer_text(payload: Any) -> str:
    if isinstance(payload, dict):
        return (
            str(payload.get("answer_text") or "")
            or str(payload.get("safe_user_message") or "")
            or str(payload.get("response_text") or "")
        ).strip() or "No answer was available."
    return "No answer was available."
