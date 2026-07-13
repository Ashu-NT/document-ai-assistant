from __future__ import annotations

"""
Export all persisted table assets for a stored document into a Markdown report.

Usage:
    python scripts/export_document_table_assets.py
    python scripts/export_document_table_assets.py --document "19P006-31-FWC12-5-1-0_Manual"
    python scripts/export_document_table_assets.py --document-id doc_123
"""

import argparse
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
DEFAULT_DOCUMENT_QUERY = "19P006-31-FWC12-5-1-0_Manual"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "debug_tables"

for _import_root in (PROJECT_ROOT, SRC_ROOT):
    _import_root_str = str(_import_root)
    if _import_root_str not in sys.path:
        sys.path.insert(0, _import_root_str)


@dataclass(slots=True)
class ResolvedTableAsset:
    table_id: str
    markdown: str
    section_path: str | None
    page_start: int | None
    page_end: int | None
    row_count: int | None
    column_count: int | None
    caption: str | None
    nearby_text: str | None
    element_ids: list[str]
    structured_rows_text: str | None


def _entry_field(document_entry, field_name: str):
    if isinstance(document_entry, dict):
        return document_entry.get(field_name)
    return getattr(document_entry, field_name)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export all persisted table assets for a stored document."
    )
    selector_group = parser.add_mutually_exclusive_group()
    selector_group.add_argument(
        "--document",
        default=DEFAULT_DOCUMENT_QUERY,
        help=(
            "Document query text matched against stored title/file name. "
            f"Defaults to {DEFAULT_DOCUMENT_QUERY!r}."
        ),
    )
    selector_group.add_argument(
        "--document-id",
        help="Exact stored document_id.",
    )
    parser.add_argument(
        "--output",
        help="Optional output Markdown path.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.document_id:
        args.document = None
    return args


def print_status(message: str) -> None:
    print(f"[export-document-table-assets] {message}", flush=True)


def _safe_file_stem(value: str) -> str:
    cleaned = [
        character if character.isalnum() or character in {"-", "_"} else "_"
        for character in value.strip()
    ]
    collapsed = "".join(cleaned).strip("_")
    return collapsed or "document"


def resolve_output_path(
    *,
    output: str | None,
    display_name: str,
) -> Path:
    if output:
        return Path(output).expanduser().resolve()
    return DEFAULT_OUTPUT_DIR / f"{_safe_file_stem(display_name)}_table_assets.md"


def format_page_range(page_start: int | None, page_end: int | None) -> str:
    if page_start is None and page_end is None:
        return "-"
    if page_start is None:
        return str(page_end)
    if page_end is None or page_end == page_start:
        return str(page_start)
    return f"{page_start}-{page_end}"


def resolve_table_assets(document_graph) -> list[ResolvedTableAsset]:
    resolved: list[ResolvedTableAsset] = []
    elements = list(document_graph.elements.values())

    for table in document_graph.tables.values():
        linked_elements = [
            element for element in elements if element.table_id == table.table_id
        ]
        linked_elements.sort(
            key=lambda element: (
                element.source.page_start or 0,
                element.reading_order or 0,
                element.element_id,
            )
        )
        section_id = table.parent_section_id or (
            linked_elements[0].parent_section_id if linked_elements else None
        )
        section = document_graph.sections.get(section_id) if section_id else None
        pages = [
            page
            for element in linked_elements
            for page in (element.source.page_start, element.source.page_end)
            if page is not None
        ]
        resolved.append(
            ResolvedTableAsset(
                table_id=table.table_id,
                markdown=table.markdown,
                section_path=section.path_text() if section is not None else None,
                page_start=min(pages) if pages else table.metadata.source.page_start,
                page_end=max(pages) if pages else table.metadata.source.page_end,
                row_count=table.row_count if table.row_count is not None else len(table.rows),
                column_count=(
                    table.column_count
                    if table.column_count is not None
                    else max((len(row) for row in table.rows), default=0)
                ),
                caption=table.metadata.caption,
                nearby_text=table.metadata.nearby_text,
                element_ids=[element.element_id for element in linked_elements],
                structured_rows_text=table.to_structured_row_text(),
            )
        )

    resolved.sort(
        key=lambda item: (
            item.page_start or 0,
            item.page_end or 0,
            item.section_path or "",
            item.table_id,
        )
    )
    return resolved


def build_report(*, document_entry, document_graph, table_assets: list[ResolvedTableAsset]) -> str:
    display_name = _entry_field(document_entry, "title") or _entry_field(
        document_entry, "file_name"
    )
    lines = [
        f"# Table Asset Report: {display_name}",
        "",
        "## Document",
        "",
        f"- document_id: `{_entry_field(document_entry, 'document_id')}`",
        f"- file_name: `{_entry_field(document_entry, 'file_name')}`",
        f"- title: `{_entry_field(document_entry, 'title') or '-'}`",
        f"- document_type: `{_entry_field(document_entry, 'document_type')}`",
        f"- page_count: `{_entry_field(document_entry, 'page_count') if _entry_field(document_entry, 'page_count') is not None else '-'}`",
        f"- stored table asset count: `{len(table_assets)}`",
        "",
    ]

    if not table_assets:
        lines.extend(
            [
                "## Tables",
                "",
                "_No table assets were found for this document._",
                "",
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            "## Tables",
            "",
        ]
    )
    for index, table in enumerate(table_assets, start=1):
        lines.extend(
            [
                f"### Table {index}: `{table.table_id}`",
                "",
                f"- section: `{table.section_path or '-'}`",
                f"- pages: `{format_page_range(table.page_start, table.page_end)}`",
                f"- row_count: `{table.row_count if table.row_count is not None else '-'}`",
                f"- column_count: `{table.column_count if table.column_count is not None else '-'}`",
                f"- linked element ids: `{', '.join(table.element_ids) if table.element_ids else '-'}`",
                f"- caption: `{table.caption or '-'}`",
                "",
            ]
        )
        if table.nearby_text:
            lines.extend(
                [
                    "#### Nearby Text",
                    "",
                    table.nearby_text,
                    "",
                ]
            )
        lines.extend(
            [
                "#### Markdown",
                "",
                table.markdown.strip() or "_Empty table markdown._",
                "",
            ]
        )
        if table.structured_rows_text:
            lines.extend(
                [
                    "#### Structured Rows",
                    "",
                    "```text",
                    table.structured_rows_text,
                    "```",
                    "",
                ]
            )

    lines.extend(
        [
            "## Graph Summary",
            "",
            f"- section_count: `{len(document_graph.sections)}`",
            f"- element_count: `{len(document_graph.elements)}`",
            f"- chunk_count: `{len(document_graph.chunks)}`",
            f"- picture_count: `{len(document_graph.pictures)}`",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    session = None

    try:
        from src.bootstrap.startup import bootstrap_application  # noqa: WPS433
        from src.infrastructure.db.base import Base  # noqa: WPS433,F401
        from src.infrastructure.db.orm_models import __all__ as _orm_models_loaded  # noqa: WPS433,F401
        from src.infrastructure.db.schema_management import ensure_database_schema  # noqa: WPS433
        from src.infrastructure.db.session import SessionLocal, engine  # noqa: WPS433
        from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork  # noqa: WPS433
        from src.application.services.document import (  # noqa: WPS433
            DocumentCatalogService,
            DocumentLookupService,
        )
        from src.application.tools.documents import (  # noqa: WPS433
            FindDocumentRequest,
            FindDocumentTool,
        )

        bootstrap_application()
        ensure_database_schema(engine)
        session = SessionLocal()
        unit_of_work = SqlAlchemyUnitOfWork(session)
        catalog_service = DocumentCatalogService(unit_of_work.documents)
        lookup_service = DocumentLookupService(unit_of_work.documents)
        find_tool = FindDocumentTool(catalog_service)

        print_status("Resolving stored document...")
        find_result = find_tool.run(
            FindDocumentRequest(
                document_id=args.document_id,
                query_text=None if args.document_id else args.document,
            )
        )
        if not find_result.success:
            print(find_result.message or "Document was not found.", file=sys.stderr)
            diagnostics = find_result.diagnostics or {}
            matches = diagnostics.get("matches")
            if matches:
                print_status(
                    "Multiple matches found: "
                    + ", ".join(match.get("display_name", "?") for match in matches)
                )
            return 1

        document_entry = find_result.data
        display_name = document_entry["display_name"]
        print_status(
            f"Loading persisted document graph for {display_name} ({document_entry['document_id']})..."
        )
        document_graph = lookup_service.get_document_graph(document_entry["document_id"])
        if document_graph is None:
            print("Stored document graph was not found.", file=sys.stderr)
            return 1

        table_assets = resolve_table_assets(document_graph)
        output_path = resolve_output_path(output=args.output, display_name=display_name)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print_status(f"Building Markdown report for {len(table_assets)} table asset(s)...")
        report = build_report(
            document_entry=document_entry,
            document_graph=document_graph,
            table_assets=table_assets,
        )
        output_path.write_text(report, encoding="utf-8")
        print_status(f"Markdown report written: {output_path}")
        print(output_path)
        return 0

    except Exception:
        traceback.print_exc()
        return 1
    finally:
        if session is not None:
            session.close()


if __name__ == "__main__":
    raise SystemExit(main())
