from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.application.workflows.parsing.parsing_workflow_result import (
        ParsingWorkflowResult,
    )


class ChunkDistributionStatsCalculator:
    """Computes chunk-type distribution stats from a parsing result."""

    def calculate(self, result: ParsingWorkflowResult) -> dict[str, object]:
        chunks = list(result.document_graph.chunks.values())
        type_counts = Counter(
            str(c.chunk_type).split(".")[-1].lower() for c in chunks
        )
        section_path_coverage = sum(1 for c in chunks if c.section_path)
        avg_content_len = (
            sum(len(c.content or "") for c in chunks) / len(chunks) if chunks else 0
        )

        return {
            "document_id": result.document_id,
            "total_chunks": len(chunks),
            "type_distribution": dict(type_counts.most_common()),
            "chunks_with_section_path": section_path_coverage,
            "chunks_without_section_path": len(chunks) - section_path_coverage,
            "avg_content_length_chars": round(avg_content_len, 1),
        }
