from __future__ import annotations

from src.application.langgraph.research.models import ResearchSynthesis
from src.application.langgraph.research.presentation import ResearchFindingBuilder


class ChecklistSynthesizer:
    def __init__(
        self,
        *,
        finding_builder: ResearchFindingBuilder | None = None,
    ) -> None:
        self.finding_builder = finding_builder or ResearchFindingBuilder()

    def synthesize(self, result) -> ResearchSynthesis:
        checklist_items = []
        references = []
        sections = []
        for evidence in result.evidence[:12]:
            label = evidence.content_excerpt.split(".")[0].strip() or evidence.content_excerpt
            checklist_items.append(
                {
                    "label": label,
                    "evidence": f"Page {evidence.page_start or '-'}, {' > '.join(evidence.section_path) or '-'}",
                }
            )
            references.append(
                {
                    "chunk_id": evidence.chunk_id,
                    "document_title": evidence.document_title,
                    "page_start": evidence.page_start,
                    "page_end": evidence.page_end,
                    "section_path": evidence.section_path,
                }
            )
        for task in result.plan.tasks:
            task_evidence = [
                evidence
                for evidence in result.evidence
                if evidence.task_id == task.task_id
            ]
            if not task_evidence:
                continue
            findings = self.finding_builder.build_findings(task_evidence, max_findings=4)
            sections.append(
                {
                    "title": task.title,
                    "body": "\n".join(
                        f"- {finding['text']}"
                        for finding in findings
                    ),
                    "findings": findings,
                    "evidence_count": len(task_evidence),
                }
            )
        return ResearchSynthesis(
            summary=(
                f"Collected {len(checklist_items)} checklist item(s) from "
                f"{len(sections)} evidence section(s)."
            ),
            sections=sections,
            checklist_items=checklist_items,
            gaps=list(result.gaps),
            references=references,
            diagnostics={
                "checklist_item_count": len(checklist_items),
                "section_count": len(sections),
            },
        )
