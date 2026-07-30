from src.application.workflows.parsing.normalizers.table_layout.text_grid.text_grid_table_detector import (
    GridElement,
    TextGridTableDetector,
)
from src.domain.common import BoundingBox


def _element(index: int, text: str, *, x1: float, x2: float, y1: float, y2: float) -> GridElement:
    return GridElement(index=index, text=text, bbox=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2))


def _door_identification_block_elements() -> list[GridElement]:
    # Exact real bbox/text data captured from a real document
    # (KSB_FSD_A3000_E3000-L-400_DOCUMENTATION_rev4_MY COSMOS.pdf, page 8)
    # whose "Door identification block" (pos | door-number | location) was
    # never recognized as a table by Docling at all -- it came through as
    # these loose text elements, in Docling's own bottom-to-top emission
    # order (pos 8 first, pos 1 last).
    return [
        _element(270, "1615.4208", x1=89.2, x2=134.6, y1=295.0, y2=287.7),
        _element(271, "8", x1=58.3, x2=63.0, y1=295.2, y2=288.0),
        _element(272, "-", x1=224.6, x2=227.3, y1=291.1, y2=290.2),
        _element(273, "1615.5204", x1=89.2, x2=134.6, y1=307.4, y2=300.1),
        _element(274, "7", x1=58.3, x2=63.0, y1=307.5, y2=300.4),
        _element(275, "-", x1=224.6, x2=227.3, y1=303.4, y2=302.6),
        _element(276, "1615.5203", x1=89.2, x2=134.6, y1=319.7, y2=312.4),
        _element(277, "6", x1=58.2, x2=62.9, y1=320.0, y2=312.7),
        _element(278, "-", x1=224.6, x2=227.3, y1=315.8, y2=314.9),
        _element(279, "1615.4203", x1=89.2, x2=134.6, y1=332.1, y2=324.8),
        _element(280, "5", x1=58.3, x2=63.0, y1=332.2, y2=325.0),
        _element(281, "-", x1=224.6, x2=227.3, y1=328.2, y2=327.3),
        _element(282, "1615.4201", x1=89.2, x2=133.2, y1=344.4, y2=337.2),
        _element(283, "4", x1=58.0, x2=62.9, y1=344.6, y2=337.5),
        _element(284, "-", x1=224.6, x2=227.3, y1=340.5, y2=339.7),
        _element(285, "1615.3205", x1=89.2, x2=134.6, y1=356.8, y2=349.5),
        _element(286, "3", x1=58.3, x2=63.0, y1=357.0, y2=349.8),
        _element(287, "-", x1=224.6, x2=227.3, y1=352.9, y2=352.0),
        _element(288, "1615.3206", x1=89.2, x2=134.6, y1=369.2, y2=361.9),
        _element(289, "2", x1=58.2, x2=62.9, y1=369.4, y2=362.2),
        _element(290, "-", x1=224.6, x2=227.3, y1=365.2, y2=364.4),
        _element(291, "1615.2208", x1=89.2, x2=134.6, y1=381.5, y2=374.2),
        _element(292, "1", x1=58.9, x2=61.6, y1=381.8, y2=374.6),
        _element(293, "-", x1=224.6, x2=227.3, y1=377.6, y2=376.7),
        # Header-ish labels above the data grid -- must not be treated as
        # data rows (only 2 of them share a row at all, and neither aligns
        # with the "location" column).
        _element(294, "pos.", x1=51.1, x2=70.3, y1=404.6, y2=397.4),
        _element(295, "door-number location", x1=80.8, x2=142.7, y1=406.1, y2=398.9),
        _element(296, "Door identification block", x1=93.8, x2=257.1, y1=437.9, y2=427.5),
    ]


def _option_system_weight_elements() -> list[GridElement]:
    # Same document, same page: the "Option" (hose port) / "System weight"
    # column pair, also never recognized as a table by Docling.
    return [
        _element(299, "no", x1=651.9, x2=661.9, y1=293.3, y2=288.0),
        _element(300, "247", x1=741.5, x2=757.4, y1=295.2, y2=288.1),
        _element(301, "yes", x1=649.3, x2=664.0, y1=305.7, y2=298.3),
        _element(302, "296", x1=741.5, x2=757.4, y1=307.6, y2=300.3),
        _element(303, "yes", x1=649.3, x2=664.0, y1=318.1, y2=310.7),
        _element(304, "294", x1=741.5, x2=757.3, y1=320.0, y2=312.7),
        _element(305, "yes", x1=649.3, x2=664.0, y1=330.4, y2=323.1),
        _element(306, "306", x1=741.7, x2=757.4, y1=332.3, y2=325.0),
        _element(307, "yes", x1=649.3, x2=664.0, y1=342.8, y2=335.4),
        _element(308, "492", x1=741.4, x2=757.3, y1=344.7, y2=337.4),
        _element(309, "yes", x1=649.3, x2=664.0, y1=355.1, y2=347.8),
        _element(310, "300", x1=741.7, x2=757.3, y1=357.0, y2=349.8),
        _element(311, "yes", x1=649.3, x2=664.0, y1=367.5, y2=360.1),
        _element(312, "481", x1=741.4, x2=756.0, y1=369.4, y2=362.1),
        _element(313, "no", x1=651.9, x2=661.9, y1=379.6, y2=374.2),
        _element(314, "236", x1=741.5, x2=757.4, y1=381.8, y2=374.5),
        # Header/unit labels -- must not be treated as data rows.
        _element(315, "[kg]", x1=743.5, x2=755.4, y1=393.2, y2=385.7),
        _element(316, "hose port", x1=634.8, x2=679.3, y1=406.5, y2=397.4),
        _element(317, "Option System weight", x1=637.9, x2=675.3, y1=436.4, y2=425.3),
    ]


def test_detect_recovers_door_identification_block_in_correct_row_order() -> None:
    detector = TextGridTableDetector()

    result = detector.detect(_door_identification_block_elements())

    assert result is not None
    assert result.rows == [
        ["", "", ""],
        ["1", "1615.2208", "-"],
        ["2", "1615.3206", "-"],
        ["3", "1615.3205", "-"],
        ["4", "1615.4201", "-"],
        ["5", "1615.4203", "-"],
        ["6", "1615.5203", "-"],
        ["7", "1615.5204", "-"],
        ["8", "1615.4208", "-"],
    ]


def test_detect_only_consumes_the_data_row_elements() -> None:
    detector = TextGridTableDetector()
    elements = _door_identification_block_elements()

    result = detector.detect(elements)

    assert result is not None
    # 8 data rows x 3 columns = 24 consumed elements; the 3 header/title
    # elements (294, 295, 296) must NOT be swept in.
    assert len(result.consumed_indices) == 24
    assert {294, 295, 296}.isdisjoint(result.consumed_indices)


def test_detect_recovers_option_system_weight_and_fixes_reversed_row_order() -> None:
    # Regression guard for a real bug: Docling emitted this block's rows in
    # its own bottom-to-top order (pos 8 first, pos 1 last), which is
    # exactly the order the DB previously stored it in as loose text.
    detector = TextGridTableDetector()

    result = detector.detect(_option_system_weight_elements())

    assert result is not None
    assert result.rows == [
        ["", ""],
        ["no", "236"],
        ["yes", "481"],
        ["yes", "300"],
        ["yes", "492"],
        ["yes", "306"],
        ["yes", "294"],
        ["yes", "296"],
        ["no", "247"],
    ]


def test_detect_returns_none_for_too_few_elements() -> None:
    detector = TextGridTableDetector()

    elements = [
        _element(0, "a", x1=0, x2=10, y1=100, y2=90),
        _element(1, "b", x1=20, x2=30, y1=100, y2=90),
    ]

    assert detector.detect(elements) is None


def test_detect_returns_none_for_ordinary_running_paragraph_text() -> None:
    # Ordinary reflowed prose -- several short lines, each spanning nearly
    # the full page width, stacked vertically -- must not be mistaken for a
    # table. There is only one real "column" here (every line starts at
    # roughly the same left edge and varies wildly in right-edge position),
    # so this should never produce >= 2 consistent column slots.
    detector = TextGridTableDetector()

    elements = [
        _element(0, "This manual describes the fire sliding door system", x1=50, x2=380, y1=500, y2=490),
        _element(1, "installation, operation, and maintenance procedures", x1=50, x2=410, y1=485, y2=475),
        _element(2, "for the A3000 and E3000mini drive types covered here.", x1=50, x2=440, y1=470, y2=460),
        _element(3, "Read all safety instructions before starting any work.", x1=50, x2=420, y1=455, y2=445),
        _element(4, "Keep this document available near the installed unit.", x1=50, x2=400, y1=440, y2=430),
    ]

    assert detector.detect(elements) is None


def test_detect_excludes_a_row_whose_elements_collide_on_the_same_column_slot() -> None:
    # A row with two elements landing on the same column slot does not fit
    # the grid cleanly and must be dropped rather than guessed at, so it
    # should not appear in the output and should not count toward
    # min-rows/consistency.
    detector = TextGridTableDetector()

    clean_rows = [
        _element(index, str(index), x1=0, x2=10, y1=100 - index * 20, y2=90 - index * 20)
        for index in range(4)
    ] + [
        _element(100 + index, f"v{index}", x1=100, x2=110, y1=100 - index * 20, y2=90 - index * 20)
        for index in range(4)
    ]
    # A 5th "row" where both elements sit at the SAME x-position as the
    # first column -- both would map to the same nearest slot.
    colliding_row = [
        _element(200, "x", x1=0, x2=10, y1=-20, y2=-30),
        _element(201, "y", x1=1, x2=11, y1=-20, y2=-30),
    ]

    result = detector.detect(clean_rows + colliding_row)

    assert result is not None
    assert len(result.rows) - 1 == 4  # header + 4 clean data rows only
    assert {200, 201}.isdisjoint(result.consumed_indices)
