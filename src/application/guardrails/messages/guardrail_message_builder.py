from __future__ import annotations


class GuardrailMessageBuilder:
    def out_of_scope_message(self) -> str:
        return (
            "I'm focused on indexed technical documents. I can help you search manuals, "
            "datasheets, certificates, drawings, and reports, retrieve evidence, compare "
            "sections, or generate grounded document summaries. Try asking: "
            "\"What are the maintenance intervals in the selected manual?\""
        )

    def unsafe_destructive_message(self) -> str:
        return (
            "I can't perform requests that mutate the document corpus from this chat. "
            "Deleting documents, clearing vectors, or resetting storage requires a dedicated "
            "approved workflow."
        )

    def prompt_injection_message(self) -> str:
        return (
            "I can't reveal hidden instructions, system prompts, or chain-of-thought, and I "
            "can't bypass safety rules. I can still help with document-grounded questions."
        )

    def secret_request_message(self) -> str:
        return (
            "I can't expose environment variables, credentials, API keys, or other secrets. "
            "I can help with document-grounded tasks instead."
        )

    def tool_abuse_message(self) -> str:
        return (
            "I can't execute arbitrary shell or system commands from this chat. I can only use "
            "the approved document-agent workflows and tools."
        )

    def missing_document_message(self) -> str:
        return (
            "Please select a document first. You can use `/list` to see available documents "
            "or `/open <document name>` to choose one."
        )

    def insufficient_evidence_message(self) -> str:
        return (
            "I found related document evidence, but not enough to answer confidently. Try "
            "asking for a specific section, part number, interval, or page reference."
        )

    def grounding_failure_message(self) -> str:
        return (
            "I could not verify a grounded answer confidently enough from the current document evidence."
        )

    def generic_block_message(self) -> str:
        return (
            "I can't complete that request in this runtime. Please try a document-grounded "
            "question or an approved document-agent command."
        )
