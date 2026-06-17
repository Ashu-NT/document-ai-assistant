from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.db.orm_models import DocumentORM


class DocumentDuplicateChecker:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_document_id_by_file_hash(self, file_hash: str) -> str | None:
        statement = select(DocumentORM.id).where(
            DocumentORM.file_hash == file_hash,
        )

        return self.session.execute(statement).scalar_one_or_none()

    def find_document_id_by_content_hash(self, content_hash: str) -> str | None:
        statement = select(DocumentORM.id).where(
            DocumentORM.content_hash == content_hash,
        )

        return self.session.execute(statement).scalar_one_or_none()