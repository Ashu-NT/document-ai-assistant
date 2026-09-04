from dataclasses import dataclass, field

from src.domain.assets import FormAsset, PictureAsset, TableAsset
from src.domain.document.entities import (
    ChunkCrossReference,
    CrossReferenceEvidence,
    DocumentChunk,
    Document,
    Identifier,
    GeneratedQuestion,
    DocumentSection,
)
from src.domain.elements import CanonicalElement


@dataclass(slots=True)
class DocumentGraph:
    document: Document

    elements: dict[str, CanonicalElement] = field(default_factory=dict)
    sections: dict[str, DocumentSection] = field(default_factory=dict)
    chunks: dict[str, DocumentChunk] = field(default_factory=dict)

    tables: dict[str, TableAsset] = field(default_factory=dict)
    pictures: dict[str, PictureAsset] = field(default_factory=dict)
    forms: dict[str, FormAsset] = field(default_factory=dict)

    questions: dict[str, GeneratedQuestion] = field(default_factory=dict)
    identifiers: dict[str, Identifier] = field(default_factory=dict)
    cross_references: dict[str, ChunkCrossReference] = field(default_factory=dict)
    # Audit-only evidence backing reconciled/canonical cross-references (see
    # CrossReferenceReconciliationService). Never read by retrieval.
    cross_reference_evidence: dict[str, CrossReferenceEvidence] = field(
        default_factory=dict
    )

    def add_element(self, element: CanonicalElement) -> None:
        self.elements[element.element_id] = element

    def add_section(self, section: DocumentSection) -> None:
        self.sections[section.section_id] = section

    def add_chunk(self, chunk: DocumentChunk) -> None:
        self.chunks[chunk.chunk_id] = chunk

    def add_cross_reference(self, cross_reference: ChunkCrossReference) -> None:
        self.cross_references[cross_reference.cross_reference_id] = cross_reference

    def add_cross_reference_evidence(self, evidence: CrossReferenceEvidence) -> None:
        self.cross_reference_evidence[evidence.evidence_id] = evidence

    def replace_chunks(self, chunks: list[DocumentChunk]) -> None:
        self.chunks = {chunk.chunk_id: chunk for chunk in chunks}

    def replace_questions(self, questions: list[GeneratedQuestion]) -> None:
        self.questions = {
            question.question_id: question
            for question in questions
        }

    def clear_chunk_dependents(self) -> None:
        self.questions = {}
        self.identifiers = {}

    def get_section_elements(self, section_id: str) -> list[CanonicalElement]:
        section = self.sections[section_id]
        return [
            self.elements[element_id]
            for element_id in section.element_ids
            if element_id in self.elements
        ]

    def get_chunk_questions(self, chunk_id: str) -> list[GeneratedQuestion]:
        return [
            question
            for question in self.questions.values()
            if question.chunk_id == chunk_id
        ]

    def get_chunk_identifiers(self, chunk_id: str) -> list[Identifier]:
        return [
            identifier
            for identifier in self.identifiers.values()
            if identifier.chunk_id == chunk_id
        ]

    def get_chunk_cross_references(self, chunk_id: str) -> list[ChunkCrossReference]:
        return [
            cross_reference
            for cross_reference in self.cross_references.values()
            if cross_reference.source_chunk_id == chunk_id
        ]
