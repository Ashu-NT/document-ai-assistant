from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ResponseSafetyPolicy:
    block_hidden_prompt_exposure: bool = True
    block_chain_of_thought_exposure: bool = True
    safe_fallback_on_grounding_failure: bool = True
