import re
from pathlib import Path

import yaml

from src.application.evaluation.ingestion.models.ingestion_expectation_case import (
    ExpectedCrossReference,
    IngestionExpectationCase,
)
from src.application.evaluation.retrieval.benchmarking.loaders.markdown_section_parser import (
    extract_sections,
)
from src.shared.exceptions import SchemaValidationError

DEFAULT_INGESTION_TRUTH_SET_PATH = Path("TestDoc/retrieval_truth_set.md")

# Structural-expectations cases live in their own numbered section of the
# same truth-set file the retrieval benchmark reads (see
# RetrievalTruthSetLoader) -- one file per document holds both, per the
# team's choice to keep one source of truth per document rather than
# splitting retrieval and structural expectations across separate files.
_STRUCTURAL_EXPECTATIONS_SECTION_NUMBER = "7"

# Real YAML (not the retrieval truth-set's flat key:value parser) -- this
# section is new, with no legacy content whose quirky formatting a stricter
# parser could break, so it can support genuine nested lists/mappings
# (expected_cross_references) from the start.
_YAML_BLOCK_PATTERN = re.compile(r"```yaml\s*\n(?P<body>.*?)```", re.DOTALL)


class IngestionTruthSetLoader:
    def load(
        self,
        path: Path | str | None = None,
    ) -> list[IngestionExpectationCase]:
        source_path = self._source_path(path)
        if not source_path.exists():
            raise SchemaValidationError(
                "Ingestion truth-set file not found.",
                details={"path": str(source_path)},
            )

        text = source_path.read_text(encoding="utf-8")
        sections = extract_sections(text)
        body = sections.get(_STRUCTURAL_EXPECTATIONS_SECTION_NUMBER, "")

        cases = [
            self._build_case(
                block_text,
                source_path=source_path,
                block_index=block_index,
            )
            for block_index, block_text in enumerate(
                _YAML_BLOCK_PATTERN.findall(body),
                start=1,
            )
        ]
        cases = [case for case in cases if case is not None]
        if not cases:
            raise SchemaValidationError(
                "Ingestion truth set did not contain any structural expectation cases.",
                details={"path": str(source_path)},
            )
        return cases

    @staticmethod
    def _source_path(path: Path | str | None) -> Path:
        if path is None:
            return DEFAULT_INGESTION_TRUTH_SET_PATH
        return Path(path)

    @staticmethod
    def _build_case(
        block_text: str,
        *,
        source_path: Path,
        block_index: int,
    ) -> IngestionExpectationCase | None:
        try:
            payload = yaml.safe_load(block_text)
        except yaml.YAMLError as exc:
            raise SchemaValidationError(
                "Ingestion truth-set case contains invalid YAML.",
                details={"path": str(source_path), "block_index": block_index},
            ) from exc

        if not isinstance(payload, dict) or not payload.get("id"):
            # Schema-illustration blocks (empty/missing id) are skipped, same
            # convention as the retrieval truth-set's case blocks.
            return None

        if not payload.get("document_path"):
            raise SchemaValidationError(
                "Ingestion truth-set case is missing required field 'document_path'.",
                details={"path": str(source_path), "block_index": block_index},
            )

        cross_references = tuple(
            ExpectedCrossReference(
                clue=entry["clue"],
                expected_reference_type=entry.get("expected_reference_type"),
                expected_target_section=(
                    str(entry["expected_target_section"])
                    if entry.get("expected_target_section") is not None
                    else None
                ),
                expected_target_annex=(
                    str(entry["expected_target_annex"])
                    if entry.get("expected_target_annex") is not None
                    else None
                ),
            )
            for entry in (payload.get("expected_cross_references") or [])
        )

        return IngestionExpectationCase(
            case_id=str(payload["id"]),
            document_path=Path(payload["document_path"]),
            expected_document_type=payload.get("expected_document_type"),
            expected_section_count=payload.get("expected_section_count"),
            expected_top_level_section_titles=tuple(
                payload.get("expected_top_level_section_titles") or []
            ),
            expected_chunk_count=payload.get("expected_chunk_count"),
            expected_chunk_type_counts=dict(
                payload.get("expected_chunk_type_counts") or {}
            ),
            expected_cross_references=cross_references,
            expected_table_count=payload.get("expected_table_count"),
            expected_picture_count=payload.get("expected_picture_count"),
            notes=payload.get("notes"),
        )


__all__ = ["IngestionTruthSetLoader", "DEFAULT_INGESTION_TRUTH_SET_PATH"]
