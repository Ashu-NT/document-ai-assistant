from src.application.workflows.parsing.normalizers.docling_table_row_repairer import (
    DoclingTableRowRepairer,
)


def test_repair_rows_splits_embedded_maintenance_interval_labels() -> None:
    rows = [
        ["Description", "Interval", "Refers to"],
        ["", "Preventive maintenance 1 First time after 1 month use", ""],
        ["Exchange of other parts When needed", "", ""],
    ]

    repaired = DoclingTableRowRepairer().repair_rows(rows)

    assert repaired[1][0] == "Preventive maintenance 1"
    assert repaired[1][1] == "First time after 1 month use"
    assert repaired[2][0] == "Exchange of other parts"
    assert repaired[2][1] == "When needed"


def test_repair_rows_reconstructs_single_column_identifier_table() -> None:
    rows = [
        ["P&ID Pos Nr. Service Function Type Part No."],
        ["V.00.03.01 Food waste Macerator Suction Valve DN50 Ball Valve, Actuated 24Vdc A00181"],
        ["V.00.04.01 Hot water Flush Solenoid, 2/2-way, 24Vdc A00103"],
    ]

    repaired = DoclingTableRowRepairer().repair_rows(rows)

    assert repaired[0] == ["P&ID Pos Nr.", "Service Function Type", "Part No."]
    assert repaired[1][0] == "V.00.03.01"
    assert repaired[1][2] == "A00181"
    assert "Food waste Macerator Suction Valve" in repaired[1][1]
    assert repaired[2][0] == "V.00.04.01"
    assert repaired[2][2] == "A00103"
