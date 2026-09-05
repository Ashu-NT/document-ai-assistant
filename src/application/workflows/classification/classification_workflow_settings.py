from src.application.workflows.common.settings_resolver import resolve_setting

# Config-backed defaults shared by classification-domain workflows
# (`PostClassificationChunkFinalizationWorkflow` and
# `HybridDocumentTypeResolver`). Each wraps its config lookup in
# `resolve_setting` (src/application/workflows/common/settings_resolver.py)
# so a missing/broken config module falls back to the hard-coded default
# instead of raising.


def default_enable_question_generation() -> bool:
    def _load() -> bool:
        from src.config.settings import ingestion_settings

        return ingestion_settings.enable_question_generation

    return resolve_setting(_load, False)


def default_max_questions_per_chunk() -> int:
    def _load() -> int:
        from src.config.settings import ingestion_settings

        return ingestion_settings.max_generated_questions_per_chunk

    return resolve_setting(_load, 5)


def default_classification_enabled() -> bool:
    def _load() -> bool:
        from src.config.settings import classification_settings

        return classification_settings.enabled

    return resolve_setting(_load, True)


def default_strong_model_threshold() -> float:
    def _load() -> float:
        from src.config.settings import classification_settings

        return classification_settings.strong_model_threshold

    return resolve_setting(_load, 0.80)


def default_strong_structural_threshold() -> float:
    def _load() -> float:
        from src.config.settings import classification_settings

        return classification_settings.strong_structural_threshold

    return resolve_setting(_load, 0.75)


def default_weak_signal_threshold() -> float:
    def _load() -> float:
        from src.config.settings import classification_settings

        return classification_settings.weak_signal_threshold

    return resolve_setting(_load, 0.55)
