from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Sequence

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.domain.common import ChunkType
from src.domain.retrieval.retrieved_chunk import RetrievedChunk

_SPECIFICATION_TERMS = (
    "specification",
    "specifications",
    "spec",
    "technical data",
    "technical details",
    "pressure",
    "temperature",
    "size",
    "dimension",
    "rating",
    "capacity",
    "voltage",
    "current",
    "material",
    "power",
    "dn ",
)
_MAINTENANCE_TERMS = (
    "maintenance",
    "maintenance task",
    "maintenance tasks",
    "maintenance schedule",
    "maintenance interval",
    "maintenance intervals",
    "preventive maintenance",
    "service interval",
    "service schedule",
    "inspection schedule",
    "routine maintenance",
    "maintenance checklist",
    "interval",
    "service",
    "inspection",
    "oil change",
    "lubricate",
    "lubrication",
    "grease",
    "overhaul",
)
_PROCEDURE_TERMS = (
    "how to",
    "how do i",
    "how can i",
    "procedure",
    "steps",
    "step",
    "install",
    "disassemble",
    "assemble",
    "remove",
    "replace",
    "start",
    "stop",
    "operate",
    "shutdown",
    "commission",
    "commissioning",
    "connect",
    "configure",
)
_SAFETY_TERMS = ("warning", "danger", "safety", "caution", "hazard")
_TROUBLESHOOTING_TERMS = (
    "fault",
    "error",
    "alarm",
    "problem",
    "cause",
    "remedy",
    "troubleshoot",
    "symptom",
)
_CERTIFICATION_TERMS = (
    "certificate",
    "approval",
    "inspection",
    "surveyor",
    "compliance",
    "lr",
    "atex",
    "iecex",
)
_IDENTIFIER_TERMS = (
    "part number",
    "serial number",
    "order code",
    "order number",
    "model number",
    "model",
    "tag",
    "drawing number",
    " id ",
)
_TABLE_TERMS = ("table", "list", "schedule", "matrix")
_DOCUMENT_SUMMARY_TERMS = (
    "summary",
    "summarize",
    "overview",
    "what is in",
    "what's in",
    "what does this document contain",
    "what does the document contain",
)
_MAINTENANCE_SUMMARY_PHRASES = (
    "maintenance task",
    "maintenance tasks",
    "maintenance schedule",
    "maintenance interval",
    "maintenance intervals",
    "preventive maintenance",
    "service interval",
    "service schedule",
    "inspection schedule",
    "routine maintenance",
    "maintenance checklist",
)
_EXPLICIT_PROCEDURE_PHRASES = (
    "how to",
    "how do i",
    "how can i",
    "show steps",
    "show the steps",
    "what are the steps",
    "procedure for",
    "steps for",
)
_TECHNICAL_VALUE_PATTERN = re.compile(
    r"\b("
    r"\d+(\.\d+)?\s*(bar|mm|cm|m|kw|w|v|a|hz|dn|pcs|pc)\b"
    r"|dn\s*\d+\b"
    r"|design pressure\b"
    r"|test pressure\b"
    r"|working pressure\b"
    r")",
    re.IGNORECASE,
)
_STEP_PATTERN = re.compile(r"^\s*(\d+[\).\s]|[-*]\s+)", re.MULTILINE)
_IDENTIFIER_VALUE_PATTERN = re.compile(
    r"\b([A-Z]{1,5}\d{1,6}[A-Z0-9-]*|\d{3,}[A-Z0-9-]+)\b"
)
_CHUNK_TYPE_TO_INTENT: dict[ChunkType, AnswerIntent] = {
    ChunkType.TECHNICAL_SPECIFICATION: AnswerIntent.SPECIFICATION_SUMMARY,
    ChunkType.CERTIFICATION_INFO: AnswerIntent.CERTIFICATION_SUMMARY,
    ChunkType.SPARE_PARTS_TABLE: AnswerIntent.TABLE_SUMMARY,
    ChunkType.MAINTENANCE_INTERVAL: AnswerIntent.MAINTENANCE_SUMMARY,
    ChunkType.MAINTENANCE_PROCEDURE: AnswerIntent.PROCEDURE_STEPS,
    ChunkType.OPERATION_INSTRUCTION: AnswerIntent.PROCEDURE_STEPS,
    ChunkType.INSTALLATION_INSTRUCTION: AnswerIntent.PROCEDURE_STEPS,
    ChunkType.SAFETY_WARNING: AnswerIntent.SAFETY_WARNINGS,
    ChunkType.TROUBLESHOOTING: AnswerIntent.TROUBLESHOOTING,
    ChunkType.OVERVIEW: AnswerIntent.DOCUMENT_SUMMARY,
}
_RETRIEVAL_INTENT_TO_ANSWER_INTENT: dict[str, AnswerIntent] = {
    "specification": AnswerIntent.SPECIFICATION_SUMMARY,
    "procedure": AnswerIntent.PROCEDURE_STEPS,
    "troubleshooting": AnswerIntent.TROUBLESHOOTING,
    "safety": AnswerIntent.SAFETY_WARNINGS,
    "table": AnswerIntent.TABLE_SUMMARY,
    "identifier": AnswerIntent.IDENTIFIER_LOOKUP,
    "overview": AnswerIntent.DOCUMENT_SUMMARY,
    "document_exploration": AnswerIntent.DOCUMENT_SUMMARY,
}
_INTENT_PRIORITY: tuple[AnswerIntent, ...] = (
    AnswerIntent.SPECIFICATION_SUMMARY,
    AnswerIntent.MAINTENANCE_SUMMARY,
    AnswerIntent.PROCEDURE_STEPS,
    AnswerIntent.SAFETY_WARNINGS,
    AnswerIntent.TROUBLESHOOTING,
    AnswerIntent.CERTIFICATION_SUMMARY,
    AnswerIntent.IDENTIFIER_LOOKUP,
    AnswerIntent.TABLE_SUMMARY,
    AnswerIntent.DOCUMENT_SUMMARY,
    AnswerIntent.GENERAL,
)


@dataclass(slots=True, frozen=True)
class AnswerIntentDecision:
    intent: AnswerIntent
    confidence: float
    reason: str
    matched_signals: list[str]


class AnswerIntentAnalyzer:
    def analyze(
        self,
        *,
        question: str,
        retrieval_intent: str | None = None,
        chunk_type_preferences: Sequence[ChunkType] | None = None,
        approved_chunks: Sequence[RetrievedChunk] | None = None,
        legacy_query_intent: str | None = None,
        route: str | None = None,
    ) -> AnswerIntentDecision:
        normalized_question = self._normalize(question)
        chunks = list(approved_chunks or [])
        scores = {intent: 0 for intent in _INTENT_PRIORITY}
        matched = {intent: [] for intent in _INTENT_PRIORITY}

        self._apply_question_signals(normalized_question, scores, matched)
        self._apply_route_signal(route, scores, matched)
        self._apply_retrieval_intent_signal(
            retrieval_intent or legacy_query_intent,
            scores,
            matched,
        )
        self._apply_chunk_type_preference_signal(
            chunk_type_preferences or [],
            scores,
            matched,
        )
        self._apply_chunk_content_signal(chunks, scores, matched)
        self._apply_maintenance_procedure_disambiguation(
            normalized_question,
            scores,
            matched,
        )

        best_intent = self._pick_intent(scores)
        if scores[best_intent] <= 0:
            return AnswerIntentDecision(
                intent=AnswerIntent.GENERAL,
                confidence=0.55,
                reason="No strong answer-format signals were detected.",
                matched_signals=[],
            )

        confidence = self._confidence(scores, best_intent)
        matched_signals = matched[best_intent]
        signal_origin = "question" if any(
            signal.startswith("question:") for signal in matched_signals
        ) else "retrieval/context"
        return AnswerIntentDecision(
            intent=best_intent,
            confidence=confidence,
            reason=(
                f"Resolved from {signal_origin} signals with supporting retrieval evidence."
            ),
            matched_signals=matched_signals,
        )

    @staticmethod
    def _normalize(value: str | None) -> str:
        return " ".join((value or "").strip().lower().split())

    def _apply_question_signals(
        self,
        question: str,
        scores: dict[AnswerIntent, int],
        matched: dict[AnswerIntent, list[str]],
    ) -> None:
        self._score_terms(
            question,
            AnswerIntent.SPECIFICATION_SUMMARY,
            _SPECIFICATION_TERMS,
            6,
            scores,
            matched,
        )
        self._score_terms(
            question,
            AnswerIntent.MAINTENANCE_SUMMARY,
            _MAINTENANCE_TERMS,
            6,
            scores,
            matched,
        )
        self._score_terms(
            question,
            AnswerIntent.PROCEDURE_STEPS,
            _PROCEDURE_TERMS,
            6,
            scores,
            matched,
        )
        self._score_terms(
            question,
            AnswerIntent.SAFETY_WARNINGS,
            _SAFETY_TERMS,
            6,
            scores,
            matched,
        )
        self._score_terms(
            question,
            AnswerIntent.TROUBLESHOOTING,
            _TROUBLESHOOTING_TERMS,
            6,
            scores,
            matched,
        )
        self._score_terms(
            question,
            AnswerIntent.CERTIFICATION_SUMMARY,
            _CERTIFICATION_TERMS,
            6,
            scores,
            matched,
        )
        self._score_terms(
            question,
            AnswerIntent.IDENTIFIER_LOOKUP,
            _IDENTIFIER_TERMS,
            6,
            scores,
            matched,
        )
        self._score_terms(
            question,
            AnswerIntent.TABLE_SUMMARY,
            _TABLE_TERMS,
            5,
            scores,
            matched,
        )
        self._score_terms(
            question,
            AnswerIntent.DOCUMENT_SUMMARY,
            _DOCUMENT_SUMMARY_TERMS,
            5,
            scores,
            matched,
        )
        if "how often" in question:
            scores[AnswerIntent.MAINTENANCE_SUMMARY] += 3
            matched[AnswerIntent.MAINTENANCE_SUMMARY].append("question:how often")
        if any(phrase in question for phrase in _MAINTENANCE_SUMMARY_PHRASES):
            scores[AnswerIntent.MAINTENANCE_SUMMARY] += 4
            matched[AnswerIntent.MAINTENANCE_SUMMARY].append(
                "question:maintenance_summary_phrase"
            )
        if "what is in" in question or "what's in" in question:
            scores[AnswerIntent.DOCUMENT_SUMMARY] += 2
            matched[AnswerIntent.DOCUMENT_SUMMARY].append("question:what is in")

    def _apply_route_signal(
        self,
        route: str | None,
        scores: dict[AnswerIntent, int],
        matched: dict[AnswerIntent, list[str]],
    ) -> None:
        if route == "document_exploration":
            scores[AnswerIntent.DOCUMENT_SUMMARY] += 5
            matched[AnswerIntent.DOCUMENT_SUMMARY].append("route:document_exploration")

    def _apply_retrieval_intent_signal(
        self,
        retrieval_intent: str | None,
        scores: dict[AnswerIntent, int],
        matched: dict[AnswerIntent, list[str]],
    ) -> None:
        normalized = self._normalize(retrieval_intent)
        answer_intent = _RETRIEVAL_INTENT_TO_ANSWER_INTENT.get(normalized)
        if answer_intent is None:
            return
        scores[answer_intent] += 4
        matched[answer_intent].append(f"retrieval:{normalized}")

    def _apply_chunk_type_preference_signal(
        self,
        chunk_types: Sequence[ChunkType],
        scores: dict[AnswerIntent, int],
        matched: dict[AnswerIntent, list[str]],
    ) -> None:
        for chunk_type in chunk_types:
            answer_intent = _CHUNK_TYPE_TO_INTENT.get(chunk_type)
            if answer_intent is None:
                continue
            scores[answer_intent] += 2
            matched[answer_intent].append(f"chunk_type:{chunk_type.value}")

    def _apply_chunk_content_signal(
        self,
        chunks: Sequence[RetrievedChunk],
        scores: dict[AnswerIntent, int],
        matched: dict[AnswerIntent, list[str]],
    ) -> None:
        if not chunks:
            return

        normalized_contents = [self._normalize(chunk.content) for chunk in chunks]
        if any(self._has_technical_values(chunk.content) for chunk in chunks):
            scores[AnswerIntent.SPECIFICATION_SUMMARY] += 3
            matched[AnswerIntent.SPECIFICATION_SUMMARY].append(
                "context:technical_values"
            )
        if any(self._looks_like_table(chunk.content) for chunk in chunks):
            scores[AnswerIntent.TABLE_SUMMARY] += 2
            matched[AnswerIntent.TABLE_SUMMARY].append("context:table_like")
        if any(self._contains_identifier_values(chunk.content) for chunk in chunks):
            scores[AnswerIntent.IDENTIFIER_LOOKUP] += 2
            matched[AnswerIntent.IDENTIFIER_LOOKUP].append("context:identifier_values")
        if any(self._contains_procedure_steps(chunk.content) for chunk in chunks):
            scores[AnswerIntent.PROCEDURE_STEPS] += 2
            matched[AnswerIntent.PROCEDURE_STEPS].append("context:ordered_steps")
        if any("maintenance" in content for content in normalized_contents):
            scores[AnswerIntent.MAINTENANCE_SUMMARY] += 2
            matched[AnswerIntent.MAINTENANCE_SUMMARY].append("context:maintenance_text")
        if any("warning" in content for content in normalized_contents):
            scores[AnswerIntent.SAFETY_WARNINGS] += 2
            matched[AnswerIntent.SAFETY_WARNINGS].append("context:safety_text")
        if any(
            any(term in content for term in ("fault", "cause", "remedy", "troubleshooting"))
            for content in normalized_contents
        ):
            scores[AnswerIntent.TROUBLESHOOTING] += 2
            matched[AnswerIntent.TROUBLESHOOTING].append(
                "context:troubleshooting_text"
            )
        if any(
            any(
                term in content
                for term in ("certificate", "approval", "inspection", "compliance")
            )
            for content in normalized_contents
        ):
            scores[AnswerIntent.CERTIFICATION_SUMMARY] += 2
            matched[AnswerIntent.CERTIFICATION_SUMMARY].append(
                "context:certification_text"
            )

    def _apply_maintenance_procedure_disambiguation(
        self,
        question: str,
        scores: dict[AnswerIntent, int],
        matched: dict[AnswerIntent, list[str]],
    ) -> None:
        if not self._looks_like_maintenance_question(question):
            return
        if self._looks_like_explicit_procedure_question(question):
            scores[AnswerIntent.PROCEDURE_STEPS] += 2
            matched[AnswerIntent.PROCEDURE_STEPS].append(
                "question:explicit_procedure_request"
            )
            return
        scores[AnswerIntent.MAINTENANCE_SUMMARY] += 4
        matched[AnswerIntent.MAINTENANCE_SUMMARY].append(
            "question:maintenance_over_procedure"
        )

    @staticmethod
    def _score_terms(
        text: str,
        intent: AnswerIntent,
        terms: Iterable[str],
        weight: int,
        scores: dict[AnswerIntent, int],
        matched: dict[AnswerIntent, list[str]],
    ) -> None:
        for term in terms:
            if term in text:
                scores[intent] += weight
                matched[intent].append(f"question:{term}")

    @staticmethod
    def _has_technical_values(content: str) -> bool:
        return bool(_TECHNICAL_VALUE_PATTERN.search(content))

    @staticmethod
    def _contains_procedure_steps(content: str) -> bool:
        normalized = content.lower()
        return bool(_STEP_PATTERN.search(content)) or any(
            marker in normalized
            for marker in ("step 1", "step 2", "first,", "then ", "next ", "finally")
        )

    @staticmethod
    def _contains_identifier_values(content: str) -> bool:
        normalized = content.lower()
        if any(
            marker in normalized
            for marker in (
                "serial number",
                "part number",
                "order code",
                "model number",
                "tag no",
                "drawing number",
            )
        ):
            return True
        return bool(_IDENTIFIER_VALUE_PATTERN.search(content))

    @staticmethod
    def _looks_like_table(content: str) -> bool:
        return sum(1 for line in content.splitlines() if "|" in line) >= 2

    @staticmethod
    def _looks_like_maintenance_question(question: str) -> bool:
        return "maintenance" in question or any(
            phrase in question for phrase in _MAINTENANCE_SUMMARY_PHRASES
        )

    @staticmethod
    def _looks_like_explicit_procedure_question(question: str) -> bool:
        return any(phrase in question for phrase in _EXPLICIT_PROCEDURE_PHRASES)

    @staticmethod
    def _pick_intent(scores: dict[AnswerIntent, int]) -> AnswerIntent:
        best_score = max(scores.values())
        candidates = [
            intent for intent in _INTENT_PRIORITY if scores.get(intent, 0) == best_score
        ]
        return candidates[0] if candidates else AnswerIntent.GENERAL

    @staticmethod
    def _confidence(
        scores: dict[AnswerIntent, int],
        best_intent: AnswerIntent,
    ) -> float:
        best = scores[best_intent]
        runner_up = max(
            (
                score
                for intent, score in scores.items()
                if intent != best_intent
            ),
            default=0,
        )
        margin = best - runner_up
        if best >= 10 and margin >= 3:
            return 0.95
        if best >= 8 and margin >= 2:
            return 0.9
        if best >= 6:
            return 0.82
        if best >= 4:
            return 0.72
        return 0.62
