from __future__ import annotations

from src.application.langgraph.research.models import ResearchSynthesis


class EvidenceSynthesizer:
    def synthesize(self, result) -> ResearchSynthesis:
        sections = []
        references = []
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
                        for item in task_evidence[:5]
                    ),
                    "evidence_count": len(task_evidence),
                }
            )
            references.extend(
                {
                    "chunk_id": item.chunk_id,
                    "document_id": item.document_id,
                    "section_path": item.section_path,
                    "page_start": item.page_start,
                    "page_end": item.page_end,
                }
                for item in task_evidence
            )
        summary = (
            f"Collected {len(result.evidence)} evidence item(s) across "
            f"{len(result.task_results)} research task(s)."
        )
        return ResearchSynthesis(
            summary=summary,
            sections=sections,
            gaps=list(result.gaps),
            references=references,
            diagnostics={"section_count": len(sections)},
        )
