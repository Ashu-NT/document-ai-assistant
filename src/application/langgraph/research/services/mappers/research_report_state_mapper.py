from __future__ import annotations

from typing import Any

from src.application.langgraph.research.models import ResearchReport


def report_from_dict(value: Any) -> ResearchReport | None:
    if not isinstance(value, dict):
        return None
    return ResearchReport(
        title=str(value.get("title") or ""),
        executive_summary=str(value.get("executive_summary") or ""),
        sections=[
            dict(section)
            for section in list(value.get("sections") or [])
            if isinstance(section, dict)
        ],
        findings=[
            str(item)
            for item in list(value.get("findings") or [])
            if str(item).strip()
        ],
        gaps=[
            dict(gap)
            for gap in list(value.get("gaps") or [])
            if isinstance(gap, dict)
        ],
        references=[
            dict(reference)
            for reference in list(value.get("references") or [])
            if isinstance(reference, dict)
        ],
        appendix=dict(value.get("appendix") or {}),
        diagnostics=dict(value.get("diagnostics") or {}),
    )
