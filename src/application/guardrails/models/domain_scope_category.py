from enum import StrEnum


class DomainScopeCategory(StrEnum):
    DOCUMENT_AGENT_SCOPE = "document_agent_scope"
    DEMO_RUNTIME_COMMAND = "demo_runtime_command"
    OUT_OF_SCOPE_GENERAL = "out_of_scope_general"
    UNSAFE_DESTRUCTIVE = "unsafe_destructive"
    PROMPT_INJECTION = "prompt_injection"
    SECRET_REQUEST = "secret_request"
    UNKNOWN_AMBIGUOUS = "unknown_ambiguous"
