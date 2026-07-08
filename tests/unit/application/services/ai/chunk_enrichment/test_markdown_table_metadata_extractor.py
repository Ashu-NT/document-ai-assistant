from src.application.services.ai.chunk_enrichment.markdown_table_metadata_extractor import (
    extract_table_metadata_from_rows,
)


def test_extract_table_metadata_from_rows_builds_headers_and_row_labels() -> None:
    rows = [
        ["Part Number", "Description"],
        ["HP-001", "Filter"],
        ["HP-002", "Gasket"],
    ]

    metadata = extract_table_metadata_from_rows(rows)

    assert metadata is not None
    assert metadata.headers == ("Part Number", "Description")
    assert metadata.row_labels == ("HP-001", "HP-002")
    assert metadata.caption is None
    assert metadata.context is None


def test_extract_table_metadata_from_rows_extracts_units() -> None:
    rows = [
        ["Parameter", "Value"],
        ["Voltage", "24 V"],
        ["Pressure", "10 bar"],
    ]

    metadata = extract_table_metadata_from_rows(rows)

    assert metadata is not None
    assert "v" in metadata.units
    assert "bar" in metadata.units


def test_extract_table_metadata_from_rows_returns_none_for_header_only_table() -> None:
    assert extract_table_metadata_from_rows([["Part Number", "Description"]]) is None


def test_extract_table_metadata_from_rows_returns_none_for_empty_rows() -> None:
    assert extract_table_metadata_from_rows([]) is None
