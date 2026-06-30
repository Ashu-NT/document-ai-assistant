from __future__ import annotations

from src.application.langgraph.research.models import ResearchEvidence


class ResearchEvidenceMerger:
    def merge(
        self,
        evidence: list[ResearchEvidence],
        *,
        max_total_evidence: int,
    ) -> list[ResearchEvidence]:
        winners: dict[tuple[str, str], ResearchEvidence] = {}
        for item in evidence:
            key = (item.chunk_id, item.task_id)
            winner = winners.get(key)
            if winner is None or (item.score or 0.0) > (winner.score or 0.0):
                winners[key] = item
        merged = sorted(
            winners.values(),
            key=lambda item: (item.score or 0.0),
            reverse=True,
        )
        return merged[:max_total_evidence]
