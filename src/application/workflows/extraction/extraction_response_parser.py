import ast
import json
import re
from typing import Any

from pydantic import ValidationError

from src.application.validation.common import ValidationResult
from src.application.workflows.extraction.extraction_response_schema import (
    ExtractionResponsePayload,
    coerce_raw_list,
)
from src.shared.exceptions import SchemaValidationError

KEY_PATTERN = re.compile(r"[^a-z0-9]+")
THINK_BLOCK_PATTERN = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
CODE_FENCE_PATTERN = re.compile(
    r"```(?:json|javascript|js|python|text)?\s*(.*?)```",
    re.IGNORECASE | re.DOTALL,
)

_LIST_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "maintenance_tasks": ("maintenance_tasks", "tasks"),
    "spare_parts": ("spare_parts", "parts"),
    "equipment": ("equipment", "equipment_info"),
    "manufacturers": ("manufacturers", "manufacturer_list"),
    "identifiers": ("identifiers", "identifier_list"),
}


class ExtractionResponseParser:
    def __init__(self) -> None:
        self.last_null_items_stripped: dict[str, int] = {}

    def parse(self, response: str) -> dict[str, Any]:
        self.last_null_items_stripped = {}
        raw_payload = self._extract_payload(response)
        self._record_null_items_stripped(raw_payload)

        try:
            validated = ExtractionResponsePayload.model_validate(raw_payload)
        except ValidationError as exc:
            raise SchemaValidationError(
                f"Extraction response failed schema validation: {self._format_validation_error(exc)}",
                details={"response": response, "errors": exc.errors()},
            ) from exc

        item_groups = (
            validated.maintenance_tasks,
            validated.spare_parts,
            validated.equipment,
            validated.manufacturers,
            validated.identifiers,
        )
        confidence_score = self._resolve_overall_confidence(validated, item_groups)

        validation = ValidationResult()
        if confidence_score < 0 or confidence_score > 1:
            validation.add_issue(
                "confidence_score",
                "Confidence score must be a number between 0 and 1.",
                "extraction.response.confidence.invalid",
            )
        validation.raise_if_invalid()

        return {
            "confidence_score": confidence_score,
            "requires_human_review": validated.requires_human_review,
            "maintenance_tasks": [item.model_dump() for item in validated.maintenance_tasks],
            "spare_parts": [item.model_dump() for item in validated.spare_parts],
            "equipment": [item.model_dump() for item in validated.equipment],
            "manufacturers": [item.model_dump() for item in validated.manufacturers],
            "identifiers": [item.model_dump() for item in validated.identifiers],
        }

    def _record_null_items_stripped(self, raw_payload: dict[str, Any]) -> None:
        for field_name, aliases in _LIST_FIELD_ALIASES.items():
            coerced = coerce_raw_list(self._pick(raw_payload, *aliases))
            if not isinstance(coerced, list):
                continue
            null_count = sum(1 for item in coerced if item is None)
            if null_count:
                self.last_null_items_stripped[field_name] = null_count

    @staticmethod
    def _format_validation_error(exc: ValidationError) -> str:
        messages = [
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        ]
        return "; ".join(messages)

    def _extract_payload(self, response: str) -> dict[str, Any]:
        candidate_texts = self._candidate_texts(response)

        for candidate_text in candidate_texts:
            for raw_candidate in self._candidate_objects(candidate_text):
                payload = self._try_parse_mapping(raw_candidate)
                if payload is not None:
                    return payload

        raise SchemaValidationError(
            "Malformed extraction response.",
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

        object_candidate = ExtractionResponseParser._extract_object_candidate(stripped)
        if object_candidate and object_candidate not in candidates:
            candidates.append(object_candidate)

        return candidates

    @staticmethod
    def _try_parse_mapping(candidate: str) -> dict[str, Any] | None:
        for loader in (json.loads, ast.literal_eval, _try_yaml_load):
            try:
                payload = loader(candidate)
            except (json.JSONDecodeError, SyntaxError, ValueError, TypeError):
                continue

            if isinstance(payload, dict):
                return payload

        repaired = _repair_json_text(candidate)
        if repaired is not None:
            try:
                payload = json.loads(repaired)
            except (json.JSONDecodeError, ValueError, TypeError):
                return None

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

    @staticmethod
    def _pick(payload: dict[str, Any], *keys: str) -> Any:
        normalized_payload = {
            KEY_PATTERN.sub("_", str(key).lower()).strip("_"): value
            for key, value in payload.items()
        }

        for key in keys:
            normalized_key = KEY_PATTERN.sub("_", key.lower()).strip("_")
            if normalized_key in normalized_payload:
                return normalized_payload[normalized_key]

        return None

    @staticmethod
    def _resolve_overall_confidence(
        validated: ExtractionResponsePayload,
        item_groups: tuple[list[Any], ...],
    ) -> float:
        if validated.confidence_score is not None:
            return validated.confidence_score

        derived_confidence = ExtractionResponseParser._derive_confidence_from_items(item_groups)
        if derived_confidence is not None:
            return derived_confidence

        return 0.0

    @staticmethod
    def _derive_confidence_from_items(item_groups: tuple[list[Any], ...]) -> float | None:
        confidences = [
            item.confidence_score
            for items in item_groups
            for item in items
            if item.confidence_score is not None
        ]

        if not confidences:
            return None

        return sum(confidences) / len(confidences)


def _repair_json_text(candidate: str) -> str | None:
    text = candidate.strip()
    if not text.startswith("{"):
        return None

    repaired = re.sub(r",\s*([}\]])", r"\1", text)

    open_braces = repaired.count("{") - repaired.count("}")
    open_brackets = repaired.count("[") - repaired.count("]")
    if open_braces <= 0 and open_brackets <= 0:
        return repaired if repaired != text else None

    repaired = repaired.rstrip().rstrip(",")
    repaired += "]" * max(open_brackets, 0)
    repaired += "}" * max(open_braces, 0)
    return repaired


def _try_yaml_load(candidate: str) -> Any:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise TypeError("yaml is not installed") from exc

    try:
        return yaml.safe_load(candidate)
    except Exception as exc:
        raise TypeError("yaml parsing failed") from exc
