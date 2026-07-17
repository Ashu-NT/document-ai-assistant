from src.application.workflows.parsing.normalizers.table_layout.geometric_row_clusterer import (
    GridElement,
)
from src.application.workflows.parsing.normalizers.table_layout.orphaned_toc_row_reconstructor import (
    OrphanedTocRowReconstructor,
)
from src.domain.common import BoundingBox


def _element(index: int, text: str, *, x1: float, x2: float, y1: float, y2: float) -> GridElement:
    return GridElement(index=index, text=text, bbox=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2))


def _real_page2_right_column_elements() -> list[GridElement]:
    # Exact real bbox/text data captured from a real document
    # (KSB_FSD_A3000_E3000-L-400_DOCUMENTATION_rev4_MY COSMOS.pdf, page 2)
    # whose right-hand TOC column was never recognized as a table by
    # Docling at all -- it came through as these loose text elements.
    return [
        _element(50, "1.6 Internal wiring of control cabinet", x1=451.5, x2=630.0, y1=483.0, y2=472.6),
        _element(52, "................................", x1=632.9, x2=719.6, y1=476.1, y2=474.9),
        _element(53, "...........................", x1=721.3, x2=794.2, y1=476.1, y2=474.9),
        _element(54, "1.7 Sensor and cable transmission", x1=451.5, x2=624.5, y1=464.5, y2=456.3),
        _element(55, ".............................", x1=715.8, x2=794.2, y1=457.7, y2=456.4),
        _element(56, "................................", x1=627.4, x2=714.1, y1=457.7, y2=456.4),
        _element(57, "1.8 Interaction of roller waggons for double sliding door", x1=451.5, x2=724.6, y1=446.1, y2=435.8),
        _element(58, "1.9 Closing frame labyrinth", x1=451.5, x2=586.6, y1=427.7, y2=417.3),
        _element(59, ".........................", x1=726.8, x2=794.2, y1=439.3, y2=438.1),
        _element(60, "................................", x1=677.1, x2=763.8, y1=420.8, y2=419.6),
        _element(61, "................................", x1=588.8, x2=675.5, y1=420.8, y2=419.6),
        _element(62, "1.10 Automatic door lock and safety strip", x1=451.5, x2=648.6, y1=409.3, y2=398.9),
        _element(63, "2 Options", x1=439.8, x2=489.8, y1=390.8, y2=380.6),
        _element(64, "...........", x1=765.4, x2=794.2, y1=420.8, y2=419.6),
        _element(65, "................................", x1=652.2, x2=739.0, y1=402.4, y2=401.2),
        _element(66, "..................", x1=740.6, x2=788.7, y1=402.4, y2=401.2),
        _element(67, "6", x1=796.2, x2=800.7, y1=482.0, y2=474.9),
        _element(68, "7", x1=796.1, x2=800.7, y1=463.4, y2=456.4),
        _element(69, "8", x1=796.0, x2=800.7, y1=445.2, y2=438.0),
        _element(70, "9", x1=796.0, x2=800.6, y1=426.7, y2=419.5),
        _element(71, "10", x1=790.9, x2=800.8, y1=408.3, y2=401.1),
        _element(72, "...................................................................................................", x1=492.7, x2=788.4, y1=384.4, y2=382.7),
        _element(73, "2.1 Alarm communication", x1=450.6, x2=579.7, y1=372.2, y2=364.1),
        _element(74, "................................", x1=583.2, x2=670.0, y1=365.5, y2=364.2),
        _element(75, "2.2 Motor unit tangential", x1=450.6, x2=573.6, y1=353.8, y2=343.6),
        _element(76, "................................", x1=577.7, x2=664.4, y1=347.1, y2=345.9),
        _element(77, "2.3 Elevated motor unit", x1=450.6, x2=569.5, y1=335.4, y2=327.3),
        _element(78, "2.4 Flap control system", x1=450.6, x2=569.6, y1=317.0, y2=306.8),
        _element(79, "................................", x1=671.6, x2=758.3, y1=365.5, y2=364.2),
        _element(80, "................................", x1=666.1, x2=752.8, y1=347.1, y2=345.9),
        _element(81, "................................", x1=572.2, x2=658.9, y1=328.6, y2=327.4),
        _element(82, "................................", x1=572.2, x2=658.9, y1=310.3, y2=309.0),
        _element(83, "2.5", x1=450.6, x2=465.2, y1=298.5, y2=290.5),
        _element(84, "Bolted frame", x1=475.7, x2=536.8, y1=298.6, y2=290.5),
        _element(85, "2.6", x1=450.6, x2=465.2, y1=280.1, y2=272.1),
        _element(86, "...........", x1=759.9, x2=788.7, y1=365.5, y2=364.2),
        _element(87, ".............", x1=754.4, x2=788.7, y1=347.1, y2=345.9),
        _element(88, "................................", x1=660.5, x2=747.2, y1=328.6, y2=327.4),
        _element(89, "...............", x1=748.9, x2=788.7, y1=328.6, y2=327.4),
        _element(90, "................................", x1=660.5, x2=747.2, y1=310.3, y2=309.0),
        _element(91, "................................", x1=539.1, x2=625.8, y1=291.8, y2=290.6),
        _element(92, "................................", x1=627.4, x2=714.1, y1=291.8, y2=290.6),
        _element(93, "Self closing hose port", x1=475.4, x2=579.9, y1=280.2, y2=269.9),
        _element(94, "...............", x1=748.9, x2=788.7, y1=310.3, y2=309.0),
        _element(95, "...........................", x1=715.8, x2=788.7, y1=291.8, y2=290.6),
        _element(96, "................................", x1=583.2, x2=670.0, y1=273.4, y2=272.2),
        _element(97, "2.7", x1=450.6, x2=465.2, y1=261.7, y2=253.7),
        _element(98, "E3000", x1=475.8, x2=506.2, y1=261.7, y2=253.6),
        _element(99, "500", x1=522.4, x2=539.8, y1=261.7, y2=253.6),
        _element(100, "C", x1=510.9, x2=517.9, y1=261.8, y2=253.6),
        _element(101, "-", x1=518.6, x2=521.6, y1=257.1, y2=256.1),
        _element(102, "-", x1=506.9, x2=509.9, y1=257.1, y2=256.1),
        _element(103, "................................", x1=541.8, x2=628.6, y1=254.9, y2=253.7),
        _element(104, "................................", x1=630.2, x2=716.9, y1=254.9, y2=253.7),
        _element(105, "3 Function description", x1=439.9, x2=556.9, y1=243.3, y2=233.2),
        _element(106, "................................", x1=671.6, x2=758.3, y1=273.4, y2=272.2),
        _element(107, "...........", x1=759.9, x2=788.7, y1=273.4, y2=272.2),
        _element(108, "..........................", x1=718.5, x2=788.7, y1=254.9, y2=253.7),
        _element(109, ".............................................................................", x1=558.7, x2=788.4, y1=237.0, y2=235.3),
        _element(110, "3.1 General arrangement", x1=450.8, x2=579.3, y1=227.0, y2=216.6),
        _element(111, "................................", x1=668.8, x2=755.6, y1=220.1, y2=218.9),
        _element(112, "................................", x1=580.5, x2=667.2, y1=220.1, y2=218.9),
        _element(113, "3.2 Function and system behaviour", x1=450.8, x2=627.7, y1=211.1, y2=200.9),
        _element(114, "3", x1=450.8, x2=455.9, y1=195.4, y2=187.4),
        _element(115, "................................", x1=630.2, x2=716.9, y1=204.4, y2=203.2),
        _element(116, "Optional functions", x1=475.3, x2=562.5, y1=195.5, y2=185.3),
        _element(117, "3", x1=450.8, x2=455.9, y1=177.5, y2=169.5),
        _element(118, "3", x1=450.8, x2=455.9, y1=159.2, y2=151.1),
        _element(119, ".", x1=457.4, x2=458.5, y1=188.6, y2=187.5),
        _element(120, ".", x1=457.4, x2=458.5, y1=170.7, y2=169.6),
        _element(121, ".", x1=457.4, x2=458.5, y1=152.3, y2=151.2),
        _element(122, "3", x1=460.0, x2=465.2, y1=195.4, y2=187.4),
        _element(123, "4", x1=459.7, x2=465.1, y1=177.5, y2=169.6),
        _element(124, "5", x1=460.0, x2=465.2, y1=159.0, y2=151.1),
        _element(125, "............", x1=757.2, x2=788.7, y1=220.1, y2=218.9),
        _element(126, "..........................", x1=718.5, x2=788.7, y1=204.4, y2=203.2),
        _element(127, "................................", x1=563.9, x2=650.6, y1=188.7, y2=187.5),
        _element(128, "................................", x1=652.2, x2=739.0, y1=188.7, y2=187.5),
        _element(129, "Passenger's safety", x1=475.8, x2=567.7, y1=177.8, y2=167.3),
        _element(130, "................................", x1=569.4, x2=656.2, y1=170.8, y2=169.6),
        _element(131, "Product quality", x1=475.8, x2=547.5, y1=159.1, y2=148.9),
        _element(132, "..................", x1=740.6, x2=788.7, y1=188.7, y2=187.5),
        _element(133, "................................", x1=657.8, x2=744.5, y1=170.8, y2=169.6),
        _element(134, "................................", x1=550.1, x2=636.8, y1=152.4, y2=151.2),
        _element(135, "................................", x1=638.4, x2=725.2, y1=152.4, y2=151.2),
        _element(136, "................", x1=746.1, x2=788.7, y1=170.8, y2=169.6),
        _element(137, ".......................", x1=726.8, x2=788.7, y1=152.4, y2=151.2),
        _element(138, "11", x1=790.7, x2=800.7, y1=389.8, y2=382.8),
        _element(139, "11", x1=790.9, x2=800.6, y1=371.3, y2=364.3),
        _element(140, "12", x1=790.9, x2=800.6, y1=353.0, y2=345.9),
        _element(141, "13", x1=790.9, x2=800.5, y1=334.5, y2=327.3),
        _element(142, "14", x1=790.9, x2=800.9, y1=316.1, y2=309.0),
        _element(143, "16", x1=790.9, x2=800.7, y1=297.7, y2=290.5),
        _element(144, "18", x1=790.9, x2=800.7, y1=279.3, y2=272.1),
        _element(145, "19", x1=790.9, x2=800.6, y1=260.8, y2=253.6),
        _element(146, "20", x1=790.4, x2=800.9, y1=242.5, y2=235.3),
        _element(147, "20", x1=790.6, x2=800.8, y1=226.0, y2=218.8),
        _element(148, "21", x1=790.6, x2=800.6, y1=210.3, y2=203.2),
        _element(149, "22", x1=790.6, x2=800.6, y1=194.6, y2=187.5),
        _element(150, "22", x1=790.6, x2=800.6, y1=176.7, y2=169.6),
        _element(151, "22", x1=790.6, x2=800.6, y1=158.3, y2=151.2),
    ]


def test_reconstruct_recovers_the_full_real_right_column_toc() -> None:
    reconstructor = OrphanedTocRowReconstructor()

    result = reconstructor.reconstruct(_real_page2_right_column_elements())

    assert result is not None
    data_rows = result.rows[1:]
    titles_and_pages = [(row[1], row[2]) for row in data_rows]
    assert titles_and_pages == [
        ("Internal wiring of control cabinet", "6"),
        ("Sensor and cable transmission", "7"),
        ("Interaction of roller waggons for double sliding door", "8"),
        ("Closing frame labyrinth", "9"),
        ("Automatic door lock and safety strip", "10"),
        ("Options", "11"),
        ("Alarm communication", "11"),
        ("Motor unit tangential", "12"),
        ("Elevated motor unit", "13"),
        ("Flap control system", "14"),
        ("Bolted frame", "16"),
        ("Self closing hose port", "18"),
        ("E3000 - C - 500", "19"),
        ("Function description", "20"),
        ("General arrangement", "20"),
        ("Function and system behaviour", "21"),
        ("Optional functions", "22"),
        ("Passenger's safety", "22"),
        ("Product quality", "22"),
    ]
    numbers = [row[0] for row in data_rows]
    assert numbers == [
        "1.6", "1.7", "1.8", "1.9", "1.10", "2", "2.1", "2.2", "2.3", "2.4",
        "2.5", "2.6", "2.7", "3", "3.1", "3.2", "3.3", "3.4", "3.5",
    ]


def test_reconstruct_returns_none_for_ordinary_paragraph_text() -> None:
    reconstructor = OrphanedTocRowReconstructor()

    elements = [
        _element(0, "This manual describes the fire sliding door system", x1=50, x2=380, y1=500, y2=490),
        _element(1, "installation, operation, and maintenance procedures", x1=50, x2=410, y1=485, y2=475),
        _element(2, "for the A3000 and E3000mini drive types covered here.", x1=50, x2=440, y1=470, y2=460),
        _element(3, "Read all safety instructions before starting any work.", x1=50, x2=420, y1=455, y2=445),
        _element(4, "Keep this document available near the installed unit.", x1=50, x2=400, y1=440, y2=430),
    ]

    assert reconstructor.reconstruct(elements) is None


def test_reconstruct_returns_none_when_too_few_dot_leader_elements() -> None:
    reconstructor = OrphanedTocRowReconstructor()

    elements = [
        _element(0, "Some Title", x1=50, x2=100, y1=500, y2=490),
        _element(1, "..........", x1=110, x2=200, y1=500, y2=490),
        _element(2, "5", x1=210, x2=220, y1=500, y2=490),
        _element(3, "Another Title", x1=50, x2=100, y1=480, y2=470),
        _element(4, "6", x1=210, x2=220, y1=480, y2=470),
    ]

    assert reconstructor.reconstruct(elements) is None
