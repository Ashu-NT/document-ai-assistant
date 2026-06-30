from __future__ import annotations

from typing import Any

from src.application.langgraph.research.models import ResearchGoalType
from src.application.langgraph.research.presentation.research_section_title_mapper import (
    ResearchSectionTitleMapper,
)


class ResearchExecutiveSummaryBuilder:
    def __init__(
        self,
        *,
        section_title_mapper: ResearchSectionTitleMapper | None = None,
    ) -> None:
        self.section_title_mapper = section_title_mapper or ResearchSectionTitleMapper()

    def build(
        self,
        *,
        result,
        sections: list[dict[str, Any]],
    ) -> str:
        goal_type = result.goal.goal_type
        if goal_type == ResearchGoalType.COMPARISON:
            return self._build_comparison_summary(sections)
        if goal_type == ResearchGoalType.CHECKLIST:
            return self._build_checklist_summary(sections)
        if goal_type == ResearchGoalType.REPORT:
            return self._build_report_summary(sections, result.goal.document_title)
        return self._build_general_summary(sections, result.goal.document_title)

    def _build_comparison_summary(self, sections: list[dict[str, Any]]) -> str:
        topics = [self._topic_label(section.get("title")) for section in sections[:2]]
        if len(topics) >= 2:
            return "\n\n".join([
                f"The selected document separates {topics[0]} from {topics[1]}.",
                f"{topics[0].capitalize()} findings focus on {self._topic_description(topics[0])}.",
                f"{topics[1].capitalize()} findings focus on {self._topic_description(topics[1])}.",
            ])
        if topics:
            topic = topics[0]
            return "\n\n".join(
                [
                    f"The selected document was reviewed for {topic}.",
                    f"The grounded findings focus on {self._topic_description(topic)}.",
                ]
            )
        return "The selected document was reviewed and grounded findings were compiled."

    def _build_checklist_summary(self, sections: list[dict[str, Any]]) -> str:
        if sections:
            topic = self._topic_label(sections[0].get("title"))
            return "\n\n".join(
                [
                    f"The selected document was reviewed to build a practical checklist for {topic}.",
                    "The output emphasizes concrete steps, prerequisites, and safety-critical actions.",
                ]
            )
        return "The selected document was reviewed to build a practical, grounded checklist."

    def _build_report_summary(
        self,
        sections: list[dict[str, Any]],
        document_title: str | None,
    ) -> str:
        document_name = document_title or "the selected document"
        section_count = len(sections)
        if section_count > 0:
            return "\n\n".join(
                [
                    f"{document_name} was reviewed to compile a grounded research report.",
                    f"The report consolidates evidence across {section_count} focused section(s).",
                ]
            )
        return f"{document_name} was reviewed to compile a grounded research report."

    def _build_general_summary(
        self,
        sections: list[dict[str, Any]],
        document_title: str | None,
    ) -> str:
        document_name = document_title or "the selected document"
        if sections:
            topics = ", ".join(self._topic_label(section.get("title")) for section in sections[:3])
            return "\n\n".join(
                [
                    f"{document_name} was reviewed to answer the requested research question.",
                    f"The grounded findings focus on {topics}.",
                ]
            )
        return f"{document_name} was reviewed and grounded findings were compiled."

    @staticmethod
    def _normalize_topic_text(value: Any) -> str:
        text = str(value or "the requested topic").strip()
        if text.lower().startswith("collect "):
            text = text[8:]
        return text.lower()

    def _topic_label(self, value: Any) -> str:
        text = self.section_title_mapper.display_title(str(value or "the requested topic"))
        return self._normalize_topic_text(text)

    @staticmethod
    def _topic_description(topic: str) -> str:
        normalized = topic.lower()
        if "maintenance" in normalized:
            return "preventive activities, inspections, servicing steps, and scheduled care"
        if "specification" in normalized or "technical" in normalized:
            return "equipment characteristics, operating data, limits, and structured technical information"
        if "procedure" in normalized or "commissioning" in normalized:
            return "step-by-step operating guidance, prerequisites, and execution steps"
        if "safety" in normalized:
            return "isolation steps, warnings, and operational safeguards"
        if "troubleshooting" in normalized:
            return "fault symptoms, corrective actions, and inspection guidance"
        if "spare parts" in normalized:
            return "replaceable components, identifiers, and support material"
        return "the most relevant grounded evidence from the selected document"
