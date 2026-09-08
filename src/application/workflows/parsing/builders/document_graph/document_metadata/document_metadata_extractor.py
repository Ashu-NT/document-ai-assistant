from dataclasses import dataclass

from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.domain.common import DocumentType


@dataclass(frozen=True, slots=True)
class DocumentTypeHint:
    """Result of extracting a document type from parser/title metadata.

    `is_confirmed` distinguishes an explicit, caller-provided document type
    (metadata's own `document_type` field) from a mere title-keyword guess:
    only a confirmed type is safe to treat as authoritative. A guess must
    still be corroborated (by structural inference and/or model
    classification) before it drives a decision -- see
    HybridDocumentTypeResolver, whose `parser_title_hint` parameter exists
    for exactly this reason.
    """

    document_type: DocumentType
    is_confirmed: bool


class DocumentMetadataExtractor:
    """Extracts document-level metadata (language, document type) from a raw parsed document."""

    @staticmethod
    def extract_language(raw_parsed_document: RawParsedDocument) -> str | None:
        language = raw_parsed_document.metadata.get("language")
        if isinstance(language, str) and language.strip():
            return language.strip()
        return None

    @staticmethod
    def extract_document_type_hint(
        raw_parsed_document: RawParsedDocument,
    ) -> DocumentTypeHint:
        raw_document_type = raw_parsed_document.metadata.get("document_type")
        if isinstance(raw_document_type, str):
            normalized = raw_document_type.strip().lower()
            for document_type in DocumentType:
                if normalized == document_type.value:
                    return DocumentTypeHint(
                        document_type=document_type, is_confirmed=True
                    )

        title = (raw_parsed_document.title or "").strip().lower()
        title_markers = {
            "datasheet": DocumentType.DATASHEET,
            "manual": DocumentType.MANUAL,
            "drawing": DocumentType.DRAWING,
            "report": DocumentType.REPORT,
            "certificate": DocumentType.CERTIFICATE,
        }
        for marker, document_type in title_markers.items():
            if marker in title:
                return DocumentTypeHint(document_type=document_type, is_confirmed=False)

        return DocumentTypeHint(document_type=DocumentType.UNKNOWN, is_confirmed=False)
