from __future__ import annotations

from src.application.langgraph.research.models import (
    ResearchGoalType,
    ResearchReport,
    ResearchSynthesis,
)
from src.application.langgraph.research.policies import ResearchSynthesisPolicy
from src.application.langgraph.research.presentation import (
    EnterpriseResearchReportFormatter,
    ResearchExecutiveSummaryBuilder,
)
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
        executive_summary_builder: ResearchExecutiveSummaryBuilder | None = None,
        formatter: EnterpriseResearchReportFormatter | None = None,
    ) -> None:
        self.comparison_synthesizer = comparison_synthesizer or ComparisonSynthesizer()
        self.maintenance_report_synthesizer = (
            maintenance_report_synthesizer or MaintenanceReportSynthesizer()
        )
        self.checklist_synthesizer = checklist_synthesizer or ChecklistSynthesizer()
        self.evidence_synthesizer = evidence_synthesizer or EvidenceSynthesizer()
        self.executive_summary_builder = (
            executive_summary_builder or ResearchExecutiveSummaryBuilder()
        )
        self.formatter = formatter or EnterpriseResearchReportFormatter()

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
            executive_summary=self.executive_summary_builder.build(
                result=result,
                sections=list(synthesis.sections),
            ),
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

    def render_text(self, report: ResearchReport, *, policy: ResearchSynthesisPolicy) -> str:
        return self.formatter.render(report, policy=policy)

    def to_markdown(self, report: ResearchReport, *, policy: ResearchSynthesisPolicy) -> str:
        return self.render_text(report, policy=policy)


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
