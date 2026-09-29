import re
from pathlib import Path

import yaml

from src.application.evaluation.classification.classification_expectation_case import (
    ClassificationExpectationCase,
)
from src.application.evaluation.classification.classification_review_status import (
    ClassificationReviewStatus,
)
from src.application.evaluation.corpus.golden_corpus_manifest import (
    GoldenCorpusManifest,
)
from src.application.evaluation.retrieval.benchmarking.loaders.markdown_section_parser import (
    extract_sections,
)
from src.config.settings import golden_corpus_settings
from src.domain.common import DocumentType
from src.shared.exceptions import SchemaValidationError

# Same shape-based-discovery convention Phase 1 established for structural
# expectations (see IngestionTruthSetLoader) - discovered via glob, never a
# hardcoded filename or section number, so new documents' classification
# expectations can be added as new files without touching this loader.
DEFAULT_CLASSIFICATION_EXPECTATIONS_GLOB = "fixtures/classification_expectations*.md"

_YAML_BLOCK_PATTERN = re.compile(r"```yaml\s*\n(?P<body>.*?)```", re.DOTALL)


class ClassificationExpectationLoader:
    def __init__(self, *, manifest: GoldenCorpusManifest | None = None) -> None:
        self._manifest = manifest or GoldenCorpusManifest.default()

    def load(
        self,
        path: Path | str | None = None,
    ) -> list[ClassificationExpectationCase]:
        source_paths = self._source_paths(path)
        missing = [p for p in source_paths if not p.exists()]
        if missing:
            raise SchemaValidationError(
                "Classification expectation file not found.",
                details={"path": str(missing[0])},
            )

        cases: list[ClassificationExpectationCase] = []
        for source_path in source_paths:
            cases.extend(self._load_file(source_path))

        self._reject_duplicate_aliases(cases)
        return cases

    def _load_file(self, source_path: Path) -> list[ClassificationExpectationCase]:
        text = source_path.read_text(encoding="utf-8")
        sections = extract_sections(text)

        cases: list[ClassificationExpectationCase] = []
        block_index = 0
        for section_body in sections.values():
            for block_text in _YAML_BLOCK_PATTERN.findall(section_body):
                block_index += 1
                case = self._build_case(
                    block_text, source_path=source_path, block_index=block_index
                )
                if case is not None:
                    cases.append(case)
        return cases

    def _source_paths(self, path: Path | str | None) -> list[Path]:
        if path is not None:
            return [Path(path)]

        root = golden_corpus_settings.root_path
        return sorted(root.glob(DEFAULT_CLASSIFICATION_EXPECTATIONS_GLOB))

    def _build_case(
        self,
        block_text: str,
        *,
        source_path: Path,
        block_index: int,
    ) -> ClassificationExpectationCase | None:
        try:
            payload = yaml.safe_load(block_text)
        except yaml.YAMLError as exc:
            raise SchemaValidationError(
                "Classification expectation case contains invalid YAML.",
                details={"path": str(source_path), "block_index": block_index},
            ) from exc

        if not isinstance(payload, dict) or not payload.get("document_alias"):
            # Schema-illustration blocks (no document_alias) are skipped,
            # same convention as the structural-expectations loader.
            return None

        alias = str(payload["document_alias"])
        # Fail fast on an alias that does not exist in the golden corpus
        # manifest, rather than silently carrying a dangling expectation
        # that could never be matched to a real evaluated document.
        self._manifest.entry(alias)

        raw_type = payload.get("expected_document_type")
        if not raw_type:
            raise SchemaValidationError(
                "Classification expectation case is missing required field "
                "'expected_document_type'.",
                details={"path": str(source_path), "alias": alias},
            )
        try:
            expected_document_type = DocumentType(str(raw_type).strip().lower())
        except ValueError as exc:
            raise SchemaValidationError(
                "Classification expectation case has an invalid "
                "'expected_document_type'.",
                details={
                    "path": str(source_path),
                    "alias": alias,
                    "expected_document_type": raw_type,
                },
            ) from exc

        raw_review_status = payload.get("review_status")
        if raw_review_status is None:
            review_status = ClassificationReviewStatus.CANDIDATE
        else:
            try:
                review_status = ClassificationReviewStatus(
                    str(raw_review_status).strip().lower()
                )
            except ValueError as exc:
                raise SchemaValidationError(
                    "Classification expectation case has an invalid "
                    "'review_status'.",
                    details={
                        "path": str(source_path),
                        "alias": alias,
                        "review_status": raw_review_status,
                    },
                ) from exc

        return ClassificationExpectationCase(
            document_alias=alias,
            expected_document_type=expected_document_type,
            ambiguous=bool(payload.get("ambiguous", False)),
            review_status=review_status,
            notes=payload.get("notes"),
        )

    @staticmethod
    def _reject_duplicate_aliases(cases: list[ClassificationExpectationCase]) -> None:
        seen: set[str] = set()
        duplicates: set[str] = set()
        for case in cases:
            if case.document_alias in seen:
                duplicates.add(case.document_alias)
            seen.add(case.document_alias)

        if duplicates:
            raise SchemaValidationError(
                "Classification expectations contain duplicate document aliases.",
                details={"aliases": sorted(duplicates)},
            )


__all__ = [
    "ClassificationExpectationLoader",
    "DEFAULT_CLASSIFICATION_EXPECTATIONS_GLOB",
]
