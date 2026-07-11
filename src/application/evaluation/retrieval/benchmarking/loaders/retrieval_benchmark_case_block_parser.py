import re
from pathlib import Path

from src.application.evaluation.retrieval.benchmarking.enums import (
    RetrievalBenchmarkPriority,
    RetrievalBenchmarkQueryType,
    RetrievalBenchmarkRankTarget,
)
from src.application.evaluation.retrieval.benchmarking.models import (
    RetrievalBenchmarkCase,
)
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.shared.exceptions import SchemaValidationError

_YAML_BLOCK_PATTERN = re.compile(
    r"```(?:yaml)?\s*\n(?P<body>.*?)```",
    re.DOTALL,
)

_REQUIRED_CASE_FIELDS = [
    "id",
    "query",
    "query_type",
    "expected_document_id",
    "expected_file",
    "expected_section_path",
    "expected_page",
    "expected_relevant_passage",
    "priority",
    "expected_rank",
]


def extract_yaml_blocks(section_text: str) -> list[str]:
    return [
        match.group("body").strip()
        for match in _YAML_BLOCK_PATTERN.finditer(section_text)
    ]


def looks_like_case_block(block_text: str) -> bool:
    """True if the YAML block has a non-empty `id` value — distinguishes
    real case blocks from schema template blocks (which have empty `id:`)."""
    for line in block_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("id:"):
            value = stripped[3:].strip().strip('"').strip("'")
            return bool(value)
    return False


def parse_case_block(
    block_text: str,
    *,
    source_path: Path,
    block_index: int,
) -> RetrievalBenchmarkCase:
    payload = parse_mapping_block(
        block_text,
        source_path=source_path,
        block_index=block_index,
    )
    missing_fields = [
        field_name
        for field_name in _REQUIRED_CASE_FIELDS
        if not payload.get(field_name)
    ]
    if missing_fields:
        raise SchemaValidationError(
            "Retrieval truth-set case is missing required fields.",
            details={
                "path": str(source_path),
                "block_index": block_index,
                "missing_fields": missing_fields,
            },
        )

    try:
        return RetrievalBenchmarkCase(
            case_id=payload["id"],
            query_text=payload["query"],
            query_type=RetrievalBenchmarkQueryType.from_value(
                payload["query_type"]
            ),
            expected_document_alias=payload["expected_document_id"],
            expected_file_name=payload["expected_file"],
            expected_section_path_text=normalize_scalar(
                payload["expected_section_path"]
            ),
            expected_page=parse_page_number(payload["expected_page"]),
            expected_relevant_passage=normalize_scalar(
                payload["expected_relevant_passage"]
            ),
            priority=RetrievalBenchmarkPriority.from_value(
                payload["priority"]
            ),
            expected_rank_target=RetrievalBenchmarkRankTarget.from_value(
                payload["expected_rank"]
            ),
            expected_intent=(
                RetrievalQueryIntent(payload["expected_intent"])
                if payload.get("expected_intent")
                else None
            ),
            notes=payload.get("notes"),
        )
    except ValueError as exc:
        raise SchemaValidationError(
            "Retrieval truth-set case contains unsupported enum values.",
            details={
                "path": str(source_path),
                "block_index": block_index,
                "payload": payload,
            },
        ) from exc


def parse_mapping_block(
    block_text: str,
    *,
    source_path: Path,
    block_index: int,
) -> dict[str, str]:
    payload: dict[str, str] = {}

    for line_number, raw_line in enumerate(
        block_text.splitlines(),
        start=1,
    ):
        line = raw_line.strip()
        if not line:
            continue
        if ":" not in line:
            raise SchemaValidationError(
                "Retrieval truth-set case contains a malformed line.",
                details={
                    "path": str(source_path),
                    "block_index": block_index,
                    "line_number": line_number,
                    "line": raw_line,
                },
            )

        raw_key, raw_value = line.split(":", 1)
        key = raw_key.strip()
        if key in payload:
            raise SchemaValidationError(
                "Retrieval truth-set case contains a duplicate key.",
                details={
                    "path": str(source_path),
                    "block_index": block_index,
                    "key": key,
                },
            )

        payload[key] = normalize_scalar(raw_value)

    return payload


def normalize_scalar(value: str) -> str:
    normalized = value.strip().rstrip(",").strip()
    if len(normalized) >= 2 and normalized[0] == normalized[-1] == '"':
        return normalized[1:-1]
    if len(normalized) >= 2 and normalized[0] == normalized[-1] == "'":
        return normalized[1:-1]
    return normalized


def parse_page_number(value: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid page number: {value}") from exc
