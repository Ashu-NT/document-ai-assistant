from src.application.workflows.parsing.tables.structure.table_shape_resolver import (
    TableShapeResolver,
)
from src.domain.document import DocumentGraph

_TABLE_SHAPE_RESOLVER = TableShapeResolver()


class AssetMetadataSynchronizer:
    """Syncs table/picture asset metadata (markdown, caption, nearby text, OCR
    text, image path) onto each element's parser_metadata.extra so downstream
    chunking sees the enriched values."""

    @staticmethod
    def sync(graph: DocumentGraph) -> None:
        for element in graph.elements.values():
            if element.parser_metadata is None:
                continue

            parser_extra = element.parser_metadata.extra
            if element.table_id is not None and element.table_id in graph.tables:
                table_asset = graph.tables[element.table_id]
                table_shape = _TABLE_SHAPE_RESOLVER.resolve(table_asset)
                parser_extra["markdown"] = table_asset.markdown
                parser_extra["table_rows"] = [list(row) for row in table_asset.rows]
                if table_asset.parallel_stream_rows:
                    parser_extra["table_parallel_stream_rows"] = [
                        [list(row) for row in stream_rows]
                        for stream_rows in table_asset.parallel_stream_rows
                    ]
                    parser_extra["table_parallel_stream_count"] = len(
                        table_asset.parallel_stream_rows
                    )
                if table_asset.parallel_stream_descriptors:
                    parser_extra["table_parallel_stream_descriptors"] = [
                        descriptor.to_dict()
                        for descriptor in table_asset.parallel_stream_descriptors
                    ]
                if table_asset.local_reading_order:
                    parser_extra["table_local_reading_order"] = (
                        table_asset.local_reading_order
                    )
                parser_extra["table_row_ids"] = list(table_asset.row_ids)
                parser_extra["table_cell_spans"] = [
                    span.to_dict() for span in table_asset.cell_spans
                ]
                parser_extra["row_count"] = table_asset.row_count
                parser_extra["column_count"] = table_asset.column_count
                parser_extra["table_structure_version"] = "1"
                if table_shape:
                    parser_extra["table_shape"] = table_shape
                if table_asset.table_structure_quality is not None:
                    parser_extra["table_structure_quality"] = (
                        table_asset.table_structure_quality
                    )
                if table_asset.header_paths:
                    parser_extra["table_header_paths_json"] = [
                        list(path) for path in table_asset.header_paths
                    ]
                if table_asset.axis_summary:
                    parser_extra["table_axis_summary"] = dict(table_asset.axis_summary)
                if table_asset.metadata.caption:
                    parser_extra["caption"] = table_asset.metadata.caption
                if table_asset.metadata.nearby_text:
                    parser_extra["nearby_text"] = table_asset.metadata.nearby_text

            if element.picture_id is not None and element.picture_id in graph.pictures:
                picture_asset = graph.pictures[element.picture_id]
                if picture_asset.metadata.caption:
                    parser_extra["caption"] = picture_asset.metadata.caption
                if picture_asset.metadata.nearby_text:
                    parser_extra["nearby_text"] = picture_asset.metadata.nearby_text
                if picture_asset.ocr_text:
                    parser_extra["ocr_text"] = picture_asset.ocr_text
                if picture_asset.ocr_provider:
                    parser_extra["ocr_provider"] = picture_asset.ocr_provider
                if picture_asset.ocr_confidence is not None:
                    parser_extra["ocr_confidence"] = picture_asset.ocr_confidence
                if picture_asset.ocr_mode:
                    parser_extra["ocr_mode"] = picture_asset.ocr_mode
                parser_extra["ocr_provenance_version"] = "1"
                if picture_asset.image_path:
                    parser_extra["image_path"] = picture_asset.image_path
