import re
from pathlib import Path

from src.application.evaluation.retrieval.benchmarking.datasets import (
    RetrievalBenchmarkSubsetDefinition,
    RetrievalBenchmarkSubsetRow,
)
from src.application.evaluation.retrieval.benchmarking.loaders.retrieval_benchmark_case_block_parser import (
    normalize_scalar,
)
from src.shared.exceptions import SchemaValidationError

_HEADER_KEY_PATTERN = re.compile(r"[^a-z0-9]+")


def parse_subset_definition(
    section_text: str | None,
    *,
    subset_name: str,
    source_path: Path,
) -> RetrievalBenchmarkSubsetDefinition:
    if section_text is None:
        raise SchemaValidationError(
            "Retrieval truth set is missing a subset section.",
            details={
                "path": str(source_path),
                "subset_name": subset_name,
            },
        )

    table_lines = [
        line.strip()
        for line in section_text.splitlines()
        if line.strip().startswith("|")
    ]
    if len(table_lines) < 2:
        raise SchemaValidationError(
            "Retrieval truth-set subset section is missing a markdown table.",
            details={
                "path": str(source_path),
                "subset_name": subset_name,
            },
        )

    headers = parse_markdown_row(table_lines[0])
    rows = [
        parse_markdown_row(line)
        for line in table_lines[2:]
    ]

    subset_rows: list[RetrievalBenchmarkSubsetRow] = []
    for row_index, row in enumerate(rows, start=1):
        if len(row) != len(headers):
            raise SchemaValidationError(
                "Retrieval truth-set subset table row has the wrong number of cells.",
                details={
                    "path": str(source_path),
                    "subset_name": subset_name,
                    "row_index": row_index,
                },
            )

        mapped_row = {
            normalize_header(header): normalize_table_cell(cell)
            for header, cell in zip(headers, row)
        }
        entry_id = mapped_row.get("id")
        if not entry_id:
            raise SchemaValidationError(
                "Retrieval truth-set subset table row is missing an ID.",
                details={
                    "path": str(source_path),
                    "subset_name": subset_name,
                    "row_index": row_index,
                },
            )

        subset_rows.append(
            RetrievalBenchmarkSubsetRow(
                entry_id=entry_id,
                values=mapped_row,
            )
        )

    return RetrievalBenchmarkSubsetDefinition(
        name=subset_name,
        rows=subset_rows,
    )


def parse_markdown_row(line: str) -> list[str]:
    return [
        cell.strip()
        for cell in line.strip().strip("|").split("|")
    ]


def normalize_header(value: str) -> str:
    normalized = _HEADER_KEY_PATTERN.sub("_", value.lower()).strip("_")
    return normalized or "value"


def normalize_table_cell(value: str) -> str:
    normalized = normalize_scalar(value)
    if len(normalized) >= 2 and normalized[0] == normalized[-1] == "`":
        return normalized[1:-1]
    if len(normalized) >= 2 and normalized[0] == normalized[-1] == '"':
        return normalized[1:-1]
    return normalized
