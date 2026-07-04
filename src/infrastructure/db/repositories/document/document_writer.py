from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.document import DocumentGraph
from src.domain.document.entities.identifier import Identifier
from src.infrastructure.db.mappers import (
    ChunkMapper,
    DocumentMapper,
    ElementMapper,
    GeneratedQuestionMapper,
    IdentifierMapper,
    SectionMapper,
)
from src.infrastructure.db.orm_models import (
    ChunkORM,
    ChunkClassificationORM,
    DocumentORM,
    GeneratedQuestionORM,
    IdentifierORM,
    ElementORM,
    SectionORM,
)
from src.shared.exceptions import DatabaseError


class DocumentWriter:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_document_graph(self, document_graph: DocumentGraph) -> None:
        try:
            self._merge_document_graph(document_graph)
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

    def replace_document_graph(self, document_graph: DocumentGraph) -> None:
        try:
            document_id = document_graph.document.document_id
            self.session.merge(DocumentMapper.to_orm(document_graph.document))
            self._delete_document_chunk_artifacts(document_id)
            self._delete_document_structure(document_id)
            self._merge_document_graph(document_graph)
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to replace document graph.",
                details={
                    "document_id": document_graph.document.document_id,
                    "section_count": len(document_graph.sections),
                    "element_count": len(document_graph.elements),
                    "chunk_count": len(document_graph.chunks),
                },
            ) from exc

    def replace_document_chunk_artifacts(self, document_graph: DocumentGraph) -> None:
        try:
            self._merge_document_structure(document_graph)
            self._delete_document_chunk_artifacts(
                document_graph.document.document_id
            )
            self._merge_chunk_artifacts(document_graph)
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to replace document chunk artifacts.",
                details={
                    "document_id": document_graph.document.document_id,
                    "chunk_count": len(document_graph.chunks),
                    "question_count": len(document_graph.questions),
                    "identifier_count": len(document_graph.identifiers),
                },
            ) from exc

    def _merge_document_graph(self, document_graph: DocumentGraph) -> None:
        self._merge_document_structure(document_graph)
        self._merge_chunk_artifacts(document_graph)

    def _merge_document_structure(self, document_graph: DocumentGraph) -> None:
        self.session.merge(DocumentMapper.to_orm(document_graph.document))

        for section in document_graph.sections.values():
            self.session.merge(SectionMapper.to_orm(section))

        for element in document_graph.elements.values():
            self.session.merge(ElementMapper.to_orm(element))

    def _merge_chunk_artifacts(self, document_graph: DocumentGraph) -> None:
        for chunk in document_graph.chunks.values():
            self.session.merge(ChunkMapper.to_orm(chunk))

        for question in document_graph.questions.values():
            self.session.merge(GeneratedQuestionMapper.to_orm(question))

        for identifier in document_graph.identifiers.values():
            self.session.merge(IdentifierMapper.to_orm(identifier))

    def _delete_document_chunk_artifacts(self, document_id: str) -> None:
        self.session.execute(
            delete(ChunkClassificationORM).where(
                ChunkClassificationORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(GeneratedQuestionORM).where(
                GeneratedQuestionORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(IdentifierORM).where(
                IdentifierORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(ChunkORM).where(
                ChunkORM.document_id == document_id
            )
        )

    def delete_document(self, document_id: str) -> None:
        """Delete a document and every row that depends on it.

        Covers structure (sections/elements), chunk artifacts (chunks,
        chunk classifications, generated questions, identifiers), and the
        document row itself. Extraction-family rows and vector mappings are
        owned by their own writers and are not touched here.
        """
        try:
            self._delete_document_chunk_artifacts(document_id)
            self._delete_document_structure(document_id)
            self.session.execute(
                delete(DocumentORM).where(DocumentORM.id == document_id)
            )
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to delete document.",
                details={"document_id": document_id},
            ) from exc

    def write_identifiers(self, identifiers: list[Identifier]) -> None:
        try:
            for identifier in identifiers:
                self.session.merge(IdentifierMapper.to_orm(identifier))
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to write identifiers.",
                details={"identifier_count": len(identifiers)},
            ) from exc

    def _delete_document_structure(self, document_id: str) -> None:
        self.session.execute(
            delete(ElementORM).where(
                ElementORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(SectionORM).where(
                SectionORM.document_id == document_id
            )
        )
