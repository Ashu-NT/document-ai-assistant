from pathlib import Path

from src.application.workflows.parsing.builders.chunking import SectionChunkBuilder
from src.application.workflows.parsing.builders.document_graph import (
    AssetNearbyTextEnricher,
    GraphChunkBuilder,
    ParsedAssetFactory,
    ParsedElementFactory,
)
from src.application.workflows.parsing.builders.section_build_result import (
    SectionBuildResult,
)
from src.application.workflows.parsing.builders.section_builder import SectionBuilder
from src.application.workflows.parsing.canonical_element import (
    CanonicalElement as ParsedCanonicalElement,
)
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.domain.common import DocumentType, ElementType
from src.domain.document import (
    Document,
    DocumentGraph,
    DocumentHashes,
    DocumentStatistics,
)
from src.domain.elements import CanonicalElement
from src.shared.exceptions import ChunkingError
from src.shared.ids import IdGenerator


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
        if section_chunk_builder is not None:
            self.section_chunk_builder = section_chunk_builder
        else:
            section_chunk_builder_kwargs: dict[str, int] = {}
            if max_chunk_tokens != 200:
                section_chunk_builder_kwargs["max_chunk_tokens"] = max_chunk_tokens
            if chunk_overlap != 20:
                section_chunk_builder_kwargs["chunk_overlap"] = chunk_overlap
            if min_section_text_length != 20:
                section_chunk_builder_kwargs["min_section_text_length"] = (
                    min_section_text_length
                )
            self.section_chunk_builder = SectionChunkBuilder(
                **section_chunk_builder_kwargs,
            )
        self.asset_factory = ParsedAssetFactory(id_generator)
        self.asset_nearby_text_enricher = AssetNearbyTextEnricher()
        self.chunk_builder = GraphChunkBuilder(
            id_generator=id_generator,
            section_chunk_builder=self.section_chunk_builder,
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
                document_type=self._extract_document_type(raw_parsed_document),
                language=self._extract_language(raw_parsed_document),
            )

            graph = DocumentGraph(document=document)
            element_factory = ParsedElementFactory(
                id_generator=self.id_generator,
                parser_name=raw_parsed_document.parser_name,
                parser_version=raw_parsed_document.parser_version,
            )

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
                    table_id, table_asset = self.asset_factory.build_table_asset(
                        document_id=document_id,
                        parent_section_id=parent_section_id,
                        parsed_element=parsed_element,
                    )
                    graph.tables[table_id] = table_asset

                if parsed_element.element_type == ElementType.PICTURE:
                    picture_id, picture_asset = self.asset_factory.build_picture_asset(
                        document_id=document_id,
                        parent_section_id=parent_section_id,
                        parsed_element=parsed_element,
                    )
                    graph.pictures[picture_id] = picture_asset

                domain_element = element_factory.build(
                    document_id=document_id,
                    parsed_element=parsed_element,
                    parent_section_id=parent_section_id,
                    resolved_section_path=resolved_section_path,
                    effective_heading_level=section_build_result.header_levels.get(
                        parsed_element.element_id
                    ),
                    heading_level_source=section_build_result.header_sources.get(
                        parsed_element.element_id
                    ),
                    table_id=table_id,
                    picture_id=picture_id,
                )

                graph.add_element(domain_element)
                if parent_section_id and parent_section_id in section_lookup:
                    section = section_lookup[parent_section_id]
                    section.element_ids.append(domain_element.element_id)
                    self._update_section_boundaries(section, domain_element)

            self.asset_nearby_text_enricher.enrich(graph)

            for chunk in self.chunk_builder.build_chunks(graph=graph, sections=sections):
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
    def _extract_document_type(raw_parsed_document: RawParsedDocument) -> DocumentType:
        raw_document_type = raw_parsed_document.metadata.get("document_type")
        if isinstance(raw_document_type, str):
            normalized = raw_document_type.strip().lower()
            for document_type in DocumentType:
                if normalized == document_type.value:
                    return document_type

        title = (raw_parsed_document.title or "").strip().lower()
        title_markers = {
            "datasheet": DocumentType.DATASHEET,
            "manual": DocumentType.MANUAL,
            "drawing": DocumentType.DRAWING,
            "report": DocumentType.REPORT,
            "certificate": DocumentType.CERTIFICATE,
        }
        for marker, document_type in title_markers.items():
            if marker in title:
                return document_type

        return DocumentType.UNKNOWN
