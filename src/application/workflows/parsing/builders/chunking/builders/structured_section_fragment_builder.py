from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.builders.structured_section_markers import (
    CERTIFICATE_STRUCTURED_MARKERS,
    DATASHEET_STRUCTURED_MARKERS,
    DRAWING_STRUCTURED_MARKERS,
    REPORT_STRUCTURED_MARKERS,
    SENSOR_LIST_STRUCTURED_MARKERS,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
)
from src.domain.common import ChunkType, DocumentType, ElementType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


@dataclass(slots=True, frozen=True)
class StructuredSectionWindowSpec:
    section_path: list[str]
    anchor_markers: tuple[str, ...]
    chunk_type: ChunkType = ChunkType.GENERAL
    radius_before: int = 0
    radius_after: int = 8
    min_tokens: int = 6
    combine_all_windows: bool = False


class StructuredSectionFragmentBuilder:
    def __init__(self, *, text_splitter: ChunkTextSplitter) -> None:
        self.text_splitter = text_splitter

    def build(
        self,
        *,
        document_title: str | None,
        document_type: DocumentType | None,
        section: DocumentSection,
        elements: list[CanonicalElement],
    ) -> tuple[list[ChunkFragment], set[str]]:
        ordered_elements = [
            element
            for element in elements
            if self._is_structurable_element(element)
        ]
        if not ordered_elements:
            return [], set()

        detection = self._detect_structured_families(
            document_title=document_title,
            document_type=document_type,
            section=section,
            elements=ordered_elements,
        )
        specs = detection["specs"]
        if not specs:
            return [], set()

        fragments: list[ChunkFragment] = []
        consumed_element_ids: set[str] = set()
        for spec in specs:
            for window in self._collect_windows(ordered_elements, spec):
                fragment = self._build_fragment(
                    section=section,
                    elements=window,
                    spec=spec,
                )
                if fragment is None:
                    continue
                fragments.append(fragment)
                consumed_element_ids.update(fragment.element_ids)

        if detection["drawing_mode"] and fragments:
            consumed_element_ids.update(
                element.element_id
                for element in ordered_elements
            )

        return (
            sorted(fragments, key=lambda fragment: fragment.order_index),
            consumed_element_ids,
        )

    def _detect_structured_families(
        self,
        *,
        document_title: str | None,
        document_type: DocumentType | None,
        section: DocumentSection,
        elements: list[CanonicalElement],
    ) -> dict[str, object]:
        normalized_title = self._normalize_text(document_title)
        normalized_section = self._normalize_text(
            " > ".join(section.section_path or [section.title])
        )
        normalized_texts = [
            self._normalize_text(element.text)
            for element in elements
        ]
        combined_text = " ".join(text for text in normalized_texts if text)

        specs: list[StructuredSectionWindowSpec] = []
        drawing_mode = self._looks_like_drawing(
            document_title=normalized_title,
            section_text=normalized_section,
            combined_text=combined_text,
        )
        if drawing_mode:
            specs.extend(
                [
                    StructuredSectionWindowSpec(
                        section_path=["Title block"],
                        anchor_markers=("title arrangement", "drawing number"),
                        chunk_type=ChunkType.GENERAL,
                        radius_before=3,
                        radius_after=8,
                    ),
                    StructuredSectionWindowSpec(
                        section_path=["Revision / modification table"],
                        anchor_markers=("modification", "revision", "as-built"),
                        chunk_type=ChunkType.GENERAL,
                        radius_before=4,
                        radius_after=8,
                    ),
                    StructuredSectionWindowSpec(
                        section_path=["Title block / vessel particulars"],
                        anchor_markers=(
                            "length over all",
                            "breadth overall",
                            "draught to dwl",
                            "draught loadline",
                        ),
                        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                        radius_before=1,
                        radius_after=6,
                    ),
                    StructuredSectionWindowSpec(
                        section_path=["Lamp labels"],
                        anchor_markers=(
                            "masthead lamp",
                            "side lamp",
                            "combined anchor",
                            "lantern",
                        ),
                        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                        radius_before=0,
                        radius_after=4,
                    ),
                    StructuredSectionWindowSpec(
                        section_path=["Lamp labels"],
                        anchor_markers=(
                            "15 - combined",
                            "16 - combined",
                            "3540.6000",
                            "3540.7000",
                            "anchor / masthead",
                            "anchor/ towing",
                        ),
                        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                        radius_before=1,
                        radius_after=4,
                        combine_all_windows=True,
                    ),
                    StructuredSectionWindowSpec(
                        section_path=["COLREG table"],
                        anchor_markers=("colreg", "desired", "actual value"),
                        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                        radius_before=2,
                        radius_after=24,
                    ),
                ]
            )

        if self._looks_like_certificate(
            document_title=normalized_title,
            section_text=normalized_section,
            combined_text=combined_text,
            document_type=document_type,
        ):
            specs.extend(
                [
                    StructuredSectionWindowSpec(
                        section_path=["General information"],
                        anchor_markers=("general information", "manufacturer"),
                        chunk_type=ChunkType.CERTIFICATION_INFO,
                        radius_before=1,
                        radius_after=14,
                    ),
                    StructuredSectionWindowSpec(
                        section_path=["Particulars"],
                        anchor_markers=(
                            "particulars",
                            "quantity",
                            "test pressure",
                            "design pressure",
                        ),
                        chunk_type=ChunkType.CERTIFICATION_INFO,
                        radius_before=2,
                        radius_after=16,
                    ),
                ]
            )

        if self._looks_like_datasheet(
            document_title=normalized_title,
            section_text=normalized_section,
            combined_text=combined_text,
            document_type=document_type,
        ):
            specs.extend(
                [
                    StructuredSectionWindowSpec(
                        section_path=["Technical Data / Specification"],
                        anchor_markers=("specification", "design", "characteristics"),
                        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                        radius_before=1,
                        radius_after=14,
                    ),
                    StructuredSectionWindowSpec(
                        section_path=["CONNECTION"],
                        anchor_markers=("connection", "flange"),
                        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                        radius_before=1,
                        radius_after=10,
                    ),
                    StructuredSectionWindowSpec(
                        section_path=["Ordering example"],
                        anchor_markers=("ordering example", "mk311007"),
                        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                        radius_before=2,
                        radius_after=10,
                    ),
                    StructuredSectionWindowSpec(
                        section_path=[
                            "Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram"
                        ],
                        anchor_markers=(
                            "pressure-temperature-diagramm",
                            "druck-temperatur-diagramm",
                        ),
                        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                        radius_before=2,
                        radius_after=14,
                    ),
                ]
            )

        if self._looks_like_report(
            document_title=normalized_title,
            section_text=normalized_section,
            combined_text=combined_text,
        ):
            specs.extend(
                [
                    StructuredSectionWindowSpec(
                        section_path=["Final Inspection Report", "Device information"],
                        anchor_markers=("device information",),
                        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                        radius_before=3,
                        radius_after=14,
                    ),
                    StructuredSectionWindowSpec(
                        section_path=["Final Inspection Report", "Additional information"],
                        anchor_markers=("additional information",),
                        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                        radius_before=2,
                        radius_after=12,
                    ),
                ]
            )

        if self._looks_like_sensor_section(
            section_text=normalized_section,
            combined_text=combined_text,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    section_path=["7 Components", "7.6 Sensor List"],
                    anchor_markers=("7.6 sensor list", "p&id pos nr", "lmt100"),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=1,
                    radius_after=12,
                )
            )

        if self._looks_like_approval_matrix(
            section_text=normalized_section,
            combined_text=combined_text,
        ):
            specs.append(
                StructuredSectionWindowSpec(
                    section_path=[
                        "Safety Instructions",
                        "Extended order code: Cerabar M",
                        "Basic specifications",
                    ],
                    anchor_markers=(
                        "position 1, 2 (approval)",
                        "approval",
                        "atex",
                        "iecex",
                    ),
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    radius_before=0,
                    radius_after=2,
                    combine_all_windows=True,
                )
            )

        return {
            "drawing_mode": drawing_mode,
            "specs": specs,
        }

    def _collect_windows(
        self,
        elements: list[CanonicalElement],
        spec: StructuredSectionWindowSpec,
    ) -> list[list[CanonicalElement]]:
        anchor_indexes = [
            index
            for index, element in enumerate(elements)
            if self._matches_markers(
                self._normalize_text(element.text),
                spec.anchor_markers,
            )
        ]
        if not anchor_indexes:
            return []

        windows: list[tuple[int, int]] = []
        for anchor_index in anchor_indexes:
            start_index = max(0, anchor_index - spec.radius_before)
            end_index = min(len(elements) - 1, anchor_index + spec.radius_after)
            windows.append((start_index, end_index))

        merged_windows = self._merge_windows(windows)
        window_elements = [
            elements[start_index : end_index + 1]
            for start_index, end_index in merged_windows
        ]
        if spec.combine_all_windows and window_elements:
            combined_elements: list[CanonicalElement] = []
            seen_element_ids: set[str] = set()
            for window in window_elements:
                for element in window:
                    if element.element_id in seen_element_ids:
                        continue
                    seen_element_ids.add(element.element_id)
                    combined_elements.append(element)
            return [combined_elements]
        return window_elements

    def _build_fragment(
        self,
        *,
        section: DocumentSection,
        elements: list[CanonicalElement],
        spec: StructuredSectionWindowSpec,
    ) -> ChunkFragment | None:
        texts = [
            clean_chunk_text(element.text)
            for element in elements
            if clean_chunk_text(element.text)
        ]
        if not texts:
            return None

        content = "\n".join(texts).strip()
        token_count = self.text_splitter.count_tokens(content)
        if token_count < spec.min_tokens:
            return None

        first_element = elements[0]
        return ChunkFragment(
            text=content,
            chunk_type=spec.chunk_type,
            standalone=True,
            section_id=section.section_id,
            section_title=spec.section_path[-1],
            section_path=list(spec.section_path),
            section_level=section.level,
            parent_section_id=section.parent_section_id,
            element_ids=[element.element_id for element in elements],
            table_ids=[
                element.table_id
                for element in elements
                if element.table_id is not None
            ],
            picture_ids=[
                element.picture_id
                for element in elements
                if element.picture_id is not None
            ],
            page_start=min(
                (
                    element.source.page_start
                    for element in elements
                    if element.source.page_start is not None
                ),
                default=first_element.source.page_start,
            ),
            page_end=max(
                (
                    element.source.page_end
                    for element in elements
                    if element.source.page_end is not None
                ),
                default=first_element.source.page_end,
            ),
            token_count=token_count,
            order_index=first_element.reading_order or 0,
        )

    @staticmethod
    def _merge_windows(windows: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if not windows:
            return []

        ordered_windows = sorted(windows)
        merged_windows = [ordered_windows[0]]
        for start_index, end_index in ordered_windows[1:]:
            previous_start, previous_end = merged_windows[-1]
            if start_index <= previous_end + 1:
                merged_windows[-1] = (
                    previous_start,
                    max(previous_end, end_index),
                )
                continue
            merged_windows.append((start_index, end_index))
        return merged_windows

    @staticmethod
    def _is_structurable_element(element: CanonicalElement) -> bool:
        if element.element_type not in {
            ElementType.TEXT,
            ElementType.LIST_ITEM,
            ElementType.KEY_VALUE,
            ElementType.CODE,
            ElementType.TABLE,
        }:
            return False
        return bool(clean_chunk_text(element.text))

    @staticmethod
    def _matches_markers(text: str, markers: tuple[str, ...]) -> bool:
        return any(marker in text for marker in markers)

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        return " ".join(str(value or "").strip().lower().split())

    @staticmethod
    def _looks_like_drawing(
        *,
        document_title: str,
        section_text: str,
        combined_text: str,
    ) -> bool:
        return any(
            marker in " ".join((document_title, section_text, combined_text))
            for marker in DRAWING_STRUCTURED_MARKERS
        )

    @staticmethod
    def _looks_like_certificate(
        *,
        document_title: str,
        section_text: str,
        combined_text: str,
        document_type: DocumentType | None,
    ) -> bool:
        if document_type == DocumentType.CERTIFICATE:
            return True
        return any(
            marker in " ".join((document_title, section_text, combined_text))
            for marker in CERTIFICATE_STRUCTURED_MARKERS
        )

    @staticmethod
    def _looks_like_datasheet(
        *,
        document_title: str,
        section_text: str,
        combined_text: str,
        document_type: DocumentType | None,
    ) -> bool:
        if document_type == DocumentType.DATASHEET:
            return True
        return any(
            marker in " ".join((document_title, section_text, combined_text))
            for marker in DATASHEET_STRUCTURED_MARKERS
        )

    @staticmethod
    def _looks_like_report(
        *,
        document_title: str,
        section_text: str,
        combined_text: str,
    ) -> bool:
        return any(
            marker in " ".join((document_title, section_text, combined_text))
            for marker in REPORT_STRUCTURED_MARKERS
        )

    @staticmethod
    def _looks_like_sensor_section(
        *,
        section_text: str,
        combined_text: str,
    ) -> bool:
        return any(
            marker in " ".join((section_text, combined_text))
            for marker in SENSOR_LIST_STRUCTURED_MARKERS
        )

    @staticmethod
    def _looks_like_approval_matrix(
        *,
        section_text: str,
        combined_text: str,
    ) -> bool:
        haystack = " ".join((section_text, combined_text))
        return (
            "approval" in haystack
            and "atex" in haystack
            and "iecex" in haystack
        )
