import pytest

from tests.unit.application.workflows.parsing.builders._test_document_graph_builder_part1 import (
    make_builder,
    make_parsed_element,
    make_raw_parsed_document,
)

from src.application.workflows.parsing.builders.document_graph.parsed_assets.parsed_element_factory import (
    ParsedElementFactory,
)
from src.domain.common import ElementType
from src.domain.document import DocumentHashes
from src.shared.exceptions import ChunkingError


def test_document_graph_builder_isolates_bad_element_and_continues(monkeypatch) -> None:
    real_build = ParsedElementFactory.build

    def exploding_build(self, *, parsed_element, **kwargs):
        if parsed_element.element_id == "tbl_bad":
            raise ValueError("boom")
        return real_build(self, parsed_element=parsed_element, **kwargs)

    monkeypatch.setattr(ParsedElementFactory, "build", exploding_build)

    builder = make_builder()
    errors: list[str] = []
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(file_hash="fh_001", content_hash="ch_001"),
        canonical_elements=[
            make_parsed_element(
                element_id="hdr_1",
                element_type=ElementType.SECTION_HEADER,
                order_index=1,
                text="Components",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="tbl_bad",
                element_type=ElementType.TABLE,
                order_index=2,
                text="Bad table",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=3,
                text="Good text.",
                page_start=1,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
        skipped_element_errors=errors,
    )

    surviving_texts = {element.text for element in graph.elements.values()}
    assert surviving_texts == {"Components", "Good text."}
    assert graph.tables == {}
    assert len(errors) == 1
    assert "tbl_bad" in errors[0]


def test_document_graph_builder_isolates_bad_form_element_and_continues(monkeypatch) -> None:
    real_build = ParsedElementFactory.build

    def exploding_build(self, *, parsed_element, **kwargs):
        if parsed_element.element_id == "form_bad":
            raise ValueError("boom")
        return real_build(self, parsed_element=parsed_element, **kwargs)

    monkeypatch.setattr(ParsedElementFactory, "build", exploding_build)

    builder = make_builder()
    errors: list[str] = []
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(file_hash="fh_001", content_hash="ch_001"),
        canonical_elements=[
            make_parsed_element(
                element_id="hdr_1",
                element_type=ElementType.SECTION_HEADER,
                order_index=1,
                text="Components",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="form_bad",
                element_type=ElementType.FORM,
                order_index=2,
                text=None,
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=3,
                text="Good text.",
                page_start=1,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
        skipped_element_errors=errors,
    )

    surviving_texts = {element.text for element in graph.elements.values()}
    assert surviving_texts == {"Components", "Good text."}
    assert graph.forms == {}
    assert len(errors) == 1
    assert "form_bad" in errors[0]


def test_document_graph_builder_raises_when_all_elements_fail(monkeypatch) -> None:
    def exploding_build(self, *, parsed_element, **kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(ParsedElementFactory, "build", exploding_build)

    builder = make_builder()
    errors: list[str] = []

    with pytest.raises(ChunkingError):
        builder.build(
            document_id="doc_001",
            file_path="data/input/pump_manual.pdf",
            hashes=DocumentHashes(file_hash="fh_001", content_hash="ch_001"),
            canonical_elements=[
                make_parsed_element(
                    element_id="txt_1",
                    element_type=ElementType.TEXT,
                    order_index=1,
                    text="Text.",
                    page_start=1,
                ),
            ],
            raw_parsed_document=make_raw_parsed_document(),
            skipped_element_errors=errors,
        )

    assert len(errors) == 1
