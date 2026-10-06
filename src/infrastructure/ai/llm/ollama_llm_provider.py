from typing import Any

from src.application.contracts.ai import LLMGenerationResult, LLMProvider
from src.config.logging import get_logger
from src.shared.exceptions import LLMProviderError

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5:3b"

_logger = get_logger(__name__)

# Native Ollama /api/generate response fields already promoted to a
# first-class LLMGenerationResult field (or to .text, via "response") -
# excluded from provider_metadata so nothing is duplicated there. "context"
# is also always excluded (see _as_dict's caller below) - it's Ollama's raw
# token-id array for the whole exchange, has no durable diagnostic value at
# this layer, and would needlessly bloat every result.
_PROMOTED_OR_EXCLUDED_RESPONSE_KEYS = frozenset(
    {
        "response",
        "context",
        "model",
        "done",
        "done_reason",
        "prompt_eval_count",
        "eval_count",
        "total_duration",
        "prompt_eval_duration",
        "eval_duration",
    }
)


def _default_ollama_base_url() -> str:
    try:
        from src.config.settings import llm_settings

        return llm_settings.ollama_base_url or DEFAULT_OLLAMA_BASE_URL
    except Exception:
        _logger.warning(
            "ollama_provider.settings_fallback setting=ollama_base_url "
            "fallback_value=%s",
            DEFAULT_OLLAMA_BASE_URL,
        )
        return DEFAULT_OLLAMA_BASE_URL


def _default_ollama_model() -> str:
    try:
        from src.config.settings import llm_settings

        return llm_settings.general_llm or DEFAULT_OLLAMA_MODEL
    except Exception:
        _logger.warning(
            "ollama_provider.settings_fallback setting=general_llm "
            "fallback_value=%s",
            DEFAULT_OLLAMA_MODEL,
        )
        return DEFAULT_OLLAMA_MODEL


class OllamaLLMProvider(LLMProvider):
    def __init__(
        self,
        *,
        base_url: str | None = None,
        default_model: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.base_url = base_url or _default_ollama_base_url()
        self.default_model = default_model or _default_ollama_model()
        self._client = client

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
        response_schema: dict[str, Any] | None = None,
        num_ctx: int | None = None,
    ) -> str:
        model_name, response = self._call_client(
            prompt,
            model=model,
            temperature=temperature,
            json_mode=json_mode,
            response_schema=response_schema,
            num_ctx=num_ctx,
        )
        return self._require_response_text(response, model_name=model_name)

    def generate_with_metadata(
        self,
        prompt: str,
        model: str | None = None,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
        response_schema: dict[str, Any] | None = None,
        num_ctx: int | None = None,
    ) -> LLMGenerationResult:
        """Same request `generate()` makes, but returns the full
        provider-neutral `LLMGenerationResult` instead of a bare string -
        mapping Ollama's native `done`/`done_reason`/`prompt_eval_count`/
        `eval_count`/duration fields onto it. Native fields this project
        has no first-class place for yet (e.g. `load_duration`,
        `created_at`) are kept in `provider_metadata`; the raw `context`
        token-id array is never retained (see module docstring note above).
        """
        model_name, response = self._call_client(
            prompt,
            model=model,
            temperature=temperature,
            json_mode=json_mode,
            response_schema=response_schema,
            num_ctx=num_ctx,
        )
        text = self._require_response_text(response, model_name=model_name)
        response_dict = self._as_dict(response)

        return LLMGenerationResult(
            text=text,
            provider_name="ollama",
            model=response_dict.get("model", model_name),
            done=response_dict.get("done"),
            finish_reason=response_dict.get("done_reason"),
            prompt_tokens=response_dict.get("prompt_eval_count"),
            completion_tokens=response_dict.get("eval_count"),
            total_duration_ns=response_dict.get("total_duration"),
            prompt_duration_ns=response_dict.get("prompt_eval_duration"),
            completion_duration_ns=response_dict.get("eval_duration"),
            provider_metadata={
                key: value
                for key, value in response_dict.items()
                if key not in _PROMOTED_OR_EXCLUDED_RESPONSE_KEYS
            },
        )

    def _call_client(
        self,
        prompt: str,
        *,
        model: str | None,
        temperature: float | None,
        json_mode: bool,
        response_schema: dict[str, Any] | None,
        num_ctx: int | None,
    ) -> tuple[str, Any]:
        model_name = model or self.default_model
        extra_kwargs: dict[str, Any] = {}
        if response_schema is not None:
            extra_kwargs["format"] = response_schema
        elif json_mode:
            extra_kwargs["format"] = "json"
        options: dict[str, Any] = {}
        if temperature is not None:
            options["temperature"] = temperature
        if num_ctx is not None:
            options["num_ctx"] = num_ctx
        if options:
            extra_kwargs["options"] = options

        try:
            response = self._get_client().generate(
                model=model_name,
                prompt=prompt,
                **extra_kwargs,
            )
        except Exception as exc:
            raise LLMProviderError(
                "Failed to generate response from Ollama.",
                details={
                    "base_url": self.base_url,
                    "model_name": model_name,
                },
            ) from exc

        return model_name, response

    def _require_response_text(self, response: Any, *, model_name: str) -> str:
        response_text = self._extract_response_text(response)

        if response_text is None:
            raise LLMProviderError(
                "Ollama returned an invalid response.",
                details={
                    "base_url": self.base_url,
                    "model_name": model_name,
                },
            )

        return response_text.strip()

    def _get_client(self) -> Any:
        if self._client is None:
            from ollama import Client

            self._client = Client(host=self.base_url)

        return self._client

    @staticmethod
    def _extract_response_text(response: Any) -> str | None:
        if isinstance(response, dict):
            value = response.get("response")
            return value if isinstance(value, str) or value is None else str(value)

        value = getattr(response, "response", None)
        if isinstance(value, str) or value is None:
            return value

        return str(value)

    @staticmethod
    def _as_dict(response: Any) -> dict[str, Any]:
        """Normalizes the ollama client's response to a plain dict -
        covers the historical plain-dict shape, newer client versions that
        return a pydantic-style model with `.model_dump()`, and a plain
        attribute-bearing object (the same shapes `_extract_response_text`
        already tolerates for the "response" field alone)."""
        if isinstance(response, dict):
            return response
        if hasattr(response, "model_dump"):
            dumped = response.model_dump()
            return dumped if isinstance(dumped, dict) else {}
        if hasattr(response, "__dict__"):
            return dict(vars(response))
        return {}
