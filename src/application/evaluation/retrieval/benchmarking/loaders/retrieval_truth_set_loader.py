import re
from pathlib import Path

from src.application.evaluation.retrieval.benchmarking.datasets import (
    RetrievalBenchmarkDataset,
    RetrievalBenchmarkSubsetDefinition,
    RetrievalBenchmarkSubsetRow,
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

DEFAULT_RETRIEVAL_TRUTH_SET_PATH = Path("TestDoc/retrieval_truth_set.md")

_HEADER_KEY_PATTERN = re.compile(r"[^a-z0-9]+")
_SECTION_PATTERN = re.compile(
    r"^# (?P<number>\d+)\.[^\n]*\n(?P<body>.*?)(?=^# \d+\.|\Z)",
    re.MULTILINE | re.DOTALL,
)
_YAML_BLOCK_PATTERN = re.compile(
    r"```(?:yaml)?\s*\n(?P<body>.*?)```",
    re.DOTALL,
)


class RetrievalTruthSetLoader:
    def load(
        self,
        path: Path | str | None = None,
    ) -> RetrievalBenchmarkDataset:
        source_path = self._source_path(path)
        if not source_path.exists():
            raise SchemaValidationError(
                "Retrieval truth-set file not found.",
                details={"path": str(source_path)},
            )

        text = source_path.read_text(encoding="utf-8")
        sections = self._extract_sections(text)
        truth_section = sections.get("4")
        if truth_section is None:
            raise SchemaValidationError(
                "Retrieval truth set is missing section 4.",
                details={"path": str(source_path)},
            )

        cases = [
            self._parse_case_block(
                block_text,
                source_path=source_path,
                block_index=block_index,
            )
            for block_index, block_text in enumerate(
                self._extract_yaml_blocks(truth_section),
                start=1,
            )
        ]
        if not cases:
            raise SchemaValidationError(
                "Retrieval truth set did not contain any canonical cases.",
                details={"path": str(source_path)},
            )

        return RetrievalBenchmarkDataset(
            source_path=source_path,
            cases=cases,
            identifier_subset_definition=self._parse_subset_definition(
                sections.get("5"),
                subset_name="identifier-heavy",
                source_path=source_path,
            ),
            semantic_procedure_subset_definition=self._parse_subset_definition(
                sections.get("6"),
                subset_name="semantic-procedure",
                source_path=source_path,
            ),
        )

    @staticmethod
    def _source_path(path: Path | str | None) -> Path:
        if path is None:
            return DEFAULT_RETRIEVAL_TRUTH_SET_PATH
        return Path(path)

    @staticmethod
    def _extract_sections(text: str) -> dict[str, str]:
        return {
            match.group("number"): match.group("body")
            for match in _SECTION_PATTERN.finditer(text)
        }

    @staticmethod
    def _extract_yaml_blocks(section_text: str) -> list[str]:
        return [
            match.group("body").strip()
            for match in _YAML_BLOCK_PATTERN.finditer(section_text)
        ]

    def _parse_case_block(
        self,
        block_text: str,
        *,
        source_path: Path,
        block_index: int,
    ) -> RetrievalBenchmarkCase:
        payload = self._parse_mapping_block(
            block_text,
            source_path=source_path,
            block_index=block_index,
        )
        required_fields = [
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
        missing_fields = [
            field_name
            for field_name in required_fields
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
                expected_section_path_text=self._normalize_scalar(
                    payload["expected_section_path"]
                ),
                expected_page=self._parse_page_number(payload["expected_page"]),
                expected_relevant_passage=self._normalize_scalar(
                    payload["expected_relevant_passage"]
                ),
                priority=RetrievalBenchmarkPriority.from_value(
                    payload["priority"]
                ),
                expected_rank_target=RetrievalBenchmarkRankTarget.from_value(
                    payload["expected_rank"]
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

    def _parse_mapping_block(
        self,
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

            payload[key] = self._normalize_scalar(raw_value)

        return payload

    def _parse_subset_definition(
        self,
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

        headers = self._parse_markdown_row(table_lines[0])
        rows = [
            self._parse_markdown_row(line)
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
                self._normalize_header(header): self._normalize_table_cell(cell)
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

    @staticmethod
    def _parse_markdown_row(line: str) -> list[str]:
        return [
            cell.strip()
            for cell in line.strip().strip("|").split("|")
        ]

    @staticmethod
    def _normalize_header(value: str) -> str:
        normalized = _HEADER_KEY_PATTERN.sub("_", value.lower()).strip("_")
        return normalized or "value"

    @staticmethod
    def _normalize_scalar(value: str) -> str:
        normalized = value.strip().rstrip(",").strip()
        if len(normalized) >= 2 and normalized[0] == normalized[-1] == '"':
            return normalized[1:-1]
        if len(normalized) >= 2 and normalized[0] == normalized[-1] == "'":
            return normalized[1:-1]
        return normalized

    @classmethod
    def _normalize_table_cell(cls, value: str) -> str:
        normalized = cls._normalize_scalar(value)
        if len(normalized) >= 2 and normalized[0] == normalized[-1] == "`":
            return normalized[1:-1]
        if len(normalized) >= 2 and normalized[0] == normalized[-1] == '"':
            return normalized[1:-1]
        return normalized

    @staticmethod
    def _parse_page_number(value: str) -> int:
        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(f"Invalid page number: {value}") from exc
