from dataclasses import dataclass

from src.application.evaluation.corpus.resolved_golden_document import (
    GoldenDocumentAvailability,
    ResolvedGoldenDocument,
)
from src.application.evaluation.golden.cache_only_parser_guard import (
    GoldenCorpusDoclingUnavailableError,
)
from src.application.evaluation.golden.golden_document_evaluation_outcome import (
    GoldenDocumentEvaluationStatus,
)
from src.domain.document import DocumentGraph
from src.shared.exceptions import ApplicationError
from src.shared.ids import IdGenerator, IdPrefix


@dataclass(slots=True, frozen=True)
class GoldenDocumentParseOutcome:
    """The parsing-stage-only result of resolving and parsing one golden
    corpus document - extracted from the Phase 1 fast-regression runner so
    the Phase 2A classification runner can reuse the exact same
    resolve-then-parse-then-classify-outcomes semantics (corpus
    availability checks, cache-only-mode guard, fault isolation around a
    single document's real parse failure) without duplicating it."""

    alias: str
    status: GoldenDocumentEvaluationStatus
    document_graph: DocumentGraph | None = None
    detail: str | None = None


def parse_golden_document(
    *,
    resolved: ResolvedGoldenDocument,
    parsing_workflow,
    id_generator: IdGenerator,
) -> GoldenDocumentParseOutcome:
    if resolved.availability == GoldenDocumentAvailability.MISSING:
        return GoldenDocumentParseOutcome(
            alias=resolved.alias,
            status=GoldenDocumentEvaluationStatus.CORPUS_MISSING,
            detail=f"expected file not found at {resolved.absolute_path}",
        )

    if resolved.availability == GoldenDocumentAvailability.HASH_MISMATCH:
        return GoldenDocumentParseOutcome(
            alias=resolved.alias,
            status=GoldenDocumentEvaluationStatus.CORPUS_HASH_MISMATCH,
            detail=(
                f"expected sha256={resolved.entry.expected_sha256} "
                f"actual={resolved.actual_sha256}"
            ),
        )

    document_id = id_generator.new_id(IdPrefix.DOCUMENT)
    try:
        parse_result = parsing_workflow.parse(
            file_path=str(resolved.absolute_path),
            file_hash=resolved.actual_sha256,
            content_hash=None,
            document_id=document_id,
        )
    except GoldenCorpusDoclingUnavailableError as exc:
        return GoldenDocumentParseOutcome(
            alias=resolved.alias,
            status=GoldenDocumentEvaluationStatus.CACHE_MISS_IN_CACHED_ONLY_MODE,
            detail=str(exc),
        )
    except ApplicationError as exc:
        # Fault isolation across an independent unit of work in a
        # multi-document batch: one document's real Docling failure must
        # not silently abort evaluation of the other nine, but must also
        # never disappear - it is recorded as an explicit, visible outcome.
        return GoldenDocumentParseOutcome(
            alias=resolved.alias,
            status=GoldenDocumentEvaluationStatus.PARSE_FAILED,
            detail=repr(exc),
        )

    return GoldenDocumentParseOutcome(
        alias=resolved.alias,
        status=GoldenDocumentEvaluationStatus.EVALUATED,
        document_graph=parse_result.document_graph,
    )


__all__ = ["GoldenDocumentParseOutcome", "parse_golden_document"]
