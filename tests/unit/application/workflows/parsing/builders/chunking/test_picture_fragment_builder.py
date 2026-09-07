from src.application.workflows.parsing.builders.chunking.builders.fragment.asset_context_resolver import (
    AssetContextResolver,
)
from src.application.workflows.parsing.builders.chunking.builders.fragment.picture_fragment_builder import (
    PictureFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import (
    BoundingBox,
    ChunkType,
    ElementType,
    ParserMetadata,
    SourceLocation,
)
from src.domain.elements import CanonicalElement


def make_picture_element(
    *,
    element_id: str = "pic_1",
    bbox: BoundingBox | None,
    page_start: int | None = 1,
    text: str | None = None,
    caption: str | None = None,
    ocr_text: str | None = None,
) -> CanonicalElement:
    extra = {}
    if caption:
        extra["caption"] = caption
    if ocr_text:
        extra["ocr_text"] = ocr_text
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.PICTURE,
        text=text,
        picture_id="picture_001",
        source=SourceLocation(page_start=page_start, page_end=page_start, bbox=bbox),
        parser_metadata=ParserMetadata(parser_name="docling", extra=extra) if extra else None,
    )


def make_text_element(
    *,
    element_id: str,
    text: str,
    page_start: int = 1,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TEXT,
        text=text,
        source=SourceLocation(page_start=page_start, page_end=page_start),
    )


def make_builder(
    *,
    page_sizes: dict[int, tuple[float, float]] | None = None,
    asset_context_window: int = 1,
    asset_context_max_tokens: int = 72,
) -> PictureFragmentBuilder:
    resolver = AssetContextResolver(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=200, chunk_overlap=20),
        asset_context_window=asset_context_window,
        asset_context_max_tokens=asset_context_max_tokens,
        element_contributes_to_chunk=lambda element: True,
    )
    return PictureFragmentBuilder(
        page_sizes=page_sizes or {},
        asset_context_resolver=resolver,
    )


def test_is_large_picture_false_without_bbox() -> None:
    builder = make_builder(page_sizes={1: (600.0, 800.0)})
    element = make_picture_element(bbox=None)

    assert builder.is_large_picture(element) is False


def test_is_large_picture_false_without_page_number() -> None:
    builder = make_builder(page_sizes={1: (600.0, 800.0)})
    element = make_picture_element(
        bbox=BoundingBox(x1=0, y1=0, x2=600, y2=800), page_start=None
    )

    assert builder.is_large_picture(element) is False


def test_is_large_picture_false_when_page_size_unknown() -> None:
    builder = make_builder(page_sizes={})
    element = make_picture_element(bbox=BoundingBox(x1=0, y1=0, x2=600, y2=800))

    assert builder.is_large_picture(element) is False


def test_is_large_picture_false_when_page_area_is_zero() -> None:
    # A degenerate page size (e.g. unparsed/zeroed) must not divide by zero.
    builder = make_builder(page_sizes={1: (0.0, 0.0)})
    element = make_picture_element(bbox=BoundingBox(x1=0, y1=0, x2=600, y2=800))

    assert builder.is_large_picture(element) is False


def test_is_large_picture_false_for_small_decorative_image() -> None:
    # A small logo in the corner of a 600x800 page: 60x40 = 2400 / 480000 = 0.5%.
    builder = make_builder(page_sizes={1: (600.0, 800.0)})
    element = make_picture_element(bbox=BoundingBox(x1=0, y1=0, x2=60, y2=40))

    assert builder.is_large_picture(element) is False


def test_is_large_picture_true_for_full_page_scan() -> None:
    builder = make_builder(page_sizes={1: (600.0, 800.0)})
    element = make_picture_element(bbox=BoundingBox(x1=0, y1=0, x2=600, y2=800))

    assert builder.is_large_picture(element) is True


def test_is_large_picture_true_at_exact_threshold() -> None:
    # 300 * 800 = 240000, exactly half of 600*800 = 480000.
    builder = make_builder(page_sizes={1: (600.0, 800.0)})
    element = make_picture_element(bbox=BoundingBox(x1=0, y1=0, x2=300, y2=800))

    assert builder.is_large_picture(element) is True


def test_picture_fragment_text_uses_caption_only_when_no_context_or_ocr() -> None:
    builder = make_builder()
    element = make_picture_element(bbox=None, caption="Scanned certificate page 1")

    text = builder.picture_fragment_text(elements=[element], index=0, element=element)

    assert text == "Figure: Scanned certificate page 1"


def test_picture_fragment_text_combines_caption_and_nearby_context() -> None:
    builder = make_builder()
    before = make_text_element(element_id="txt_1", text="The pump housing shown below.")
    picture = make_picture_element(bbox=None, caption="Pump housing diagram")
    elements = [before, picture]

    text = builder.picture_fragment_text(elements=elements, index=1, element=picture)

    assert text == "Figure: Pump housing diagram\n\nContext: The pump housing shown below."


def test_picture_fragment_text_falls_back_to_ocr_when_no_caption_or_context_but_substantial() -> (
    None
):
    builder = make_builder()
    element = make_picture_element(
        bbox=None,
        ocr_text="Serial number twelve three four five six seven eight nine ten",
    )

    text = builder.picture_fragment_text(elements=[element], index=0, element=element)

    assert text is not None
    assert text.startswith("OCR: ")


def test_picture_fragment_text_discards_short_ocr_text_with_no_caption_or_context() -> None:
    # Fewer than 6 words of raw OCR text and nothing else -- not enough
    # substance to justify a fragment.
    builder = make_builder()
    element = make_picture_element(bbox=None, ocr_text="Fig 1 only")

    text = builder.picture_fragment_text(elements=[element], index=0, element=element)

    assert text is None


def test_picture_fragment_text_none_when_nothing_present() -> None:
    builder = make_builder()
    element = make_picture_element(bbox=None)

    text = builder.picture_fragment_text(elements=[element], index=0, element=element)

    assert text is None


def test_picture_chunk_type_defaults_to_drawing_reference_for_empty_text() -> None:
    assert PictureFragmentBuilder.picture_chunk_type(None) == ChunkType.DRAWING_REFERENCE
    assert PictureFragmentBuilder.picture_chunk_type("") == ChunkType.DRAWING_REFERENCE


def test_picture_chunk_type_defaults_to_drawing_reference_for_unrelated_text() -> None:
    text = "Figure: Exploded view of the housing assembly"

    assert PictureFragmentBuilder.picture_chunk_type(text) == ChunkType.DRAWING_REFERENCE


def test_picture_chunk_type_detects_maintenance_interval_signal() -> None:
    text = "OCR: Oil quantity: 2.5 liters SAE 15W-40"

    assert PictureFragmentBuilder.picture_chunk_type(text) == ChunkType.MAINTENANCE_INTERVAL
