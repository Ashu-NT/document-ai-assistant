from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RetrievalBenchmarkCorpusDocument:
    document_alias: str
    document_id: str
    file_name: str
    file_path: Path
    file_hash: str
    content_hash: str | None
    document_type: str
    page_count: int | None
    section_count: int
    element_count: int
    chunk_count: int
    question_count: int
    classification_label: str | None = None
    classification_confidence: float | None = None
    embedding_model: str | None = None
    vector_collection: str | None = None
    seed_status: str = "seeded_new"

    @classmethod
    def from_dict(
        cls,
        payload: dict[str, Any],
    ) -> "RetrievalBenchmarkCorpusDocument":
        return cls(
            document_alias=str(payload["document_alias"]),
            document_id=str(payload["document_id"]),
            file_name=str(payload["file_name"]),
            file_path=Path(payload["file_path"]),
            file_hash=str(payload["file_hash"]),
            content_hash=payload.get("content_hash"),
            document_type=str(payload["document_type"]),
            page_count=payload.get("page_count"),
            section_count=int(payload["section_count"]),
            element_count=int(payload["element_count"]),
            chunk_count=int(payload["chunk_count"]),
            question_count=int(payload["question_count"]),
            classification_label=payload.get("classification_label"),
            classification_confidence=payload.get("classification_confidence"),
            embedding_model=payload.get("embedding_model"),
            vector_collection=payload.get("vector_collection"),
            seed_status=str(payload.get("seed_status", "seeded_new")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_alias": self.document_alias,
            "document_id": self.document_id,
            "file_name": self.file_name,
            "file_path": str(self.file_path),
            "file_hash": self.file_hash,
            "content_hash": self.content_hash,
            "document_type": self.document_type,
            "page_count": self.page_count,
            "section_count": self.section_count,
            "element_count": self.element_count,
            "chunk_count": self.chunk_count,
            "question_count": self.question_count,
            "classification_label": self.classification_label,
            "classification_confidence": self.classification_confidence,
            "embedding_model": self.embedding_model,
            "vector_collection": self.vector_collection,
            "seed_status": self.seed_status,
        }
