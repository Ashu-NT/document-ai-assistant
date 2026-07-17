from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.workflows.retrieval.table_focus import is_table_focused_query
from src.application.workflows.shared.text_signature_utils import detect_scaffolding_role
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery, RetrievedChunk

_LOW_VALUE_ROLES = {"overview_companion", "context_companion"}
_TABLE_LIKE_CHUNK_TYPES = {
    ChunkType.SPARE_PARTS_TABLE,
    ChunkType.TECHNICAL_SPECIFICATION,
    ChunkType.CERTIFICATION_INFO,
    ChunkType.MAINTENANCE_INTERVAL,
    ChunkType.MAINTENANCE_PROCEDURE,
    ChunkType.TROUBLESHOOTING,
}
# Only the intents with an unambiguous single expected table family --
# TABLE/IDENTIFIER are deliberately excluded since "show me the table" or an
# identifier lookup can legitimately want any table type, not one family.
_FAMILY_EXPECTED_CHUNK_TYPES: dict[RetrievalQueryIntent, frozenset[ChunkType]] = {
    RetrievalQueryIntent.MAINTENANCE: frozenset({ChunkType.MAINTENANCE_INTERVAL}),
    RetrievalQueryIntent.SPECIFICATION: frozenset(
        {ChunkType.TECHNICAL_SPECIFICATION, ChunkType.CERTIFICATION_INFO}
    ),
    RetrievalQueryIntent.TROUBLESHOOTING: frozenset({ChunkType.TROUBLESHOOTING}),
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

        expected_types = self._expected_table_types(query)
        matching_direct_chunks = [
            chunk
            for chunk in direct_table_chunks
            if not expected_types or chunk.chunk_type in expected_types
        ]
        # Only reject a mismatched table family once at least one matching
        # chunk survives -- never discard the only table evidence available
        # just because it isn't the exact expected family.
        mismatched_chunk_ids = (
            {
                chunk.chunk_id
                for chunk in direct_table_chunks
                if chunk.chunk_type not in expected_types
            }
            if expected_types and matching_direct_chunks
            else set()
        )

        pruned = [
            chunk
            for chunk in chunks
            if not self._is_low_value_companion(chunk)
            and chunk.chunk_id not in mismatched_chunk_ids
        ]
        return pruned or matching_direct_chunks or direct_table_chunks

    @staticmethod
    def _expected_table_types(query: RetrievalQuery) -> frozenset[ChunkType]:
        raw_intent = query.detected_intent
        if not raw_intent:
            return frozenset()
        try:
            intent = RetrievalQueryIntent(raw_intent)
        except ValueError:
            return frozenset()
        return _FAMILY_EXPECTED_CHUNK_TYPES.get(intent, frozenset())

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
        # Only auto-generated scaffolding companions (the literal "Context: "/
        # "Section overview: " prefixes injected by picture_fragment_builder.py
        # and section_overview_chunk_builder.py) get pruned here -- chunk_type
        # OVERVIEW/GENERAL is not itself a low-value signal, since GENERAL is
        # the deterministic classifier's catch-all for any real content that
        # didn't hit a specific category's keyword threshold (a caveat, a
        # safety note, install context), and OVERVIEW can also be assigned to
        # genuine organic prose by the optional LLM chunk-type classifier.
        if TableFocusedEvidencePruner._is_direct_table_evidence(chunk):
            return False
        return detect_scaffolding_role(chunk.content) in _LOW_VALUE_ROLES
