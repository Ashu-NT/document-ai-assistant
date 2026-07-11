from src.application.prompts.answer_generation.maintenance_prompt_context_formatter import (
    MaintenancePromptContextFormatter,
)
from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
)


class OrganizedContextFormatter:
    def __init__(
        self,
        maintenance_context_formatter: MaintenancePromptContextFormatter | None = None,
    ) -> None:
        self.maintenance_context_formatter = (
            maintenance_context_formatter or MaintenancePromptContextFormatter()
        )

    def format(self, context: PromptContextBundle | None) -> str:
        if context is None:
            return ""

        lines = [
            "Organized context:",
            f"- Intent: {context.answer_intent_value}",
            f"- Source count: {context.source_count}",
        ]
        if context.maintenance_entries:
            lines.extend(
                self.maintenance_context_formatter.format(context.maintenance_entries)
            )
        if context.key_values:
            lines.append("Key values:")
            for item in context.key_values:
                value = item.value
                if item.unit and item.unit.lower() not in value.lower():
                    value = f"{value} {item.unit}"
                lines.append(f"- [SOURCE {item.source_number}] {item.key}: {value}")
        if context.entities:
            lines.append("Structured entities:")
            for entity in context.entities:
                lines.append(
                    f"- {entity.entity_type} [{entity.entity_id}]: "
                    f"{self._format_entity_fields(entity.fields)}"
                )
                for relationship in entity.relationships:
                    lines.append(
                        f"  - {relationship.relationship_type} -> "
                        f"{relationship.target_entity_type} "
                        f"[{relationship.target_entity_id}]: "
                        f"{self._format_entity_fields(relationship.target_entity_fields)}"
                    )
        if context.source_groups:
            lines.append("Source groups:")
            for group in context.source_groups:
                source_refs = ", ".join(
                    f"SOURCE {source_number}" for source_number in group.source_numbers
                )
                lines.append(f"- {group.group_name}: {source_refs}")
        if context.section_groups:
            lines.append("Section groups:")
            for group in context.section_groups:
                page_range = self._format_page_bounds(group.page_start, group.page_end)
                source_refs = ", ".join(
                    f"SOURCE {source_number}" for source_number in group.source_numbers
                )
                lines.append(
                    f"- {group.group_name} | Pages: {page_range} | Sources: {source_refs}"
                )
        return "\n".join(lines) + "\n\n"

    @staticmethod
    def _format_entity_fields(fields: dict[str, object]) -> str:
        if not fields:
            return "(no additional fields)"
        parts: list[str] = []
        for key, value in fields.items():
            if isinstance(value, list):
                value = "; ".join(str(item) for item in value)
            parts.append(f"{key}: {value}")
        return ", ".join(parts)

    @staticmethod
    def _format_page_bounds(
        page_start: int | None,
        page_end: int | None,
    ) -> str:
        if page_start is None and page_end is None:
            return "N/A"
        if page_start == page_end:
            return str(page_start)
        if page_start is None:
            return str(page_end)
        if page_end is None:
            return str(page_start)
        return f"{page_start}-{page_end}"
