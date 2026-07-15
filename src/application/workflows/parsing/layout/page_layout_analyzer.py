from collections import defaultdict
from typing import Any

from src.application.workflows.parsing.layout.front_matter_page_classifier import (
    FrontMatterPageClassifier,
)
from src.application.workflows.parsing.layout.layout_lane_detector import (
    LayoutLaneDetector,
)
from src.application.workflows.parsing.layout.layout_metadata_serializer import (
    LayoutMetadataSerializer,
)
from src.application.workflows.parsing.layout.layout_region_builder import (
    LayoutRegionBuilder,
)
from src.application.workflows.parsing.layout.models.page_layout_analysis import (
    PageLayoutAnalysis,
)
from src.application.workflows.parsing.layout.models.page_layout_candidate import (
    PageLayoutCandidate,
)
from src.application.workflows.parsing.layout.page_orientation_resolver import (
    PageOrientationResolver,
)


class PageLayoutAnalyzer:
    def __init__(
        self,
        *,
        front_matter_page_classifier: FrontMatterPageClassifier | None = None,
        lane_detector: LayoutLaneDetector | None = None,
        metadata_serializer: LayoutMetadataSerializer | None = None,
        orientation_resolver: PageOrientationResolver | None = None,
        region_builder: LayoutRegionBuilder | None = None,
    ) -> None:
        self.front_matter_page_classifier = (
            front_matter_page_classifier or FrontMatterPageClassifier()
        )
        self.lane_detector = lane_detector or LayoutLaneDetector()
        self.metadata_serializer = metadata_serializer or LayoutMetadataSerializer()
        self.orientation_resolver = orientation_resolver or PageOrientationResolver()
        self.region_builder = region_builder or LayoutRegionBuilder()

    def analyze(
        self,
        *,
        raw_document: Any,
        candidates: list[PageLayoutCandidate],
    ) -> list[PageLayoutAnalysis]:
        page_sizes = self._extract_page_sizes(raw_document)
        front_matter_pages = self.front_matter_page_classifier.classify(candidates)
        grouped: dict[int, list[PageLayoutCandidate]] = defaultdict(list)
        for candidate in candidates:
            grouped[candidate.page_number].append(candidate)

        analyses: list[PageLayoutAnalysis] = []
        for page_number in sorted(grouped):
            page_width, page_height = page_sizes.get(page_number, (None, None))
            page_candidates = grouped[page_number]
            lane_detection = self.lane_detector.detect(
                page_width=page_width,
                candidates=page_candidates,
            )
            analyses.append(
                PageLayoutAnalysis(
                    page_number=page_number,
                    page_width=page_width,
                    page_height=page_height,
                    orientation=self.orientation_resolver.resolve(
                        page_width=page_width,
                        page_height=page_height,
                    ),
                    is_front_matter=page_number in front_matter_pages,
                    regions=self.region_builder.build(
                        page_number=page_number,
                        page_width=page_width,
                        detection=lane_detection,
                        is_front_matter=page_number in front_matter_pages,
                        candidates=page_candidates,
                    ),
                )
            )
        return analyses

    def analyze_and_serialize(
        self,
        *,
        raw_document: Any,
        candidates: list[PageLayoutCandidate],
    ) -> dict[str, dict[str, object]]:
        analyses = self.analyze(
            raw_document=raw_document,
            candidates=candidates,
        )
        return self.metadata_serializer.serialize(analyses)

    @staticmethod
    def _extract_page_sizes(
        raw_document: Any,
    ) -> dict[int, tuple[float | None, float | None]]:
        pages = getattr(raw_document, "pages", None)
        if not pages:
            return {}

        page_sizes: dict[int, tuple[float | None, float | None]] = {}
        for page_no, page in pages.items():
            try:
                normalized_page_no = int(page_no)
            except (TypeError, ValueError):
                continue
            size = getattr(page, "size", None)
            width = getattr(size, "width", None)
            height = getattr(size, "height", None)
            try:
                page_sizes[normalized_page_no] = (
                    float(width) if width is not None else None,
                    float(height) if height is not None else None,
                )
            except (TypeError, ValueError):
                page_sizes[normalized_page_no] = (None, None)
        return page_sizes
