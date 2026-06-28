from pathlib import Path

from src.application.contracts.ai import OCRResult
from src.application.workflows.parsing.ocr import (
    OCRMergeResult,
    OCRTarget,
    OCRTargetExecutionResult,
    OCRTargetType,
    OCRTrace,
    PageOCRFallbackWorkflow,
)


class FakeOCRService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def extract_result_from_image(self, image_path: str, activity_context=None) -> OCRResult:
        self.calls.append(image_path)
        return OCRResult(
            text="Detected page text",
            provider_name="FakeOCRService",
            confidence=0.8,
            source_image_path=image_path,
        )


class FakeTargetSelector:
    def __init__(self, target: OCRTarget) -> None:
        self.target = target
        self.calls: list[tuple[str, int | None]] = []
        self.policy = type("Policy", (), {"page_render_dpi": 150})()

    def select(self, *, document_path: str, canonical_elements, page_count: int | None):
        self.calls.append((document_path, page_count))
        return type(
            "SelectionResult",
            (),
            {
                "page_analyses": [],
                "targets": [self.target],
                "warnings": [],
            },
        )()


class FakePageRenderer:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int, int, Path]] = []

    def render_page(self, pdf_path: str, page_number: int, dpi: int, output_dir: Path):
        self.calls.append((pdf_path, page_number, dpi, output_dir))
        return type("RenderedPage", (), {"image_path": "outputs/debug_ocr/pages/page_1.png"})()


class FakeMerger:
    def __init__(self) -> None:
        self.execution_results: list[OCRTargetExecutionResult] = []

    def merge(self, **kwargs) -> OCRMergeResult:
        self.execution_results = list(kwargs["execution_results"])
        return OCRMergeResult(
            canonical_elements=kwargs["canonical_elements"],
            ocr_trace=OCRTrace(document_path=kwargs["document_path"], page_count=1),
        )


def test_workflow_renders_selected_page_and_calls_ocr_service() -> None:
    target = OCRTarget(
        target_id="page:1",
        target_type=OCRTargetType.PAGE,
        document_path="manual.pdf",
        page_number=1,
        reason="probable_scanned_page",
    )
    service = FakeOCRService()
    selector = FakeTargetSelector(target)
    renderer = FakePageRenderer()
    merger = FakeMerger()
    workflow = PageOCRFallbackWorkflow(
        ocr_service=service,
        target_selector=selector,
        canonical_ocr_merger=merger,
        page_renderer=renderer,
        region_cropper=None,
        output_dir=Path("outputs/debug_ocr"),
    )

    workflow.run(
        file_path="manual.pdf",
        canonical_elements=[],
        page_count=1,
    )

    assert selector.calls == [("manual.pdf", 1)]
    assert renderer.calls[0][0] == "manual.pdf"
    assert service.calls == ["outputs/debug_ocr/pages/page_1.png"]
    assert merger.execution_results[0].ocr_result is not None
