from src.application.workflows.retrieval.table_focus import is_table_focused_query
from src.application.workflows.shared.text_signature_utils import detect_scaffolding_role
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery, RetrievedChunk

_LOW_VALUE_CHUNK_TYPES = {ChunkType.OVERVIEW, ChunkType.GENERAL}
_LOW_VALUE_ROLES = {"overview_companion", "context_companion"}
_TABLE_LIKE_CHUNK_TYPES = {
    ChunkType.SPARE_PARTS_TABLE,
    ChunkType.TECHNICAL_SPECIFICATION,
    ChunkType.CERTIFICATION_INFO,
    ChunkType.MAINTENANCE_INTERVAL,
    ChunkType.MAINTENANCE_PROCEDURE,
    ChunkType.TROUBLESHOOTING,
}


class TableFocusedEvidencePruner:
    def prune(
        self,
        *,
        query: RetrievalQuery | None,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        if query is None or len(chunks) < 2:
            return list(chunks)
        if not is_table_focused_query(query=query):
            return list(chunks)

        direct_table_chunks = [
            chunk for chunk in chunks if self._is_direct_table_evidence(chunk)
        ]
        if not direct_table_chunks:
            return list(chunks)

        pruned = [
            chunk for chunk in chunks if not self._is_low_value_companion(chunk)
        ]
        return pruned or list(direct_table_chunks)

    @staticmethod
    def _is_direct_table_evidence(chunk: RetrievedChunk) -> bool:
        metadata = chunk.metadata
        if metadata.get("table_evidence_hydrated") == "true":
            return True
        if metadata.get("logical_table_family_id"):
            return True
        if metadata.get("hydrated_table_ids") or metadata.get("table_rows_json"):
            return True
        return chunk.chunk_type in _TABLE_LIKE_CHUNK_TYPES and "|" in chunk.content

    @staticmethod
    def _is_low_value_companion(chunk: RetrievedChunk) -> bool:
        if TableFocusedEvidencePruner._is_direct_table_evidence(chunk):
            return False
        if detect_scaffolding_role(chunk.content) in _LOW_VALUE_ROLES:
            return True
        return chunk.chunk_type in _LOW_VALUE_CHUNK_TYPES
