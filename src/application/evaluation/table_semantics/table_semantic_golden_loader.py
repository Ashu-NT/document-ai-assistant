from __future__ import annotations

import re
from pathlib import Path

import yaml

from src.application.evaluation.retrieval.benchmarking.loaders.markdown_section_parser import (
    extract_sections,
)
from src.application.evaluation.table_semantics.human_semantic_status import (
    HumanSemanticStatus,
)
from src.application.evaluation.table_semantics.table_semantic_golden_case import (
    ColumnSemanticGoldenCase,
)
from src.application.evaluation.table_semantics.table_semantic_review_status import (
    TableSemanticReviewStatus,
)
from src.application.workflows.shared.table_column_semantic_role import (
    TableColumnSemanticRole,
)
from src.config.settings import golden_corpus_settings
from src.shared.exceptions import SchemaValidationError

# Same shape-based-discovery / "# N. <title>" + fenced ```yaml``` block
# convention ClassificationExpectationLoader already established -- see
# that loader for the precedent. One YAML block = one reviewed column
# (the atomic review unit), matching the existing one-block-per-case style
# rather than inventing a nested-list schema.
DEFAULT_TABLE_SEMANTIC_EXPECTATIONS_GLOB = "fixtures/table_semantic_expectations*.md"

_YAML_BLOCK_PATTERN = re.compile(r"```yaml\s*\n(?P<body>.*?)```", re.DOTALL)


class TableSemanticGoldenLoader:
    def load(self, path: Path | str | None = None) -> list[ColumnSemanticGoldenCase]:
        source_paths = self._source_paths(path)
        missing = [p for p in source_paths if not p.exists()]
        if missing:
            raise SchemaValidationError(
                "Table semantic golden fixture file not found.",
                details={"path": str(missing[0])},
            )

        cases: list[ColumnSemanticGoldenCase] = []
        for source_path in source_paths:
            cases.extend(self._load_file(source_path))
        return cases

    def _source_paths(self, path: Path | str | None) -> list[Path]:
        if path is not None:
            return [Path(path)]
        root = golden_corpus_settings.root_path
        return sorted(root.glob(DEFAULT_TABLE_SEMANTIC_EXPECTATIONS_GLOB))

    def _load_file(self, source_path: Path) -> list[ColumnSemanticGoldenCase]:
        text = source_path.read_text(encoding="utf-8")
        sections = extract_sections(text)

        cases: list[ColumnSemanticGoldenCase] = []
        for section_body in sections.values():
            for block_text in _YAML_BLOCK_PATTERN.findall(section_body):
                case = self._build_case(block_text, source_path=source_path)
                if case is not None:
                    cases.append(case)
        return cases

    def _build_case(self, block_text: str, *, source_path: Path) -> ColumnSemanticGoldenCase | None:
        data = yaml.safe_load(block_text) or {}
        if not data or data.get("document_title") is None:
            # the blank schema-template block at the top of each file
            return None

        try:
            human_role_raw = data.get("human_role")
            human_role = (
                TableColumnSemanticRole(human_role_raw) if human_role_raw else None
            )
            return ColumnSemanticGoldenCase(
                document_title=str(data["document_title"]),
                table_category=str(data["table_category"]),
                header_substring=(
                    str(data["header_substring"])
                    if data.get("header_substring") is not None
                    else None
                ),
                occurrence_index=int(data.get("occurrence_index", 0)),
                section_path=tuple(data.get("section_path") or ()),
                column_index=int(data["column_index"]),
                source_header=(
                    str(data["source_header"])
                    if data.get("source_header") is not None
                    else None
                ),
                human_status=HumanSemanticStatus(data["human_status"]),
                human_role=human_role,
                human_concept=data.get("human_concept"),
                review_status=TableSemanticReviewStatus(
                    data.get("review_status", "candidate")
                ),
                notes=str(data.get("notes") or ""),
            )
        except (KeyError, ValueError) as exc:
            raise SchemaValidationError(
                "Malformed table semantic golden fixture entry.",
                details={"path": str(source_path), "error": str(exc), "block": block_text},
            ) from exc
