from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
)


class EvidenceSchemaFormatter:
    def format(self, context: PromptContextBundle | None) -> str:
        if context is None:
            return ""
        lines = [
            "Evidence schema:",
            "- sources: provenance records for retrieved evidence units with section/page scope and retained structured table rows when they are the primary prompt representation.",
            "- key_values: normalized factual values derived from text or tables, each tied to a source_number.",
            "- maintenance_entries: task-centered maintenance records with interval, component, notes, and explicit references.",
            "- structured_entities: typed entities with nested fields and typed relationships.",
            "- source_groups: source numbers grouped by chunk type.",
            "- section_groups: source numbers grouped by section path and page span.",
        ]
        return "\n".join(lines) + "\n\n"
