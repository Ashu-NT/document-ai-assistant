from src.domain.document import DocumentGraph


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
                parser_extra["markdown"] = table_asset.markdown
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
                if picture_asset.image_path:
                    parser_extra["image_path"] = picture_asset.image_path
