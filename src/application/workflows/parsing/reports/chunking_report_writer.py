from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.application.workflows.parsing.parsing_workflow_result import (
        ParsingWorkflowResult,
    )

_DEFAULT_OUTPUT_DIR = Path("outputs/debug_parsing")


class ChunkingReportWriter:
    """Writes a chunk type distribution report to outputs/debug_parsing/."""

    def __init__(self, output_dir: Path | str | None = None) -> None:
        self.output_dir = Path(output_dir) if output_dir else _DEFAULT_OUTPUT_DIR

    def write(self, result: ParsingWorkflowResult) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{result.document_id}_chunk_report.json"

        chunks = list(result.document_graph.chunks.values())
        type_counts = Counter(
            str(c.chunk_type).split(".")[-1].lower() for c in chunks
        )
        section_path_coverage = sum(
            1 for c in chunks if c.section_path
        )
        avg_content_len = (
            sum(len(c.content or "") for c in chunks) / len(chunks)
            if chunks
            else 0
        )

        payload = {
            "document_id": result.document_id,
            "total_chunks": len(chunks),
            "type_distribution": dict(type_counts.most_common()),
            "chunks_with_section_path": section_path_coverage,
            "chunks_without_section_path": len(chunks) - section_path_coverage,
            "avg_content_length_chars": round(avg_content_len, 1),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path
