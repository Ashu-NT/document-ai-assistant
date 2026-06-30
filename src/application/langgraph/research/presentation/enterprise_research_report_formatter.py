from __future__ import annotations

from typing import Any

from src.application.langgraph.research.models import ResearchReport
from src.application.langgraph.research.policies import ResearchSynthesisPolicy
from src.application.langgraph.research.presentation.research_citation_formatter import (
    ResearchCitationFormatter,
)
from src.application.langgraph.research.presentation.research_section_title_mapper import (
    ResearchSectionTitleMapper,
)


class EnterpriseResearchReportFormatter:
    def __init__(
        self,
        *,
        citation_formatter: ResearchCitationFormatter | None = None,
        section_title_mapper: ResearchSectionTitleMapper | None = None,
    ) -> None:
        self.citation_formatter = citation_formatter or ResearchCitationFormatter()
        self.section_title_mapper = section_title_mapper or ResearchSectionTitleMapper()

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
            section_title = self._section_title(section)
            lines.extend(
                [
                    "",
                    section_title,
                    "-" * len(section_title),
                    "",
                ]
            )
            findings = self._section_findings(section)
            if findings:
                lines.extend(self._render_findings(section_title=section_title, findings=findings))
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
                    section_path = entry.get("section_path")
                    if section_path:
                        lines.append(f"    Path: {section_path}")
        return "\n".join(lines).strip()

    def _render_findings(
        self,
        *,
        section_title: str,
        findings: list[dict[str, Any]],
    ) -> list[str]:
        lines: list[str] = []
        is_comparison = section_title.casefold() == "comparison"
        for index, finding in enumerate(findings, start=1):
            prefix = "-" if is_comparison else f"{index}."
            lines.append(f"{prefix} {finding['text']}")
            for detail in self._details(finding):
                lines.append(f"   - {detail}")
            reference_detail = self.citation_formatter.format_reference_detail(finding)
            path_detail = self.citation_formatter.format_path_detail(finding)
            if reference_detail:
                lines.append(f"   Reference: {reference_detail}")
            if path_detail:
                lines.append(f"   Path: {path_detail}")
            lines.append("")
        if lines and not lines[-1]:
            lines.pop()
        return lines

    def _section_title(self, section: dict[str, Any]) -> str:
        return self.section_title_mapper.display_title(str(section.get("title") or "Section"))

    @staticmethod
    def _section_findings(section: dict[str, Any]) -> list[dict[str, Any]]:
        findings = section.get("findings")
        if isinstance(findings, list):
            return [item for item in findings if isinstance(item, dict) and item.get("text")]
        return []

    @staticmethod
    def _details(finding: dict[str, Any]) -> list[str]:
        details = finding.get("details")
        if not isinstance(details, list):
            return []
        return [str(item).strip() for item in details if isinstance(item, str) and item.strip()]

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
        references: list[dict[str, Any]] = []
        for section in report.sections:
            for finding in self._section_findings(section):
                if finding.get("document_title") or finding.get("document_name"):
                    references.append(finding)
        if references:
            return references
        if report.references:
            return [item for item in report.references if isinstance(item, dict)]
        return []
