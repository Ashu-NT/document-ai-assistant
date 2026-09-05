from src.application.workflows.parsing.normalizers.docling_element_metadata_builder import (
    DoclingElementMetadataBuilder,
)
from src.application.workflows.parsing.normalizers.table_layout.table_reconstruction_result import (
    TableReconstructionResult,
)
from src.domain.assets import TableCellSpan, TableParallelStream
from src.domain.common import ElementType


class _FakeItemExtractor:
    def __init__(
        self,
        *,
        label: str | None = None,
        content_layer: str | None = None,
        parent_ref: str | None = None,
    ) -> None:
        self.label = label
        self.content_layer = content_layer
        self.parent_ref = parent_ref

    def lower_label(self, item):
        return self.label

    def extract_content_layer(self, item):
        return self.content_layer

    def extract_parent_ref(self, item):
        return self.parent_ref


class _FakeTableExtractor:
    def __init__(self, *, dimensions=(None, None)) -> None:
        self.dimensions = dimensions

    def extract_dimensions(self, item):
        return self.dimensions


def _builder(*, item_extractor=None, table_extractor=None) -> DoclingElementMetadataBuilder:
    return DoclingElementMetadataBuilder(
        item_extractor=item_extractor or _FakeItemExtractor(),
        table_extractor=table_extractor or _FakeTableExtractor(),
    )


def test_build_populates_non_table_metadata() -> None:
    builder = _builder(
        item_extractor=_FakeItemExtractor(
            label="picture", content_layer="body", parent_ref="#/groups/0"
        )
    )

    metadata = builder.build(
        {
            "level": 2,
            "image_path": "outputs/images/deck_filler.png",
            "ocr_text": "  scanned text  ",
            "ocr_provider": "paddleocr",
            "ocr_confidence": 0.87,
        },
        raw_ref="#/pictures/0",
        element_type=ElementType.PICTURE,
        caption="Deck filler",
        layout_metadata={"layout_region_id": "page_1:lane_1"},
        markdown=None,
        table_structure=None,
    )

    assert metadata["item_label"] == "picture"
    assert metadata["raw_ref"] == "#/pictures/0"
    assert metadata["content_layer"] == "body"
    assert metadata["parent_ref"] == "#/groups/0"
    assert metadata["heading_level"] == 2
    assert metadata["layout_region_id"] == "page_1:lane_1"
    assert metadata["caption"] == "Deck filler"
    assert metadata["image_path"] == "outputs/images/deck_filler.png"
    assert metadata["ocr_text"] == "scanned text"
    assert metadata["ocr_provider"] == "paddleocr"
    assert metadata["ocr_confidence"] == 0.87
    assert "table_structure_tier" not in metadata


def test_build_defaults_to_row_grid_tier_when_rows_present() -> None:
    builder = _builder(table_extractor=_FakeTableExtractor(dimensions=(9, 9)))
    table_structure = TableReconstructionResult(rows=[["A", "B"], ["1", "2"]])

    metadata = builder.build(
        {},
        raw_ref=None,
        element_type=ElementType.TABLE,
        caption=None,
        layout_metadata=None,
        markdown="| A | B |",
        table_structure=table_structure,
    )

    assert metadata["markdown"] == "| A | B |"
    assert metadata["table_rows"] == [["A", "B"], ["1", "2"]]
    assert metadata["table_structure_tier"] == "row_grid"
    # Post-repair row/column counts must win over the pre-repair dimensions.
    assert metadata["row_count"] == 2
    assert metadata["column_count"] == 2


def test_build_upgrades_tier_to_span_aware_when_cell_spans_present() -> None:
    builder = _builder()
    table_structure = TableReconstructionResult(
        rows=[["A"]],
        cell_spans=[
            TableCellSpan(row_start=0, row_end=0, col_start=0, col_end=0, text="A")
        ],
    )

    metadata = builder.build(
        {},
        raw_ref=None,
        element_type=ElementType.TABLE,
        caption=None,
        layout_metadata=None,
        markdown=None,
        table_structure=table_structure,
    )

    assert metadata["table_structure_tier"] == "span_aware"
    assert len(metadata["table_cell_spans"]) == 1


def test_build_upgrades_tier_to_parallel_streams_when_present() -> None:
    builder = _builder()
    table_structure = TableReconstructionResult(
        rows=[["A"]],
        parallel_stream_rows=[[["A"]], [["B"]]],
        parallel_stream_descriptors=[
            TableParallelStream(
                stream_index=1,
                source_row_start=0,
                source_row_end=0,
                source_col_start=0,
                source_col_end=0,
                row_count=1,
                column_count=1,
                page_number=2,
            ),
            TableParallelStream(
                stream_index=2,
                source_row_start=0,
                source_row_end=0,
                source_col_start=1,
                source_col_end=1,
                row_count=1,
                column_count=1,
                page_number=2,
            ),
        ],
        local_reading_order="left_to_right_top_to_bottom",
        reconstruction_version="2",
    )

    metadata = builder.build(
        {},
        raw_ref=None,
        element_type=ElementType.TABLE,
        caption=None,
        layout_metadata=None,
        markdown=None,
        table_structure=table_structure,
    )

    assert metadata["table_structure_tier"] == "parallel_streams"
    assert metadata["table_parallel_stream_count"] == 2
    assert metadata["table_region_partition_version"] == "2"
    assert metadata["table_local_reading_order"] == "left_to_right_top_to_bottom"
    assert metadata["table_parallel_stream_descriptors"][0]["page_number"] == 2


def test_build_extracts_form_fields_from_graph_key_value_links() -> None:
    builder = _builder()

    metadata = builder.build(
        {
            "graph": {
                "cells": [
                    {"cell_id": 0, "label": "key", "text": "Model"},
                    {"cell_id": 1, "label": "value", "text": "HP-001"},
                ],
                "links": [
                    {"label": "to_value", "source_cell_id": 0, "target_cell_id": 1},
                ],
            }
        },
        raw_ref=None,
        element_type=ElementType.FORM,
        caption=None,
        layout_metadata=None,
        markdown=None,
        table_structure=None,
    )

    assert metadata["form_fields"] == [
        {"label": "key", "key_text": "Model", "value_text": "HP-001", "cell_id": 0}
    ]


def test_build_extracts_checkbox_field_with_no_linked_value() -> None:
    builder = _builder()

    metadata = builder.build(
        {
            "graph": {
                "cells": [
                    {"cell_id": 0, "label": "checkbox", "text": "Approved"},
                ],
                "links": [],
            }
        },
        raw_ref=None,
        element_type=ElementType.FORM,
        caption=None,
        layout_metadata=None,
        markdown=None,
        table_structure=None,
    )

    assert metadata["form_fields"] == [
        {"label": "checkbox", "key_text": "Approved", "value_text": None, "cell_id": 0}
    ]


def test_build_extracts_form_fields_from_real_docling_graph_objects() -> None:
    # Regression test: docling_core's real GraphLink/GraphCell.label are
    # Enum members, not plain strings (GraphLinkLabel is a plain Enum, so
    # str() on it gives "GraphLinkLabel.TO_VALUE", not "to_value") -- a dict-
    # shaped fake graph with string labels would pass even if the value-cell
    # linking logic couldn't handle real Docling output at all.
    from docling_core.types.doc import (
        GraphCell,
        GraphCellLabel,
        GraphData,
        GraphLink,
        GraphLinkLabel,
    )

    builder = _builder()
    graph = GraphData(
        cells=[
            GraphCell(cell_id=0, label=GraphCellLabel.KEY, text="Model", orig="Model"),
            GraphCell(cell_id=1, label=GraphCellLabel.VALUE, text="HP-001", orig="HP-001"),
        ],
        links=[
            GraphLink(
                label=GraphLinkLabel.TO_VALUE, source_cell_id=0, target_cell_id=1
            ),
        ],
    )

    metadata = builder.build(
        {"graph": graph},
        raw_ref=None,
        element_type=ElementType.FORM,
        caption=None,
        layout_metadata=None,
        markdown=None,
        table_structure=None,
    )

    assert metadata["form_fields"] == [
        {"label": "key", "key_text": "Model", "value_text": "HP-001", "cell_id": 0}
    ]


def test_build_skips_form_fields_when_graph_missing() -> None:
    builder = _builder()

    metadata = builder.build(
        {},
        raw_ref=None,
        element_type=ElementType.FORM,
        caption=None,
        layout_metadata=None,
        markdown=None,
        table_structure=None,
    )

    assert "form_fields" not in metadata


def test_build_ignores_orphan_value_cell_with_no_key_link() -> None:
    builder = _builder()

    metadata = builder.build(
        {
            "graph": {
                "cells": [
                    {"cell_id": 0, "label": "value", "text": "Unlinked"},
                ],
                "links": [],
            }
        },
        raw_ref=None,
        element_type=ElementType.FORM,
        caption=None,
        layout_metadata=None,
        markdown=None,
        table_structure=None,
    )

    assert "form_fields" not in metadata


def test_build_falls_back_to_markdown_only_tier_without_structure() -> None:
    builder = _builder()

    metadata = builder.build(
        {},
        raw_ref=None,
        element_type=ElementType.TABLE,
        caption=None,
        layout_metadata=None,
        markdown="| A |",
        table_structure=None,
    )

    assert metadata["table_structure_tier"] == "markdown_only"
