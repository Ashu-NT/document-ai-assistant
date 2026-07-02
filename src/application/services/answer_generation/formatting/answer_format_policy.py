from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)

if TYPE_CHECKING:
    from src.application.workflows.question_answering.answer_context.structured_answer_context import (
        StructuredAnswerContext,
    )


@dataclass(slots=True, frozen=True)
class AnswerFormatPolicy:
    intent: AnswerIntent
    preferred_format: str
    include_table: bool
    include_bullets: bool
    include_steps: bool
    include_sources_inline: bool
    max_bullets: int | None
    response_label: str
    instruction_lines: tuple[str, ...]

    @classmethod
    def for_intent(cls, intent: AnswerIntent) -> "AnswerFormatPolicy":
        return _POLICIES.get(intent, _POLICIES[AnswerIntent.GENERAL])

    @classmethod
    def resolve(
        cls,
        *,
        intent: AnswerIntent,
        structured_context: "StructuredAnswerContext | None" = None,
    ) -> "AnswerFormatPolicy":
        _ = structured_context
        return cls.for_intent(intent)


_POLICIES: dict[AnswerIntent, AnswerFormatPolicy] = {
    AnswerIntent.SPECIFICATION_SUMMARY: AnswerFormatPolicy(
        intent=AnswerIntent.SPECIFICATION_SUMMARY,
        preferred_format="structured_bullets",
        include_table=True,
        include_bullets=True,
        include_steps=False,
        include_sources_inline=False,
        max_bullets=8,
        response_label="Available specifications",
        instruction_lines=(
            "The user is asking for technical specifications.",
            "Extract and summarize available technical values from the provided sources.",
            "Do not say that specifications are missing if the sources contain technical values such as pressure, temperature, size, quantity, dimensions, rating, capacity, voltage, current, material, inspection date, or working pressure.",
            "If only partial specifications are available, say 'Available specifications' and list them.",
            "Use only the provided sources.",
        ),
    ),
    AnswerIntent.MAINTENANCE_SUMMARY: AnswerFormatPolicy(
        intent=AnswerIntent.MAINTENANCE_SUMMARY,
        preferred_format="maintenance_numbered_entries",
        include_table=False,
        include_bullets=False,
        include_steps=False,
        include_sources_inline=False,
        max_bullets=None,
        response_label="Maintenance Tasks",
        instruction_lines=(
            "The user is asking for maintenance information.",
            "Summarize all maintenance tasks from the provided sources.",
            "Use the heading 'Maintenance Tasks'.",
            "Use numbered entries only. Do not output markdown tables.",
            "Answer only maintenance intervals, frequencies, and directly related maintenance tasks.",
            "Each numbered entry must cover one maintenance task only.",
            "For each task include Description, Interval / Frequency, Component, and Reference.",
            "Merge duplicate maintenance tasks that describe the same activity.",
            "Prefer document order unless the document explicitly presents a maintenance interval order.",
            "Preserve intervals, units, and operating-hour values exactly as written in the sources.",
            "Preserve page references and section paths when they are available.",
            "If an interval is not explicitly stated, write 'Not specified'.",
            "If a component is not explicitly stated, write 'Not specified'.",
            "Do not output placeholders such as X, -, N/A, or Unknown.",
            "Do not invent intervals, tasks, components, or frequencies.",
            "Do not include unrelated technical specifications such as voltage, power, pump type, serial number, tank capacity, installed power, or nominal speed unless the user explicitly asked for specifications.",
            "Keep terminology from the document.",
            "Use only the provided sources.",
        ),
    ),
    AnswerIntent.PROCEDURE_STEPS: AnswerFormatPolicy(
        intent=AnswerIntent.PROCEDURE_STEPS,
        preferred_format="numbered_steps",
        include_table=False,
        include_bullets=False,
        include_steps=True,
        include_sources_inline=False,
        max_bullets=None,
        response_label="Procedure",
        instruction_lines=(
            "The user is asking for a procedure.",
            "Return numbered steps only if steps are explicitly present in the provided sources.",
            "Preserve sequence and warnings.",
            "Do not invent missing steps.",
        ),
    ),
    AnswerIntent.SAFETY_WARNINGS: AnswerFormatPolicy(
        intent=AnswerIntent.SAFETY_WARNINGS,
        preferred_format="warning_list",
        include_table=False,
        include_bullets=True,
        include_steps=False,
        include_sources_inline=False,
        max_bullets=8,
        response_label="Safety warnings",
        instruction_lines=(
            "The user is asking for safety information.",
            "List only explicit warnings, cautions, or dangers from the provided sources.",
            "Do not invent additional safety advice.",
        ),
    ),
    AnswerIntent.TROUBLESHOOTING: AnswerFormatPolicy(
        intent=AnswerIntent.TROUBLESHOOTING,
        preferred_format="fault_cause_remedy",
        include_table=False,
        include_bullets=True,
        include_steps=False,
        include_sources_inline=False,
        max_bullets=8,
        response_label="Troubleshooting information",
        instruction_lines=(
            "The user is asking for troubleshooting information.",
            "Summarize the explicit fault, cause, and remedy details from the provided sources.",
            "Do not invent diagnoses or remedies.",
        ),
    ),
    AnswerIntent.CERTIFICATION_SUMMARY: AnswerFormatPolicy(
        intent=AnswerIntent.CERTIFICATION_SUMMARY,
        preferred_format="fact_summary",
        include_table=True,
        include_bullets=True,
        include_steps=False,
        include_sources_inline=False,
        max_bullets=8,
        response_label="Certification facts",
        instruction_lines=(
            "The user is asking about certification or inspection information.",
            "Summarize certificate facts such as certificate number, inspection date, surveyor, approval, compliance, and remarks when present.",
            "Use only the provided sources.",
        ),
    ),
    AnswerIntent.IDENTIFIER_LOOKUP: AnswerFormatPolicy(
        intent=AnswerIntent.IDENTIFIER_LOOKUP,
        preferred_format="fact_list",
        include_table=False,
        include_bullets=True,
        include_steps=False,
        include_sources_inline=False,
        max_bullets=12,
        response_label="Requested identifiers",
        instruction_lines=(
            "The user is asking for identifiers or codes.",
            "Return only explicit identifier values that are present in the provided sources.",
            "Do not summarize the system, the procedure, or the document.",
            "Group identifiers by type such as part number, serial number, model number, or order code when available.",
            "Prefer exact values over interpretation and do not paraphrase identifier strings.",
            "If the question asks for a subset such as serial numbers or part numbers, return only that subset.",
        ),
    ),
    AnswerIntent.TABLE_SUMMARY: AnswerFormatPolicy(
        intent=AnswerIntent.TABLE_SUMMARY,
        preferred_format="table_summary",
        include_table=True,
        include_bullets=True,
        include_steps=False,
        include_sources_inline=False,
        max_bullets=8,
        response_label="Table summary",
        instruction_lines=(
            "The user is asking about table or list content, such as a spare "
            "parts list.",
            "Summarize the relevant rows or entries from the provided sources.",
            "Preserve exact values when they are present.",
            "Do not say that no spare parts list or table was found if the "
            "provided sources include spare parts table content or a section "
            "titled 'Spare Parts List' or 'Spare Parts'.",
            "If a complete table cannot be reconstructed, list the available "
            "rows or entries instead of denying that a table or list exists.",
            "For CLI-style output, group rows by section and page and present "
            "them as a readable list instead of a wide markdown table, unless "
            "the user explicitly asks for a markdown table or export format.",
            "If some row fields are missing from the sources, omit the field "
            "or write '-' rather than inventing a value.",
        ),
    ),
    AnswerIntent.DOCUMENT_SUMMARY: AnswerFormatPolicy(
        intent=AnswerIntent.DOCUMENT_SUMMARY,
        preferred_format="summary_paragraph",
        include_table=False,
        include_bullets=True,
        include_steps=False,
        include_sources_inline=False,
        max_bullets=6,
        response_label="Document summary",
        instruction_lines=(
            "The user is asking for a document-level summary or overview.",
            "Summarize only what is explicitly covered by the provided sources.",
            "Do not infer coverage that is not present in the evidence.",
        ),
    ),
    AnswerIntent.GENERAL: AnswerFormatPolicy(
        intent=AnswerIntent.GENERAL,
        preferred_format="concise_paragraph",
        include_table=False,
        include_bullets=False,
        include_steps=False,
        include_sources_inline=False,
        max_bullets=None,
        response_label="Grounded answer",
        instruction_lines=(
            "Answer concisely using only the provided sources.",
            "If the sources only partially answer the question, clearly state what is available.",
        ),
    ),
}
