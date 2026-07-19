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


def _sparse_context() -> PromptContextBundle:
    return PromptContextBundle(
        answer_intent_value="general",
        source_count=1,
        sources=[PromptSourceView(source_number=1, chunk_id="chunk_001")],
    )


def test_allocate_matches_default_budget_at_the_reference_num_ctx() -> None:
    default_budget = PromptBudgetAllocator().allocate(_sparse_context())
    reference_budget = PromptBudgetAllocator(num_ctx=8192).allocate(_sparse_context())

    assert reference_budget == default_budget


def test_allocate_matches_default_budget_below_the_reference_num_ctx() -> None:
    default_budget = PromptBudgetAllocator().allocate(_sparse_context())
    smaller_budget = PromptBudgetAllocator(num_ctx=4096).allocate(_sparse_context())

    assert smaller_budget == default_budget


def test_allocate_scales_up_budget_for_a_larger_num_ctx() -> None:
    default_budget = PromptBudgetAllocator().allocate(_sparse_context())
    scaled_budget = PromptBudgetAllocator(num_ctx=16384).allocate(_sparse_context())

    assert scaled_budget.max_sources > default_budget.max_sources
    assert scaled_budget.max_chars_per_source > default_budget.max_chars_per_source


def test_allocate_caps_scaling_at_the_max_scale_for_very_large_num_ctx() -> None:
    budget_at_cap = PromptBudgetAllocator(num_ctx=32768).allocate(_sparse_context())
    budget_beyond_cap = PromptBudgetAllocator(num_ctx=131072).allocate(_sparse_context())

    assert budget_beyond_cap == budget_at_cap
