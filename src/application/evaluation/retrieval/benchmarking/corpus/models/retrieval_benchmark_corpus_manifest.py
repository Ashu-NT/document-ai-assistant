from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.application.evaluation.retrieval.benchmarking.corpus.models.retrieval_benchmark_corpus_document import (
    RetrievalBenchmarkCorpusDocument,
)


@dataclass(slots=True)
class RetrievalBenchmarkCorpusManifest:
    truth_set_path: Path
    input_directory: Path
    generated_at: str
    documents: list[RetrievalBenchmarkCorpusDocument] = field(default_factory=list)

    @property
    def document_count(self) -> int:
        return len(self.documents)

    @classmethod
    def from_dict(
        cls,
        payload: dict[str, Any],
    ) -> "RetrievalBenchmarkCorpusManifest":
        return cls(
            truth_set_path=Path(payload["truth_set_path"]),
            input_directory=Path(payload["input_directory"]),
            generated_at=str(payload["generated_at"]),
            documents=[
                RetrievalBenchmarkCorpusDocument.from_dict(document_payload)
                for document_payload in payload.get("documents", [])
            ],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "truth_set_path": str(self.truth_set_path),
            "input_directory": str(self.input_directory),
            "generated_at": self.generated_at,
            "document_count": self.document_count,
            "documents": [
                document.to_dict()
                for document in self.documents
            ],
        }
