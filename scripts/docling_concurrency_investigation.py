"""Investigation-only harness: does the raw Docling conversion result for
one PDF become incomplete/corrupted when a second, independent OS process
is concurrently running its own Docling conversion of a *different* PDF?

Isolates strictly at `converter.convert(...)` -- the raw Docling result --
using the real production converter factory
(`src.infrastructure.parsing.docling.docling_converter_factory.build_docling_converter`,
same factory `DoclingParser`'s production subprocess path calls). Does NOT
touch canonical normalization, DocumentGraphBuilder, chunking,
DoclingGroupIndex, cross-reference processing, graph validation, or any
persistence layer.

Not a fix, not a lock, not a cache. Investigation artifacts only, written
under diagnostics/docling_concurrency/.

Usage:
    python scripts/docling_concurrency_investigation.py smoke
    python scripts/docling_concurrency_investigation.py baseline --repeats 3
    python scripts/docling_concurrency_investigation.py concurrent --trials 8
"""
from __future__ import annotations

import argparse
import json
import multiprocessing
import os
import sys
import time
import traceback
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
for _import_root in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    _text = str(_import_root)
    if _text not in sys.path:
        sys.path.insert(0, _text)

DIAGNOSTICS_ROOT = PROJECT_ROOT / "diagnostics" / "docling_concurrency"
BASELINE_DIR = DIAGNOSTICS_ROOT / "baselines"
RUNS_DIR = DIAGNOSTICS_ROOT

PDF_A = PROJECT_ROOT / "TestDoc" / "datasheet" / "30008_FLW-Boardwalk_TechnicalSpecification_Rev_0_6.pdf"
PDF_B = PROJECT_ROOT / "TestDoc" / "report" / "Antenna Measurement VSWR-Report MY  BOARDWALK.pdf"


# --------------------------------------------------------------------------
# Child-process worker: builds its OWN converter (production factory),
# converts, exports via Docling's own supported export_to_dict(), writes
# the full export to a scratch temp file (not crossed through the Queue --
# large/possibly image-bearing payloads), and returns a compact fingerprint
# + timing/resource info through the Queue.
# --------------------------------------------------------------------------

def _convert_worker(
    pdf_path: str,
    label: str,
    scratch_export_path: str,
    out_queue: "multiprocessing.Queue[dict[str, Any]]",
) -> None:
    import psutil

    from src.infrastructure.parsing.docling.docling_converter_factory import (
        build_docling_converter,
    )

    pid = os.getpid()
    start = time.monotonic()
    try:
        # No enable_ocr_override -- exactly what production's subprocess
        # worker (docling_conversion_worker.run_conversion_in_subprocess)
        # does, so this picks up the real environment-configured
        # docling_settings, not a simplified/overridden config.
        converter = build_docling_converter()
        result = converter.convert(pdf_path, raises_on_error=True)
        elapsed = time.monotonic() - start
        doc = getattr(result, "document", None)
        if doc is None:
            raise RuntimeError("Docling conversion returned no document.")

        doc_dict = doc.export_to_dict()
        with open(scratch_export_path, "w", encoding="utf-8") as handle:
            json.dump(doc_dict, handle)

        fingerprint = build_fingerprint(doc_dict)
        rss_bytes = psutil.Process(pid).memory_info().rss

        out_queue.put(
            {
                "label": label,
                "status": "ok",
                "pid": pid,
                "elapsed_seconds": elapsed,
                "rss_bytes": rss_bytes,
                "fingerprint": fingerprint,
                "scratch_export_path": scratch_export_path,
            }
        )
    except BaseException as exc:  # noqa: BLE001
        elapsed = time.monotonic() - start
        out_queue.put(
            {
                "label": label,
                "status": "error",
                "pid": pid,
                "elapsed_seconds": elapsed,
                "error": repr(exc),
                "traceback": traceback.format_exc(),
            }
        )


# --------------------------------------------------------------------------
# Structural fingerprint -- built from Docling's own export_to_dict() shape
# (verified against a real exported document.json earlier this session:
# top-level keys schema_name/version/name/origin/furniture/body/groups/
# texts/pictures/tables/key_value_items/form_items/pages).
# --------------------------------------------------------------------------

def build_fingerprint(doc_dict: dict[str, Any]) -> dict[str, Any]:
    pages = doc_dict.get("pages") or {}
    texts = doc_dict.get("texts") or []
    tables = doc_dict.get("tables") or []
    pictures = doc_dict.get("pictures") or []
    key_value_items = doc_dict.get("key_value_items") or []
    form_items = doc_dict.get("form_items") or []
    groups = doc_dict.get("groups") or []

    text_label_counts = Counter((t.get("label") or "") for t in texts)

    group_label_counts = Counter((g.get("label") or "") for g in groups)
    group_children = [
        {
            "self_ref": group.get("self_ref"),
            "label": group.get("label"),
            "name": group.get("name"),
            "child_refs": [
                (child.get("$ref") if isinstance(child, dict) else child)
                for child in (group.get("children") or [])
            ],
        }
        for group in groups
    ]

    def _page_no(item: dict[str, Any]) -> Any:
        prov = item.get("prov") or []
        if not prov:
            return None
        first = prov[0]
        return first.get("page_no") if isinstance(first, dict) else None

    text_provenance = [
        {"self_ref": t.get("self_ref"), "page_no": _page_no(t)} for t in texts
    ]

    return {
        "page_count": len(pages),
        "text_count": len(texts),
        "table_count": len(tables),
        "picture_count": len(pictures),
        "key_value_item_count": len(key_value_items),
        "form_item_count": len(form_items),
        "list_item_count": int(text_label_counts.get("list_item", 0)),
        "text_label_counts": dict(sorted(text_label_counts.items())),
        "group_count": len(groups),
        "group_label_counts": dict(sorted(group_label_counts.items())),
        "group_children": group_children,
        "text_order_refs": [t.get("self_ref") for t in texts],
        "table_order_refs": [t.get("self_ref") for t in tables],
        "picture_order_refs": [p.get("self_ref") for p in pictures],
        "text_provenance": text_provenance,
    }


@dataclass
class DiffResult:
    equivalent: bool
    first_difference: str | None
    differences: list[str] = field(default_factory=list)
    baseline_totals: dict[str, int] = field(default_factory=dict)
    concurrent_totals: dict[str, int] = field(default_factory=dict)
    size_ratio: dict[str, float] = field(default_factory=dict)


_COUNT_KEYS = (
    "page_count",
    "text_count",
    "table_count",
    "picture_count",
    "key_value_item_count",
    "form_item_count",
    "list_item_count",
    "group_count",
)


def diff_fingerprints(baseline: dict[str, Any], concurrent: dict[str, Any]) -> DiffResult:
    differences: list[str] = []
    first_difference: str | None = None

    def _note(msg: str) -> None:
        nonlocal first_difference
        differences.append(msg)
        if first_difference is None:
            first_difference = msg

    for key in _COUNT_KEYS:
        if baseline.get(key) != concurrent.get(key):
            _note(f"{key}: baseline={baseline.get(key)} concurrent={concurrent.get(key)}")

    if baseline.get("text_label_counts") != concurrent.get("text_label_counts"):
        _note(
            "text_label_counts differ: "
            f"baseline={baseline.get('text_label_counts')} "
            f"concurrent={concurrent.get('text_label_counts')}"
        )

    if baseline.get("group_label_counts") != concurrent.get("group_label_counts"):
        _note(
            "group_label_counts differ: "
            f"baseline={baseline.get('group_label_counts')} "
            f"concurrent={concurrent.get('group_label_counts')}"
        )

    baseline_groups = {g["self_ref"]: g for g in baseline.get("group_children", [])}
    concurrent_groups = {g["self_ref"]: g for g in concurrent.get("group_children", [])}
    missing_groups = set(baseline_groups) - set(concurrent_groups)
    extra_groups = set(concurrent_groups) - set(baseline_groups)
    if missing_groups:
        _note(f"groups missing in concurrent run: {sorted(missing_groups)[:5]} (+{max(0, len(missing_groups) - 5)} more)")
    if extra_groups:
        _note(f"groups only in concurrent run: {sorted(extra_groups)[:5]} (+{max(0, len(extra_groups) - 5)} more)")
    for ref in sorted(set(baseline_groups) & set(concurrent_groups)):
        b_children = baseline_groups[ref]["child_refs"]
        c_children = concurrent_groups[ref]["child_refs"]
        if b_children != c_children:
            _note(f"group {ref} child_refs differ: baseline={b_children} concurrent={c_children}")
        if baseline_groups[ref]["label"] != concurrent_groups[ref]["label"]:
            _note(
                f"group {ref} label differs: "
                f"baseline={baseline_groups[ref]['label']} concurrent={concurrent_groups[ref]['label']}"
            )

    if baseline.get("text_order_refs") != concurrent.get("text_order_refs"):
        b_refs = baseline.get("text_order_refs", [])
        c_refs = concurrent.get("text_order_refs", [])
        missing_texts = set(b_refs) - set(c_refs)
        if missing_texts:
            _note(f"text items missing in concurrent run: {len(missing_texts)} of {len(b_refs)}")
        elif b_refs != c_refs:
            _note("text_order_refs: same set of refs but different order")

    if baseline.get("table_order_refs") != concurrent.get("table_order_refs"):
        _note(
            f"table_order_refs differ: baseline={baseline.get('table_order_refs')} "
            f"concurrent={concurrent.get('table_order_refs')}"
        )

    if baseline.get("picture_order_refs") != concurrent.get("picture_order_refs"):
        _note(
            f"picture_order_refs differ: baseline={baseline.get('picture_order_refs')} "
            f"concurrent={concurrent.get('picture_order_refs')}"
        )

    baseline_totals = {key: int(baseline.get(key) or 0) for key in _COUNT_KEYS}
    concurrent_totals = {key: int(concurrent.get(key) or 0) for key in _COUNT_KEYS}
    size_ratio = {
        key: (concurrent_totals[key] / baseline_totals[key]) if baseline_totals[key] else 1.0
        for key in _COUNT_KEYS
    }

    return DiffResult(
        equivalent=not differences,
        first_difference=first_difference,
        differences=differences,
        baseline_totals=baseline_totals,
        concurrent_totals=concurrent_totals,
        size_ratio=size_ratio,
    )


# --------------------------------------------------------------------------
# Process orchestration
# --------------------------------------------------------------------------

def _run_one_subprocess(pdf_path: Path, label: str, scratch_dir: Path) -> dict[str, Any]:
    ctx = multiprocessing.get_context("spawn")
    out_queue: "multiprocessing.Queue[dict[str, Any]]" = ctx.Queue()
    scratch_export_path = str(scratch_dir / f"{label}_export.json")
    process = ctx.Process(
        target=_convert_worker,
        args=(str(pdf_path), label, scratch_export_path, out_queue),
    )
    process.start()
    result = out_queue.get()
    process.join()
    result["exit_code"] = process.exitcode
    return result


def _run_two_subprocesses_concurrently(
    pdf_a: Path, pdf_b: Path, scratch_dir: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    ctx = multiprocessing.get_context("spawn")
    out_queue: "multiprocessing.Queue[dict[str, Any]]" = ctx.Queue()
    scratch_a = str(scratch_dir / "A_export.json")
    scratch_b = str(scratch_dir / "B_export.json")

    process_a = ctx.Process(target=_convert_worker, args=(str(pdf_a), "A", scratch_a, out_queue))
    process_b = ctx.Process(target=_convert_worker, args=(str(pdf_b), "B", scratch_b, out_queue))

    process_a.start()
    process_b.start()

    results_by_label: dict[str, dict[str, Any]] = {}
    for _ in range(2):
        result = out_queue.get()
        results_by_label[result["label"]] = result

    process_a.join()
    process_b.join()
    results_by_label["A"]["exit_code"] = process_a.exitcode
    results_by_label["B"]["exit_code"] = process_b.exitcode
    return results_by_label["A"], results_by_label["B"]


def cmd_smoke(_args: argparse.Namespace) -> None:
    print(f"[smoke] PDF_A = {PDF_A}")
    print(f"[smoke] PDF_B = {PDF_B}")
    assert PDF_A.exists(), f"missing {PDF_A}"
    assert PDF_B.exists(), f"missing {PDF_B}"

    scratch = DIAGNOSTICS_ROOT / "_smoke_scratch"
    scratch.mkdir(parents=True, exist_ok=True)

    print("[smoke] sequential single conversion of PDF_A ...")
    result = _run_one_subprocess(PDF_A, "A", scratch)
    print(
        f"[smoke] A: status={result['status']} elapsed={result.get('elapsed_seconds'):.1f}s "
        f"exit_code={result.get('exit_code')}"
    )
    if result["status"] == "ok":
        fp = result["fingerprint"]
        print(
            f"[smoke] A fingerprint: pages={fp['page_count']} texts={fp['text_count']} "
            f"tables={fp['table_count']} pictures={fp['picture_count']} "
            f"groups={fp['group_count']} group_labels={fp['group_label_counts']}"
        )
    else:
        print(f"[smoke] A error: {result.get('error')}\n{result.get('traceback')}")


def cmd_baseline(args: argparse.Namespace) -> None:
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    for label, pdf_path in (("A", PDF_A), ("B", PDF_B)):
        fingerprints = []
        for repeat in range(args.repeats):
            scratch = BASELINE_DIR / f"_scratch_{label}_{repeat}"
            scratch.mkdir(parents=True, exist_ok=True)
            start = time.monotonic()
            result = _run_one_subprocess(pdf_path, label, scratch)
            wall = time.monotonic() - start
            status = result["status"]
            print(
                f"[baseline {label} repeat {repeat}] status={status} "
                f"elapsed={result.get('elapsed_seconds', 0):.1f}s wall={wall:.1f}s "
                f"exit_code={result.get('exit_code')}"
            )
            if status != "ok":
                print(f"  error: {result.get('error')}")
                continue
            fingerprints.append(result["fingerprint"])
            (BASELINE_DIR / f"{label}_repeat_{repeat}_fingerprint.json").write_text(
                json.dumps(result["fingerprint"], indent=2)
            )
        if fingerprints:
            first = fingerprints[0]
            for idx, fp in enumerate(fingerprints[1:], start=1):
                d = diff_fingerprints(first, fp)
                print(
                    f"[baseline {label} repeat 0 vs {idx}] equivalent={d.equivalent} "
                    f"first_difference={d.first_difference}"
                )
            (BASELINE_DIR / f"{label}_baseline_fingerprint.json").write_text(
                json.dumps(first, indent=2)
            )


def cmd_concurrent(args: argparse.Namespace) -> None:
    baseline_a_path = BASELINE_DIR / "A_baseline_fingerprint.json"
    baseline_b_path = BASELINE_DIR / "B_baseline_fingerprint.json"
    if not baseline_a_path.exists() or not baseline_b_path.exists():
        raise SystemExit("Run `baseline` first -- missing baseline fingerprint file(s).")

    baseline_a = json.loads(baseline_a_path.read_text())
    baseline_b = json.loads(baseline_b_path.read_text())

    divergent_a = 0
    divergent_b = 0
    divergent_trials = 0
    trial_records = []

    for trial in range(args.trials):
        run_dir = RUNS_DIR / f"run_{trial:03d}"
        scratch_dir = run_dir / "_scratch"
        scratch_dir.mkdir(parents=True, exist_ok=True)

        wall_start = time.monotonic()
        result_a, result_b = _run_two_subprocesses_concurrently(PDF_A, PDF_B, scratch_dir)
        wall = time.monotonic() - wall_start

        record: dict[str, Any] = {
            "trial": trial,
            "wall_seconds": wall,
            "A": {k: v for k, v in result_a.items() if k != "fingerprint"},
            "B": {k: v for k, v in result_b.items() if k != "fingerprint"},
        }

        trial_diverged = False
        for label, result, baseline in (("A", result_a, baseline_a), ("B", result_b, baseline_b)):
            if result["status"] != "ok":
                trial_diverged = True
                record[f"{label}_diff"] = {"status": result["status"], "error": result.get("error")}
                continue
            diff = diff_fingerprints(baseline, result["fingerprint"])
            record[f"{label}_diff"] = asdict(diff)
            if not diff.equivalent:
                trial_diverged = True
                if label == "A":
                    divergent_a += 1
                else:
                    divergent_b += 1

        progress_line = {
            "trial": trial,
            "wall_seconds": wall,
            "A_status": result_a["status"],
            "A_elapsed_seconds": result_a.get("elapsed_seconds", 0),
            "B_status": result_b["status"],
            "B_elapsed_seconds": result_b.get("elapsed_seconds", 0),
            "diverged": trial_diverged,
            "first_difference_A": record.get("A_diff", {}).get("first_difference"),
            "first_difference_B": record.get("B_diff", {}).get("first_difference"),
        }
        with open(RUNS_DIR / "progress.jsonl", "a", encoding="utf-8") as handle:
            handle.write(json.dumps(progress_line) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

        print(
            f"[concurrent trial {trial}] wall={wall:.1f}s "
            f"A_status={result_a['status']} A_elapsed={result_a.get('elapsed_seconds', 0):.1f}s "
            f"B_status={result_b['status']} B_elapsed={result_b.get('elapsed_seconds', 0):.1f}s "
            f"diverged={trial_diverged}",
            flush=True,
        )
        if trial_diverged:
            divergent_trials += 1
            (run_dir / "run.json").write_text(json.dumps(record, indent=2))
            (run_dir / "A_summary.json").write_text(json.dumps(result_a.get("fingerprint"), indent=2))
            (run_dir / "B_summary.json").write_text(json.dumps(result_b.get("fingerprint"), indent=2))
            for label in ("A", "B"):
                src = scratch_dir / f"{label}_export.json"
                if src.exists():
                    dest = run_dir / f"{label}_document.json"
                    dest.write_bytes(src.read_bytes())
            print(f"  !! DIVERGED -- artifacts saved under {run_dir}")

        for label in ("A", "B"):
            src = scratch_dir / f"{label}_export.json"
            if src.exists() and not trial_diverged:
                src.unlink()
        trial_records.append(record if trial_diverged else {"trial": trial, "diverged": False, "wall_seconds": wall})

    print("")
    print(f"Total trials: {args.trials}")
    print(f"Divergent trials: {divergent_trials} ({100.0 * divergent_trials / args.trials:.1f}%)")
    print(f"  A diverged: {divergent_a} ({100.0 * divergent_a / args.trials:.1f}%)")
    print(f"  B diverged: {divergent_b} ({100.0 * divergent_b / args.trials:.1f}%)")

    (RUNS_DIR / "summary.json").write_text(
        json.dumps(
            {
                "trials": args.trials,
                "divergent_trials": divergent_trials,
                "divergent_a": divergent_a,
                "divergent_b": divergent_b,
                "records": trial_records,
            },
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    smoke_parser = subparsers.add_parser("smoke")
    smoke_parser.set_defaults(func=cmd_smoke)

    baseline_parser = subparsers.add_parser("baseline")
    baseline_parser.add_argument("--repeats", type=int, default=3)
    baseline_parser.set_defaults(func=cmd_baseline)

    concurrent_parser = subparsers.add_parser("concurrent")
    concurrent_parser.add_argument("--trials", type=int, default=8)
    concurrent_parser.set_defaults(func=cmd_concurrent)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
