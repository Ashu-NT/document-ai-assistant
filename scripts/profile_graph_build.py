from __future__ import annotations

import argparse
import cProfile
import pstats
import sys
import tracemalloc
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for import_root in (PROJECT_ROOT, SRC_ROOT):
    import_root_text = str(import_root)
    if import_root_text not in sys.path:
        sys.path.insert(0, import_root_text)

from src.application.workflows.parsing.builders.document_graph_builder import (
    DocumentGraphBuilder,
)
from src.application.workflows.parsing.builders.section_builder import SectionBuilder
from src.application.workflows.parsing.normalizers.docling_document_normalizer import (
    DoclingDocumentNormalizer,
)
from src.application.workflows.parsing.profiling import (
    GraphBuildProfiler,
    GraphBuildReportWriter,
    build_graph_stage_catalog,
)
from src.domain.document import DocumentHashes
from src.infrastructure.parsing.docling.docling_parser import DoclingParser
from src.shared.ids import IdGenerator


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Profile the document graph build stage for a single document.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input PDF/document.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. Defaults to outputs/debug_graph_build/<input_stem>/",
    )
    parser.add_argument(
        "--baseline-graph-build-seconds",
        type=float,
        default=None,
        help="Optional baseline graph build duration for before/after comparison.",
    )
    parser.add_argument(
        "--top-functions",
        type=int,
        default=30,
        help="How many cProfile entries to keep per ranking table.",
    )
    return parser.parse_args()


def _emit(message: str) -> None:
    print(message, flush=True)


def _default_output_dir(input_path: Path) -> Path:
    return Path("outputs") / "debug_graph_build" / input_path.stem


def _format_function_name(filename: str, line_number: int, function_name: str) -> str:
    return f"{Path(filename).name}:{line_number}({function_name})"


def _profile_entries(
    profiler: cProfile.Profile,
    *,
    sort_key: str,
    limit: int,
) -> list[dict[str, object]]:
    stats = pstats.Stats(profiler).stats.items()
    entries = [
        {
            "calls": total_calls,
            "primitive_calls": primitive_calls,
            "total_seconds": total_seconds,
            "cumulative_seconds": cumulative_seconds,
            "function": _format_function_name(
                filename,
                line_number,
                function_name,
            )
            if filename
            else str(function_name),
            "recursive_calls": max(total_calls - primitive_calls, 0),
        }
        for (filename, line_number, function_name), (
            primitive_calls,
            total_calls,
            total_seconds,
            cumulative_seconds,
            _callers,
        ) in stats
    ]
    return sorted(
        entries,
        key=lambda entry: entry[sort_key],
        reverse=True,
    )[:limit]


def _write_profile_tables(
    output_dir: Path,
    *,
    prefix: str,
    cumulative_entries: list[dict[str, object]],
    call_count_entries: list[dict[str, object]],
    recursive_entries: list[dict[str, object]],
) -> None:
    def render(entries: list[dict[str, object]]) -> str:
        lines = [
            "calls | primitive_calls | cumulative_seconds | total_seconds | recursive_calls | function",
            "--- | --- | --- | --- | --- | ---",
        ]
        for entry in entries:
            lines.append(
                f"{entry['calls']} | "
                f"{entry['primitive_calls']} | "
                f"{entry['cumulative_seconds']:.6f} | "
                f"{entry['total_seconds']:.6f} | "
                f"{entry['recursive_calls']} | "
                f"{entry['function']}"
            )
        return "\n".join(lines) + "\n"

    (output_dir / f"{prefix}_top_cumulative.txt").write_text(
        render(cumulative_entries),
        encoding="utf-8",
    )
    (output_dir / f"{prefix}_top_call_count.txt").write_text(
        render(call_count_entries),
        encoding="utf-8",
    )
    (output_dir / f"{prefix}_top_recursive.txt").write_text(
        render(recursive_entries),
        encoding="utf-8",
    )


def _top_allocations(snapshot: tracemalloc.Snapshot, *, limit: int = 20) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for stat in snapshot.statistics("lineno")[:limit]:
        frame = stat.traceback[0]
        entries.append(
            {
                "trace": f"{frame.filename}:{frame.lineno}",
                "size_bytes": stat.size,
                "count": stat.count,
            }
        )
    return entries


def _profile_operation(
    *,
    label: str,
    operation,
    output_dir: Path,
    output_prefix: str,
    top_functions: int,
) -> tuple[object, dict[str, object]]:
    profiler = cProfile.Profile()
    prof_path = output_dir / f"{output_prefix}.prof"
    _emit(f"[graph] Profiling {label}...")
    tracemalloc.start()
    profiler.enable()
    started_at = perf_counter()
    result = operation()
    elapsed_seconds = perf_counter() - started_at
    profiler.disable()
    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()
    profiler.dump_stats(str(prof_path))

    top_cumulative = _profile_entries(
        profiler,
        sort_key="cumulative_seconds",
        limit=top_functions,
    )
    top_call_count = _profile_entries(
        profiler,
        sort_key="calls",
        limit=top_functions,
    )
    top_recursive = _profile_entries(
        profiler,
        sort_key="recursive_calls",
        limit=top_functions,
    )
    _write_profile_tables(
        output_dir,
        prefix=output_prefix,
        cumulative_entries=top_cumulative,
        call_count_entries=top_call_count,
        recursive_entries=top_recursive,
    )
    return result, {
        "elapsed_seconds": elapsed_seconds,
        "cprofile": {
            "prof_path": str(prof_path),
            "top_cumulative": top_cumulative,
            "top_call_count": top_call_count,
            "top_recursive": top_recursive,
        },
        "memory": {
            "current_bytes": current_bytes,
            "peak_bytes": peak_bytes,
            "top_allocations": _top_allocations(snapshot),
        },
    }


def _ranked_bottlenecks(
    *,
    stage_metrics: list[dict[str, object]],
    graph_build_seconds: float,
) -> list[dict[str, object]]:
    catalog_by_name = {
        descriptor.name: descriptor
        for descriptor in build_graph_stage_catalog()
    }
    recommendations = {
        "section_builder.resolve_hierarchy": "Preserve the prefix-sum approach and avoid reintroducing header-pair full scans.",
        "section_chunk_builder.build_fragments": "Focus future work on structured window generation and repeated text normalization.",
        "section_chunk_builder.deduplicate_payloads": "Keep candidate indexing bucketed by section-path prefix and page overlap.",
        "section_chunk_builder.build_base_payloads": "Avoid repeated fragment token recounts or redundant content assembly.",
        "document_graph_builder.materialize_elements_assets": "If needed later, add local indexes rather than repeated graph scans.",
    }
    ranked_metrics = sorted(
        stage_metrics,
        key=lambda metric: float(metric["elapsed_seconds"]),
        reverse=True,
    )
    bottlenecks: list[dict[str, object]] = []
    for rank, metric in enumerate(ranked_metrics[:10], start=1):
        descriptor = catalog_by_name.get(str(metric["name"]))
        elapsed_seconds = float(metric["elapsed_seconds"])
        bottlenecks.append(
            {
                "rank": rank,
                "function": metric["name"],
                "complexity": (
                    descriptor.worst_case_complexity
                    if descriptor is not None
                    else "Unknown"
                ),
                "runtime_percent": (
                    (elapsed_seconds / graph_build_seconds) * 100.0
                    if graph_build_seconds > 0
                    else 0.0
                ),
                "evidence": (
                    f"elapsed={elapsed_seconds:.3f}s; "
                    f"inputs={metric['input_counts']}; "
                    f"outputs={metric['output_counts']}"
                ),
                "recommendation": recommendations.get(
                    str(metric["name"]),
                    "Monitor this stage on larger documents before optimizing further.",
                ),
            }
        )
    return bottlenecks


def main() -> int:
    args = _parse_args()
    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir) if args.output_dir else _default_output_dir(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    _emit(f"[graph] Input file: {input_path}")
    _emit(f"[graph] Output directory: {output_dir.resolve()}")

    parser = DoclingParser()
    normalizer = DoclingDocumentNormalizer()

    _emit("[graph] Running raw parse...")
    raw_started_at = perf_counter()
    raw_parsed_document = parser.parse(str(input_path))
    raw_parse_seconds = perf_counter() - raw_started_at
    _emit(
        "[graph] Raw parse completed "
        f"({raw_parse_seconds:.3f}s, pages={raw_parsed_document.page_count})."
    )

    _emit("[graph] Normalizing canonical elements...")
    normalize_started_at = perf_counter()
    canonical_elements = normalizer.normalize(
        raw_parsed_document,
        "doc_graph_profile",
    )
    normalize_seconds = perf_counter() - normalize_started_at
    _emit(
        "[graph] Normalization completed "
        f"({normalize_seconds:.3f}s, canonical_elements={len(canonical_elements)})."
    )

    _emit("[graph] Measuring unprofiled document graph build...")
    measurement_id_generator = IdGenerator()
    measurement_builder = DocumentGraphBuilder(
        id_generator=measurement_id_generator,
        section_builder=SectionBuilder(measurement_id_generator),
    )
    graph_started_at = perf_counter()
    measured_document_graph = measurement_builder.build(
        document_id="doc_graph_profile",
        file_path=str(input_path),
        hashes=DocumentHashes(
            file_hash="graph_profile",
            content_hash="graph_profile",
        ),
        canonical_elements=canonical_elements,
        raw_parsed_document=raw_parsed_document,
    )
    graph_build_seconds = perf_counter() - graph_started_at
    _emit(
        "[graph] Unprofiled graph build completed "
        f"({graph_build_seconds:.3f}s, sections={len(measured_document_graph.sections)}, "
        f"chunks={len(measured_document_graph.chunks)})."
    )

    profiler = cProfile.Profile()
    prof_path = output_dir / "graph_build.prof"
    graph_profiler = GraphBuildProfiler(progress_callback=_emit)
    profiled_id_generator = IdGenerator()
    profiled_builder = DocumentGraphBuilder(
        id_generator=profiled_id_generator,
        section_builder=SectionBuilder(profiled_id_generator),
        profiler=graph_profiler,
    )
    _emit("[graph] Profiling document graph build...")
    tracemalloc.start()
    profiler.enable()
    profiled_started_at = perf_counter()
    profiled_document_graph = profiled_builder.build(
        document_id="doc_graph_profile",
        file_path=str(input_path),
        hashes=DocumentHashes(
            file_hash="graph_profile",
            content_hash="graph_profile",
        ),
        canonical_elements=canonical_elements,
        raw_parsed_document=raw_parsed_document,
    )
    profiled_graph_build_seconds = perf_counter() - profiled_started_at
    profiler.disable()
    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()
    profiler.dump_stats(str(prof_path))
    _emit(
        "[graph] Profiled graph build completed "
        f"({profiled_graph_build_seconds:.3f}s, sections={len(profiled_document_graph.sections)}, "
        f"chunks={len(profiled_document_graph.chunks)})."
    )

    top_cumulative = _profile_entries(
        profiler,
        sort_key="cumulative_seconds",
        limit=args.top_functions,
    )
    top_call_count = _profile_entries(
        profiler,
        sort_key="calls",
        limit=args.top_functions,
    )
    top_recursive = _profile_entries(
        profiler,
        sort_key="recursive_calls",
        limit=args.top_functions,
    )
    _write_profile_tables(
        output_dir,
        cumulative_entries=top_cumulative,
        call_count_entries=top_call_count,
        recursive_entries=top_recursive,
    )

    baseline = args.baseline_graph_build_seconds
    improvement_percent = None
    if baseline is not None and baseline > 0:
        improvement_percent = ((baseline - graph_build_seconds) / baseline) * 100.0

    stage_metrics = [asdict(metric) for metric in graph_profiler.stage_metrics]
    report_data = {
        "input_document": {
            "file_path": str(input_path),
            "page_count": raw_parsed_document.page_count,
        },
        "counts": {
            "canonical_elements": len(canonical_elements),
            "sections": len(measured_document_graph.sections),
            "elements": len(measured_document_graph.elements),
            "chunks": len(measured_document_graph.chunks),
            "tables": len(measured_document_graph.tables),
            "pictures": len(measured_document_graph.pictures),
        },
        "timings": {
            "raw_parse_seconds": raw_parse_seconds,
            "normalize_seconds": normalize_seconds,
            "graph_build_seconds": graph_build_seconds,
            "profiled_graph_build_seconds": profiled_graph_build_seconds,
            "baseline_graph_build_seconds": baseline,
            "graph_build_improvement_percent": improvement_percent,
        },
        "stage_metrics": stage_metrics,
        "architecture_map": [
            asdict(descriptor)
            for descriptor in build_graph_stage_catalog()
        ],
        "ranked_bottlenecks": _ranked_bottlenecks(
            stage_metrics=stage_metrics,
            graph_build_seconds=profiled_graph_build_seconds,
        ),
        "cprofile": {
            "prof_path": str(prof_path),
            "top_cumulative": top_cumulative,
            "top_call_count": top_call_count,
            "top_recursive": top_recursive,
        },
        "memory": {
            "current_bytes": current_bytes,
            "peak_bytes": peak_bytes,
            "top_allocations": _top_allocations(snapshot),
        },
    }

    writer = GraphBuildReportWriter(output_dir)
    json_path, markdown_path = writer.write(report_data=report_data)
    _emit(f"[graph] JSON report: {json_path.resolve()}")
    _emit(f"[graph] Markdown report: {markdown_path.resolve()}")
    _emit(f"[graph] cProfile dump: {prof_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
