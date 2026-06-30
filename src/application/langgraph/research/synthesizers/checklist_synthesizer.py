from __future__ import annotations

from src.application.langgraph.research.models import ResearchSynthesis


class ChecklistSynthesizer:
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
            sections.append(
                {
                    "title": task.title,
                    "body": "\n".join(
                        f"- {item.content_excerpt} (p. {item.page_start or '-'})"
                        for item in task_evidence[:4]
                    ),
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
