from src.application.workflows.parsing.builders.chunking.builders.fragment.degraded_table_plain_text_renderer import (
    DegradedTablePlainTextRenderer,
)


class TestDegradedTablePlainTextRenderer:
    def test_renders_meaningful_cell_text_without_markdown_syntax(self) -> None:
        renderer = DegradedTablePlainTextRenderer()

        text = renderer.render([["DN25", "PN16", "80 C"]])

        assert text is not None
        assert "DN25" in text
        assert "PN16" in text
        assert "80 C" in text
        assert "---" not in text
        assert "|" not in text

    def test_preserves_giant_cell_text_verbatim(self) -> None:
        giant_cell = "engine type engine no. 8351446 turbocharger type TCR12-43063 " * 3
        renderer = DegradedTablePlainTextRenderer()

        text = renderer.render([[giant_cell, "12V175D-ML"]])

        assert text is not None
        assert giant_cell.strip() in text
        assert "12V175D-ML" in text

    def test_multiple_rows_all_preserved(self) -> None:
        renderer = DegradedTablePlainTextRenderer()

        text = renderer.render([["alpha", "beta"], ["gamma", "delta"]])

        for value in ("alpha", "beta", "gamma", "delta"):
            assert value in text

    def test_none_table_rows_returns_none(self) -> None:
        assert DegradedTablePlainTextRenderer().render(None) is None

    def test_empty_table_rows_returns_none(self) -> None:
        assert DegradedTablePlainTextRenderer().render([]) is None

    def test_blank_cells_only_returns_none(self) -> None:
        assert DegradedTablePlainTextRenderer().render([["", "   "]]) is None

    def test_blank_cells_mixed_with_real_content_keep_only_the_real_content(self) -> None:
        text = DegradedTablePlainTextRenderer().render([["", "TCR12-43063", "   "]])

        assert text == "TCR12-43063"

    def test_deterministic_across_repeated_calls(self) -> None:
        renderer = DegradedTablePlainTextRenderer()
        rows = [["alpha", "beta gamma"]]

        assert renderer.render(rows) == renderer.render(rows)
