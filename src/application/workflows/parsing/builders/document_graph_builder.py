from pathlib import Path

from src.application.workflows.parsing.builders.chunking import SectionChunkBuilder
from src.application.workflows.parsing.builders.section_build_result import (
    SectionBuildResult,
)
from src.application.workflows.parsing.builders.section_builder import SectionBuilder
from src.application.workflows.parsing.canonical_element import (
    CanonicalElement as ParsedCanonicalElement,
)
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.domain.assets import AssetMetadata, PictureAsset, TableAsset
from src.domain.common import (
    BoundingBox,
    DocumentType,
    ElementType,
    ParserMetadata,
    SourceLocation,
)
from src.domain.document import (
    Document,
    DocumentChunk,
    DocumentGraph,
    DocumentHashes,
    DocumentStatistics,
)
from src.domain.elements import CanonicalElement
from src.shared.exceptions import ChunkingError
from src.shared.ids import IdGenerator, IdPrefix


class DocumentGraphBuilder:
    def __init__(
        self,
        id_generator: IdGenerator,
        section_builder: SectionBuilder,
        *,
        max_chunk_tokens: int = 200,
        chunk_overlap: int = 20,
        min_section_text_length: int = 20,
        section_chunk_builder: SectionChunkBuilder | None = None,
    ) -> None:
        self.id_generator = id_generator
        self.section_builder = section_builder
        self.section_chunk_builder = section_chunk_builder or SectionChunkBuilder(
            max_chunk_tokens=max_chunk_tokens,
            chunk_overlap=chunk_overlap,
            min_section_text_length=min_section_text_length,
        )
        self.last_section_build_result: SectionBuildResult | None = None

    def build(
        self,
        *,
        document_id: str,
        file_path: str,
        hashes: DocumentHashes,
        canonical_elements: list[ParsedCanonicalElement],
        raw_parsed_document: RawParsedDocument,
    ) -> DocumentGraph:
        try:
            document = Document(
                document_id=document_id,
                file_name=Path(file_path).name,
                file_path=file_path,
                hashes=hashes,
                title=raw_parsed_document.title or Path(file_path).stem,
                document_type=DocumentType.UNKNOWN,
                language=self._extract_language(raw_parsed_document),
            )

            graph = DocumentGraph(document=document)

            section_build_result = self.section_builder.build(
                document_id,
                canonical_elements,
                default_title=raw_parsed_document.title or "Document",
            )
            self.last_section_build_result = section_build_result
            sections = section_build_result.sections
            section_lookup = {section.section_id: section for section in sections}

            for section in sections:
                graph.add_section(section)

            ordered_elements = sorted(
                canonical_elements,
                key=lambda element: element.order_index,
            )

            for parsed_element in ordered_elements:
                parent_section_id = self.section_builder.resolve_section_id(
                    parsed_element,
                    section_build_result,
                )
                resolved_section_path = self.section_builder.resolve_section_path(
                    parsed_element,
                    section_build_result,
                )
                table_id = None
                picture_id = None

                if parsed_element.element_type == ElementType.TABLE:
                    table_id = self._create_table_asset(
                        graph,
                        document_id=document_id,
                        parent_section_id=parent_section_id,
                        parsed_element=parsed_element,
                    )

                if parsed_element.element_type == ElementType.PICTURE:
                    picture_id = self._create_picture_asset(
                        graph,
                        document_id=document_id,
                        parent_section_id=parent_section_id,
                        parsed_element=parsed_element,
                    )

                domain_element = CanonicalElement(
                    element_id=self.id_generator.new_id(IdPrefix.ELEMENT),
                    document_id=document_id,
                    element_type=parsed_element.element_type,
                    text=parsed_element.text,
                    parent_section_id=parent_section_id,
                    reading_order=parsed_element.order_index,
                    source=self._source_from_parsed(parsed_element),
                    table_id=table_id,
                    picture_id=picture_id,
                    parser_metadata=ParserMetadata(
                        parser_name=raw_parsed_document.parser_name,
                        parser_version=raw_parsed_document.parser_version,
                        raw_source_type=parsed_element.metadata.get("raw_source_type"),
                        raw_ref=parsed_element.raw_ref,
                        extra={
                            **dict(parsed_element.metadata),
                            "resolved_section_path": list(resolved_section_path),
                            "effective_heading_level": section_build_result.header_levels.get(
                                parsed_element.element_id
                            ),
                            "heading_level_source": section_build_result.header_sources.get(
                                parsed_element.element_id
                            ),
                        },
                    ),
                )

                graph.add_element(domain_element)
                if parent_section_id and parent_section_id in section_lookup:
                    section = section_lookup[parent_section_id]
                    section.element_ids.append(domain_element.element_id)
                    self._update_section_boundaries(section, domain_element)

            for chunk in self._build_chunks(graph, sections):
                graph.add_chunk(chunk)

            graph.document.statistics = DocumentStatistics(
                page_count=raw_parsed_document.page_count,
                element_count=len(graph.elements),
                section_count=len(graph.sections),
                chunk_count=len(graph.chunks),
                table_count=len(graph.tables),
                picture_count=len(graph.pictures),
            )

            return graph
        except ChunkingError:
            raise
        except Exception as exc:
            raise ChunkingError(
                "Failed to build document graph from canonical elements.",
                details={
                    "document_id": document_id,
                    "file_path": file_path,
                },
            ) from exc

    def _create_table_asset(
        self,
        graph: DocumentGraph,
        *,
        document_id: str,
        parent_section_id: str | None,
        parsed_element: ParsedCanonicalElement,
    ) -> str:
        table_id = self.id_generator.new_id("table")
        graph.tables[table_id] = TableAsset(
            table_id=table_id,
            document_id=document_id,
            markdown=(
                parsed_element.metadata.get("markdown")
                or parsed_element.text
                or ""
            ),
            parent_section_id=parent_section_id,
            metadata=AssetMetadata(
                source=self._source_from_parsed(parsed_element),
                caption=parsed_element.metadata.get("caption"),
            ),
        )
        return table_id

    def _create_picture_asset(
        self,
        graph: DocumentGraph,
        *,
        document_id: str,
        parent_section_id: str | None,
        parsed_element: ParsedCanonicalElement,
    ) -> str:
        picture_id = self.id_generator.new_id("picture")
        graph.pictures[picture_id] = PictureAsset(
            picture_id=picture_id,
            document_id=document_id,
            parent_section_id=parent_section_id,
            image_path=parsed_element.metadata.get("image_path"),
            ocr_text=parsed_element.metadata.get("ocr_text"),
            metadata=AssetMetadata(
                source=self._source_from_parsed(parsed_element),
                caption=parsed_element.metadata.get("caption") or parsed_element.text,
            ),
        )
        return picture_id

    def _build_chunks(
        self,
        graph: DocumentGraph,
        sections: list,
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        sequence_number = 1

        for section in sorted(sections, key=lambda value: value.sequence_number or 0):
            elements = graph.get_section_elements(section.section_id)
            chunk_payloads = self.section_chunk_builder.build_chunk_payloads(
                document_title=graph.document.title,
                section=section,
                elements=elements,
            )
            total_windows = len(chunk_payloads)

            for chunk_index, chunk_payload in enumerate(chunk_payloads, start=1):
                chunks.append(
                    DocumentChunk(
                        chunk_id=self.id_generator.new_id(IdPrefix.CHUNK),
                        document_id=graph.document.document_id,
                        section_id=chunk_payload.section_id,
                        content=chunk_payload.content,
                        chunk_type=chunk_payload.chunk_type,
                        section_path=list(chunk_payload.section_path),
                        element_ids=list(chunk_payload.element_ids),
                        table_ids=list(chunk_payload.table_ids),
                        picture_ids=list(chunk_payload.picture_ids),
                        source=SourceLocation(
                            page_start=chunk_payload.page_start,
                            page_end=chunk_payload.page_end,
                        ),
                        sequence_number=sequence_number,
                        chunk_index=chunk_index,
                        chunk_total=total_windows,
                        embedding_text=chunk_payload.embedding_text,
                    )
                )
                sequence_number += 1

        return chunks

    @staticmethod
    def _source_from_parsed(parsed_element: ParsedCanonicalElement) -> SourceLocation:
        bbox = None
        if parsed_element.bbox is not None:
            bbox = BoundingBox(
                x1=parsed_element.bbox.x1,
                y1=parsed_element.bbox.y1,
                x2=parsed_element.bbox.x2,
                y2=parsed_element.bbox.y2,
            )

        return SourceLocation(
            page_start=parsed_element.page_start,
            page_end=parsed_element.page_end,
            bbox=bbox,
        )

    @staticmethod
    def _update_section_boundaries(section, element: CanonicalElement) -> None:
        reading_order = element.reading_order
        if reading_order is not None:
            if section.reading_order_start is None or reading_order < section.reading_order_start:
                section.reading_order_start = reading_order
            if section.reading_order_end is None or reading_order > section.reading_order_end:
                section.reading_order_end = reading_order

        source = element.source
        if source.page_start is not None:
            if section.source.page_start is None or source.page_start < section.source.page_start:
                section.source.page_start = source.page_start
        if source.page_end is not None:
            if section.source.page_end is None or source.page_end > section.source.page_end:
                section.source.page_end = source.page_end

    @staticmethod
    def _extract_language(raw_parsed_document: RawParsedDocument) -> str | None:
        language = raw_parsed_document.metadata.get("language")
        if isinstance(language, str) and language.strip():
            return language.strip()
        return None

    @staticmethod
    def _min_page(elements: list[CanonicalElement]) -> int | None:
        pages = [
            element.source.page_start
            for element in elements
            if element.source.page_start is not None
        ]
        return min(pages) if pages else None

    @staticmethod
    def _max_page(elements: list[CanonicalElement]) -> int | None:
        pages = [
            element.source.page_end
            for element in elements
            if element.source.page_end is not None
        ]
        return max(pages) if pages else None

    @staticmethod
    def _merge_min_page(
        left: int | None,
        right: int | None,
    ) -> int | None:
        values = [value for value in [left, right] if value is not None]
        return min(values) if values else None

    @staticmethod
    def _merge_max_page(
        left: int | None,
        right: int | None,
    ) -> int | None:
        values = [value for value in [left, right] if value is not None]
        return max(values) if values else None
