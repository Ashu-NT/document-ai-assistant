from collections import Counter
from typing import Callable

from src.application.workflows.classification.finalization.asset_fallback_chunk_recovery import (
    AssetFallbackChunkRecovery,
)
from src.application.workflows.parsing.builders.document_graph.graph_chunk_builder import (
    GraphChunkBuilder,
)
from src.domain.document import DocumentChunk, DocumentGraph, DocumentSection
from src.shared.exceptions import ApplicationError
from src.shared.progress.progress_emitter import emit_progress


class FinalChunkResolver:
    """Decides the final chunk set for a document during post-classification
    finalization: reuse the stored chunks, rebuild them, rechunk outright, or
    fall back to asset-aware recovery -- raising a clear diagnostic error if
    every strategy yields zero chunks for a non-empty parsed document."""

    def __init__(
        self,
        *,
        graph_chunk_builder: GraphChunkBuilder,
        asset_fallback_recovery: AssetFallbackChunkRecovery,
    ) -> None:
        self.graph_chunk_builder = graph_chunk_builder
        self.asset_fallback_recovery = asset_fallback_recovery

    def resolve(
        self,
        *,
        graph: DocumentGraph,
        sections: list[DocumentSection],
        decision,
        effective_include_picture_chunks: bool,
        progress_callback: Callable[[str], None] | None = None,
    ) -> tuple[list[DocumentChunk], str]:
        stored_chunks = sorted(
            graph.chunks.values(),
            key=lambda chunk: chunk.sequence_number,
        )
        rebuilt_chunks = self.graph_chunk_builder.build_chunks(
            graph=graph,
            sections=sections,
            document_type_override=decision.effective_document_type,
            chunking_profile_override=decision.effective_chunking_profile,
        )
        if decision.should_rechunk:
            selected_chunks, selected_mode = rebuilt_chunks, "rechunked"
        elif not stored_chunks:
            selected_chunks, selected_mode = rebuilt_chunks, "rebuilt_missing"
        elif self._chunk_structures_match(stored_chunks, rebuilt_chunks):
            selected_chunks, selected_mode = stored_chunks, "reused"
        else:
            selected_chunks, selected_mode = rebuilt_chunks, "refreshed_stale"

        if selected_chunks:
            return selected_chunks, selected_mode

        fallback_chunks = self.asset_fallback_recovery.attempt(
            graph=graph,
            sections=sections,
            decision=decision,
            progress_callback=progress_callback,
        )
        if fallback_chunks:
            return fallback_chunks, "asset_fallback"

        if stored_chunks:
            emit_progress(
                progress_callback,
                (
                    f"Rebuilding produced zero chunks under the "
                    f"{decision.effective_chunking_profile.value} profile; falling back to "
                    f"{len(stored_chunks)} previously stored chunk(s) instead of failing."
                ),
            )
            return stored_chunks, "reused_after_empty_rebuild"

        raise ApplicationError(
            "Post-classification chunk finalization produced zero chunks for a non-empty parsed document.",
            details=self._build_zero_chunk_diagnostics(
                graph=graph,
                decision=decision,
                effective_include_picture_chunks=effective_include_picture_chunks,
                fallback_attempted=True,
            ),
        )

    @staticmethod
    def _build_zero_chunk_diagnostics(
        *,
        graph: DocumentGraph,
        decision,
        effective_include_picture_chunks: bool,
        fallback_attempted: bool,
    ) -> dict[str, object]:
        element_type_counts = Counter(
            element.element_type.value
            for element in graph.elements.values()
        )
        return {
            "document_id": graph.document.document_id,
            "document_type": decision.effective_document_type.value,
            "chunking_profile": decision.effective_chunking_profile.value,
            "element_count": len(graph.elements),
            "element_type_counts": dict(element_type_counts),
            "table_count": len(graph.tables),
            "picture_count": len(graph.pictures),
            "stored_chunk_count": len(graph.chunks),
            "include_picture_chunks": effective_include_picture_chunks,
            "asset_fallback_attempted": fallback_attempted,
        }

    @classmethod
    def _chunk_structures_match(
        cls,
        stored_chunks: list[DocumentChunk],
        rebuilt_chunks: list[DocumentChunk],
    ) -> bool:
        if len(stored_chunks) != len(rebuilt_chunks):
            return False

        return [
            cls._chunk_structure_signature(chunk)
            for chunk in stored_chunks
        ] == [
            cls._chunk_structure_signature(chunk)
            for chunk in rebuilt_chunks
        ]

    @staticmethod
    def _chunk_structure_signature(
        chunk: DocumentChunk,
    ) -> tuple[object, ...]:
        return (
            chunk.content,
            chunk.chunk_type.value,
            tuple(chunk.section_path),
            tuple(chunk.element_ids),
            tuple(chunk.table_ids),
            tuple(chunk.picture_ids),
            chunk.source.page_start,
            chunk.source.page_end,
            chunk.chunk_index,
            chunk.chunk_total,
            chunk.embedding_text,
        )

    @staticmethod
    def progress_message(mode: str) -> str:
        if mode == "rechunked":
            return "Building final chunk set..."
        if mode == "rebuilt_missing":
            return "Rebuilding final chunk set because no stored final chunks were available..."
        if mode == "refreshed_stale":
            return "Refreshing stored final chunk set using the current chunk builder..."
        if mode == "asset_fallback":
            return "Using asset-aware fallback chunk set..."
        if mode == "reused_after_empty_rebuild":
            return "Keeping previously stored final chunk set after rebuild produced none..."
        return "Reusing stored final chunk set..."
