from src.application.workflows.parsing.builders.chunking.builders.fragment.asset_context_resolver import (
    AssetContextResolver,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import ElementType, SourceLocation
from src.domain.elements import CanonicalElement


def make_element(
    *,
    element_id: str,
    element_type: ElementType,
    text: str | None,
    page_start: int | None = 1,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        source=SourceLocation(page_start=page_start, page_end=page_start),
    )


def make_resolver(
    *,
    asset_context_window: int = 1,
    asset_context_max_tokens: int = 72,
    element_contributes_to_chunk=lambda element: True,
) -> AssetContextResolver:
    return AssetContextResolver(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=200, chunk_overlap=0),
        asset_context_window=asset_context_window,
        asset_context_max_tokens=asset_context_max_tokens,
        element_contributes_to_chunk=element_contributes_to_chunk,
    )


def test_nearby_text_returns_none_when_window_is_zero() -> None:
    resolver = make_resolver(asset_context_window=0)
    elements = [
        make_element(element_id="txt_1", element_type=ElementType.TEXT, text="Before the table."),
        make_element(element_id="tbl_1", element_type=ElementType.TABLE, text="| a |"),
    ]

    result = resolver.nearby_text(elements=elements, index=1)

    assert result is None


def test_nearby_text_pulls_in_preceding_and_following_elements_within_window() -> None:
    resolver = make_resolver(asset_context_window=1)
    elements = [
        make_element(element_id="txt_before", element_type=ElementType.TEXT, text="Context before."),
        make_element(element_id="tbl_1", element_type=ElementType.TABLE, text="| a |"),
        make_element(element_id="txt_after", element_type=ElementType.TEXT, text="Context after."),
    ]

    result = resolver.nearby_text(elements=elements, index=1)

    assert result == "Context before.\n\nContext after."


def test_nearby_text_does_not_reach_beyond_the_configured_window() -> None:
    resolver = make_resolver(asset_context_window=1)
    elements = [
        make_element(element_id="txt_far", element_type=ElementType.TEXT, text="Too far away."),
        make_element(element_id="txt_near", element_type=ElementType.TEXT, text="Just before."),
        make_element(element_id="tbl_1", element_type=ElementType.TABLE, text="| a |"),
    ]

    result = resolver.nearby_text(elements=elements, index=2)

    assert result == "Just before."


def test_nearby_text_excludes_elements_that_do_not_contribute_to_chunk() -> None:
    resolver = make_resolver(
        asset_context_window=1,
        element_contributes_to_chunk=lambda element: element.element_id != "txt_before",
    )
    elements = [
        make_element(element_id="txt_before", element_type=ElementType.TEXT, text="Excluded caption run."),
        make_element(element_id="tbl_1", element_type=ElementType.TABLE, text="| a |"),
        make_element(element_id="txt_after", element_type=ElementType.TEXT, text="Included context."),
    ]

    result = resolver.nearby_text(elements=elements, index=1)

    assert result == "Included context."


def test_nearby_text_excludes_element_types_outside_the_text_bearing_set() -> None:
    resolver = make_resolver(asset_context_window=1)
    elements = [
        make_element(element_id="pic_before", element_type=ElementType.PICTURE, text="Figure caption."),
        make_element(element_id="tbl_1", element_type=ElementType.TABLE, text="| a |"),
        make_element(element_id="txt_after", element_type=ElementType.TEXT, text="Real context."),
    ]

    result = resolver.nearby_text(elements=elements, index=1)

    assert result == "Real context."


def test_nearby_text_excludes_candidates_on_a_distant_page() -> None:
    resolver = make_resolver(asset_context_window=1)
    elements = [
        make_element(
            element_id="txt_far_page",
            element_type=ElementType.TEXT,
            text="From a much earlier page.",
            page_start=1,
        ),
        make_element(element_id="tbl_1", element_type=ElementType.TABLE, text="| a |", page_start=5),
    ]

    result = resolver.nearby_text(elements=elements, index=1)

    assert result is None


def test_nearby_text_allows_candidates_missing_page_information() -> None:
    resolver = make_resolver(asset_context_window=1)
    elements = [
        make_element(
            element_id="txt_no_page",
            element_type=ElementType.TEXT,
            text="No page metadata at all.",
            page_start=None,
        ),
        make_element(element_id="tbl_1", element_type=ElementType.TABLE, text="| a |", page_start=5),
    ]

    result = resolver.nearby_text(elements=elements, index=1)

    assert result == "No page metadata at all."


def test_nearby_text_truncates_to_the_configured_token_budget() -> None:
    resolver = make_resolver(asset_context_window=1, asset_context_max_tokens=3)
    elements = [
        make_element(
            element_id="txt_before",
            element_type=ElementType.TEXT,
            text="one two three four five",
        ),
        make_element(element_id="tbl_1", element_type=ElementType.TABLE, text="| a |"),
    ]

    result = resolver.nearby_text(elements=elements, index=1)

    assert result == "one two three"


def test_nearby_text_stops_once_the_token_budget_is_exhausted_across_candidates() -> None:
    resolver = make_resolver(asset_context_window=1, asset_context_max_tokens=3)
    elements = [
        make_element(element_id="txt_before", element_type=ElementType.TEXT, text="alpha beta gamma"),
        make_element(element_id="tbl_1", element_type=ElementType.TABLE, text="| a |"),
        make_element(element_id="txt_after", element_type=ElementType.TEXT, text="delta epsilon"),
    ]

    result = resolver.nearby_text(elements=elements, index=1)

    assert result == "alpha beta gamma"


def test_nearby_text_returns_none_when_no_candidates_have_text() -> None:
    resolver = make_resolver(asset_context_window=1)
    elements = [
        make_element(element_id="txt_before", element_type=ElementType.TEXT, text=""),
        make_element(element_id="tbl_1", element_type=ElementType.TABLE, text="| a |"),
    ]

    result = resolver.nearby_text(elements=elements, index=1)

    assert result is None


def test_truncate_to_asset_context_returns_none_for_empty_text() -> None:
    resolver = make_resolver(asset_context_max_tokens=5)

    text, token_count = resolver.truncate_to_asset_context(None)

    assert text is None
    assert token_count == 0


def test_truncate_to_asset_context_truncates_to_max_tokens() -> None:
    resolver = make_resolver(asset_context_max_tokens=2)

    text, token_count = resolver.truncate_to_asset_context("one two three four")

    assert text == "one two"
    assert token_count == 2
