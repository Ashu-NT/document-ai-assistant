from __future__ import annotations

from src.application.validation.common import ValidationResult, Validator


class ResearchReportValidator(Validator):
    def validate(self, value) -> ValidationResult:
        result = ValidationResult()
        title = getattr(value, "title", "")
        executive_summary = getattr(value, "executive_summary", "")
        sections = getattr(value, "sections", [])

        if not isinstance(title, str) or not title.strip():
            result.add_issue("title", "Research report title cannot be empty.", "research.report.title.required")
        if not isinstance(executive_summary, str) or not executive_summary.strip():
            result.add_issue(
                "executive_summary",
                "Research report executive summary cannot be empty.",
                "research.report.executive_summary.required",
            )
        if not isinstance(sections, list) or not sections:
            result.add_issue("sections", "Research report must contain at least one section.", "research.report.sections.required")
        return result
