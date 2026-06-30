from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class EnterpriseGuardrailPolicy:
    block_out_of_scope_queries: bool = True
    require_citations: bool = True
    min_confidence: float = 0.50
    max_context_tokens: int = 4000
    block_prompt_injection: bool = True
    block_secret_requests: bool = True
    block_tool_abuse_requests: bool = True
