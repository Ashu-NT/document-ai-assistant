from src.application.workflows.extraction.specialized.maintenance_task_component_backfill import (
    backfill_maintenance_task_component_names,
)
from src.domain.extraction import MaintenanceTask
from src.domain.assets import TableAsset

# Real MTU table shape (pages 67-68): header row + data rows, with the
# source column literally named "Item" -- exactly the structural fact this
# fix is grounded in, confirmed earlier this investigation via direct
# TableCellSpan inspection (no merged cells; values are genuinely re-typed
# per row).
_MTU_HEADER = ["Task", "Item", "Maintenance tasks", "Option"]
_MTU_ROWS = [
    _MTU_HEADER,
    ["WM00285", "ENGINE OPERATIONAL MONITORING", "Check engine oil level", ""],
    [
        "WM00286",
        "ENGINE OPERATIONAL MONITORING",
        "Visually inspect engine for leaks and general condition",
        "",
    ],
    ["WM00290", "LUBE OIL SYSTEM", "Check lube oil pressure", ""],
]


def _table(rows: list[list[str]], header_paths: list[list[str]] | None = None) -> TableAsset:
    return TableAsset(
        table_id="table_mtu",
        document_id="doc_mtu",
        markdown="irrelevant",
        rows=rows,
        header_paths=header_paths or [],
    )


def _task(title: str, component_name: str | None = None) -> MaintenanceTask:
    return MaintenanceTask(
        task_id=f"task_{title[:8]}",
        document_id="doc_mtu",
        title=title,
        component_name=component_name,
    )


def test_backfills_the_two_known_failing_rows_from_the_real_table_shape():
    """The two rows this fix exists for -- real titles, real expected
    component value, taken directly from the reviewed golden fixture."""
    table = _table(_MTU_ROWS)
    entities = [
        _task("Check engine oil level"),
        _task("Visually inspect engine for leaks and general condition"),
    ]

    backfilled = backfill_maintenance_task_component_names(
        entities, table=table, row_start=1, row_end=3
    )

    assert backfilled == 2
    assert entities[0].component_name == "ENGINE OPERATIONAL MONITORING"
    assert entities[1].component_name == "ENGINE OPERATIONAL MONITORING"


def test_never_overrides_an_already_populated_component_name():
    table = _table(_MTU_ROWS)
    entities = [_task("Check engine oil level", component_name="Something the model already said")]

    backfilled = backfill_maintenance_task_component_names(
        entities, table=table, row_start=1, row_end=3
    )

    assert backfilled == 0
    assert entities[0].component_name == "Something the model already said"


def test_does_nothing_when_table_has_no_item_column():
    table = _table(
        [["Row ID", "Component", "Description"], ["ID001", "Component 1", "Task 1"]]
    )
    entities = [_task("Task 1")]

    backfilled = backfill_maintenance_task_component_names(
        entities, table=table, row_start=1, row_end=1
    )

    assert backfilled == 0
    assert entities[0].component_name is None


def test_does_nothing_when_title_does_not_match_any_row_missing_evidence():
    table = _table(_MTU_ROWS)
    entities = [_task("A task that does not appear in this table at all")]

    backfilled = backfill_maintenance_task_component_names(
        entities, table=table, row_start=1, row_end=3
    )

    assert backfilled == 0
    assert entities[0].component_name is None


def test_does_nothing_when_title_matches_more_than_one_row_ambiguous_evidence():
    """Ambiguous: the same title text happens to appear in two rows within
    the window -- must abstain, never guess which one is correct."""
    duplicate_rows = [
        _MTU_HEADER,
        ["WM00285", "ENGINE OPERATIONAL MONITORING", "Check engine oil level", ""],
        ["WM00999", "LUBE OIL SYSTEM", "Check engine oil level", ""],
    ]
    table = _table(duplicate_rows)
    entities = [_task("Check engine oil level")]

    backfilled = backfill_maintenance_task_component_names(
        entities, table=table, row_start=1, row_end=2
    )

    assert backfilled == 0
    assert entities[0].component_name is None


def test_does_nothing_when_matched_rows_item_cell_is_itself_empty_conflicting_evidence():
    """The row matches by title, but its OWN Item cell is blank -- the
    source itself provides no value, so none must be invented."""
    rows_with_blank_item = [
        _MTU_HEADER,
        ["WM00285", "", "Check engine oil level", ""],
    ]
    table = _table(rows_with_blank_item)
    entities = [_task("Check engine oil level")]

    backfilled = backfill_maintenance_task_component_names(
        entities, table=table, row_start=1, row_end=1
    )

    assert backfilled == 0
    assert entities[0].component_name is None


def test_only_backfills_rows_within_the_given_window_row_range():
    """A title that matches a row OUTSIDE this window's row_start/row_end
    must not be used -- this window's evidence is scoped to its own rows."""
    table = _table(_MTU_ROWS)
    entities = [_task("Check lube oil pressure")]  # that's row 3, not in window 1-2

    backfilled = backfill_maintenance_task_component_names(
        entities, table=table, row_start=1, row_end=2
    )

    assert backfilled == 0
    assert entities[0].component_name is None


def test_matching_is_case_and_whitespace_insensitive():
    table = _table(_MTU_ROWS)
    entities = [_task("  check ENGINE oil   level  ")]

    backfilled = backfill_maintenance_task_component_names(
        entities, table=table, row_start=1, row_end=3
    )

    assert backfilled == 1
    assert entities[0].component_name == "ENGINE OPERATIONAL MONITORING"


def test_structural_header_divergence_does_not_confuse_matching():
    """header_paths may label this column differently (e.g. the real MTU
    table's own "Parameter"/axis-label quirk on a DIFFERENT column) -- the
    backfill must still find the literal "Item" header in the canonicalized
    row data regardless of what header_paths says about OTHER columns."""
    table = _table(
        _MTU_ROWS,
        header_paths=[["Parameter"], ["Field", "Item"], ["Field", "Maintenance tasks"], ["Field", "Option"]],
    )
    entities = [_task("Check engine oil level")]

    backfilled = backfill_maintenance_task_component_names(
        entities, table=table, row_start=1, row_end=3
    )

    assert backfilled == 1
    assert entities[0].component_name == "ENGINE OPERATIONAL MONITORING"


def test_empty_entities_list_is_a_safe_no_op():
    table = _table(_MTU_ROWS)
    assert backfill_maintenance_task_component_names([], table=table, row_start=1, row_end=3) == 0


def test_table_with_only_a_header_row_is_a_safe_no_op():
    table = _table([_MTU_HEADER])
    entities = [_task("Check engine oil level")]
    backfilled = backfill_maintenance_task_component_names(
        entities, table=table, row_start=1, row_end=1
    )
    assert backfilled == 0
    assert entities[0].component_name is None
