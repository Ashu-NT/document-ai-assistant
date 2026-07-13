from __future__ import annotations

import importlib.util
import sys

from pathlib import Path

from src.application.contracts.document.document_catalog_entry import DocumentCatalogEntry

_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts"


def _load_script(script_name: str):
    cached_key = f"_cli_test_{script_name}"
    if cached_key in sys.modules:
        return sys.modules[cached_key]

    script_path = _SCRIPTS_DIR / f"{script_name}.py"
    saved_path = list(sys.path)
    spec = importlib.util.spec_from_file_location(cached_key, script_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[cached_key] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(cached_key, None)
        raise
    finally:
        sys.path[:] = saved_path
    return mod


def test_export_document_table_assets_module_importable() -> None:
    mod = _load_script("export_document_table_assets")
    assert hasattr(mod, "parse_args")
    assert hasattr(mod, "build_report")
    assert hasattr(mod, "main")


def test_export_document_table_assets_parse_args_defaults() -> None:
    mod = _load_script("export_document_table_assets")
    args = mod.parse_args([])
    assert args.document == "19P006-31-FWC12-5-1-0_Manual"
    assert args.document_id is None
    assert args.output is None


def test_export_document_table_assets_parse_args_document_id() -> None:
    mod = _load_script("export_document_table_assets")
    args = mod.parse_args(["--document-id", "doc_123"])
    assert args.document_id == "doc_123"
    assert args.document is None


def test_export_document_table_assets_default_output_path_uses_safe_stem() -> None:
    mod = _load_script("export_document_table_assets")
    output_path = mod.resolve_output_path(
        output=None,
        display_name="19P006-31-FWC12-5-1-0 Manual.pdf",
    )
    assert output_path.name == "19P006-31-FWC12-5-1-0_Manual_pdf_table_assets.md"


def test_export_document_table_assets_build_report_includes_table_markdown(
    sample_document_graph,
) -> None:
    mod = _load_script("export_document_table_assets")
    document_entry = DocumentCatalogEntry(
        document_id=sample_document_graph.document.document_id,
        title=sample_document_graph.document.title,
        file_name=sample_document_graph.document.file_name,
        file_path=sample_document_graph.document.file_path,
        document_type=str(sample_document_graph.document.document_type),
        language=sample_document_graph.document.language,
        page_count=sample_document_graph.document.statistics.page_count,
        chunk_count=len(sample_document_graph.chunks),
        section_count=len(sample_document_graph.sections),
        identifier_count=len(sample_document_graph.identifiers),
        table_count=len(sample_document_graph.tables),
        picture_count=len(sample_document_graph.pictures),
        created_at=None,
    )

    table_assets = mod.resolve_table_assets(sample_document_graph)
    report = mod.build_report(
        document_entry=document_entry,
        document_graph=sample_document_graph,
        table_assets=table_assets,
    )

    assert "# Table Asset Report: Hydraulic Pump Manual" in report
    assert "### Table 1: `table_001`" in report
    assert "| Part Number | Description |" in report
    assert "- section: `Maintenance Schedule`" in report
