from typing import Protocol


class DocumentStorage(Protocol):
    def save_file(self, source_path: str, document_id: str) -> str:
        ...

    def get_file_path(self, document_id: str) -> str | None:
        ...

    def delete_file(self, document_id: str) -> None:
        ...