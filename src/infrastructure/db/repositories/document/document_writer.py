from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.document import DocumentGraph
from src.domain.document.entities.chunk_cross_reference import ChunkCrossReference
from src.domain.document.entities.identifier import Identifier
from src.infrastructure.db.mappers import (
    ChunkCrossReferenceMapper,
    ChunkMapper,
    CrossReferenceEvidenceMapper,
    DocumentMapper,
    ElementMapper,
    GeneratedQuestionMapper,
    IdentifierMapper,
    SectionMapper,
)
from src.infrastructure.db.repositories.common import bulk_merge
from src.infrastructure.db.orm_models import (
    ChunkCrossReferenceORM,
    ChunkORM,
    CrossReferenceEvidenceORM,
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
                    "cross_reference_count": len(document_graph.cross_references),
                },
            ) from exc

    def _merge_document_graph(self, document_graph: DocumentGraph) -> None:
        self._merge_document_structure(document_graph)
        self._merge_chunk_artifacts(document_graph)

    def _merge_document_structure(self, document_graph: DocumentGraph) -> None:
        # Explicit flush()es between stages: none of documents/sections/
        # elements/chunks have an ORM relationship() declared toward each
        # other (only plain FK columns), so SQLAlchemy's automatic
        # flush-time insert ordering cannot topologically sort them within
        # a single flush -- it silently attempted to INSERT chunks before
        # their parent document/section existed once FK enforcement was
        # actually turned on (PRAGMA foreign_keys=ON), which no test caught
        # because the test engine never enabled that pragma either.
        self.session.merge(DocumentMapper.to_orm(document_graph.document))
        self.session.flush()

        bulk_merge(
            self.session,
            SectionORM,
            [SectionMapper.to_orm(section) for section in document_graph.sections.values()],
        )
        self.session.flush()

        bulk_merge(
            self.session,
            ElementORM,
            [ElementMapper.to_orm(element) for element in document_graph.elements.values()],
        )
        self.session.flush()

    def _merge_chunk_artifacts(self, document_graph: DocumentGraph) -> None:
        bulk_merge(
            self.session,
            ChunkORM,
            [ChunkMapper.to_orm(chunk) for chunk in document_graph.chunks.values()],
        )
        self.session.flush()

        bulk_merge(
            self.session,
            GeneratedQuestionORM,
            [
                GeneratedQuestionMapper.to_orm(question)
                for question in document_graph.questions.values()
            ],
        )
        bulk_merge(
            self.session,
            IdentifierORM,
            [
                IdentifierMapper.to_orm(identifier)
                for identifier in document_graph.identifiers.values()
            ],
        )
        bulk_merge(
            self.session,
            ChunkCrossReferenceORM,
            [
                ChunkCrossReferenceMapper.to_orm(cross_reference)
                for cross_reference in document_graph.cross_references.values()
            ],
        )
        self.session.flush()

        bulk_merge(
            self.session,
            CrossReferenceEvidenceORM,
            [
                CrossReferenceEvidenceMapper.to_orm(evidence)
                for evidence in document_graph.cross_reference_evidence.values()
            ],
        )

    def _delete_document_chunk_artifacts(self, document_id: str) -> None:
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
        # Evidence is append-only *within* a document's lifecycle, not
        # forever - a reingest deletes and reinserts it same as the
        # canonical cross-references it backs. Deleted before the canonical
        # rows so no ON DELETE SET NULL churn happens for rows being removed
        # anyway.
        self.session.execute(
            delete(CrossReferenceEvidenceORM).where(
                CrossReferenceEvidenceORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(ChunkCrossReferenceORM).where(
                ChunkCrossReferenceORM.document_id == document_id
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
            bulk_merge(
                self.session,
                IdentifierORM,
                [IdentifierMapper.to_orm(identifier) for identifier in identifiers],
            )
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to write identifiers.",
                details={"identifier_count": len(identifiers)},
            ) from exc

    def replace_chunk_cross_references(
        self,
        *,
        document_id: str,
        cross_references: list[ChunkCrossReference],
    ) -> None:
        try:
            self.session.execute(
                delete(ChunkCrossReferenceORM).where(
                    ChunkCrossReferenceORM.document_id == document_id
                )
            )
            bulk_merge(
                self.session,
                ChunkCrossReferenceORM,
                [
                    ChunkCrossReferenceMapper.to_orm(cross_reference)
                    for cross_reference in cross_references
                ],
            )
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to replace chunk cross references.",
                details={
                    "document_id": document_id,
                    "cross_reference_count": len(cross_references),
                },
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
