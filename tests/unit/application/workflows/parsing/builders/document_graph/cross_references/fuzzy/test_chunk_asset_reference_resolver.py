from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_asset_number_index import (
    ChunkAssetNumberIndex,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_asset_reference_resolver import (
    ChunkAssetReferenceResolver,
)
from src.domain.assets import TableAsset
from src.domain.assets.asset_metadata import AssetMetadata
from src.domain.common import ChunkType, SourceLocation
from src.domain.document.entities import ChunkCrossReferenceResolutionStatus
from src.domain.document.entities.chunk import DocumentChunk


def make_chunk(
    *,
    chunk_id: str,
    table_ids: list[str] | None = None,
    chunk_type: ChunkType = ChunkType.GENERAL,
    sequence_number: int = 1,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        content="content",
        chunk_type=chunk_type,
        source=SourceLocation(page_start=1, page_end=1),
        table_ids=table_ids or [],
        sequence_number=sequence_number,
    )


def make_table(*, table_id: str, caption: str | None) -> TableAsset:
    return TableAsset(
        table_id=table_id,
        document_id="doc_001",
        markdown="| a | b |",
        metadata=AssetMetadata(caption=caption),
    )


def _resolver() -> ChunkAssetReferenceResolver:
    return ChunkAssetReferenceResolver()


def test_resolves_uniquely_when_exactly_one_chunk_contains_the_table() -> None:
    table = make_table(table_id="table_1", caption="Table 3. Spare parts list")
    chunk = make_chunk(chunk_id="a", table_ids=["table_1"])
    index = ChunkAssetNumberIndex(chunks=[chunk], tables={"table_1": table}, pictures={})

    result = _resolver().resolve_table(target_label="3", index=index)

    assert result.target_chunk_id == "a"
    assert result.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE
    assert result.confidence_score == 0.75


def test_returns_unresolved_when_no_asset_is_captioned_with_that_number() -> None:
    table = make_table(table_id="table_1", caption="Table 3. Spare parts list")
    chunk = make_chunk(chunk_id="a", table_ids=["table_1"])
    index = ChunkAssetNumberIndex(chunks=[chunk], tables={"table_1": table}, pictures={})

    result = _resolver().resolve_table(target_label="9", index=index)

    assert result.target_chunk_id is None
    assert result.resolution_status == ChunkCrossReferenceResolutionStatus.UNRESOLVED
    assert result.confidence_score == 0.0


def test_returns_unresolved_when_document_never_captions_tables_with_numbers() -> None:
    # Expected, non-error outcome per the module docstring: a document that
    # doesn't number its tables/figures at all simply produces no matches.
    table = make_table(table_id="table_1", caption="Spare parts list")
    chunk = make_chunk(chunk_id="a", table_ids=["table_1"])
    index = ChunkAssetNumberIndex(chunks=[chunk], tables={"table_1": table}, pictures={})

    result = _resolver().resolve_table(target_label="3", index=index)

    assert result.resolution_status == ChunkCrossReferenceResolutionStatus.UNRESOLVED


def test_falls_back_to_nearest_table_on_adjacent_page_when_uncaptioned() -> None:
    # No caption number matches "3" at all (the table has no caption), but
    # the source_page is adjacent to the table's page, so this should still
    # resolve as a low-confidence proximity guess rather than UNRESOLVED.
    table = make_table(table_id="table_1", caption=None)
    chunk = make_chunk(chunk_id="a", table_ids=["table_1"])
    index = ChunkAssetNumberIndex(chunks=[chunk], tables={"table_1": table}, pictures={})

    result = _resolver().resolve_table(target_label="3", index=index, source_page=1)

    assert result.target_chunk_id == "a"
    assert result.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS
    assert result.confidence_score == 0.3


def test_proximity_fallback_does_not_trigger_without_a_source_page() -> None:
    table = make_table(table_id="table_1", caption=None)
    chunk = make_chunk(chunk_id="a", table_ids=["table_1"])
    index = ChunkAssetNumberIndex(chunks=[chunk], tables={"table_1": table}, pictures={})

    result = _resolver().resolve_table(target_label="3", index=index)

    assert result.resolution_status == ChunkCrossReferenceResolutionStatus.UNRESOLVED


def test_proximity_fallback_does_not_trigger_beyond_the_page_window() -> None:
    table = make_table(table_id="table_1", caption=None)
    chunk = DocumentChunk(
        chunk_id="a",
        document_id="doc_001",
        section_id=None,
        content="content",
        source=SourceLocation(page_start=10, page_end=10),
        table_ids=["table_1"],
    )
    index = ChunkAssetNumberIndex(chunks=[chunk], tables={"table_1": table}, pictures={})

    result = _resolver().resolve_table(target_label="3", index=index, source_page=1)

    assert result.resolution_status == ChunkCrossReferenceResolutionStatus.UNRESOLVED


def test_prefers_procedure_like_chunk_when_multiple_chunks_share_the_table_number() -> (
    None
):
    table_one = make_table(table_id="table_1", caption="Table 3. Overview list")
    table_two = make_table(table_id="table_2", caption="Table 3. Repeated in appendix")
    overview = make_chunk(
        chunk_id="overview",
        table_ids=["table_1"],
        chunk_type=ChunkType.OVERVIEW,
        sequence_number=1,
    )
    procedure = make_chunk(
        chunk_id="procedure",
        table_ids=["table_2"],
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
        sequence_number=2,
    )
    index = ChunkAssetNumberIndex(
        chunks=[overview, procedure],
        tables={"table_1": table_one, "table_2": table_two},
        pictures={},
    )

    result = _resolver().resolve_table(target_label="3", index=index)

    assert result.target_chunk_id == "procedure"
    assert (
        result.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS
    )
    assert result.confidence_score == 0.5
