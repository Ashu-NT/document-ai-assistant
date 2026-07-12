from src.application.services.answer_generation import AnswerIntent
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerKeyValue,
    AnswerMaintenanceEntry,
    AnswerMaintenanceReference,
    AnswerSource,
    AnswerStructuredEntity,
    StructuredAnswerContext,
)

from tests.unit.application.services.answer_generation._answer_generation_service_support import (
    FakeLLMService,
    _make_chunk,
    make_service,
)


def test_generate_uses_deterministic_maintenance_schedule_renderer() -> None:
    llm = FakeLLMService(response='{"answer_text":"unused"}')
    service, _ = make_service(llm)
    structured_context = StructuredAnswerContext(
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        maintenance_entries=[
            AnswerMaintenanceEntry(
                task="Replace filter",
                interval="Every 1000 operating hours",
                component="Primary filter",
                notes="Isolate power before opening the housing.",
                source_number=1,
                references=[
                    AnswerMaintenanceReference(
                        source_number=1,
                        page_start=58,
                        page_end=59,
                        section_path="6 Maintenance > Preventive Maintenance",
                    )
                ],
            )
        ],
    )
    result = service.generate(
        AnswerGenerationRequest(
            question="What are the maintenance intervals?",
            context_chunks=[_make_chunk()],
            answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
            structured_context=structured_context,
        )
    )

    assert result.model_name == "deterministic_maintenance_schedule_renderer"
    assert "Task" in result.answer_text
    assert "Every 1000 operating hours" in result.answer_text
    assert "Isolate power before opening the housing." in result.answer_text
    assert llm.calls == []


def test_generate_uses_deterministic_procedure_steps_renderer() -> None:
    llm = FakeLLMService(response='{"answer_text":"unused"}')
    service, _ = make_service(llm)
    structured_context = StructuredAnswerContext(
        answer_intent=AnswerIntent.PROCEDURE_STEPS,
        sources=[
            AnswerSource(
                source_number=1,
                chunk_id="chunk_proc",
                section_path="6 Maintenance > Filter Replacement",
                page_start=58,
                page_end=59,
            )
        ],
        structured_entities=[
            AnswerStructuredEntity(
                entity_type="procedure",
                entity_id="procedure_001",
                source_chunk_id="chunk_proc",
                fields={
                    "title": "Replace filter cartridge",
                    "component_name": "Primary filter",
                    "steps": [
                        "Isolate electrical power.",
                        "Remove the housing cover.",
                        "Install the new cartridge.",
                    ],
                },
            )
        ],
    )
    result = service.generate(
        AnswerGenerationRequest(
            question="Show the filter replacement procedure.",
            context_chunks=[_make_chunk()],
            answer_intent=AnswerIntent.PROCEDURE_STEPS,
            structured_context=structured_context,
        )
    )

    assert result.model_name == "deterministic_procedure_steps_renderer"
    assert "1. Replace filter cartridge" in result.answer_text
    assert "1. Isolate electrical power." in result.answer_text
    assert "Pages: pp.58-59" in result.answer_text
    assert llm.calls == []


def test_generate_uses_deterministic_troubleshooting_renderer() -> None:
    llm = FakeLLMService(response='{"answer_text":"unused"}')
    service, _ = make_service(llm)
    structured_context = StructuredAnswerContext(
        answer_intent=AnswerIntent.TROUBLESHOOTING,
        sources=[
            AnswerSource(
                source_number=1,
                chunk_id="chunk_trouble",
                page_start=72,
                page_end=72,
            )
        ],
        structured_entities=[
            AnswerStructuredEntity(
                entity_type="troubleshooting",
                entity_id="trouble_001",
                source_chunk_id="chunk_trouble",
                fields={
                    "symptom": "Pump does not start",
                    "cause": "Main breaker is open",
                    "remedy": "Reset the breaker and retry",
                },
            )
        ],
    )
    result = service.generate(
        AnswerGenerationRequest(
            question="How do I troubleshoot a pump that does not start?",
            context_chunks=[_make_chunk()],
            answer_intent=AnswerIntent.TROUBLESHOOTING,
            structured_context=structured_context,
        )
    )

    assert result.model_name == "deterministic_troubleshooting_renderer"
    assert "Symptom" in result.answer_text
    assert "Pump does not start" in result.answer_text
    assert "Reset the breaker and retry" in result.answer_text
    assert llm.calls == []


def test_generate_uses_deterministic_fact_sheet_renderer() -> None:
    llm = FakeLLMService(response='{"answer_text":"unused"}')
    service, _ = make_service(llm)
    structured_context = StructuredAnswerContext(
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        sources=[
            AnswerSource(
                source_number=1,
                chunk_id="chunk_spec",
                page_start=12,
                page_end=12,
            )
        ],
        key_values=[
            AnswerKeyValue(
                key="Operating pressure",
                value="10",
                unit="bar",
                source_number=1,
            )
        ],
    )
    result = service.generate(
        AnswerGenerationRequest(
            question="What is the operating pressure specification?",
            context_chunks=[_make_chunk()],
            answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
            structured_context=structured_context,
        )
    )

    assert result.model_name == "deterministic_fact_sheet_renderer"
    assert "Operating pressure" in result.answer_text
    assert "10 bar" in result.answer_text
    assert "p.12" in result.answer_text
    assert llm.calls == []
