import re
from dataclasses import dataclass, field

from src.application.evaluation.retrieval.benchmarking.enums import (
    RetrievalBenchmarkPriority,
    RetrievalBenchmarkQueryType,
    RetrievalBenchmarkRankTarget,
)
from src.domain.retrieval import RetrievalQuery

_CASE_ID_PATTERN = re.compile(r"[^a-z0-9]+")


@dataclass(slots=True)
class RetrievalBenchmarkCase:
    case_id: str | None = None
    query_text: str | None = None
    query_type: RetrievalBenchmarkQueryType | None = None
    expected_document_alias: str | None = None
    expected_file_name: str | None = None
    expected_section_path_text: str | None = None
    expected_page: int | None = None
    expected_relevant_passage: str | None = None
    priority: RetrievalBenchmarkPriority | None = None
    expected_rank_target: RetrievalBenchmarkRankTarget | None = None
    notes: str | None = None
    query: RetrievalQuery | None = None
    expected_chunk_ids: list[str] = field(default_factory=list)
    expected_section_paths: list[list[str]] = field(default_factory=list)
    description: str | None = None

    def __post_init__(self) -> None:
        if self.query is not None:
            if self.case_id is None:
                self.case_id = self.query.query_id
            if self.query_text is None:
                self.query_text = self.query.query_text

        if self.query is None and self.query_text:
            query_id = self.case_id or self._fallback_query_id(self.query_text)
            self.query = RetrievalQuery(
                query_id=query_id,
                query_text=self.query_text,
            )
            if self.case_id is None:
                self.case_id = query_id

        if self.notes is None and self.description is not None:
            self.notes = self.description
        if self.description is None and self.notes is not None:
            self.description = self.notes

        if self.expected_section_path_text:
            expected_path = self._split_section_path_text(
                self.expected_section_path_text
            )
            if expected_path and expected_path not in self.expected_section_paths:
                self.expected_section_paths.append(expected_path)
        elif self.expected_section_paths:
            self.expected_section_path_text = " > ".join(
                self.expected_section_paths[0]
            )

    @property
    def expected_section_path(self) -> list[str]:
        if self.expected_section_paths:
            return list(self.expected_section_paths[0])
        if self.expected_section_path_text:
            return self._split_section_path_text(
                self.expected_section_path_text
            )
        return []

    @property
    def expected_document_family(self) -> str | None:
        if not self.expected_document_alias:
            return None
        return self.expected_document_alias.split("_", 1)[0]

    @staticmethod
    def _fallback_query_id(query_text: str) -> str:
        normalized = _CASE_ID_PATTERN.sub("_", query_text.lower()).strip("_")
        return normalized or "retrieval_benchmark_case"

    @staticmethod
    def _split_section_path_text(value: str) -> list[str]:
        return [
            segment.strip()
            for segment in value.split(">")
            if segment.strip()
        ]
