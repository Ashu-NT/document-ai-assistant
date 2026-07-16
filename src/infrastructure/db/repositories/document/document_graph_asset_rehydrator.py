from src.domain.assets import AssetMetadata, PictureAsset, TableAsset, TableCellSpan
from src.domain.document import DocumentGraph
from src.infrastructure.db.repositories.document.document_graph_value_cleaners import (
    clean_axis_summary,
    clean_header_paths,
    clean_multiline_text,
    clean_parallel_stream_rows,
    clean_rows,
    clean_text,
    coerce_float,
)


def rehydrate_assets(graph: DocumentGraph) -> None:
    for element in graph.elements.values():
        parser_metadata = element.parser_metadata
        parser_extra = parser_metadata.extra if parser_metadata is not None else {}

        if element.table_id is not None and element.table_id not in graph.tables:
            graph.tables[element.table_id] = TableAsset(
                table_id=element.table_id,
                document_id=element.document_id,
                parent_section_id=element.parent_section_id,
                markdown=clean_multiline_text(
                    parser_extra.get("markdown") or element.text or ""
                )
                or "",
                rows=clean_rows(parser_extra.get("table_rows")),
                parallel_stream_rows=clean_parallel_stream_rows(
                    parser_extra.get("table_parallel_stream_rows")
                ),
                row_ids=[
                    str(row_id)
                    for row_id in (parser_extra.get("table_row_ids") or [])
                    if str(row_id).strip()
                ],
                cell_spans=TableCellSpan.list_from_data(
                    parser_extra.get("table_cell_spans")
                ),
                row_count=parser_extra.get("row_count"),
                column_count=parser_extra.get("column_count"),
                local_reading_order=parser_extra.get("table_local_reading_order"),
                logical_table_family_id=parser_extra.get("logical_table_family_id"),
                family_index=parser_extra.get("family_index"),
                family_total=parser_extra.get("family_total"),
                continuation_role=parser_extra.get("continuation_role"),
                normalized_header_signature=parser_extra.get(
                    "normalized_header_signature"
                ),
                table_category=parser_extra.get("table_category"),
                table_category_confidence=parser_extra.get(
                    "table_category_confidence"
                ),
                table_shape=parser_extra.get("table_shape"),
                table_structure_quality=coerce_float(
                    parser_extra.get("table_structure_quality")
                ),
                header_paths=clean_header_paths(
                    parser_extra.get("table_header_paths_json")
                ),
                axis_summary=clean_axis_summary(
                    parser_extra.get("table_axis_summary")
                ),
                metadata=AssetMetadata(
                    source=element.source,
                    caption=(
                        clean_text(parser_extra.get("caption"))
                        if parser_extra.get("caption") is not None
                        else None
                    ),
                    nearby_text=(
                        clean_text(parser_extra.get("nearby_text"))
                        if parser_extra.get("nearby_text") is not None
                        else None
                    ),
                ),
            )

        if element.picture_id is not None and element.picture_id not in graph.pictures:
            graph.pictures[element.picture_id] = PictureAsset(
                picture_id=element.picture_id,
                document_id=element.document_id,
                parent_section_id=element.parent_section_id,
                image_path=(
                    str(parser_extra.get("image_path"))
                    if parser_extra.get("image_path") is not None
                    else None
                ),
                ocr_text=(
                    str(parser_extra.get("ocr_text"))
                    if parser_extra.get("ocr_text") is not None
                    else None
                ),
                ocr_confidence=coerce_float(parser_extra.get("ocr_confidence")),
                ocr_provider=(
                    str(parser_extra.get("ocr_provider"))
                    if parser_extra.get("ocr_provider") is not None
                    else None
                ),
                ocr_mode=(
                    str(
                        parser_extra.get("ocr_mode")
                        or parser_extra.get("ocr_target_type")
                    )
                    if (
                        parser_extra.get("ocr_mode") is not None
                        or parser_extra.get("ocr_target_type") is not None
                    )
                    else None
                ),
                metadata=AssetMetadata(
                    source=element.source,
                    caption=(
                        str(parser_extra.get("caption") or element.text)
                        if parser_extra.get("caption") is not None or element.text is not None
                        else None
                    ),
                    nearby_text=(
                        str(parser_extra.get("nearby_text"))
                        if parser_extra.get("nearby_text") is not None
                        else None
                    ),
                ),
            )
