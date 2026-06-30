from __future__ import annotations

from src.application.langgraph.research.models import (
    ResearchGoalType,
    ResearchReport,
    ResearchSynthesis,
)
from src.application.langgraph.research.policies import ResearchSynthesisPolicy
from src.application.langgraph.research.synthesizers.checklist_synthesizer import (
    ChecklistSynthesizer,
)
from src.application.langgraph.research.synthesizers.comparison_synthesizer import (
    ComparisonSynthesizer,
)
from src.application.langgraph.research.synthesizers.evidence_synthesizer import (
    EvidenceSynthesizer,
)
from src.application.langgraph.research.synthesizers.maintenance_report_synthesizer import (
    MaintenanceReportSynthesizer,
)


class ResearchReportBuilder:
    def __init__(
        self,
        *,
        comparison_synthesizer: ComparisonSynthesizer | None = None,
        maintenance_report_synthesizer: MaintenanceReportSynthesizer | None = None,
        checklist_synthesizer: ChecklistSynthesizer | None = None,
        evidence_synthesizer: EvidenceSynthesizer | None = None,
    ) -> None:
        self.comparison_synthesizer = comparison_synthesizer or ComparisonSynthesizer()
        self.maintenance_report_synthesizer = (
            maintenance_report_synthesizer or MaintenanceReportSynthesizer()
        )
        self.checklist_synthesizer = checklist_synthesizer or ChecklistSynthesizer()
        self.evidence_synthesizer = evidence_synthesizer or EvidenceSynthesizer()

    def build_synthesis(self, result) -> ResearchSynthesis:
        goal_type = result.goal.goal_type
        if goal_type == ResearchGoalType.COMPARISON:
            return self.comparison_synthesizer.synthesize(result)
        if goal_type == ResearchGoalType.CHECKLIST:
            return self.checklist_synthesizer.synthesize(result)
        if goal_type == ResearchGoalType.REPORT and "maintenance" in result.goal.user_input.lower():
            return self.maintenance_report_synthesizer.synthesize(result)
        return self.evidence_synthesizer.synthesize(result)

    def build_report(
        self,
        *,
        result,
        synthesis: ResearchSynthesis,
        context: dict,
        policy: ResearchSynthesisPolicy,
    ) -> ResearchReport:
        title = _report_title(result.goal.goal_type)
        findings = [
            section["title"]
            for section in synthesis.sections
            if isinstance(section, dict) and section.get("title")
        ]
        return ResearchReport(
            title=title,
            executive_summary=synthesis.summary,
            sections=list(synthesis.sections),
            findings=findings,
            gaps=[gap.to_dict() for gap in synthesis.gaps] if policy.include_gaps else [],
            references=list(synthesis.references) if policy.include_references else [],
            appendix={
                "comparisons": list(synthesis.comparisons),
                "checklist_items": list(synthesis.checklist_items),
                "context": context,
            },
            diagnostics=dict(synthesis.diagnostics),
        )

    def to_markdown(self, report: ResearchReport, *, policy: ResearchSynthesisPolicy) -> str:
        lines = [f"# {report.title}", "", "## Executive Summary", report.executive_summary]
        for section in report.sections:
            title = str(section.get("title") or "Section")
            body = str(section.get("body") or "").strip()
            lines.extend(["", f"## {title}", body or "No evidence summary available."])
        checklist_items = report.appendix.get("checklist_items", [])
        if checklist_items:
            lines.extend(["", "## Checklist"])
            for item in checklist_items:
                label = item.get("label") or "Item"
                evidence = item.get("evidence") or "-"
                lines.append(f"{policy.checklist_prefix} {label}")
                lines.append(f"Evidence: {evidence}")
        if report.gaps:
            lines.extend(["", "## Missing Evidence"])
            for gap in report.gaps:
                lines.append(f"- {gap.get('description')}")
        if report.references:
            lines.extend(["", "## References"])
            for ref in report.references:
                section_path = " > ".join(ref.get("section_path") or [])
                lines.append(
                    f"- {ref.get('document_id')} | {section_path or '-'} | "
                    f"p. {ref.get('page_start') or '-'}-{ref.get('page_end') or ref.get('page_start') or '-'}"
                )
        return "\n".join(lines).strip()


def _report_title(goal_type) -> str:
    return {
        ResearchGoalType.COMPARISON: "Comparison Summary",
        ResearchGoalType.CHECKLIST: "Checklist",
        ResearchGoalType.AUDIT: "Research Audit",
        ResearchGoalType.EVIDENCE_REVIEW: "Evidence Review",
        ResearchGoalType.GAP_ANALYSIS: "Evidence Review",
        ResearchGoalType.REPORT: "Research Report",
        ResearchGoalType.SUMMARY: "Research Summary",
        ResearchGoalType.GENERAL_RESEARCH: "Research Report",
    }[goal_type]
