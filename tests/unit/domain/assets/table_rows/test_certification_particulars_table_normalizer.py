from src.domain.assets.table_rows.certification_particulars_table_normalizer import (
    CertificationParticularsTableNormalizer,
)

_WRAPPED_ROWS = [
    ["Certificate No", "CE-2024-001", "Issue Date", "2024-01-15"],
    ["Issuing Body", "Lloyd's Register", "Expiry Date", "2029-01-15"],
]


def test_normalize_projects_wrapped_certification_rows() -> None:
    normalized = CertificationParticularsTableNormalizer().normalize(
        _WRAPPED_ROWS,
        table_category="certification_table",
        chunk_type=None,
    )

    assert normalized is not None
    assert normalized.headers == ["Label", "Value"]
    assert normalized.rows == [
        ["Certificate No", "CE-2024-001"],
        ["Issue Date", "2024-01-15"],
        ["Issuing Body", "Lloyd's Register"],
        ["Expiry Date", "2029-01-15"],
    ]


def test_normalize_returns_none_when_explicit_header_already_present() -> None:
    normalized = CertificationParticularsTableNormalizer().normalize(
        [["Parameter", "Value"], ["Certificate No", "CE-2024-001"]],
        table_category="certification_table",
        chunk_type=None,
    )

    assert normalized is None


def test_normalize_returns_none_for_unrelated_category() -> None:
    normalized = CertificationParticularsTableNormalizer().normalize(
        _WRAPPED_ROWS,
        table_category="technical_data_table",
        chunk_type=None,
    )

    assert normalized is None
