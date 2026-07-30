from collections import defaultdict

from src.application.workflows.parsing.normalizers.docling_caption_extractor import (
    DoclingCaptionExtractor,
)
from src.application.workflows.parsing.normalizers.docling_element_metadata_builder import (
    DoclingElementMetadataBuilder,
)
from src.application.workflows.parsing.normalizers.docling_element_text_resolver import (
    DoclingElementTextResolver,
)
from src.application.workflows.parsing.normalizers.docling_item_extractor import (
    DoclingItemExtractor,
)
from src.application.workflows.parsing.normalizers.docling_layout_metadata_builder import (
    DoclingLayoutMetadataBuilder,
)
from src.application.workflows.parsing.normalizers.docling_provenance_extractor import (
    DoclingProvenanceExtractor,
)
from src.application.workflows.parsing.normalizers.table_rows.docling_table_extractor import (
    DoclingTableExtractor,
)
from src.application.workflows.parsing.normalizers.table_layout.text_grid.text_grid_table_fallback_applier import (
    TextGridTableFallbackApplier,
)
from src.application.workflows.parsing.parsed_canonical_element import ParsedCanonicalElement
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.shared.exceptions import DocumentNormalizationError


class DoclingDocumentNormalizer:
    def __init__(
        self,
        *,
        text_resolver: DoclingElementTextResolver | None = None,
        metadata_builder: DoclingElementMetadataBuilder | None = None,
        text_grid_table_fallback_applier: TextGridTableFallbackApplier | None = None,
    ) -> None:
        self.layout_metadata_builder = DoclingLayoutMetadataBuilder()
        self.table_extractor = DoclingTableExtractor()
        self.item_extractor = DoclingItemExtractor(self.table_extractor)
        self.provenance_extractor = DoclingProvenanceExtractor()
        self.text_resolver = text_resolver or DoclingElementTextResolver(
            self.table_extractor
        )
        self.metadata_builder = metadata_builder or DoclingElementMetadataBuilder(
            item_extractor=self.item_extractor,
            table_extractor=self.table_extractor,
        )
        self.text_grid_table_fallback_applier = (
            text_grid_table_fallback_applier or TextGridTableFallbackApplier()
        )

    def normalize(
        self,
        raw_parsed_document: RawParsedDocument,
        document_id: str,
        *,
        skipped_item_errors: list[str] | None = None,
    ) -> list[ParsedCanonicalElement]:
        try:
            raw_document = raw_parsed_document.raw_document
            items = list(self.item_extractor.iter_items(raw_document))
            normalized: list[ParsedCanonicalElement] = []
            errors = skipped_item_errors if skipped_item_errors is not None else []
            caption_extractor = DoclingCaptionExtractor(
                raw_document,
                items=items,
            )
            layout_metadata_by_element_ref = self.layout_metadata_builder.build(
                raw_document=raw_document,
                items=items,
                item_extractor=self.item_extractor,
                provenance_extractor=self.provenance_extractor,
            )

            for index, item in enumerate(
                items,
                start=1,
            ):
                try:
                    if self.item_extractor.should_skip(item):
                        continue

                    element = self._build_canonical_element(
                        item=item,
                        index=index,
                        document_id=document_id,
                        raw_document=raw_document,
                        caption_extractor=caption_extractor,
                        layout_metadata_by_element_ref=layout_metadata_by_element_ref,
                    )
                except Exception as exc:  # one bad item must not sink the document
                    errors.append(f"item {index}: {exc}")
                    continue

                normalized.append(element)

            if errors and not normalized:
                raise DocumentNormalizationError(
                    "Docling normalization produced zero usable elements.",
                    details={"item_count": len(items), "errors": errors[:10]},
                )

            reordered = self._apply_multi_column_reading_order(normalized)
            return self.text_grid_table_fallback_applier.apply(reordered)
        except DocumentNormalizationError:
            raise
        except Exception as exc:
            raise DocumentNormalizationError(
                "Failed to normalize Docling document.",
                details={
                    "file_path": raw_parsed_document.file_path,
                    "parser_name": raw_parsed_document.parser_name,
                },
            ) from exc

    def _build_canonical_element(
        self,
        *,
        item,
        index: int,
        document_id: str,
        raw_document,
        caption_extractor: DoclingCaptionExtractor,
        layout_metadata_by_element_ref: dict[str, dict[str, object]],
    ) -> ParsedCanonicalElement:
        element_type = self.item_extractor.extract_element_type(item)
        raw_ref = self.item_extractor.extract_raw_ref(item)
        element_layout_metadata = layout_metadata_by_element_ref.get(
            raw_ref or f"canon_{index}"
        )
        table_markdown = self.text_resolver.extract_table_markdown(
            item,
            element_type,
            raw_document=raw_document,
        )
        table_structure = self.text_resolver.extract_table_structure(
            item,
            element_type,
            page_lane_count=self._extract_page_lane_count(
                element_layout_metadata
            ),
        )
        caption = self.text_resolver.extract_caption_text(
            item,
            caption_extractor,
        )
        text = self.text_resolver.extract_text(
            item,
            element_type,
            caption=caption,
            table_markdown=table_markdown,
        )
        page_start, page_end = self.provenance_extractor.extract_pages(item)
        bbox = self.provenance_extractor.extract_bbox(item)
        section_path = self.item_extractor.extract_section_path(item)
        section_title = self.text_resolver.extract_section_title(
            element_type, text
        )
        metadata = self.metadata_builder.build(
            item,
            raw_ref=raw_ref,
            element_type=element_type,
            caption=caption,
            layout_metadata=element_layout_metadata,
            markdown=table_markdown,
            table_structure=table_structure,
        )

        return ParsedCanonicalElement(
            element_id=raw_ref or f"canon_{index}",
            document_id=document_id,
            element_type=element_type,
            text=text,
            page_start=page_start,
            page_end=page_end,
            bbox=bbox,
            order_index=index,
            section_title=section_title,
            section_path=section_path,
            raw_ref=raw_ref,
            metadata=metadata,
        )

    @staticmethod
    def _apply_multi_column_reading_order(
        elements: list[ParsedCanonicalElement],
    ) -> list[ParsedCanonicalElement]:
        """Re-sequences same-page elements into layout-resolved reading
        order (left lane fully before right lane) wherever the page layout
        analyzer detected genuine multi-column content. Docling's native
        item order does not follow column boundaries, so on a two-column
        page it can interleave left/right text roughly by paint position.
        Single-column pages -- the overwhelming majority -- are left
        byte-for-byte in their original order: a page is only touched here
        if at least one of its elements carries layout_lane_count > 1.
        """
        positions_by_page: dict[int, list[int]] = defaultdict(list)
        for position, element in enumerate(elements):
            if element.page_start is not None:
                positions_by_page[element.page_start].append(position)

        reordered = list(elements)
        for positions in positions_by_page.values():
            if len(positions) < 2:
                continue
            entries = [(position, elements[position]) for position in positions]
            if not any(
                (entry_element.metadata.get("layout_lane_count") or 1) > 1
                for _, entry_element in entries
            ):
                continue
            entries.sort(key=DoclingDocumentNormalizer._reading_order_sort_key)
            for position, (_, element) in zip(positions, entries):
                reordered[position] = element

        for index, element in enumerate(reordered, start=1):
            element.order_index = index
        return reordered

    @staticmethod
    def _reading_order_sort_key(entry: tuple[int, ParsedCanonicalElement]) -> int:
        position, element = entry
        layout_page_order = element.metadata.get("layout_page_order")
        return int(layout_page_order) if layout_page_order is not None else position

    @staticmethod
    def _extract_page_lane_count(
        element_layout_metadata: dict[str, object] | None,
    ) -> int | None:
        if element_layout_metadata is None:
            return None
        value = element_layout_metadata.get("layout_lane_count")
        return value if isinstance(value, int) else None
