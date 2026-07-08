from src.application.langgraph.research.presentation.table_text_summarizer import (
    TableTextSummarizer,
)


def test_summarize_prefers_table_rows_over_text_parsing() -> None:
    summarizer = TableTextSummarizer()
    text = (
        "| Parameter | Value |\n"
        "|---|---|\n"
        "| Voltage (from text) | 12 V |\n"
        "| Pressure (from text) | 5 bar |\n"
    )
    table_rows = [["Parameter", "Value"], ["Voltage", "24 V"], ["Pressure", "10 bar"]]

    pairs = summarizer.extract_pairs(text, table_rows=table_rows)

    assert pairs == [("Voltage", "24 V"), ("Pressure", "10 bar")]


def test_summarize_falls_back_to_text_parsing_when_no_table_rows() -> None:
    summarizer = TableTextSummarizer()
    text = (
        "| Parameter | Value |\n"
        "|---|---|\n"
        "| Voltage | 24 V |\n"
        "| Pressure | 10 bar |\n"
    )

    pairs = summarizer.extract_pairs(text)

    assert ("Voltage", "24 V") in pairs
    assert ("Pressure", "10 bar") in pairs


def test_summarize_uses_rows_via_public_entry_point() -> None:
    summarizer = TableTextSummarizer()
    lines = summarizer.summarize(
        "unrelated free text",
        table_rows=[["Parameter", "Value"], ["Voltage", "24 V"], ["Pressure", "10 bar"]],
    )

    assert any("Voltage: 24 V" in line for line in lines)
