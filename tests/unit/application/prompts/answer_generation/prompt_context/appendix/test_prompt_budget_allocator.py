from src.application.prompts.answer_generation.prompt_context.appendix import (
    PromptBudgetAllocator,
)
from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
    PromptSourceView,
    PromptTableRowView,
    PromptTableView,
)


def test_allocate_prefers_small_appendix_for_table_heavy_context() -> None:
    context = PromptContextBundle(
        answer_intent_value="table_summary",
        source_count=2,
        sources=[PromptSourceView(source_number=1, chunk_id="chunk_001")],
        tables=[
            PromptTableView(
                table_id="chunk_001:table",
                table_type="specification_table",
                source_number=1,
                chunk_id="chunk_001",
                headers=["Parameter", "Value"],
                rows=[
                    PromptTableRowView(
                        source_row_index=1,
                        cells=["Test pressure", "700 bar"],
                    )
                ],
            )
        ],
    )

    budget = PromptBudgetAllocator().allocate(context)

    assert budget.max_sources == 2
    assert budget.max_chars_per_source == 350


def test_allocate_allows_larger_appendix_for_sparse_context() -> None:
    context = PromptContextBundle(
        answer_intent_value="general",
        source_count=1,
        sources=[PromptSourceView(source_number=1, chunk_id="chunk_001")],
    )

    budget = PromptBudgetAllocator().allocate(context)

    assert budget.max_sources == 4
    assert budget.max_chars_per_source == 1200
