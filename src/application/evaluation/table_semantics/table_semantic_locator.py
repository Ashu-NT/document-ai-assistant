from __future__ import annotations

import json
from pathlib import Path

from docling_core.types.doc import DoclingDocument

from src.application.evaluation.corpus import EvaluationCorpusTier, GoldenCorpusManifest
from src.application.orchestrator.ingestion.parsing_runtime_builder import (
    build_parsing_runtime,
)
from src.application.workflows.ingestion.hashing.file_hash_service import (
    compute_file_hash,
)
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.application.workflows.parsing.tables.rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)
from src.config.settings import golden_corpus_settings
from src.domain.assets import TableAsset
from src.domain.document import DocumentGraph
from src.shared.ids import IdGenerator

# Documents available only through GoldenCorpusManifest (e.g. CHALLENGE-tier
# documents, which are deliberately local/external and never committed to
# the repo -- see GoldenCorpusSettings's own docstring) rather than through
# the generic data/artifacts/parsed_documents cache: document_title -> the
# manifest alias that resolves it. A REAL parse is performed for these (no
# supplied pre-cached artifact) -- this also naturally warms the normal
# artifact-store cache for next time, via the workflow's own unmodified
# cache-check-then-parse flow.
_MANIFEST_ALIAS_BY_TITLE: dict[str, str] = {
    "MTU_20V4000_Marine_Diesel_Operation_Manual_Part1": (
        "challenge_mtu_marine_engine_generator_part1"
    ),
}

# Isolated, read-only, evaluation-only table locator. Re-identifies a real
# cached table deterministically by (document_title, table_category,
# header_substring, occurrence_index) rather than by table_id, because
# table_id is generated fresh by IdGenerator on every parse call and is NOT
# stable across separate parse invocations of the same cached document,
# even though the composed table's CONTENT/order is deterministic given the
# same cached document.json input. This module never modifies parsing
# behavior, classifier behavior, thresholds, aliases, or roles, and never
# calls an LLM -- it only re-runs the existing deterministic parsing
# pipeline against an already-cached document artifact.

_PARSED_ARTIFACT_CACHE_DIR = "data/artifacts/parsed_documents"


class _SuppliedArtifactParser:
    parser_name = "docling"
    parser_version = None

    def __init__(self, raw: RawParsedDocument) -> None:
        self._raw = raw

    def parse(self, file_path: str, *, enable_ocr_override: bool | None = None) -> RawParsedDocument:
        return self._raw

    def resolve_conversion_fingerprint(self, *, enable_ocr_override: bool | None = None) -> str:
        raise NotImplementedError


def _project_root() -> Path:
    # golden_corpus_settings.root_path resolves to <project_root>/TestDoc
    return golden_corpus_settings.root_path.parent


def _find_cached_document_json(document_title: str) -> Path | None:
    cache_dir = _project_root() / _PARSED_ARTIFACT_CACHE_DIR
    if not cache_dir.exists():
        return None
    for entry_dir in cache_dir.iterdir():
        manifest_path = entry_dir / "manifest.json"
        document_path = entry_dir / "document.json"
        if not manifest_path.exists() or not document_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("title") == document_title:
            return document_path
    return None


def _find_real_pdf(document_title: str) -> Path | None:
    testdoc_dir = golden_corpus_settings.root_path
    candidates = list(testdoc_dir.rglob("*.pdf"))
    for candidate in candidates:
        if candidate.stem == document_title:
            return candidate
    return None


def load_cached_document_graph(document_title: str, *, id_generator: IdGenerator) -> DocumentGraph:
    """Loads a real document's parsed graph -- preferring an already-cached
    parsed artifact (data/artifacts/parsed_documents/*/document.json, no
    re-parse, no LLM, no new PDF conversion) and falling back to a REAL
    parse (still no LLM) for documents only reachable through
    GoldenCorpusManifest (e.g. local/external CHALLENGE-tier documents that
    are never committed to the repo). Raises FileNotFoundError if neither
    path can locate `document_title`."""
    document_json_path = _find_cached_document_json(document_title)
    if document_json_path is not None:
        real_pdf = _find_real_pdf(document_title)
        if real_pdf is None:
            raise FileNotFoundError(
                f"No real source PDF found under {golden_corpus_settings.root_path} "
                f"matching title {document_title!r}"
            )
        with open(document_json_path, encoding="utf-8") as f:
            raw_dict = json.load(f)
        docling_document = DoclingDocument.model_validate(raw_dict)
        raw_parsed_document = RawParsedDocument(
            file_path=str(real_pdf),
            title=docling_document.name,
            page_count=len(docling_document.pages),
            raw_document=docling_document,
            parser_name="docling",
            parser_version=None,
        )
        workflow, _ = build_parsing_runtime(id_generator=id_generator)
        workflow.parser = _SuppliedArtifactParser(raw_parsed_document)
        workflow.parsed_artifact_store = None
        result = workflow.parse(
            file_path=str(real_pdf),
            file_hash=compute_file_hash(real_pdf),
            content_hash=None,
            document_id=id_generator.new_id("doc"),
        )
        return result.document_graph

    manifest_alias = _MANIFEST_ALIAS_BY_TITLE.get(document_title)
    if manifest_alias is not None:
        manifest = GoldenCorpusManifest.default()
        resolved = next(
            (
                r
                for r in manifest.resolve_all(
                    tiers=frozenset(
                        {EvaluationCorpusTier.CORE, EvaluationCorpusTier.CHALLENGE}
                    )
                )
                if r.alias == manifest_alias
            ),
            None,
        )
        if resolved is not None and resolved.absolute_path.exists():
            workflow, _ = build_parsing_runtime(id_generator=id_generator)
            result = workflow.parse(
                file_path=str(resolved.absolute_path),
                file_hash=resolved.actual_sha256 or compute_file_hash(resolved.absolute_path),
                content_hash=None,
                document_id=id_generator.new_id("doc"),
            )
            return result.document_graph

    raise FileNotFoundError(
        f"No cached parsed-document artifact and no resolvable GoldenCorpusManifest "
        f"entry found for document_title={document_title!r}"
    )


def locate_real_table(
    graph: DocumentGraph,
    *,
    table_category: str,
    header_substring: str | None,
    occurrence_index: int,
    row_canonicalizer: TableRowCanonicalizer | None = None,
) -> TableAsset | None:
    """Deterministically re-identifies the same logical table a human
    reviewer selected, within a FRESH parse of the same cached document.
    Matching is positional among same-category (and, if given,
    same-header-substring) tables in `graph.tables`' iteration order --
    stable because the underlying parse is deterministic given the same
    cached input, even though each table's generated `table_id` is not."""
    canonicalizer = row_canonicalizer or TableRowCanonicalizer()
    matches = []
    for table in graph.tables.values():
        if table.table_category != table_category:
            continue
        if header_substring is not None:
            canonical_rows = canonicalizer.canonicalize(table.rows)
            has_header = canonicalizer.has_explicit_header_row(canonical_rows)
            headers = canonical_rows[0] if has_header else []
            if not any(header_substring.lower() in (h or "").lower() for h in headers):
                continue
        matches.append(table)
    if occurrence_index >= len(matches):
        return None
    return matches[occurrence_index]
