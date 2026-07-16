from __future__ import annotations

from src.application.workflows.question_answering.answer_context.maintenance.maintenance_candidate_parser import (
    looks_like_maintenance_task,
)
from src.application.workflows.question_answering.answer_context.tables.table_header_semantics import (
    match_header_role,
    schedule_interval_labels,
)
from src.application.workflows.question_answering.answer_context.tables.table_query_strategy import (
    TableQueryStrategy,
)
from src.application.workflows.shared.table_category import TableCategory
from src.application.workflows.shared.table_shape import TableShape

_RECORD_TABLE_CATEGORIES = frozenset(
    {
        TableCategory.TECHNICAL_DATA_TABLE,
        TableCategory.OPERATING_LIMITS_TABLE,
        TableCategory.CONNECTION_TABLE,
        TableCategory.IDENTIFIER_TABLE,
        TableCategory.OPERATION_REFERENCE_TABLE,
        TableCategory.SENSOR_INSTRUMENT_TABLE,
    }
)
_RECORD_TABLE_CHUNK_TYPES = frozenset({"technical_specification", "certification_info"})


def resolve_table_type(
    *,
    table_category: str | None,
    table_shape: str | None,
    chunk_type: str | None,
    headers: list[str] | None = None,
    rows: list[list[str]] | None = None,
) -> tuple[TableQueryStrategy, dict[int, str]]:
    """Single source of truth for "what kind of table is this," shared by the
    deterministic answer-renderer path (`AnswerTableSchemaInferer`) and the
    generic-LLM prompt path (`PromptTableTypeDetector`).

    Ordering invariant: the header-role/row-content rules below MUST stay
    ahead of the table_category/table_shape/chunk_type rules, matching the
    precedence `AnswerTableSchemaInferer` already used before this was
    extracted. Do not move the header-role block after the category/shape
    checks -- that ordering is what keeps every currently-reachable input's
    resolved type (and therefore both adapters' output) unchanged by this
    refactor. Category/shape/chunk_type checks are otherwise mutually
    exclusive (a table has exactly one `table_category` string), so their
    relative order among themselves does not affect correctness.
    """
    headers = headers or []
    column_roles = {
        index: role
        for index, header in enumerate(headers)
        if (role := match_header_role(header)) is not None
    }
    schedule_columns = {
        index: interval_labels
        for index, header in enumerate(headers)
        if (interval_labels := schedule_interval_labels(header))
    }

    if schedule_columns:
        implicit_roles = _infer_implicit_maintenance_roles(
            headers=headers,
            rows=rows or [],
            schedule_columns=schedule_columns,
            existing_roles=column_roles,
        )
        if implicit_roles:
            column_roles.update(implicit_roles)

    roles = set(column_roles.values())
    category = (table_category or "").strip().lower()
    shape = (table_shape or "").strip().lower()
    chunk = (chunk_type or "").strip().lower()

    if "task" in roles and schedule_columns:
        return TableQueryStrategy.MAINTENANCE_SCHEDULE_MATRIX, column_roles
    if "task" in roles and "interval" in roles:
        return TableQueryStrategy.MAINTENANCE_SCHEDULE_TABLE, column_roles
    if "label" in roles and "value" in roles:
        return TableQueryStrategy.KEY_VALUE_TABLE, column_roles

    if shape == TableShape.MAINTENANCE_SCHEDULE_MATRIX:
        return TableQueryStrategy.MAINTENANCE_SCHEDULE_MATRIX, column_roles
    if shape == TableShape.PERFORMANCE_CURVE_MATRIX:
        return TableQueryStrategy.PERFORMANCE_CURVE_MATRIX, column_roles
    if shape == TableShape.SPECIFICATION_MATRIX:
        return TableQueryStrategy.SPECIFICATION_MATRIX, column_roles

    if category == TableCategory.TOC_TABLE:
        return TableQueryStrategy.TOC_TABLE, column_roles
    if category == TableCategory.MAINTENANCE_INTERVAL_TABLE:
        return TableQueryStrategy.MAINTENANCE_SCHEDULE_TABLE, column_roles
    if category == TableCategory.TROUBLESHOOTING_TABLE:
        return TableQueryStrategy.TROUBLESHOOTING_TABLE, column_roles
    if category == TableCategory.SPARE_PARTS_TABLE:
        return TableQueryStrategy.SPARE_PARTS_TABLE, column_roles
    if category == TableCategory.CERTIFICATION_TABLE:
        return TableQueryStrategy.CERTIFICATION_TABLE, column_roles
    if category in _RECORD_TABLE_CATEGORIES:
        return TableQueryStrategy.RECORD_TABLE, column_roles

    if chunk in _RECORD_TABLE_CHUNK_TYPES:
        return TableQueryStrategy.RECORD_TABLE, column_roles

    return TableQueryStrategy.GENERAL_TABLE, column_roles


def _infer_implicit_maintenance_roles(
    *,
    headers: list[str],
    rows: list[list[str]],
    schedule_columns: dict[int, tuple[str, ...]],
    existing_roles: dict[int, str],
) -> dict[int, str]:
    if not rows:
        return {}

    implicit_roles: dict[int, str] = {}
    notes_index = _implicit_notes_index(headers, existing_roles)
    if notes_index is not None:
        implicit_roles[notes_index] = "notes"

    task_index = _implicit_task_index(
        headers=headers,
        rows=rows,
        schedule_columns=schedule_columns,
        existing_roles={**existing_roles, **implicit_roles},
    )
    if task_index is None:
        return implicit_roles

    implicit_roles[task_index] = "task"
    return implicit_roles


def _implicit_notes_index(
    headers: list[str],
    existing_roles: dict[int, str],
) -> int | None:
    for index, role in existing_roles.items():
        if role == "notes":
            return index
    for index, header in enumerate(headers):
        normalized = " ".join(str(header or "").strip().lower().split())
        if normalized in {"reference", "task reference"}:
            return index
    return None


def _implicit_task_index(
    *,
    headers: list[str],
    rows: list[list[str]],
    schedule_columns: dict[int, tuple[str, ...]],
    existing_roles: dict[int, str],
) -> int | None:
    best_index: int | None = None
    best_score = 0

    for index, header in enumerate(headers):
        if existing_roles.get(index) in {"task", "notes", "interval"}:
            continue

        text_match_count = 0
        rich_text_count = 0
        non_empty_count = 0

        for row in rows:
            if index >= len(row):
                continue
            cell = " ".join(str(row[index] or "").strip().split())
            if not cell:
                continue
            non_empty_count += 1
            if looks_like_maintenance_task(cell):
                text_match_count += 1
            if len(cell.split()) >= 4:
                rich_text_count += 1

        if text_match_count == 0:
            continue

        score = (text_match_count * 3) + rich_text_count + non_empty_count
        if index in schedule_columns:
            score += 2
        if score > best_score:
            best_score = score
            best_index = index

    return best_index
