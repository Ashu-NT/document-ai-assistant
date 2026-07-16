from src.application.workflows.parsing.tables.semantics import (
    TableSemanticClassifier,
)
from src.application.workflows.parsing.tables.structure import (
    TableStructureSummaryBuilder,
)
from src.application.workflows.parsing.tables.normalization import (
    TableRowSemanticNormalizer,
)
from src.domain.document import DocumentGraph
from src.domain.elements import CanonicalElement


class TableSemanticResolver:
    def __init__(
        self,
        *,
        classifier: TableSemanticClassifier | None = None,
        row_normalizer: TableRowSemanticNormalizer | None = None,
        structure_summary_builder: TableStructureSummaryBuilder | None = None,
    ) -> None:
        self.classifier = classifier or TableSemanticClassifier()
        self.row_normalizer = row_normalizer or TableRowSemanticNormalizer()
        self.structure_summary_builder = (
            structure_summary_builder or TableStructureSummaryBuilder()
        )

    def resolve(self, graph: DocumentGraph) -> None:
        for element in graph.elements.values():
            if element.table_id is None or element.table_id not in graph.tables:
                continue

            table = graph.tables[element.table_id]
            parser_extra = dict(element.parser_metadata.extra or {}) if element.parser_metadata else {}
            section = graph.sections.get(table.parent_section_id or element.parent_section_id or "")
            section_path = list(
                section.normalized_section_path
                if section is not None and section.normalized_section_path
                else parser_extra.get("resolved_section_path") or []
            )
            structure_summary = self.structure_summary_builder.build(table)
            category, confidence = self.classifier.classify(
                table=table,
                caption=table.metadata.caption,
                nearby_text=table.metadata.nearby_text,
                section_path=section_path,
                item_label=parser_extra.get("item_label"),
                structure_summary=structure_summary,
            )
            table.table_category = category.value
            table.table_category_confidence = confidence
            signals = self.classifier.detect_signals(
                table=table,
                caption=table.metadata.caption,
                nearby_text=table.metadata.nearby_text,
                section_path=section_path,
            )
            table.signals = frozenset(signal.value for signal in signals)
            rows_normalized = self.row_normalizer.normalize(table)
            if structure_summary is not None:
                table.table_shape = structure_summary.table_shape.value
                table.table_structure_quality = structure_summary.quality_score
                table.header_paths = [
                    list(path) for path in structure_summary.header_paths
                ]
                table.axis_summary = dict(structure_summary.axis_summary)

            if element.parser_metadata is not None:
                updated_extra = {
                    **parser_extra,
                    "normalized_table_section_path": section_path,
                    "table_category": category.value,
                    "table_category_confidence": confidence,
                    "table_semantic_version": "3",
                    "table_rows": [list(row) for row in table.rows],
                    "row_count": len(table.rows) or None,
                    "column_count": max((len(row) for row in table.rows), default=0)
                    or None,
                }
                if table.parallel_stream_rows:
                    updated_extra["table_parallel_stream_rows"] = [
                        [list(row) for row in stream_rows]
                        for stream_rows in table.parallel_stream_rows
                    ]
                    updated_extra["table_parallel_stream_count"] = len(
                        table.parallel_stream_rows
                    )
                if rows_normalized:
                    updated_extra["table_row_normalization_version"] = "1"
                if table.table_shape:
                    updated_extra["table_shape"] = table.table_shape
                if table.table_structure_quality is not None:
                    updated_extra["table_structure_quality"] = (
                        table.table_structure_quality
                    )
                if table.header_paths:
                    updated_extra["table_header_paths_json"] = [
                        list(path) for path in table.header_paths
                    ]
                if table.axis_summary:
                    updated_extra["table_axis_summary"] = dict(table.axis_summary)
                if table.signals:
                    updated_extra["table_signals"] = sorted(table.signals)
                element.parser_metadata.extra = updated_extra
