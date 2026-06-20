from src.application.workflows.parsing.canonical_element import (
    CanonicalElement as ParsedCanonicalElement,
)
from src.application.workflows.parsing.builders.document_graph.source_location_factory import (
    SourceLocationFactory,
)
from src.domain.assets import AssetMetadata, PictureAsset, TableAsset
from src.shared.ids import IdGenerator


class ParsedAssetFactory:
    def __init__(self, id_generator: IdGenerator) -> None:
        self.id_generator = id_generator

    def build_table_asset(
        self,
        *,
        document_id: str,
        parent_section_id: str | None,
        parsed_element: ParsedCanonicalElement,
    ) -> tuple[str, TableAsset]:
        table_id = self.id_generator.new_id("table")
        return (
            table_id,
            TableAsset(
                table_id=table_id,
                document_id=document_id,
                markdown=(
                    parsed_element.metadata.get("markdown")
                    or parsed_element.text
                    or ""
                ),
                parent_section_id=parent_section_id,
                metadata=AssetMetadata(
                    source=SourceLocationFactory.from_parsed(parsed_element),
                    caption=parsed_element.metadata.get("caption"),
                ),
            ),
        )

    def build_picture_asset(
        self,
        *,
        document_id: str,
        parent_section_id: str | None,
        parsed_element: ParsedCanonicalElement,
    ) -> tuple[str, PictureAsset]:
        picture_id = self.id_generator.new_id("picture")
        return (
            picture_id,
            PictureAsset(
                picture_id=picture_id,
                document_id=document_id,
                parent_section_id=parent_section_id,
                image_path=parsed_element.metadata.get("image_path"),
                ocr_text=parsed_element.metadata.get("ocr_text"),
                metadata=AssetMetadata(
                    source=SourceLocationFactory.from_parsed(parsed_element),
                    caption=parsed_element.metadata.get("caption")
                    or parsed_element.text,
                ),
            ),
        )
