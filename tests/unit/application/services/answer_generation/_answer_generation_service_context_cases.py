import logging

from src.application.prompts.answer_generation import ANSWER_PROMPT_VERSION
from src.application.services.answer_generation import AnswerIntent
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.answer_generation_service import (
    AnswerGenerationService,
)
from src.domain.common import ChunkType

from tests.unit.application.services.answer_generation._answer_generation_service_support import (
    FakeLLMService,
    FakePromptBuilder,
    _make_chunk,
    _make_table_chunk,
    make_service,
)


def test_generate_sets_prompt_version() -> None:
    service, _ = make_service()
    result = service.generate(
        AnswerGenerationRequest(question="Test question?", context_chunks=[_make_chunk()])
    )
    assert result.prompt_version == ANSWER_PROMPT_VERSION


def test_generate_model_name_is_reflected_in_result_and_metadata() -> None:
    service, _ = make_service(model="qwen3:8b")
    result = service.generate(
        AnswerGenerationRequest(
            question="What is the pressure?",
            context_chunks=[_make_chunk()],
        )
    )
    assert result.model_name == "qwen3:8b"
    assert result.metadata is not None
    assert result.metadata.model_name == "qwen3:8b"
    assert result.metadata.model_type == "answer_generation"
    assert result.metadata.prompt_version == ANSWER_PROMPT_VERSION


def test_generate_infers_answer_intent_when_missing() -> None:
    service, _ = make_service()
    result = service.generate(
        AnswerGenerationRequest(
            question="specification",
            context_chunks=[
                _make_chunk(
                    content="Test pressure: 700 bar\nDesign pressure: 350 bar\nSize: DN 8",
                )
            ],
        )
    )
    assert result.answer_intent == AnswerIntent.SPECIFICATION_SUMMARY
    assert result.diagnostics["answer_intent"] == "specification_summary"


def test_generate_builds_structured_context_and_format_policy_before_prompt() -> None:
    llm = FakeLLMService()
    prompt_builder = FakePromptBuilder()
    service = AnswerGenerationService(
        llm_service=llm,
        prompt_builder=prompt_builder,
        answer_generation_model="qwen3:8b",
    )
    service.generate(
        AnswerGenerationRequest(
            question="Explain the pressure specification in detail",
            context_chunks=[
                _make_chunk(
                    content="Test pressure: 700 bar\nDesign pressure: 350 bar",
                    chunk_id="chunk_101",
                )
            ],
        )
    )
    built_request = prompt_builder.requests[0]
    assert built_request.answer_intent == AnswerIntent.SPECIFICATION_SUMMARY
    assert built_request.structured_context is not None
    assert built_request.structured_context.key_values
    assert built_request.format_policy is not None
    assert built_request.format_policy.preferred_format == "structured_bullets"


def test_generate_real_prompt_builder_emits_topology_tables_and_budgeted_appendix() -> None:
    llm = FakeLLMService(response='{"answer_text":"Table answer"}')
    service, _ = make_service(llm)
    service.generate(
        AnswerGenerationRequest(
            question="Show the specification table",
            context_chunks=[
                _make_table_chunk(
                    chunk_id="chunk_table",
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    content="Test pressure and design pressure values.",
                    section_path=["Certificate", "Particulars"],
                    page_start=5,
                    page_end=5,
                    metadata={
                        "table_rows_json": '[["Parameter","Value"],["Test pressure","700 bar"]]'
                    },
                ),
                _make_table_chunk(
                    chunk_id="chunk_supporting",
                    chunk_type=ChunkType.GENERAL,
                    content="The certificate particulars summarize the main ratings.",
                    section_path=["Certificate", "Particulars"],
                    page_start=5,
                    page_end=5,
                ),
                _make_table_chunk(
                    chunk_id="chunk_context",
                    chunk_type=ChunkType.OVERVIEW,
                    content="Overview context that should be deprioritized in the appendix.",
                    section_path=["Certificate", "Overview"],
                    page_start=4,
                    page_end=4,
                ),
            ],
            answer_intent=AnswerIntent.TABLE_SUMMARY,
        )
    )
    prompt = llm.calls[0]["prompt"]
    assert '"tables": [' in prompt
    assert '"source_families": [' in prompt
    assert '"section_topology": [' in prompt
    assert "Raw source appendix:" in prompt
    assert "SOURCE 1" in prompt
    assert "SOURCE 2" in prompt
    assert "SOURCE 3" not in prompt


def test_generate_uses_maintenance_summary_path_and_reports_diagnostics() -> None:
    llm = FakeLLMService(response='{"answer_text":"Maintenance Tasks"}')
    prompt_builder = FakePromptBuilder()
    service = AnswerGenerationService(
        llm_service=llm,
        prompt_builder=prompt_builder,
        answer_generation_model="qwen3:8b",
    )
    result = service.generate(
        AnswerGenerationRequest(
            question="What are maintenance tasks in the document?",
            context_chunks=[
                _make_chunk(
                    content=(
                        "Replace cartridge filters every 1000 operating hours.\n"
                        "Inspect regulating valves."
                    ),
                    chunk_id="chunk_maintenance",
                )
            ],
        )
    )
    built_request = prompt_builder.requests[0]
    assert built_request.answer_intent == AnswerIntent.MAINTENANCE_SUMMARY
    assert built_request.structured_context is not None
    assert len(built_request.structured_context.maintenance_entries) == 2
    assert built_request.format_policy is not None
    assert built_request.format_policy.preferred_format == "maintenance_numbered_entries"
    assert result.diagnostics["answer_intent"] == "maintenance_summary"
    assert result.diagnostics["maintenance_items_found"] == 2
    assert result.diagnostics["maintenance_items_with_interval"] == 1
    assert result.diagnostics["maintenance_items_without_interval"] == 1
    assert result.diagnostics["maintenance_items_merged"] == 0


def test_generate_merges_duplicate_maintenance_entries_before_prompt_building() -> None:
    llm = FakeLLMService(response='{"answer_text":"Maintenance Tasks"}')
    prompt_builder = FakePromptBuilder()
    service = AnswerGenerationService(
        llm_service=llm,
        prompt_builder=prompt_builder,
        answer_generation_model="qwen3:8b",
    )
    result = service.generate(
        AnswerGenerationRequest(
            question="What are the maintenance tasks in the document?",
            context_chunks=[
                _make_chunk(content="Check gearbox every 6 months.", chunk_id="chunk_a"),
                _make_chunk(
                    content="Check gearbox for leaks every 6 months.",
                    chunk_id="chunk_b",
                ),
            ],
        )
    )
    built_request = prompt_builder.requests[0]
    assert built_request.structured_context is not None
    assert len(built_request.structured_context.maintenance_entries) == 1
    assert built_request.structured_context.maintenance_entries[0].task == (
        "Check gearbox for leaks"
    )
    assert result.diagnostics["maintenance_items_found"] == 1
    assert result.diagnostics["maintenance_items_merged"] == 1


# -- finding 3.7: settings-load failure logs a warning before falling back -


def test_default_answer_generation_model_logs_warning_on_settings_failure(
    monkeypatch, caplog
) -> None:
    from src.application.services.answer_generation.answer_generation_service import (
        _default_answer_generation_model,
    )

    monkeypatch.setattr("src.config.settings.llm_settings", object())

    with caplog.at_level(logging.WARNING):
        result = _default_answer_generation_model()

    assert result is None
    assert any(
        "settings_fallback" in message and "answer_generation_model" in message
        for message in caplog.messages
    )


def test_default_answer_generation_temperature_logs_warning_on_settings_failure(
    monkeypatch, caplog
) -> None:
    from src.application.services.answer_generation.answer_generation_service import (
        _default_answer_generation_temperature,
    )

    monkeypatch.setattr("src.config.settings.llm_settings", object())

    with caplog.at_level(logging.WARNING):
        result = _default_answer_generation_temperature()

    assert result == 0.2
    assert any(
        "settings_fallback" in message and "answer_generation_temperature" in message
        for message in caplog.messages
    )
