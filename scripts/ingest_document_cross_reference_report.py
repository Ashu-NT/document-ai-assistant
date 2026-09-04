from __future__ import annotations

"""
Ingest one PDF through the production parsing path (Docling conversion ->
canonical normalization -> document graph build, including the PDF-native
link extractor and fuzzy/native cross-reference reconciliation when
enabled) and write a Markdown report covering the resulting DocumentGraph
in human-readable form plus every cross-reference/reconciliation metric
needed for corpus verification (see
outputs/architecture/pdf_link_cross_reference_plan.md).

Does not persist anything to a database and does not run embedding -
neither is needed to inspect the parsing/cross-reference path, and this
keeps the script side-effect-free (nothing written outside the one report
file). Classification/extraction/question-generation are not invoked
either; they are separate downstream stages that don't affect chunking or
cross-references, and are commonly disabled locally anyway since they
require a local LLM (Ollama).

Usage:
    python scripts/ingest_document_cross_reference_report.py --input <pdf>
        [--output <md>] [--full-dump] [--disable-pdf-links] [--disable-fuzzy]
"""

import argparse
import hashlib
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
for _import_root in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    _text = str(_import_root)
    if _text not in sys.path:
        sys.path.insert(0, _text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the production parsing path for one PDF (no classification/"
            "extraction/embedding/question-generation, no DB writes - no "
            "LLM calls and no side effects outside the one report file) and "
            "write a Markdown report of the resulting DocumentGraph plus "
            "PDF-native/fuzzy cross-reference reconciliation metrics."
        )
    )
    parser.add_argument("--input", required=True, help="Path to the input PDF.")
    parser.add_argument(
        "--output",
        help=(
            "Optional output Markdown path. Defaults to "
            "outputs/debug_parsing/<stem>_cross_reference_report.md"
        ),
    )
    parser.add_argument(
        "--disable-pdf-links",
        action="store_true",
        help="Disable the PDF-native link extractor/linker for this run.",
    )
    parser.add_argument(
        "--disable-fuzzy",
        action="store_true",
        help="Disable the fuzzy (text-based) cross-reference detector/linker for this run.",
    )
    parser.add_argument(
        "--full-dump",
        action="store_true",
        help=(
            "Include the full human-readable DocumentGraph dump (all "
            "sections, elements, table/picture assets, and every chunk's "
            "full content with its outgoing cross-references) in addition "
            "to the summary/metrics sections. Can produce a very large file "
            "for big documents."
        ),
    )
    return parser.parse_args()


_args = parse_args()

# Must happen before any `from src...` import: settings are pydantic
# BaseSettings singletons instantiated at module-import time, so an env var
# set after that point has no effect. A real process env var here takes
# precedence over whatever .env has, per pydantic-settings' own precedence.
os.environ.setdefault(
    "CHUNK_CROSS_REFERENCE_PDF_LINKS_ENABLED",
    "false" if _args.disable_pdf_links else "true",
)
os.environ.setdefault(
    "CHUNK_CROSS_REFERENCE_DETECTION_ENABLED",
    "false" if _args.disable_fuzzy else "true",
)

from src.application.orchestrator.ingestion.parsing_runtime_builder import (  # noqa: E402
    build_parsing_runtime,
)
from src.bootstrap.startup import bootstrap_application  # noqa: E402
from src.config.paths import ensure_directory  # noqa: E402
from src.config.settings import chunking_settings  # noqa: E402
from src.domain.document.entities import ChunkCrossReferenceType  # noqa: E402
from src.shared.ids import IdGenerator, IdPrefix  # noqa: E402


def print_status(message: str) -> None:
    print(f"[cross-reference-report] {message}", flush=True)


def format_elapsed_seconds(elapsed_seconds: float) -> str:
    if elapsed_seconds < 1:
        return f"{elapsed_seconds:.2f}s"
    if elapsed_seconds < 60:
        return f"{elapsed_seconds:.1f}s"
    minutes, seconds = divmod(elapsed_seconds, 60.0)
    if minutes < 60:
        return f"{int(minutes)}m {seconds:.1f}s"
    hours, minutes = divmod(minutes, 60.0)
    return f"{int(hours)}h {int(minutes)}m {seconds:.1f}s"


def resolve_input_path(value: str) -> Path:
    input_path = Path(value).expanduser().resolve()
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    return input_path


def resolve_output_path(input_path: Path, value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    return (
        PROJECT_ROOT / "outputs" / "debug_parsing" / f"{input_path.stem}_cross_reference_report.md"
    ).resolve()


def compute_hashes(file_path: Path) -> tuple[str, str]:
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    file_hash = digest.hexdigest()
    return file_hash, file_hash


def preview_text(value: Any, limit: int = 160) -> str:
    if value is None:
        return ""
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return f"{text[: max(0, limit - 3)].rstrip()}..."


def format_table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return "_No rows._"

    def _cell(value: Any) -> str:
        text = preview_text(value, limit=200) if value is not None else ""
        return text.replace("|", "\\|")

    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    body_rows = ["| " + " | ".join(_cell(v) for v in row) + " |" for row in rows]
    return "\n".join([header_row, separator_row, *body_rows])


def _display(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)


def _page_range(source: Any) -> str:
    page_start = getattr(source, "page_start", None)
    page_end = getattr(source, "page_end", None)
    if page_start is None and page_end is None:
        return "unknown"
    if page_start == page_end:
        return str(page_start)
    return f"{page_start} -> {page_end}"


def main() -> int:
    input_path = resolve_input_path(_args.input)
    output_path = resolve_output_path(input_path, _args.output)
    ensure_directory(output_path.parent)
    bootstrap_application()

    print_status(f"Input: {input_path}")
    print_status(f"Output report: {output_path}")
    print_status(
        "Cross-reference flags: "
        f"pdf_links_enabled={chunking_settings.pdf_link_cross_reference_enabled}, "
        f"fuzzy_enabled={chunking_settings.chunk_cross_reference_detection_enabled}"
    )

    id_generator = IdGenerator()
    document_id = id_generator.new_id(IdPrefix.DOCUMENT)
    file_hash, content_hash = compute_hashes(input_path)

    parsing_workflow, document_graph_builder = build_parsing_runtime(
        id_generator=id_generator
    )

    print_status("Starting ParsingWorkflow.parse() (Docling conversion can take a while)...")
    started_at = time.perf_counter()
    result = parsing_workflow.parse(
        file_path=str(input_path),
        file_hash=file_hash,
        content_hash=content_hash,
        document_id=document_id,
        progress_callback=print_status,
    )
    elapsed_seconds = time.perf_counter() - started_at
    print_status(
        f"ParsingWorkflow.parse() completed in {format_elapsed_seconds(elapsed_seconds)}."
    )

    document_graph = result.document_graph
    extraction_result = parsing_workflow.last_pdf_link_extraction_result
    linking_outcome = document_graph_builder.last_cross_reference_linking_outcome

    report = build_report(
        input_path=input_path,
        output_path=output_path,
        elapsed_seconds=elapsed_seconds,
        stage_durations=result.stage_durations,
        page_count=result.page_count,
        document_graph=document_graph,
        extraction_result=extraction_result,
        linking_outcome=linking_outcome,
        full_dump=_args.full_dump,
    )
    output_path.write_text(report, encoding="utf-8")

    print_status(f"Report written to {output_path}")
    print(str(output_path))
    return 0


def build_report(
    *,
    input_path: Path,
    output_path: Path,
    elapsed_seconds: float,
    stage_durations: dict[str, float],
    page_count: int | None,
    document_graph: Any,
    extraction_result: Any,
    linking_outcome: Any,
    full_dump: bool,
) -> str:
    lines: list[str] = ["# Cross-Reference Ingestion Report", ""]

    # Statistics first - this is what corpus verification is actually
    # checking; run config and the (potentially huge) full graph dump are
    # supporting detail and belong further down.
    lines.extend(
        [
            "## Document Graph Summary",
            f"- page count: `{page_count}`",
            f"- section count: `{len(document_graph.sections)}`",
            f"- element count: `{len(document_graph.elements)}`",
            f"- chunk count: `{len(document_graph.chunks)}`",
            f"- table asset count: `{len(document_graph.tables)}`",
            f"- picture asset count: `{len(document_graph.pictures)}`",
            "",
        ]
    )
    lines.extend(build_extraction_section(extraction_result))
    lines.extend(build_native_linker_section(linking_outcome))
    lines.extend(build_fuzzy_section(document_graph, linking_outcome))
    lines.extend(build_reconciliation_section(linking_outcome))
    lines.extend(build_graph_totals_section(document_graph))
    lines.extend(build_representative_cases_section(document_graph))

    lines.extend(
        [
            "## Run Configuration",
            f"- input: `{input_path}`",
            f"- output report: `{output_path}`",
            f"- document id: `{document_graph.document.document_id}`",
            f"- CHUNK_CROSS_REFERENCE_PDF_LINKS_ENABLED: `{chunking_settings.pdf_link_cross_reference_enabled}`",
            f"- CHUNK_CROSS_REFERENCE_DETECTION_ENABLED: `{chunking_settings.chunk_cross_reference_detection_enabled}`",
            f"- total parse duration: `{format_elapsed_seconds(elapsed_seconds)}`",
            f"- stage durations: `{stage_durations}`",
            "- note: nothing was persisted to a database and no embedding "
            "was run - all counts above are computed directly from the "
            "in-memory DocumentGraph, which is exactly what DocumentWriter "
            "would map 1:1 to DB rows.",
            "",
        ]
    )

    if full_dump:
        lines.extend(build_sections_section(document_graph))
        lines.extend(build_elements_section(document_graph))
        lines.extend(build_table_assets_section(document_graph))
        lines.extend(build_picture_assets_section(document_graph))
        lines.extend(build_full_chunk_dump_section(document_graph))
    else:
        lines.extend(build_chunk_summary_section(document_graph))

    return "\n".join(lines)


def build_extraction_section(extraction_result: Any) -> list[str]:
    lines = ["## PDF-Native Link Extraction", ""]
    if extraction_result is None:
        lines.append("_PDF link extraction did not run (extractor not enabled)._")
        lines.append("")
        return lines

    kind_counts = Counter(a.link_kind for a in extraction_result.annotations)
    lines.extend(
        [
            f"- status: `{extraction_result.status}`",
            f"- error message: `{extraction_result.error_message or ''}`",
            f"- total annotations extracted: `{len(extraction_result.annotations)}`",
            f"- direct_destination: `{kind_counts.get('direct_destination', 0)}`",
            f"- goto (PDFACTION_GOTO): `{kind_counts.get('goto', 0)}`",
            f"- non_internal_links_excluded: `{extraction_result.non_internal_links_excluded}`",
            f"- invalid_destinations_skipped: `{extraction_result.invalid_destinations_skipped}`",
            f"- page-level failures: `{len(extraction_result.page_failures)}`",
            "",
        ]
    )
    if extraction_result.page_failures:
        lines.append("### Page Failures")
        lines.append(
            format_table(
                headers=["page_number", "error_message"],
                rows=[
                    [f.page_number, f.error_message]
                    for f in extraction_result.page_failures
                ],
            )
        )
        lines.append("")
    return lines


def build_native_linker_section(linking_outcome: Any) -> list[str]:
    lines = ["## Native Linker Results (page/chunk resolution)", ""]
    if linking_outcome is None or linking_outcome.native_diagnostics is None:
        lines.append("_Native linker did not run (pdf-link linker not enabled)._")
        lines.append("")
        return lines

    diagnostics = linking_outcome.native_diagnostics
    uniquely_resolved = sum(
        1
        for e in linking_outcome.evidence
        if e.reference_type == ChunkCrossReferenceType.PDF_LINK_REFERENCE
    )
    lines.extend(
        [
            f"- uniquely resolved (source+dest each match exactly one chunk): `{uniquely_resolved}`",
            f"- ambiguous (skipped, no tie-break): `{diagnostics.ambiguous_count}`",
            f"- unresolved (no covering chunk on one/both sides): `{diagnostics.unresolved_count}`",
            f"- self-reference (skipped): `{diagnostics.self_reference_count}`",
            f"- duplicate pairs collapsed: `{diagnostics.duplicate_count}`",
            "",
        ]
    )
    return lines


def build_fuzzy_section(document_graph: Any, linking_outcome: Any) -> list[str]:
    lines = ["## Fuzzy Cross-Reference Counts", ""]

    detection_counts: Counter[str] = Counter()
    if linking_outcome is not None:
        for evidence in linking_outcome.evidence:
            if evidence.reference_type != ChunkCrossReferenceType.PDF_LINK_REFERENCE:
                detection_counts[evidence.reference_type.value] += 1

    canonical_counts: Counter[str] = Counter(
        xref.reference_type.value for xref in document_graph.cross_references.values()
    )

    lines.extend(
        [
            "- fuzzy detections found (evidence-level, PAGE_REFERENCE/SECTION_REFERENCE - "
            "includes those later overridden/conflicted/unreconciled by reconciliation):",
            f"  - page_reference: `{detection_counts.get('page_reference', 0)}`",
            f"  - section_reference: `{detection_counts.get('section_reference', 0)}`",
            "- canonical rows by reference_type (post-reconciliation, what retrieval actually sees):",
            f"  - page_reference: `{canonical_counts.get('page_reference', 0)}`",
            f"  - section_reference: `{canonical_counts.get('section_reference', 0)}`",
            f"  - table_reference: `{canonical_counts.get('table_reference', 0)}`",
            f"  - figure_reference: `{canonical_counts.get('figure_reference', 0)}`",
            f"  - pdf_link_reference: `{canonical_counts.get('pdf_link_reference', 0)}`",
            "",
        ]
    )
    return lines


def build_reconciliation_section(linking_outcome: Any) -> list[str]:
    lines = ["## Reconciliation Counts", ""]
    if linking_outcome is None:
        lines.append("_Reconciliation did not run (no cross-reference pipeline enabled)._")
        lines.append("")
        return lines

    diagnostics = linking_outcome.reconciliation_diagnostics
    lines.extend(
        [
            f"- SINGLE_SOURCE: `{diagnostics.single_source_count}`",
            f"- CONFIRMED: `{diagnostics.confirmed_count}`",
            f"- ACCEPTED_TEXTUAL: `{diagnostics.accepted_textual_count}`",
            f"- ACCEPTED_NATIVE: `{diagnostics.accepted_native_count}`",
            f"- CONFLICT: `{diagnostics.conflict_count}`",
            f"- UNRECONCILED_MULTI_CANDIDATE: `{diagnostics.unreconciled_multi_candidate_chunks}`",
            "",
        ]
    )
    return lines


def build_graph_totals_section(document_graph: Any) -> list[str]:
    lines = ["## Graph Totals (not persisted - see note above)", ""]
    cross_references = list(document_graph.cross_references.values())
    evidence = list(document_graph.cross_reference_evidence.values())
    outcome_counts = Counter(
        (xref.reconciliation_outcome.value if xref.reconciliation_outcome else "(none)")
        for xref in cross_references
    )
    lines.extend(
        [
            f"- total CrossReferenceEvidence rows: `{len(evidence)}`",
            f"- total canonical ChunkCrossReference rows: `{len(cross_references)}`",
            "- canonical rows by reconciliation_outcome:",
            *[f"  - {outcome}: `{count}`" for outcome, count in sorted(outcome_counts.items())],
            "",
        ]
    )
    return lines


def build_representative_cases_section(document_graph: Any) -> list[str]:
    lines = ["## Representative Cases", ""]
    cross_references = list(document_graph.cross_references.values())
    evidence = list(document_graph.cross_reference_evidence.values())
    chunks_by_id = document_graph.chunks

    lines.append("### One PDF-Native Link: destination vs. resolved target chunk")
    native_row = next(
        (x for x in cross_references if x.reference_type == ChunkCrossReferenceType.PDF_LINK_REFERENCE),
        None,
    )
    if native_row is None:
        lines.append("_No PDF_LINK_REFERENCE canonical row present._")
    else:
        target_chunk = chunks_by_id.get(native_row.target_chunk_id or "")
        target_source = getattr(target_chunk, "source", None)
        lines.extend(
            [
                f"- cross_reference_id: `{native_row.cross_reference_id}`",
                f"- source_chunk_id: `{native_row.source_chunk_id}`",
                f"- target_page (resolved dest page): `{native_row.target_page}`",
                f"- target_chunk_id: `{native_row.target_chunk_id}`",
                f"- target chunk page_start/page_end: `{getattr(target_source, 'page_start', None)}/{getattr(target_source, 'page_end', None)}`",
                "- MANUAL CHECK: does target_page fall within [page_start, page_end] above?",
                f"- target chunk content preview: `{preview_text(getattr(target_chunk, 'content', ''), 240)}`",
                f"- link_provenance: `{native_row.link_provenance}`",
            ]
        )
    lines.append("")

    lines.append("### One CONFIRMED Case")
    confirmed_row = next(
        (
            x for x in cross_references
            if x.reconciliation_outcome is not None
            and x.reconciliation_outcome.value == "confirmed"
        ),
        None,
    )
    if confirmed_row is None:
        lines.append("_No CONFIRMED canonical row present._")
    else:
        same_pair_count = sum(
            1
            for x in cross_references
            if x.source_chunk_id == confirmed_row.source_chunk_id
            and x.target_chunk_id == confirmed_row.target_chunk_id
        )
        backing_evidence = [
            e for e in evidence if e.canonical_cross_reference_id == confirmed_row.cross_reference_id
        ]
        lines.extend(
            [
                f"- canonical cross_reference_id: `{confirmed_row.cross_reference_id}`",
                f"- reference_type (winning shape): `{_display(confirmed_row.reference_type)}`",
                f"- source_chunk_id -> target_chunk_id: `{confirmed_row.source_chunk_id}` -> `{confirmed_row.target_chunk_id}`",
                f"- canonical rows sharing this exact (source, target) pair: `{same_pair_count}` (must be 1)",
                f"- backing evidence row count: `{len(backing_evidence)}` (expected 2: one fuzzy, one native)",
                format_table(
                    headers=["evidence_id", "reference_type", "matched_text", "resolution_status"],
                    rows=[
                        [
                            e.evidence_id,
                            _display(e.reference_type),
                            e.matched_text,
                            _display(e.resolution_status),
                        ]
                        for e in backing_evidence
                    ],
                ),
            ]
        )
    lines.append("")

    lines.append("### CONFLICT Case (if present)")
    conflict_evidence = [
        e for e in evidence
        if e.reconciliation_outcome is not None and e.reconciliation_outcome.value == "conflict"
    ]
    if not conflict_evidence:
        lines.append("_No CONFLICT evidence rows present._")
    else:
        by_group: dict[str, list[Any]] = defaultdict(list)
        for e in conflict_evidence:
            by_group[e.reconciliation_group_id or ""].append(e)
        group_id, members = next(iter(by_group.items()))
        lines.append(f"- reconciliation_group_id: `{group_id}`")
        lines.append(
            format_table(
                headers=["evidence_id", "reference_type", "matched_text", "target_chunk_id", "confidence_score"],
                rows=[
                    [e.evidence_id, _display(e.reference_type), e.matched_text, e.target_chunk_id, e.confidence_score]
                    for e in members
                ],
            )
        )
        lines.append(
            f"- total distinct CONFLICT groups found: `{len(by_group)}` "
            "(each group = one fuzzy PAGE_REFERENCE vs. one native link disagreeing, neither trusted)"
        )
    lines.append("")

    lines.append("### UNRECONCILED_MULTI_CANDIDATE Case (if present)")
    multi_evidence = [
        e for e in evidence
        if e.reconciliation_outcome is not None
        and e.reconciliation_outcome.value == "unreconciled_multi_candidate"
    ]
    if not multi_evidence:
        lines.append("_No UNRECONCILED_MULTI_CANDIDATE evidence rows present._")
    else:
        by_group = defaultdict(list)
        for e in multi_evidence:
            by_group[e.reconciliation_group_id or ""].append(e)
        group_id, members = next(iter(by_group.items()))
        lines.append(f"- reconciliation_group_id: `{group_id}`")
        lines.append(
            format_table(
                headers=["evidence_id", "reference_type", "matched_text", "target_chunk_id"],
                rows=[
                    [e.evidence_id, _display(e.reference_type), e.matched_text, e.target_chunk_id]
                    for e in members
                ],
            )
        )
        lines.append(f"- total distinct UNRECONCILED_MULTI_CANDIDATE groups found: `{len(by_group)}`")
    lines.append("")

    return lines


def build_chunk_summary_section(document_graph: Any) -> list[str]:
    lines = ["## Chunk Summary (first 30 - pass --full-dump for every chunk's full content)", ""]
    chunks = sorted(
        document_graph.chunks.values(), key=lambda c: c.sequence_number or 0
    )
    lines.append(
        format_table(
            headers=["sequence", "chunk_id", "pages", "type", "content preview"],
            rows=[
                [
                    c.sequence_number,
                    c.chunk_id,
                    _page_range(c.source),
                    _display(c.chunk_type),
                    preview_text(c.content, 120),
                ]
                for c in chunks[:30]
            ],
        )
    )
    lines.append("")
    return lines


def build_sections_section(document_graph: Any) -> list[str]:
    lines = ["## Sections (full)", ""]
    sections = sorted(
        document_graph.sections.values(),
        key=lambda s: (s.sequence_number or 0, s.title or ""),
    )
    if not sections:
        lines.append("_No sections._")
        lines.append("")
        return lines

    for section in sections:
        lines.extend(
            [
                f"### {section.section_id}",
                f"- title: `{section.title}`",
                f"- level: `{section.level}`",
                f"- parent_section_id: `{section.parent_section_id or ''}`",
                f"- section_path: `{' > '.join(section.section_path) if section.section_path else ''}`",
                f"- page range: `{_page_range(section.source)}`",
                f"- element_ids ({len(section.element_ids)}): `{', '.join(section.element_ids[:15])}"
                f"{' ...' if len(section.element_ids) > 15 else ''}`",
                "",
            ]
        )
    return lines


def build_elements_section(document_graph: Any) -> list[str]:
    lines = ["## Elements (full)", ""]
    elements = sorted(
        document_graph.elements.values(), key=lambda e: e.reading_order or 0
    )
    if not elements:
        lines.append("_No elements._")
        lines.append("")
        return lines

    lines.append(
        format_table(
            headers=["order", "element_id", "type", "section_id", "pages", "text preview"],
            rows=[
                [
                    e.reading_order,
                    e.element_id,
                    _display(e.element_type),
                    e.parent_section_id or "",
                    _page_range(e.source),
                    preview_text(e.text, 160),
                ]
                for e in elements
            ],
        )
    )
    lines.append("")
    return lines


def build_table_assets_section(document_graph: Any) -> list[str]:
    lines = ["## Table Assets (full)", ""]
    if not document_graph.tables:
        lines.append("_No table assets._")
        lines.append("")
        return lines

    for table in document_graph.tables.values():
        lines.extend(
            [
                f"### {table.table_id}",
                f"- parent_section_id: `{table.parent_section_id or ''}`",
                f"- page range: `{_page_range(table.metadata.source)}`",
                f"- caption: `{table.metadata.caption or ''}`",
                f"- row_count/column_count: `{table.row_count}/{table.column_count}`",
                "- markdown:",
                "```text",
                (table.markdown or "").replace("```", "'''"),
                "```",
                "",
            ]
        )
    return lines


def build_picture_assets_section(document_graph: Any) -> list[str]:
    lines = ["## Picture Assets (full)", ""]
    if not document_graph.pictures:
        lines.append("_No picture assets._")
        lines.append("")
        return lines

    for picture in document_graph.pictures.values():
        lines.extend(
            [
                f"### {picture.picture_id}",
                f"- parent_section_id: `{picture.parent_section_id or ''}`",
                f"- page range: `{_page_range(picture.metadata.source)}`",
                f"- caption: `{picture.metadata.caption or ''}`",
                f"- image_path: `{picture.image_path or ''}`",
                f"- ocr_text preview: `{preview_text(picture.ocr_text, 200)}`",
                "",
            ]
        )
    return lines


def build_full_chunk_dump_section(document_graph: Any) -> list[str]:
    lines = ["## Chunks (full content + outgoing cross-references)", ""]
    chunks = sorted(
        document_graph.chunks.values(), key=lambda c: c.sequence_number or 0
    )
    if not chunks:
        lines.append("_No chunks._")
        lines.append("")
        return lines

    for chunk in chunks:
        outgoing = document_graph.get_chunk_cross_references(chunk.chunk_id)
        lines.extend(
            [
                f"### {chunk.chunk_id} (sequence {chunk.sequence_number})",
                f"- section_id: `{chunk.section_id or ''}`",
                f"- section_path: `{' > '.join(chunk.section_path) if chunk.section_path else ''}`",
                f"- page range: `{_page_range(chunk.source)}`",
                f"- chunk_type: `{_display(chunk.chunk_type)}`",
                f"- table_ids: `{', '.join(chunk.table_ids)}`",
                f"- picture_ids: `{', '.join(chunk.picture_ids)}`",
                "- content:",
                "```text",
                (chunk.content or "").replace("```", "'''"),
                "```",
            ]
        )
        if outgoing:
            lines.append(f"- outgoing cross-references ({len(outgoing)}):")
            lines.append(
                format_table(
                    headers=[
                        "reference_type",
                        "target_chunk_id",
                        "target_page",
                        "resolution_status",
                        "reconciliation_outcome",
                        "matched_text",
                    ],
                    rows=[
                        [
                            _display(xref.reference_type),
                            xref.target_chunk_id or "",
                            xref.target_page if xref.target_page is not None else "",
                            _display(xref.resolution_status),
                            _display(xref.reconciliation_outcome),
                            xref.matched_text,
                        ]
                        for xref in outgoing
                    ],
                )
            )
        else:
            lines.append("- outgoing cross-references: none")
        lines.append("")

    return lines


if __name__ == "__main__":
    raise SystemExit(main())
