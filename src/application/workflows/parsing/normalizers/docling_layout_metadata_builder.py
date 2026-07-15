from typing import Any

from src.application.workflows.parsing.layout.page_layout_analyzer import (
    PageLayoutAnalyzer,
)
from src.application.workflows.parsing.layout.models.page_layout_candidate import (
    PageLayoutCandidate,
)
from src.application.workflows.parsing.normalizers.docling_item_extractor import (
    DoclingItemExtractor,
)
from src.application.workflows.parsing.normalizers.docling_provenance_extractor import (
    DoclingProvenanceExtractor,
)
from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)


class DoclingLayoutMetadataBuilder:
    def __init__(
        self,
        *,
        layout_analyzer: PageLayoutAnalyzer | None = None,
    ) -> None:
        self.layout_analyzer = layout_analyzer or PageLayoutAnalyzer()

    def build(
        self,
        *,
        raw_document: Any,
        items: list[Any],
        item_extractor: DoclingItemExtractor,
        provenance_extractor: DoclingProvenanceExtractor,
    ) -> dict[str, dict[str, object]]:
        candidates: list[PageLayoutCandidate] = []
        for index, item in enumerate(items, start=1):
            if item_extractor.should_skip(item):
                continue
            page_start, page_end = provenance_extractor.extract_pages(item)
            page_number = page_start or page_end
            if page_number is None:
                continue
            element_ref = item_extractor.extract_raw_ref(item) or f"canon_{index}"
            candidates.append(
                PageLayoutCandidate(
                    element_ref=element_ref,
                    page_number=page_number,
                    bbox=provenance_extractor.extract_bbox(item),
                    label=item_extractor.lower_label(item),
                    text=self._candidate_text(item),
                    content_layer=item_extractor.extract_content_layer(item),
                )
            )

        return self.layout_analyzer.analyze_and_serialize(
            raw_document=raw_document,
            candidates=candidates,
        )

    @staticmethod
    def _candidate_text(item: Any) -> str | None:
        for attribute_name in ("text", "caption", "name", "markdown"):
            value = getattr(item, attribute_name, None)
            if value is None:
                continue
            text = repair_docling_text(str(value)).strip()
            if text:
                return text
        return None
