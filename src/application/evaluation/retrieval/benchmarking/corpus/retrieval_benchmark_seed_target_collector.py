from dataclasses import dataclass
from pathlib import Path

from src.application.evaluation.retrieval.benchmarking.datasets import (
    RetrievalBenchmarkDataset,
)
from src.shared.exceptions import SchemaValidationError


@dataclass(slots=True)
class _CorpusSeedTarget:
    document_alias: str
    file_name: str
    file_path: Path


def resolve_input_directory(
    *,
    input_directory: Path | str | None,
    dataset: RetrievalBenchmarkDataset,
) -> Path:
    if input_directory is None:
        return dataset.source_path.parent
    return Path(input_directory)


def collect_seed_targets(
    *,
    dataset: RetrievalBenchmarkDataset,
    input_directory: Path,
) -> list[_CorpusSeedTarget]:
    file_by_alias: dict[str, str] = {}
    alias_by_file: dict[str, str] = {}
    ordered_targets: list[_CorpusSeedTarget] = []

    for case in dataset.canonical_cases:
        alias = case.expected_document_alias
        file_name = case.expected_file_name

        if not alias or not file_name:
            raise SchemaValidationError(
                "Retrieval benchmark case is missing document alias or file name.",
                details={
                    "case_id": case.case_id,
                },
            )

        existing_file_name = file_by_alias.get(alias)
        if existing_file_name is not None and existing_file_name != file_name:
            raise SchemaValidationError(
                "Retrieval benchmark dataset maps one alias to multiple files.",
                details={
                    "document_alias": alias,
                    "first_file_name": existing_file_name,
                    "conflicting_file_name": file_name,
                },
            )

        existing_alias = alias_by_file.get(file_name)
        if existing_alias is not None and existing_alias != alias:
            raise SchemaValidationError(
                "Retrieval benchmark dataset maps one file to multiple aliases.",
                details={
                    "file_name": file_name,
                    "first_alias": existing_alias,
                    "conflicting_alias": alias,
                },
            )

        if alias in file_by_alias:
            continue

        file_path = input_directory / file_name
        if not file_path.exists() or not file_path.is_file():
            raise SchemaValidationError(
                "Retrieval benchmark corpus file not found.",
                details={
                    "document_alias": alias,
                    "file_name": file_name,
                    "input_directory": str(input_directory),
                },
            )

        file_by_alias[alias] = file_name
        alias_by_file[file_name] = alias
        ordered_targets.append(
            _CorpusSeedTarget(
                document_alias=alias,
                file_name=file_name,
                file_path=file_path,
            )
        )

    return ordered_targets
