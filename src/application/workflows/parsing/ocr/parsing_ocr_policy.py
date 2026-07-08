from dataclasses import dataclass

from src.config.settings import docling_settings, ocr_settings


@dataclass(frozen=True, slots=True)
class ParsingOCRPolicy:
    docling_ocr_enabled: bool
    provider_requested: bool
    provider_name: str
    asset_ocr_enabled: bool
    page_fallback_enabled: bool
    region_fallback_enabled: bool

    @property
    def provider_runtime_enabled(self) -> bool:
        return (
            self.asset_ocr_enabled
            or self.page_fallback_enabled
            or self.region_fallback_enabled
        )


def resolve_parsing_ocr_policy(
    *,
    enable_docling_ocr_override: bool | None = None,
) -> ParsingOCRPolicy:
    docling_ocr_enabled = (
        enable_docling_ocr_override
        if enable_docling_ocr_override is not None
        else docling_settings.enable_ocr
    )
    provider_requested = ocr_settings.enabled
    provider_name = ocr_settings.provider

    asset_ocr_enabled = provider_requested and ocr_settings.asset_enabled
    page_fallback_enabled = (
        provider_requested and ocr_settings.page_fallback_enabled
    )
    region_fallback_enabled = (
        provider_requested and ocr_settings.region_fallback_enabled
    )

    return ParsingOCRPolicy(
        docling_ocr_enabled=docling_ocr_enabled,
        provider_requested=provider_requested,
        provider_name=provider_name,
        asset_ocr_enabled=asset_ocr_enabled,
        page_fallback_enabled=page_fallback_enabled,
        region_fallback_enabled=region_fallback_enabled,
    )
