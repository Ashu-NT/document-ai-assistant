from src.application.workflows.parsing.tables.semantics import (
    TableCategory,
    TableSemanticClassifier,
)
from src.domain.document import DocumentGraph
from src.domain.elements import CanonicalElement


class TableSemanticResolver:
    def __init__(
        self,
        *,
        classifier: TableSemanticClassifier | None = None,
    ) -> None:
        self.classifier = classifier or TableSemanticClassifier()

    def resolve(self, graph: DocumentGraph) -> None:
        for element in graph.elements.values():
            if element.table_id is None or element.table_id not in graph.tables:
                continue

            table = graph.tables[element.table_id]
            parser_extra = dict(element.parser_metadata.extra or {}) if element.parser_metadata else {}
            category, confidence = self.classifier.classify(
                table=table,
                caption=table.metadata.caption,
                section_path=parser_extra.get("resolved_section_path") or [],
                item_label=parser_extra.get("item_label"),
            )
            table.table_category = category.value
            table.table_category_confidence = confidence

            if element.parser_metadata is not None:
                element.parser_metadata.extra = {
                    **parser_extra,
                    "table_category": category.value,
                    "table_category_confidence": confidence,
                    "table_semantic_version": "1",
                }
