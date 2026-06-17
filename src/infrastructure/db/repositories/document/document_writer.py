from sqlalchemy.orm import Session

from src.domain.document import DocumentGraph
from src.infrastructure.db.mappers.document.chunk_mapper import ChunkMapper
from src.infrastructure.db.mappers.document.document_mapper import DocumentMapper
from src.infrastructure.db.mappers.document.element_mapper import ElementMapper
from src.infrastructure.db.mappers.document.identifier_mapper import IdentifierMapper
from src.infrastructure.db.mappers.document.question_mapper import GeneratedQuestionMapper
from src.infrastructure.db.mappers.document.section_mapper import SectionMapper


class DocumentWriter:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_document_graph(self, document_graph: DocumentGraph) -> None:
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