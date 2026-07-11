from __future__ import annotations

from src.application.workflows.common.settings_resolver import resolve_setting

# `ExtractionWorkflow`'s config-lookup defaults, split out of
# extraction_workflow.py so that file's job is orchestration, not config
# plumbing. Each function keeps its own `_default_*() -> T` shape (matching
# the shared `resolve_setting` primitive's calling convention from Phase 1)
# so its exact existing behavior -- including falling back to a hard-coded
# default whenever `src.config.settings` can't be imported or the lookup
# otherwise fails -- is preserved byte-for-byte.


def _default_extraction_model() -> str | None:
    def _load() -> str | None:
        from src.config.settings import llm_settings

        return llm_settings.extraction_llm or llm_settings.general_llm

    return resolve_setting(_load, None)


def _default_extraction_confidence_threshold() -> float:
    def _load() -> float:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_confidence_threshold

    return resolve_setting(_load, 1.0)


def _default_extraction_require_human_review() -> bool:
    def _load() -> bool:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_require_human_review

    return resolve_setting(_load, True)


def _default_max_chunks_per_batch() -> int:
    def _load() -> int:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_max_chunks_per_batch

    return resolve_setting(_load, 16)


def _default_max_chars_per_batch() -> int:
    def _load() -> int:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_max_chars_per_batch

    return resolve_setting(_load, 16_000)


def _default_allow_partial_batches() -> bool:
    def _load() -> bool:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_allow_partial_batches

    return resolve_setting(_load, False)


def _default_failure_preview_chars() -> int:
    def _load() -> int:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_failure_preview_chars

    return resolve_setting(_load, 1_200)


def _default_extraction_max_attempts() -> int:
    def _load() -> int:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_max_attempts

    return resolve_setting(_load, 2)


def _default_extraction_temperature() -> float:
    def _load() -> float:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_temperature

    return resolve_setting(_load, 0.0)


def _default_extraction_json_mode() -> bool:
    def _load() -> bool:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_json_mode

    return resolve_setting(_load, True)


def _default_candidate_narrowing_enabled() -> bool:
    def _load() -> bool:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_candidate_narrowing_enabled

    return resolve_setting(_load, False)
