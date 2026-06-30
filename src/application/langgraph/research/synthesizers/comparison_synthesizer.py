from __future__ import annotations

from src.application.langgraph.research.models import ResearchSynthesis
from src.application.langgraph.research.synthesizers.evidence_synthesizer import (
    EvidenceSynthesizer,
)


class ComparisonSynthesizer:
    def __init__(self, *, evidence_synthesizer: EvidenceSynthesizer | None = None) -> None:
        self.evidence_synthesizer = evidence_synthesizer or EvidenceSynthesizer()

    def synthesize(self, result) -> ResearchSynthesis:
        base = self.evidence_synthesizer.synthesize(result)
        comparisons = []
        titles = [section["title"] for section in base.sections]
        if len(titles) >= 2:
            comparisons.append(
                {
                    "left": titles[0],
                    "right": titles[1],
                    "relationship": "Both topics were researched from the same selected document.",
                }
            )
        comparison_findings = _comparison_findings(base.sections)
        if comparison_findings:
            base.sections.append(
                {
                    "title": "Comparison",
                    "body": "\n".join(
                        f"- {finding['text']}"
                        for finding in comparison_findings
                    ),
                    "findings": comparison_findings,
                    "evidence_count": 0,
                }
            )
        base.summary = "Comparison Summary"
        base.comparisons = comparisons
        return base


def _comparison_findings(sections: list[dict]) -> list[dict[str, str]]:
    titles = [str(section.get("title") or "").casefold() for section in sections]
    has_maintenance = any("maintenance" in title for title in titles)
    has_specifications = any(
        "specification" in title or "technical" in title
        for title in titles
    )
    findings: list[dict[str, str]] = []
    if has_maintenance:
        findings.append(
            {
                "text": "Maintenance findings describe required actions, inspections, isolation steps, and scheduled servicing."
            }
        )
    if has_specifications:
        findings.append(
            {
                "text": "Technical specification findings describe equipment identity, operating limits, and structured component data."
            }
        )
    if has_maintenance and has_specifications:
        findings.extend(
            [
                {
                    "text": "Specification evidence identifies the equipment, power, capacity, and material context that the maintenance instructions apply to."
                },
                {
                    "text": "Technical sections can also bridge both topics when they include service intervals, oil quantities, or other maintenance-adjacent operating data."
                },
            ]
        )
    if not findings and len(sections) >= 2:
        findings.append(
            {
                "text": "The researched sections address different aspects of the same document and should be read together when making operational decisions."
            }
        )
    return findings
