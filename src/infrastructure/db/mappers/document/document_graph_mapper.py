from src.domain.document import DocumentGraph
from src.infrastructure.db.mappers.document.chunk_mapper import ChunkMapper
from src.infrastructure.db.mappers.document.document_mapper import DocumentMapper
from src.infrastructure.db.mappers.document.element_mapper import ElementMapper
from src.infrastructure.db.mappers.document.identifier_mapper import IdentifierMapper
from src.infrastructure.db.mappers.document.question_mapper import GeneratedQuestionMapper
from src.infrastructure.db.mappers.document.section_mapper import SectionMapper


class DocumentGraphMapper:
    @staticmethod
    def to_orm_parts(graph: DocumentGraph) -> dict[str, list]:
        return {
            "document": [DocumentMapper.to_orm(graph.document)],
            "sections": [
                SectionMapper.to_orm(section)
                for section in graph.sections.values()
            ],
            "elements": [
                ElementMapper.to_orm(element)
                for element in graph.elements.values()
            ],
            "chunks": [
                ChunkMapper.to_orm(chunk)
                for chunk in graph.chunks.values()
            ],
            "questions": [
                GeneratedQuestionMapper.to_orm(question)
                for question in graph.questions.values()
            ],
            "identifiers": [
                IdentifierMapper.to_orm(identifier)
                for identifier in graph.identifiers.values()
            ],
        }