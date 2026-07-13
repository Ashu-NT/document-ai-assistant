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
    document_alias: str | None = None,
    file_name: str | None = None,
) -> list[_CorpusSeedTarget]:
    file_by_alias: dict[str, str] = {}
    alias_by_file: dict[str, str] = {}
    ordered_targets: list[_CorpusSeedTarget] = []
    normalized_document_alias = _normalize_optional_filter(document_alias)
    normalized_file_name = _normalize_optional_filter(file_name)

    for case in dataset.canonical_cases:
        alias = case.expected_document_alias
        expected_file_name = case.expected_file_name

        if not _matches_target_filters(
            alias=alias,
            file_name=expected_file_name,
            document_alias_filter=normalized_document_alias,
            file_name_filter=normalized_file_name,
        ):
            continue

        if not alias or not expected_file_name:
            raise SchemaValidationError(
                "Retrieval benchmark case is missing document alias or file name.",
                details={
                    "case_id": case.case_id,
                },
            )

        existing_file_name = file_by_alias.get(alias)
        if (
            existing_file_name is not None
            and existing_file_name != expected_file_name
        ):
            raise SchemaValidationError(
                "Retrieval benchmark dataset maps one alias to multiple files.",
                details={
                    "document_alias": alias,
                    "first_file_name": existing_file_name,
                    "conflicting_file_name": expected_file_name,
                },
            )

        existing_alias = alias_by_file.get(expected_file_name)
        if existing_alias is not None and existing_alias != alias:
            raise SchemaValidationError(
                "Retrieval benchmark dataset maps one file to multiple aliases.",
                details={
                    "file_name": expected_file_name,
                    "first_alias": existing_alias,
                    "conflicting_alias": alias,
                },
            )

        if alias in file_by_alias:
            continue

        file_path = input_directory / expected_file_name
        if not file_path.exists() or not file_path.is_file():
            raise SchemaValidationError(
                "Retrieval benchmark corpus file not found.",
                details={
                    "document_alias": alias,
                    "file_name": expected_file_name,
                    "input_directory": str(input_directory),
                },
            )

        file_by_alias[alias] = expected_file_name
        alias_by_file[expected_file_name] = alias
        ordered_targets.append(
            _CorpusSeedTarget(
                document_alias=alias,
                file_name=expected_file_name,
                file_path=file_path,
            )
        )

    if ordered_targets:
        return ordered_targets

    if normalized_document_alias is not None or normalized_file_name is not None:
        raise SchemaValidationError(
            "No retrieval benchmark corpus seed target matched the requested filter.",
            details={
                "document_alias": normalized_document_alias,
                "file_name": normalized_file_name,
                "input_directory": str(input_directory),
            },
        )

    return ordered_targets


def _matches_target_filters(
    *,
    alias: str | None,
    file_name: str | None,
    document_alias_filter: str | None,
    file_name_filter: str | None,
) -> bool:
    normalized_alias = _normalize_optional_filter(alias)
    normalized_file_name = _normalize_optional_filter(file_name)
    if (
        document_alias_filter is not None
        and normalized_alias != document_alias_filter
    ):
        return False
    if file_name_filter is not None and normalized_file_name != file_name_filter:
        return False
    return True


def _normalize_optional_filter(value: str | None) -> str | None:
    text = str(value or "").strip()
    return text.casefold() if text else None
