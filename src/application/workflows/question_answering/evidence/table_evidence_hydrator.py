import json
from dataclasses import replace as dataclass_replace

from src.domain.assets import TableAsset
from src.domain.common import ChunkType
from src.domain.document import DocumentGraph
from src.domain.retrieval import RetrievedChunk

_TABLE_LIKE_CHUNK_TYPES = {
    ChunkType.SPARE_PARTS_TABLE,
    ChunkType.TECHNICAL_SPECIFICATION,
    ChunkType.CERTIFICATION_INFO,
    ChunkType.TROUBLESHOOTING,
    ChunkType.MAINTENANCE_INTERVAL,
    ChunkType.MAINTENANCE_PROCEDURE,
}


class TableEvidenceHydrator:
    def hydrate(
        self,
        *,
        chunks: list[RetrievedChunk],
        graphs_by_document_id: dict[str, DocumentGraph],
    ) -> list[RetrievedChunk]:
        seen_table_keys: set[tuple[str, str]] = set()
        hydrated_chunks: list[RetrievedChunk] = []

        for chunk in chunks:
            graph = graphs_by_document_id.get(chunk.document_id)
            if graph is None:
                hydrated_chunks.append(chunk)
                continue

            source_chunk = graph.chunks.get(chunk.chunk_id)
            if source_chunk is None or not source_chunk.table_ids:
                hydrated_chunks.append(chunk)
                continue

            if not self._should_hydrate(chunk):
                hydrated_chunks.append(chunk)
                continue

            unseen_table_ids = [
                table_id
                for table_id in source_chunk.table_ids
                if (chunk.document_id, table_id) not in seen_table_keys
            ]
            if not unseen_table_ids:
                continue

            qualifying_tables = [
                graph.tables[table_id]
                for table_id in unseen_table_ids
                if table_id in graph.tables and graph.tables[table_id].has_content()
            ]
            if not qualifying_tables:
                hydrated_chunks.append(chunk)
                continue

            table_texts = [
                self._table_text_with_structured_rows(table)
                for table in qualifying_tables
            ]

            seen_table_keys.update(
                (chunk.document_id, table_id) for table_id in unseen_table_ids
            )
            metadata = dict(chunk.metadata)
            metadata["table_evidence_hydrated"] = "true"
            metadata["hydrated_table_ids"] = ",".join(unseen_table_ids)
            # Structured rows are only stashed for the first qualifying table --
            # a chunk referencing more than one table is rare (chunk fragments
            # are built per-table-element), and every downstream consumer
            # expects a single row grid per chunk.
            structured_table = next(
                (table for table in qualifying_tables if table.has_structured_rows()),
                None,
            )
            if structured_table is not None:
                metadata["table_rows_json"] = json.dumps(structured_table.rows)
            hydrated_chunks.append(
                dataclass_replace(
                    chunk,
                    content="\n\n".join(table_texts),
                    metadata=metadata,
                )
            )

        return hydrated_chunks

    @staticmethod
    def _table_text_with_structured_rows(table: TableAsset) -> str:
        parts = [table.to_embedding_text()]
        structured_rows = table.to_structured_row_text()
        if structured_rows:
            parts.append(structured_rows)
        return "\n\n".join(parts)

    @staticmethod
    def _should_hydrate(chunk: RetrievedChunk) -> bool:
        if chunk.metadata.get("context_relation") == "asset_companion":
            return False

        if chunk.chunk_type in _TABLE_LIKE_CHUNK_TYPES:
            return True

        return "|" in chunk.content
