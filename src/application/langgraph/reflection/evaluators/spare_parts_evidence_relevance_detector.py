from __future__ import annotations

from typing import Any


class SparePartsEvidenceRelevanceDetector:
    @staticmethod
    def has_relevant_evidence(
        *,
        approved_chunks: list[dict[str, Any]],
        selected_document_id: str | None,
    ) -> bool:
        for chunk in approved_chunks:
            if not isinstance(chunk, dict):
                continue
            if (
                selected_document_id
                and chunk.get("document_id")
                and str(chunk.get("document_id")) != selected_document_id
            ):
                continue
            chunk_type = str(chunk.get("chunk_type") or "").strip().lower()
            if chunk_type == "spare_parts_table":
                return True
            content = str(chunk.get("content") or "").lower()
            if "spare part" in content and (
                "spare parts list" in content
                or "spare part no" in content
                or "spare parts no" in content
            ):
                return True
        return False
