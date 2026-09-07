from src.application.workflows.parsing.builders.chunking.builders.fragment.table_chunk_eligibility_policy import (
    TableChunkEligibilityPolicy,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import ElementType, ParserMetadata, SourceLocation
from src.domain.elements import CanonicalElement


def make_table_element(
    *,
    text: str = "| Part | Description |\n|---|---|\n| HP-001 | Filter |",
    markdown: str | None = None,
    column_count: int | None = 2,
    row_count: int | None = 2,
    metadata: dict | None = None,
) -> CanonicalElement:
    extra: dict = {}
    if markdown is not None:
        extra["markdown"] = markdown
    if column_count is not None:
        extra["column_count"] = column_count
    if row_count is not None:
        extra["row_count"] = row_count
    if metadata:
        extra.update(metadata)

    return CanonicalElement(
        element_id="tbl_1",
        document_id="doc_001",
        element_type=ElementType.TABLE,
        text=text,
        table_id="table_001",
        source=SourceLocation(page_start=1, page_end=1),
        parser_metadata=ParserMetadata(parser_name="docling", extra=extra) if extra else None,
    )


def make_policy(*, max_chunk_tokens: int = 200) -> TableChunkEligibilityPolicy:
    return TableChunkEligibilityPolicy(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=max_chunk_tokens, chunk_overlap=20),
    )


def test_multi_row_multi_column_table_is_eligible() -> None:
    policy = make_policy()
    element = make_table_element(column_count=2, row_count=2)

    assert policy.should_chunk(element) is True


def test_single_column_table_is_never_eligible() -> None:
    # A single-column "table" carries no tabular structure worth chunking
    # as a table on its own -- regardless of row count or content length.
    policy = make_policy()
    element = make_table_element(column_count=1, row_count=5)

    assert policy.should_chunk(element) is False


def test_single_row_table_with_long_markdown_is_not_eligible() -> None:
    # A header-only table (row_count<=1, i.e. no body rows) whose markdown
    # still runs long is more likely leftover layout noise than a real
    # table worth its own chunk.
    policy = make_policy()
    long_markdown = "| " + " | ".join(f"Column {i}" for i in range(40)) + " |"
    element = make_table_element(column_count=3, row_count=1, markdown=long_markdown)

    assert policy.should_chunk(element) is False


def test_single_row_table_with_short_markdown_is_eligible() -> None:
    # A short header-only table row is still worth keeping -- the veto is
    # specifically for long, noisy single-row content.
    policy = make_policy()
    element = make_table_element(column_count=3, row_count=1, markdown="| A | B | C |")

    assert policy.should_chunk(element) is True


def test_missing_row_count_skips_the_single_row_check() -> None:
    # No row_count metadata at all means the row-based veto can't apply --
    # falls through to eligible.
    policy = make_policy()
    element = make_table_element(column_count=2, row_count=None)

    assert policy.should_chunk(element) is True


def test_missing_column_count_skips_the_single_column_check() -> None:
    policy = make_policy()
    element = make_table_element(column_count=None, row_count=2)

    assert policy.should_chunk(element) is True


def test_zero_row_count_does_not_coerce_to_a_positive_int_and_is_treated_as_missing() -> (
    None
):
    # coerce_positive_int() maps non-positive values to None, so row_count=0
    # behaves the same as row_count being absent -- it does not trigger the
    # single-row veto even with long markdown.
    policy = make_policy()
    long_markdown = "| " + " | ".join(f"Column {i}" for i in range(40)) + " |"
    element = make_table_element(column_count=3, row_count=0, markdown=long_markdown)

    assert policy.should_chunk(element) is True


def test_falls_back_to_element_text_when_markdown_metadata_is_absent() -> None:
    # markdown is not provided in parser_extra -- the eligibility check
    # falls back to element.text for the long-single-row-content veto.
    policy = make_policy()
    long_text = " ".join(f"word{i}" for i in range(40))
    element = make_table_element(column_count=3, row_count=1, markdown=None, text=long_text)

    assert policy.should_chunk(element) is False
