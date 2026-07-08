from src.application.workflows.parsing.builders.document_graph.asset_nearby_text_enricher import (
    AssetNearbyTextEnricher,
)
from src.application.workflows.parsing.builders.chunking.text.tokenization import (
    WhitespaceChunkTokenCounter,
)
from src.domain.assets import TableAsset
from src.domain.common import ElementType, SourceLocation
from src.domain.document import Document, DocumentGraph, DocumentHashes, DocumentSection
from src.domain.elements import CanonicalElement


def _make_document() -> Document:
    return Document(
        document_id="doc_001",
        file_name="manual.pdf",
        file_path="data/input/manual.pdf",
        hashes=DocumentHashes(file_hash="hash_1", content_hash="content_1"),
    )


def test_enrich_finds_nearby_text_for_table_and_picture_assets() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.add_section(
        DocumentSection(section_id="sec_1", document_id="doc_001", title="Section")
    )

    intro_text = CanonicalElement(
        element_id="el_intro",
        document_id="doc_001",
        element_type=ElementType.TEXT,
        text="This table lists the spare parts.",
        parent_section_id="sec_1",
        source=SourceLocation(page_start=1, page_end=1),
    )
    table_element = CanonicalElement(
        element_id="el_table",
        document_id="doc_001",
        element_type=ElementType.TABLE,
        table_id="table_1",
        parent_section_id="sec_1",
        source=SourceLocation(page_start=1, page_end=1),
    )
    picture_element = CanonicalElement(
        element_id="el_picture",
        document_id="doc_001",
        element_type=ElementType.PICTURE,
        picture_id="picture_1",
        parent_section_id="sec_1",
        source=SourceLocation(page_start=1, page_end=1),
    )
    outro_text = CanonicalElement(
        element_id="el_outro",
        document_id="doc_001",
        element_type=ElementType.TEXT,
        text="Figure 1 shows the assembly.",
        parent_section_id="sec_1",
        source=SourceLocation(page_start=1, page_end=1),
    )

    for element in (intro_text, table_element, picture_element, outro_text):
        graph.add_element(element)
    graph.sections["sec_1"].element_ids = [
        "el_intro",
        "el_table",
        "el_picture",
        "el_outro",
    ]

    graph.tables["table_1"] = TableAsset(
        table_id="table_1",
        document_id="doc_001",
        markdown="| Part | Qty |\n|---|---|\n| HP-001 | 1 |",
    )
    from src.domain.assets import PictureAsset

    graph.pictures["picture_1"] = PictureAsset(
        picture_id="picture_1",
        document_id="doc_001",
    )

    AssetNearbyTextEnricher(context_window=2).enrich(graph)

    assert graph.tables["table_1"].metadata.nearby_text is not None
    assert "spare parts" in graph.tables["table_1"].metadata.nearby_text
    assert graph.pictures["picture_1"].metadata.nearby_text is not None
    assert "assembly" in graph.pictures["picture_1"].metadata.nearby_text


def test_enrich_skips_assets_with_no_owning_element() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.tables["orphan_table"] = TableAsset(
        table_id="orphan_table",
        document_id="doc_001",
        markdown="| A |",
    )

    # Should not raise even though no element references this table.
    AssetNearbyTextEnricher(context_window=2).enrich(graph)

    assert graph.tables["orphan_table"].metadata.nearby_text is None


def test_enrich_does_nothing_when_context_window_is_zero() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.add_section(
        DocumentSection(section_id="sec_1", document_id="doc_001", title="Section")
    )
    table_element = CanonicalElement(
        element_id="el_table",
        document_id="doc_001",
        element_type=ElementType.TABLE,
        table_id="table_1",
        parent_section_id="sec_1",
    )
    graph.add_element(table_element)
    graph.sections["sec_1"].element_ids = ["el_table"]
    graph.tables["table_1"] = TableAsset(
        table_id="table_1",
        document_id="doc_001",
        markdown="| A |",
    )

    AssetNearbyTextEnricher(context_window=0).enrich(graph)

    assert graph.tables["table_1"].metadata.nearby_text is None


def test_enrich_truncates_nearby_text_with_token_counter_budget() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.add_section(
        DocumentSection(section_id="sec_1", document_id="doc_001", title="Section")
    )
    intro_text = CanonicalElement(
        element_id="el_intro",
        document_id="doc_001",
        element_type=ElementType.TEXT,
        text=(
            "alpha beta gamma delta epsilon zeta eta theta "
            "iota kappa lambda mu nu"
        ),
        parent_section_id="sec_1",
        source=SourceLocation(page_start=1, page_end=1),
    )
    table_element = CanonicalElement(
        element_id="el_table",
        document_id="doc_001",
        element_type=ElementType.TABLE,
        table_id="table_1",
        parent_section_id="sec_1",
        source=SourceLocation(page_start=1, page_end=1),
    )

    for element in (intro_text, table_element):
        graph.add_element(element)
    graph.sections["sec_1"].element_ids = ["el_intro", "el_table"]
    graph.tables["table_1"] = TableAsset(
        table_id="table_1",
        document_id="doc_001",
        markdown="| Part | Qty |",
    )

    AssetNearbyTextEnricher(
        context_window=1,
        max_context_tokens=2,
        token_counter=WhitespaceChunkTokenCounter(),
    ).enrich(graph)

    assert graph.tables["table_1"].metadata.nearby_text == (
        "alpha beta gamma delta epsilon zeta eta theta "
        "iota kappa lambda mu"
    )
