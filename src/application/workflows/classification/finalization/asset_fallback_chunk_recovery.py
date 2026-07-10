from typing import Callable

from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.document_graph.graph_chunk_builder import (
    GraphChunkBuilder,
)
from src.domain.document import DocumentChunk, DocumentGraph, DocumentSection
from src.shared.progress import emit_progress


class AssetFallbackChunkRecovery:
    """Recovers a non-empty final chunk set for asset-heavy documents (tables
    and pictures with meaningful content) when the normal reuse/rebuild path
    in `FinalChunkResolver` produces zero chunks, by retrying the chunk build
    under the default chunking profile."""

    def __init__(self, *, graph_chunk_builder: GraphChunkBuilder) -> None:
        self.graph_chunk_builder = graph_chunk_builder

    def attempt(
        self,
        *,
        graph: DocumentGraph,
        sections: list[DocumentSection],
        decision,
        progress_callback: Callable[[str], None] | None = None,
    ) -> list[DocumentChunk]:
        if not self._has_meaningful_asset_evidence(graph):
            return []

        emit_progress(
            progress_callback,
            "No final chunks were produced. Retrying with an asset-aware fallback chunking policy...",
        )
        fallback_chunks = self.graph_chunk_builder.build_chunks(
            graph=graph,
            sections=sections,
            document_type_override=decision.effective_document_type,
            chunking_profile_override=ChunkingProfile.DEFAULT,
        )
        if fallback_chunks:
            emit_progress(
                progress_callback,
                f"Asset-aware fallback recovered {len(fallback_chunks)} chunk(s).",
            )
        return fallback_chunks

    @staticmethod
    def _has_meaningful_asset_evidence(graph: DocumentGraph) -> bool:
        for asset in graph.tables.values():
            if asset.has_content():
                return True

        for asset in graph.pictures.values():
            if (
                asset.has_ocr_text()
                or bool(asset.metadata.caption and asset.metadata.caption.strip())
                or bool(asset.metadata.nearby_text and asset.metadata.nearby_text.strip())
            ):
                return True

        for element in graph.elements.values():
            parser_extra = (
                element.parser_metadata.extra
                if element.parser_metadata is not None
                else {}
            )
            if element.table_id and str(parser_extra.get("markdown") or "").strip():
                return True
            if element.picture_id and any(
                str(parser_extra.get(key) or "").strip()
                for key in ("caption", "ocr_text", "nearby_text")
            ):
                return True
        return False
