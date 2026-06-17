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
from src.shared.exceptions import DatabaseError

class DocumentWriter:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_document_graph(self, document_graph: DocumentGraph) -> None:
        try:
            self.session.merge(DocumentMapper.to_orm(document_graph.document))

            for section in document_graph.sections.values():
                self.session.merge(SectionMapper.to_orm(section))

            for element in document_graph.elements.values():
                self.session.merge(ElementMapper.to_orm(element))

            for chunk in document_graph.chunks.values():
                self.session.merge(ChunkMapper.to_orm(chunk))

            for question in document_graph.questions.values():
                self.session.merge(GeneratedQuestionMapper.to_orm(question))

            for identifier in document_graph.identifiers.values():
                self.session.merge(IdentifierMapper.to_orm(identifier))

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to save document graph.",
                details={
                    "document_id": document_graph.document.document_id,
                    "section_count": len(document_graph.sections),
                    "element_count": len(document_graph.elements),
                    "chunk_count": len(document_graph.chunks),
                },
            ) from exc
