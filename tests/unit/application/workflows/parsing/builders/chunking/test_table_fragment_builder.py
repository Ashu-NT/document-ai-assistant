from src.application.workflows.parsing.builders.chunking.builders.fragment.asset_context_resolver import (
    AssetContextResolver,
)
from src.application.workflows.parsing.builders.chunking.builders.fragment.table_fragment_builder import (
    TableFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import ChunkType, ElementType, ParserMetadata
from src.domain.elements import CanonicalElement


def _make_builder() -> TableFragmentBuilder:
    text_splitter = ChunkTextSplitter()
    return TableFragmentBuilder(
        text_splitter=text_splitter,
        include_table_context=False,
        asset_context_resolver=AssetContextResolver(
            text_splitter=text_splitter,
            asset_context_window=0,
            asset_context_max_tokens=0,
            element_contributes_to_chunk=lambda _element: True,
        ),
    )


def _make_table_element(*, table_category: str) -> CanonicalElement:
    return CanonicalElement(
        element_id="el_table_1",
        document_id="doc_001",
        element_type=ElementType.TABLE,
        text="| Parameter | Value |",
        parser_metadata=ParserMetadata(
            parser_name="docling",
            extra={
                "markdown": "| Parameter | Value |",
                "table_category": table_category,
            },
        ),
    )


def test_table_chunk_type_uses_maintenance_interval_category() -> None:
    chunk_type = _make_builder().table_chunk_type(
        _make_table_element(table_category="maintenance_interval_table"),
        "| Task | Daily |",
    )

    assert chunk_type == ChunkType.MAINTENANCE_INTERVAL


def test_table_chunk_type_uses_technical_data_category() -> None:
    chunk_type = _make_builder().table_chunk_type(
        _make_table_element(table_category="technical_data_table"),
        "| Parameter | Value |",
    )

    assert chunk_type == ChunkType.TECHNICAL_SPECIFICATION


def test_table_chunk_type_uses_operation_reference_category() -> None:
    chunk_type = _make_builder().table_chunk_type(
        _make_table_element(table_category="operation_reference_table"),
        "| Operating key | Meaning |",
    )

    assert chunk_type == ChunkType.OPERATION_INSTRUCTION


def _make_structured_table_element(
    *,
    element_id: str = "el_table_1",
    table_shape: str | None = None,
    table_structure_quality: float | None = None,
    header_paths: list | None = None,
    axis_summary: dict | None = None,
) -> CanonicalElement:
    extra: dict = {"markdown": "| Parameter | Value |"}
    if table_shape is not None:
        extra["table_shape"] = table_shape
    if table_structure_quality is not None:
        extra["table_structure_quality"] = table_structure_quality
    if header_paths is not None:
        extra["table_header_paths_json"] = header_paths
    if axis_summary is not None:
        extra["table_axis_summary"] = axis_summary
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TABLE,
        text="| Parameter | Value |",
        parser_metadata=ParserMetadata(parser_name="docling", extra=extra),
    )


def test_table_metadata_forwards_shape_quality_header_paths_and_axis_summary() -> None:
    element = _make_structured_table_element(
        table_shape="specification_matrix",
        table_structure_quality=0.87,
        header_paths=[["Parameter"], ["Value"]],
        axis_summary={"rows": "parameter", "columns": "value"},
    )

    metadata = TableFragmentBuilder.table_metadata(element)

    assert metadata["table_shape"] == "specification_matrix"
    assert metadata["table_structure_quality"] == 0.87
    assert metadata["header_paths"] == [["Parameter"], ["Value"]]
    assert metadata["axis_summary"] == {"rows": "parameter", "columns": "value"}


def test_table_metadata_defaults_the_four_fields_when_absent() -> None:
    element = _make_structured_table_element()

    metadata = TableFragmentBuilder.table_metadata(element)

    assert metadata["table_shape"] is None
    assert metadata["table_structure_quality"] is None
    assert metadata["header_paths"] == []
    assert metadata["axis_summary"] == {}


def test_merge_family_table_metadata_takes_first_non_null_shape_and_quality() -> None:
    elements = [
        _make_structured_table_element(element_id="el_1"),
        _make_structured_table_element(
            element_id="el_2",
            table_shape="performance_curve_matrix",
            table_structure_quality=0.75,
        ),
        _make_structured_table_element(
            element_id="el_3",
            table_shape="record_table",
            table_structure_quality=0.5,
        ),
    ]

    merged = TableFragmentBuilder.merge_family_table_metadata(elements)

    assert merged["table_shape"] == "performance_curve_matrix"
    assert merged["table_structure_quality"] == 0.75


def _make_table_element_with_rows(
    *,
    row_count: object,
    table_rows: list[list[str]] | None,
    markdown: str = "| Parameter | Value |\n| --- | --- |\n| Pressure | 16 bar |",
) -> CanonicalElement:
    extra: dict = {"markdown": markdown}
    if row_count is not None:
        extra["row_count"] = row_count
    if table_rows is not None:
        extra["table_rows"] = table_rows
    return CanonicalElement(
        element_id="el_table_1",
        document_id="doc_001",
        element_type=ElementType.TABLE,
        text=markdown,
        parser_metadata=ParserMetadata(parser_name="docling", extra=extra),
    )


class TestDegradedTableMarkdownFallback:
    """See DegradedTablePlainTextRenderer and
    TableFragmentBuilder._has_too_few_rows_for_structure - the row_count<2
    threshold is the exact one every table-structure summarizer already
    uses, not a new heuristic invented for this."""

    def test_well_structured_multi_row_table_is_unchanged(self) -> None:
        markdown = (
            "| Parameter | Value |\n| --- | --- |\n| Pressure | 16 bar |\n"
            "| Temperature | 80 C |\n| Flow | 12 l/min |"
        )
        element = _make_table_element_with_rows(
            row_count=5,
            table_rows=[
                ["Parameter", "Value"],
                ["Pressure", "16 bar"],
                ["Temperature", "80 C"],
                ["Flow", "12 l/min"],
                ["Weight", "3 kg"],
            ],
            markdown=markdown,
        )

        text = TableFragmentBuilder.table_markdown_text(element)

        assert text == markdown

    def test_legitimate_small_one_row_table_preserves_all_meaningful_values(self) -> None:
        # A genuinely tiny, well-formed one-row table - NOT a Docling
        # recognition failure, just a table that happens to have one row.
        # Production cannot reliably tell this apart from a degraded table
        # (see GenericRecordStructureSummarizer's own row_count<2 gate), so
        # both get the same safe treatment - but nothing meaningful may be
        # lost either way.
        element = _make_table_element_with_rows(
            row_count=1,
            table_rows=[["DN25", "PN16", "80 C"]],
        )

        text = TableFragmentBuilder.table_markdown_text(element)

        assert text is not None
        assert "DN25" in text
        assert "PN16" in text
        assert "80 C" in text
        # No fabricated header/separator row for a table with no real
        # header/body distinction to justify one.
        assert "---" not in text

    def test_degraded_table_with_giant_meaningful_cell_preserves_the_text_verbatim(
        self,
    ) -> None:
        giant_cell = (
            "engine type engine no. 8351446 turbocharger type TCR12-43063 "
            "turbocharger no. attached pumps testbed no. water brake type "
            "Power engine power engine speed mean eff.press."
        )
        element = _make_table_element_with_rows(
            row_count=1,
            table_rows=[[giant_cell, "12V175D-ML", "atmospheric pressure 995 mbar"]],
        )

        text = TableFragmentBuilder.table_markdown_text(element)

        assert text is not None
        assert giant_cell in text
        assert "12V175D-ML" in text
        assert "atmospheric pressure 995 mbar" in text
        assert "---" not in text
        assert "| " not in text  # no Markdown table syntax introduced

    def test_row_count_missing_entirely_is_treated_as_too_few_rows(self) -> None:
        element = _make_table_element_with_rows(
            row_count=None,
            table_rows=[["TCR12-43063", "8351446"]],
        )

        text = TableFragmentBuilder.table_markdown_text(element)

        assert text is not None
        assert "TCR12-43063" in text
        assert "8351446" in text

    def test_missing_table_rows_falls_back_to_raw_markdown_safely(self) -> None:
        markdown = "| Parameter | Value |\n| --- | --- |"
        element = _make_table_element_with_rows(
            row_count=1, table_rows=None, markdown=markdown
        )

        text = TableFragmentBuilder.table_markdown_text(element)

        # No table_rows available to render plainly - never crash, never
        # emit a blank chunk; fall back to whatever markdown text exists.
        assert text == markdown

    def test_blank_cells_fall_back_to_raw_markdown_rather_than_emit_nothing(self) -> None:
        markdown = "| Parameter | Value |\n| --- | --- |"
        element = _make_table_element_with_rows(
            row_count=1,
            table_rows=[["   ", ""]],
            markdown=markdown,
        )

        text = TableFragmentBuilder.table_markdown_text(element)

        assert text == markdown

    def test_deterministic_output_across_repeated_calls(self) -> None:
        element = _make_table_element_with_rows(
            row_count=1,
            table_rows=[["TCR12-43063", "8351446", "12V175D-ML"]],
        )

        first = TableFragmentBuilder.table_markdown_text(element)
        second = TableFragmentBuilder.table_markdown_text(element)

        assert first == second


def test_merge_family_table_metadata_unions_header_paths_and_axis_summary() -> None:
    elements = [
        _make_structured_table_element(
            element_id="el_1",
            header_paths=[["Parameter"], ["Value"]],
            axis_summary={"rows": "parameter"},
        ),
        _make_structured_table_element(
            element_id="el_2",
            header_paths=[["Value"], ["Unit"]],
            axis_summary={"rows": "parameter", "columns": "unit"},
        ),
    ]

    merged = TableFragmentBuilder.merge_family_table_metadata(elements)

    assert merged["header_paths"] == [["Parameter"], ["Value"], ["Unit"]]
    assert merged["axis_summary"] == {"rows": "parameter", "columns": "unit"}
