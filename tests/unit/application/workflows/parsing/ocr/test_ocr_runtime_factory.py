from types import SimpleNamespace

import src.application.workflows.parsing.ocr.ocr_runtime_factory as ocr_runtime_factory
import src.application.workflows.parsing.ocr.parsing_ocr_policy as parsing_ocr_policy
from src.application.workflows.parsing.ocr import (
    ParsingOCRPolicy,
    resolve_parsing_ocr_policy,
)
from src.shared.ids import IdGenerator


def test_resolve_parsing_ocr_policy_gates_provider_stages_when_provider_disabled(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        parsing_ocr_policy,
        "docling_settings",
        SimpleNamespace(enable_ocr=False),
    )
    monkeypatch.setattr(
        parsing_ocr_policy,
        "ocr_settings",
        SimpleNamespace(
            enabled=False,
            provider="paddleocr",
            asset_enabled=True,
            page_fallback_enabled=True,
            region_fallback_enabled=True,
        ),
    )

    policy = resolve_parsing_ocr_policy()

    assert policy.docling_ocr_enabled is False
    assert policy.provider_requested is False
    assert policy.provider_runtime_enabled is False
    assert policy.asset_ocr_enabled is False
    assert policy.page_fallback_enabled is False
    assert policy.region_fallback_enabled is False


def test_resolve_parsing_ocr_policy_applies_docling_override(monkeypatch) -> None:
    monkeypatch.setattr(
        parsing_ocr_policy,
        "docling_settings",
        SimpleNamespace(enable_ocr=False),
    )
    monkeypatch.setattr(
        parsing_ocr_policy,
        "ocr_settings",
        SimpleNamespace(
            enabled=True,
            provider="paddleocr",
            asset_enabled=True,
            page_fallback_enabled=False,
            region_fallback_enabled=False,
        ),
    )

    policy = resolve_parsing_ocr_policy(enable_docling_ocr_override=True)

    assert policy.docling_ocr_enabled is True
    assert policy.provider_requested is True
    assert policy.provider_runtime_enabled is True
    assert policy.asset_ocr_enabled is True


def test_build_parsing_ocr_runtime_skips_provider_construction_when_no_stages_enabled(
    monkeypatch,
) -> None:
    build_calls: list[str] = []
    monkeypatch.setattr(
        ocr_runtime_factory,
        "build_ocr_provider",
        lambda: build_calls.append("provider") or object(),
    )
    policy = ParsingOCRPolicy(
        docling_ocr_enabled=False,
        provider_requested=True,
        provider_name="paddleocr",
        asset_ocr_enabled=False,
        page_fallback_enabled=False,
        region_fallback_enabled=False,
    )

    runtime = ocr_runtime_factory.build_parsing_ocr_runtime(
        id_generator=IdGenerator(),
        policy=policy,
    )

    assert runtime.policy == policy
    assert runtime.canonical_element_ocr_enricher is None
    assert runtime.page_ocr_fallback_workflow is None
    assert build_calls == []


def test_build_parsing_ocr_runtime_builds_asset_enricher_when_enabled(
    monkeypatch,
) -> None:
    build_calls: list[str] = []

    monkeypatch.setattr(
        ocr_runtime_factory,
        "build_ocr_provider",
        lambda: build_calls.append("provider") or "provider",
    )
    monkeypatch.setattr(
        ocr_runtime_factory,
        "OCRService",
        lambda provider, **kwargs: ("ocr_service", provider),
    )
    monkeypatch.setattr(
        ocr_runtime_factory,
        "CanonicalElementOCREnricher",
        lambda service: ("enricher", service),
    )

    policy = ParsingOCRPolicy(
        docling_ocr_enabled=False,
        provider_requested=True,
        provider_name="paddleocr",
        asset_ocr_enabled=True,
        page_fallback_enabled=False,
        region_fallback_enabled=False,
    )

    runtime = ocr_runtime_factory.build_parsing_ocr_runtime(
        id_generator=IdGenerator(),
        policy=policy,
    )

    assert runtime.policy == policy
    assert runtime.canonical_element_ocr_enricher == (
        "enricher",
        ("ocr_service", "provider"),
    )
    assert runtime.page_ocr_fallback_workflow is None
    assert build_calls == ["provider"]
