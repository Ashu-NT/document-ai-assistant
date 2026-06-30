from __future__ import annotations

from src.application.langgraph.research.models import ResearchEvidence, ResearchGap


class ResearchContextBuilder:
    def build(
        self,
        *,
        evidence: list[ResearchEvidence],
        gaps: list[ResearchGap],
    ) -> dict:
        by_task: dict[str, list[dict]] = {}
        by_section: dict[str, list[dict]] = {}
        by_page: dict[str, list[dict]] = {}
        references: list[dict] = []

        for item in evidence:
            payload = item.to_dict()
            by_task.setdefault(item.task_id, []).append(payload)
            section_key = " > ".join(item.section_path) or "-"
            by_section.setdefault(section_key, []).append(payload)
            page_key = f"{item.page_start or '-'}-{item.page_end or item.page_start or '-'}"
            by_page.setdefault(page_key, []).append(payload)
            references.append(
                {
                    "chunk_id": item.chunk_id,
                    "document_id": item.document_id,
                    "document_title": item.document_title,
                    "section_path": item.section_path,
                    "page_start": item.page_start,
                    "page_end": item.page_end,
                }
            )

        return {
            "tasks": by_task,
            "sections": by_section,
            "pages": by_page,
            "gaps": [gap.to_dict() for gap in gaps],
            "references": references,
        }
