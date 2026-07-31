from __future__ import annotations


class IngestionStagePayloadBuilder:
    def parsing_completed(self, parsing_result) -> dict[str, object]:
        return {
            "page_count": parsing_result.page_count,
            "section_count": parsing_result.section_count,
            "chunk_count": parsing_result.chunk_count,
        }

    @staticmethod
    def registration_completed(document_id: str) -> dict[str, object]:
        return {"document_id": document_id}

    @staticmethod
    def classification_completed(
        classification,
        *,
        classification_enabled: bool,
    ) -> dict[str, object]:
        return {
            "skipped": not classification_enabled,
            "reason": "disabled_by_config" if not classification_enabled else None,
            "document_type": (
                classification.document_type.value
                if classification is not None
                else None
            ),
            "confidence_score": (
                classification.result.confidence_score
                if classification is not None and classification.result is not None
                else None
            ),
        }

    @staticmethod
    def finalization_completed(
        *,
        final_graph,
        runtime_diagnostics: dict[str, object],
    ) -> dict[str, object]:
        return {
            **runtime_diagnostics,
            "chunk_count": len(final_graph.chunks),
            "question_count": len(final_graph.questions),
        }

    @staticmethod
    def extraction_completed(
        *,
        extraction_result,
        extraction_stage_result,
        extraction_enabled: bool,
        runtime_diagnostics: dict[str, object],
    ) -> dict[str, object]:
        return {
            **runtime_diagnostics,
            "skipped": not extraction_enabled,
            "reason": "disabled_by_config" if not extraction_enabled else None,
            "extraction_id": (
                extraction_result.extraction_id
                if extraction_result is not None
                else None
            ),
            "maintenance_task_count": (
                len(extraction_result.maintenance_tasks)
                if extraction_result is not None
                else 0
            ),
            "spare_part_count": (
                len(extraction_result.spare_parts)
                if extraction_result is not None
                else 0
            ),
            "unresolved_chunk_count": (
                len(extraction_result.unresolved_chunk_ids)
                if extraction_result is not None
                else 0
            ),
            "deterministic_identifier_count": (
                extraction_stage_result.deterministic_identifier_count
            ),
            "semantic_relationship_count": (
                extraction_stage_result.semantic_relationship_count
            ),
        }

    @staticmethod
    def vector_completed(vector_count: int) -> dict[str, object]:
        return {"vector_count": vector_count}
