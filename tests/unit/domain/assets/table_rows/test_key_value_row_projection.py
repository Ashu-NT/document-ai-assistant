from src.application.workflows.parsing.tables.normalization.key_value.key_value_row_projection import (
    project_key_value_rows,
)
from src.application.workflows.parsing.tables.rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)


def test_project_key_value_rows_projects_wrapped_multi_field_rows() -> None:
    rows = [
        ["Model", "XV2000", "Speed", "1450 RPM"],
        ["Weight", "120 kg", "Diameter", "250 mm"],
    ]

    projected = project_key_value_rows(
        rows,
        row_canonicalizer=TableRowCanonicalizer(),
    )

    assert projected is not None
    assert projected.headers == ["Label", "Value"]
    assert projected.rows == [
        ["Model", "XV2000"],
        ["Speed", "1450 RPM"],
        ["Weight", "120 kg"],
        ["Diameter", "250 mm"],
    ]


def test_project_key_value_rows_returns_none_when_explicit_header_already_present() -> None:
    rows = [["Parameter", "Value"], ["Voltage", "400V"]]

    projected = project_key_value_rows(
        rows,
        row_canonicalizer=TableRowCanonicalizer(),
    )

    assert projected is None


def test_project_key_value_rows_returns_none_for_too_few_rows() -> None:
    projected = project_key_value_rows(
        [["Single row only"]],
        row_canonicalizer=TableRowCanonicalizer(),
    )

    assert projected is None
