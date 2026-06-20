from dataclasses import dataclass, field
from pathlib import Path

from src.application.evaluation.retrieval.benchmarking.models.retrieval_benchmark_case import (
    RetrievalBenchmarkCase,
)


@dataclass(slots=True)
class RetrievalBenchmarkSubsetRow:
    entry_id: str
    values: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievalBenchmarkSubsetDefinition:
    name: str
    rows: list[RetrievalBenchmarkSubsetRow] = field(default_factory=list)

    @property
    def row_count(self) -> int:
        return len(self.rows)


@dataclass(slots=True)
class RetrievalBenchmarkDataset:
    source_path: Path
    cases: list[RetrievalBenchmarkCase] = field(default_factory=list)
    identifier_subset_definition: RetrievalBenchmarkSubsetDefinition | None = None
    semantic_procedure_subset_definition: RetrievalBenchmarkSubsetDefinition | None = None

    @property
    def case_count(self) -> int:
        return len(self.cases)

    @property
    def canonical_cases(self) -> list[RetrievalBenchmarkCase]:
        return list(self.cases)

    @property
    def identifier_focused_cases(self) -> list[RetrievalBenchmarkCase]:
        return [
            case
            for case in self.cases
            if case.query_type is not None
            and case.query_type.is_identifier_focused()
        ]

    @property
    def semantic_procedure_cases(self) -> list[RetrievalBenchmarkCase]:
        return [
            case
            for case in self.cases
            if case.query_type is not None
            and case.query_type.is_semantic_procedure_focused()
        ]
