"""CHALLENGE-tier structural regression for the MTU marine engine-generator
system documentation (see EvaluationCorpusTier and
outputs/architecture/mtu_challenge_document_reconnaissance.md).

This document lives outside the repo (the user's local Downloads folder)
and has no entry in the Parsed Artifact Store (per the explicit instruction
not to fabricate its ParsedArtifactKey identity - the originating Docling
version is not provable from available evidence). It is never picked up by
`run_fast_golden_regression()`'s default (CORE-only) tier filtering, and
this test itself skips cleanly wherever the external PDF or the supplied
`document.json` raw parse are not present - it must never be a hard
dependency of an ordinary `pytest tests/integration -m integration` run on
another machine/CI.

Instead of a live Docling call, this test reconstructs a real
`DoclingDocument` from the already-supplied `document.json` (git-tracked at
the repo root) and runs it through the SAME production
normalizer/DocumentGraphBuilder path `ParsingWorkflow` always uses - only
the live Docling conversion step is replaced, exactly like the existing
`CacheOnlyParserGuard`/fake-parser substitution pattern already used
elsewhere in the golden-regression test suite.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

_MTU_PDF_PATH = Path(
    r"C:\Users\ashuf\Downloads\3210-0010 MTU MAN Marine Engine Generator "
    r"20V4000M53B System Documentation SA18000434_00E Part1.pdf"
)
_MTU_DOCUMENT_JSON_PATH = Path(__file__).resolve().parents[3] / "document.json"


def _build_mtu_document_graph():
    from docling_core.types.doc import DoclingDocument

    from src.application.evaluation.corpus import (
        EvaluationCorpusTier,
        GoldenCorpusManifest,
    )
    from src.application.orchestrator.ingestion.parsing_runtime_builder import (
        build_parsing_runtime,
    )
    from src.application.workflows.ingestion.hashing.file_hash_service import (
        compute_file_hash,
    )
    from src.application.workflows.parsing.raw_parsed_document import (
        RawParsedDocument,
    )
    from src.shared.ids import IdGenerator

    manifest = GoldenCorpusManifest.default()
    resolved = next(
        r
        for r in manifest.resolve_all(tiers=frozenset({EvaluationCorpusTier.CHALLENGE}))
        if r.alias == "challenge_mtu_marine_engine_generator_part1"
    )

    with open(_MTU_DOCUMENT_JSON_PATH, encoding="utf-8") as f:
        raw_dict = json.load(f)
    docling_document = DoclingDocument.model_validate(raw_dict)

    raw_parsed_document = RawParsedDocument(
        file_path=str(resolved.absolute_path),
        title=docling_document.name,
        page_count=len(docling_document.pages),
        raw_document=docling_document,
        parser_name="docling",
        # Not provable from available evidence - see report Part 8/17.
        parser_version=None,
    )

    class _SuppliedArtifactParser:
        parser_name = "docling"
        parser_version = None

        def __init__(self, raw):
            self._raw = raw

        def parse(self, file_path, *, enable_ocr_override=None):
            return self._raw

        def resolve_conversion_fingerprint(self, *, enable_ocr_override=None):
            raise NotImplementedError(
                "no real fingerprint available for a supplied artifact"
            )

    id_generator = IdGenerator()
    workflow, _ = build_parsing_runtime(id_generator=id_generator)
    workflow.parser = _SuppliedArtifactParser(raw_parsed_document)
    # Never touch the real Parsed Artifact Store for a supplied artifact.
    workflow.parsed_artifact_store = None

    result = workflow.parse(
        file_path=str(resolved.absolute_path),
        file_hash=resolved.actual_sha256 or compute_file_hash(resolved.absolute_path),
        content_hash=None,
        document_id=id_generator.new_id("doc"),
    )
    return result.document_graph


@pytest.mark.skipif(
    not _MTU_PDF_PATH.is_file(),
    reason=(
        "MTU challenge-document PDF not present at the expected local path "
        "- this document is external/local-provisioned, never committed"
    ),
)
@pytest.mark.skipif(
    not _MTU_DOCUMENT_JSON_PATH.is_file(),
    reason="no supplied raw Docling parse (document.json) found at repo root",
)
def test_mtu_challenge_structural_regression() -> None:
    from src.application.evaluation.ingestion.ingestion_expectation_evaluator import (
        IngestionExpectationEvaluator,
    )
    from src.application.evaluation.ingestion.loaders.ingestion_truth_set_loader import (
        IngestionTruthSetLoader,
    )
    from src.shared.text.rendering_noise_detector import is_rendering_only_noise

    graph = _build_mtu_document_graph()

    cases = IngestionTruthSetLoader().load()
    case = next(
        c
        for c in cases
        if c.document_alias == "challenge_mtu_marine_engine_generator_part1"
    )

    evaluator = IngestionExpectationEvaluator()
    structural_result = evaluator.evaluate(case=case, document_graph=graph)
    budget_result = evaluator.evaluate_chunk_token_budget(graph)

    # Universal invariants that must hold regardless of document size -
    # never weakened for a large challenge document.
    empty_chunks = [
        c.chunk_id for c in graph.chunks.values() if not (c.content or "").strip()
    ]
    assert not empty_chunks, f"empty chunks found: {empty_chunks}"

    missing_chunk_provenance = [
        c.chunk_id
        for c in graph.chunks.values()
        if c.source is None or c.source.page_start is None
    ]
    assert not missing_chunk_provenance

    missing_element_provenance = [
        e.element_id
        for e in graph.elements.values()
        if e.source is None or e.source.page_start is None
    ]
    assert not missing_element_provenance

    noise_chunks = [
        c.chunk_id
        for c in graph.chunks.values()
        if is_rendering_only_noise(c.content)
    ]
    assert not noise_chunks, f"rendering-only noise chunks found: {noise_chunks}"

    # Tolerant/candidate structural expectations (see
    # structural_expectations_mtu_challenge.md) - report, don't silently
    # weaken, any failure here. `chunk_hard_token_budget` is deliberately
    # excluded from this "must all pass" check: it is a real, distinct,
    # NOT-YET-FIXED finding (4 ordinary multi-fragment-packed chunks,
    # unrelated to table degeneracy or the previously-fixed overlap-
    # injection defect - see the challenge-integration report), asserted
    # on explicitly below instead so a REGRESSION (a change in count) is
    # visible without pretending the current count is zero.
    failed_case_assertions = [
        a.name
        for a in structural_result.assertions
        if not a.passed and a.name != "chunk_hard_token_budget"
    ]
    assert not failed_case_assertions, (
        f"structural expectation assertions failed: {failed_case_assertions}"
    )

    assert budget_result.hard_budget_violation_count == 4, (
        "expected the 4 already-characterized hard-budget-violation "
        f"chunks; got {budget_result.hard_budget_violation_count} - "
        "investigate before updating this expectation"
    )
    assert budget_result.oversized_indivisible_count == 0
