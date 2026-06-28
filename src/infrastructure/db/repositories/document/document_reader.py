from collections import Counter

from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.application.contracts.document import DocumentCatalogEntry
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

class DocumentReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_document_entries(self) -> list[DocumentCatalogEntry]:
        try:
            rows = self.session.execute(
                self._document_entry_statement().order_by(DocumentORM.created_at.desc())
            ).all()
            return [self._to_catalog_entry(row) for row in rows]
        except SQLAlchemyError as exc:
            raise DatabaseError("Failed to list documents.") from exc

    def find_document_entries(self, query_text: str) -> list[DocumentCatalogEntry]:
        try:
            normalized = query_text.strip()
            if not normalized:
                return []

            pattern = f"%{normalized}%"
            rows = self.session.execute(
                self._document_entry_statement()
                .where(
                    or_(
                        DocumentORM.title.ilike(pattern),
                        DocumentORM.file_name.ilike(pattern),
                    )
                )
                .order_by(DocumentORM.created_at.desc())
            ).all()
            return [self._to_catalog_entry(row) for row in rows]
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to search documents.",
                details={"query_text": query_text},
            ) from exc

    def get_document_entry(self, document_id: str) -> DocumentCatalogEntry | None:
        try:
            row = self.session.execute(
                self._document_entry_statement().where(DocumentORM.id == document_id)
            ).one_or_none()
            if row is None:
                return None
            return self._to_catalog_entry(row)
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to load document entry.",
                details={"document_id": document_id},
            ) from exc

    def get_latest_document_entry(self) -> DocumentCatalogEntry | None:
        try:
            row = self.session.execute(
                self._document_entry_statement()
                .order_by(DocumentORM.created_at.desc())
                .limit(1)
            ).one_or_none()
            if row is None:
                return None
            return self._to_catalog_entry(row)
        except SQLAlchemyError as exc:
            raise DatabaseError("Failed to load latest document.") from exc

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
            table_count = len(
                {
                    element.table_id
                    for element in graph.elements.values()
                    if getattr(element, "table_id", None)
                }
            )
            picture_count = len(
                {
                    element.picture_id
                    for element in graph.elements.values()
                    if getattr(element, "picture_id", None)
                }
            )
            graph.document.statistics = DocumentStatistics(
                page_count=graph.document.statistics.page_count,
                element_count=len(graph.elements),
                section_count=len(graph.sections),
                chunk_count=len(graph.chunks),
                table_count=table_count,
                picture_count=picture_count,
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
    def _document_entry_statement():
        chunk_count = (
            select(func.count(ChunkORM.id))
            .where(ChunkORM.document_id == DocumentORM.id)
            .correlate(DocumentORM)
            .scalar_subquery()
        )
        section_count = (
            select(func.count(SectionORM.id))
            .where(SectionORM.document_id == DocumentORM.id)
            .correlate(DocumentORM)
            .scalar_subquery()
        )
        identifier_count = (
            select(func.count(IdentifierORM.id))
            .where(IdentifierORM.document_id == DocumentORM.id)
            .correlate(DocumentORM)
            .scalar_subquery()
        )
        table_count = (
            select(func.count(func.distinct(ElementORM.table_id)))
            .where(
                ElementORM.document_id == DocumentORM.id,
                ElementORM.table_id.is_not(None),
            )
            .correlate(DocumentORM)
            .scalar_subquery()
        )
        picture_count = (
            select(func.count(func.distinct(ElementORM.picture_id)))
            .where(
                ElementORM.document_id == DocumentORM.id,
                ElementORM.picture_id.is_not(None),
            )
            .correlate(DocumentORM)
            .scalar_subquery()
        )
        return select(
            DocumentORM,
            chunk_count.label("chunk_count"),
            section_count.label("section_count"),
            identifier_count.label("identifier_count"),
            table_count.label("table_count"),
            picture_count.label("picture_count"),
        )

    @staticmethod
    def _to_catalog_entry(row) -> DocumentCatalogEntry:
        document_orm = row[0]
        return DocumentCatalogEntry(
            document_id=document_orm.id,
            title=document_orm.title,
            file_name=document_orm.file_name,
            file_path=document_orm.file_path,
            document_type=document_orm.document_type,
            language=document_orm.language,
            page_count=document_orm.page_count,
            chunk_count=int(getattr(row, "chunk_count", 0) or 0),
            section_count=int(getattr(row, "section_count", 0) or 0),
            identifier_count=int(getattr(row, "identifier_count", 0) or 0),
            table_count=int(getattr(row, "table_count", 0) or 0),
            picture_count=int(getattr(row, "picture_count", 0) or 0),
            created_at=document_orm.created_at,
        )
