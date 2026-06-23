from typing import Any

from src.application.contracts.ai import LLMProvider
from src.shared.exceptions import LLMProviderError

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5:3b"


def _default_ollama_base_url() -> str:
    try:
        from src.config.settings import llm_settings

        return llm_settings.ollama_base_url or DEFAULT_OLLAMA_BASE_URL
    except Exception:
        return DEFAULT_OLLAMA_BASE_URL


def _default_ollama_model() -> str:
    try:
        from src.config.settings import llm_settings

        return llm_settings.general_llm or DEFAULT_OLLAMA_MODEL
    except Exception:
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

    def generate(self, prompt: str, model: str | None = None) -> str:
        model_name = model or self.default_model

        try:
            response = self._get_client().generate(
                model=model_name,
                prompt=prompt,
            )
        except Exception as exc:
            raise LLMProviderError(
                "Failed to generate response from Ollama.",
                details={
                    "base_url": self.base_url,
                    "model_name": model_name,
                },
            ) from exc

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
