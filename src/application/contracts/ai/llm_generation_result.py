from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class LLMGenerationResult:
    """Provider-neutral generation result - the richer sibling of the plain
    `str` `LLMProvider.generate()`/`LLMService.generate()` return value.

    Exists so callers that want generation metadata (token counts, timing,
    termination reason) can get it without depending on any provider's
    native response shape. `generate()` keeps returning a bare `str`
    unchanged for every existing caller; this is reached only via the
    additive `generate_with_metadata()` method.

    Durations are reported in nanoseconds (`_ns` suffix) because the one
    real provider (Ollama) reports them in nanoseconds natively - naming
    the unit explicitly avoids a future caller silently misinterpreting
    the scale.

    `provider_metadata` is a bounded bucket for provider-specific fields
    that don't deserve a first-class place here (e.g. Ollama's
    `load_duration`, `created_at`). It deliberately never holds large
    payloads such as Ollama's raw `context` token-id array - that has no
    durable diagnostic value here and would needlessly bloat every result.
    """

    text: str
    provider_name: str
    model: str | None = None
    done: bool | None = None
    finish_reason: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_duration_ns: int | None = None
    prompt_duration_ns: int | None = None
    completion_duration_ns: int | None = None
    provider_metadata: dict[str, Any] = field(default_factory=dict)
