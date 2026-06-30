from __future__ import annotations

from src.application.langgraph.research.models import ResearchSynthesis
from src.application.langgraph.research.presentation import ResearchFindingBuilder


class EvidenceSynthesizer:
    def __init__(
        self,
        *,
        finding_builder: ResearchFindingBuilder | None = None,
    ) -> None:
        self.finding_builder = finding_builder or ResearchFindingBuilder()

    def synthesize(self, result) -> ResearchSynthesis:
        sections = []
        references = []
        for task in result.plan.tasks:
            task_evidence = _task_evidence(result, task.task_id)
            if not task_evidence:
                continue
            findings = self.finding_builder.build_findings(task_evidence)
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
            references.extend(
                {
                    "chunk_id": item.chunk_id,
                    "document_id": item.document_id,
                    "document_title": item.document_title,
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


def _task_evidence(result, task_id: str):
    for task_result in result.task_results:
        if task_result.task_id == task_id and task_result.evidence:
            return list(task_result.evidence)
    return [
        evidence
        for evidence in result.evidence
        if evidence.task_id == task_id
    ]
