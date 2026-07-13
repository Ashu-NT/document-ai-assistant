from dataclasses import dataclass


@dataclass(slots=True)
class LogicalTableFamilyAssignment:
    logical_table_family_id: str
    family_index: int
    family_total: int
    continuation_role: str
    normalized_header_signature: str | None = None
