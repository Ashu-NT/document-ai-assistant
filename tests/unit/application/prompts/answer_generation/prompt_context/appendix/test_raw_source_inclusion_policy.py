from src.application.prompts.answer_generation.prompt_context.appendix import (
    RawSourceInclusionPolicy,
)
from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
    PromptSourceFamilyView,
    PromptSourceView,
    PromptTableRowView,
    PromptTableView,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerKeyValue,
)


def test_select_prefers_direct_then_supporting_sources() -> None:
    long_context = " ".join(["evidence"] * 120)
    context = PromptContextBundle(
        answer_intent_value="specification_summary",
        source_count=3,
        sources=[
            PromptSourceView(source_number=1, chunk_id="chunk_001", content=long_context),
            PromptSourceView(source_number=2, chunk_id="chunk_002", content=long_context),
            PromptSourceView(source_number=3, chunk_id="chunk_003", content=long_context),
        ],
        appendix_sources=[
            PromptSourceView(source_number=1, chunk_id="chunk_001", content=long_context),
            PromptSourceView(source_number=2, chunk_id="chunk_002", content=long_context),
            PromptSourceView(source_number=3, chunk_id="chunk_003", content=long_context),
        ],
        source_families=[
            PromptSourceFamilyView(
                family_id="family_001",
                family_label="Specs",
                anchor_source_number=1,
                direct_source_numbers=[1],
                supporting_source_numbers=[2],
                contextual_source_numbers=[3],
            )
        ],
        key_values=[],
    )

    selected = RawSourceInclusionPolicy().select(context)

    assert [source.source_number for source in selected] == [1, 2, 3]
    assert selected[0].content.endswith("...")


def test_select_limits_rich_context_and_skips_contextual_tail() -> None:
    long_context = " ".join(["evidence"] * 120)
    context = PromptContextBundle(
        answer_intent_value="table_summary",
        source_count=3,
        sources=[
            PromptSourceView(source_number=1, chunk_id="chunk_001", content=long_context),
            PromptSourceView(source_number=2, chunk_id="chunk_002", content=long_context),
            PromptSourceView(source_number=3, chunk_id="chunk_003", content=long_context),
        ],
        appendix_sources=[
            PromptSourceView(source_number=1, chunk_id="chunk_001", content=long_context),
            PromptSourceView(source_number=2, chunk_id="chunk_002", content=long_context),
            PromptSourceView(source_number=3, chunk_id="chunk_003", content=long_context),
        ],
        source_families=[
            PromptSourceFamilyView(
                family_id="family_001",
                family_label="Specs",
                anchor_source_number=1,
                direct_source_numbers=[1],
                supporting_source_numbers=[2],
                contextual_source_numbers=[3],
                table_source_numbers=[1],
            )
        ],
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
        entities=[],
        relationship_edges=[],
        key_values=[
            AnswerKeyValue(key="A", value="1", unit=None, source_number=1),
            AnswerKeyValue(key="B", value="2", unit=None, source_number=1),
            AnswerKeyValue(key="C", value="3", unit=None, source_number=1),
            AnswerKeyValue(key="D", value="4", unit=None, source_number=1),
        ],
    )

    selected = RawSourceInclusionPolicy().select(context)

    assert [source.source_number for source in selected] == [1, 2]
    assert all(len(source.content) <= 353 for source in selected)


def test_select_prefers_higher_score_among_same_role_when_budget_is_tight() -> None:
    """Finding 2.1: PromptSourceView.score (real retrieval relevance) must
    actually influence which same-role sources win the scarce raw-prose
    budget slots, instead of being computed during projection and never
    read again."""
    long_context = " ".join(["evidence"] * 120)
    context = PromptContextBundle(
        answer_intent_value="table_summary",
        source_count=3,
        sources=[
            PromptSourceView(
                source_number=1, chunk_id="chunk_001", content=long_context, score=0.4
            ),
            PromptSourceView(
                source_number=2, chunk_id="chunk_002", content=long_context, score=0.9
            ),
            PromptSourceView(
                source_number=3, chunk_id="chunk_003", content=long_context, score=0.7
            ),
        ],
        appendix_sources=[
            PromptSourceView(
                source_number=1, chunk_id="chunk_001", content=long_context, score=0.4
            ),
            PromptSourceView(
                source_number=2, chunk_id="chunk_002", content=long_context, score=0.9
            ),
            PromptSourceView(
                source_number=3, chunk_id="chunk_003", content=long_context, score=0.7
            ),
        ],
        source_families=[
            PromptSourceFamilyView(
                family_id="family_001",
                family_label="Specs",
                anchor_source_number=1,
                direct_source_numbers=[1, 2, 3],
                supporting_source_numbers=[],
                contextual_source_numbers=[],
                table_source_numbers=[1],
            )
        ],
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
        entities=[],
        relationship_edges=[],
        key_values=[],
    )

    selected = RawSourceInclusionPolicy().select(context)

    # All 3 sources share the same "direct" role, so the tie is broken by
    # score alone; the table-heavy budget only fits 2, so the lowest-scored
    # source (source 1, score 0.4) must lose its slot to source 3 (0.7)
    # even though source 1 has the lowest source_number.
    assert [source.source_number for source in selected] == [2, 3]
