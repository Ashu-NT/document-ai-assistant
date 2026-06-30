from __future__ import annotations

from typing import Any

from src.application.langgraph.research.models import ResearchReport
from src.application.langgraph.research.policies import ResearchSynthesisPolicy
from src.application.langgraph.research.presentation.research_citation_formatter import (
    ResearchCitationFormatter,
)


class EnterpriseResearchReportFormatter:
    def __init__(
        self,
        *,
        citation_formatter: ResearchCitationFormatter | None = None,
    ) -> None:
        self.citation_formatter = citation_formatter or ResearchCitationFormatter()

    def render(
        self,
        report: ResearchReport,
        *,
        policy: ResearchSynthesisPolicy,
    ) -> str:
        lines = [
            "=" * 50,
            report.title,
            "=" * 50,
            "",
            "Executive Summary",
            "-----------------",
            "",
        ]
        lines.extend(self._paragraph_lines(report.executive_summary))
        for section in report.sections:
            lines.extend(
                [
                    "",
                    self._section_title(section),
                    "-" * len(self._section_title(section)),
                    "",
                ]
            )
            findings = self._section_findings(section)
            if findings:
                for finding in findings:
                    citation = self.citation_formatter.format_inline_citation(finding)
                    lines.append(f"- {finding['text']} {citation}".strip())
            else:
                lines.append("No grounded findings were available for this section.")
        if report.gaps:
            lines.extend(["", "Missing Evidence", "----------------", ""])
            for gap in report.gaps:
                description = str(gap.get("description") or "").strip()
                if description:
                    lines.append(f"- {description}")
        if policy.include_references:
            reference_entries = self.citation_formatter.build_reference_entries(
                self._reference_payloads(report)
            )
            if reference_entries:
                lines.extend(["", "References", "----------", ""])
                for index, entry in enumerate(reference_entries, start=1):
                    page_list = self.citation_formatter.format_page_list(entry["page_spans"])
                    label = f"[{index}] {entry['document_name']}"
                    if page_list:
                        label = f"{label}, {page_list}"
                    lines.append(label)
                    if entry["sections"]:
                        lines.append(
                            f"    Sections: {'; '.join(entry['sections'][:3])}"
                        )
        return "\n".join(lines).strip()

    @staticmethod
    def _section_title(section: dict[str, Any]) -> str:
        return str(section.get("title") or "Section")

    @staticmethod
    def _section_findings(section: dict[str, Any]) -> list[dict[str, Any]]:
        findings = section.get("findings")
        if isinstance(findings, list):
            return [item for item in findings if isinstance(item, dict) and item.get("text")]
        return []

    @staticmethod
    def _paragraph_lines(text: str) -> list[str]:
        stripped = text.strip()
        if not stripped:
            return ["No executive summary was available."]
        lines: list[str] = []
        for paragraph in stripped.split("\n\n"):
            paragraph_text = paragraph.strip()
            if not paragraph_text:
                continue
            if lines:
                lines.append("")
            lines.extend(paragraph_text.splitlines())
        return lines or ["No executive summary was available."]

    def _reference_payloads(self, report: ResearchReport) -> list[dict[str, Any]]:
        if report.references:
            return [item for item in report.references if isinstance(item, dict)]
        references: list[dict[str, Any]] = []
        for section in report.sections:
            for finding in self._section_findings(section):
                references.append(finding)
        return references
