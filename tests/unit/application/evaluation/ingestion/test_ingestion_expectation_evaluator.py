from pathlib import Path

from src.application.evaluation import (
    ExpectedCrossReference,
    IngestionExpectationCase,
    IngestionExpectationEvaluator,
)
from src.domain.assets import TableAsset
from src.domain.assets.asset_metadata import AssetMetadata
from src.domain.assets.picture_asset import PictureAsset
from src.domain.common import ChunkType, DocumentType, SourceLocation
from src.domain.document.aggregates.document_graph import DocumentGraph
from src.domain.document.entities.chunk import DocumentChunk
from src.domain.document.entities.chunk_cross_reference import (
    ChunkCrossReference,
    ChunkCrossReferenceType,
)
from src.domain.document.entities.document import Document
from src.domain.document.entities.section import DocumentSection
from src.domain.document.value_objects import DocumentHashes


def make_case(**overrides) -> IngestionExpectationCase:
    defaults = dict(
        case_id="struct_001",
        document_path=Path("TestDoc/fixtures/sample.pdf"),
    )
    defaults.update(overrides)
    return IngestionExpectationCase(**defaults)


def make_graph(
    *,
    sections: dict[str, DocumentSection] | None = None,
    chunks: dict[str, DocumentChunk] | None = None,
    tables: dict[str, TableAsset] | None = None,
    pictures: dict[str, PictureAsset] | None = None,
    cross_references: dict[str, ChunkCrossReference] | None = None,
) -> DocumentGraph:
    document = Document(
        document_id="doc_001",
        file_name="sample.pdf",
        file_path="TestDoc/fixtures/sample.pdf",
        hashes=DocumentHashes(file_hash="h1", content_hash="c1"),
        document_type=DocumentType.MANUAL,
    )
    graph = DocumentGraph(document=document)
    graph.sections = sections or {}
    graph.chunks = chunks or {}
    graph.tables = tables or {}
    graph.pictures = pictures or {}
    graph.cross_references = cross_references or {}
    return graph


def make_section(*, section_id: str, title: str, parent_section_id: str | None) -> DocumentSection:
    return DocumentSection(
        section_id=section_id,
        document_id="doc_001",
        title=title,
        parent_section_id=parent_section_id,
    )


def make_chunk(*, chunk_id: str, chunk_type: ChunkType) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        chunk_type=chunk_type,
        content="content",
        source=SourceLocation(page_start=1, page_end=1),
        sequence_number=1,
    )


def _evaluator() -> IngestionExpectationEvaluator:
    return IngestionExpectationEvaluator()


def test_section_count_assertion_passes_and_fails_correctly() -> None:
    graph = make_graph(
        sections={
            "s1": make_section(section_id="s1", title="Cover", parent_section_id=None),
            "s2": make_section(section_id="s2", title="1 General", parent_section_id=None),
        }
    )

    passing_result = _evaluator().evaluate(
        case=make_case(expected_section_count=2), document_graph=graph
    )
    failing_result = _evaluator().evaluate(
        case=make_case(expected_section_count=5), document_graph=graph
    )

    assert passing_result.passed is True
    assert failing_result.passed is False
    assert failing_result.failed_assertions[0].name == "section_count"
    assert failing_result.failed_assertions[0].expected == 5
    assert failing_result.failed_assertions[0].actual == 2


def test_top_level_section_titles_assertion_ignores_nested_sections() -> None:
    graph = make_graph(
        sections={
            "s1": make_section(section_id="s1", title="Cover", parent_section_id=None),
            "s2": make_section(section_id="s2", title="1 General", parent_section_id=None),
            "s3": make_section(section_id="s3", title="1.1 Nested", parent_section_id="s2"),
        }
    )

    result = _evaluator().evaluate(
        case=make_case(
            expected_top_level_section_titles=("Cover", "1 General")
        ),
        document_graph=graph,
    )

    assert result.passed is True


def test_chunk_count_and_chunk_type_counts_assertions() -> None:
    graph = make_graph(
        chunks={
            "c1": make_chunk(chunk_id="c1", chunk_type=ChunkType.GENERAL),
            "c2": make_chunk(chunk_id="c2", chunk_type=ChunkType.GENERAL),
            "c3": make_chunk(chunk_id="c3", chunk_type=ChunkType.SAFETY_WARNING),
        }
    )

    result = _evaluator().evaluate(
        case=make_case(
            expected_chunk_count=3,
            expected_chunk_type_counts={"general": 2, "safety_warning": 1},
        ),
        document_graph=graph,
    )

    assert result.passed is True

    wrong_result = _evaluator().evaluate(
        case=make_case(expected_chunk_type_counts={"safety_warning": 5}),
        document_graph=graph,
    )
    assert wrong_result.passed is False
    assert wrong_result.assertions[0].name == "chunk_type_count[safety_warning]"
    assert wrong_result.assertions[0].actual == 1


def test_table_and_picture_count_assertions() -> None:
    graph = make_graph(
        tables={
            "t1": TableAsset(table_id="t1", document_id="doc_001", markdown="| a |"),
        },
        pictures={
            "p1": PictureAsset(picture_id="p1", document_id="doc_001"),
            "p2": PictureAsset(picture_id="p2", document_id="doc_001"),
        },
    )

    result = _evaluator().evaluate(
        case=make_case(expected_table_count=1, expected_picture_count=2),
        document_graph=graph,
    )

    assert result.passed is True


def test_cross_reference_present_assertion_matches_by_clue_type_and_target() -> None:
    graph = make_graph(
        cross_references={
            "xref_1": ChunkCrossReference(
                cross_reference_id="xref_1",
                document_id="doc_001",
                source_chunk_id="c1",
                reference_type=ChunkCrossReferenceType.SECTION_REFERENCE,
                matched_text="See Section 8",
                target_section_label="8",
            ),
        }
    )

    result = _evaluator().evaluate(
        case=make_case(
            expected_cross_references=(
                ExpectedCrossReference(
                    clue="See Section 8",
                    expected_reference_type="section_reference",
                    expected_target_section="8",
                ),
            )
        ),
        document_graph=graph,
    )

    assert result.passed is True


def test_cross_reference_present_assertion_matches_annex_target() -> None:
    graph = make_graph(
        cross_references={
            "xref_1": ChunkCrossReference(
                cross_reference_id="xref_1",
                document_id="doc_001",
                source_chunk_id="c1",
                reference_type=ChunkCrossReferenceType.ANNEX_REFERENCE,
                matched_text="Refer to Annex 2",
                target_annex_label="2",
            ),
        }
    )

    result = _evaluator().evaluate(
        case=make_case(
            expected_cross_references=(
                ExpectedCrossReference(
                    clue="Refer to Annex 2",
                    expected_reference_type="annex_reference",
                    expected_target_annex="2",
                ),
            )
        ),
        document_graph=graph,
    )

    assert result.passed is True


def test_cross_reference_present_assertion_fails_when_missing() -> None:
    graph = make_graph(cross_references={})

    result = _evaluator().evaluate(
        case=make_case(
            expected_cross_references=(
                ExpectedCrossReference(
                    clue="With reference to section 9.4",
                    expected_reference_type="section_reference",
                    expected_target_section="9.4",
                ),
            )
        ),
        document_graph=graph,
    )

    assert result.passed is False
    assert "cross_reference_present" in result.failed_assertions[0].name


def test_cross_reference_absent_assertion_passes_when_nothing_produced() -> None:
    # The external-directive case: this clue must NOT resolve internally.
    graph = make_graph(cross_references={})

    result = _evaluator().evaluate(
        case=make_case(
            expected_cross_references=(
                ExpectedCrossReference(clue="Annex I, Section 1.2"),
            )
        ),
        document_graph=graph,
    )

    assert result.passed is True


def test_cross_reference_absent_assertion_fails_when_something_was_produced() -> None:
    graph = make_graph(
        cross_references={
            "xref_1": ChunkCrossReference(
                cross_reference_id="xref_1",
                document_id="doc_001",
                source_chunk_id="c1",
                reference_type=ChunkCrossReferenceType.SECTION_REFERENCE,
                matched_text="Annex I, Section 1.2",
                target_section_label="1.2",
            ),
        }
    )

    result = _evaluator().evaluate(
        case=make_case(
            expected_cross_references=(
                ExpectedCrossReference(clue="Annex I, Section 1.2"),
            )
        ),
        document_graph=graph,
    )

    assert result.passed is False


def test_unset_expected_fields_produce_no_assertions() -> None:
    graph = make_graph()

    result = _evaluator().evaluate(case=make_case(), document_graph=graph)

    assert result.assertions == []
    assert result.passed is True
