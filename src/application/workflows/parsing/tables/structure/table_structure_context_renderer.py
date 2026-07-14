from __future__ import annotations

from src.domain.assets import TableAsset


class TableStructureContextRenderer:
    def render(self, table: TableAsset) -> str | None:
        parts: list[str] = []
        table_shape = table.resolved_table_shape()
        if table_shape:
            parts.append(f"Table shape: {table_shape}")
        if table.header_paths:
            formatted_paths = [
                " > ".join(path).strip()
                for path in table.header_paths
                if any(str(part).strip() for part in path)
            ]
            if formatted_paths:
                parts.append("Header paths: " + " | ".join(formatted_paths))
        if table.axis_summary:
            parts.append(
                "Axis summary: "
                + "; ".join(
                    f"{key}={value}"
                    for key, value in table.axis_summary.items()
                    if str(key).strip() and str(value).strip()
                )
            )
        return "\n".join(parts) if parts else None
