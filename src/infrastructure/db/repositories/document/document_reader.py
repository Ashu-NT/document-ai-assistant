from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.document import DocumentGraph
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