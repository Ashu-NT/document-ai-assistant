import ctypes

import pypdfium2.raw as _real_raw
import pytest

from src.infrastructure.pdf.pdf_link_annotation_extractor import PdfLinkAnnotationExtractor
from src.infrastructure.pdf.pdfium_process_lock import PDFIUM_PROCESS_LOCK


class _FakeRaw:
    """Fake pypdfium2.raw: real (empty/opaque) pdfium pointer TYPES borrowed
    from the real module (safe to instantiate/address, never dereferenced
    for real field data - sizeof() == 0), with the ctypes FUNCTIONS replaced
    by test-controlled Python fakes. Each handle is a pointer to a tagged
    c_int backing object; the tag is recovered by casting the handle back to
    POINTER(c_int), which lets one shared registry track every link/dest/
    action handle regardless of which "type" it nominally is.
    """

    PDFACTION_UNSUPPORTED = 0
    PDFACTION_GOTO = 1
    PDFACTION_REMOTEGOTO = 2
    PDFACTION_URI = 3
    PDFACTION_LAUNCH = 4
    PDFACTION_EMBEDDEDGOTO = 5

    FPDF_LINK = _real_raw.FPDF_LINK
    FPDF_DEST = _real_raw.FPDF_DEST
    FPDF_ACTION = _real_raw.FPDF_ACTION
    FS_RECTF = _real_raw.FS_RECTF

    def __init__(self, pages: dict[int, list[dict]], lock_observations: list[bool] | None = None):
        self._pages = pages
        self._specs: dict[int, dict] = {}
        self._tag_counter = 0
        self._keepalive: list = []
        self._lock_observations = lock_observations

    def _new_tag(self) -> int:
        self._tag_counter += 1
        return self._tag_counter

    def _make_handle(self, handle_type, tag: int):
        backing = ctypes.c_int(tag)
        self._keepalive.append(backing)
        return ctypes.cast(ctypes.pointer(backing), handle_type)

    @staticmethod
    def _read_tag(handle) -> int:
        return ctypes.cast(handle, ctypes.POINTER(ctypes.c_int)).contents.value

    def FPDFLink_Enumerate(self, page_raw, start_pos_ref, link_ref):
        if self._lock_observations is not None:
            self._lock_observations.append(PDFIUM_PROCESS_LOCK.locked())
        links = self._pages.get(page_raw, [])
        index = start_pos_ref._obj.value
        if index >= len(links):
            return 0
        spec = links[index]
        start_pos_ref._obj.value = index + 1
        tag = self._new_tag()
        self._specs[tag] = spec
        handle = self._make_handle(self.FPDF_LINK, tag)
        link_ref._obj.contents = handle.contents
        return 1

    def FPDFLink_GetAnnotRect(self, link_handle, rect_ref):
        spec = self._specs[self._read_tag(link_handle)]
        rect = spec.get("rect")
        if rect is None:
            return 0
        left, top, right, bottom = rect
        rect_ref._obj.left = left
        rect_ref._obj.top = top
        rect_ref._obj.right = right
        rect_ref._obj.bottom = bottom
        return 1

    def FPDFLink_GetDest(self, doc_raw, link_handle):
        spec = self._specs[self._read_tag(link_handle)]
        dest_index = spec.get("dest_index")
        if dest_index is None:
            return self.FPDF_DEST()
        tag = self._new_tag()
        self._specs[tag] = {"dest_index": dest_index}
        return self._make_handle(self.FPDF_DEST, tag)

    def FPDFLink_GetAction(self, link_handle):
        spec = self._specs[self._read_tag(link_handle)]
        action_type = spec.get("action_type")
        if action_type is None:
            return self.FPDF_ACTION()
        tag = self._new_tag()
        self._specs[tag] = spec
        return self._make_handle(self.FPDF_ACTION, tag)

    def FPDFAction_GetType(self, action_handle):
        return self._specs[self._read_tag(action_handle)]["action_type"]

    def FPDFAction_GetDest(self, doc_raw, action_handle):
        spec = self._specs[self._read_tag(action_handle)]
        dest_index = spec.get("action_dest_index")
        if dest_index is None:
            return self.FPDF_DEST()
        tag = self._new_tag()
        self._specs[tag] = {"dest_index": dest_index}
        return self._make_handle(self.FPDF_DEST, tag)

    def FPDFDest_GetDestPageIndex(self, doc_raw, dest_handle):
        return self._specs[self._read_tag(dest_handle)]["dest_index"]


class _FakePdfPage:
    def __init__(self, page_index: int, size, rotation, raises: bool = False):
        if raises:
            raise RuntimeError(f"cannot open page {page_index}")
        self.raw = page_index
        self._size = size
        self._rotation = rotation
        self.closed = False

    def get_size(self):
        return self._size

    def get_rotation(self):
        return self._rotation

    def close(self) -> None:
        self.closed = True


class _FakePdfDocument:
    def __init__(
        self,
        *,
        page_count: int,
        page_meta: dict[int, tuple] | None = None,
        page_labels: dict[int, str] | None = None,
        raising_pages: set[int] | None = None,
    ):
        self.raw = object()
        self._page_count = page_count
        self._page_meta = page_meta or {}
        self._page_labels = page_labels or {}
        self._raising_pages = raising_pages or set()
        self.closed = False

    def __len__(self) -> int:
        return self._page_count

    def __getitem__(self, index: int) -> _FakePdfPage:
        size, rotation = self._page_meta.get(index, ((612.0, 792.0), 0))
        return _FakePdfPage(index, size, rotation, raises=index in self._raising_pages)

    def get_page_label(self, index: int) -> str:
        return self._page_labels.get(index, "")

    def close(self) -> None:
        self.closed = True


class _FakePdfiumModule:
    def __init__(self, document_factory, raw):
        self._document_factory = document_factory
        self.raw = raw

    def PdfDocument(self, file_path: str):
        return self._document_factory(file_path)


def _patch_extractor(monkeypatch, *, document_factory, raw):
    fake_module = _FakePdfiumModule(document_factory, raw)
    monkeypatch.setattr(
        PdfLinkAnnotationExtractor,
        "_import_pypdfium2",
        staticmethod(lambda: fake_module),
    )


def test_extract_direct_destination_link(monkeypatch) -> None:
    raw = _FakeRaw(pages={0: [{"dest_index": 48, "rect": (1.0, 2.0, 3.0, 4.0)}]})
    document = _FakePdfDocument(page_count=49, page_labels={0: "313", 48: "41"})
    _patch_extractor(monkeypatch, document_factory=lambda path: document, raw=raw)

    result = PdfLinkAnnotationExtractor().extract("sample.pdf")

    assert result.status == "ok"
    assert len(result.annotations) == 1
    annotation = result.annotations[0]
    assert annotation.link_kind == "direct_destination"
    assert annotation.source_page == 1
    assert annotation.dest_page == 49
    assert annotation.source_page_label == "313"
    assert annotation.dest_page_label == "41"
    # rect tuple is (left, top, right, bottom); BoundingBox maps
    # x1=left, y1=bottom, x2=right, y2=top (native bottom-left origin).
    assert annotation.source_rect.x1 == 1.0
    assert annotation.source_rect.y1 == 4.0
    assert annotation.source_rect.x2 == 3.0
    assert annotation.source_rect.y2 == 2.0
    assert result.non_internal_links_excluded == 0
    assert result.invalid_destinations_skipped == 0


def test_extract_goto_action_link(monkeypatch) -> None:
    raw = _FakeRaw(pages={0: [{"action_type": _FakeRaw.PDFACTION_GOTO, "action_dest_index": 9}]})
    document = _FakePdfDocument(page_count=10)
    _patch_extractor(monkeypatch, document_factory=lambda path: document, raw=raw)

    result = PdfLinkAnnotationExtractor().extract("sample.pdf")

    assert len(result.annotations) == 1
    assert result.annotations[0].link_kind == "goto"
    assert result.annotations[0].dest_page == 10


@pytest.mark.parametrize(
    "action_type",
    [
        _FakeRaw.PDFACTION_UNSUPPORTED,
        _FakeRaw.PDFACTION_REMOTEGOTO,
        _FakeRaw.PDFACTION_URI,
        _FakeRaw.PDFACTION_LAUNCH,
        _FakeRaw.PDFACTION_EMBEDDEDGOTO,
    ],
)
def test_extract_excludes_non_goto_actions_as_non_internal(monkeypatch, action_type) -> None:
    raw = _FakeRaw(pages={0: [{"action_type": action_type}]})
    document = _FakePdfDocument(page_count=1)
    _patch_extractor(monkeypatch, document_factory=lambda path: document, raw=raw)

    result = PdfLinkAnnotationExtractor().extract("sample.pdf")

    assert result.annotations == []
    assert result.non_internal_links_excluded == 1


def test_extract_excludes_link_with_no_dest_and_no_action(monkeypatch) -> None:
    raw = _FakeRaw(pages={0: [{}]})
    document = _FakePdfDocument(page_count=1)
    _patch_extractor(monkeypatch, document_factory=lambda path: document, raw=raw)

    result = PdfLinkAnnotationExtractor().extract("sample.pdf")

    assert result.annotations == []
    assert result.non_internal_links_excluded == 1


def test_extract_skips_out_of_range_destination_index(monkeypatch) -> None:
    raw = _FakeRaw(pages={0: [{"dest_index": 999}]})
    document = _FakePdfDocument(page_count=1)
    _patch_extractor(monkeypatch, document_factory=lambda path: document, raw=raw)

    result = PdfLinkAnnotationExtractor().extract("sample.pdf")

    assert result.annotations == []
    assert result.invalid_destinations_skipped == 1


def test_extract_is_partial_when_one_page_fails_but_others_still_return_annotations(
    monkeypatch,
) -> None:
    raw = _FakeRaw(pages={0: [{"dest_index": 2}], 2: [{"dest_index": 0}]})
    document = _FakePdfDocument(page_count=3, raising_pages={1})
    _patch_extractor(monkeypatch, document_factory=lambda path: document, raw=raw)

    result = PdfLinkAnnotationExtractor().extract("sample.pdf")

    assert result.status == "partial"
    assert len(result.page_failures) == 1
    assert result.page_failures[0].page_number == 2
    assert len(result.annotations) == 2
    assert {a.source_page for a in result.annotations} == {1, 3}


def test_extract_returns_failed_status_when_file_cannot_be_opened(monkeypatch) -> None:
    def _raise(path):
        raise RuntimeError("not a PDF")

    _patch_extractor(monkeypatch, document_factory=_raise, raw=_FakeRaw(pages={}))

    result = PdfLinkAnnotationExtractor().extract("not_a_pdf.pdf")

    assert result.status == "failed"
    assert result.annotations == []
    assert result.page_failures == []
    assert result.error_message == "not a PDF"


def test_extract_holds_the_process_lock_during_pdfium_calls(monkeypatch) -> None:
    observations: list[bool] = []
    raw = _FakeRaw(pages={0: [{"dest_index": 0}]}, lock_observations=observations)
    document = _FakePdfDocument(page_count=1)
    _patch_extractor(monkeypatch, document_factory=lambda path: document, raw=raw)

    PdfLinkAnnotationExtractor().extract("sample.pdf")

    assert observations, "FPDFLink_Enumerate was never called"
    assert all(observations)
    assert not PDFIUM_PROCESS_LOCK.locked()
