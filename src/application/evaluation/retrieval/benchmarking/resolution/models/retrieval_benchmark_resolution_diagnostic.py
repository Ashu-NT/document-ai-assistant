from dataclasses import dataclass, field
from typing import Any

from src.application.evaluation.retrieval.benchmarking.resolution.models.retrieval_benchmark_resolution_candidate import (
    RetrievalBenchmarkResolutionCandidate,
)


@dataclass(slots=True)
class RetrievalBenchmarkResolutionDiagnostic:
    case_id: str | None
    document_alias: str | None
    file_name: str | None
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    candidate_summaries: list[RetrievalBenchmarkResolutionCandidate] = field(
        default_factory=list
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "document_alias": self.document_alias,
            "file_name": self.file_name,
            "message": self.message,
            "details": dict(self.details),
            "candidate_summaries": [
                candidate.to_dict()
                for candidate in self.candidate_summaries
            ],
        }
