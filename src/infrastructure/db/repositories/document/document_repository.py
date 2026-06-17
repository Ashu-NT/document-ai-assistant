from sqlalchemy.orm import Session

from src.application.contracts.document import DocumentRepository
from src.domain.document import DocumentGraph
from src.domain.document.entities import DocumentChunk, Identifier
from src.infrastructure.db.repositories.document.chunk_reader import ChunkReader
from src.infrastructure.db.repositories.document.document_duplicate_checker import (
    DocumentDuplicateChecker,
)
from src.infrastructure.db.repositories.document.document_reader import DocumentReader
from src.infrastructure.db.repositories.document.document_writer import DocumentWriter
from src.infrastructure.db.repositories.document.identifier_reader import IdentifierReader


class SqlAlchemyDocumentRepository(DocumentRepository):
    """
    Facade repository implementing the application contract.

    Internally delegates to smaller focused classes so this file does not
    become a dump file.
    """

    def __init__(self, session: Session) -> None:
        self.duplicate_checker = DocumentDuplicateChecker(session)
        self.reader = DocumentReader(session)
        self.writer = DocumentWriter(session)
        self.chunk_reader = ChunkReader(session)
        self.identifier_reader = IdentifierReader(session)

    def find_document_id_by_file_hash(self, file_hash: str) -> str | None:
        return self.duplicate_checker.find_document_id_by_file_hash(file_hash)

    def find_document_id_by_content_hash(self, content_hash: str) -> str | None:
        return self.duplicate_checker.find_document_id_by_content_hash(content_hash)

    def save_document_graph(self, document_graph: DocumentGraph) -> None:
        self.writer.save_document_graph(document_graph)

    def get_document_graph(self, document_id: str) -> DocumentGraph | None:
        return self.reader.get_document_graph(document_id)

    def list_chunks_by_document(self, document_id: str) -> list[DocumentChunk]:
        return self.chunk_reader.list_chunks_by_document(document_id)

    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[DocumentChunk]:
        return self.chunk_reader.get_chunks_by_ids(chunk_ids)

    def search_identifiers(self, value: str) -> list[Identifier]:
        return self.identifier_reader.search_identifiers(value)