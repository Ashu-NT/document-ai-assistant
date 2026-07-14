import json
from dataclasses import replace as dataclass_replace

from src.application.workflows.parsing.tables.families import (
    LogicalTableFamilyLookup,
    LogicalTableFamilyRowMerger,
)
from src.application.workflows.parsing.tables.structure import (
    TableStructureContextRenderer,
)
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
    def __init__(
        self,
        *,
        table_structure_context_renderer: TableStructureContextRenderer | None = None,
    ) -> None:
        self.table_structure_context_renderer = (
            table_structure_context_renderer or TableStructureContextRenderer()
        )

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

            family_lookup = LogicalTableFamilyLookup.from_tables(graph.tables)
            row_merger = LogicalTableFamilyRowMerger()
            family_id = (
                source_chunk.logical_table_family_id
                or family_lookup.family_id_for_table_ids(source_chunk.table_ids)
            )
            if family_id:
                group_key = (chunk.document_id, family_id)
            else:
                group_key = (
                    chunk.document_id,
                    ",".join(sorted(source_chunk.table_ids)),
                )
            if group_key in seen_table_keys:
                continue

            qualifying_tables = [
                table
                for table in family_lookup.members_for_table_ids(source_chunk.table_ids)
                if table.has_content()
            ]
            if not qualifying_tables:
                hydrated_chunks.append(chunk)
                continue

            table_texts = [
                self._table_text_with_structured_rows(table)
                for table in qualifying_tables
            ]

            seen_table_keys.add(group_key)
            metadata = dict(chunk.metadata)
            metadata["table_evidence_hydrated"] = "true"
            hydrated_table_ids = [table.table_id for table in qualifying_tables]
            metadata["hydrated_table_ids"] = ",".join(hydrated_table_ids)
            if family_id:
                metadata["logical_table_family_id"] = family_id
            table_category = source_chunk.table_category or next(
                (table.table_category for table in qualifying_tables if table.table_category),
                None,
            )
            if table_category:
                metadata["table_category"] = table_category
            table_category_confidence = (
                source_chunk.table_category_confidence
                if source_chunk.table_category_confidence is not None
                else next(
                    (
                        table.table_category_confidence
                        for table in qualifying_tables
                        if table.table_category_confidence is not None
                    ),
                    None,
                )
            )
            if table_category_confidence is not None:
                metadata["table_category_confidence"] = str(table_category_confidence)
            table_shape = self._resolve_table_shape(qualifying_tables)
            if table_shape:
                metadata["table_shape"] = table_shape
            table_structure_quality = self._resolve_table_structure_quality(
                qualifying_tables
            )
            if table_structure_quality is not None:
                metadata["table_structure_quality"] = str(table_structure_quality)
            header_paths = self._merge_header_paths(qualifying_tables)
            if header_paths:
                metadata["table_header_paths_json"] = json.dumps(header_paths)
            axis_summary = self._merge_axis_summary(qualifying_tables)
            if axis_summary:
                metadata["table_axis_summary"] = json.dumps(axis_summary)
            merged_rows = row_merger.merge_tables(qualifying_tables)
            if merged_rows is not None:
                metadata["table_rows_json"] = json.dumps(merged_rows)
            hydrated_chunks.append(
                dataclass_replace(
                    chunk,
                    content="\n\n".join(table_texts),
                    metadata=metadata,
                )
            )

        return hydrated_chunks

    def _table_text_with_structured_rows(self, table: TableAsset) -> str:
        parts: list[str] = []
        structure_context = self.table_structure_context_renderer.render(table)
        if structure_context:
            parts.append(structure_context)
        parts.append(table.to_embedding_text())
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

    @staticmethod
    def _resolve_table_shape(tables: list[TableAsset]) -> str | None:
        for table in tables:
            table_shape = table.resolved_table_shape()
            if table_shape:
                return table_shape
        return None

    @staticmethod
    def _resolve_table_structure_quality(tables: list[TableAsset]) -> float | None:
        for table in tables:
            if table.table_structure_quality is not None:
                return table.table_structure_quality
        return None

    @staticmethod
    def _merge_header_paths(tables: list[TableAsset]) -> list[list[str]]:
        merged: list[list[str]] = []
        seen: set[tuple[str, ...]] = set()
        for table in tables:
            for path in table.header_paths:
                cleaned = tuple(
                    str(part).strip() for part in path if str(part).strip()
                )
                if not cleaned or cleaned in seen:
                    continue
                seen.add(cleaned)
                merged.append(list(cleaned))
        return merged

    @staticmethod
    def _merge_axis_summary(tables: list[TableAsset]) -> dict[str, str]:
        merged: dict[str, str] = {}
        for table in tables:
            for key, value in table.axis_summary.items():
                cleaned_key = str(key).strip()
                cleaned_value = str(value).strip()
                if cleaned_key and cleaned_value and cleaned_key not in merged:
                    merged[cleaned_key] = cleaned_value
        return merged
