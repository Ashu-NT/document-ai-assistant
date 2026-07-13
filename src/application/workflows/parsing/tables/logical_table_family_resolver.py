from src.application.workflows.parsing.tables.logical_table_family_assignment import (
    LogicalTableFamilyAssignment,
)
from src.application.workflows.parsing.tables.table_header_compatibility_matcher import (
    TableHeaderCompatibilityMatcher,
)
from src.application.workflows.parsing.tables.table_header_signature_builder import (
    TableHeaderSignatureBuilder,
)
from src.domain.document import DocumentGraph
from src.domain.elements import CanonicalElement


class LogicalTableFamilyResolver:
    def __init__(
        self,
        *,
        header_signature_builder: TableHeaderSignatureBuilder | None = None,
        header_compatibility_matcher: TableHeaderCompatibilityMatcher | None = None,
        max_continuation_page_gap: int = 1,
    ) -> None:
        self.header_signature_builder = (
            header_signature_builder or TableHeaderSignatureBuilder()
        )
        self.header_compatibility_matcher = (
            header_compatibility_matcher
            or TableHeaderCompatibilityMatcher(
                header_signature_builder=self.header_signature_builder
            )
        )
        self.max_continuation_page_gap = max_continuation_page_gap

    def resolve(self, graph: DocumentGraph) -> None:
        table_elements = self._sorted_table_elements(graph)
        families: list[list[CanonicalElement]] = []

        for element in table_elements:
            if not families or not self._continues_family(graph, families[-1][-1], element):
                families.append([element])
                continue
            families[-1].append(element)

        for family in families:
            assignment_by_table_id = self._build_assignments(graph, family)
            for element in family:
                if element.table_id is None:
                    continue
                assignment = assignment_by_table_id.get(element.table_id)
                if assignment is None:
                    continue
                self._apply_assignment(graph, element, assignment)

    @staticmethod
    def _sorted_table_elements(graph: DocumentGraph) -> list[CanonicalElement]:
        return sorted(
            [
                element
                for element in graph.elements.values()
                if element.table_id is not None and element.table_id in graph.tables
            ],
            key=lambda element: (
                element.source.page_start or 0,
                element.source.page_end or 0,
                element.reading_order or 0,
            ),
        )

    def _continues_family(
        self,
        graph: DocumentGraph,
        previous: CanonicalElement,
        current: CanonicalElement,
    ) -> bool:
        previous_table = graph.tables.get(previous.table_id or "")
        current_table = graph.tables.get(current.table_id or "")
        if previous_table is None or current_table is None:
            return False

        previous_item_label = self._item_label(previous)
        current_item_label = self._item_label(current)
        if previous_item_label == current_item_label == "document_index":
            return self._pages_are_adjacent(previous, current) and self._column_counts_are_compatible(
                previous_table,
                current_table,
            )

        if previous.parent_section_id != current.parent_section_id:
            return False

        if not self.header_compatibility_matcher.are_compatible(
            previous_table,
            current_table,
        ):
            return False

        if not self._column_counts_are_compatible(previous_table, current_table):
            return False

        return self._pages_are_adjacent(previous, current)

    def _pages_are_adjacent(
        self,
        previous: CanonicalElement,
        current: CanonicalElement,
    ) -> bool:
        previous_page = previous.source.page_end or previous.source.page_start
        current_page = current.source.page_start or current.source.page_end
        if previous_page is None or current_page is None:
            return False

        page_gap = current_page - previous_page
        return 0 <= page_gap <= self.max_continuation_page_gap

    @staticmethod
    def _column_counts_are_compatible(previous_table, current_table) -> bool:
        return not (
            previous_table.column_count is not None
            and current_table.column_count is not None
            and previous_table.column_count != current_table.column_count
        )

    @staticmethod
    def _item_label(element: CanonicalElement) -> str | None:
        if element.parser_metadata is None:
            return None
        value = str(element.parser_metadata.extra.get("item_label") or "").strip().lower()
        return value or None

    def _build_assignments(
        self,
        graph: DocumentGraph,
        family: list[CanonicalElement],
    ) -> dict[str, LogicalTableFamilyAssignment]:
        first_table_id = family[0].table_id
        if first_table_id is None:
            return {}

        logical_table_family_id = f"table_family_{first_table_id}"
        family_total = len(family)
        assignments: dict[str, LogicalTableFamilyAssignment] = {}

        for index, element in enumerate(family, start=1):
            table_id = element.table_id
            if table_id is None:
                continue

            table = graph.tables.get(table_id)
            normalized_header_signature = (
                self.header_signature_builder.build(table) if table is not None else None
            )
            assignments[table_id] = LogicalTableFamilyAssignment(
                logical_table_family_id=logical_table_family_id,
                family_index=index,
                family_total=family_total,
                continuation_role=self._resolve_continuation_role(
                    family_index=index,
                    family_total=family_total,
                ),
                normalized_header_signature=normalized_header_signature,
            )

        return assignments

    @staticmethod
    def _resolve_continuation_role(*, family_index: int, family_total: int) -> str:
        if family_total <= 1:
            return "single"
        if family_index == 1:
            return "start"
        if family_index == family_total:
            return "end"
        return "middle"

    @staticmethod
    def _apply_assignment(
        graph: DocumentGraph,
        element: CanonicalElement,
        assignment: LogicalTableFamilyAssignment,
    ) -> None:
        table = graph.tables.get(element.table_id or "")
        if table is not None:
            table.logical_table_family_id = assignment.logical_table_family_id
            table.family_index = assignment.family_index
            table.family_total = assignment.family_total
            table.continuation_role = assignment.continuation_role
            table.normalized_header_signature = assignment.normalized_header_signature

        parser_metadata = element.parser_metadata
        if parser_metadata is None:
            return

        parser_metadata.extra = {
            **dict(parser_metadata.extra or {}),
            "logical_table_family_id": assignment.logical_table_family_id,
            "family_index": assignment.family_index,
            "family_total": assignment.family_total,
            "continuation_role": assignment.continuation_role,
            "normalized_header_signature": assignment.normalized_header_signature,
            "logical_table_family_version": "1",
        }
