import ast
import json
import re
from typing import Any

from src.application.services.ai import LLMService
from src.application.services.classification import ClassificationService
from src.application.validation.classification import DocumentClassificationValidator
from src.application.validation.common import ValidationResult
from src.application.workflows.classification.prompt_builders import (
    ClassificationPromptBuilder,
)
from src.domain.classification import ClassificationResult, DocumentClassification
from src.domain.common import DocumentType, ModelProcessingMetadata
from src.domain.document import Document
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action
from src.shared.exceptions import SchemaValidationError
from src.shared.ids import IdGenerator, IdPrefix

KEY_PATTERN = re.compile(r"[^a-z0-9]+")
LIST_ITEM_PATTERN = re.compile(r"^\s*(?:[-*]+|\d+[\.\)]|[A-Za-z]\))\s*")


def _default_document_classification_model() -> str | None:
    try:
        from src.config.settings import classification_settings, llm_settings

        return (
            classification_settings.classification_llm
            or llm_settings.classification_llm
            or llm_settings.general_llm
        )
    except Exception:
        return None


class DocumentClassificationWorkflow:
    def __init__(
        self,
        llm_service: LLMService,
        classification_service: ClassificationService,
        document_classification_validator: DocumentClassificationValidator,
        id_generator: IdGenerator,
        prompt_builder: ClassificationPromptBuilder | None = None,
        classification_model: str | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.classification_service = classification_service
        self.document_classification_validator = document_classification_validator
        self.id_generator = id_generator
        self.prompt_builder = prompt_builder or ClassificationPromptBuilder()
        self.classification_model = (
            classification_model
            or _default_document_classification_model()
        )

    @tracked_action(
        action="classification.document_generated",
        entity_type="document",
        activity=True,
        audit=False,
        event=False,
    )
    def classify_document(
        self,
        document: Document,
        activity_context: ActivityContext | None = None,
    ) -> DocumentClassification:
        prompt = self.prompt_builder.build_document_classification_prompt(document)
        response = self.llm_service.generate(
            prompt,
            model=self.classification_model,
            activity_context=activity_context,
        )

        classification = self._build_classification(document, response)

        validation = self.document_classification_validator.validate(classification)
        validation.raise_if_invalid()

        self.classification_service.save_document_classification(
            classification,
            activity_context=activity_context,
        )
        return classification

    def _build_classification(
        self,
        document: Document,
        response: str,
    ) -> DocumentClassification:
        parsed = self._parse_response(response)
        document_type = self._resolve_document_type(parsed["label"])
        metadata_errors = self._build_metadata_errors(parsed["label"], document_type)

        result = ClassificationResult(
            classification_id=self.id_generator.new_id(IdPrefix.CLASSIFICATION),
            document_id=document.document_id,
            predicted_label=document_type.value,
            confidence_score=parsed["confidence_score"],
            rationale=parsed["rationale"],
            evidence=parsed["evidence"],
            processing_metadata=ModelProcessingMetadata(
                model_name=self.classification_model or "default",
                model_type="document_classification",
                confidence=parsed["confidence_score"],
                prompt_version=self.prompt_builder.prompt_version,
                errors=metadata_errors,
            ),
        )

        return DocumentClassification(
            document_id=document.document_id,
            document_type=document_type,
            result=result,
        )

    @classmethod
    def _parse_response(cls, response: str) -> dict[str, Any]:
        payload = cls._extract_payload(response)
        validation = ValidationResult()

        label = cls._coerce_text(payload.get("label"))
        if not label:
            validation.add_issue("label", "Classification label is required.", "classification.response.label.required")

        raw_confidence = payload.get("confidence_score")
        confidence_score = cls._parse_confidence(raw_confidence)
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
            "rationale": cls._coerce_text(payload.get("rationale")),
            "evidence": cls._coerce_evidence(payload.get("evidence")),
        }

    @classmethod
    def _extract_payload(cls, response: str) -> dict[str, Any]:
        text = response.strip()
        candidate = cls._extract_object_candidate(text)

        for raw_candidate in [candidate, text]:
            if not raw_candidate:
                continue

            for loader in (json.loads, ast.literal_eval):
                try:
                    payload = loader(raw_candidate)
                except (json.JSONDecodeError, SyntaxError, ValueError):
                    continue

                if isinstance(payload, dict):
                    return payload

        payload = cls._parse_key_value_text(text)
        if payload:
            return payload

        raise SchemaValidationError(
            "Malformed classification response.",
            details={"response": response},
        )

    @staticmethod
    def _extract_object_candidate(text: str) -> str:
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            return ""

        return text[start : end + 1]

    @classmethod
    def _parse_key_value_text(cls, text: str) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        evidence_items: list[str] = []
        collecting_evidence = False

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if ":" in line:
                raw_key, raw_value = line.split(":", 1)
                key = cls._normalize_key(raw_key)
                value = raw_value.strip().rstrip(",")

                if key == "evidence":
                    collecting_evidence = True
                    evidence_items.extend(cls._coerce_evidence(value))
                else:
                    collecting_evidence = False
                    payload[key] = value.strip().strip('"').strip("'")

                continue

            if collecting_evidence:
                item = cls._strip_list_prefix(line)
                if item:
                    evidence_items.append(item)

        if evidence_items:
            payload["evidence"] = evidence_items

        return payload

    @staticmethod
    def _normalize_key(value: str) -> str:
        normalized = KEY_PATTERN.sub("_", value.lower()).strip("_")

        if normalized in {"predicted_label", "document_type"}:
            return "label"

        if normalized == "confidence":
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

    @classmethod
    def _coerce_evidence(cls, value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, (list, tuple)):
            return [
                item
                for item in (
                    cls._strip_list_prefix(str(entry).strip())
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
                    return cls._coerce_evidence(list(parsed))

        lines = [cls._strip_list_prefix(line.strip()) for line in text.splitlines()]
        evidence = [line for line in lines if line]

        if evidence:
            return evidence

        item = cls._strip_list_prefix(text)
        return [item] if item else []

    @staticmethod
    def _strip_list_prefix(value: str) -> str:
        return LIST_ITEM_PATTERN.sub("", value).strip().strip('"').strip("'").strip()

    @staticmethod
    def _resolve_document_type(label: str) -> DocumentType:
        normalized = KEY_PATTERN.sub("_", label.lower()).strip("_")

        for document_type in DocumentType:
            if normalized in {
                document_type.value,
                document_type.name.lower(),
            }:
                return document_type

        return DocumentType.UNKNOWN

    @staticmethod
    def _build_metadata_errors(
        raw_label: str,
        document_type: DocumentType,
    ) -> list[str]:
        normalized = KEY_PATTERN.sub("_", raw_label.lower()).strip("_")

        if document_type == DocumentType.UNKNOWN and normalized != DocumentType.UNKNOWN.value:
            return [f"Unknown label returned by model: {raw_label}"]

        return []
