import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from src.application.evaluation.corpus.golden_corpus_manifest import (
    GoldenCorpusManifest,
)
from src.application.evaluation.extraction.extraction_applicability import (
    ExtractionApplicability,
)
from src.application.evaluation.extraction.extraction_completeness import (
    ExtractionCompleteness,
)
from src.application.evaluation.extraction.extraction_entity_type import (
    ExtractionEntityType,
)
from src.application.evaluation.extraction.extraction_evaluation_scope import (
    ExtractionEvaluationScope,
    ExtractionScopeType,
)
from src.application.evaluation.extraction.extraction_expectation_case import (
    ExtractedEvidenceExpectation,
    ExtractionApplicabilityDeclaration,
    ExtractionExpectationCase,
)
from src.application.evaluation.extraction.extraction_review_status import (
    ExtractionReviewStatus,
)
from src.application.evaluation.extraction.matchers.entity_identity_keys import (
    ENTITY_IDENTITY_FIELD_NAMES,
)
from src.application.evaluation.extraction.matchers.field_assertion import (
    has_usable_identity_assertion,
)
from src.application.evaluation.retrieval.benchmarking.loaders.markdown_section_parser import (
    extract_sections,
)
from src.config.settings import golden_corpus_settings
from src.shared.exceptions import SchemaValidationError

# Same shape-based-discovery convention as Phase 1/2A - discovered via glob,
# never a hardcoded filename/section number.
DEFAULT_EXTRACTION_EXPECTATIONS_GLOB = "fixtures/extraction_expectations*.md"

_YAML_BLOCK_PATTERN = re.compile(r"```yaml\s*\n(?P<body>.*?)```", re.DOTALL)


@dataclass(slots=True)
class ExtractionTruthSet:
    expectations: list[ExtractionExpectationCase] = field(default_factory=list)
    applicability_declarations: list[ExtractionApplicabilityDeclaration] = field(
        default_factory=list
    )


class ExtractionExpectationLoader:
    def __init__(self, *, manifest: GoldenCorpusManifest | None = None) -> None:
        self._manifest = manifest or GoldenCorpusManifest.default()

    def load(self, path: Path | str | None = None) -> ExtractionTruthSet:
        source_paths = self._source_paths(path)
        missing = [p for p in source_paths if not p.exists()]
        if missing:
            raise SchemaValidationError(
                "Extraction expectation file not found.",
                details={"path": str(missing[0])},
            )

        truth_set = ExtractionTruthSet()
        for source_path in source_paths:
            self._load_file(source_path, truth_set)

        self._reject_duplicate_ids(truth_set)
        return truth_set

    def _source_paths(self, path: Path | str | None) -> list[Path]:
        if path is not None:
            return [Path(path)]
        root = golden_corpus_settings.root_path
        return sorted(root.glob(DEFAULT_EXTRACTION_EXPECTATIONS_GLOB))

    def _load_file(self, source_path: Path, truth_set: ExtractionTruthSet) -> None:
        text = source_path.read_text(encoding="utf-8")
        sections = extract_sections(text)

        block_index = 0
        for section_body in sections.values():
            for block_text in _YAML_BLOCK_PATTERN.findall(section_body):
                block_index += 1
                self._build_entry(
                    block_text,
                    source_path=source_path,
                    block_index=block_index,
                    truth_set=truth_set,
                )

    def _build_entry(
        self,
        block_text: str,
        *,
        source_path: Path,
        block_index: int,
        truth_set: ExtractionTruthSet,
    ) -> None:
        try:
            payload = yaml.safe_load(block_text)
        except yaml.YAMLError as exc:
            raise SchemaValidationError(
                "Extraction expectation entry contains invalid YAML.",
                details={"path": str(source_path), "block_index": block_index},
            ) from exc

        if not isinstance(payload, dict) or not payload.get("kind"):
            # Schema-illustration blocks (no `kind`) are skipped.
            return

        kind = str(payload["kind"]).strip().lower()
        if kind == "expectation":
            truth_set.expectations.append(
                self._build_expectation(payload, source_path=source_path)
            )
        elif kind == "applicability":
            truth_set.applicability_declarations.append(
                self._build_applicability_declaration(payload, source_path=source_path)
            )
        else:
            raise SchemaValidationError(
                "Extraction expectation entry has an unknown 'kind' - must be "
                "'expectation' or 'applicability'.",
                details={"path": str(source_path), "kind": kind},
            )

    def _resolve_alias(self, payload: dict, *, source_path: Path) -> str:
        alias = payload.get("document_alias")
        if not alias:
            raise SchemaValidationError(
                "Extraction expectation entry is missing required field "
                "'document_alias'.",
                details={"path": str(source_path)},
            )
        alias = str(alias)
        # Fail fast on a dangling alias, same convention as Phase 1/2A.
        self._manifest.entry(alias)
        return alias

    def _resolve_entity_type(
        self, payload: dict, *, alias: str, source_path: Path
    ) -> ExtractionEntityType:
        raw = payload.get("entity_type")
        if not raw:
            raise SchemaValidationError(
                "Extraction expectation entry is missing required field "
                "'entity_type'.",
                details={"path": str(source_path), "alias": alias},
            )
        try:
            return ExtractionEntityType(str(raw).strip().lower())
        except ValueError as exc:
            raise SchemaValidationError(
                "Extraction expectation entry has an invalid 'entity_type' - "
                "must be one of the exact production entity types.",
                details={"path": str(source_path), "alias": alias, "entity_type": raw},
            ) from exc

    def _resolve_scope(
        self, payload: dict, *, alias: str, source_path: Path
    ) -> ExtractionEvaluationScope:
        raw_scope_type = payload.get("scope_type")
        if not raw_scope_type:
            raise SchemaValidationError(
                "Extraction expectation entry is missing required field "
                "'scope_type'.",
                details={"path": str(source_path), "alias": alias},
            )
        try:
            scope_type = ExtractionScopeType(str(raw_scope_type).strip().lower())
        except ValueError as exc:
            raise SchemaValidationError(
                "Extraction expectation entry has an invalid 'scope_type'.",
                details={
                    "path": str(source_path),
                    "alias": alias,
                    "scope_type": raw_scope_type,
                },
            ) from exc

        page_start = payload.get("page_start")
        page_end = payload.get("page_end")
        try:
            return ExtractionEvaluationScope(
                scope_type=scope_type,
                page_start=int(page_start) if page_start is not None else None,
                page_end=int(page_end) if page_end is not None else None,
            )
        except ValueError as exc:
            raise SchemaValidationError(
                "Extraction expectation entry has an invalid scope "
                f"({exc}).",
                details={
                    "path": str(source_path),
                    "alias": alias,
                    "scope_type": raw_scope_type,
                    "page_start": page_start,
                    "page_end": page_end,
                },
            ) from exc

    def _resolve_review_status(
        self, payload: dict, *, alias: str, source_path: Path
    ) -> ExtractionReviewStatus:
        raw = payload.get("review_status")
        if raw is None:
            return ExtractionReviewStatus.CANDIDATE
        try:
            return ExtractionReviewStatus(str(raw).strip().lower())
        except ValueError as exc:
            raise SchemaValidationError(
                "Extraction expectation entry has an invalid 'review_status'.",
                details={"path": str(source_path), "alias": alias, "review_status": raw},
            ) from exc

    def _build_expectation(
        self, payload: dict, *, source_path: Path
    ) -> ExtractionExpectationCase:
        alias = self._resolve_alias(payload, source_path=source_path)
        entity_type = self._resolve_entity_type(
            payload, alias=alias, source_path=source_path
        )
        scope = self._resolve_scope(payload, alias=alias, source_path=source_path)
        review_status = self._resolve_review_status(
            payload, alias=alias, source_path=source_path
        )

        case_id = payload.get("case_id")
        if not case_id:
            raise SchemaValidationError(
                "Extraction expectation entry is missing required field "
                "'case_id'.",
                details={"path": str(source_path), "alias": alias},
            )

        raw_completeness = payload.get("completeness")
        if raw_completeness is None:
            completeness = ExtractionCompleteness.PRESENCE_ONLY
        else:
            try:
                completeness = ExtractionCompleteness(
                    str(raw_completeness).strip().lower()
                )
            except ValueError as exc:
                raise SchemaValidationError(
                    "Extraction expectation entry has an invalid 'completeness'.",
                    details={
                        "path": str(source_path),
                        "alias": alias,
                        "completeness": raw_completeness,
                    },
                ) from exc

        expected_fields = payload.get("expected_fields") or {}
        if not isinstance(expected_fields, dict):
            raise SchemaValidationError(
                "Extraction expectation 'expected_fields' must be a mapping.",
                details={"path": str(source_path), "alias": alias, "case_id": case_id},
            )
        expected_fields = {
            str(key): (None if value is None else str(value))
            for key, value in expected_fields.items()
        }

        expected_evidence = None
        raw_evidence = payload.get("expected_evidence")
        if raw_evidence is not None:
            if not isinstance(raw_evidence, dict):
                raise SchemaValidationError(
                    "Extraction expectation 'expected_evidence' must be a "
                    "mapping.",
                    details={
                        "path": str(source_path),
                        "alias": alias,
                        "case_id": case_id,
                    },
                )
            expected_evidence = ExtractedEvidenceExpectation(
                page_start=(
                    int(raw_evidence["page_start"])
                    if raw_evidence.get("page_start") is not None
                    else None
                ),
                page_end=(
                    int(raw_evidence["page_end"])
                    if raw_evidence.get("page_end") is not None
                    else None
                ),
                section_heading=raw_evidence.get("section_heading"),
                requires_table_association=raw_evidence.get(
                    "requires_table_association"
                ),
            )

        identity_override = payload.get("identity_fields_override")
        identity_fields_override = (
            tuple(str(name) for name in identity_override)
            if identity_override
            else None
        )

        production_identity_fields = identity_fields_override or (
            ENTITY_IDENTITY_FIELD_NAMES[entity_type]
        )
        if not has_usable_identity_assertion(
            expected_fields, production_identity_fields
        ):
            raise SchemaValidationError(
                "Extraction expectation has no usable asserted identity "
                "field - this would vacuously match every actual entity of "
                f"this type. entity_type={entity_type.value!r} requires at "
                "least one of "
                f"{production_identity_fields!r} to be asserted as a real "
                "(non-null) value in 'expected_fields'. Asserting a field "
                "as explicitly null alone does not count - see "
                "field_assertion.has_usable_identity_assertion.",
                details={
                    "path": str(source_path),
                    "alias": alias,
                    "case_id": case_id,
                    "entity_type": entity_type.value,
                    "identity_fields": list(production_identity_fields),
                    "expected_fields": expected_fields,
                },
            )

        return ExtractionExpectationCase(
            case_id=str(case_id),
            document_alias=alias,
            entity_type=entity_type,
            scope=scope,
            completeness=completeness,
            review_status=review_status,
            expected_fields=expected_fields,
            identity_fields_override=identity_fields_override,
            expected_evidence=expected_evidence,
            notes=payload.get("notes"),
        )

    def _build_applicability_declaration(
        self, payload: dict, *, source_path: Path
    ) -> ExtractionApplicabilityDeclaration:
        alias = self._resolve_alias(payload, source_path=source_path)
        entity_type = self._resolve_entity_type(
            payload, alias=alias, source_path=source_path
        )
        scope = self._resolve_scope(payload, alias=alias, source_path=source_path)
        review_status = self._resolve_review_status(
            payload, alias=alias, source_path=source_path
        )

        declaration_id = payload.get("declaration_id")
        if not declaration_id:
            raise SchemaValidationError(
                "Extraction applicability entry is missing required field "
                "'declaration_id'.",
                details={"path": str(source_path), "alias": alias},
            )

        raw_applicability = payload.get("applicability")
        if not raw_applicability:
            raise SchemaValidationError(
                "Extraction applicability entry is missing required field "
                "'applicability'.",
                details={
                    "path": str(source_path),
                    "alias": alias,
                    "declaration_id": declaration_id,
                },
            )
        try:
            applicability = ExtractionApplicability(
                str(raw_applicability).strip().lower()
            )
        except ValueError as exc:
            raise SchemaValidationError(
                "Extraction applicability entry has an invalid "
                "'applicability'.",
                details={
                    "path": str(source_path),
                    "alias": alias,
                    "declaration_id": declaration_id,
                    "applicability": raw_applicability,
                },
            ) from exc

        try:
            return ExtractionApplicabilityDeclaration(
                declaration_id=str(declaration_id),
                document_alias=alias,
                entity_type=entity_type,
                scope=scope,
                applicability=applicability,
                review_status=review_status,
                reason=payload.get("reason"),
                notes=payload.get("notes"),
            )
        except ValueError as exc:
            raise SchemaValidationError(
                str(exc),
                details={
                    "path": str(source_path),
                    "alias": alias,
                    "declaration_id": declaration_id,
                },
            ) from exc

    @staticmethod
    def _reject_duplicate_ids(truth_set: ExtractionTruthSet) -> None:
        seen_case_ids: set[str] = set()
        duplicate_case_ids: set[str] = set()
        for expectation in truth_set.expectations:
            if expectation.case_id in seen_case_ids:
                duplicate_case_ids.add(expectation.case_id)
            seen_case_ids.add(expectation.case_id)
        if duplicate_case_ids:
            raise SchemaValidationError(
                "Extraction expectations contain duplicate case ids.",
                details={"case_ids": sorted(duplicate_case_ids)},
            )

        seen_declaration_ids: set[str] = set()
        duplicate_declaration_ids: set[str] = set()
        for declaration in truth_set.applicability_declarations:
            if declaration.declaration_id in seen_declaration_ids:
                duplicate_declaration_ids.add(declaration.declaration_id)
            seen_declaration_ids.add(declaration.declaration_id)
        if duplicate_declaration_ids:
            raise SchemaValidationError(
                "Extraction applicability declarations contain duplicate ids.",
                details={"declaration_ids": sorted(duplicate_declaration_ids)},
            )


__all__ = [
    "ExtractionExpectationLoader",
    "ExtractionTruthSet",
    "DEFAULT_EXTRACTION_EXPECTATIONS_GLOB",
]
