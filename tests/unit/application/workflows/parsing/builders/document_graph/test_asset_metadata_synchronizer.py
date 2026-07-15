from src.application.workflows.parsing.builders.document_graph.asset_metadata_synchronizer import (
    AssetMetadataSynchronizer,
)
from src.domain.assets import AssetMetadata, PictureAsset, TableAsset, TableCellSpan
from src.domain.common import ElementType, ParserMetadata
from src.domain.document import Document, DocumentGraph, DocumentHashes
from src.domain.elements import CanonicalElement


def _make_graph() -> DocumentGraph:
    return DocumentGraph(
        document=Document(
            document_id="doc_001",
            file_name="manual.pdf",
            file_path="data/input/manual.pdf",
            hashes=DocumentHashes(file_hash="hash_1", content_hash="content_1"),
        )
    )


def test_sync_forwards_table_structure_fields_onto_parser_extra() -> None:
    graph = _make_graph()
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="| Parameter | Value |",
        rows=[["Parameter", "Value"], ["Bore", "25mm"]],
        row_ids=["table_001:row:0", "table_001:row:1"],
        cell_spans=[
            TableCellSpan(row_start=0, row_end=0, col_start=0, col_end=0, text="Parameter"),
        ],
        row_count=2,
        column_count=2,
        table_shape="specification_matrix",
        table_structure_quality=0.87,
        header_paths=[["Parameter"], ["Value"]],
        axis_summary={"rows": "parameter", "columns": "value"},
        metadata=AssetMetadata(caption="Bearing specifications", nearby_text="See section 7."),
    )
    graph.tables["table_001"] = table
    element = CanonicalElement(
        element_id="el_1",
        document_id="doc_001",
        element_type=ElementType.TABLE,
        table_id="table_001",
        parser_metadata=ParserMetadata(parser_name="docling", extra={}),
    )
    graph.add_element(element)

    AssetMetadataSynchronizer.sync(graph)

    extra = element.parser_metadata.extra
    assert extra["markdown"] == "| Parameter | Value |"
    assert extra["table_rows"] == [["Parameter", "Value"], ["Bore", "25mm"]]
    assert extra["table_row_ids"] == ["table_001:row:0", "table_001:row:1"]
    assert extra["table_cell_spans"] == [table.cell_spans[0].to_dict()]
    assert extra["row_count"] == 2
    assert extra["column_count"] == 2
    assert extra["table_structure_version"] == "1"
    assert extra["table_shape"] == "specification_matrix"
    assert extra["table_structure_quality"] == 0.87
    assert extra["table_header_paths_json"] == [["Parameter"], ["Value"]]
    assert extra["table_axis_summary"] == {"rows": "parameter", "columns": "value"}
    assert extra["caption"] == "Bearing specifications"
    assert extra["nearby_text"] == "See section 7."


def test_sync_omits_optional_table_structure_keys_when_unset() -> None:
    graph = _make_graph()
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="| A | B |",
        rows=[["A", "B"]],
    )
    graph.tables["table_001"] = table
    element = CanonicalElement(
        element_id="el_1",
        document_id="doc_001",
        element_type=ElementType.TABLE,
        table_id="table_001",
        parser_metadata=ParserMetadata(parser_name="docling", extra={}),
    )
    graph.add_element(element)

    AssetMetadataSynchronizer.sync(graph)

    extra = element.parser_metadata.extra
    assert "table_shape" not in extra
    assert "table_structure_quality" not in extra
    assert "table_header_paths_json" not in extra
    assert "table_axis_summary" not in extra
    assert "caption" not in extra
    assert "nearby_text" not in extra


def test_sync_forwards_picture_ocr_and_caption_fields() -> None:
    graph = _make_graph()
    picture = PictureAsset(
        picture_id="picture_001",
        document_id="doc_001",
        image_path="images/fig1.png",
        ocr_text="Warning: hot surface",
        ocr_confidence=0.93,
        ocr_provider="paddleocr",
        ocr_mode="scanned",
        metadata=AssetMetadata(caption="Figure 1", nearby_text="See below."),
    )
    graph.pictures["picture_001"] = picture
    element = CanonicalElement(
        element_id="el_2",
        document_id="doc_001",
        element_type=ElementType.PICTURE,
        picture_id="picture_001",
        parser_metadata=ParserMetadata(parser_name="docling", extra={}),
    )
    graph.add_element(element)

    AssetMetadataSynchronizer.sync(graph)

    extra = element.parser_metadata.extra
    assert extra["caption"] == "Figure 1"
    assert extra["nearby_text"] == "See below."
    assert extra["ocr_text"] == "Warning: hot surface"
    assert extra["ocr_provider"] == "paddleocr"
    assert extra["ocr_confidence"] == 0.93
    assert extra["ocr_mode"] == "scanned"
    assert extra["ocr_provenance_version"] == "1"
    assert extra["image_path"] == "images/fig1.png"


def test_sync_skips_elements_with_no_parser_metadata() -> None:
    graph = _make_graph()
    element = CanonicalElement(
        element_id="el_3",
        document_id="doc_001",
        element_type=ElementType.TEXT,
        parser_metadata=None,
    )
    graph.add_element(element)

    AssetMetadataSynchronizer.sync(graph)

    assert element.parser_metadata is None


def test_sync_skips_table_element_whose_table_id_is_not_in_graph() -> None:
    graph = _make_graph()
    element = CanonicalElement(
        element_id="el_4",
        document_id="doc_001",
        element_type=ElementType.TABLE,
        table_id="missing_table",
        parser_metadata=ParserMetadata(parser_name="docling", extra={}),
    )
    graph.add_element(element)

    AssetMetadataSynchronizer.sync(graph)

    assert element.parser_metadata.extra == {}
