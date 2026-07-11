from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
)


class EvidenceSchemaFormatter:
    def format(self, context: PromptContextBundle | None) -> str:
        if context is None:
            return ""
        lines = [
            "Evidence schema:",
            "- sources: provenance records for retrieved evidence units with section/page scope, compact payload content, and identifiers.",
            "- key_values: normalized factual values derived from text or tables, each tied to a source_number.",
            "- maintenance_entries: task-centered maintenance records with interval, component, notes, and explicit references.",
            "- tables: first-class table evidence with headers, normalized row objects, table type, and row-level provenance.",
            "- structured_entities: typed entities with their direct fields only.",
            "- relationship_edges: explicit graph edges linking source entities to related target entities, including direction, status, confidence, and target fields.",
            "- relationship_families: grouped local semantic neighborhoods built around one anchor entity and its related edges.",
            "- source_families: anchor-centered source families that separate direct, supporting, contextual, and table-bearing evidence.",
            "- section_topology: section-level evidence topology with parent scope, page span, and role distribution.",
        ]
        return "\n".join(lines) + "\n\n"
