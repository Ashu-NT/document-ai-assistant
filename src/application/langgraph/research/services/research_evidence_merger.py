from __future__ import annotations

from src.application.langgraph.research.models import ResearchEvidence


class ResearchEvidenceMerger:
    def merge(
        self,
        evidence: list[ResearchEvidence],
        *,
        max_total_evidence: int,
    ) -> list[ResearchEvidence]:
        winners: dict[str, ResearchEvidence] = {}
        for item in evidence:
            winner = winners.get(item.chunk_id)
            if winner is None or (item.score or 0.0) > (winner.score or 0.0):
                winners[item.chunk_id] = item
                continue
            if winner.task_id != item.task_id:
                winner.diagnostics.setdefault("related_task_ids", [])
                related = winner.diagnostics["related_task_ids"]
                if isinstance(related, list) and item.task_id not in related:
                    related.append(item.task_id)
        merged = sorted(
            winners.values(),
            key=lambda item: (item.score or 0.0),
            reverse=True,
        )
        return merged[:max_total_evidence]
