from __future__ import annotations

from src.application.workflows.ingestion.content_hash import compute_content_hash_from_graph
from src.domain.common import ElementType, SourceLocation
from src.domain.elements import CanonicalElement


class FakeSource:
    def __init__(self, page_start=None):
        self.page_start = page_start


class FakeElementType:
    def __init__(self, value):
        self.value = value


class FakeElement:
    def __init__(self, element_id, element_type, text, reading_order, page_start=None):
        self.element_id = element_id
        self.element_type = FakeElementType(element_type)
        self.text = text
        self.reading_order = reading_order
        self.source = FakeSource(page_start=page_start)


class FakeGraph:
    def __init__(self, elements):
        self.elements = {e.element_id: e for e in elements}


def _make_element(eid, text, reading_order, elem_type="text", page=1):
    return FakeElement(
        element_id=eid,
        element_type=elem_type,
        text=text,
        reading_order=reading_order,
        page_start=page,
    )


def test_same_content_same_hash():
    e1 = _make_element("e1", "Hello world", 0)
    e2 = _make_element("e1", "Hello world", 0)
    g1 = FakeGraph([e1])
    g2 = FakeGraph([e2])
    assert compute_content_hash_from_graph(g1) == compute_content_hash_from_graph(g2)


def test_different_content_different_hash():
    e1 = _make_element("e1", "Hello world", 0)
    e2 = _make_element("e1", "Different text", 0)
    g1 = FakeGraph([e1])
    g2 = FakeGraph([e2])
    assert compute_content_hash_from_graph(g1) != compute_content_hash_from_graph(g2)


def test_whitespace_normalization():
    e1 = _make_element("e1", "Hello   world\n\n\nfoo", 0)
    e2 = _make_element("e1", "Hello world\n\nfoo", 0)
    g1 = FakeGraph([e1])
    g2 = FakeGraph([e2])
    assert compute_content_hash_from_graph(g1) == compute_content_hash_from_graph(g2)


def test_element_id_does_not_affect_hash():
    e1 = _make_element("e-original-id", "Same text", 0)
    e2 = _make_element("e-different-id", "Same text", 0)
    g1 = FakeGraph([e1])
    g2 = FakeGraph([e2])
    assert compute_content_hash_from_graph(g1) == compute_content_hash_from_graph(g2)


def test_empty_graph_stable():
    g = FakeGraph([])
    h1 = compute_content_hash_from_graph(g)
    h2 = compute_content_hash_from_graph(g)
    assert h1 == h2


def test_element_type_affects_hash():
    e1 = _make_element("e1", "Same text", 0, elem_type="text")
    e2 = _make_element("e1", "Same text", 0, elem_type="table")
    g1 = FakeGraph([e1])
    g2 = FakeGraph([e2])
    assert compute_content_hash_from_graph(g1) != compute_content_hash_from_graph(g2)


def test_real_canonical_element_fields_are_compatible():
    """Prove that compute_content_hash_from_graph works with real CanonicalElement objects."""
    element = CanonicalElement(
        element_id="el_001",
        document_id="doc_001",
        element_type=ElementType.TEXT,
        text="Hello world",
        reading_order=1,
        source=SourceLocation(page_start=1, page_end=1),
    )
    graph = FakeGraph([element])
    h = compute_content_hash_from_graph(graph)
    assert isinstance(h, str) and len(h) == 64


def test_same_content_different_element_ids_same_hash():
    """Different generated IDs must not affect the content hash."""
    e1 = CanonicalElement(
        element_id="generated-uuid-1",
        document_id="doc_a",
        element_type=ElementType.TEXT,
        text="Same content",
        reading_order=0,
        source=SourceLocation(page_start=1),
    )
    e2 = CanonicalElement(
        element_id="generated-uuid-2",
        document_id="doc_b",
        element_type=ElementType.TEXT,
        text="Same content",
        reading_order=0,
        source=SourceLocation(page_start=1),
    )
    g1 = FakeGraph([e1])
    g2 = FakeGraph([e2])
    assert compute_content_hash_from_graph(g1) == compute_content_hash_from_graph(g2)
