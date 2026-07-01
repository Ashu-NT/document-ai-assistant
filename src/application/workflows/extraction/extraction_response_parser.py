import ast
import json
import re
from typing import Any

from src.application.validation.common import ValidationResult
from src.shared.exceptions import SchemaValidationError

KEY_PATTERN = re.compile(r"[^a-z0-9]+")
THINK_BLOCK_PATTERN = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
CODE_FENCE_PATTERN = re.compile(
    r"```(?:json|javascript|js|python|text)?\s*(.*?)```",
    re.IGNORECASE | re.DOTALL,
)


class ExtractionResponseParser:
    def parse(self, response: str) -> dict[str, Any]:
        payload = self._extract_payload(response)
        maintenance_tasks = self._coerce_item_list(
            self._pick(payload, "maintenance_tasks", "tasks"),
            field_name="maintenance_tasks",
        )
        spare_parts = self._coerce_item_list(
            self._pick(payload, "spare_parts", "parts"),
            field_name="spare_parts",
        )
        equipment = self._coerce_item_list(
            self._pick(payload, "equipment", "equipment_info"),
            field_name="equipment",
        )
        manufacturers = self._coerce_item_list(
            self._pick(payload, "manufacturers", "manufacturer_list"),
            field_name="manufacturers",
        )
        identifiers = self._coerce_item_list(
            self._pick(payload, "identifiers", "identifier_list"),
            field_name="identifiers",
        )
        confidence_score = self._resolve_overall_confidence(
            payload=payload,
            item_groups=(
                maintenance_tasks,
                spare_parts,
                equipment,
                manufacturers,
                identifiers,
            ),
        )
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
            "requires_human_review": self._pick(
                payload,
                "requires_human_review",
                "requires_review",
            ),
            "maintenance_tasks": maintenance_tasks,
            "spare_parts": spare_parts,
            "equipment": equipment,
            "manufacturers": manufacturers,
            "identifiers": identifiers,
        }

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

    @classmethod
    def _coerce_item_list(
        cls,
        value: Any,
        *,
        field_name: str,
    ) -> list[dict[str, Any]]:
        if value is None:
            return []

        parsed_value = value
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []

            for loader in (json.loads, ast.literal_eval, _try_yaml_load):
                try:
                    parsed_value = loader(stripped)
                    break
                except (json.JSONDecodeError, SyntaxError, ValueError, TypeError):
                    continue

        if isinstance(parsed_value, dict):
            parsed_value = [parsed_value]

        if not isinstance(parsed_value, list):
            raise SchemaValidationError(
                f"{field_name} must be a list.",
                details={field_name: value},
            )

        items: list[dict[str, Any]] = []
        for item in parsed_value:
            if not isinstance(item, dict):
                raise SchemaValidationError(
                    f"{field_name} items must be objects.",
                    details={field_name: value},
                )
            items.append(item)

        return items

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

    @classmethod
    def _resolve_overall_confidence(
        cls,
        *,
        payload: dict[str, Any],
        item_groups: tuple[list[dict[str, Any]], ...],
    ) -> float:
        top_level_confidence = cls._parse_confidence(
            cls._pick(
                payload,
                "confidence_score",
                "confidence",
                "overall_confidence",
            )
        )
        if top_level_confidence is not None:
            return top_level_confidence

        derived_confidence = cls._derive_confidence_from_items(item_groups)
        if derived_confidence is not None:
            return derived_confidence

        return 0.0

    @classmethod
    def _derive_confidence_from_items(
        cls,
        item_groups: tuple[list[dict[str, Any]], ...],
    ) -> float | None:
        confidences: list[float] = []
        for items in item_groups:
            for item in items:
                confidence = cls._parse_confidence(
                    cls._pick(item, "confidence_score", "confidence")
                )
                if confidence is not None:
                    confidences.append(confidence)

        if not confidences:
            return None

        return sum(confidences) / len(confidences)


def _try_yaml_load(candidate: str) -> Any:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise TypeError("yaml is not installed") from exc

    try:
        return yaml.safe_load(candidate)
    except Exception as exc:
        raise TypeError("yaml parsing failed") from exc
