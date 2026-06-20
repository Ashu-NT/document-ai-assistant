from dataclasses import dataclass, field

from src.domain.assets import PictureAsset, TableAsset
from src.domain.document.entities import (
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

    questions: dict[str, GeneratedQuestion] = field(default_factory=dict)
    identifiers: dict[str, Identifier] = field(default_factory=dict)

    def add_element(self, element: CanonicalElement) -> None:
        self.elements[element.element_id] = element

    def add_section(self, section: DocumentSection) -> None:
        self.sections[section.section_id] = section

    def add_chunk(self, chunk: DocumentChunk) -> None:
        self.chunks[chunk.chunk_id] = chunk

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
