from src.application.workflows.parsing.builders.document_graph.cross_references.chunk_asset_number_index import (
    ChunkAssetNumberIndex,
    extract_leading_figure_number,
    extract_leading_table_number,
)
from src.domain.assets import PictureAsset, TableAsset
from src.domain.assets.asset_metadata import AssetMetadata
from src.domain.common import SourceLocation
from src.domain.document.entities.chunk import DocumentChunk


def make_chunk(
    *,
    chunk_id: str,
    table_ids: list[str] | None = None,
    picture_ids: list[str] | None = None,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        content="content",
        source=SourceLocation(page_start=1, page_end=1),
        table_ids=table_ids or [],
        picture_ids=picture_ids or [],
    )


def make_table(*, table_id: str, caption: str | None) -> TableAsset:
    return TableAsset(
        table_id=table_id,
        document_id="doc_001",
        markdown="| a | b |",
        metadata=AssetMetadata(caption=caption),
    )


def make_picture(*, picture_id: str, caption: str | None) -> PictureAsset:
    return PictureAsset(
        picture_id=picture_id,
        document_id="doc_001",
        metadata=AssetMetadata(caption=caption),
    )


def test_extract_leading_table_number_handles_dotted_numbers() -> None:
    assert extract_leading_table_number("Table 3. Spare parts list") == "3"
    assert extract_leading_table_number("Table 3.2: Torque values") == "3.2"


def test_extract_leading_table_number_returns_none_for_uncaptioned_text() -> None:
    assert extract_leading_table_number("Spare parts list") is None


def test_extract_leading_figure_number_handles_abbreviation() -> None:
    assert extract_leading_figure_number("Fig. 2 Oil filter assembly") == "2"
    assert extract_leading_figure_number("Figure 5: Wiring diagram") == "5"


def test_index_maps_table_number_to_containing_chunk() -> None:
    table = make_table(table_id="table_1", caption="Table 3. Spare parts list")
    chunk = make_chunk(chunk_id="a", table_ids=["table_1"])
    index = ChunkAssetNumberIndex(chunks=[chunk], tables={"table_1": table}, pictures={})

    assert [c.chunk_id for c in index.table_matches("3")] == ["a"]
    assert index.table_matches("9") == []


def test_index_maps_figure_number_to_containing_chunk() -> None:
    picture = make_picture(picture_id="pic_1", caption="Figure 2: Oil filter assembly")
    chunk = make_chunk(chunk_id="a", picture_ids=["pic_1"])
    index = ChunkAssetNumberIndex(chunks=[chunk], tables={}, pictures={"pic_1": picture})

    assert [c.chunk_id for c in index.figure_matches("2")] == ["a"]


def test_index_ignores_assets_with_no_caption() -> None:
    table = make_table(table_id="table_1", caption=None)
    chunk = make_chunk(chunk_id="a", table_ids=["table_1"])
    index = ChunkAssetNumberIndex(chunks=[chunk], tables={"table_1": table}, pictures={})

    assert index.table_matches("3") == []


def test_index_ignores_captions_with_no_leading_number() -> None:
    table = make_table(table_id="table_1", caption="Spare parts list")
    chunk = make_chunk(chunk_id="a", table_ids=["table_1"])
    index = ChunkAssetNumberIndex(chunks=[chunk], tables={"table_1": table}, pictures={})

    assert index.table_matches("3") == []


def test_table_and_figure_labels_do_not_collide() -> None:
    table = make_table(table_id="table_1", caption="Table 3. Spare parts list")
    picture = make_picture(picture_id="pic_1", caption="Figure 3: Oil filter assembly")
    chunk = make_chunk(chunk_id="a", table_ids=["table_1"], picture_ids=["pic_1"])
    index = ChunkAssetNumberIndex(
        chunks=[chunk], tables={"table_1": table}, pictures={"pic_1": picture}
    )

    assert [c.chunk_id for c in index.table_matches("3")] == ["a"]
    assert [c.chunk_id for c in index.figure_matches("3")] == ["a"]
