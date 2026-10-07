"""Tests for TableColumnSemanticClassifier.

Split per the PHASE 2B IMPLEMENT ISOLATED TABLE COLUMN SEMANTIC CLASSIFIER
test philosophy:

- STRUCTURAL CONTRACT tests (determinism, source/structural header
  preservation, evidence/confidence invariants, no-forced-resolution,
  abstention behavior) use small synthetic fixtures built to exercise a
  specific mechanism, and do not assert a human-reviewed "correct" role.

- SEMANTIC GOLDEN tests use only outcomes already empirically OBSERVED by
  directly running this classifier against real cached tables (MTU 39-row
  maintenance table; FWC12 clean Label/Value spec table; FWC12 degenerate
  spare-parts-like table) in this task's own diagnostic run -- they pin
  down REAL, OBSERVED behavior as a regression guard, never a hoped-for
  answer invented ahead of running the code.
"""

from __future__ import annotations

import inspect

from src.application.workflows.shared.table_column_resolution_state import (
    ColumnResolutionState,
)
from src.application.workflows.shared.table_column_semantic_classifier import (
    TableColumnSemanticClassifier,
)
from src.application.workflows.shared.table_column_semantic_role import (
    TableColumnSemanticRole,
)
from src.domain.assets import TableAsset

classifier = TableColumnSemanticClassifier()


def _table(
    *,
    rows,
    table_category=None,
    table_category_confidence=None,
    table_shape=None,
    table_structure_quality=None,
    header_paths=None,
    table_id="table_test",
) -> TableAsset:
    return TableAsset(
        table_id=table_id,
        document_id="doc_test",
        markdown="",
        rows=rows,
        table_category=table_category,
        table_category_confidence=table_category_confidence,
        table_shape=table_shape,
        table_structure_quality=table_structure_quality,
        header_paths=header_paths or [],
    )


# ---------------------------------------------------------------------------
# STRUCTURAL CONTRACT TESTS
# ---------------------------------------------------------------------------


def test_classification_is_deterministic():
    table = _table(
        rows=[
            ["Task", "Item", "Maintenance tasks", "Option"],
            ["WM00285", "ENGINE OPERATIONAL MONITORING", "Check engine oil level", ""],
            ["WM00286", "ENGINE OPERATIONAL MONITORING", "Visually inspect engine for leaks and general condition", ""],
        ],
        table_category="technical_data_table",
        table_category_confidence=0.72,
        table_shape="specification_matrix",
        table_structure_quality=0.98,
        header_paths=[["Parameter"], ["Field", "Item"], ["Field", "Maintenance tasks"], ["Field", "Option"]],
    )
    first = classifier.classify(table)
    second = classifier.classify(table)
    assert first == second


def test_every_source_column_is_represented():
    table = _table(
        rows=[
            ["A", "B", "C", "D"],
            ["x", "y", "z", "w"],
        ]
    )
    result = classifier.classify(table)
    assert [col.column_index for col in result.columns] == [0, 1, 2, 3]


def test_source_header_is_preserved_literally():
    table = _table(
        rows=[
            ["Task", "Item"],
            ["WM00285", "ENGINE OPERATIONAL MONITORING"],
        ],
        header_paths=[["Parameter"], ["Field", "Item"]],
    )
    result = classifier.classify(table)
    assert result.columns[0].source_header == "Task"
    assert result.columns[1].source_header == "Item"


def test_structural_header_is_independently_observable_and_may_diverge_from_source():
    """Regression for the known MTU condition: source header 'Task', but
    the upstream structural interpretation (header_paths) displays
    'Parameter'. Both must remain simultaneously, independently readable --
    neither field may silently replace the other."""
    table = _table(
        rows=[
            ["Task", "Item"],
            ["WM00285", "ENGINE OPERATIONAL MONITORING"],
        ],
        header_paths=[["Parameter"], ["Field", "Item"]],
    )
    result = classifier.classify(table)
    task_column = result.columns[0]
    assert task_column.source_header == "Task"
    assert task_column.structural_header == "Parameter"
    assert task_column.source_header != task_column.structural_header

    item_column = result.columns[1]
    assert item_column.source_header == "Item"
    assert item_column.structural_header == "Item"


def test_partial_resolution_is_normal_not_all_or_nothing():
    """A table is never rejected merely because not every column can be
    characterized -- resolved and non-resolved columns can coexist in the
    same result."""
    table = _table(
        rows=[
            ["Label", "Value", "????"],
            ["Tank Capacity", "1,200L", "qqqqq"],
            ["Pump Capacity", "16,000L/hr", "wwwww"],
        ],
        table_category_confidence=0.95,
        table_structure_quality=0.95,
    )
    result = classifier.classify(table)
    states = {col.column_index: col.resolution_state for col in result.columns}
    assert states[0] == ColumnResolutionState.RESOLVED
    assert states[1] == ColumnResolutionState.RESOLVED
    # column 2's header matches no alias and its content is inconclusive --
    # weak/no evidence, not an affirmatively-understood-but-unmapped
    # concept, so this is UNKNOWN (see ColumnResolutionState's corrected
    # semantics).
    assert states[2] == ColumnResolutionState.UNKNOWN


def test_unlabeled_inconclusive_content_column_is_unknown():
    """A column with no header text and content too sparse/ambiguous in
    shape to vote for any role (not numeric, not rich text, not
    code-like) has no role evidence at all -- UNKNOWN, not a guess."""
    table = _table(
        rows=[
            ["Label", "Value", ""],
            ["Tank Capacity", "1,200L", "foo bar"],
            ["Pump Capacity", "16,000L/hr", "foo bar"],
        ],
        table_category_confidence=0.95,
        table_structure_quality=0.95,
    )
    result = classifier.classify(table)
    blank_column = result.columns[2]
    assert blank_column.source_header is None
    assert blank_column.resolution_state == ColumnResolutionState.UNKNOWN
    assert blank_column.semantic_role is None
    assert blank_column.confidence is None
    assert not any(item.role is not None for item in blank_column.evidence)


def test_ambiguous_state_never_itself_reported_as_a_semantic_role():
    for role in TableColumnSemanticRole:
        assert role.value != "ambiguous"


def test_ambiguous_column_exposes_multiple_plausible_candidates_not_a_single_guess():
    """A header whose own alias data is genuinely ambiguous ("item" is
    listed under both "label" and "position" in the real alias vocabulary)
    must surface BOTH candidates rather than silently picking the first one
    a dict happens to iterate to -- the exact first-match-wins failure mode
    this design replaces."""
    table = _table(
        rows=[
            ["Task", "Item"],
            ["WM00285", "ENGINE OPERATIONAL MONITORING"],
            ["WM00286", "ENGINE MOUNTING ARRANGEMENT"],
        ],
        table_category_confidence=0.95,
        table_structure_quality=0.95,
    )
    result = classifier.classify(table)
    column = result.columns[1]
    assert column.source_header == "Item"
    assert column.resolution_state == ColumnResolutionState.AMBIGUOUS
    assert column.semantic_role is None
    candidate_roles = {role for role, _score in column.candidate_roles}
    assert {TableColumnSemanticRole.LABEL, TableColumnSemanticRole.POSITION} <= candidate_roles
    assert TableColumnSemanticRole.COMPONENT not in candidate_roles


def test_evidence_records_identify_category_role_and_description():
    table = _table(rows=[["Value"], ["1,200"], ["16,000"]], table_category_confidence=0.95, table_structure_quality=0.95)
    result = classifier.classify(table)
    column = result.columns[0]
    assert column.evidence
    for item in column.evidence:
        assert item.category is not None
        assert isinstance(item.description, str) and item.description
        assert isinstance(item.weight, float)


def test_confidence_is_none_unless_resolved():
    table = _table(
        rows=[["Item"], ["ENGINE OPERATIONAL MONITORING"], ["ENGINE MOUNTING"]],
        table_category_confidence=0.95,
        table_structure_quality=0.95,
    )
    result = classifier.classify(table)
    for column in result.columns:
        if column.resolution_state != ColumnResolutionState.RESOLVED:
            assert column.confidence is None
        else:
            assert column.confidence is not None
            assert 0.0 < column.confidence <= 1.0


def test_resolved_confidence_never_exceeds_one():
    table = _table(
        rows=[["Value"], ["1,200"], ["16,000"], ["42,000"]],
        table_category_confidence=0.99,
        table_structure_quality=0.99,
    )
    result = classifier.classify(table)
    for column in result.columns:
        if column.confidence is not None:
            assert column.confidence <= 1.0


def test_weak_lexical_evidence_alone_does_not_force_resolution_under_low_context_trust():
    """A single clean alias match (weight 0.5, exactly at the floor) must
    NOT resolve once contextual dampening applies -- abstention is
    preferred over a resolution that only barely clears the floor before
    context is accounted for."""
    table = _table(
        rows=[["Label", "Value"], ["Tank Capacity", "1,200L"]],
        table_category_confidence=0.6,
        table_structure_quality=0.98,
    )
    result = classifier.classify(table)
    label_column = result.columns[0]
    assert label_column.resolution_state != ColumnResolutionState.RESOLVED


def test_conflicting_lexical_and_structural_evidence_can_prevent_resolution():
    """Lexical evidence voting for one role and structural evidence voting
    for a different role on the SAME column must be representable as
    genuine conflict, not silently resolved toward whichever ran first."""
    table = _table(
        rows=[
            ["Task", "Maintenance tasks"],
            ["WM00285", "Check engine oil level and top up as required"],
            ["WM00286", "Visually inspect engine for leaks and general condition"],
        ],
        header_paths=[["Parameter"], ["Field", "Maintenance tasks"]],
        table_category_confidence=0.72,
        table_structure_quality=0.98,
    )
    result = classifier.classify(table)
    task_header_column = result.columns[0]
    lexical_roles = {
        item.role for item in task_header_column.evidence if item.category.value == "lexical" and item.role
    }
    structural_roles = {
        item.role for item in task_header_column.evidence if item.category.value == "structural" and item.role
    }
    assert TableColumnSemanticRole.TASK in lexical_roles
    assert TableColumnSemanticRole.LABEL in structural_roles
    assert lexical_roles != structural_roles


def test_table_category_confidence_does_not_automatically_resolve_columns():
    """A high table_category_confidence must never, by itself, cause a
    column with no real header/content support to resolve -- table-level
    and column-level confidence are independent."""
    table = _table(
        rows=[["P19", "P16"], ["P20", "P4"], ["P21", "P2"]],
        table_category="spare_parts_table",
        table_category_confidence=0.95,
    )
    result = classifier.classify(table)
    assert all(col.resolution_state != ColumnResolutionState.RESOLVED for col in result.columns)


def test_degenerate_table_abstains_rather_than_guessing():
    table = _table(
        rows=[["P19", "P16"], ["P20", "P4"], ["P21", "P2"]],
        table_category="spare_parts_table",
        table_category_confidence=0.9,
    )
    result = classifier.classify(table)
    for column in result.columns:
        assert column.resolution_state != ColumnResolutionState.RESOLVED


def test_clean_label_value_table_resolves_under_high_context_trust():
    """A clean alias match MAY resolve -- only demonstrated under high
    table_category_confidence/table_structure_quality, i.e. the condition
    this design's confidence model requires before trusting a lone lexical
    signal."""
    table = _table(
        rows=[["Label", "Value"], ["Tank Capacity", "1,200L"], ["Pump Capacity", "16,000L/hr"]],
        table_category="technical_data_table",
        table_category_confidence=0.95,
        table_structure_quality=0.95,
    )
    result = classifier.classify(table)
    label_column, value_column = result.columns
    assert label_column.resolution_state == ColumnResolutionState.RESOLVED
    assert label_column.semantic_role == TableColumnSemanticRole.LABEL
    assert value_column.resolution_state == ColumnResolutionState.RESOLVED
    assert value_column.semantic_role == TableColumnSemanticRole.VALUE


def test_classifier_module_contains_no_mtu_vendor_specific_literals():
    """The classifier's own source code must not hardcode a mapping from
    real MTU content (Item, ENGINE OPERATIONAL MONITORING, WM00285, ENGINE
    MOUNTING) or an Item->component rule -- only generic vocabulary/alias
    data already used elsewhere in this codebase."""
    import src.application.workflows.shared.table_column_semantic_classifier as module

    source = inspect.getsource(module)
    forbidden_literals = (
        "ENGINE OPERATIONAL MONITORING",
        "WM00285",
        "ENGINE MOUNTING",
        "component_name",
    )
    for literal in forbidden_literals:
        assert literal not in source

    # "item" must not be special-cased toward "component" anywhere.
    assert '"item": ("component"' not in source
    assert "'item': ('component'" not in source


def test_state_semantics_case_a_no_evidence_is_unknown():
    """A: zero evidence (no header, content shape that votes for no role
    at all) -> UNKNOWN."""
    table = _table(
        rows=[
            ["Label", "Value", ""],
            ["Tank Capacity", "1,200L", "foo bar"],
            ["Pump Capacity", "16,000L/hr", "foo bar"],
        ],
        table_category_confidence=0.95,
        table_structure_quality=0.95,
    )
    result = classifier.classify(table)
    column = result.columns[2]
    assert not any(item.role is not None for item in column.evidence)
    assert column.resolution_state == ColumnResolutionState.UNKNOWN


def test_state_semantics_case_b_weak_evidence_for_known_role_is_unknown_not_unmapped():
    """B: evidence items DO exist and DO carry a role (short, code-like
    content weakly voting for part_no/position/type), but the score never
    clears PLAUSIBILITY_FLOOR or RESOLVE_FLOOR -- this must be UNKNOWN, not
    UNMAPPED. Weak support for a known role is not the same as an
    affirmatively-understood-but-unmapped concept."""
    table = _table(
        rows=[["", ""], ["X1", "Y1"], ["X2", "Y2"], ["X3", "Y3"]],
        table_category_confidence=0.95,
        table_structure_quality=0.95,
    )
    result = classifier.classify(table)
    column = result.columns[0]
    role_evidence = [item for item in column.evidence if item.role is not None]
    assert role_evidence  # evidence exists and carries a role...
    assert all(item.weight < TableColumnSemanticClassifier.PLAUSIBILITY_FLOOR for item in role_evidence)
    assert column.resolution_state == ColumnResolutionState.UNKNOWN
    assert column.resolution_state != ColumnResolutionState.UNMAPPED


def test_state_semantics_case_c_competing_supported_roles_is_ambiguous():
    """C: already covered by test_ambiguous_column_exposes_multiple_
    plausible_candidates_not_a_single_guess and the real MTU Item-column
    golden test below -- restated here under the explicit A-E naming."""
    table = _table(
        rows=[["Task", "Item"], ["WM00285", "ENGINE OPERATIONAL MONITORING"], ["WM00286", "ENGINE MOUNTING"]],
        table_category_confidence=0.95,
        table_structure_quality=0.95,
    )
    result = classifier.classify(table)
    column = result.columns[1]
    assert column.resolution_state == ColumnResolutionState.AMBIGUOUS


def test_state_semantics_case_d_strong_evidence_for_one_role_is_resolved():
    """D: already covered by test_clean_label_value_table_resolves_under_
    high_context_trust -- restated here under the explicit A-E naming."""
    table = _table(
        rows=[["Label", "Value"], ["Tank Capacity", "1,200L"]],
        table_category_confidence=0.95,
        table_structure_quality=0.95,
    )
    result = classifier.classify(table)
    assert result.columns[0].resolution_state == ColumnResolutionState.RESOLVED


def test_state_semantics_case_e_unmapped_is_currently_unreachable_by_design():
    """E: UNMAPPED requires affirmative, generic evidence of a coherent
    semantic concept independent of role-scoring. No evidence source in
    this classifier establishes that judgment yet, so UNMAPPED must not be
    emitted by ANY of the fixtures exercised across this test module --
    reaching it today would mean a heuristic was added merely to make the
    state appear, which the task explicitly prohibits. The state stays in
    the contract, reserved for a future evidence source capable of that
    distinct judgment."""
    fixtures = [
        _table(rows=[["A", "B", "C", "D"], ["x", "y", "z", "w"]]),
        _table(
            rows=[["Label", "Value", "????"], ["Tank Capacity", "1,200L", "qqqqq"], ["Pump Capacity", "16,000L/hr", "wwwww"]],
            table_category_confidence=0.95,
            table_structure_quality=0.95,
        ),
        _table(rows=[["P19", "P16"], ["P20", "P4"], ["P21", "P2"]], table_category="spare_parts_table", table_category_confidence=0.9),
        _real_mtu_shaped_table(),
    ]
    for table in fixtures:
        result = classifier.classify(table)
        for column in result.columns:
            assert column.resolution_state != ColumnResolutionState.UNMAPPED


def test_no_first_match_wins_shortcut_in_alias_lookup():
    """A header string that is a genuine alias of more than one role must
    surface every matching role, never only the first one a dict iterates
    to."""
    from src.application.workflows.shared.table_column_semantic_classifier import (
        _lookup_roles_by_text,
    )

    roles = _lookup_roles_by_text("item")
    assert TableColumnSemanticRole.LABEL in roles
    assert TableColumnSemanticRole.POSITION in roles
    assert len(roles) >= 2


# ---------------------------------------------------------------------------
# SEMANTIC GOLDEN TESTS -- pin down REAL, OBSERVED behavior from running this
# classifier against real cached tables (see diagnostic run output captured
# in this task's final report). Not aspirational; not human-reviewed golden
# truth -- a regression guard over behavior already demonstrated to occur.
# ---------------------------------------------------------------------------


def _real_mtu_shaped_table() -> TableAsset:
    return _table(
        table_id="table_family_table_a9dfb7ab4dfe441db848ef7a093d91bb",
        rows=[
            ["Task", "Item", "Maintenance tasks", "Option", ""],
            [
                "WM00285",
                "ENGINE OPERATIONAL MONITORING",
                "Check engine oil level",
                "",
                "(→ Page 192)",
            ],
            [
                "WM00286",
                "ENGINE OPERATIONAL MONITORING",
                "Visually inspect engine for leaks and general condition",
                "",
                "(→ Page 74)",
            ],
        ],
        table_category="technical_data_table",
        table_category_confidence=0.72,
        table_shape="specification_matrix",
        table_structure_quality=0.98,
        header_paths=[
            ["Parameter"],
            ["Field", "Item"],
            ["Field", "Maintenance tasks"],
            ["Field", "Option"],
        ],
    )


def test_real_mtu_table_maintenance_tasks_column_resolves_to_task():
    result = classifier.classify(_real_mtu_shaped_table())
    maintenance_tasks_column = result.columns[2]
    assert maintenance_tasks_column.source_header == "Maintenance tasks"
    assert maintenance_tasks_column.resolution_state == ColumnResolutionState.RESOLVED
    assert maintenance_tasks_column.semantic_role == TableColumnSemanticRole.TASK


def test_real_mtu_table_item_column_is_ambiguous_between_label_and_position_not_component():
    result = classifier.classify(_real_mtu_shaped_table())
    item_column = result.columns[1]
    assert item_column.source_header == "Item"
    assert item_column.resolution_state == ColumnResolutionState.AMBIGUOUS
    candidate_roles = {role for role, _score in item_column.candidate_roles}
    assert candidate_roles == {TableColumnSemanticRole.LABEL, TableColumnSemanticRole.POSITION}


def test_real_mtu_table_task_code_column_does_not_force_resolution():
    """The literal header 'Task' lexically matches role 'task', but real
    content evidence (short WM##### codes vs. the genuinely descriptive
    'Maintenance tasks' column) and relational pressure from that stronger
    column must prevent this column from confidently resolving to 'task'
    anyway."""
    result = classifier.classify(_real_mtu_shaped_table())
    task_code_column = result.columns[0]
    assert task_code_column.source_header == "Task"
    assert task_code_column.resolution_state != ColumnResolutionState.RESOLVED


def test_real_mtu_table_option_column_abstains():
    result = classifier.classify(_real_mtu_shaped_table())
    option_column = result.columns[3]
    assert option_column.source_header == "Option"
    assert option_column.resolution_state != ColumnResolutionState.RESOLVED
    assert option_column.semantic_role is None


def test_real_fwc12_degenerate_spare_parts_table_has_no_explicit_header_and_abstains():
    """Observed finding: this real table's own header row ('P19', 'P16') is
    not even recognized as an explicit header by the shared row
    canonicalizer, so every column abstains -- correctly reflecting a
    genuinely degenerate real table rather than forcing a guess."""
    table = _table(
        table_id="table_b24dd2a4ad84425d8c5ae32f4f55b828",
        rows=[["P19", "P16"], ["P20", "P4"], ["P21", "P2"]],
        table_category="spare_parts_table",
        table_category_confidence=0.9,
    )
    result = classifier.classify(table)
    assert all(col.source_header is None for col in result.columns)
    assert all(col.resolution_state != ColumnResolutionState.RESOLVED for col in result.columns)
