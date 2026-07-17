from src.application.workflows.parsing.builders.chunking.builders.fragment.table_fragment_splitter import (
    TableFragmentSplitter,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import ChunkType


def test_table_fragment_splitter_splits_large_table_by_row_groups() -> None:
    fragment = ChunkFragment(
        text="placeholder",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        standalone=True,
        token_count=200,
        table_context="Maintenance schedule",
        table_rows=[
            ["Task", "Interval"],
            ["Inspect filter assembly", "Monthly inspection required"],
            ["Replace hydraulic seals", "Quarterly service required"],
            ["Clean debris trap", "Weekly cleaning required"],
        ],
        logical_table_family_id="table_family_1",
    )
    splitter = TableFragmentSplitter(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=18, chunk_overlap=0)
    )

    split_fragments = splitter.split(fragment)

    assert len(split_fragments) >= 2
    assert [item.logical_table_family_index for item in split_fragments] == list(
        range(1, len(split_fragments) + 1)
    )
    assert all(item.logical_table_family_total == len(split_fragments) for item in split_fragments)
    assert split_fragments[0].table_row_start == 1
    assert split_fragments[-1].table_row_end == 3
    assert all(item.table_rows is not None for item in split_fragments)


def test_table_fragment_splitter_rerenders_text_when_all_rows_fit_in_one_group() -> None:
    # Regression guard for a real bug: when the row-based grouping loop
    # decides everything fits in a single group, the returned fragment must
    # be rebuilt from that group's actual rows -- not left with whatever
    # stale text/token_count the original (pre-split) fragment happened to
    # carry. A bloated original fragment.text (e.g. from un-normalized
    # whitespace in the raw parsed table) must not leak through untouched
    # just because the cleaned rows themselves are small enough to fit.
    stale_oversized_text = "X " * 100_000
    fragment = ChunkFragment(
        text=stale_oversized_text,
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        standalone=True,
        token_count=100_000,
        table_context=None,
        table_rows=[
            ["Header1", "Header2"],
            ["row1val", "small content"],
            ["row2val", "small content"],
        ],
    )
    splitter = TableFragmentSplitter(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=1000, chunk_overlap=100)
    )

    split_fragments = splitter.split(fragment)

    assert len(split_fragments) == 1
    result = split_fragments[0]
    assert result.text != stale_oversized_text
    assert result.token_count < 100
    assert "row1val" in result.text
    assert "row2val" in result.text
