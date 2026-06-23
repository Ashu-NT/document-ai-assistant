from src.application.services.document import DocumentLookupService
from src.application.services.document_exploration.document_exploration_result import (
    AssetEntry,
    DocumentCoverage,
    DocumentExplorationResult,
    DocumentOverview,
    IdentifierEntry,
    SectionEntry,
    TableEntry,
)
from src.domain.document import DocumentGraph
from src.shared.activity import ActivityContext


class DocumentNotFoundError(Exception):
    pass


class DocumentExplorationService:
    def __init__(self, document_lookup_service: DocumentLookupService) -> None:
        self.document_lookup_service = document_lookup_service

    def explore(
        self,
        document_id: str,
        activity_context: ActivityContext | None = None,
    ) -> DocumentExplorationResult:
        graph = self.document_lookup_service.get_document_graph(
            document_id, activity_context=activity_context
        )
        if graph is None:
            raise DocumentNotFoundError(document_id)
        return self._build_result(graph)

    def explore_graph(self, graph: DocumentGraph) -> DocumentExplorationResult:
        return self._build_result(graph)

    def _build_result(self, graph: DocumentGraph) -> DocumentExplorationResult:
        overview = self._build_overview(graph)
        sections = self._build_sections(graph)
        identifiers = self._build_identifiers(graph)
        tables = self._build_tables(graph)
        assets = self._build_assets(graph)
        coverage = self._build_coverage(graph)
        return DocumentExplorationResult(
            document_id=graph.document.document_id,
            overview=overview,
            sections=sections,
            identifiers=identifiers,
            tables=tables,
            assets=assets,
            coverage=coverage,
        )

    @staticmethod
    def _build_overview(graph: DocumentGraph) -> DocumentOverview:
        doc = graph.document
        stats = doc.statistics
        return DocumentOverview(
            document_id=doc.document_id,
            title=doc.title,
            file_name=doc.file_name,
            document_type=str(doc.document_type),
            language=doc.language,
            page_count=stats.page_count,
            section_count=stats.section_count or len(graph.sections),
            chunk_count=stats.chunk_count or len(graph.chunks),
            table_count=stats.table_count or len(graph.tables),
            picture_count=stats.picture_count or len(graph.pictures),
            identifier_count=stats.identifier_count or len(graph.identifiers),
        )

    @staticmethod
    def _build_sections(graph: DocumentGraph) -> list[SectionEntry]:
        sections = sorted(
            graph.sections.values(),
            key=lambda s: (s.sequence_number if s.sequence_number is not None else 0),
        )
        return [
            SectionEntry(
                section_id=s.section_id,
                title=s.title,
                level=s.level,
                parent_section_id=s.parent_section_id,
                section_path=list(s.section_path),
                overview_text=s.overview_text,
                chunk_type_signals=list(s.chunk_type_signals),
            )
            for s in sections
        ]

    @staticmethod
    def _build_identifiers(graph: DocumentGraph) -> list[IdentifierEntry]:
        return [
            IdentifierEntry(
                identifier_id=ident.identifier_id,
                raw_value=ident.raw_value,
                identifier_type=str(ident.identifier_type),
                normalized_value=ident.normalized_value,
            )
            for ident in sorted(
                graph.identifiers.values(),
                key=lambda i: (str(i.identifier_type), i.raw_value),
            )
        ]

    @staticmethod
    def _build_tables(graph: DocumentGraph) -> list[TableEntry]:
        section_titles: dict[str, str] = {
            s.section_id: s.title for s in graph.sections.values()
        }
        return [
            TableEntry(
                table_id=t.table_id,
                caption=t.metadata.caption,
                section_title=section_titles.get(t.parent_section_id)
                if t.parent_section_id
                else None,
                page=t.metadata.source.page_start,
            )
            for t in graph.tables.values()
        ]

    @staticmethod
    def _build_assets(graph: DocumentGraph) -> list[AssetEntry]:
        section_titles: dict[str, str] = {
            s.section_id: s.title for s in graph.sections.values()
        }
        return [
            AssetEntry(
                picture_id=p.picture_id,
                caption=p.metadata.caption,
                section_title=section_titles.get(p.parent_section_id)
                if p.parent_section_id
                else None,
                page=p.metadata.source.page_start,
                has_ocr_text=p.has_ocr_text(),
            )
            for p in graph.pictures.values()
        ]

    @staticmethod
    def _build_coverage(graph: DocumentGraph) -> DocumentCoverage:
        return DocumentCoverage(
            chunk_type_counts=dict(graph.document.statistics.chunk_type_counts),
            has_tables=bool(graph.tables),
            has_pictures=bool(graph.pictures),
            has_identifiers=bool(graph.identifiers),
            has_sections=bool(graph.sections),
        )
