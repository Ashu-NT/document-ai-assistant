"""Regression tests for silent structural corruption under concurrent
`ParsingWorkflow.parse()` calls (see project memory: a real FWC12-manual
parse produced a silently truncated DocumentGraph -
section_count=35/element_count=189/chunk_count=47 instead of 178/1078/319 -
under two concurrent OS-process parses of the same PDF; no exception was
raised, and an isolated re-run always reproduced the correct result).

These tests deliberately bypass real Docling (slow, non-deterministic ML
inference) with a fast, deterministic fake `ParserPort`, so many concurrent
trials can run quickly while still exercising every REAL orchestration
collaborator: `ParsingWorkflow`, `DocumentGraphBuilder`, `SectionBuilder`,
`GraphChunkBuilder`/`SectionChunkBuilder`, `ChunkCrossReferenceLinker`,
`CrossReferencePipeline`, `CrossReferenceReconciliationService`, and
`IdGenerator`. If a fake-converter run still diverges from its sequential
baseline, the bug is proven to live in OUR orchestration code, not inside
Docling's own (unauditable, third-party) ML pipeline.

HISTORY: this file started as an investigation-only reproducer proving a
confirmed shared-instance race (`SectionChunkBuilder.last_structural_
profile_inference` and its sibling `last_*` attributes on `GraphChunkBuilder`/
`DocumentGraphBuilder`/`ParsingWorkflow` - an invocation-specific result
written to `self` mid-call and read back by a caller after the call
returned, unsafe when the owning instance is reused across concurrent
calls). That race has since been fixed by replacing every such attribute
with an explicit return value (`SectionChunkBuildResult`,
`GraphChunkBuildResult`, `DocumentGraphBuildResult`,
`ParsingWorkflowResult.pdf_link_extraction_result`/
`.cross_reference_linking_outcome`) - see the accompanying session report.
No lock/semaphore/thread-local/cache was added; the fix is state-ownership
only. The tests below are now genuine regression tests: the two
probabilistic reproducers and the deterministic forced-interleaving proof
must all stay green, alongside the two control groups that were already
green before the fix (fresh-runtime-per-call, and same-document concurrency
- the latter was always green too, but only because an identical "leaked"
value is indistinguishable from the correct one when both concurrent
documents are identical; it does not by itself prove the race was absent).
"""

from __future__ import annotations

import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable

from src.application.contracts.pdf_links import PdfLinkExtractionResult
from src.application.validation.document import DocumentGraphValidator
from src.application.workflows.parsing import ParsingWorkflow
from src.application.workflows.parsing.builders import DocumentGraphBuilder, SectionBuilder
from src.application.workflows.parsing.builders.document_graph.cross_references import (
    CrossReferencePipeline,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_linker import (
    ChunkCrossReferenceLinker,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.reconciliation import (
    CrossReferenceReconciliationService,
)
from src.application.workflows.parsing.normalizers import DoclingDocumentNormalizer
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.domain.document import DocumentGraph
from src.shared.ids import IdGenerator

# ---------------------------------------------------------------------------
# Fake Docling raw-document model (mirrors
# tests/unit/application/workflows/parsing/normalizers/
# _test_docling_document_normalizer_part1.py's fixtures exactly, duplicated
# here rather than imported so this investigation file stays self-contained
# and doesn't create a test-to-test import dependency).
# ---------------------------------------------------------------------------


class _FakeLabel:
    def __init__(self, value: str) -> None:
        self.value = value


class _FakeProvenance:
    def __init__(self, page_no: int) -> None:
        self.page_no = page_no
        self.bbox = None


class _FakeDoclingItem:
    def __init__(
        self,
        *,
        label: str,
        text: str | None = None,
        self_ref: str | None = None,
        level: int | None = None,
        prov: list[_FakeProvenance] | None = None,
    ) -> None:
        self.label = _FakeLabel(label)
        self.text = text
        self.markdown = None
        self.caption = None
        self.image_path = None
        self.section_path = None
        self.self_ref = self_ref
        self.prov = prov or []
        self.level = level
        self.content_layer = "body"
        self.name = None
        self.parent = None
        self.captions = []
        self.data = None
        self.requires_doc_for_markdown = False

    def export_to_markdown(self, doc=None) -> str | None:
        return self.markdown


class _FakeRawDoclingDocument:
    def __init__(self, items: list[_FakeDoclingItem]) -> None:
        self._items = items
        self.texts = []
        self.tables = []
        self.pictures = []

    def iterate_items(self, with_groups: bool = False, traverse_pictures: bool = False):
        del with_groups, traverse_pictures
        return [(item, 0) for item in self._items]


# ---------------------------------------------------------------------------
# Synthetic document shapes - deliberately very different sizes/structure so
# any cross-document contamination (wrong section count, wrong structural
# profile, wrong chunk content) is unambiguous, not a coincidental match.
# ---------------------------------------------------------------------------


def _build_manual_like_raw_document(*, marker: str, section_count: int = 24) -> tuple[
    _FakeRawDoclingDocument, int
]:
    """A ~24-section, ~3-element-per-section synthetic manual, with an
    internal annex cross-reference so the fuzzy cross-reference pipeline
    (detect -> qualify -> resolve -> reconcile) is genuinely exercised, not
    just present-but-idle."""
    items: list[_FakeDoclingItem] = []
    ref_counter = 0
    for section_index in range(1, section_count + 1):
        page = section_index
        items.append(
            _FakeDoclingItem(
                label="section_header",
                text=f"{section_index} {marker} Section {section_index}",
                self_ref=f"#/texts/{ref_counter}",
                level=1,
                prov=[_FakeProvenance(page)],
            )
        )
        ref_counter += 1
        for paragraph_index in range(3):
            ref_counter += 1
            text = (
                f"{marker} paragraph {section_index}.{paragraph_index} discussing "
                "routine maintenance procedures for the equipment covered in this "
                "manual, including inspection intervals and safety precautions."
            )
            if section_index == 2 and paragraph_index == 0:
                text += " Refer to Annex 2 for the full wiring diagram."
            items.append(
                _FakeDoclingItem(
                    label="text",
                    text=text,
                    self_ref=f"#/texts/{ref_counter}",
                    prov=[_FakeProvenance(page)],
                )
            )
    # The annex section itself, so "Refer to Annex 2" has a real target.
    ref_counter += 1
    items.append(
        _FakeDoclingItem(
            label="section_header",
            text="Annexes",
            self_ref=f"#/texts/{ref_counter}",
            level=1,
            prov=[_FakeProvenance(section_count + 1)],
        )
    )
    ref_counter += 1
    items.append(
        _FakeDoclingItem(
            label="text",
            text="8.2 Annex 2",
            self_ref=f"#/texts/{ref_counter}",
            prov=[_FakeProvenance(section_count + 1)],
        )
    )
    return _FakeRawDoclingDocument(items), section_count + 1


def _build_small_raw_document(*, marker: str, section_count: int = 3) -> tuple[
    _FakeRawDoclingDocument, int
]:
    """A tiny, structurally very different synthetic document (few sections,
    single short paragraph each) - deliberately far from the manual shape so
    any cross-document bleed under concurrency is glaringly obvious in
    section/element counts alone, not just in subtle metadata."""
    items: list[_FakeDoclingItem] = []
    ref_counter = 0
    for section_index in range(1, section_count + 1):
        items.append(
            _FakeDoclingItem(
                label="section_header",
                text=f"{section_index} {marker} Note {section_index}",
                self_ref=f"#/texts/{ref_counter}",
                level=1,
                prov=[_FakeProvenance(section_index)],
            )
        )
        ref_counter += 1
        items.append(
            _FakeDoclingItem(
                label="text",
                text=f"{marker} short note {section_index}.",
                self_ref=f"#/texts/{ref_counter}",
                prov=[_FakeProvenance(section_index)],
            )
        )
        ref_counter += 1
    return _FakeRawDoclingDocument(items), section_count


class _FakeParser:
    """Conforms to ParserPort. Deterministic, in-process, no subprocess/ML -
    isolates the investigation to OUR orchestration code."""

    parser_name = "fake"
    parser_version = "1.0.0"

    def __init__(self, raw_document: _FakeRawDoclingDocument, *, page_count: int) -> None:
        self._raw_document = raw_document
        self._page_count = page_count

    def parse(self, file_path: str, *, enable_ocr_override: bool | None = None) -> RawParsedDocument:
        del enable_ocr_override
        return RawParsedDocument(
            file_path=file_path,
            title=None,
            page_count=self._page_count,
            raw_document=self._raw_document,
            parser_name=self.parser_name,
            parser_version=self.parser_version,
        )


class _RoutingParser:
    """Conforms to ParserPort. Routes by `file_path` to one of several fake
    single-document parsers - lets many threads share ONE ParsingWorkflow
    while each still parsing "its own" synthetic document content, exactly
    mirroring how a real shared runtime would route real different files."""

    parser_name = "fake"
    parser_version = "1.0.0"

    def __init__(self, parsers_by_path: dict[str, _FakeParser]) -> None:
        self._parsers_by_path = parsers_by_path

    def parse(self, file_path: str, *, enable_ocr_override: bool | None = None) -> RawParsedDocument:
        return self._parsers_by_path[file_path].parse(
            file_path, enable_ocr_override=enable_ocr_override
        )


def _build_workflow(parser: Any) -> tuple[ParsingWorkflow, DocumentGraphBuilder]:
    """Mirrors `build_parsing_runtime()`'s wiring shape exactly (same
    collaborator classes, same construction order) but with a fake parser
    and no PDF-link extractor, so this file has zero dependency on ambient
    `chunking_settings`/env state and stays fully self-contained."""
    id_generator = IdGenerator()
    section_builder = SectionBuilder(id_generator)
    chunk_cross_reference_linker = ChunkCrossReferenceLinker(id_generator=id_generator)
    cross_reference_pipeline = CrossReferencePipeline(
        fuzzy_linker=chunk_cross_reference_linker,
        native_linker=None,
        reconciliation_service=CrossReferenceReconciliationService(
            id_generator=id_generator
        ),
    )
    document_graph_builder = DocumentGraphBuilder(
        id_generator=id_generator,
        section_builder=section_builder,
        cross_reference_pipeline=cross_reference_pipeline,
    )
    parsing_workflow = ParsingWorkflow(
        parser=parser,
        normalizer=DoclingDocumentNormalizer(),
        document_graph_builder=document_graph_builder,
        id_generator=id_generator,
        document_graph_validator=DocumentGraphValidator(),
    )
    return parsing_workflow, document_graph_builder


# ---------------------------------------------------------------------------
# Structural snapshot - the FULL comparison list the investigation requires,
# not just "did parse() return without raising."
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _Snapshot:
    element_count: int
    element_type_counts: tuple[tuple[str, int], ...]
    section_count: int
    chunk_count: int
    table_count: int
    picture_count: int
    cross_reference_evidence_count: int
    canonical_cross_reference_count: int
    reconciliation_outcome_counts: tuple[tuple[str, int], ...]
    structural_profile_features_section_count: int | None
    graph_validation_ok: bool
    marker: str
    chunk_content_markers: tuple[str, ...]


def _snapshot(graph: DocumentGraph, *, expected_marker: str) -> _Snapshot:
    element_type_counts = Counter(
        str(element.element_type) for element in graph.elements.values()
    )
    reconciliation_outcome_counts = Counter(
        (xref.reconciliation_outcome.value if xref.reconciliation_outcome else "(none)")
        for xref in graph.cross_references.values()
    )
    inference = graph.document.metadata.get("structural_profile_inference")
    structural_section_count = None
    if isinstance(inference, dict):
        structural_section_count = (
            inference.get("features", {}).get("section_count")
        )
    # Distinct non-marker-content substrings actually found in this
    # document's own chunks - a direct, content-level cross-contamination
    # check independent of raw counts (two different-sized documents could
    # in principle produce a matching chunk count by coincidence; they can
    # never legitimately share chunk text unless something bled across).
    chunk_markers = tuple(
        sorted(
            {
                chunk.content.split()[0]
                for chunk in graph.chunks.values()
                if chunk.content
            }
        )
    )
    return _Snapshot(
        element_count=len(graph.elements),
        element_type_counts=tuple(sorted(element_type_counts.items())),
        section_count=len(graph.sections),
        chunk_count=len(graph.chunks),
        table_count=len(graph.tables),
        picture_count=len(graph.pictures),
        cross_reference_evidence_count=len(graph.cross_reference_evidence),
        canonical_cross_reference_count=len(graph.cross_references),
        reconciliation_outcome_counts=tuple(sorted(reconciliation_outcome_counts.items())),
        structural_profile_features_section_count=structural_section_count,
        graph_validation_ok=True,  # parse() raises internally otherwise
        marker=expected_marker,
        chunk_content_markers=chunk_markers,
    )


def _parse_once(
    workflow: ParsingWorkflow, *, file_path: str, document_id: str
) -> DocumentGraph:
    result = workflow.parse(
        file_path=file_path,
        file_hash=f"hash_{document_id}",
        content_hash=f"content_{document_id}",
        document_id=document_id,
    )
    return result.document_graph


# ---------------------------------------------------------------------------
# Reproducer 1: same document, shared runtime, concurrent threads.
# ---------------------------------------------------------------------------


def _run_same_document_trial(trial_index: int) -> tuple[_Snapshot, list[_Snapshot]]:
    raw_document, page_count = _build_manual_like_raw_document(
        marker=f"SAME{trial_index}", section_count=24
    )
    file_path = f"data/input/same_{trial_index}.pdf"
    parser = _FakeParser(raw_document, page_count=page_count)
    workflow, _ = _build_workflow(parser)

    baseline_graph = _parse_once(
        workflow, file_path=file_path, document_id=f"doc_same_{trial_index}_baseline"
    )
    baseline = _snapshot(baseline_graph, expected_marker=f"SAME{trial_index}")

    concurrent_snapshots: list[_Snapshot] = []
    concurrency = 4

    def _worker(worker_index: int) -> _Snapshot:
        graph = _parse_once(
            workflow,
            file_path=file_path,
            document_id=f"doc_same_{trial_index}_{worker_index}",
        )
        return _snapshot(graph, expected_marker=f"SAME{trial_index}")

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        for snapshot in executor.map(_worker, range(concurrency)):
            concurrent_snapshots.append(snapshot)

    return baseline, concurrent_snapshots


def test_same_document_concurrent_parsing_matches_sequential_baseline() -> None:
    trials = 25
    diverging = 0
    details: list[str] = []

    for trial_index in range(trials):
        baseline, concurrent_snapshots = _run_same_document_trial(trial_index)
        for worker_index, snapshot in enumerate(concurrent_snapshots):
            if snapshot != baseline:
                diverging += 1
                details.append(
                    f"trial={trial_index} worker={worker_index} "
                    f"baseline={baseline} got={snapshot}"
                )

    total = trials * 4
    assert diverging == 0, (
        f"{diverging}/{total} same-document concurrent parses diverged from "
        f"the sequential baseline. First divergence: "
        f"{details[0] if details else 'n/a'}"
    )


# ---------------------------------------------------------------------------
# Reproducer 2: two structurally different documents, shared runtime,
# concurrent threads.
# ---------------------------------------------------------------------------


def _run_different_document_trial(
    trial_index: int,
) -> tuple[dict[str, _Snapshot], list[tuple[str, _Snapshot]]]:
    manual_raw, manual_pages = _build_manual_like_raw_document(
        marker=f"MANUAL{trial_index}", section_count=24
    )
    small_raw, small_pages = _build_small_raw_document(
        marker=f"SMALL{trial_index}", section_count=3
    )
    manual_path = f"data/input/manual_{trial_index}.pdf"
    small_path = f"data/input/small_{trial_index}.pdf"

    parser = _RoutingParser(
        {
            manual_path: _FakeParser(manual_raw, page_count=manual_pages),
            small_path: _FakeParser(small_raw, page_count=small_pages),
        }
    )
    workflow, _ = _build_workflow(parser)

    baselines = {
        manual_path: _snapshot(
            _parse_once(
                workflow,
                file_path=manual_path,
                document_id=f"doc_manual_{trial_index}_baseline",
            ),
            expected_marker=f"MANUAL{trial_index}",
        ),
        small_path: _snapshot(
            _parse_once(
                workflow,
                file_path=small_path,
                document_id=f"doc_small_{trial_index}_baseline",
            ),
            expected_marker=f"SMALL{trial_index}",
        ),
    }

    jobs = [
        (manual_path, f"MANUAL{trial_index}"),
        (small_path, f"SMALL{trial_index}"),
        (manual_path, f"MANUAL{trial_index}"),
        (small_path, f"SMALL{trial_index}"),
    ]
    results: list[tuple[str, _Snapshot]] = []

    def _worker(job_index: int) -> tuple[str, _Snapshot]:
        path, marker = jobs[job_index]
        graph = _parse_once(
            workflow,
            file_path=path,
            document_id=f"doc_{trial_index}_{job_index}",
        )
        return path, _snapshot(graph, expected_marker=marker)

    with ThreadPoolExecutor(max_workers=len(jobs)) as executor:
        for result in executor.map(_worker, range(len(jobs))):
            results.append(result)

    return baselines, results


def test_different_document_concurrent_parsing_matches_sequential_baseline() -> None:
    trials = 25
    diverging = 0
    details: list[str] = []

    for trial_index in range(trials):
        baselines, results = _run_different_document_trial(trial_index)
        for job_index, (path, snapshot) in enumerate(results):
            baseline = baselines[path]
            if snapshot != baseline:
                diverging += 1
                details.append(
                    f"trial={trial_index} job={job_index} path={path} "
                    f"baseline={baseline} got={snapshot}"
                )

    total = trials * 4
    assert diverging == 0, (
        f"{diverging}/{total} different-document concurrent parses diverged "
        f"from the sequential baseline. First divergence: "
        f"{details[0] if details else 'n/a'}"
    )


# ---------------------------------------------------------------------------
# Control group: a FRESH, independent runtime per call (no instance sharing)
# under the exact same concurrency pattern. This must stay green - it
# isolates the bug to *shared-instance reuse*, not to concurrency itself.
# ---------------------------------------------------------------------------


def test_different_document_concurrent_parsing_with_fresh_runtime_per_call_matches_baseline() -> (
    None
):
    trials = 10
    diverging = 0
    details: list[str] = []

    for trial_index in range(trials):
        manual_raw, manual_pages = _build_manual_like_raw_document(
            marker=f"FRESHMANUAL{trial_index}", section_count=24
        )
        small_raw, small_pages = _build_small_raw_document(
            marker=f"FRESHSMALL{trial_index}", section_count=3
        )
        manual_path = f"data/input/fresh_manual_{trial_index}.pdf"
        small_path = f"data/input/fresh_small_{trial_index}.pdf"

        def _fresh_workflow_for(path: str) -> ParsingWorkflow:
            if path == manual_path:
                parser: Any = _FakeParser(manual_raw, page_count=manual_pages)
            else:
                parser = _FakeParser(small_raw, page_count=small_pages)
            workflow, _ = _build_workflow(parser)
            return workflow

        baselines = {
            manual_path: _snapshot(
                _parse_once(
                    _fresh_workflow_for(manual_path),
                    file_path=manual_path,
                    document_id=f"doc_fresh_manual_{trial_index}_baseline",
                ),
                expected_marker=f"FRESHMANUAL{trial_index}",
            ),
            small_path: _snapshot(
                _parse_once(
                    _fresh_workflow_for(small_path),
                    file_path=small_path,
                    document_id=f"doc_fresh_small_{trial_index}_baseline",
                ),
                expected_marker=f"FRESHSMALL{trial_index}",
            ),
        }

        jobs = [manual_path, small_path, manual_path, small_path]

        def _worker(job_index: int) -> tuple[str, _Snapshot]:
            path = jobs[job_index]
            workflow = _fresh_workflow_for(path)
            graph = _parse_once(
                workflow,
                file_path=path,
                document_id=f"doc_fresh_{trial_index}_{job_index}",
            )
            marker = f"FRESHMANUAL{trial_index}" if path == manual_path else (
                f"FRESHSMALL{trial_index}"
            )
            return path, _snapshot(graph, expected_marker=marker)

        with ThreadPoolExecutor(max_workers=len(jobs)) as executor:
            for path, snapshot in executor.map(_worker, range(len(jobs))):
                baseline = baselines[path]
                if snapshot != baseline:
                    diverging += 1
                    details.append(
                        f"trial={trial_index} path={path} "
                        f"baseline={baseline} got={snapshot}"
                    )

    total = trials * 4
    assert diverging == 0, (
        f"{diverging}/{total} fresh-runtime-per-call concurrent parses "
        f"diverged from the sequential baseline (this control group is "
        f"expected to always pass). First divergence: "
        f"{details[0] if details else 'n/a'}"
    )


# ---------------------------------------------------------------------------
# Deterministic proof: forces the exact interleaving that used to make
# SectionChunkBuilder.last_structural_profile_inference (a shared instance
# attribute set mid-call and read by the caller only after the whole call
# returns) leak one document's structural-profile inference into another
# document's graph metadata. That attribute no longer exists -
# build_document_chunk_payloads() now returns a SectionChunkBuildResult
# (payloads + structural_inference bundled explicitly) instead of stashing
# the inference on self. This test still forces the same interleaving (the
# SMALL document's call is made to complete strictly *between* the MANUAL
# thread's own call and the point its caller would previously have read the
# shared attribute) and proves the MANUAL thread's result is now correct
# regardless - not probabilistic, this either holds every time or the
# underlying code has regressed back to the old anti-pattern.
# ---------------------------------------------------------------------------


def test_shared_section_chunk_builder_does_not_leak_structural_profile_inference_across_threads() -> (
    None
):
    manual_raw, manual_pages = _build_manual_like_raw_document(
        marker="DETMANUAL", section_count=24
    )
    small_raw, small_pages = _build_small_raw_document(marker="DETSMALL", section_count=3)
    manual_path = "data/input/det_manual.pdf"
    small_path = "data/input/det_small.pdf"

    parser = _RoutingParser(
        {
            manual_path: _FakeParser(manual_raw, page_count=manual_pages),
            small_path: _FakeParser(small_raw, page_count=small_pages),
        }
    )
    workflow, document_graph_builder = _build_workflow(parser)
    section_chunk_builder = document_graph_builder.section_chunk_builder

    baseline_manual_graph = _parse_once(
        workflow, file_path=manual_path, document_id="doc_det_manual_baseline"
    )
    baseline_section_count = (
        baseline_manual_graph.document.metadata["structural_profile_inference"]["features"]["section_count"]
    )

    # Force: the SMALL document's build_document_chunk_payloads() call
    # completes strictly *between* the MANUAL thread's own call and the
    # point its caller (GraphChunkBuilder.build_chunks) consumes the
    # result - the exact window where the old shared last_structural_
    # profile_inference attribute used to get clobbered.
    real_build = type(section_chunk_builder).build_document_chunk_payloads
    manual_thread_reached_write = threading.Event()
    small_thread_finished = threading.Event()

    def _patched_build_document_chunk_payloads(self, *args, **kwargs):
        document_title = kwargs.get("document_title") or ""
        is_manual = "manual" in document_title.lower()
        if is_manual:
            result = real_build(self, *args, **kwargs)
            manual_thread_reached_write.set()
            # Give the SMALL thread its full window to run and (under the
            # old code) overwrite self.last_structural_profile_inference
            # before this thread's caller consumed it.
            small_thread_finished.wait(timeout=5)
            return result
        manual_thread_reached_write.wait(timeout=5)
        result = real_build(self, *args, **kwargs)
        small_thread_finished.set()
        return result

    section_chunk_builder.__class__.build_document_chunk_payloads = (
        _patched_build_document_chunk_payloads
    )
    try:
        results: dict[str, DocumentGraph] = {}

        def _parse_manual() -> None:
            results["manual"] = _parse_once(
                workflow, file_path=manual_path, document_id="doc_det_manual_race"
            )

        def _parse_small() -> None:
            results["small"] = _parse_once(
                workflow, file_path=small_path, document_id="doc_det_small_race"
            )

        manual_thread = threading.Thread(target=_parse_manual)
        small_thread = threading.Thread(target=_parse_small)
        manual_thread.start()
        small_thread.start()
        manual_thread.join(timeout=10)
        small_thread.join(timeout=10)
    finally:
        section_chunk_builder.__class__.build_document_chunk_payloads = real_build

    assert "manual" in results and "small" in results, (
        "Race harness did not complete both threads within the timeout - "
        "re-run; this indicates a harness issue, not evidence either way."
    )

    assert not hasattr(section_chunk_builder, "last_structural_profile_inference")
    assert not hasattr(document_graph_builder.chunk_builder, "last_structural_profile_inference")

    manual_inference = results["manual"].document.metadata.get(
        "structural_profile_inference"
    )
    assert manual_inference is not None
    manual_section_count_seen = manual_inference["features"]["section_count"]

    assert manual_section_count_seen == baseline_section_count, (
        "The MANUAL document's own graph metadata should report its OWN "
        f"structural_profile_inference (section_count={baseline_section_count}), "
        f"but under this forced interleaving it recorded "
        f"section_count={manual_section_count_seen} instead - the "
        "concurrently-parsed SMALL document's inference leaked in, meaning "
        "the shared-instance race has regressed."
    )
