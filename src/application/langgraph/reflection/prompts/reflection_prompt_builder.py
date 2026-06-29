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
        lines.append(
            "\n".join(
                [
                    f"- chunk_id: {chunk.get('chunk_id') or '-'}",
                    f"  chunk_type: {chunk.get('chunk_type') or '-'}",
                    f"  section_path: {section_label}",
                    f"  page_start: {page_start if page_start is not None else '-'}",
                    f"  score: {score if isinstance(score, int | float) else '-'}",
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

        return "\n".join(
            [
                f"Reflection prompt version: {REFLECTION_PROMPT_VERSION}",
                "You are reviewing a document-grounded answer.",
                "You are not answering the user.",
                "Return JSON only.",
                "Decide whether the answer should be accepted, retried, clarified, or failed.",
                "If retrying, write a retrieval query based only on the original user question and missing evidence.",
                "Do not invent new tasks.",
                "Do not include facts not present in evidence.",
                "Do not discard existing useful evidence.",
                "If clarification is needed, write one clear clarification question.",
                "",
                "JSON schema:",
                '{',
                '  "decision": "ACCEPT | RETRIEVE_AGAIN | CLARIFY | FAIL",',
                '  "confidence": 0.0,',
                '  "reason": "string",',
                '  "retry_query": "string or null",',
                '  "clarification_question": "string or null",',
                '  "missing_information": ["string"]',
                '}',
                "",
                f"Original user question: {original_user_question}",
                f"Selected document id: {selected_document_id or '-'}",
                f"Selected document title: {selected_document_title or '-'}",
                f"Answer intent: {answer_intent or '-'}",
                f"Reflection attempt count: {reflection_attempt_count}",
                f"Retry count: {retry_count}",
                f"Context document ids: {', '.join(context_document_ids) if context_document_ids else '-'}",
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
