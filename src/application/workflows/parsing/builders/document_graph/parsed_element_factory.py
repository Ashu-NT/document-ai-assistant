from src.application.workflows.parsing.builders.document_graph.source_location_factory import (
    SourceLocationFactory,
)
from src.application.workflows.parsing.canonical_element import (
    CanonicalElement as ParsedCanonicalElement,
)
from src.domain.common import ParserMetadata
from src.domain.elements import CanonicalElement
from src.shared.ids import IdGenerator, IdPrefix


class ParsedElementFactory:
    def __init__(
        self,
        *,
        id_generator: IdGenerator,
        parser_name: str,
        parser_version: str | None,
    ) -> None:
        self.id_generator = id_generator
        self.parser_name = parser_name
        self.parser_version = parser_version

    def build(
        self,
        *,
        document_id: str,
        parsed_element: ParsedCanonicalElement,
        parent_section_id: str | None,
        resolved_section_path: list[str],
        effective_heading_level: int | None,
        heading_level_source: str | None,
        table_id: str | None,
        picture_id: str | None,
    ) -> CanonicalElement:
        return CanonicalElement(
            element_id=self.id_generator.new_id(IdPrefix.ELEMENT),
            document_id=document_id,
            element_type=parsed_element.element_type,
            text=parsed_element.text,
            parent_section_id=parent_section_id,
            reading_order=parsed_element.order_index,
            source=SourceLocationFactory.from_parsed(parsed_element),
            table_id=table_id,
            picture_id=picture_id,
            parser_metadata=ParserMetadata(
                parser_name=self.parser_name,
                parser_version=self.parser_version,
                raw_source_type=parsed_element.metadata.get("raw_source_type"),
                raw_ref=parsed_element.raw_ref,
                extra={
                    **dict(parsed_element.metadata),
                    "resolved_section_path": list(resolved_section_path),
                    "effective_heading_level": effective_heading_level,
                    "heading_level_source": heading_level_source,
                },
            ),
        )
