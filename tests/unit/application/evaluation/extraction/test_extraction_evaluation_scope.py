import pytest

from src.application.evaluation.extraction.extraction_evaluation_scope import (
    ExtractionEvaluationScope,
    ExtractionScopeType,
)


class TestWholeDocumentScope:
    def test_whole_document_contains_any_page(self) -> None:
        scope = ExtractionEvaluationScope.whole_document()
        assert scope.contains_page(1)
        assert scope.contains_page(9999)
        assert scope.contains_page(None)

    def test_whole_document_overlaps_any_pages(self) -> None:
        scope = ExtractionEvaluationScope.whole_document()
        assert scope.overlaps_pages(None, None)
        assert scope.overlaps_pages(5, 5)

    def test_whole_document_rejects_page_bounds(self) -> None:
        with pytest.raises(ValueError):
            ExtractionEvaluationScope(
                scope_type=ExtractionScopeType.WHOLE_DOCUMENT, page_start=1
            )


class TestPageRangeScope:
    def test_requires_both_bounds(self) -> None:
        with pytest.raises(ValueError):
            ExtractionEvaluationScope(
                scope_type=ExtractionScopeType.PAGE_RANGE, page_start=1
            )

    def test_rejects_inverted_range(self) -> None:
        with pytest.raises(ValueError):
            ExtractionEvaluationScope.page_range(10, 5)

    def test_rejects_zero_or_negative_page(self) -> None:
        with pytest.raises(ValueError):
            ExtractionEvaluationScope.page_range(0, 5)

    def test_contains_page_inclusive_boundaries(self) -> None:
        scope = ExtractionEvaluationScope.page_range(10, 12)
        assert scope.contains_page(10)
        assert scope.contains_page(11)
        assert scope.contains_page(12)
        assert not scope.contains_page(9)
        assert not scope.contains_page(13)
        assert not scope.contains_page(None)

    def test_overlaps_pages_true_when_ranges_intersect(self) -> None:
        scope = ExtractionEvaluationScope.page_range(10, 12)
        assert scope.overlaps_pages(11, 11)
        assert scope.overlaps_pages(12, 20)
        assert scope.overlaps_pages(1, 10)

    def test_overlaps_pages_false_when_disjoint(self) -> None:
        scope = ExtractionEvaluationScope.page_range(10, 12)
        assert not scope.overlaps_pages(13, 20)
        assert not scope.overlaps_pages(1, 9)

    def test_overlaps_pages_false_when_both_none(self) -> None:
        scope = ExtractionEvaluationScope.page_range(10, 12)
        assert not scope.overlaps_pages(None, None)

    def test_overlaps_pages_handles_single_sided_bound(self) -> None:
        scope = ExtractionEvaluationScope.page_range(10, 12)
        assert scope.overlaps_pages(11, None)
        assert scope.overlaps_pages(None, 11)

    def test_hashable_for_set_grouping(self) -> None:
        a = ExtractionEvaluationScope.page_range(10, 12)
        b = ExtractionEvaluationScope.page_range(10, 12)
        assert a == b
        assert len({a, b}) == 1
