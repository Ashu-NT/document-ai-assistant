from __future__ import annotations

import argparse
import cProfile
import pstats
import sys
import tracemalloc
from dataclasses import asdict
from pathlib import Path
from threading import Event, Thread
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

_STAGE_HEARTBEAT_INTERVAL_SECONDS = 30.0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Profile the parsing pipeline stages for a single document.",
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


def _format_elapsed_seconds(elapsed_seconds: float) -> str:
    if elapsed_seconds < 1:
        return f"{elapsed_seconds:.2f}s"
    if elapsed_seconds < 60:
        return f"{elapsed_seconds:.1f}s"

    minutes, seconds = divmod(elapsed_seconds, 60.0)
    if minutes < 60:
        return f"{int(minutes)}m {seconds:.1f}s"

    hours, minutes = divmod(minutes, 60.0)
    return f"{int(hours)}h {int(minutes)}m {seconds:.1f}s"


class _StageHeartbeat:
    def __init__(
        self,
        *,
        label: str,
        interval_seconds: float = _STAGE_HEARTBEAT_INTERVAL_SECONDS,
    ) -> None:
        self.label = label
        self.interval_seconds = interval_seconds
        self._started_at = 0.0
        self._stop_event = Event()
        self._thread: Thread | None = None

    def start(self) -> None:
        if self._thread is not None:
            return

        self._started_at = perf_counter()
        self._thread = Thread(
            target=self._run,
            name="profile-graph-build-stage-heartbeat",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if self._thread is None:
            return

        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join(timeout=0.1)

    def _run(self) -> None:
        while not self._stop_event.wait(self.interval_seconds):
            elapsed_seconds = perf_counter() - self._started_at
            _emit(
                f"[graph] {self.label} still running... "
                f"({_format_elapsed_seconds(elapsed_seconds)} elapsed)"
            )


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
    start_message: str,
    heartbeat_label: str,
    failure_label: str,
    operation,
    output_dir: Path,
    output_prefix: str,
    top_functions: int,
) -> tuple[object, dict[str, object]]:
    profiler = cProfile.Profile()
    prof_path = output_dir / f"{output_prefix}.prof"
    _emit(start_message)
    started_at = perf_counter()
    heartbeat = _StageHeartbeat(label=heartbeat_label)
    tracemalloc.start()
    heartbeat.start()
    profiler.enable()
    try:
        result = operation()
    except Exception:
        elapsed_seconds = perf_counter() - started_at
        _emit(
            f"[graph] {failure_label} failed after "
            f"{_format_elapsed_seconds(elapsed_seconds)}."
        )
        raise
    finally:
        elapsed_seconds = perf_counter() - started_at
        profiler.disable()
        heartbeat.stop()
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
    _emit(
        f"[graph] {label} completed "
        f"({_format_elapsed_seconds(elapsed_seconds)})."
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


def _run_operation_with_heartbeat(
    *,
    start_message: str,
    heartbeat_label: str,
    failure_label: str,
    completion_message_builder,
    operation,
) -> tuple[object, float]:
    _emit(start_message)
    started_at = perf_counter()
    heartbeat = _StageHeartbeat(label=heartbeat_label)
    heartbeat.start()
    try:
        result = operation()
    except Exception:
        elapsed_seconds = perf_counter() - started_at
        _emit(
            f"[graph] {failure_label} failed after "
            f"{_format_elapsed_seconds(elapsed_seconds)}."
        )
        raise
    finally:
        heartbeat.stop()

    elapsed_seconds = perf_counter() - started_at
    _emit(completion_message_builder(result, elapsed_seconds))
    return result, elapsed_seconds


def main() -> int:
    args = _parse_args()
    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir) if args.output_dir else _default_output_dir(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    _emit(f"[graph] Input file: {input_path}")
    _emit(f"[graph] Output directory: {output_dir.resolve()}")

    parser = DoclingParser()
    normalizer = DoclingDocumentNormalizer()

    raw_parsed_document, docling_conversion_profile = _profile_operation(
        label="Docling conversion",
        start_message=(
            f"[graph] Docling conversion started for {input_path.name}. "
            "This can take a while for large or image-heavy PDFs."
        ),
        heartbeat_label=f"Docling conversion for {input_path.name}",
        failure_label=f"Docling conversion for {input_path.name}",
        operation=lambda: parser.parse(str(input_path)),
        output_dir=output_dir,
        output_prefix="docling_conversion",
        top_functions=args.top_functions,
    )

    canonical_elements, canonical_normalization_profile = _profile_operation(
        label="canonical normalization",
        start_message="[graph] Normalizing Docling output into canonical elements...",
        heartbeat_label="Canonical normalization",
        failure_label="Canonical normalization",
        operation=lambda: normalizer.normalize(
            raw_parsed_document,
            "doc_graph_profile",
        ),
        output_dir=output_dir,
        output_prefix="canonical_normalization",
        top_functions=args.top_functions,
    )

    measurement_id_generator = IdGenerator()
    measurement_builder = DocumentGraphBuilder(
        id_generator=measurement_id_generator,
        section_builder=SectionBuilder(measurement_id_generator),
    )
    measured_document_graph, graph_build_seconds = _run_operation_with_heartbeat(
        start_message=(
            "[graph] Measuring unprofiled document graph build from "
            f"{len(canonical_elements)} canonical element(s)..."
        ),
        heartbeat_label="Unprofiled document graph build",
        failure_label="Unprofiled document graph build",
        operation=lambda: measurement_builder.build(
            document_id="doc_graph_profile",
            file_path=str(input_path),
            hashes=DocumentHashes(
                file_hash="graph_profile",
                content_hash="graph_profile",
            ),
            canonical_elements=canonical_elements,
            raw_parsed_document=raw_parsed_document,
        ),
        completion_message_builder=lambda result, elapsed_seconds: (
            "[graph] Unprofiled graph build completed "
            f"({_format_elapsed_seconds(elapsed_seconds)}, "
            f"sections={len(result.sections)}, "
            f"chunks={len(result.chunks)})."
        ),
    )

    graph_profiler = GraphBuildProfiler(progress_callback=_emit)
    profiled_id_generator = IdGenerator()
    profiled_builder = DocumentGraphBuilder(
        id_generator=profiled_id_generator,
        section_builder=SectionBuilder(profiled_id_generator),
        profiler=graph_profiler,
    )
    profiled_document_graph, graph_build_profile = _profile_operation(
        label="document graph build",
        start_message=(
            "[graph] Profiling document graph build from "
            f"{len(canonical_elements)} canonical element(s)..."
        ),
        heartbeat_label="Profiled document graph build",
        failure_label="Profiled document graph build",
        operation=lambda: profiled_builder.build(
            document_id="doc_graph_profile",
            file_path=str(input_path),
            hashes=DocumentHashes(
                file_hash="graph_profile",
                content_hash="graph_profile",
            ),
            canonical_elements=canonical_elements,
            raw_parsed_document=raw_parsed_document,
        ),
        output_dir=output_dir,
        output_prefix="graph_build",
        top_functions=args.top_functions,
    )
    profiled_graph_build_seconds = float(graph_build_profile["elapsed_seconds"])
    _emit(
        "[graph] Profiled graph build counts "
        f"(sections={len(profiled_document_graph.sections)}, "
        f"chunks={len(profiled_document_graph.chunks)})."
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
            "docling_conversion_seconds": docling_conversion_profile["elapsed_seconds"],
            "raw_parse_seconds": docling_conversion_profile["elapsed_seconds"],
            "canonical_normalization_seconds": canonical_normalization_profile["elapsed_seconds"],
            "normalize_seconds": canonical_normalization_profile["elapsed_seconds"],
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
        "operation_profiles": {
            "docling_conversion": docling_conversion_profile,
            "canonical_normalization": canonical_normalization_profile,
            "graph_build": graph_build_profile,
        },
        "cprofile": graph_build_profile["cprofile"],
        "memory": graph_build_profile["memory"],
    }

    writer = GraphBuildReportWriter(output_dir)
    json_path, markdown_path = writer.write(report_data=report_data)
    _emit(f"[graph] JSON report: {json_path.resolve()}")
    _emit(f"[graph] Markdown report: {markdown_path.resolve()}")
    _emit(
        "[graph] cProfile dumps: "
        f"{Path(str(docling_conversion_profile['cprofile']['prof_path'])).resolve()}, "
        f"{Path(str(canonical_normalization_profile['cprofile']['prof_path'])).resolve()}, "
        f"{Path(str(graph_build_profile['cprofile']['prof_path'])).resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
