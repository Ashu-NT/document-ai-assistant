from src.application.workflows.parsing.tables.semantics import (
    TableCategory,
    TableSemanticClassifier,
)
from src.domain.assets import TableAsset


def _make_table(rows: list[list[str]], *, markdown: str = "table") -> TableAsset:
    return TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown=markdown,
        rows=rows,
        row_count=len(rows),
        column_count=len(rows[0]) if rows else None,
    )


def test_classify_detects_generic_maintenance_interval_matrix() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table(
            [
                ["Task", "Daily", "Weekly", "Monthly"],
                ["Inspect filter", "x", "", "x"],
            ]
        ),
    )

    assert category == TableCategory.MAINTENANCE_INTERVAL_TABLE
    assert confidence >= 0.9


def test_classify_detects_headerless_technical_data_table() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table(
            [
                ["Tank Capacity", "1,200L"],
                ["Pump Capacity", "max 16,000L/hr"],
                ["Voltage", "400V 50Hz"],
            ]
        ),
        section_path=["Safety", "Warnings"],
    )

    assert category == TableCategory.TECHNICAL_DATA_TABLE
    assert confidence >= 0.85


def test_classify_prefers_maintenance_interval_direct_evidence_over_spare_parts_mentions() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table(
            [
                ["Description", "Interval", "Refers to"],
                ["Check line strainer", "First month, then when needed", ""],
                [
                    "Preventive maintenance",
                    "Every 2 years",
                    "Replace parts shown in spare parts table",
                ],
            ]
        ),
        section_path=["Spare Parts", "Preventive Maintenance"],
    )

    assert category == TableCategory.MAINTENANCE_INTERVAL_TABLE
    assert confidence >= 0.85


def test_classify_detects_troubleshooting_table() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table(
            [
                ["Problem", "Probable causes", "Possible remedies"],
                ["Low pressure", "Blocked filter", "Clean filter"],
            ]
        ),
    )

    assert category == TableCategory.TROUBLESHOOTING_TABLE
    assert confidence >= 0.9


def test_classify_detects_technical_data_table() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table(
            [
                ["Parameter", "Value"],
                ["Voltage", "24 V"],
                ["Power", "5 kW"],
            ]
        ),
    )

    assert category == TableCategory.TECHNICAL_DATA_TABLE
    assert confidence >= 0.8


def test_classify_detects_toc_table_from_item_label() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table([["1", "Introduction", "2"]]),
        item_label="document_index",
    )

    assert category == TableCategory.TOC_TABLE
    assert confidence >= 0.99


def test_classify_detects_schedule_matrix_with_reference_columns() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table(
            [
                ["D", "Q", "A", "Task Reference"],
                ["X", "", "", "Inspect basket"],
                ["", "X", "", "Change lubricant"],
            ]
        ),
    )

    assert category == TableCategory.MAINTENANCE_INTERVAL_TABLE
    assert confidence >= 0.9


def test_classify_uses_nearby_context_for_compact_maintenance_schedule_table() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table(
            [
                ["D", "Q Q", "M S A", "Task Reference"],
                ["X", "", "Inspect basket", ""],
                ["", "X", "Change lubricant", "See annex"],
            ]
        ),
        nearby_text="Half-yearly maintenance work. Annual maintenance work.",
    )

    assert category == TableCategory.MAINTENANCE_INTERVAL_TABLE
    assert confidence >= 0.85


def test_classify_detects_split_header_spare_parts_table() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table(
            [
                [
                    "Position No:",
                    "Qty: Denomination: Spare Part",
                    "No: Included in Service Package:",
                ],
                ["P31 1", "Disassembly screw for carrier", "-18/02 2"],
                ["P32 1", "Torque protection bar", "-28/V"],
            ]
        ),
        section_path=["Components", "Spare Parts List"],
    )

    assert category == TableCategory.SPARE_PARTS_TABLE
    assert confidence >= 0.85


def test_classify_detects_lubrication_schedule_from_generic_section_and_time_signals() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table(
            [
                ["Task", "Lubricant", "Interval"],
                ["Main bearing", "Grease", "Every 500 hours"],
                ["Drive shaft", "Oil", "When needed"],
            ]
        ),
        section_path=["Components", "Vacuum Pump", "Lubrication Schedule"],
    )

    assert category == TableCategory.MAINTENANCE_INTERVAL_TABLE
    assert confidence >= 0.85


def test_classify_detects_troubleshooting_from_generic_section_context() -> None:
    category, confidence = TableSemanticClassifier().classify(
        table=_make_table(
            [
                ["Symptom", "Cause", "Action"],
                ["Low pressure", "Blocked line", "Clean the line"],
                ["No start", "No power", "Check the supply"],
            ]
        ),
        section_path=["Components", "Pump", "Trouble-Shooting"],
    )

    assert category == TableCategory.TROUBLESHOOTING_TABLE
    assert confidence >= 0.85


def test_classify_valve_list_is_not_sensor_instrument_table_from_pid_text_alone() -> None:
    category, _ = TableSemanticClassifier().classify(
        table=_make_table(
            [
                ["P&ID Pos Nr.", "Service Function", "Type", "Part No."],
                ["V.00.01.01", "Dry Running Protection", "Solenoid", "A00103"],
                ["V.00.03.01", "Macerator Suction Valve", "Ball Valve", "A00181"],
            ]
        ),
        section_path=["Components", "Valve List"],
    )

    assert category == TableCategory.IDENTIFIER_TABLE
