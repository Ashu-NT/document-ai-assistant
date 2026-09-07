from types import SimpleNamespace

from src.application.workflows.parsing.normalizers.docling_layout_metadata_builder import (
    DoclingLayoutMetadataBuilder,
)
from src.domain.common import BoundingBox


class _ItemExtractor:
    @staticmethod
    def should_skip(item) -> bool:
        return item.label in {"page_header", "page_footer"}

    @staticmethod
    def extract_raw_ref(item) -> str:
        return item.self_ref

    @staticmethod
    def lower_label(item) -> str:
        return item.label

    @staticmethod
    def extract_content_layer(item) -> str:
        return item.content_layer


class _ProvenanceExtractor:
    @staticmethod
    def extract_pages(item) -> tuple[int, int]:
        return item.page, item.page

    @staticmethod
    def extract_bbox(item, *, raw_document) -> BoundingBox:
        del raw_document
        return item.bbox


class _RecordingAnalyzer:
    def __init__(self) -> None:
        self.candidates = []
        self.furniture_references = []

    def analyze_and_serialize(
        self,
        *,
        raw_document,
        candidates,
        furniture_reference_candidates,
    ) -> dict[str, dict[str, object]]:
        del raw_document
        self.candidates = candidates
        self.furniture_references = furniture_reference_candidates
        return {}


def _item(ref: str, label: str, *, page: int) -> SimpleNamespace:
    return SimpleNamespace(
        self_ref=ref,
        label=label,
        text="Compressor Operating Manual" if "header" in label else "Body text",
        content_layer="furniture" if label == "page_header" else "body",
        page=page,
        bbox=BoundingBox(x1=50, y1=940, x2=550, y2=970),
    )


def test_native_furniture_is_reference_evidence_not_canonical_candidate() -> None:
    analyzer = _RecordingAnalyzer()
    builder = DoclingLayoutMetadataBuilder(layout_analyzer=analyzer)

    builder.build(
        raw_document=SimpleNamespace(),
        items=[
            _item("native_header", "page_header", page=1),
            _item("mislabelled_header", "section_header", page=2),
            _item("body", "text", page=2),
        ],
        item_extractor=_ItemExtractor(),
        provenance_extractor=_ProvenanceExtractor(),
    )

    assert [candidate.element_ref for candidate in analyzer.candidates] == [
        "mislabelled_header",
        "body",
    ]
    assert [
        candidate.element_ref for candidate in analyzer.furniture_references
    ] == ["native_header"]
