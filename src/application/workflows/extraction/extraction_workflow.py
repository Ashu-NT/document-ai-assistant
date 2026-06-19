import ast
import json
import re
from typing import Any

from src.application.services.ai import LLMService
from src.application.services.extraction import ExtractionService
from src.application.validation.common import ValidationResult
from src.application.validation.extraction import ExtractionResultValidator
from src.application.workflows.extraction.prompt_builders import (
    ExtractionPromptBuilder,
)
from src.domain.document import DocumentChunk
from src.domain.extraction import (
    EquipmentInfo,
    ExtractionResult,
    MaintenanceTask,
    Manufacturer,
    SparePart,
)
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action
from src.shared.exceptions import SchemaValidationError
from src.shared.ids import IdGenerator, IdPrefix

KEY_PATTERN = re.compile(r"[^a-z0-9]+")


def _default_extraction_model() -> str | None:
    try:
        from src.config.settings import llm_settings

        return llm_settings.extraction_llm or llm_settings.general_llm
    except Exception:
        return None


def _default_extraction_confidence_threshold() -> float:
    try:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_confidence_threshold
    except Exception:
        return 1.0


def _default_extraction_require_human_review() -> bool:
    try:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_require_human_review
    except Exception:
        return True


class ExtractionWorkflow:
    def __init__(
        self,
        llm_service: LLMService,
        extraction_service: ExtractionService,
        extraction_result_validator: ExtractionResultValidator,
        id_generator: IdGenerator,
        prompt_builder: ExtractionPromptBuilder | None = None,
        extraction_model: str | None = None,
        confidence_threshold: float | None = None,
        require_human_review_default: bool | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.extraction_service = extraction_service
        self.extraction_result_validator = extraction_result_validator
        self.id_generator = id_generator
        self.prompt_builder = prompt_builder or ExtractionPromptBuilder()
        self.extraction_model = extraction_model or _default_extraction_model()
        self.confidence_threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else _default_extraction_confidence_threshold()
        )
        self.require_human_review_default = (
            require_human_review_default
            if require_human_review_default is not None
            else _default_extraction_require_human_review()
        )

    @tracked_action(
        action="extraction.generated",
        entity_type="document",
        activity=True,
        audit=False,
        event=False,
    )
    def extract(
        self,
        document_id: str,
        chunks: DocumentChunk | list[DocumentChunk],
        activity_context: ActivityContext | None = None,
    ) -> ExtractionResult:
        chunk_list = self._coerce_chunks(chunks)
        self._validate_input(document_id, chunk_list)

        prompt = self.prompt_builder.build_extraction_prompt(
            document_id,
            chunk_list,
        )
        response = self.llm_service.generate(
            prompt,
            model=self.extraction_model,
            activity_context=activity_context,
        )

        extraction_result = self._build_extraction_result(
            document_id,
            chunk_list,
            response,
        )

        validation = self.extraction_result_validator.validate(extraction_result)
        validation.raise_if_invalid()

        self.extraction_service.save_extraction_result(
            extraction_result,
            activity_context=activity_context,
        )
        return extraction_result

    @staticmethod
    def _coerce_chunks(
        chunks: DocumentChunk | list[DocumentChunk],
    ) -> list[DocumentChunk]:
        if isinstance(chunks, list):
            return chunks

        return [chunks]

    @staticmethod
    def _validate_input(
        document_id: str,
        chunks: list[DocumentChunk],
    ) -> None:
        validation = ValidationResult()

        if not document_id:
            validation.add_issue(
                "document_id",
                "Document id is required.",
                "extraction.document_id.required",
            )

        if not chunks:
            validation.add_issue(
                "chunks",
                "At least one chunk is required.",
                "extraction.chunks.required",
            )

        for index, chunk in enumerate(chunks):
            if chunk.document_id != document_id:
                validation.add_issue(
                    f"chunks[{index}].document_id",
                    "Chunk document_id must match the workflow document_id.",
                    "extraction.chunk.document_mismatch",
                )

        validation.raise_if_invalid()

    def _build_extraction_result(
        self,
        document_id: str,
        chunks: list[DocumentChunk],
        response: str,
    ) -> ExtractionResult:
        payload = self._parse_response(response)
        chunk_lookup = {chunk.chunk_id: chunk for chunk in chunks}
        default_source_chunk_id = chunks[0].chunk_id if len(chunks) == 1 else None
        overall_confidence = payload["confidence_score"]

        maintenance_tasks = [
            self._build_maintenance_task(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in payload["maintenance_tasks"]
        ]
        spare_parts = [
            self._build_spare_part(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in payload["spare_parts"]
        ]
        equipment = [
            self._build_equipment_info(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in payload["equipment"]
        ]
        manufacturers = [
            self._build_manufacturer(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in payload["manufacturers"]
        ]

        requires_human_review = self._resolve_requires_human_review(
            payload.get("requires_human_review"),
            overall_confidence,
        )
        requires_human_review = requires_human_review or any(
            item.requires_human_review
            for item in [
                *maintenance_tasks,
                *spare_parts,
                *equipment,
                *manufacturers,
            ]
        )

        return ExtractionResult(
            extraction_id=self.id_generator.new_id(IdPrefix.EXTRACTION),
            document_id=document_id,
            maintenance_tasks=maintenance_tasks,
            spare_parts=spare_parts,
            equipment=equipment,
            manufacturers=manufacturers,
            source_chunk_ids=list(chunk_lookup),
            confidence_score=overall_confidence,
            requires_human_review=requires_human_review,
        )

    @classmethod
    def _parse_response(cls, response: str) -> dict[str, Any]:
        payload = cls._extract_payload(response)
        validation = ValidationResult()

        confidence_score = cls._parse_confidence(
            cls._pick(
                payload,
                "confidence_score",
                "confidence",
                "overall_confidence",
            )
        )
        if confidence_score is None:
            validation.add_issue(
                "confidence_score",
                "Confidence score must be a number between 0 and 1.",
                "extraction.response.confidence.invalid",
            )

        validation.raise_if_invalid()

        return {
            "confidence_score": confidence_score,
            "requires_human_review": cls._pick(
                payload,
                "requires_human_review",
                "requires_review",
            ),
            "maintenance_tasks": cls._coerce_item_list(
                cls._pick(payload, "maintenance_tasks", "tasks"),
                field_name="maintenance_tasks",
            ),
            "spare_parts": cls._coerce_item_list(
                cls._pick(payload, "spare_parts", "parts"),
                field_name="spare_parts",
            ),
            "equipment": cls._coerce_item_list(
                cls._pick(payload, "equipment", "equipment_info"),
                field_name="equipment",
            ),
            "manufacturers": cls._coerce_item_list(
                cls._pick(payload, "manufacturers", "manufacturer_list"),
                field_name="manufacturers",
            ),
        }

    @classmethod
    def _extract_payload(cls, response: str) -> dict[str, Any]:
        text = cls._strip_code_fences(response.strip())
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

        raise SchemaValidationError(
            "Malformed extraction response.",
            details={"response": response},
        )

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        if text.startswith("```") and text.endswith("```"):
            lines = text.splitlines()

            if len(lines) >= 3:
                return "\n".join(lines[1:-1]).strip()

        return text

    @staticmethod
    def _extract_object_candidate(text: str) -> str:
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            return ""

        return text[start : end + 1]

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

            for loader in (json.loads, ast.literal_eval):
                try:
                    parsed_value = loader(stripped)
                    break
                except (json.JSONDecodeError, SyntaxError, ValueError):
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

    def _build_maintenance_task(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> MaintenanceTask:
        title = self._required_text(
            payload,
            field_name="maintenance_tasks.title",
            keys=("title", "task", "name"),
        )
        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        return MaintenanceTask(
            task_id=self.id_generator.new_id("task"),
            document_id=document_id,
            title=title,
            description=self._optional_text(payload, "description", "details"),
            interval=self._optional_text(payload, "interval", "frequency"),
            component_name=self._optional_text(payload, "component_name", "component"),
            equipment_id=self._optional_text(payload, "equipment_id"),
            source_chunk_id=self._resolve_source_chunk_id(
                payload,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
            ),
            confidence_score=confidence_score,
            requires_human_review=self._resolve_requires_human_review(
                self._pick(payload, "requires_human_review", "requires_review"),
                confidence_score,
            ),
        )

    def _build_spare_part(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> SparePart:
        part_number = self._optional_text(payload, "part_number", "part")
        description = self._optional_text(payload, "description")
        quantity = self._optional_text(payload, "quantity", "qty")
        component_name = self._optional_text(payload, "component_name", "component")
        manufacturer_name = self._optional_text(
            payload,
            "manufacturer_name",
            "manufacturer",
        )

        if not any(
            [
                part_number,
                description,
                quantity,
                component_name,
                manufacturer_name,
            ]
        ):
            raise SchemaValidationError(
                "spare_parts items must contain at least one supported field.",
                details={"spare_part": payload},
            )

        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        return SparePart(
            spare_part_id=self.id_generator.new_id("spare"),
            document_id=document_id,
            part_number=part_number,
            description=description,
            quantity=quantity,
            component_name=component_name,
            manufacturer_name=manufacturer_name,
            source_chunk_id=self._resolve_source_chunk_id(
                payload,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
            ),
            confidence_score=confidence_score,
            requires_human_review=self._resolve_requires_human_review(
                self._pick(payload, "requires_human_review", "requires_review"),
                confidence_score,
            ),
        )

    def _build_equipment_info(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> EquipmentInfo:
        name = self._optional_text(payload, "name", "equipment_name")
        model_number = self._optional_text(payload, "model_number", "model")
        serial_number = self._optional_text(payload, "serial_number", "serial")
        manufacturer_name = self._optional_text(
            payload,
            "manufacturer_name",
            "manufacturer",
        )

        if not any(
            [
                name,
                model_number,
                serial_number,
                manufacturer_name,
            ]
        ):
            raise SchemaValidationError(
                "equipment items must contain at least one supported field.",
                details={"equipment": payload},
            )

        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        return EquipmentInfo(
            equipment_id=self.id_generator.new_id("equipment"),
            document_id=document_id,
            name=name,
            model_number=model_number,
            serial_number=serial_number,
            manufacturer_name=manufacturer_name,
            source_chunk_id=self._resolve_source_chunk_id(
                payload,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
            ),
            confidence_score=confidence_score,
            requires_human_review=self._resolve_requires_human_review(
                self._pick(payload, "requires_human_review", "requires_review"),
                confidence_score,
            ),
        )

    def _build_manufacturer(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> Manufacturer:
        name = self._required_text(
            payload,
            field_name="manufacturers.name",
            keys=("name", "manufacturer_name"),
        )
        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        return Manufacturer(
            manufacturer_id=self.id_generator.new_id("manufacturer"),
            document_id=document_id,
            name=name,
            website=self._optional_text(payload, "website", "url"),
            country=self._optional_text(payload, "country"),
            source_chunk_id=self._resolve_source_chunk_id(
                payload,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
            ),
            confidence_score=confidence_score,
            requires_human_review=self._resolve_requires_human_review(
                self._pick(payload, "requires_human_review", "requires_review"),
                confidence_score,
            ),
        )

    @staticmethod
    def _pick(payload: dict[str, Any], *keys: str) -> Any:
        normalized_payload = {
            KEY_PATTERN.sub("_", key.lower()).strip("_"): value
            for key, value in payload.items()
        }

        for key in keys:
            normalized_key = KEY_PATTERN.sub("_", key.lower()).strip("_")
            if normalized_key in normalized_payload:
                return normalized_payload[normalized_key]

        return None

    @classmethod
    def _required_text(
        cls,
        payload: dict[str, Any],
        *,
        field_name: str,
        keys: tuple[str, ...],
    ) -> str:
        value = cls._optional_text(payload, *keys)
        if value:
            return value

        raise SchemaValidationError(
            f"{field_name} is required.",
            details={field_name: payload},
        )

    @classmethod
    def _optional_text(cls, payload: dict[str, Any], *keys: str) -> str | None:
        value = cls._pick(payload, *keys)
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

    @staticmethod
    def _parse_bool(value: Any) -> bool | None:
        if value is None:
            return None

        if isinstance(value, bool):
            return value

        text = str(value).strip().lower()
        if text in {"true", "yes", "1"}:
            return True

        if text in {"false", "no", "0"}:
            return False

        return None

    def _resolve_requires_human_review(
        self,
        raw_value: Any,
        confidence_score: float | None,
    ) -> bool:
        parsed_value = self._parse_bool(raw_value)
        if parsed_value is not None:
            return parsed_value

        if self.require_human_review_default:
            return True

        if confidence_score is None:
            return True

        return confidence_score < self.confidence_threshold

    @classmethod
    def _resolve_source_chunk_id(
        cls,
        payload: dict[str, Any],
        *,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
    ) -> str | None:
        source_chunk_id = cls._optional_text(
            payload,
            "source_chunk_id",
            "chunk_id",
        )
        if source_chunk_id is None:
            return default_source_chunk_id

        if source_chunk_id not in chunk_lookup:
            raise SchemaValidationError(
                "source_chunk_id must reference one of the provided chunks.",
                details={
                    "source_chunk_id": source_chunk_id,
                    "available_chunk_ids": list(chunk_lookup),
                },
            )

        return source_chunk_id
