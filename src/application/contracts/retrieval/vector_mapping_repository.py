from typing import Protocol, TypedDict


class VectorMappingSpec(TypedDict):
    vector_id: str
    document_id: str
    chunk_id: str
    qdrant_collection: str
    qdrant_point_id: str
    embedding_model: str
    embedding_text_hash: str | None


class VectorMappingRepository(Protocol):
    def save_mapping(
        self,
        *,
        vector_id: str,
        document_id: str,
        chunk_id: str,
        qdrant_collection: str,
        qdrant_point_id: str,
        embedding_model: str,
        embedding_text_hash: str | None = None,
    ) -> None:
        ...

    def save_mappings(self, mappings: list[VectorMappingSpec]) -> None:
        ...

    def get_qdrant_point_id(self, chunk_id: str) -> str | None:
        ...

    def list_chunk_ids_by_document(self, document_id: str) -> list[str]:
        ...

    def list_qdrant_point_ids_by_document(self, document_id: str) -> list[str]:
        ...

    def delete_document_mappings(self, document_id: str) -> None:
        ...
