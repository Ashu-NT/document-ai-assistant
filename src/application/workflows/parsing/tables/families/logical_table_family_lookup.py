from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from src.domain.assets import TableAsset


@dataclass(frozen=True, slots=True)
class LogicalTableFamilyLookup:
    tables_by_id: dict[str, TableAsset]
    family_members_by_id: dict[str, tuple[TableAsset, ...]]
    table_to_family_id: dict[str, str]

    @classmethod
    def from_tables(
        cls,
        tables: Mapping[str, TableAsset],
    ) -> "LogicalTableFamilyLookup":
        tables_by_id = {table_id: table for table_id, table in tables.items()}
        family_buckets: dict[str, list[TableAsset]] = {}
        table_to_family_id: dict[str, str] = {}

        for table in tables_by_id.values():
            family_id = str(table.logical_table_family_id or "").strip()
            if not family_id:
                continue
            family_buckets.setdefault(family_id, []).append(table)
            table_to_family_id[table.table_id] = family_id

        family_members_by_id = {
            family_id: tuple(_ordered_tables(members))
            for family_id, members in family_buckets.items()
        }
        return cls(
            tables_by_id=tables_by_id,
            family_members_by_id=family_members_by_id,
            table_to_family_id=table_to_family_id,
        )

    def family_id_for_table_ids(self, table_ids: Sequence[str]) -> str | None:
        for table_id in table_ids:
            family_id = self.table_to_family_id.get(str(table_id).strip())
            if family_id:
                return family_id
        return None

    def members_for_table_ids(self, table_ids: Sequence[str]) -> list[TableAsset]:
        ordered_members: list[TableAsset] = []
        seen_table_ids: set[str] = set()
        seen_family_ids: set[str] = set()

        for raw_table_id in table_ids:
            table_id = str(raw_table_id).strip()
            if not table_id:
                continue
            family_id = self.table_to_family_id.get(table_id)
            if family_id and family_id not in seen_family_ids:
                seen_family_ids.add(family_id)
                for member in self.family_members_by_id.get(family_id, ()):
                    if member.table_id not in seen_table_ids:
                        ordered_members.append(member)
                        seen_table_ids.add(member.table_id)
                continue

            table = self.tables_by_id.get(table_id)
            if table is not None and table.table_id not in seen_table_ids:
                ordered_members.append(table)
                seen_table_ids.add(table.table_id)

        return ordered_members


def _ordered_tables(tables: Sequence[TableAsset]) -> list[TableAsset]:
    return sorted(
        tables,
        key=lambda table: (
            table.family_index if table.family_index is not None else 10_000,
            table.table_id,
        ),
    )
