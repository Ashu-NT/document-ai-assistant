from __future__ import annotations

from src.application.prompts.answer_generation.prompt_context.models.prompt_section_topology_view import (
    PromptSectionTopologyView,
)
from src.application.prompts.answer_generation.prompt_context.models.prompt_source_family_view import (
    PromptSourceFamilyView,
)
from src.application.prompts.answer_generation.prompt_context.models.prompt_source_view import (
    PromptSourceView,
)
from src.application.prompts.answer_generation.prompt_context.models.prompt_table_view import (
    PromptTableView,
)
from src.application.prompts.answer_generation.prompt_context.topology.prompt_evidence_role_assigner import (
    PromptEvidenceRoleAssigner,
)
from src.application.prompts.answer_generation.prompt_context.topology.prompt_section_topology_builder import (
    PromptSectionTopologyBuilder,
)
from src.application.prompts.answer_generation.prompt_context.topology.prompt_source_family_builder import (
    PromptSourceFamilyBuilder,
)


class PromptEvidenceTopologyBuilder:
    def __init__(
        self,
        prompt_evidence_role_assigner: PromptEvidenceRoleAssigner | None = None,
        prompt_source_family_builder: PromptSourceFamilyBuilder | None = None,
        prompt_section_topology_builder: PromptSectionTopologyBuilder | None = None,
    ) -> None:
        self.prompt_evidence_role_assigner = (
            prompt_evidence_role_assigner or PromptEvidenceRoleAssigner()
        )
        self.prompt_source_family_builder = (
            prompt_source_family_builder or PromptSourceFamilyBuilder()
        )
        self.prompt_section_topology_builder = (
            prompt_section_topology_builder or PromptSectionTopologyBuilder()
        )

    def build(
        self,
        *,
        answer_intent_value: str,
        sources: list[PromptSourceView],
        tables: list[PromptTableView],
    ) -> tuple[list[PromptSourceFamilyView], list[PromptSectionTopologyView]]:
        table_source_numbers = {table.source_number for table in tables}
        roles_by_source_number = self.prompt_evidence_role_assigner.assign(
            answer_intent_value=answer_intent_value,
            sources=sources,
            table_source_numbers=table_source_numbers,
        )
        source_families = self.prompt_source_family_builder.build(
            sources=sources,
            roles_by_source_number=roles_by_source_number,
            table_source_numbers=table_source_numbers,
        )
        section_topology = self.prompt_section_topology_builder.build(
            sources=sources,
            roles_by_source_number=roles_by_source_number,
            table_source_numbers=table_source_numbers,
        )
        return source_families, section_topology
