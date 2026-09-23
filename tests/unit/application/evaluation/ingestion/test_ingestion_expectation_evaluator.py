from pathlib import Path

from src.application.evaluation import (
    ExpectedCrossReference,
    IngestionExpectationCase,
    IngestionExpectationEvaluator,
)
from src.application.evaluation.ingestion.models.chunk_token_budget_result import (
    ChunkTokenBudgetStatus,
)
from src.domain.assets import TableAsset
from src.domain.assets.asset_metadata import AssetMetadata
from src.domain.assets.picture_asset import PictureAsset
from src.domain.common import ChunkType, DocumentType, ElementType, SourceLocation
from src.domain.document.aggregates.document_graph import DocumentGraph
from src.domain.document.entities.chunk import DocumentChunk
from src.domain.document.entities.chunk_cross_reference import (
    ChunkCrossReference,
    ChunkCrossReferenceType,
)
from src.domain.document.entities.cross_reference_reconciliation_outcome import (
    CrossReferenceReconciliationOutcome,
)
from src.domain.document.entities.document import Document
from src.domain.document.entities.section import DocumentSection
from src.domain.document.value_objects import DocumentHashes
from src.domain.elements.canonical_element import CanonicalElement
from src.application.workflows.parsing.builders.document_graph.document_metadata.document_type_signal_cache import (
    store_document_type_confirmed,
)


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
    elements: dict[str, CanonicalElement] | None = None,
    document_type: DocumentType = DocumentType.MANUAL,
    # Marks document_type as confirmed so the effective chunking profile is
    # reliably resolvable (via DOCUMENT_TYPE_CHUNKING_PROFILES) without
    # needing a real structural_profile_inference in every test fixture.
    # Pass False to exercise the "cannot be resolved" path.
    document_type_confirmed: bool = True,
) -> DocumentGraph:
    document = Document(
        document_id="doc_001",
        file_name="sample.pdf",
        file_path="TestDoc/fixtures/sample.pdf",
        hashes=DocumentHashes(file_hash="h1", content_hash="c1"),
        document_type=document_type,
    )
    store_document_type_confirmed(document.metadata, is_confirmed=document_type_confirmed)
    graph = DocumentGraph(document=document)
    graph.sections = sections or {}
    graph.chunks = chunks or {}
    graph.tables = tables or {}
    graph.pictures = pictures or {}
    graph.cross_references = cross_references or {}
    graph.elements = elements or {}
    return graph


def make_section(*, section_id: str, title: str, parent_section_id: str | None) -> DocumentSection:
    return DocumentSection(
        section_id=section_id,
        document_id="doc_001",
        title=title,
        parent_section_id=parent_section_id,
    )


def make_chunk(
    *,
    chunk_id: str,
    chunk_type: ChunkType = ChunkType.GENERAL,
    content: str = "content",
    source: SourceLocation | None = None,
    table_ids: list[str] | None = None,
    table_row_start: int | None = None,
    table_row_end: int | None = None,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        chunk_type=chunk_type,
        content=content,
        source=source if source is not None else SourceLocation(page_start=1, page_end=1),
        sequence_number=1,
        table_ids=table_ids or [],
        table_row_start=table_row_start,
        table_row_end=table_row_end,
    )


def make_element(
    *,
    element_id: str,
    text: str | None,
    source: SourceLocation | None = None,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TEXT,
        text=text,
        source=source if source is not None else SourceLocation(page_start=1, page_end=1),
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


def test_unset_expected_fields_produce_no_case_specific_assertions() -> None:
    # Universal structural/chunk invariants (no_empty_chunks, provenance,
    # token budget) always run regardless of case content -- only the
    # CASE-SPECIFIC assertions are gated on populated `expected_*` fields.
    graph = make_graph()

    result = _evaluator().evaluate(case=make_case(), document_graph=graph)

    assert {assertion.name for assertion in result.assertions} <= {
        "no_empty_chunks",
        "chunk_page_provenance_present",
        "element_page_provenance_present",
        "chunk_hard_token_budget",
    }
    assert result.passed is True


def _assertion(result, name: str):
    matches = [a for a in result.assertions if a.name == name]
    assert matches, f"no assertion named {name!r} in {[a.name for a in result.assertions]}"
    return matches[0]


class TestToleratedRangeAssertions:
    def test_element_count_range_passes_within_bounds(self) -> None:
        graph = make_graph(
            elements={"e1": make_element(element_id="e1", text="a"), "e2": make_element(element_id="e2", text="b")}
        )

        result = _evaluator().evaluate(
            case=make_case(expected_element_count_min=1, expected_element_count_max=5),
            document_graph=graph,
        )

        assert _assertion(result, "element_count_range").passed is True

    def test_chunk_count_range_fails_below_minimum(self) -> None:
        graph = make_graph(chunks={"c1": make_chunk(chunk_id="c1")})

        result = _evaluator().evaluate(
            case=make_case(expected_chunk_count_min=5),
            document_graph=graph,
        )

        assertion = _assertion(result, "chunk_count_range")
        assert assertion.passed is False
        assert assertion.actual == 1

    def test_table_and_picture_count_ranges_fail_above_maximum(self) -> None:
        graph = make_graph(
            tables={"t1": TableAsset(table_id="t1", document_id="doc_001", markdown="| a |")},
            pictures={
                "p1": PictureAsset(picture_id="p1", document_id="doc_001"),
                "p2": PictureAsset(picture_id="p2", document_id="doc_001"),
            },
        )

        result = _evaluator().evaluate(
            case=make_case(
                expected_table_count_max=0,
                expected_picture_count_max=1,
            ),
            document_graph=graph,
        )

        assert _assertion(result, "table_count_range").passed is False
        assert _assertion(result, "picture_count_range").passed is False


class TestRequiredTextClues:
    def test_required_text_clue_passes_when_present(self) -> None:
        graph = make_graph(
            elements={"e1": make_element(element_id="e1", text="Replace the oil filter every 500 hours.")}
        )

        result = _evaluator().evaluate(
            case=make_case(required_text_clues=("oil filter",)),
            document_graph=graph,
        )

        assert _assertion(result, "required_text_clue[oil filter]").passed is True

    def test_required_text_clue_fails_when_absent(self) -> None:
        graph = make_graph(elements={"e1": make_element(element_id="e1", text="unrelated content")})

        result = _evaluator().evaluate(
            case=make_case(required_text_clues=("torque specification",)),
            document_graph=graph,
        )

        assertion = _assertion(result, "required_text_clue[torque specification]")
        assert assertion.passed is False
        assert result.passed is False


class TestUniversalInvariants:
    def test_no_empty_chunks_invariant_fails_on_blank_chunk(self) -> None:
        graph = make_graph(
            chunks={
                "c1": make_chunk(chunk_id="c1", content="real content"),
                "c2": make_chunk(chunk_id="c2", content="   "),
            }
        )

        result = _evaluator().evaluate(case=make_case(), document_graph=graph)

        assertion = _assertion(result, "no_empty_chunks")
        assert assertion.passed is False
        assert assertion.actual == 1

    def test_chunk_provenance_invariant_fails_when_page_start_missing(self) -> None:
        graph = make_graph(
            chunks={"c1": make_chunk(chunk_id="c1", source=SourceLocation(page_start=None))}
        )

        result = _evaluator().evaluate(case=make_case(), document_graph=graph)

        assertion = _assertion(result, "chunk_page_provenance_present")
        assert assertion.passed is False
        assert assertion.actual == 1

    def test_element_provenance_invariant_fails_when_page_start_missing(self) -> None:
        graph = make_graph(
            elements={
                "e1": make_element(element_id="e1", text="a", source=SourceLocation(page_start=None))
            }
        )

        result = _evaluator().evaluate(case=make_case(), document_graph=graph)

        assertion = _assertion(result, "element_page_provenance_present")
        assert assertion.passed is False
        assert assertion.actual == 1

    def _certificate_budget(self) -> int:
        from src.application.workflows.parsing.builders.chunking.policies.policy.chunking_policy_registry import (
            default_registry,
        )
        from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
            ChunkingProfile,
        )

        return default_registry().get(ChunkingProfile.CERTIFICATE).max_chunk_tokens

    def _content_over_budget(self, budget: int) -> str:
        from src.application.workflows.parsing.builders.chunking.text.tokenization.chunk_token_counter_factory import (
            ChunkTokenCounterFactory,
        )

        counter = ChunkTokenCounterFactory().create()
        words = ["word"]
        while counter.count_tokens(" ".join(words)) <= budget:
            words.append("word")
        return " ".join(words)

    def test_a_ordinary_chunk_below_effective_budget_passes(self) -> None:
        budget = self._certificate_budget()
        graph = make_graph(
            document_type=DocumentType.CERTIFICATE,
            chunks={"c1": make_chunk(chunk_id="c1", content="short content")},
        )

        result = _evaluator().evaluate_chunk_token_budget(graph)

        assert result.resolved is True
        assert result.profile == "certificate"
        assert result.effective_budget == budget
        assert result.normal_count == 1
        assert result.oversized_indivisible_count == 0
        assert result.hard_budget_violation_count == 0
        assert result.passed is True

    def test_b_non_table_chunk_above_effective_budget_is_hard_violation(self) -> None:
        budget = self._certificate_budget()
        content = self._content_over_budget(budget)
        graph = make_graph(
            document_type=DocumentType.CERTIFICATE,
            chunks={"c1": make_chunk(chunk_id="c1", content=content)},
        )

        result = _evaluator().evaluate_chunk_token_budget(graph)

        assert result.hard_budget_violation_count == 1
        assert result.oversized_indivisible_count == 0
        assert result.passed is False
        diagnostic = result.oversized_chunks[0]
        assert diagnostic.status == ChunkTokenBudgetStatus.HARD_BUDGET_VIOLATION
        assert diagnostic.chunk_id == "c1"

    def test_c_multi_row_table_fragment_above_budget_is_hard_violation(self) -> None:
        # A multi-row group (table_row_start != table_row_end) still over
        # budget means production's own row-accumulation guard did not keep
        # it in bounds -- NOT proof of minimum granularity, since the
        # splitter could in principle have produced smaller (e.g. single-
        # row) groups instead.
        budget = self._certificate_budget()
        content = self._content_over_budget(budget)
        graph = make_graph(
            document_type=DocumentType.CERTIFICATE,
            chunks={
                "c1": make_chunk(
                    chunk_id="c1",
                    content=content,
                    table_ids=["t1"],
                    table_row_start=1,
                    table_row_end=3,
                )
            },
        )

        result = _evaluator().evaluate_chunk_token_budget(graph)

        assert result.hard_budget_violation_count == 1
        assert result.oversized_indivisible_count == 0
        diagnostic = result.oversized_chunks[0]
        assert diagnostic.status == ChunkTokenBudgetStatus.HARD_BUDGET_VIOLATION
        assert diagnostic.table_id == "t1"
        assert diagnostic.table_row_start == 1
        assert diagnostic.table_row_end == 3

    def test_d_single_row_table_fragment_above_budget_is_oversized_indivisible(self) -> None:
        # table_row_start == table_row_end: this fragment IS the minimum
        # granularity TableFragmentSplitter can ever produce (it only ever
        # splits at row boundaries) - proof, not assumption.
        budget = self._certificate_budget()
        content = self._content_over_budget(budget)
        graph = make_graph(
            document_type=DocumentType.CERTIFICATE,
            chunks={
                "c1": make_chunk(
                    chunk_id="c1",
                    content=content,
                    table_ids=["t1"],
                    table_row_start=5,
                    table_row_end=5,
                )
            },
        )

        result = _evaluator().evaluate_chunk_token_budget(graph)

        assert result.hard_budget_violation_count == 0
        assert result.oversized_indivisible_count == 1
        # Oversized-indivisible findings remain visible and do NOT fail the
        # invariant - only hard_budget_violation_count gates pass/fail.
        assert result.passed is True
        diagnostic = result.oversized_chunks[0]
        assert diagnostic.status == ChunkTokenBudgetStatus.OVERSIZED_INDIVISIBLE
        assert diagnostic.table_id == "t1"
        assert diagnostic.table_row_start == 5
        assert diagnostic.table_row_end == 5

    def test_d_bare_table_id_alone_does_not_imply_indivisible(self) -> None:
        # A table_id without row-range metadata proving single-row
        # granularity must NOT be classified as indivisible merely for
        # carrying a table_id.
        budget = self._certificate_budget()
        content = self._content_over_budget(budget)
        graph = make_graph(
            document_type=DocumentType.CERTIFICATE,
            chunks={
                "c1": make_chunk(
                    chunk_id="c1",
                    content=content,
                    table_ids=["t1"],
                    table_row_start=None,
                    table_row_end=None,
                )
            },
        )

        result = _evaluator().evaluate_chunk_token_budget(graph)

        assert result.hard_budget_violation_count == 1
        assert result.oversized_indivisible_count == 0

    def test_e_uses_effective_profile_budget_not_max_across_profiles(self) -> None:
        from src.application.workflows.parsing.builders.chunking.policies.policy.chunking_policy_registry import (
            default_registry,
        )
        from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
            ChunkingProfile,
        )
        from src.application.workflows.parsing.builders.chunking.text.tokenization.chunk_token_counter_factory import (
            ChunkTokenCounterFactory,
        )

        certificate_budget = default_registry().get(ChunkingProfile.CERTIFICATE).max_chunk_tokens
        manual_budget = default_registry().get(ChunkingProfile.MANUAL).max_chunk_tokens
        assert certificate_budget < manual_budget, "profiles must genuinely differ for this test to be meaningful"

        counter = ChunkTokenCounterFactory().create()
        words = ["word"]
        while counter.count_tokens(" ".join(words)) <= certificate_budget:
            words.append("word")
        content = " ".join(words)
        assert counter.count_tokens(content) <= manual_budget, (
            "content must stay under the LARGER profile's budget so this "
            "test actually proves the smaller, effective one is enforced"
        )

        graph = make_graph(
            document_type=DocumentType.CERTIFICATE,
            chunks={"c1": make_chunk(chunk_id="c1", content=content)},
        )

        result = _evaluator().evaluate_chunk_token_budget(graph)

        assert result.resolved is True
        assert result.profile == "certificate"
        assert result.effective_budget == certificate_budget
        assert result.hard_budget_violation_count == 1

    def test_f_unresolved_effective_profile_is_explicit_not_a_silent_pass(self) -> None:
        graph = make_graph(
            document_type=DocumentType.UNKNOWN,
            document_type_confirmed=False,
            chunks={"c1": make_chunk(chunk_id="c1", content="short content")},
        )

        result = _evaluator().evaluate_chunk_token_budget(graph)

        assert result.resolved is False
        assert result.unresolved_reason is not None
        assert result.effective_budget is None
        assert result.passed is False  # explicit non-pass, never a silent pass

        case_result = _evaluator().evaluate(case=make_case(), document_graph=graph)
        assertion = _assertion(case_result, "chunk_hard_token_budget")
        assert assertion.passed is False
        assert "unresolved" in str(assertion.actual)


class TestCrossReferenceEvaluation:
    def test_presence_only_type_computes_recall_but_not_precision(self) -> None:
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
                # An extra, unannotated actual reference of the same type --
                # must NOT count as a false positive under presence-only scope.
                "xref_2": ChunkCrossReference(
                    cross_reference_id="xref_2",
                    document_id="doc_001",
                    source_chunk_id="c2",
                    reference_type=ChunkCrossReferenceType.SECTION_REFERENCE,
                    matched_text="See Section 3",
                    target_section_label="3",
                ),
            }
        )
        case = make_case(
            expected_cross_references=(
                ExpectedCrossReference(
                    clue="See Section 8",
                    expected_reference_type="section_reference",
                    expected_target_section="8",
                ),
            )
        )

        result = _evaluator().evaluate_cross_references(case=case, document_graph=graph)

        assert len(result.type_metrics) == 1
        metrics = result.type_metrics[0]
        assert metrics.reference_type == "section_reference"
        assert metrics.exhaustive is False
        assert metrics.true_positives == 1
        assert metrics.false_negatives == 0
        assert metrics.false_positives is None
        assert metrics.precision is None
        assert metrics.recall == 1.0

    def test_exhaustive_type_computes_false_positives_and_precision(self) -> None:
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
                "xref_2": ChunkCrossReference(
                    cross_reference_id="xref_2",
                    document_id="doc_001",
                    source_chunk_id="c2",
                    reference_type=ChunkCrossReferenceType.ANNEX_REFERENCE,
                    matched_text="Refer to Annex 9",
                    target_annex_label="9",
                ),
            }
        )
        case = make_case(
            expected_cross_references=(
                ExpectedCrossReference(
                    clue="Refer to Annex 2",
                    expected_reference_type="annex_reference",
                    expected_target_annex="2",
                ),
            ),
            exhaustive_cross_reference_types=("annex_reference",),
        )

        result = _evaluator().evaluate_cross_references(case=case, document_graph=graph)

        metrics = result.type_metrics[0]
        assert metrics.exhaustive is True
        assert metrics.true_positives == 1
        assert metrics.false_negatives == 0
        assert metrics.false_positives == 1  # xref_2 is unexplained
        assert metrics.precision == 0.5
        assert metrics.recall == 1.0
        assert metrics.f1 is not None

    def test_missed_expected_reference_counts_as_false_negative(self) -> None:
        graph = make_graph(cross_references={})
        case = make_case(
            expected_cross_references=(
                ExpectedCrossReference(
                    clue="See Section 8",
                    expected_reference_type="section_reference",
                    expected_target_section="8",
                ),
            )
        )

        result = _evaluator().evaluate_cross_references(case=case, document_graph=graph)

        metrics = result.type_metrics[0]
        assert metrics.true_positives == 0
        assert metrics.false_negatives == 1
        assert metrics.recall == 0.0

    def test_per_reference_type_aggregation_keeps_types_separate(self) -> None:
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
                "xref_2": ChunkCrossReference(
                    cross_reference_id="xref_2",
                    document_id="doc_001",
                    source_chunk_id="c2",
                    reference_type=ChunkCrossReferenceType.ANNEX_REFERENCE,
                    matched_text="Refer to Annex 2",
                    target_annex_label="2",
                ),
            }
        )
        case = make_case(
            expected_cross_references=(
                ExpectedCrossReference(
                    clue="See Section 8",
                    expected_reference_type="section_reference",
                    expected_target_section="8",
                ),
                ExpectedCrossReference(
                    clue="Refer to Annex 2",
                    expected_reference_type="annex_reference",
                    expected_target_annex="2",
                ),
            )
        )

        result = _evaluator().evaluate_cross_references(case=case, document_graph=graph)

        types_seen = {m.reference_type for m in result.type_metrics}
        assert types_seen == {"section_reference", "annex_reference"}
        assert all(m.true_positives == 1 for m in result.type_metrics)

    def test_reconciliation_outcome_counts_are_reported(self) -> None:
        graph = make_graph(
            cross_references={
                "xref_1": ChunkCrossReference(
                    cross_reference_id="xref_1",
                    document_id="doc_001",
                    source_chunk_id="c1",
                    reference_type=ChunkCrossReferenceType.SECTION_REFERENCE,
                    matched_text="See Section 8",
                    target_section_label="8",
                    reconciliation_outcome=CrossReferenceReconciliationOutcome.SINGLE_SOURCE,
                ),
                "xref_2": ChunkCrossReference(
                    cross_reference_id="xref_2",
                    document_id="doc_001",
                    source_chunk_id="c2",
                    reference_type=ChunkCrossReferenceType.ANNEX_REFERENCE,
                    matched_text="Refer to Annex 2",
                    target_annex_label="2",
                    reconciliation_outcome=CrossReferenceReconciliationOutcome.CONFIRMED,
                ),
            }
        )

        result = _evaluator().evaluate_cross_references(case=make_case(), document_graph=graph)

        assert result.reconciliation_outcome_counts == {"single_source": 1, "confirmed": 1}

    def test_external_reference_clue_checks_are_tracked_separately_from_type_metrics(self) -> None:
        graph = make_graph(cross_references={})
        case = make_case(
            expected_cross_references=(
                ExpectedCrossReference(clue="Annex I, Section 1.2"),
            )
        )

        result = _evaluator().evaluate_cross_references(case=case, document_graph=graph)

        assert result.type_metrics == []
        assert result.external_reference_clues_correctly_unresolved == 1
        assert result.external_reference_clues_incorrectly_resolved == 0
