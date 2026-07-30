from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.domain.common import DocumentType


class DocumentMetadataExtractor:
    """Extracts document-level metadata (language, document type) from a raw parsed document."""

    @staticmethod
    def extract_language(raw_parsed_document: RawParsedDocument) -> str | None:
        language = raw_parsed_document.metadata.get("language")
        if isinstance(language, str) and language.strip():
            return language.strip()
        return None

    @staticmethod
    def extract_document_type(raw_parsed_document: RawParsedDocument) -> DocumentType:
        raw_document_type = raw_parsed_document.metadata.get("document_type")
        if isinstance(raw_document_type, str):
            normalized = raw_document_type.strip().lower()
            for document_type in DocumentType:
                if normalized == document_type.value:
                    return document_type

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
                return document_type

        return DocumentType.UNKNOWN
