from __future__ import annotations

from typing import Any

from src.application.workflows.shared.maintenance_signal_detection import (
    mentions_maintenance_interval,
)


class MaintenanceEvidenceRelevanceDetector:
    @classmethod
    def has_relevant_evidence(
        cls,
        *,
        question: str,
        answer_intent: str | None,
        approved_chunks: list[dict[str, Any]],
        selected_document_id: str | None,
    ) -> bool:
        if not cls.is_maintenance_interval_question(
            question=question.lower(),
            answer_intent=(answer_intent or "").lower(),
        ):
            return False
        for chunk in approved_chunks:
            if not isinstance(chunk, dict):
                continue
            if (
                selected_document_id
                and chunk.get("document_id")
                and str(chunk.get("document_id")) != selected_document_id
            ):
                continue
            chunk_type = str(chunk.get("chunk_type") or "").strip().lower()
            if chunk_type == "maintenance_interval":
                return True
            content = str(chunk.get("content") or "").lower()
            if not content:
                continue
            if (
                "maintenance" in content
                and any(
                    marker in content
                    for marker in (
                        "interval",
                        "operating hours",
                        "daily",
                        "weekly",
                        "monthly",
                        "quarterly",
                        "annual",
                        "annually",
                        "schedule",
                        "preventive maintenance",
                    )
                )
            ):
                return True
        return False

    @classmethod
    def is_maintenance_interval_question(
        cls,
        *,
        question: str,
        answer_intent: str,
    ) -> bool:
        if "maintenance_summary" not in answer_intent and "maintenance" not in question:
            return False
        return cls.question_requests_maintenance_intervals(question)

    @staticmethod
    def question_requests_maintenance_intervals(question: str) -> bool:
        return mentions_maintenance_interval(question)

    @staticmethod
    def contains_unrelated_specifications(answer: str) -> bool:
        return any(
            marker in answer
            for marker in (
                "voltage",
                "installed power",
                "pump type",
                "serial number",
                "tank capacity",
                "nominal speed",
                "rpm",
            )
        )

    @staticmethod
    def has_interval_structure(answer: str) -> bool:
        return any(
            marker in answer
            for marker in (
                "interval",
                "frequency",
                "operating hours",
                "daily",
                "weekly",
                "monthly",
                "quarterly",
                "annual",
                "annually",
                "every ",
            )
        )
