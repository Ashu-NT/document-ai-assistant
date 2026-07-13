from pathlib import Path

import pytest

from src.application.evaluation.retrieval.benchmarking.corpus.retrieval_benchmark_seed_target_collector import (
    collect_seed_targets,
)
from src.application.evaluation.retrieval.benchmarking.datasets import (
    RetrievalBenchmarkDataset,
)
from src.application.evaluation.retrieval.benchmarking.enums import (
    RetrievalBenchmarkPriority,
    RetrievalBenchmarkQueryType,
    RetrievalBenchmarkRankTarget,
)
from src.application.evaluation.retrieval.benchmarking.models import (
    RetrievalBenchmarkCase,
)
from src.shared.exceptions import SchemaValidationError


def test_collect_seed_targets_filters_to_requested_document_alias(tmp_path: Path) -> None:
    dataset = _build_dataset(
        source_path=tmp_path / "retrieval_truth_set.md",
        cases=[
            _build_case("A-001", "manual_alias", "manual.pdf"),
            _build_case("A-002", "report_alias", "report.pdf"),
        ],
    )
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    (input_directory / "manual.pdf").write_text("manual", encoding="utf-8")
    (input_directory / "report.pdf").write_text("report", encoding="utf-8")

    targets = collect_seed_targets(
        dataset=dataset,
        input_directory=input_directory,
        document_alias="manual_alias",
    )

    assert [target.document_alias for target in targets] == ["manual_alias"]
    assert [target.file_name for target in targets] == ["manual.pdf"]


def test_collect_seed_targets_filters_to_requested_file_name_case_insensitively(
    tmp_path: Path,
) -> None:
    dataset = _build_dataset(
        source_path=tmp_path / "retrieval_truth_set.md",
        cases=[
            _build_case("A-001", "manual_alias", "Manual.PDF"),
            _build_case("A-002", "report_alias", "report.pdf"),
        ],
    )
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    (input_directory / "Manual.PDF").write_text("manual", encoding="utf-8")
    (input_directory / "report.pdf").write_text("report", encoding="utf-8")

    targets = collect_seed_targets(
        dataset=dataset,
        input_directory=input_directory,
        file_name="manual.pdf",
    )

    assert [target.document_alias for target in targets] == ["manual_alias"]
    assert [target.file_name for target in targets] == ["Manual.PDF"]


def test_collect_seed_targets_raises_when_requested_single_target_does_not_exist(
    tmp_path: Path,
) -> None:
    dataset = _build_dataset(
        source_path=tmp_path / "retrieval_truth_set.md",
        cases=[_build_case("A-001", "manual_alias", "manual.pdf")],
    )
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    (input_directory / "manual.pdf").write_text("manual", encoding="utf-8")

    with pytest.raises(SchemaValidationError) as exc_info:
        collect_seed_targets(
            dataset=dataset,
            input_directory=input_directory,
            document_alias="missing_alias",
        )

    assert exc_info.value.details["document_alias"] == "missing_alias"


def _build_dataset(
    *,
    source_path: Path,
    cases: list[RetrievalBenchmarkCase],
) -> RetrievalBenchmarkDataset:
    return RetrievalBenchmarkDataset(
        source_path=source_path,
        cases=cases,
    )


def _build_case(
    case_id: str,
    document_alias: str,
    file_name: str,
) -> RetrievalBenchmarkCase:
    return RetrievalBenchmarkCase(
        case_id=case_id,
        query_text="query",
        query_type=RetrievalBenchmarkQueryType.PROCEDURE_LOOKUP,
        expected_document_alias=document_alias,
        expected_file_name=file_name,
        expected_section_path_text="Section",
        expected_page=1,
        expected_relevant_passage="passage",
        priority=RetrievalBenchmarkPriority.HIGH,
        expected_rank_target=RetrievalBenchmarkRankTarget.TOP_3,
        notes=None,
    )
