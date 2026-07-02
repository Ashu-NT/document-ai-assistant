from __future__ import annotations

from src.application.langgraph.reflection.prompts.reflection_prompt_version import (
    REFLECTION_PROMPT_VERSION,
)


def _format_chunk_summaries(
    chunks: list[dict[str, object]],
    *,
    limit: int = 6,
) -> str:
    lines: list[str] = []
    for index, chunk in enumerate(chunks[:limit], start=1):
        section_path = chunk.get("section_path") or []
        section_label = (
            " > ".join(str(part) for part in section_path)
            if isinstance(section_path, list) and section_path
            else "-"
        )
        source = chunk.get("source") or {}
        page_start = source.get("page_start") if isinstance(source, dict) else None
        score = chunk.get("score")
        content = " ".join(str(chunk.get("content") or "").split())
        preview = content[:280] + ("..." if len(content) > 280 else "")
        score_text = (
            score
            if isinstance(score, (int, float)) and not isinstance(score, bool)
            else "-"
        )
        lines.append(
            "\n".join(
                [
                    f"- chunk_id: {chunk.get('chunk_id') or '-'}",
                    f"  chunk_type: {chunk.get('chunk_type') or '-'}",
                    f"  section_path: {section_label}",
                    f"  page_start: {page_start if page_start is not None else '-'}",
                    f"  score: {score_text}",
                    f"  preview: {preview or '-'}",
                ]
            )
        )
    if not lines:
        return "- none"
    return "\n".join(lines)


class ReflectionPromptBuilder:
    def build(
        self,
        *,
        original_user_question: str,
        selected_document_id: str | None,
        selected_document_title: str | None,
        answer_intent: str | None,
        generated_answer: str,
        approved_chunk_summaries: list[dict[str, object]],
        rejected_chunk_summaries: list[dict[str, object]],
        citations: list[dict[str, object]],
        context_document_ids: list[str],
        reflection_attempt_count: int,
        retry_count: int,
    ) -> str:
        citation_text = "\n".join(
            f"- {citation.get('chunk_id') or '-'} | {citation.get('section_title') or '-'} | page {((citation.get('source') or {}).get('page_start') if isinstance(citation.get('source'), dict) else '-')}"
            for citation in citations[:8]
            if isinstance(citation, dict)
        ) or "- none"
        maintenance_interval_review = _is_maintenance_interval_review(
            question=original_user_question,
            answer_intent=answer_intent,
        )

        extra_rules: list[str] = []
        if maintenance_interval_review:
            extra_rules.extend(
                [
                    "Maintenance interval review rules:",
                    "- The user is asking for maintenance intervals/frequencies, not general technical specifications.",
                    "- ACCEPT if the answer is grounded and complete.",
                    "- ACCEPT_WITH_LIMITATIONS if the answer is grounded but may be incomplete.",
                    "- Valid interval evidence includes values such as daily, weekly, monthly, yearly, annually, every X hours, every X months, 500 h, 1000 h, 2000 h, 4000 h, 8000 h, 12000 h, or similar scheduled maintenance frequencies.",
                    "- Reject the answer if it mainly contains unrelated specifications such as voltage, power, pump type, tank capacity, nominal speed, dimensions, serial number, model number, or installation data.",
                    "- Reject the answer if it describes maintenance generally but does not state when or how often tasks must be performed.",
                    "- If the selected document is already fixed and approved chunks contain maintenance interval evidence, do not choose CLARIFY.",
                    "- If approved chunks contain useful equipment context but no interval/frequency evidence, choose RETRIEVE_AGAIN.",
                    "- For RETRIEVE_AGAIN, write a focused retry_query using the original question plus terms such as maintenance schedule, service interval, inspection interval, periodic maintenance, preventive maintenance, maintenance table, or intervals.",
                    "- If retry attempts are exhausted but grounded maintenance interval evidence exists, choose ACCEPT_WITH_LIMITATIONS.",
                    "- Do not choose FAIL if grounded maintenance interval evidence exists in the selected document.",
                    "",
                ]
            )

        return "\n".join(
            [
                f"Reflection prompt version: {REFLECTION_PROMPT_VERSION}",
                "You are reviewing a document-grounded answer.",
                "You are not answering the user.",
                "Return JSON only.",
                "Decide whether the answer should be accepted, accepted with limitations, retried, clarified, or failed.",
                "ACCEPT if the answer is grounded and complete.",
                "ACCEPT_WITH_LIMITATIONS if the answer is grounded but may be incomplete.",
                "RETRIEVE_AGAIN when the answer is missing specific evidence that may exist elsewhere in the selected document.",
                "CLARIFY only when the user question is ambiguous and cannot be answered by retrieval.",
                "FAIL only when the answer cannot be grounded after available retrieval attempts or the evidence clearly does not contain the requested information.",
                "If retrying, write a retrieval query based only on the original user question and missing evidence.",
                "Do not invent new tasks.",
                "Do not include facts not present in evidence.",
                "Do not discard existing useful evidence.",
                "If clarification is needed, write one clear clarification question.",
                "",
                *extra_rules,
                "JSON schema:",
                '{',
                '  "decision": "ACCEPT | ACCEPT_WITH_LIMITATIONS | RETRIEVE_AGAIN | CLARIFY | FAIL",',
                '  "confidence": 0.0,',
                '  "reason": "string",',
                '  "retry_query": "string or null",',
                '  "clarification_question": "string or null",',
                '  "missing_information": ["string"]',
                '}',
                "",
                f"Original user question: {original_user_question}",
                f"Selected document title: {selected_document_title or '-'}",
                f"Answer intent: {answer_intent or '-'}",
                f"Reflection attempt count: {reflection_attempt_count}",
                f"Retry count: {retry_count}",
                (
                    f"Context document ids: {', '.join(context_document_ids)}"
                    if context_document_ids and not maintenance_interval_review
                    else "Context document ids: -"
                ),
                "",
                "Generated answer:",
                generated_answer or "-",
                "",
                "Approved chunk summaries:",
                _format_chunk_summaries(approved_chunk_summaries),
                "",
                "Rejected chunk summaries:",
                _format_chunk_summaries(rejected_chunk_summaries),
                "",
                "Citations:",
                citation_text,
            ]
        )


def _is_maintenance_interval_review(
    *,
    question: str,
    answer_intent: str | None,
) -> bool:
    normalized_question = question.lower()
    normalized_intent = (answer_intent or "").lower()
    if "maintenance_summary" not in normalized_intent and "maintenance" not in normalized_question:
        return False
    return any(
        marker in normalized_question
        for marker in (
            "maintenance interval",
            "maintenance intervals",
            "service interval",
            "inspection interval",
            "maintenance schedule",
            "how often",
        )
    )
