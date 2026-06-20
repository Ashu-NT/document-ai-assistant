from __future__ import annotations

"""
Debug utility for verifying Docling output -> canonical elements -> document graph
-> provisional chunks -> document classification -> post-classification chunks.

Usage:
    python scripts/debug_parse_document.py --input data/input/example.pdf
"""

import argparse
import hashlib
import json
import re
import sys
import traceback
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for import_root in (PROJECT_ROOT, SRC_ROOT):
    import_root_text = str(import_root)
    if import_root_text not in sys.path:
        sys.path.insert(0, import_root_text)

from src.application.workflows.parsing.builders import (  # noqa: E402
    DocumentGraphBuilder,
    SectionBuilder,
    SectionBuildResult,
)
from src.application.workflows.classification import (  # noqa: E402
    DocumentClassificationWorkflow,
    HybridDocumentTypeResolver,
)
from src.application.validation.classification import (  # noqa: E402
    DocumentClassificationValidator,
)
from src.application.services.ai import LLMService  # noqa: E402
from src.application.workflows.parsing.normalizers import (  # noqa: E402
    DoclingDocumentNormalizer,
)
from src.application.workflows.parsing.builders.chunking.policies import (  # noqa: E402
    ChunkingProfileInferer,
    DocumentChunkingPolicyResolver,
)
from src.config.paths import ensure_directory, resolve_project_path  # noqa: E402
from src.domain.document import DocumentHashes  # noqa: E402
from src.infrastructure.ai.llm import OllamaLLMProvider  # noqa: E402
from src.infrastructure.parsing.docling import DoclingParser  # noqa: E402
from src.shared.exceptions import ApplicationError  # noqa: E402
from src.shared.ids import IdGenerator, IdPrefix  # noqa: E402


class DebugClassificationService:
    def __init__(self) -> None:
        self.saved_document_classification = None

    def save_document_classification(
        self,
        classification: Any,
        activity_context: Any = None,
    ) -> Any:
        self.saved_document_classification = classification
        return classification


def safe_getattr(value: Any, *names: str, default: Any = None) -> Any:
    current = value

    for name in names:
        if current is None:
            return default

        if isinstance(current, dict):
            current = current.get(name)
        else:
            current = getattr(current, name, None)

    return default if current is None else current


def preview_text(value: Any, limit: int = 160) -> str:
    if value is None:
        return ""

    text = re.sub(r"\s+", " ", str(value)).strip()
    if len(text) <= limit:
        return text

    return f"{text[: max(0, limit - 3)].rstrip()}..."


def count_by_type(values: list[Any], attribute_name: str = "element_type") -> dict[str, int]:
    counts = Counter()

    for value in values:
        raw_type = safe_getattr(value, attribute_name)
        display_type = display_value(raw_type) or "unknown"
        counts[display_type] += 1

    return dict(sorted(counts.items(), key=lambda item: item[0]))


def format_table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return "_No rows._"

    def _cell(value: Any) -> str:
        text = preview_text(value, limit=220) if value is not None else ""
        return text.replace("|", "\\|").replace("\n", "<br>")

    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    body_rows = [
        "| " + " | ".join(_cell(value) for value in row) + " |"
        for row in rows
    ]

    return "\n".join([header_row, separator_row, *body_rows])


def write_markdown_report(output_path: Path, content: str) -> None:
    output_path.write_text(content, encoding="utf-8")


def sort_chunks(chunks: list[Any]) -> list[Any]:
    return sorted(
        chunks,
        key=lambda item: safe_getattr(item, "sequence_number", default=0) or 0,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the local parsing pipeline for one document and write a Markdown inspection report.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input PDF/document.",
    )
    parser.add_argument(
        "--output",
        help="Optional output Markdown path. Defaults to outputs/debug_parsing/<stem>_parsing_report.md",
    )
    return parser.parse_args()


def resolve_input_path(input_value: str) -> Path:
    input_path = resolve_project_path(input_value).expanduser().resolve()
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    return input_path


def resolve_output_path(input_path: Path, output_value: str | None) -> Path:
    if output_value:
        return resolve_project_path(output_value).expanduser().resolve()

    return (PROJECT_ROOT / "outputs" / "debug_parsing" / f"{input_path.stem}_parsing_report.md").resolve()


def compute_debug_hashes(file_path: Path) -> tuple[str, str]:
    digest = hashlib.sha256()

    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    file_hash = digest.hexdigest()
    content_hash = file_hash
    return file_hash, content_hash


def display_value(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)


def format_page_range(page_start: Any, page_end: Any) -> str:
    if page_start is None and page_end is None:
        return "unknown"
    if page_start == page_end:
        return str(page_start)
    return f"{page_start} -> {page_end}"


def format_section_path(section_path: Any) -> str:
    if not section_path:
        return ""
    if isinstance(section_path, (list, tuple)):
        return " > ".join(str(part) for part in section_path)
    return str(section_path)


def format_bbox(bbox: Any) -> str:
    if bbox is None:
        return ""

    x1 = safe_getattr(bbox, "x1")
    y1 = safe_getattr(bbox, "y1")
    x2 = safe_getattr(bbox, "x2")
    y2 = safe_getattr(bbox, "y2")

    if any(value is None for value in (x1, y1, x2, y2)):
        return preview_text(bbox, limit=120)

    return f"({x1}, {y1}) -> ({x2}, {y2})"


def format_json_block(value: Any) -> str:
    try:
        return json.dumps(
            value,
            indent=2,
            default=lambda item: item.__dict__ if hasattr(item, "__dict__") else str(item),
        )
    except TypeError:
        return str(value)


def sanitize_code_block(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("```", "'''")


def format_list_summary(values: Any, limit: int = 8) -> str:
    if not values:
        return ""

    if not isinstance(values, (list, tuple, set)):
        return str(values)

    items = [str(value) for value in values]
    if len(items) <= limit:
        return ", ".join(items)

    preview_items = ", ".join(items[:limit])
    return f"{preview_items}, ... (+{len(items) - limit} more)"


def build_section_tree(section_build_result: SectionBuildResult | None) -> str:
    if section_build_result is None or not section_build_result.sections:
        return "_No section hierarchy available._"

    sections = list(section_build_result.sections)
    children_by_parent: dict[str | None, list[Any]] = {}
    for section in sections:
        children_by_parent.setdefault(
            safe_getattr(section, "parent_section_id"),
            [],
        ).append(section)

    for children in children_by_parent.values():
        children.sort(
            key=lambda item: (
                safe_getattr(item, "sequence_number", default=0) or 0,
                safe_getattr(item, "title", default=""),
            )
        )

    lines: list[str] = []

    def render(parent_id: str | None, depth: int) -> None:
        for section in children_by_parent.get(parent_id, []):
            indent = "  " * depth
            lines.append(f"{indent}- {safe_getattr(section, 'title', default='')}")
            render(safe_getattr(section, "section_id"), depth + 1)

    render(None, 0)
    return "\n".join(lines) if lines else "_No section hierarchy available._"


def invert_mapping(mapping: dict[str, str]) -> dict[str, str]:
    return {
        value: key
        for key, value in mapping.items()
    }


def build_validation_summary(
    canonical_elements: list[Any],
    document_graph: Any,
    section_build_result: SectionBuildResult | None,
) -> list[str]:
    section_count_with_parent = 0
    root_section_count = 0
    if section_build_result is not None:
        for section in section_build_result.sections:
            if safe_getattr(section, "parent_section_id"):
                section_count_with_parent += 1
            else:
                root_section_count += 1

    elements_without_section_id = sum(
        1
        for element in document_graph.elements.values()
        if safe_getattr(element, "parent_section_id") is None
    )
    chunks_without_section_path = sum(
        1
        for chunk in document_graph.chunks.values()
        if not safe_getattr(chunk, "section_path")
    )
    multi_element_chunks = sum(
        1
        for chunk in document_graph.chunks.values()
        if len(safe_getattr(chunk, "element_ids", default=[]) or []) > 1
    )
    multi_page_chunks = sum(
        1
        for chunk in document_graph.chunks.values()
        if (
            safe_getattr(chunk, "source", "page_start") is not None
            and safe_getattr(chunk, "source", "page_end") is not None
            and safe_getattr(chunk, "source", "page_start")
            != safe_getattr(chunk, "source", "page_end")
        )
    )
    self_titled_text_elements = sum(
        1
        for element in canonical_elements
        if display_value(safe_getattr(element, "element_type")) == "text"
        and safe_getattr(element, "section_title")
        and safe_getattr(element, "section_title") == safe_getattr(element, "text")
    )

    return [
        f"- sections with parent_section_id: `{section_count_with_parent}`",
        f"- root sections: `{root_section_count}`",
        f"- elements without section_id: `{elements_without_section_id}`",
        f"- chunks without section_path: `{chunks_without_section_path}`",
        f"- chunks spanning multiple elements: `{multi_element_chunks}`",
        f"- chunks spanning multiple pages: `{multi_page_chunks}`",
        f"- normal text elements with self-derived section_title: `{self_titled_text_elements}`",
    ]


def build_warnings(
    canonical_elements: list[Any],
    document_graph: Any,
    section_build_result: SectionBuildResult | None,
) -> list[str]:
    warnings: list[str] = []

    if not canonical_elements:
        warnings.append("No canonical elements were produced.")

    if not document_graph.sections:
        warnings.append("No sections were created in the document graph.")

    if not document_graph.chunks:
        warnings.append("No chunks were created in the document graph.")

    has_page_numbers = any(
        safe_getattr(element, "page_start") is not None
        or safe_getattr(element, "page_end") is not None
        for element in canonical_elements
    )
    if not has_page_numbers:
        warnings.append("No page numbers were detected in canonical elements.")

    if not document_graph.tables:
        warnings.append("No table assets were detected.")

    if not document_graph.pictures:
        warnings.append("No picture assets were detected.")

    empty_chunks = [
        chunk.chunk_id
        for chunk in document_graph.chunks.values()
        if not safe_getattr(chunk, "content", default="").strip()
    ]
    if empty_chunks:
        warnings.append(
            "Chunks with empty content: " + ", ".join(empty_chunks)
        )

    unassigned_elements = [
        element.element_id
        for element in document_graph.elements.values()
        if safe_getattr(element, "parent_section_id") is None
    ]
    if unassigned_elements:
        warnings.append(
            "Elements without section assignment: " + ", ".join(unassigned_elements)
        )

    if section_build_result is not None:
        root_sections = [
            section.section_id
            for section in section_build_result.sections
            if not safe_getattr(section, "parent_section_id")
        ]
        if root_sections and len(root_sections) == len(section_build_result.sections):
            warnings.append("All sections are root sections.")

    chunks_without_section_path = [
        chunk.chunk_id
        for chunk in document_graph.chunks.values()
        if not safe_getattr(chunk, "section_path")
    ]
    if chunks_without_section_path:
        warnings.append(
            "Chunks without section_path: " + ", ".join(chunks_without_section_path)
        )

    self_titled_text_elements = [
        element.element_id
        for element in canonical_elements
        if display_value(safe_getattr(element, "element_type")) == "text"
        and safe_getattr(element, "section_title")
        and safe_getattr(element, "section_title") == safe_getattr(element, "text")
    ]
    if self_titled_text_elements:
        warnings.append(
            "Text elements using their own paragraph text as section_title: "
            + ", ".join(self_titled_text_elements)
        )

    return warnings


def build_report(
    *,
    input_path: Path,
    output_path: Path,
    file_hash: str,
    content_hash: str,
    raw_parsed_document: Any,
    canonical_elements: list[Any],
    document_graph: Any,
    section_build_result: SectionBuildResult | None,
    initial_chunks: list[Any] | None = None,
    post_classification_chunks: list[Any] | None = None,
    structural_profile_inference: Any | None = None,
    provisional_chunking_policy: Any | None = None,
    document_classification: Any | None = None,
    document_type_decision: Any | None = None,
    classification_provider: Any | None = None,
) -> str:
    lines: list[str] = ["# Parsing Debug Report", ""]
    structural_profile_inference = (
        structural_profile_inference
        or infer_structural_profile_inference(document_graph)
    )
    initial_chunks = initial_chunks or sort_chunks(list(document_graph.chunks.values()))
    post_classification_chunks = (
        post_classification_chunks
        or initial_chunks
    )

    lines.extend(
        [
            "## Input",
            f"- file path: `{input_path}`",
            f"- file name: `{input_path.name}`",
            f"- file hash: `{file_hash}`",
            f"- content hash: `{content_hash}`",
            f"- report path: `{output_path}`",
            "",
        ]
    )

    lines.extend(
        [
            "## Raw Parsed Document",
            f"- parser name: `{safe_getattr(raw_parsed_document, 'parser_name', default='')}`",
            f"- parser version: `{safe_getattr(raw_parsed_document, 'parser_version', default='')}`",
            f"- title: `{safe_getattr(raw_parsed_document, 'title', default='')}`",
            f"- page count: `{safe_getattr(raw_parsed_document, 'page_count', default='')}`",
            f"- raw document type: `{type(safe_getattr(raw_parsed_document, 'raw_document')).__name__}`",
            "",
        ]
    )

    lines.extend(
        build_structural_profile_inference_section(structural_profile_inference)
    )
    lines.extend(
        build_document_classification_section(
            document_graph=document_graph,
            structural_profile_inference=structural_profile_inference,
            provisional_chunking_policy=provisional_chunking_policy,
            document_classification=document_classification,
            document_type_decision=document_type_decision,
            classification_provider=classification_provider,
            initial_chunks=initial_chunks,
            post_classification_chunks=post_classification_chunks,
        )
    )

    canonical_counts = count_by_type(canonical_elements)
    page_values = [
        value
        for element in canonical_elements
        for value in (
            safe_getattr(element, "page_start"),
            safe_getattr(element, "page_end"),
        )
        if value is not None
    ]
    page_range = (
        f"{min(page_values)} -> {max(page_values)}"
        if page_values
        else "unknown"
    )

    lines.extend(
        [
            "## Canonical Elements Summary",
            f"- total canonical elements: `{len(canonical_elements)}`",
            f"- count by element_type: `{format_json_block(canonical_counts)}`",
            f"- page range: `{page_range}`",
            "",
            "### First 20 Elements",
            format_table(
                headers=[
                    "order_index",
                    "element_id",
                    "element_type",
                    "page_start",
                    "page_end",
                    "section_title",
                    "text preview",
                ],
                rows=[
                    [
                        safe_getattr(element, "order_index"),
                        safe_getattr(element, "element_id"),
                        display_value(safe_getattr(element, "element_type")),
                        safe_getattr(element, "page_start"),
                        safe_getattr(element, "page_end"),
                        safe_getattr(element, "section_title"),
                        preview_text(safe_getattr(element, "text"), limit=120),
                    ]
                    for element in sorted(
                        canonical_elements,
                        key=lambda item: safe_getattr(item, "order_index", default=0),
                    )[:20]
                ],
            ),
            "",
        ]
    )

    lines.append("## Canonical Elements Full Dump")
    lines.append("")
    if not canonical_elements:
        lines.append("_No canonical elements._")
        lines.append("")
    else:
        for element in sorted(
            canonical_elements,
            key=lambda item: safe_getattr(item, "order_index", default=0),
        ):
            lines.extend(
                [
                    f"### {safe_getattr(element, 'element_id', default='')}",
                    f"- type: `{display_value(safe_getattr(element, 'element_type'))}`",
                    f"- order index: `{safe_getattr(element, 'order_index', default='')}`",
                    f"- page: `{format_page_range(safe_getattr(element, 'page_start'), safe_getattr(element, 'page_end'))}`",
                    f"- section title: `{safe_getattr(element, 'section_title', default='')}`",
                    f"- section path: `{format_section_path(safe_getattr(element, 'section_path'))}`",
                    f"- bbox: `{format_bbox(safe_getattr(element, 'bbox'))}`",
                    f"- raw_ref: `{safe_getattr(element, 'raw_ref', default='')}`",
                    f"- text/content preview: `{preview_text(safe_getattr(element, 'text'), limit=320)}`",
                    "",
                ]
            )

    lines.extend(
        [
            "## Document Graph Summary",
            f"- document id: `{safe_getattr(document_graph, 'document', 'document_id', default='')}`",
            f"- document title: `{safe_getattr(document_graph, 'document', 'title', default='')}`",
            f"- document type: `{display_value(safe_getattr(document_graph, 'document', 'document_type'))}`",
            f"- section count: `{len(document_graph.sections)}`",
            f"- element count: `{len(document_graph.elements)}`",
            f"- chunk count: `{len(document_graph.chunks)}`",
            f"- table asset count: `{len(document_graph.tables)}`",
            f"- picture asset count: `{len(document_graph.pictures)}`",
            "",
        ]
    )

    lines.append("## Section Hierarchy Tree")
    lines.append("")
    lines.append(build_section_tree(section_build_result))
    lines.append("")

    section_header_by_section_id = (
        invert_mapping(section_build_result.header_section_ids)
        if section_build_result is not None
        else {}
    )

    lines.append("## Sections")
    lines.append("")
    if not document_graph.sections:
        lines.append("_No sections._")
        lines.append("")
    else:
        for section in sorted(
            document_graph.sections.values(),
            key=lambda item: (
                safe_getattr(item, "sequence_number", default=0) or 0,
                safe_getattr(item, "title", default=""),
            ),
        ):
            header_element_id = section_header_by_section_id.get(
                safe_getattr(section, "section_id", default="")
            )
            raw_heading_level = (
                section_build_result.header_raw_levels.get(header_element_id)
                if section_build_result is not None and header_element_id is not None
                else None
            )
            effective_heading_level = (
                section_build_result.header_levels.get(header_element_id)
                if section_build_result is not None and header_element_id is not None
                else safe_getattr(section, "level")
            )
            heading_source = (
                section_build_result.header_sources.get(header_element_id)
                if section_build_result is not None and header_element_id is not None
                else "default"
            )
            lines.extend(
                [
                    f"### {safe_getattr(section, 'section_id', default='')}",
                    f"- title: `{safe_getattr(section, 'title', default='')}`",
                    f"- parent section id: `{safe_getattr(section, 'parent_section_id', default='')}`",
                    f"- section path: `{format_section_path(safe_getattr(section, 'section_path'))}`",
                    f"- page_start/page_end: `{format_page_range(safe_getattr(section, 'source', 'page_start'), safe_getattr(section, 'source', 'page_end'))}`",
                    f"- order_index: `{safe_getattr(section, 'reading_order_start', default='')}`",
                    f"- raw heading_level: `{raw_heading_level if raw_heading_level is not None else ''}`",
                    f"- effective heading_level: `{effective_heading_level if effective_heading_level is not None else ''}`",
                    f"- strategy: `{heading_source}`",
                    "",
                ]
            )

    lines.append("## Elements")
    lines.append("")
    if not document_graph.elements:
        lines.append("_No graph elements._")
        lines.append("")
    else:
        for element in sorted(
            document_graph.elements.values(),
            key=lambda item: safe_getattr(item, "reading_order", default=0) or 0,
        ):
            parser_extra = safe_getattr(element, "parser_metadata", "extra", default={}) or {}
            lines.extend(
                [
                    f"### {safe_getattr(element, 'element_id', default='')}",
                    f"- type: `{display_value(safe_getattr(element, 'element_type'))}`",
                    f"- section id: `{safe_getattr(element, 'parent_section_id', default='')}`",
                    f"- resolved section path: `{format_section_path(parser_extra.get('resolved_section_path'))}`",
                    f"- page_start/page_end: `{format_page_range(safe_getattr(element, 'source', 'page_start'), safe_getattr(element, 'source', 'page_end'))}`",
                    f"- order_index: `{safe_getattr(element, 'reading_order', default='')}`",
                    f"- effective heading_level: `{parser_extra.get('effective_heading_level') or ''}`",
                    f"- heading level source: `{parser_extra.get('heading_level_source') or ''}`",
                    f"- text preview: `{preview_text(safe_getattr(element, 'text'), limit=240)}`",
                    "",
                ]
            )

    table_element_lookup = {
        safe_getattr(element, "table_id"): element
        for element in document_graph.elements.values()
        if safe_getattr(element, "table_id")
    }
    lines.append("## Table Assets")
    lines.append("")
    if not document_graph.tables:
        lines.append("_No table assets._")
        lines.append("")
    else:
        for table in document_graph.tables.values():
            linked_element = table_element_lookup.get(safe_getattr(table, "table_id"))
            source = safe_getattr(table, "metadata", "source") or safe_getattr(linked_element, "source")
            lines.extend(
                [
                    f"### {safe_getattr(table, 'table_id', default='')}",
                    f"- document id: `{safe_getattr(table, 'document_id', default='')}`",
                    f"- element id: `{safe_getattr(linked_element, 'element_id', default='')}`",
                    f"- page_start/page_end: `{format_page_range(safe_getattr(source, 'page_start'), safe_getattr(source, 'page_end'))}`",
                    f"- markdown preview: `{preview_text(safe_getattr(table, 'markdown'), limit=320)}`",
                    "- metadata:",
                    "```json",
                    sanitize_code_block(format_json_block(safe_getattr(table, 'metadata'))),
                    "```",
                    "",
                ]
            )

    picture_element_lookup = {
        safe_getattr(element, "picture_id"): element
        for element in document_graph.elements.values()
        if safe_getattr(element, "picture_id")
    }
    lines.append("## Picture Assets")
    lines.append("")
    if not document_graph.pictures:
        lines.append("_No picture assets._")
        lines.append("")
    else:
        for picture in document_graph.pictures.values():
            linked_element = picture_element_lookup.get(safe_getattr(picture, "picture_id"))
            source = safe_getattr(picture, "metadata", "source") or safe_getattr(linked_element, "source")
            lines.extend(
                [
                    f"### {safe_getattr(picture, 'picture_id', default='')}",
                    f"- document id: `{safe_getattr(picture, 'document_id', default='')}`",
                    f"- element id: `{safe_getattr(linked_element, 'element_id', default='')}`",
                    f"- page_start/page_end: `{format_page_range(safe_getattr(source, 'page_start'), safe_getattr(source, 'page_end'))}`",
                    f"- image path: `{safe_getattr(picture, 'image_path', default='')}`",
                    f"- caption/text: `{preview_text(safe_getattr(picture, 'metadata', 'caption') or safe_getattr(picture, 'ocr_text'), limit=240)}`",
                    "- metadata:",
                    "```json",
                    sanitize_code_block(format_json_block(safe_getattr(picture, 'metadata'))),
                    "```",
                    "",
                ]
            )

    lines.extend(
        build_chunk_section(
            heading="## Initial Chunks",
            chunks=initial_chunks,
            note="Structural chunks produced directly by parsing before model classification.",
        )
    )
    lines.extend(
        build_chunk_section(
            heading="## Post-Classification Chunks",
            chunks=post_classification_chunks,
            note=(
                "Final chunk view after document classification and hybrid chunk-profile decision."
            ),
        )
    )

    lines.append("## Warnings")
    lines.append("")
    lines.append("### Validation")
    lines.extend(
        build_validation_summary(
            canonical_elements,
            document_graph,
            section_build_result,
        )
    )
    lines.append("")
    lines.append("### Warnings")
    warnings = build_warnings(
        canonical_elements,
        document_graph,
        section_build_result,
    )
    if not warnings:
        lines.append("- None")
    else:
        lines.extend(f"- {warning}" for warning in warnings)

    lines.append("")
    return "\n".join(lines)


def infer_structural_profile_inference(document_graph: Any) -> Any:
    inferer = ChunkingProfileInferer()
    ordered_sections = sorted(
        document_graph.sections.values(),
        key=lambda value: value.sequence_number or 0,
    )
    section_elements_by_id = {
        section.section_id: document_graph.get_section_elements(section.section_id)
        for section in ordered_sections
    }
    return inferer.infer_result(
        document_title=safe_getattr(document_graph, "document", "title"),
        sections=ordered_sections,
        section_elements_by_id=section_elements_by_id,
    )


def build_structural_profile_inference_section(structural_profile_inference: Any) -> list[str]:
    statistics = (
        structural_profile_inference.statistics.to_debug_dict()
        if hasattr(structural_profile_inference, "statistics")
        else {}
    )
    scores = (
        structural_profile_inference.scores_by_name()
        if hasattr(structural_profile_inference, "scores_by_name")
        else {}
    )
    reasons = (
        structural_profile_inference.reasons_by_name()
        if hasattr(structural_profile_inference, "reasons_by_name")
        else {}
    )
    return [
        "## Structural Profile Inference",
        f"- selected profile: `{display_value(safe_getattr(structural_profile_inference, 'selected_profile'))}`",
        f"- confidence: `{safe_getattr(structural_profile_inference, 'confidence', default='')}`",
        "- scores:",
        "```json",
        sanitize_code_block(json.dumps(scores, indent=2)),
        "```",
        "- selected profile reasons:",
        "```json",
        sanitize_code_block(
            json.dumps(
                reasons.get(
                    display_value(
                        safe_getattr(structural_profile_inference, "selected_profile")
                    ),
                    [],
                ),
                indent=2,
            )
        ),
        "```",
        "- key statistics:",
        "```json",
        sanitize_code_block(json.dumps(statistics, indent=2)),
        "```",
        "",
    ]


def build_document_classification_section(
    *,
    document_graph: Any,
    structural_profile_inference: Any,
    provisional_chunking_policy: Any | None,
    document_classification: Any | None,
    document_type_decision: Any | None,
    classification_provider: Any | None,
    initial_chunks: list[Any],
    post_classification_chunks: list[Any],
) -> list[str]:
    if document_classification is None:
        return [
            "## Document Classification",
            "- classification: `not run`",
            "",
        ]

    processing_metadata = safe_getattr(
        document_classification,
        "result",
        "processing_metadata",
    )
    evidence = safe_getattr(document_classification, "result", "evidence", default=[]) or []
    errors = safe_getattr(processing_metadata, "errors", default=[]) or []
    classification_statistics = {
        "parser_title_hint_document_type": display_value(
            safe_getattr(document_graph, "document", "document_type")
        ),
        "predicted_document_type": display_value(
            safe_getattr(document_classification, "document_type")
        ),
        "classification_confidence_score": safe_getattr(
            document_classification,
            "result",
            "confidence_score",
            default="",
        ),
        "structural_profile": display_value(
            safe_getattr(structural_profile_inference, "selected_profile")
        ),
        "structural_confidence": safe_getattr(
            structural_profile_inference,
            "confidence",
            default="",
        ),
        "provisional_chunking_profile": display_value(
            safe_getattr(provisional_chunking_policy, "profile_name")
        ),
        "effective_document_type": display_value(
            safe_getattr(document_type_decision, "effective_document_type")
        ),
        "effective_chunking_profile": display_value(
            safe_getattr(document_type_decision, "effective_chunking_profile")
        ),
        "decision_confidence": safe_getattr(
            document_type_decision,
            "confidence",
            default="",
        ),
        "should_rechunk": safe_getattr(
            document_type_decision,
            "should_rechunk",
            default=False,
        ),
        "initial_chunk_count": len(initial_chunks),
        "post_classification_chunk_count": len(post_classification_chunks),
        "initial_chunk_types": count_by_type(
            initial_chunks,
            attribute_name="chunk_type",
        ),
        "post_classification_chunk_types": count_by_type(
            post_classification_chunks,
            attribute_name="chunk_type",
        ),
    }
    lines = [
        "## Document Classification",
        f"- provider: `{type(classification_provider).__name__ if classification_provider is not None else ''}`",
        f"- ollama base url: `{safe_getattr(classification_provider, 'base_url', default='')}`",
        f"- parser/title hint document type: `{display_value(safe_getattr(document_graph, 'document', 'document_type'))}`",
        f"- classification id: `{safe_getattr(document_classification, 'result', 'classification_id', default='')}`",
        f"- predicted document type: `{display_value(safe_getattr(document_classification, 'document_type'))}`",
        f"- confidence score: `{safe_getattr(document_classification, 'result', 'confidence_score', default='')}`",
        f"- model name: `{safe_getattr(processing_metadata, 'model_name', default='')}`",
        f"- model type: `{safe_getattr(processing_metadata, 'model_type', default='')}`",
        f"- prompt version: `{safe_getattr(processing_metadata, 'prompt_version', default='')}`",
        f"- rationale: `{preview_text(safe_getattr(document_classification, 'result', 'rationale'), limit=320)}`",
        "- evidence:",
        "```json",
        sanitize_code_block(json.dumps(evidence, indent=2)),
        "```",
        "- metadata errors:",
        "```json",
        sanitize_code_block(json.dumps(errors, indent=2)),
        "```",
    ]

    if document_type_decision is None:
        lines.append("- hybrid decision: `not resolved`")
        lines.append("")
        return lines

    lines.extend(
        [
            "## Hybrid Chunking Decision",
            f"- provisional chunking profile: `{display_value(safe_getattr(provisional_chunking_policy, 'profile_name'))}`",
            f"- structural profile: `{display_value(safe_getattr(structural_profile_inference, 'selected_profile'))}`",
            f"- structural confidence: `{safe_getattr(structural_profile_inference, 'confidence', default='')}`",
            f"- effective document type: `{display_value(safe_getattr(document_type_decision, 'effective_document_type'))}`",
            f"- effective chunking profile: `{display_value(safe_getattr(document_type_decision, 'effective_chunking_profile'))}`",
            f"- decision confidence: `{safe_getattr(document_type_decision, 'confidence', default='')}`",
            f"- should rechunk: `{safe_getattr(document_type_decision, 'should_rechunk', default=False)}`",
            "- decision reasons:",
            "```json",
            sanitize_code_block(
                json.dumps(
                    safe_getattr(document_type_decision, "reasons", default=[]) or [],
                    indent=2,
                )
            ),
            "```",
            "### Classification Statistics",
            "```json",
            sanitize_code_block(json.dumps(classification_statistics, indent=2)),
            "```",
            "",
        ]
    )
    return lines


def build_chunk_section(
    *,
    heading: str,
    chunks: list[Any],
    note: str,
) -> list[str]:
    lines = [heading, f"- note: {note}", ""]
    if not chunks:
        lines.append("_No chunks._")
        lines.append("")
        return lines

    ordered_chunks = sort_chunks(chunks)
    lines.append("### Chunk Summary")
    lines.append(
        format_table(
            headers=[
                "sequence",
                "chunk_id",
                "section_id",
                "section_path",
                "chunk_pos",
                "type",
                "elements",
                "pages",
                "content preview",
            ],
            rows=[
                [
                    safe_getattr(chunk, "sequence_number"),
                    safe_getattr(chunk, "chunk_id"),
                    safe_getattr(chunk, "section_id"),
                    format_section_path(safe_getattr(chunk, "section_path")),
                    (
                        f"{safe_getattr(chunk, 'chunk_index', default='')}/"
                        f"{safe_getattr(chunk, 'chunk_total', default='')}"
                    ),
                    display_value(safe_getattr(chunk, "chunk_type")),
                    len(safe_getattr(chunk, "element_ids", default=[]) or []),
                    format_page_range(
                        safe_getattr(chunk, "source", "page_start"),
                        safe_getattr(chunk, "source", "page_end"),
                    ),
                    preview_text(safe_getattr(chunk, "content"), limit=120),
                ]
                for chunk in ordered_chunks[:20]
            ],
        )
    )
    lines.append("")

    for chunk in ordered_chunks:
        token_count = safe_getattr(chunk, "statistics", "token_count_estimate")
        lines.extend(
            [
                f"### {safe_getattr(chunk, 'chunk_id', default='')}",
                f"- document id: `{safe_getattr(chunk, 'document_id', default='')}`",
                f"- section id: `{safe_getattr(chunk, 'section_id', default='')}`",
                f"- sequence_number: `{safe_getattr(chunk, 'sequence_number', default='')}`",
                f"- chunk_index/chunk_total: `{safe_getattr(chunk, 'chunk_index', default='')}/{safe_getattr(chunk, 'chunk_total', default='')}`",
                f"- chunk type: `{display_value(safe_getattr(chunk, 'chunk_type'))}`",
                f"- page_start/page_end: `{format_page_range(safe_getattr(chunk, 'source', 'page_start'), safe_getattr(chunk, 'source', 'page_end'))}`",
                f"- token_count: `{token_count if token_count is not None else ''}`",
                f"- section_path: `{format_section_path(safe_getattr(chunk, 'section_path'))}`",
                f"- element_ids ({len(safe_getattr(chunk, 'element_ids', default=[]) or [])}): `{format_list_summary(safe_getattr(chunk, 'element_ids', default=[]))}`",
                f"- table_ids ({len(safe_getattr(chunk, 'table_ids', default=[]) or [])}): `{format_list_summary(safe_getattr(chunk, 'table_ids', default=[]))}`",
                f"- picture_ids ({len(safe_getattr(chunk, 'picture_ids', default=[]) or [])}): `{format_list_summary(safe_getattr(chunk, 'picture_ids', default=[]))}`",
                f"- embedding_text preview: `{preview_text(safe_getattr(chunk, 'embedding_text'), limit=240)}`",
                "- content:",
                "```text",
                sanitize_code_block(safe_getattr(chunk, "content", default="")),
                "```",
                "",
            ]
        )

    return lines


def resolve_ordered_sections(document_graph: Any) -> list[Any]:
    return sorted(
        document_graph.sections.values(),
        key=lambda value: value.sequence_number or 0,
    )


def resolve_section_elements_by_id(document_graph: Any) -> dict[str, list[Any]]:
    ordered_sections = resolve_ordered_sections(document_graph)
    return {
        section.section_id: document_graph.get_section_elements(section.section_id)
        for section in ordered_sections
    }


def run_document_classification(
    *,
    document_graph: Any,
    id_generator: IdGenerator,
) -> tuple[Any, Any]:
    classification_service = DebugClassificationService()
    provider = OllamaLLMProvider()
    workflow = DocumentClassificationWorkflow(
        llm_service=LLMService(provider),
        classification_service=classification_service,
        document_classification_validator=DocumentClassificationValidator(),
        id_generator=id_generator,
    )
    classification = workflow.classify_document(document_graph)
    return classification, provider


def resolve_post_classification_chunks(
    *,
    document_graph: Any,
    graph_builder: DocumentGraphBuilder,
    document_classification: Any,
    structural_profile_inference: Any,
) -> tuple[Any, Any, list[Any]]:
    ordered_sections = resolve_ordered_sections(document_graph)
    section_elements_by_id = resolve_section_elements_by_id(document_graph)
    policy_resolver = DocumentChunkingPolicyResolver()
    provisional_chunking_policy = policy_resolver.resolve(
        document_title=safe_getattr(document_graph, "document", "title"),
        document_type=safe_getattr(document_graph, "document", "document_type"),
        sections=ordered_sections,
        section_elements_by_id=section_elements_by_id,
    )
    document_type_decision = HybridDocumentTypeResolver().resolve(
        parser_title_hint=safe_getattr(document_graph, "document", "document_type"),
        structural_inference=structural_profile_inference,
        classification=document_classification,
        provisional_chunking_profile=safe_getattr(
            provisional_chunking_policy,
            "profile_name",
        ),
    )
    if not safe_getattr(document_type_decision, "should_rechunk", default=False):
        return (
            provisional_chunking_policy,
            document_type_decision,
            sort_chunks(list(document_graph.chunks.values())),
        )

    return (
        provisional_chunking_policy,
        document_type_decision,
        graph_builder.chunk_builder.build_chunks(
            graph=document_graph,
            sections=ordered_sections,
            document_type_override=safe_getattr(
                document_type_decision,
                "effective_document_type",
            ),
            chunking_profile_override=safe_getattr(
                document_type_decision,
                "effective_chunking_profile",
            ),
        ),
    )


def main() -> int:
    args = parse_args()

    try:
        input_path = resolve_input_path(args.input)
        output_path = resolve_output_path(input_path, args.output)
        ensure_directory(output_path.parent)

        file_hash, content_hash = compute_debug_hashes(input_path)

        id_generator = IdGenerator()
        document_id = id_generator.new_id(IdPrefix.DOCUMENT)
        parser = DoclingParser()
        normalizer = DoclingDocumentNormalizer()
        graph_builder = DocumentGraphBuilder(
            id_generator=id_generator,
            section_builder=SectionBuilder(id_generator),
        )

        raw_parsed_document = parser.parse(str(input_path))
        canonical_elements = normalizer.normalize(
            raw_parsed_document,
            document_id,
        )
        document_graph = graph_builder.build(
            document_id=document_id,
            file_path=str(input_path),
            hashes=DocumentHashes(
                file_hash=file_hash,
                content_hash=content_hash,
            ),
            canonical_elements=canonical_elements,
            raw_parsed_document=raw_parsed_document,
        )
        section_build_result = graph_builder.last_section_build_result
        initial_chunks = sort_chunks(list(document_graph.chunks.values()))
        structural_profile_inference = infer_structural_profile_inference(
            document_graph
        )
        document_classification, classification_provider = run_document_classification(
            document_graph=document_graph,
            id_generator=id_generator,
        )
        (
            provisional_chunking_policy,
            document_type_decision,
            post_classification_chunks,
        ) = resolve_post_classification_chunks(
            document_graph=document_graph,
            graph_builder=graph_builder,
            document_classification=document_classification,
            structural_profile_inference=structural_profile_inference,
        )

        report = build_report(
            input_path=input_path,
            output_path=output_path,
            file_hash=file_hash,
            content_hash=content_hash,
            raw_parsed_document=raw_parsed_document,
            canonical_elements=canonical_elements,
            document_graph=document_graph,
            section_build_result=section_build_result,
            initial_chunks=initial_chunks,
            post_classification_chunks=post_classification_chunks,
            structural_profile_inference=structural_profile_inference,
            provisional_chunking_policy=provisional_chunking_policy,
            document_classification=document_classification,
            document_type_decision=document_type_decision,
            classification_provider=classification_provider,
        )
        write_markdown_report(output_path, report)

        print(output_path)
        return 0
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except ApplicationError as exc:
        print(f"{exc.error_code}: {exc.message}", file=sys.stderr)
        if exc.details:
            print(format_json_block(exc.details), file=sys.stderr)
        return 1
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
