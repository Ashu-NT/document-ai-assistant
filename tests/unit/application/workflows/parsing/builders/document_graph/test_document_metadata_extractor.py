from src.application.workflows.parsing.builders.document_graph.document_metadata.document_metadata_extractor import (
    DocumentMetadataExtractor,
)
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.domain.common import DocumentType


def _raw_document(*, title: str | None, metadata: dict | None = None) -> RawParsedDocument:
    return RawParsedDocument(
        file_path="doc.pdf",
        title=title,
        page_count=1,
        raw_document=None,
        parser_name="docling",
        metadata=metadata or {},
    )


def test_explicitly_requested_document_type_is_confirmed() -> None:
    raw_document = _raw_document(
        title="Some Title With No Markers",
        metadata={"document_type": "datasheet"},
    )

    hint = DocumentMetadataExtractor.extract_document_type_hint(raw_document)

    assert hint.document_type == DocumentType.DATASHEET
    assert hint.is_confirmed is True


def test_explicit_document_type_wins_even_when_title_suggests_something_else() -> None:
    raw_document = _raw_document(
        title="Pump Manual",
        metadata={"document_type": "datasheet"},
    )

    hint = DocumentMetadataExtractor.extract_document_type_hint(raw_document)

    assert hint.document_type == DocumentType.DATASHEET
    assert hint.is_confirmed is True


def test_title_derived_hint_is_not_confirmed() -> None:
    raw_document = _raw_document(title="Field Service Manual")

    hint = DocumentMetadataExtractor.extract_document_type_hint(raw_document)

    assert hint.document_type == DocumentType.MANUAL
    assert hint.is_confirmed is False


def test_misleading_title_hint_is_still_only_a_hint_not_confirmed() -> None:
    # The extractor has no way to know a title marker is "wrong" -- its only
    # job is to flag that ANY title-derived guess is unconfirmed, so a
    # downstream consumer (structural inference / HybridDocumentTypeResolver)
    # can catch a misleading one instead of trusting it outright.
    raw_document = _raw_document(title="Annual Maintenance Report for the Manual Press")

    hint = DocumentMetadataExtractor.extract_document_type_hint(raw_document)

    assert hint.is_confirmed is False


def test_unknown_title_yields_unconfirmed_unknown_type() -> None:
    raw_document = _raw_document(title="Untitled Document 47")

    hint = DocumentMetadataExtractor.extract_document_type_hint(raw_document)

    assert hint.document_type == DocumentType.UNKNOWN
    assert hint.is_confirmed is False


def test_missing_title_yields_unconfirmed_unknown_type() -> None:
    raw_document = _raw_document(title=None)

    hint = DocumentMetadataExtractor.extract_document_type_hint(raw_document)

    assert hint.document_type == DocumentType.UNKNOWN
    assert hint.is_confirmed is False
