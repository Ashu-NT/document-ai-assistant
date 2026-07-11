from src.application.prompts.answer_generation.prompt_context.tables import (
    PromptTableRowNormalizer,
)


def test_normalize_detects_headers_and_builds_cells_by_header() -> None:
    headers, rows = PromptTableRowNormalizer().normalize(
        [["Parameter", "Value"], ["Test pressure", "700 bar"]]
    )

    assert headers == ["Parameter", "Value"]
    assert len(rows) == 1
    assert rows[0].source_row_index == 1
    assert rows[0].cells == ["Test pressure", "700 bar"]
    assert rows[0].cells_by_header == {
        "Parameter": "Test pressure",
        "Value": "700 bar",
    }


def test_normalize_keeps_rows_without_headers_when_needed() -> None:
    headers, rows = PromptTableRowNormalizer().normalize(
        [["14.00", "Pump Casing"], ["16.00", "Suction casing"]]
    )

    assert headers == []
    assert len(rows) == 2
    assert rows[0].source_row_index == 0
    assert rows[0].cells_by_header == {}
