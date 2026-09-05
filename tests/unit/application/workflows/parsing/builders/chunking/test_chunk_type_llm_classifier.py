import json

from src.application.workflows.parsing.builders.chunking.builders.chunk_type_llm_classifier import (
    ChunkTypeLLMClassifier,
)
from src.domain.common import ChunkType


class FakeLLMService:
    def __init__(self, label: str, confidence: float = 0.9) -> None:
        self.label = label
        self.confidence = confidence
        self.calls: list[dict[str, object]] = []

    def generate(self, prompt, model=None, response_schema=None):
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "response_schema": response_schema,
            }
        )
        return json.dumps(
            {
                "label": self.label,
                "confidence_score": self.confidence,
            }
        )


def make_classifier(label: str) -> ChunkTypeLLMClassifier:
    return ChunkTypeLLMClassifier(llm_service=FakeLLMService(label))


def test_classify_matches_exact_enum_value() -> None:
    classifier = make_classifier("maintenance_interval")

    result = classifier.classify(content="Replace filter every 1000 hours.", section_path=[])

    assert result == ChunkType.MAINTENANCE_INTERVAL


def test_classify_normalizes_spaces_to_underscores() -> None:
    classifier = make_classifier("Maintenance Interval")

    result = classifier.classify(content="Replace filter every 1000 hours.", section_path=[])

    assert result == ChunkType.MAINTENANCE_INTERVAL


def test_classify_normalizes_hyphens_to_underscores() -> None:
    classifier = make_classifier("Safety-Warning")

    result = classifier.classify(content="Depressurize before servicing.", section_path=[])

    assert result == ChunkType.SAFETY_WARNING


def test_classify_matches_enum_name_case_insensitively() -> None:
    classifier = make_classifier("SPARE_PARTS_TABLE")

    result = classifier.classify(content="Part number HP-001, qty 1.", section_path=[])

    assert result == ChunkType.SPARE_PARTS_TABLE


def test_classify_discards_general_label() -> None:
    classifier = make_classifier("general")

    result = classifier.classify(content="Miscellaneous notes.", section_path=[])

    assert result is None


def test_classify_discards_unknown_label() -> None:
    classifier = make_classifier("unknown")

    result = classifier.classify(content="Miscellaneous notes.", section_path=[])

    assert result is None


def test_classify_returns_none_for_unresolvable_label() -> None:
    classifier = make_classifier("not_a_real_chunk_type")

    result = classifier.classify(content="Some content.", section_path=[])

    assert result is None


def test_classify_returns_none_when_llm_service_missing() -> None:
    classifier = ChunkTypeLLMClassifier(llm_service=None)

    result = classifier.classify(content="Some content.", section_path=[])

    assert result is None


def test_classify_returns_none_for_empty_content() -> None:
    classifier = make_classifier("maintenance_interval")

    result = classifier.classify(content="   ", section_path=[])

    assert result is None


def test_is_available_reflects_llm_service_presence() -> None:
    assert make_classifier("maintenance_interval").is_available() is True
    assert ChunkTypeLLMClassifier(llm_service=None).is_available() is False


def test_classify_passes_response_schema_to_llm() -> None:
    llm_service = FakeLLMService("maintenance_interval")
    classifier = ChunkTypeLLMClassifier(llm_service=llm_service, model="chunk-model")

    classifier.classify(
        content="Replace filter every 1000 hours.",
        section_path=["Maintenance"],
    )

    assert llm_service.calls
    assert llm_service.calls[0]["model"] == "chunk-model"
    assert isinstance(llm_service.calls[0]["response_schema"], dict)


def test_classify_discards_label_below_confidence_threshold() -> None:
    classifier = ChunkTypeLLMClassifier(
        llm_service=FakeLLMService("maintenance_interval", confidence=0.69),
        confidence_threshold=0.70,
    )

    result = classifier.classify(
        content="Replace filter at the specified service interval.",
        section_path=["Maintenance"],
    )

    assert result is None


def test_classify_accepts_label_at_confidence_threshold() -> None:
    classifier = ChunkTypeLLMClassifier(
        llm_service=FakeLLMService("maintenance_interval", confidence=0.70),
        confidence_threshold=0.70,
    )

    result = classifier.classify(
        content="Replace filter at the specified service interval.",
        section_path=["Maintenance"],
    )

    assert result == ChunkType.MAINTENANCE_INTERVAL
