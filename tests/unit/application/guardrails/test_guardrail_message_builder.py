from src.application.guardrails.messages.guardrail_message_builder import (
    GuardrailMessageBuilder,
)


def test_guardrail_message_builder_produces_friendly_out_of_scope_message() -> None:
    builder = GuardrailMessageBuilder()

    message = builder.out_of_scope_message().lower()

    assert "technical documents" in message
    assert "maintenance intervals" in message


def test_guardrail_message_builder_mentions_mutating_corpus_for_unsafe_requests() -> None:
    builder = GuardrailMessageBuilder()

    message = builder.unsafe_destructive_message().lower()

    assert "mutate the document corpus" in message
    assert "approved workflow" in message


def test_guardrail_message_builder_guides_document_selection() -> None:
    builder = GuardrailMessageBuilder()

    message = builder.missing_document_message()

    assert "/list" in message
    assert "/open <document name>" in message
