from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.builders.structured.markers import (
    StructuredMarkerMatcher,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_element_text_resolver import (
    StructuredElementTextResolver,
)
from src.domain.common import DocumentType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


_MARKER_MATCHER = StructuredMarkerMatcher()


@dataclass(slots=True, frozen=True)
class StructuredFamilyContext:
    document_title: str | None
    document_type: DocumentType | None
    section: DocumentSection
    elements: tuple[CanonicalElement, ...]

    normalized_title: str
    normalized_section_text: str
    normalized_texts: tuple[str, ...]
    combined_text: str
    document_sections_combined_text: str = ""

    @classmethod
    def from_inputs(
        cls,
        *,
        document_title: str | None,
        document_type: DocumentType | None,
        section: DocumentSection,
        elements: list[CanonicalElement],
        normalizer,
        document_sections_combined_text: str = "",
    ) -> "StructuredFamilyContext":
        normalized_parts: list[str] = []

        for element in elements:
            normalized_text = normalizer(
                StructuredElementTextResolver.resolve(element)
            )

            if normalized_text:
                normalized_parts.append(normalized_text)

        normalized_texts = tuple(normalized_parts)

        return cls(
            document_title=document_title,
            document_type=document_type,
            section=section,
            elements=tuple(elements),
            normalized_title=normalizer(document_title),
            normalized_section_text=normalizer(
                " > ".join(
                    section.section_path
                    or [section.title]
                )
            ),
            normalized_texts=normalized_texts,
            combined_text=" ".join(normalized_texts),
            document_sections_combined_text=normalizer(
                document_sections_combined_text
            ),
        )

    def base_section_path(self) -> list[str]:
        if self.section.section_path:
            return list(self.section.section_path)

        if self.section.title:
            return [self.section.title]

        return []

    def has_known_document_type(self) -> bool:
        return self.document_type not in {
            None,
            DocumentType.UNKNOWN,
        }

    def matches_document_type(
        self,
        document_type: DocumentType,
    ) -> bool:
        return self.document_type == document_type

    def contains_any(
        self,
        markers: tuple[EvidenceMarker, ...],
    ) -> bool:
        return self._contains_in(
            markers,
            self.normalized_title,
            self.normalized_section_text,
            self.combined_text,
            self.document_sections_combined_text,
        )

    def local_contains_any(
        self,
        markers: tuple[EvidenceMarker, ...],
    ) -> bool:
        return self._contains_in(
            markers,
            self.normalized_title,
            self.normalized_section_text,
            self.combined_text,
            *self.normalized_texts,
        )

    def document_contains_any(
        self,
        markers: tuple[EvidenceMarker, ...],
    ) -> bool:
        return self._contains_in(
            markers,
            self.document_sections_combined_text,
        )

    def section_contains_any(
        self,
        markers: tuple[EvidenceMarker, ...],
    ) -> bool:
        return self._contains_in(
            markers,
            self.normalized_title,
            self.normalized_section_text,
        )

    def content_contains_any(
        self,
        markers: tuple[EvidenceMarker, ...],
    ) -> bool:
        return self._contains_in(
            markers,
            self.combined_text,
            *self.normalized_texts,
        )

    @staticmethod
    def _contains_in(
        markers: tuple[EvidenceMarker, ...],
        *haystacks: str,
    ) -> bool:
        return any(
            _MARKER_MATCHER.contains_any(
                haystack,
                markers,
            )
            for haystack in haystacks
            if haystack
        )
        
    def section_contains_any_term(
        self,
        terms: tuple[str, ...],
    ) -> bool:
        return _MARKER_MATCHER.contains_any_term(
            self.normalized_section_text,
            terms,
        )


    def content_contains_any_term(
        self,
        terms: tuple[str, ...],
    ) -> bool:
        return _MARKER_MATCHER.contains_any_term(
            self.combined_text,
            terms,
        )