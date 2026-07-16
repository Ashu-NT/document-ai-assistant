from src.application.workflows.parsing.normalizers.table_layout.docling_parallel_toc_reconstructor import (
    DoclingParallelTocReconstructor,
)
from src.domain.assets import TableCellSpan
from src.domain.common import BoundingBox


def _span(*, row, col, text, x1, x2, page=1) -> TableCellSpan:
    return TableCellSpan(
        row_start=row,
        row_end=row,
        col_start=col,
        col_end=col,
        text=text,
        page_number=page,
        bbox=BoundingBox(x1=x1, y1=100 + (row * 20), x2=x2, y2=118 + (row * 20)),
    )


def test_reconstruct_merges_two_lanes_with_non_english_titles() -> None:
    """The reconstructor must never depend on English header/title words --
    only on digit-based page-number patterns -- so a non-English manual's
    dual-column table of contents still merges correctly."""
    reconstructor = DoclingParallelTocReconstructor()

    left_lane = [
        _span(row=0, col=0, text="1 Consignes de sécurité", x1=40, x2=320),
        _span(row=0, col=1, text="12", x1=330, x2=360),
        _span(row=1, col=0, text="1.1 Étalonnage et réglage", x1=40, x2=320),
        _span(row=1, col=1, text="27", x1=330, x2=360),
        _span(row=2, col=0, text="2 Dépannage", x1=40, x2=320),
        _span(row=2, col=1, text="41", x1=330, x2=360),
    ]
    right_lane = [
        _span(row=0, col=0, text="6 Entretien", x1=610, x2=900),
        _span(row=0, col=1, text="67", x1=910, x2=940),
        _span(row=1, col=0, text="7 Mode d'emploi", x1=610, x2=900),
        _span(row=1, col=1, text="69", x1=910, x2=940),
        _span(row=2, col=0, text="7.2 Dépannage avancé", x1=610, x2=900),
        _span(row=2, col=1, text="81", x1=910, x2=940),
    ]

    rows = reconstructor.reconstruct(left_lane + right_lane)

    assert rows == [
        ["Number", "Title", "Page"],
        ["1", "Consignes de sécurité", "12"],
        ["1.1", "Étalonnage et réglage", "27"],
        ["2", "Dépannage", "41"],
        ["6", "Entretien", "67"],
        ["7", "Mode d'emploi", "69"],
        ["7.2", "Dépannage avancé", "81"],
    ]


def test_looks_like_reconstructed_toc_does_not_depend_on_english_header_word() -> None:
    """Regression test for the hardcoded `header[-1] == "Page"` bug: detection
    must key off the numeric last column of each data row, not a literal
    English header word, so a localized header (e.g. "Página") still passes."""
    raw_rows = [["unreconstructed placeholder row"]]
    reconstructed = [
        ["Número", "Título", "Página"],
        ["1", "Prefacio", "11"],
        ["2", "Seguridad", "15"],
        ["3", "Extra", "20"],
    ]

    assert DoclingParallelTocReconstructor._looks_like_reconstructed_toc(
        raw_rows,
        reconstructed,
    )


def test_looks_like_reconstructed_toc_rejects_non_numeric_last_column() -> None:
    raw_rows = [["unreconstructed placeholder row"]]
    reconstructed = [
        ["Label", "Value"],
        ["Voltage", "400V"],
        ["Weight", "120 kg"],
        ["Power", "5.5 kW"],
    ]

    assert not DoclingParallelTocReconstructor._looks_like_reconstructed_toc(
        raw_rows,
        reconstructed,
    )
