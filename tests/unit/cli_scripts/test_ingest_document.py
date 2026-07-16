from __future__ import annotations

import importlib.util
import sys

from pathlib import Path
from types import SimpleNamespace

from src.application.workflows.ingestion.ingestion_result import IngestionResult
from src.application.workflows.ingestion.ingestion_status import IngestionStatus

_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts"


def _load_script(script_name: str):
    cached_key = f"_cli_ingest_test_{script_name}"
    if cached_key in sys.modules:
        return sys.modules[cached_key]

    script_path = _SCRIPTS_DIR / f"{script_name}.py"
    saved_path = list(sys.path)
    spec = importlib.util.spec_from_file_location(cached_key, script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = saved_path
    sys.modules[cached_key] = module
    return module


def test_parse_args_accepts_explicit_reingest_document_id() -> None:
    mod = _load_script("ingest_document")

    args = mod.parse_args(["--reingest-document-id", "doc_123"])

    assert args.reingest_document_id == "doc_123"
    assert args.input is None


def test_parse_args_accepts_reingest_if_duplicate_for_input_mode() -> None:
    mod = _load_script("ingest_document")

    args = mod.parse_args(
        ["--input", "example.pdf", "--reingest-if-duplicate"]
    )

    assert args.input == "example.pdf"
    assert args.reingest_if_duplicate is True


def test_parse_args_rejects_force_with_reingest_if_duplicate() -> None:
    mod = _load_script("ingest_document")

    try:
        mod.parse_args(["--input", "example.pdf", "--force", "--reingest-if-duplicate"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("Expected argparse to reject conflicting flags.")


def test_main_reingests_explicit_document_id_in_place(monkeypatch) -> None:
    mod = _load_script("ingest_document")
    captured: dict[str, object] = {}

    def fake_reingest(request, *, progress_callback=None):
        captured["request"] = request
        captured["progress_callback"] = progress_callback
        return IngestionResult(
            status=IngestionStatus.COMPLETE,
            document_id="doc_123",
            diagnostics={},
        )

    runtime = SimpleNamespace(
        ingestion_workflow=SimpleNamespace(reingest=fake_reingest),
        close=lambda: None,
    )
    monkeypatch.setattr(mod, "_build_runtime", lambda: runtime)

    result = mod.main(["--reingest-document-id", "doc_123", "--json"])

    assert result == 0
    assert getattr(captured["request"], "document_id") == "doc_123"
    assert getattr(captured["request"], "requested_by") == "ingest_document_script_reingest"


def test_main_upgrades_duplicate_skip_to_reingest_when_requested(monkeypatch, tmp_path) -> None:
    mod = _load_script("ingest_document")
    input_path = tmp_path / "example.pdf"
    input_path.write_text("placeholder", encoding="utf-8")
    calls: list[tuple[str, object]] = []

    def fake_run(request, *, progress_callback=None):
        calls.append(("run", request))
        return IngestionResult(
            status=IngestionStatus.SKIPPED_FILE_DUPLICATE,
            document_id="doc_existing",
            duplicate_of_document_id="doc_existing",
            diagnostics={},
        )

    def fake_reingest(request, *, progress_callback=None):
        calls.append(("reingest", request))
        return IngestionResult(
            status=IngestionStatus.COMPLETE,
            document_id="doc_existing",
            diagnostics={},
        )

    runtime = SimpleNamespace(
        ingestion_workflow=SimpleNamespace(run=fake_run, reingest=fake_reingest),
        close=lambda: None,
    )
    monkeypatch.setattr(mod, "_build_runtime", lambda: runtime)

    result = mod.main(
        [
            "--input",
            str(input_path),
            "--reingest-if-duplicate",
            "--json",
        ]
    )

    assert result == 0
    assert [name for name, _ in calls] == ["run", "reingest"]
    assert getattr(calls[1][1], "document_id") == "doc_existing"
