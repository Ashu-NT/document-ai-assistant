from collections import Counter

from src.application.workflows.parsing.builders.section_build_result import (
    SectionBuildResult,
)
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.domain.document import DocumentGraph


class DocumentPersistentMetadataBuilder:
    SECTION_PATH_SCHEMA_VERSION = "2"
    TABLE_STRUCTURE_SCHEMA_VERSION = "1"
    TABLE_SEMANTIC_SCHEMA_VERSION = "1"
    OCR_PROVENANCE_SCHEMA_VERSION = "1"

    def build(
        self,
        *,
        raw_parsed_document: RawParsedDocument,
        section_build_result: SectionBuildResult,
        graph: DocumentGraph,
    ) -> dict[str, object]:
        table_categories = Counter(
            table.table_category
            for table in graph.tables.values()
            if table.table_category
        )
        logical_table_families = {
            table.logical_table_family_id
            for table in graph.tables.values()
            if table.logical_table_family_id
        }

        return {
            "parser": {
                "name": raw_parsed_document.parser_name,
                "version": raw_parsed_document.parser_version,
            },
            "artifact_versions": {
                "section_path_schema": self.SECTION_PATH_SCHEMA_VERSION,
                "table_structure_schema": self.TABLE_STRUCTURE_SCHEMA_VERSION,
                "table_semantic_schema": self.TABLE_SEMANTIC_SCHEMA_VERSION,
                "ocr_provenance_schema": self.OCR_PROVENANCE_SCHEMA_VERSION,
            },
            "outline": {
                "header_numberings": dict(section_build_result.header_numberings),
                "toc_outline": (
                    section_build_result.toc_outline.to_dict()
                    if section_build_result.toc_outline is not None
                    else None
                ),
            },
            "table_understanding": {
                "logical_table_family_count": len(logical_table_families),
                "table_category_counts": dict(table_categories),
            },
        }
