from __future__ import annotations

from src.application.langgraph.research.models import ResearchSynthesis


class ChecklistSynthesizer:
    def synthesize(self, result) -> ResearchSynthesis:
        checklist_items = []
        references = []
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
        return ResearchSynthesis(
            summary="Checklist",
            checklist_items=checklist_items,
            gaps=list(result.gaps),
            references=references,
            diagnostics={"checklist_item_count": len(checklist_items)},
        )
