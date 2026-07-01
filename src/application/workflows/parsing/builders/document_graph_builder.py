from collections import Counter, defaultdict
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
from src.application.workflows.parsing.profiling import GraphBuildProfiler
from src.application.workflows.parsing.canonical_element import (
    CanonicalElement as ParsedCanonicalElement,
)
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.domain.common import ChunkType, DocumentType, ElementType
from src.domain.document import (
    Document,
    DocumentGraph,
    DocumentHashes,
    DocumentStatistics,
)
from src.domain.elements import CanonicalElement
from src.shared.exceptions import ChunkingError
from src.shared.ids import IdGenerator


def _default_max_chunk_tokens() -> int:
    try:
        from src.config.settings import ingestion_settings
        return ingestion_settings.max_chunk_tokens
    except Exception:
        return 1000


def _default_chunk_overlap() -> int:
    try:
        from src.config.settings import ingestion_settings
        return ingestion_settings.chunk_overlap
    except Exception:
        return 150


def _default_min_section_text_length() -> int:
    try:
        from src.config.settings import ingestion_settings
        return ingestion_settings.min_section_text_length
    except Exception:
        return 150


class DocumentGraphBuilder:
    def __init__(
        self,
        id_generator: IdGenerator,
        section_builder: SectionBuilder,
        *,
        max_chunk_tokens: int | None = None,
        chunk_overlap: int | None = None,
        min_section_text_length: int | None = None,
        section_chunk_builder: SectionChunkBuilder | None = None,
        profiler: GraphBuildProfiler | None = None,
    ) -> None:
        self.id_generator = id_generator
        self.section_builder = section_builder
        self.profiler = profiler or GraphBuildProfiler.disabled()
        if section_chunk_builder is not None:
            self.section_chunk_builder = section_chunk_builder
        else:
            self.section_chunk_builder = SectionChunkBuilder(
                max_chunk_tokens=(
                    max_chunk_tokens
                    if max_chunk_tokens is not None
                    else _default_max_chunk_tokens()
                ),
                chunk_overlap=(
                    chunk_overlap
                    if chunk_overlap is not None
                    else _default_chunk_overlap()
                ),
                min_section_text_length=(
                    min_section_text_length
                    if min_section_text_length is not None
                    else _default_min_section_text_length()
                ),
                profiler=self.profiler,
            )
        self.asset_factory = ParsedAssetFactory(id_generator)
        self.asset_nearby_text_enricher = AssetNearbyTextEnricher(
            profiler=self.profiler
        )
        self.chunk_builder = GraphChunkBuilder(
            id_generator=id_generator,
            section_chunk_builder=self.section_chunk_builder,
            profiler=self.profiler,
        )
        self.last_section_build_result: SectionBuildResult | None = None
        if hasattr(self.section_builder, "set_profiler"):
            self.section_builder.set_profiler(self.profiler)
        if hasattr(self.section_chunk_builder, "set_profiler"):
            self.section_chunk_builder.set_profiler(self.profiler)

    def set_profiler(self, profiler: GraphBuildProfiler | None) -> None:
        self.profiler = profiler or GraphBuildProfiler.disabled()
        if hasattr(self.section_builder, "set_profiler"):
            self.section_builder.set_profiler(self.profiler)
        if hasattr(self.section_chunk_builder, "set_profiler"):
            self.section_chunk_builder.set_profiler(self.profiler)
        if hasattr(self.asset_nearby_text_enricher, "set_profiler"):
            self.asset_nearby_text_enricher.set_profiler(self.profiler)
        if hasattr(self.chunk_builder, "set_profiler"):
            self.chunk_builder.set_profiler(self.profiler)

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
            with self.profiler.measure(
                name="document_graph_builder.initialize_document",
                input_counts={"canonical_elements": len(canonical_elements)},
            ) as stage:
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
                stage.output_counts["document_id"] = document.document_id

            section_build_result = self.section_builder.build(
                document_id,
                canonical_elements,
                default_title=raw_parsed_document.title or "Document",
            )
            self.last_section_build_result = section_build_result
            sections = section_build_result.sections
            section_lookup = {section.section_id: section for section in sections}

            with self.profiler.measure(
                name="document_graph_builder.add_sections",
                input_counts={"sections": len(sections)},
            ) as stage:
                for section in sections:
                    graph.add_section(section)
                stage.output_counts["graph_sections"] = len(graph.sections)

            ordered_elements = sorted(
                canonical_elements,
                key=lambda element: element.order_index,
            )

            with self.profiler.measure(
                name="document_graph_builder.materialize_elements_assets",
                input_counts={"ordered_elements": len(ordered_elements)},
            ) as stage:
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
                stage.output_counts["graph_elements"] = len(graph.elements)
                stage.output_counts["tables"] = len(graph.tables)
                stage.output_counts["pictures"] = len(graph.pictures)

            self.asset_nearby_text_enricher.enrich(graph)
            self._sync_asset_metadata_to_elements(graph)

            with self.profiler.measure(
                name="graph_chunk_builder.build_chunks",
                input_counts={
                    "sections": len(sections),
                    "elements": len(graph.elements),
                },
            ) as stage:
                for chunk in self.chunk_builder.build_chunks(graph=graph, sections=sections):
                    graph.add_chunk(chunk)
                stage.output_counts["graph_chunks"] = len(graph.chunks)

            section_signals: defaultdict[str, set[str]] = defaultdict(set)
            chunk_type_counts: Counter[str] = Counter()
            with self.profiler.measure(
                name="document_graph_builder.aggregate_chunk_signals",
                input_counts={"chunks": len(graph.chunks)},
            ) as stage:
                for chunk in graph.chunks.values():
                    chunk_type_counts[str(chunk.chunk_type)] += 1
                    if chunk.section_id and chunk.chunk_type not in {
                        ChunkType.GENERAL,
                        ChunkType.UNKNOWN,
                    }:
                        section_signals[chunk.section_id].add(str(chunk.chunk_type))

                for section_id, signals in section_signals.items():
                    if section_id in graph.sections:
                        graph.sections[section_id].chunk_type_signals = sorted(signals)
                stage.output_counts["sections_with_signals"] = len(section_signals)

            with self.profiler.measure(
                name="document_graph_builder.compute_statistics",
                input_counts={
                    "elements": len(graph.elements),
                    "sections": len(graph.sections),
                    "chunks": len(graph.chunks),
                },
            ) as stage:
                graph.document.statistics = DocumentStatistics(
                    page_count=raw_parsed_document.page_count,
                    element_count=len(graph.elements),
                    section_count=len(graph.sections),
                    chunk_count=len(graph.chunks),
                    table_count=len(graph.tables),
                    picture_count=len(graph.pictures),
                    identifier_count=len(graph.identifiers),
                    chunk_type_counts=dict(chunk_type_counts),
                )
                stage.output_counts["chunk_type_counts"] = len(chunk_type_counts)

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

    @staticmethod
    def _sync_asset_metadata_to_elements(graph: DocumentGraph) -> None:
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
