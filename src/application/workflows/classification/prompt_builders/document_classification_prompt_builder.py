from src.application.workflows.classification.prompt_builders.document_graph_classification_summary_builder import (
    DocumentGraphClassificationSummaryBuilder,
)
from src.domain.common import DocumentType
from src.domain.document import Document, DocumentGraph


class DocumentClassificationPromptBuilder:
    prompt_version = "v2"

    def __init__(
        self,
        *,
        summary_builder: DocumentGraphClassificationSummaryBuilder | None = None,
    ) -> None:
        self.summary_builder = (
            summary_builder or DocumentGraphClassificationSummaryBuilder()
        )

    def build(self, document_or_graph: DocumentGraph | Document) -> str:
        document = self._resolve_document(document_or_graph)
        document_types = ", ".join(
            document_type.value
            for document_type in DocumentType
        )
        title = document.title or "N/A"
        language = document.language or "N/A"
        stats = self._resolve_statistics(document_or_graph)
        graph_summary = self._resolve_graph_summary(document_or_graph)

        return (
            "You classify technical documents using metadata, document statistics, "
            "document structure, and representative content from a parsed document graph.\n"
            "Return JSON only.\n"
            "Use this schema:\n"
            "{\n"
            '  "label": "<document type>",\n'
            '  "confidence_score": <float between 0 and 1>,\n'
            '  "rationale": "<short explanation>",\n'
            '  "evidence": ["<evidence 1>", "<evidence 2>"]\n'
            "}\n"
            f"Allowed labels: {document_types}\n"
            "Decision guidance:\n"
            "- Prioritize graph-derived section, chunk, table, and picture evidence over file path naming.\n"
            "- Use document statistics as supporting evidence, not the sole basis.\n"
            "- If signals conflict or remain insufficient, use the label 'unknown'.\n"
            f"Document id: {document.document_id}\n"
            f"File name: {document.file_name}\n"
            f"File path: {document.file_path}\n"
            f"Title: {title}\n"
            f"Language: {language}\n"
            "Document statistics:\n"
            f"- Page count: {stats['page_count']}\n"
            f"- Element count: {stats['element_count']}\n"
            f"- Section count: {stats['section_count']}\n"
            f"- Chunk count: {stats['chunk_count']}\n"
            f"- Table count: {stats['table_count']}\n"
            f"- Picture count: {stats['picture_count']}\n"
            "Graph-derived content summary:\n"
            f"{graph_summary}"
        )

    @staticmethod
    def _resolve_document(document_or_graph: DocumentGraph | Document) -> Document:
        if isinstance(document_or_graph, DocumentGraph):
            return document_or_graph.document
        return document_or_graph

    def _resolve_graph_summary(self, document_or_graph: DocumentGraph | Document) -> str:
        if isinstance(document_or_graph, DocumentGraph):
            return self.summary_builder.build(document_or_graph)
        return "- No graph-derived content summary was available."

    @staticmethod
    def _resolve_statistics(
        document_or_graph: DocumentGraph | Document,
    ) -> dict[str, int | str]:
        if isinstance(document_or_graph, DocumentGraph):
            document = document_or_graph.document
            return {
                "page_count": (
                    document.statistics.page_count
                    if document.statistics.page_count is not None
                    else "N/A"
                ),
                "element_count": len(document_or_graph.elements),
                "section_count": len(document_or_graph.sections),
                "chunk_count": len(document_or_graph.chunks),
                "table_count": len(document_or_graph.tables),
                "picture_count": len(document_or_graph.pictures),
            }

        return {
            "page_count": (
                document_or_graph.statistics.page_count
                if document_or_graph.statistics.page_count is not None
                else "N/A"
            ),
            "element_count": document_or_graph.statistics.element_count,
            "section_count": document_or_graph.statistics.section_count,
            "chunk_count": document_or_graph.statistics.chunk_count,
            "table_count": document_or_graph.statistics.table_count,
            "picture_count": document_or_graph.statistics.picture_count,
        }
