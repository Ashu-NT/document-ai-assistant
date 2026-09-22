import re
from pathlib import Path

import yaml

from src.application.evaluation.corpus.golden_corpus_manifest import (
    GoldenCorpusManifest,
)
from src.application.evaluation.ingestion.models.ingestion_expectation_case import (
    ExpectedCrossReference,
    IngestionExpectationCase,
)
from src.application.evaluation.retrieval.benchmarking.loaders.markdown_section_parser import (
    extract_sections,
)
from src.config.settings import golden_corpus_settings
from src.shared.exceptions import SchemaValidationError

# Structural-expectations cases live in their own dedicated file(s), one per
# reviewed document (e.g. structural_expectations_fwc12.md), NOT inside
# TestDoc/retrieval_truth_set.md - that file stays retrieval-focused (see
# approved decision "retrieval_truth_set.md remains retrieval-focused").
# Discovered via glob rather than one hardcoded filename so new documents'
# structural expectations can be added as new files without touching this
# loader.
DEFAULT_INGESTION_TRUTH_SET_GLOB = "fixtures/structural_expectations*.md"

# Real YAML (not the retrieval truth-set's flat key:value parser) so nested
# structures (expected_cross_references) are supported without a bespoke
# parser.
_YAML_BLOCK_PATTERN = re.compile(r"```yaml\s*\n(?P<body>.*?)```", re.DOTALL)


class IngestionTruthSetLoader:
    """Discovers structural-expectation cases by content shape (any ```yaml
    block with a non-empty `id:`), scanning EVERY numbered Markdown section
    of the source file(s) - never a hardcoded section number. A prior
    version hardcoded section "7", which silently stopped finding any case
    the moment that file's section numbering changed (see the fixed
    regression this loader now has a dedicated test for). Mirrors the same
    shape-based discovery RetrievalTruthSetLoader already uses.
    """

    def __init__(self, *, manifest: GoldenCorpusManifest | None = None) -> None:
        self._manifest = manifest or GoldenCorpusManifest.default()

    def load(
        self,
        path: Path | str | None = None,
    ) -> list[IngestionExpectationCase]:
        source_paths = self._source_paths(path)
        missing = [p for p in source_paths if not p.exists()]
        if missing:
            raise SchemaValidationError(
                "Ingestion truth-set file not found.",
                details={"path": str(missing[0])},
            )

        cases: list[IngestionExpectationCase] = []
        for source_path in source_paths:
            cases.extend(self._load_file(source_path))

        if not cases:
            raise SchemaValidationError(
                "Ingestion truth set did not contain any structural expectation cases.",
                details={"paths": [str(p) for p in source_paths]},
            )
        return cases

    def _load_file(self, source_path: Path) -> list[IngestionExpectationCase]:
        text = source_path.read_text(encoding="utf-8")
        sections = extract_sections(text)

        cases: list[IngestionExpectationCase] = []
        block_index = 0
        for section_body in sections.values():
            for block_text in _YAML_BLOCK_PATTERN.findall(section_body):
                block_index += 1
                case = self._build_case(
                    block_text,
                    source_path=source_path,
                    block_index=block_index,
                )
                if case is not None:
                    cases.append(case)
        return cases

    def _source_paths(self, path: Path | str | None) -> list[Path]:
        if path is not None:
            return [Path(path)]

        root = golden_corpus_settings.root_path
        return sorted(root.glob(DEFAULT_INGESTION_TRUTH_SET_GLOB))

    def _build_case(
        self,
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

        document_path, document_alias = self._resolve_document_path(
            payload, source_path=source_path, block_index=block_index
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
            document_path=document_path,
            document_alias=document_alias,
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
            expected_element_count_min=payload.get("expected_element_count_min"),
            expected_element_count_max=payload.get("expected_element_count_max"),
            expected_chunk_count_min=payload.get("expected_chunk_count_min"),
            expected_chunk_count_max=payload.get("expected_chunk_count_max"),
            expected_table_count_min=payload.get("expected_table_count_min"),
            expected_table_count_max=payload.get("expected_table_count_max"),
            expected_picture_count_min=payload.get("expected_picture_count_min"),
            expected_picture_count_max=payload.get("expected_picture_count_max"),
            required_text_clues=tuple(payload.get("required_text_clues") or []),
            exhaustive_cross_reference_types=tuple(
                payload.get("exhaustive_cross_reference_types") or []
            ),
            notes=payload.get("notes"),
        )

    def _resolve_document_path(
        self,
        payload: dict,
        *,
        source_path: Path,
        block_index: int,
    ) -> tuple[Path, str | None]:
        literal_path = payload.get("document_path")
        alias = payload.get("document_alias")

        if not literal_path and not alias:
            raise SchemaValidationError(
                "Ingestion truth-set case is missing required field "
                "'document_path' or 'document_alias'.",
                details={"path": str(source_path), "block_index": block_index},
            )

        if literal_path:
            return Path(literal_path), (str(alias) if alias else None)

        resolved_entry = self._manifest.entry(str(alias))
        return (
            self._manifest.root_dir / resolved_entry.relative_path,
            str(alias),
        )


__all__ = ["IngestionTruthSetLoader", "DEFAULT_INGESTION_TRUTH_SET_GLOB"]
