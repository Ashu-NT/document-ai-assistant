from typing import TYPE_CHECKING

from src.application.prompts.answer_generation.maintenance_prompt_context_formatter import (
    MaintenancePromptContextFormatter,
)
from src.application.prompts.answer_generation.answer_prompt_version import (
    ANSWER_PROMPT_VERSION,
)
from src.application.prompts.common import (
    ANSWER_GROUNDING_RULES,
    PromptMetadata,
)
from src.domain.retrieval.retrieved_chunk import RetrievedChunk

if TYPE_CHECKING:
    from src.application.services.answer_generation.answer_generation_request import (
        AnswerGenerationRequest,
    )


class AnswerPromptBuilder:
    prompt_version = ANSWER_PROMPT_VERSION
    metadata = PromptMetadata(
        name="answer_generation",
        version=ANSWER_PROMPT_VERSION,
        task_type="answer_generation",
        model_type="llm",
        description="Grounded answer generation from retrieved document chunks.",
    )

    def __init__(
        self,
        maintenance_context_formatter: MaintenancePromptContextFormatter | None = None,
    ) -> None:
        self.maintenance_context_formatter = (
            maintenance_context_formatter or MaintenancePromptContextFormatter()
        )

    def build(self, request: "AnswerGenerationRequest") -> str:
        source_blocks = self._raw_source_block(request)

        return (
            f"{ANSWER_GROUNDING_RULES}\n\n"
            f"{self._intent_block(request)}"
            f"{self._format_policy_block(request)}"
            f"Question: {request.question}\n\n"
            f"{self._identifier_block(request)}"
            f"{self._organized_context_block(request)}"
            "Raw sources:\n"
            f"{source_blocks}"
        )

    @staticmethod
    def _identifier_block(request: "AnswerGenerationRequest") -> str:
        identifiers = getattr(request, "resolved_identifiers", None)
        if not identifiers:
            return ""
        lines = ["Resolved identifiers:"]
        for identifier in identifiers:
            type_label = identifier.identifier_type.value.replace("_", " ").title()
            lines.append(
                f"- {type_label}: {identifier.raw_value}"
                f" (normalized: {identifier.normalized_value})"
            )
        return "\n".join(lines) + "\n\n"

    @staticmethod
    def _intent_block(request: "AnswerGenerationRequest") -> str:
        lines: list[str] = []
        if request.answer_intent is not None:
            lines.append(f"Answer intent: {request.answer_intent.value}")
        if request.retrieval_intent:
            lines.append(f"Retrieval intent: {request.retrieval_intent}")
        elif request.query_intent:
            lines.append(f"Legacy query intent: {request.query_intent}")
        if not lines:
            return ""
        return "\n".join(lines) + "\n\n"

    @staticmethod
    def _format_policy_block(request: "AnswerGenerationRequest") -> str:
        policy = request.format_policy
        if policy is None:
            return ""
        lines = [
            "Answer format policy:",
            f"- Preferred format: {policy.preferred_format}",
            f"- Response label: {policy.response_label}",
            f"- Include bullets: {'yes' if policy.include_bullets else 'no'}",
            f"- Include numbered steps: {'yes' if policy.include_steps else 'no'}",
            f"- Include table-like structure: {'yes' if policy.include_table else 'no'}",
        ]
        if policy.max_bullets is not None:
            lines.append(f"- Max bullets: {policy.max_bullets}")
        lines.append("Task instructions:")
        lines.extend(f"- {instruction}" for instruction in policy.instruction_lines)
        return "\n".join(lines) + "\n\n"

    def _organized_context_block(self, request: "AnswerGenerationRequest") -> str:
        context = request.structured_context
        if context is None:
            return ""

        lines = [
            "Organized context:",
            f"- Intent: {context.answer_intent.value}",
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
                lines.append(
                    f"- [SOURCE {item.source_number}] {item.key}: {value}"
                )
        if context.source_groups:
            lines.append("Source groups:")
            for group in context.source_groups:
                source_refs = ", ".join(
                    f"SOURCE {source.source_number}" for source in group.sources
                )
                lines.append(
                    f"- {group.group_name}: {source_refs}"
                )
        if context.section_groups:
            lines.append("Section groups:")
            for group in context.section_groups:
                page_range = self._format_page_bounds(group.page_start, group.page_end)
                source_refs = ", ".join(
                    f"SOURCE {source_number}"
                    for source_number in group.source_numbers
                )
                lines.append(
                    f"- {group.group_name} | Pages: {page_range} | Sources: {source_refs}"
                )
        return "\n".join(lines) + "\n\n"

    def _raw_source_block(self, request: "AnswerGenerationRequest") -> str:
        structured_context = request.structured_context
        if structured_context is not None and structured_context.sources:
            return "\n\n".join(
                self._format_answer_source_block(source)
                for source in structured_context.sources
            )

        return "\n\n".join(
            self._format_source_block(index + 1, chunk)
            for index, chunk in enumerate(request.context_chunks)
        )

    @staticmethod
    def _format_source_block(index: int, chunk: RetrievedChunk) -> str:
        section_path = " > ".join(chunk.section_path) if chunk.section_path else "N/A"
        page_range = AnswerPromptBuilder._format_page_range(chunk)
        document_name = (
            chunk.citation.document_name
            if chunk.citation is not None and chunk.citation.document_name
            else "Current document"
        )

        return (
            f"SOURCE {index}\n"
            f"Document: {document_name}\n"
            f"Section: {section_path}\n"
            f"Pages: {page_range}\n"
            "---\n"
            f"{chunk.content}"
        )

    @staticmethod
    def _format_answer_source_block(source) -> str:
        page_range = AnswerPromptBuilder._format_page_bounds(
            source.page_start,
            source.page_end,
        )
        section_path = source.section_path or "N/A"
        document_title = source.document_title or "Current document"
        return (
            f"SOURCE {source.source_number}\n"
            f"Document: {document_title}\n"
            f"Section: {section_path}\n"
            f"Pages: {page_range}\n"
            "---\n"
            f"{source.content}"
        )

    @staticmethod
    def _format_page_range(chunk: RetrievedChunk) -> str:
        return AnswerPromptBuilder._format_page_bounds(
            chunk.source.page_start,
            chunk.source.page_end,
        )

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
