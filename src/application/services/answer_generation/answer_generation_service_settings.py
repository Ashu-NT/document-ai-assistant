from src.application.workflows.common.settings_resolver import resolve_setting
from src.config.logging import get_logger

_logger = get_logger(__name__)


def default_answer_generation_model() -> str | None:
    def _load() -> str | None:
        from src.config.settings import llm_settings

        return llm_settings.answer_generation_llm or llm_settings.general_llm

    def _log_fallback(_fallback: str | None) -> None:
        _logger.warning(
            "answer_generation.settings_fallback setting=answer_generation_model "
            "fallback_value=%s",
            None,
        )

    return resolve_setting(_load, None, on_fallback=_log_fallback)


def default_answer_generation_temperature() -> float:
    fallback = 0.2

    def _load() -> float:
        from src.config.settings import llm_settings

        return llm_settings.answer_generation_temperature

    def _log_fallback(resolved_fallback: float) -> None:
        _logger.warning(
            "answer_generation.settings_fallback setting=answer_generation_temperature "
            "fallback_value=%s",
            resolved_fallback,
        )

    return resolve_setting(_load, fallback, on_fallback=_log_fallback)


def default_answer_generation_num_ctx() -> int:
    fallback = 8192

    def _load() -> int:
        from src.config.settings import llm_settings

        return llm_settings.answer_generation_num_ctx

    def _log_fallback(resolved_fallback: int) -> None:
        _logger.warning(
            "answer_generation.settings_fallback setting=answer_generation_num_ctx "
            "fallback_value=%s",
            resolved_fallback,
        )

    return resolve_setting(_load, fallback, on_fallback=_log_fallback)


def default_capture_answer_prompt_text() -> bool:
    fallback = False

    def _load() -> bool:
        from src.config.settings import llm_settings

        return llm_settings.capture_answer_prompt_text

    def _log_fallback(resolved_fallback: bool) -> None:
        _logger.warning(
            "answer_generation.settings_fallback setting=capture_answer_prompt_text "
            "fallback_value=%s",
            resolved_fallback,
        )

    return resolve_setting(_load, fallback, on_fallback=_log_fallback)
