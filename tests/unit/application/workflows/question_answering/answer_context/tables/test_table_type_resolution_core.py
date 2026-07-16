import pytest

from src.application.prompts.answer_generation.prompt_context.models.prompt_source_view import (
    PromptSourceView,
)
from src.application.prompts.answer_generation.prompt_context.tables.prompt_table_type_detector import (
    _RESOLVED_TYPE_TO_PROMPT_LABEL,
    PromptTableTypeDetector,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table_schema_inferer import (
    _RESOLVED_TYPE_TO_ANSWER_KIND,
    AnswerTableSchemaInferer,
)
from src.application.workflows.question_answering.answer_context.tables.table_query_strategy import (
    TableQueryStrategy,
)
from src.application.workflows.question_answering.answer_context.tables.table_type_resolution_core import (
    resolve_table_type,
)
from src.application.workflows.shared.table_category import TableCategory
from src.application.workflows.shared.table_shape import TableShape


def _combinations():
    for category in TableCategory:
        for shape in TableShape:
            yield category, shape


@pytest.mark.parametrize("category,shape", list(_combinations()))
def test_resolve_table_type_matches_both_adapters_for_every_category_and_shape_combination(
    category: TableCategory,
    shape: TableShape,
) -> None:
    resolved, _ = resolve_table_type(
        table_category=category.value,
        table_shape=shape.value,
        chunk_type=None,
        headers=[],
        rows=None,
    )
    assert isinstance(resolved, TableQueryStrategy)

    answer_kind = AnswerTableSchemaInferer().infer(
        chunk_type=None,
        headers=[],
        table_category=category.value,
        table_shape=shape.value,
    )[0]
    assert answer_kind == _RESOLVED_TYPE_TO_ANSWER_KIND[resolved]

    prompt_label = _RESOLVED_TYPE_TO_PROMPT_LABEL[resolved]
    if prompt_label != "general_table":
        # A non-"general_table" mapping is returned immediately by the
        # detector without falling through to its residual heuristics, so
        # this is a hard, always-true equality -- proof the two adapters
        # cannot silently diverge for any input the shared core resolves
        # to a specific kind.
        source = PromptSourceView(
            source_number=1,
            chunk_id="chunk_001",
            chunk_type=None,
            section_path="N/A",
            table_shape=shape.value,
            metadata={"table_category": category.value},
        )
        assert (
            PromptTableTypeDetector().detect(source, headers=[]) == prompt_label
        )
