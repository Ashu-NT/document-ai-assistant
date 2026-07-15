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


def test_repair_rows_reconstructs_identifier_rows_with_multi_token_part_numbers() -> None:
    rows = [
        ["P&ID Pos Nr . Service Function Type Part No."],
        ["M.01.01.01 Macerator 1 Lid Position Switch Position switch, FA 4510-2DN"],
        ["M.00.08.01 FW Liquor Transfer Tank Level 4-20mA Radar level LR9020 A00031"],
    ]

    repaired = DoclingTableRowRepairer().repair_rows(rows)

    assert repaired[0] == ["P&ID Pos Nr.", "Service Function Type", "Part No."]
    assert repaired[1] == [
        "M.01.01.01",
        "Macerator 1 Lid Position Switch Position switch,",
        "FA 4510-2DN",
    ]
    assert repaired[2] == [
        "M.00.08.01",
        "FW Liquor Transfer Tank Level 4-20mA Radar level",
        "LR9020 A00031",
    ]


def test_repair_rows_reconstructs_position_quantity_list_and_preserves_note_rows() -> None:
    rows = [
        ["Position  No:"],
        ["P1 1 Motor with drained upper flange -14"],
        ["P2 1 Carrier -18 2"],
        ["Below parts with Pos. No. P19 – P25 are not used for disposers installed in closed cabinet models"],
    ]

    repaired = DoclingTableRowRepairer().repair_rows(rows)

    assert repaired[0] == ["Position No.", "Qty", "Description"]
    assert repaired[1] == ["P1", "1", "Motor with drained upper flange -14"]
    assert repaired[2] == ["P2", "1", "Carrier -18 2"]
    assert repaired[3] == [
        "",
        "",
        "Below parts with Pos. No. P19 – P25 are not used for disposers installed in closed cabinet models",
    ]


def test_repair_rows_reconstructs_single_column_toc_table() -> None:
    rows = [
        ["1.1 Explanation of Documentation ...................................................................................................... 6"],
        ["1.2 Other Applicable Documents ........................................................................................................ 6"],
        ["2.1 General Operating Information ..................................................................................................... 9"],
    ]

    repaired = DoclingTableRowRepairer().repair_rows(rows)

    assert repaired == [
        ["Number", "Title", "Page"],
        ["1.1", "Explanation of Documentation", "6"],
        ["1.2", "Other Applicable Documents", "6"],
        ["2.1", "General Operating Information", "9"],
    ]


def test_repair_rows_reconstructs_multi_column_toc_table() -> None:
    rows = [
        ["1.1", "Explanation of Documentation", "6"],
        ["1.2", "Other Applicable Documents", "6"],
        ["2.1", "General Operating Information", "9"],
    ]

    repaired = DoclingTableRowRepairer().repair_rows(rows)

    assert repaired == [
        ["Number", "Title", "Page"],
        ["1.1", "Explanation of Documentation", "6"],
        ["1.2", "Other Applicable Documents", "6"],
        ["2.1", "General Operating Information", "9"],
    ]


def test_repair_rows_does_not_misclassify_spare_parts_rows_as_toc() -> None:
    rows = [
        ["Position  No:"],
        ["P1 1 Motor with drained upper flange -14"],
        ["P2 1 Carrier -18 2"],
    ]

    repaired = DoclingTableRowRepairer().repair_rows(rows)

    assert repaired[0] == ["Position No.", "Qty", "Description"]
    assert repaired[1][0] == "P1"
    assert repaired[2][0] == "P2"


def test_repair_rows_collapses_uniform_repeated_label_rows() -> None:
    rows = [
        ["D", "Q Q", "M S A", "Task Reference", "", "", "", ""],
        [
            "General Maintenance Work on the Press",
            "General Maintenance Work on the Press",
            "General Maintenance Work on the Press",
            "General Maintenance Work on the Press",
            "General Maintenance Work on the Press",
            "General Maintenance Work on the Press",
            "General Maintenance Work on the Press",
            "General Maintenance Work on the Press",
        ],
        ["X", "", "Inspect basket", "", "", "", "", ""],
    ]

    repaired = DoclingTableRowRepairer().repair_rows(rows)

    assert repaired[1] == [
        "General Maintenance Work on the Press",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ]


def test_repair_rows_preserves_multi_interval_marker_rows() -> None:
    rows = [
        ["D", "W", "M"],
        ["X", "X", "X"],
    ]

    repaired = DoclingTableRowRepairer().repair_rows(rows)

    assert repaired == rows


def test_repair_rows_collapses_duplicate_template_columns_into_field_value_rows() -> None:
    rows = [
        [
            "Card of Task Specification",
            "Card of Task Specification",
            "Card of Task Specification",
        ],
        ["Location:", "Location:", "Machine Room"],
        ["Description of Task:", "Description of Task:", "Service main ropes"],
        ["1.", "1.", "Check rope tension"],
    ]

    repaired = DoclingTableRowRepairer().repair_rows(rows)

    assert repaired == [
        ["Card of Task Specification", ""],
        ["Location:", "Machine Room"],
        ["Description of Task:", "Service main ropes"],
        ["1.", "Check rope tension"],
    ]


def test_repair_rows_merges_sparse_continuation_rows_after_column_collapse() -> None:
    rows = [
        ["Cause", "Corrective action", "Corrective action"],
        ["Blocked filter", "Replace the filter and", "Replace the filter and"],
        ["", "clean the housing before restart.", "clean the housing before restart."],
    ]

    repaired = DoclingTableRowRepairer().repair_rows(rows)

    assert repaired == [
        ["Cause", "Corrective action"],
        ["Blocked filter", "Replace the filter and clean the housing before restart."],
    ]
