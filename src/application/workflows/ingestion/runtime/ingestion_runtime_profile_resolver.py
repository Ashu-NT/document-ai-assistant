from __future__ import annotations

from src.application.workflows.ingestion.models.ingestion_exceptions import (
    IngestionDependencyError,
)
from src.application.workflows.ingestion.runtime.ingestion_runtime_capabilities import (
    IngestionRuntimeCapabilities,
)
from src.application.workflows.ingestion.runtime.ingestion_runtime_profile import (
    IngestionRuntimeProfile,
)


class IngestionRuntimeProfileResolver:
    def resolve(
        self,
        *,
        requested_profile: IngestionRuntimeProfile | str | None,
        extraction_enabled: bool,
        question_generation_enabled: bool,
        deterministic_identifier_scan_enabled: bool,
        semantic_linking_enabled: bool,
    ) -> IngestionRuntimeCapabilities:
        profile = self._coerce_profile(requested_profile)
        resolved_profile = self._resolve_profile(
            profile=profile,
            extraction_enabled=extraction_enabled,
            semantic_linking_enabled=semantic_linking_enabled,
        )
        if resolved_profile is IngestionRuntimeProfile.STRUCTURAL_ONLY:
            extraction_enabled = False
            semantic_linking_enabled = False
        return IngestionRuntimeCapabilities(
            requested_profile=profile,
            resolved_profile=resolved_profile,
            extraction_enabled=extraction_enabled,
            question_generation_enabled=question_generation_enabled,
            deterministic_identifier_scan_enabled=(
                deterministic_identifier_scan_enabled
            ),
            semantic_linking_enabled=semantic_linking_enabled,
        )

    @staticmethod
    def _coerce_profile(
        value: IngestionRuntimeProfile | str | None,
    ) -> IngestionRuntimeProfile:
        if isinstance(value, IngestionRuntimeProfile):
            return value
        if value is None:
            return IngestionRuntimeProfile.AUTO
        normalized = value.strip().lower()
        for profile in IngestionRuntimeProfile:
            if normalized == profile.value:
                return profile
        raise IngestionDependencyError(
            "Unsupported ingestion runtime profile.",
            error_code="ingestion.runtime_profile.invalid",
            details={"requested_profile": value},
        )

    @staticmethod
    def _resolve_profile(
        *,
        profile: IngestionRuntimeProfile,
        extraction_enabled: bool,
        semantic_linking_enabled: bool,
    ) -> IngestionRuntimeProfile:
        if profile is IngestionRuntimeProfile.AUTO:
            if extraction_enabled:
                return IngestionRuntimeProfile.SEMANTIC_ENRICHED
            return IngestionRuntimeProfile.STRUCTURAL_ONLY
        if profile is IngestionRuntimeProfile.SEMANTIC_ENRICHED and not extraction_enabled:
            raise IngestionDependencyError(
                "Semantic-enriched ingestion requires extraction to be enabled.",
                error_code="ingestion.runtime_profile.requires_extraction",
                details={
                    "requested_profile": profile.value,
                    "extraction_enabled": extraction_enabled,
                    "semantic_linking_enabled": semantic_linking_enabled,
                },
            )
        return profile
