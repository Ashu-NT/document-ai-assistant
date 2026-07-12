from src.shared.text.ascii_table_renderer import AsciiTableColumn, render_ascii_table


def test_render_ascii_table_renders_headers_and_rows() -> None:
    table = render_ascii_table(
        columns=[
            AsciiTableColumn("task", "Task", 20),
            AsciiTableColumn("interval", "Interval", 20),
        ],
        rows=[{"task": "Replace filter", "interval": "Every 1000 hours"}],
    )

    assert "+----------------" in table
    assert "Task" in table
    assert "Replace filter" in table
    assert "Every 1000 hours" in table


def test_render_ascii_table_truncates_long_cells() -> None:
    table = render_ascii_table(
        columns=[AsciiTableColumn("notes", "Notes", 18)],
        rows=[
            {
                "notes": "This cell is intentionally much longer than the configured width.",
            }
        ],
    )

    assert "This cell is..." in table
