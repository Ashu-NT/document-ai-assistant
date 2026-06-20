import ast
import json
import re
from typing import Any

from src.application.validation.common import ValidationResult
from src.shared.exceptions import SchemaValidationError

KEY_PATTERN = re.compile(r"[^a-z0-9]+")
LIST_ITEM_PATTERN = re.compile(r"^\s*(?:[-*]+|\d+[\.\)]|[A-Za-z]\))\s*")
THINK_BLOCK_PATTERN = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
CODE_FENCE_PATTERN = re.compile(
    r"```(?:json|javascript|js|python|text)?\s*(.*?)```",
    re.IGNORECASE | re.DOTALL,
)


class ClassificationResponseParser:
    def __init__(self, *, label_aliases: set[str]) -> None:
        self.label_aliases = set(label_aliases)

    def parse(self, response: str) -> dict[str, Any]:
        payload = self._extract_payload(response)
        validation = ValidationResult()

        label = self._coerce_text(payload.get("label"))
        if not label:
            validation.add_issue(
                "label",
                "Classification label is required.",
                "classification.response.label.required",
            )

        raw_confidence = payload.get("confidence_score")
        confidence_score = self._parse_confidence(raw_confidence)
        if confidence_score is None:
            validation.add_issue(
                "confidence_score",
                "Confidence score must be a number between 0 and 1.",
                "classification.response.confidence.invalid",
            )

        validation.raise_if_invalid()

        return {
            "label": label,
            "confidence_score": confidence_score,
            "rationale": self._coerce_text(payload.get("rationale")),
            "evidence": self._coerce_evidence(payload.get("evidence")),
        }

    def _extract_payload(self, response: str) -> dict[str, Any]:
        candidate_texts = self._candidate_texts(response)

        for candidate_text in candidate_texts:
            for raw_candidate in self._candidate_objects(candidate_text):
                payload = self._try_parse_mapping(raw_candidate)
                if payload is not None:
                    return self._normalize_payload(payload)

        for candidate_text in candidate_texts:
            payload = self._parse_key_value_text(candidate_text)
            if payload:
                return payload

        raise SchemaValidationError(
            "Malformed classification response.",
            details={"response": response},
        )

    @staticmethod
    def _candidate_texts(response: str) -> list[str]:
        original = response.strip()
        stripped = THINK_BLOCK_PATTERN.sub("", original).strip()

        candidates: list[str] = []
        for value in [original, stripped]:
            if value and value not in candidates:
                candidates.append(value)

        for value in [original, stripped]:
            for match in CODE_FENCE_PATTERN.findall(value):
                cleaned = str(match).strip()
                if cleaned and cleaned not in candidates:
                    candidates.append(cleaned)

        return candidates

    @staticmethod
    def _candidate_objects(text: str) -> list[str]:
        candidates: list[str] = []
        stripped = text.strip()
        if stripped:
            candidates.append(stripped)

        object_candidate = ClassificationResponseParser._extract_object_candidate(
            stripped
        )
        if object_candidate and object_candidate not in candidates:
            candidates.append(object_candidate)

        return candidates

    @staticmethod
    def _try_parse_mapping(candidate: str) -> dict[str, Any] | None:
        for loader in (json.loads, ast.literal_eval):
            try:
                payload = loader(candidate)
            except (json.JSONDecodeError, SyntaxError, ValueError):
                continue

            if isinstance(payload, dict):
                return payload

        return None

    @staticmethod
    def _extract_object_candidate(text: str) -> str:
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            return ""

        return text[start : end + 1]

    def _parse_key_value_text(self, text: str) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        evidence_items: list[str] = []
        collecting_evidence = False

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if ":" in line:
                raw_key, raw_value = line.split(":", 1)
                key = self._normalize_key(raw_key)
                value = raw_value.strip().rstrip(",")

                if key == "evidence":
                    collecting_evidence = True
                    evidence_items.extend(self._coerce_evidence(value))
                else:
                    collecting_evidence = False
                    payload[key] = value.strip().strip('"').strip("'")

                continue

            if collecting_evidence:
                item = self._strip_list_prefix(line)
                if item:
                    evidence_items.append(item)

        if evidence_items:
            payload["evidence"] = evidence_items

        return payload

    def _normalize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized_payload: dict[str, Any] = {}

        for raw_key, value in payload.items():
            normalized_payload[self._normalize_key(str(raw_key))] = value

        return normalized_payload

    def _normalize_key(self, value: str) -> str:
        normalized = KEY_PATTERN.sub("_", value.lower()).strip("_")

        if normalized in self.label_aliases:
            return "label"

        if normalized in {"confidence", "confidence_score", "score"}:
            return "confidence_score"

        return normalized

    @staticmethod
    def _coerce_text(value: Any) -> str | None:
        if value is None:
            return None

        text = str(value).strip().strip('"').strip("'").strip()
        return text or None

    @staticmethod
    def _parse_confidence(value: Any) -> float | None:
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).strip().strip('"').strip("'").strip()
        if not text:
            return None

        try:
            if text.endswith("%"):
                return float(text[:-1].strip()) / 100

            return float(text)
        except ValueError:
            return None

    def _coerce_evidence(self, value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, (list, tuple)):
            return [
                item
                for item in (
                    self._strip_list_prefix(str(entry).strip())
                    for entry in value
                )
                if item
            ]

        text = str(value).strip()
        if not text:
            return []

        if text.startswith("[") and text.endswith("]"):
            for loader in (json.loads, ast.literal_eval):
                try:
                    parsed = loader(text)
                except (json.JSONDecodeError, SyntaxError, ValueError):
                    continue

                if isinstance(parsed, (list, tuple)):
                    return self._coerce_evidence(list(parsed))

        lines = [self._strip_list_prefix(line.strip()) for line in text.splitlines()]
        evidence = [line for line in lines if line]

        if evidence:
            return evidence

        item = self._strip_list_prefix(text)
        return [item] if item else []

    @staticmethod
    def _strip_list_prefix(value: str) -> str:
        return LIST_ITEM_PATTERN.sub("", value).strip().strip('"').strip("'").strip()
