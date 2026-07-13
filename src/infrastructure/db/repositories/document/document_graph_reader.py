from collections import Counter

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.assets import AssetMetadata, PictureAsset, TableAsset, TableCellSpan
from src.domain.document import DocumentGraph, DocumentStatistics
from src.infrastructure.db.mappers import (
    ChunkMapper,
    DocumentMapper,
    ElementMapper,
    IdentifierMapper,
    GeneratedQuestionMapper,
    SectionMapper,
)
from src.infrastructure.db.orm_models import (
    ChunkORM,
    DocumentORM,
    ElementORM,
    GeneratedQuestionORM,
    IdentifierORM,
    SectionORM,
)
from src.shared.exceptions import DatabaseError

class DocumentGraphReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_document_graph(self, document_id: str) -> DocumentGraph | None:
        try:
            document_orm = self.session.get(DocumentORM, document_id)

            if document_orm is None:
                return None

            graph = DocumentGraph(
                document=DocumentMapper.to_domain(document_orm),
            )

            sections = self.session.execute(
                select(SectionORM).where(SectionORM.document_id == document_id)
            ).scalars().all()

            elements = self.session.execute(
                select(ElementORM).where(ElementORM.document_id == document_id)
            ).scalars().all()

            chunks = self.session.execute(
                select(ChunkORM).where(ChunkORM.document_id == document_id)
            ).scalars().all()

            questions = self.session.execute(
                select(GeneratedQuestionORM).where(
                    GeneratedQuestionORM.document_id == document_id
                )
            ).scalars().all()

            identifiers = self.session.execute(
                select(IdentifierORM).where(IdentifierORM.document_id == document_id)
            ).scalars().all()

            element_ids_by_section = self._group_element_ids_by_section(elements)

            for section_orm in sections:
                graph.add_section(
                    SectionMapper.to_domain(
                        section_orm,
                        element_ids=element_ids_by_section.get(section_orm.id, []),
                    )
                )

            for element_orm in elements:
                graph.add_element(ElementMapper.to_domain(element_orm))

            self._rehydrate_assets(graph)

            for chunk_orm in chunks:
                graph.add_chunk(ChunkMapper.to_domain(chunk_orm))

            for question_orm in questions:
                question = GeneratedQuestionMapper.to_domain(question_orm)
                graph.questions[question.question_id] = question

            for identifier_orm in identifiers:
                identifier = IdentifierMapper.to_domain(identifier_orm)
                graph.identifiers[identifier.identifier_id] = identifier

            chunk_type_counts = dict(
                Counter(str(c.chunk_type) for c in graph.chunks.values())
            )
            graph.document.statistics = DocumentStatistics(
                page_count=graph.document.statistics.page_count,
                element_count=len(graph.elements),
                section_count=len(graph.sections),
                chunk_count=len(graph.chunks),
                table_count=len(graph.tables),
                picture_count=len(graph.pictures),
                identifier_count=len(graph.identifiers),
                chunk_type_counts=chunk_type_counts,
            )

            return graph

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to load document graph.",
                details={"document_id": document_id},
            ) from exc

    def _group_element_ids_by_section(
        self,
        elements: list[ElementORM],
    ) -> dict[str, list[str]]:
        grouped: dict[str, list[str]] = {}

        for element in elements:
            if element.parent_section_id is None:
                continue

            grouped.setdefault(element.parent_section_id, []).append(element.id)

        return grouped

    @staticmethod
    def _rehydrate_assets(graph: DocumentGraph) -> None:
        for element in graph.elements.values():
            parser_metadata = element.parser_metadata
            parser_extra = parser_metadata.extra if parser_metadata is not None else {}

            if element.table_id is not None and element.table_id not in graph.tables:
                graph.tables[element.table_id] = TableAsset(
                    table_id=element.table_id,
                    document_id=element.document_id,
                    parent_section_id=element.parent_section_id,
                    markdown=str(parser_extra.get("markdown") or element.text or ""),
                    rows=parser_extra.get("table_rows") or [],
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
                    metadata=AssetMetadata(
                        source=element.source,
                        caption=(
                            str(parser_extra.get("caption"))
                            if parser_extra.get("caption") is not None
                            else None
                        ),
                        nearby_text=(
                            str(parser_extra.get("nearby_text"))
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
                    ocr_confidence=DocumentGraphReader._coerce_float(
                        parser_extra.get("ocr_confidence")
                    ),
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

    @staticmethod
    def _coerce_float(value: object) -> float | None:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None
