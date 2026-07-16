from collections.abc import Sequence

from src.application.workflows.parsing.layout.models.page_layout_analysis import (
    PageLayoutAnalysis,
)


class LayoutMetadataSerializer:
    VERSION = "1"

    def serialize(
        self,
        analyses: Sequence[PageLayoutAnalysis],
    ) -> dict[str, dict[str, object]]:
        serialized: dict[str, dict[str, object]] = {}
        for analysis in analyses:
            page_order = 0
            for region in analysis.regions:
                for element_ref in region.element_refs:
                    page_order += 1
                    payload: dict[str, object] = {
                        "page_width": analysis.page_width,
                        "page_height": analysis.page_height,
                        "page_orientation": analysis.orientation,
                        "layout_region_id": region.region_id,
                        "layout_region_role": region.role.value,
                        "layout_lane_count": region.lane_count,
                        "layout_reading_order": region.reading_order_by_element_ref.get(
                            element_ref
                        ),
                        # Flattened, page-global position across all regions in
                        # their already-resolved traversal order (regions sorted
                        # by top_y/rank, elements sorted within each region) --
                        # unlike layout_reading_order (local to one region), this
                        # is directly comparable across lanes on the same page.
                        "layout_page_order": page_order,
                        "layout_model_version": self.VERSION,
                    }
                    if analysis.is_front_matter:
                        payload["layout_is_front_matter"] = True
                    if region.lane_index is not None:
                        payload["layout_lane_index"] = region.lane_index + 1
                    if region.bbox is not None:
                        payload["layout_region_bbox"] = {
                            "x1": region.bbox.x1,
                            "y1": region.bbox.y1,
                            "x2": region.bbox.x2,
                            "y2": region.bbox.y2,
                        }
                    serialized[element_ref] = payload
        return serialized
