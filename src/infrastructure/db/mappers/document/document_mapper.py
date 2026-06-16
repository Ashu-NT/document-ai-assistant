from src.domain.common import DocumentType
from src.domain.document.entities import Document
from src.domain.document.value_objects import DocumentHashes, DocumentStatistics
from src.infrastructure.db.orm_models import DocumentORM


class DocumentMapper:
    @staticmethod
    def to_orm(document: Document) -> DocumentORM:
        return DocumentORM(
            id=document.document_id,
            file_name=document.file_name,
            file_path=document.file_path,
            file_hash=document.hashes.file_hash,
            content_hash=document.hashes.content_hash,
            title=document.title,
            document_type=document.document_type.value,
            language=document.language,
            page_count=document.statistics.page_count,
            created_at=document.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: DocumentORM) -> Document:
        return Document(
            document_id=orm.id,
            file_name=orm.file_name,
            file_path=orm.file_path,
            hashes=DocumentHashes(
                file_hash=orm.file_hash,
                content_hash=orm.content_hash,
            ),
            title=orm.title,
            document_type=DocumentType(orm.document_type),
            language=orm.language,
            statistics=DocumentStatistics(
                page_count=orm.page_count,
            ),
        )