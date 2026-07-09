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
    def __init__(self, targets: OCRTarget | list[OCRTarget]) -> None:
        self.targets = targets if isinstance(targets, list) else [targets]
        self.target = self.targets[0]
        self.calls: list[tuple[str, int | None]] = []
        self.policy = type("Policy", (), {"page_render_dpi": 150})()

    def select(self, *, document_path: str, canonical_elements, page_count: int | None):
        self.calls.append((document_path, page_count))
        return type(
            "SelectionResult",
            (),
            {
                "page_analyses": [],
                "targets": list(self.targets),
                "warnings": [],
            },
        )()


class FakeOpenedPDFDocument:
    def __init__(self, pdf_path: str, calls: list) -> None:
        self.pdf_path = pdf_path
        self.calls = calls
        self.closed = False

    def render_page(self, page_number: int, dpi: int, output_dir: Path):
        self.calls.append((self.pdf_path, page_number, dpi, output_dir))
        output_dir.mkdir(parents=True, exist_ok=True)
        image_path = output_dir / "page_1.png"
        image_path.write_bytes(b"fake-page")
        return type("RenderedPage", (), {"image_path": str(image_path)})()

    def close(self) -> None:
        self.closed = True


class FakePageRenderer:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int, int, Path]] = []
        self.opened_documents: list[FakeOpenedPDFDocument] = []

    def open(self, pdf_path: str) -> FakeOpenedPDFDocument:
        opened = FakeOpenedPDFDocument(pdf_path, self.calls)
        self.opened_documents.append(opened)
        return opened


class FakeRegionCropper:
    def __init__(self) -> None:
        self.crop_calls = 0

    def crop(self, image_path: str, bbox, output_dir: Path):
        self.crop_calls += 1
        output_dir.mkdir(parents=True, exist_ok=True)
        cropped_path = output_dir / f"page_1_crop_{self.crop_calls}.png"
        cropped_path.write_bytes(b"fake-region")
        return type("CroppedRegion", (), {"image_path": str(cropped_path)})()


class FakeMerger:
    def __init__(self) -> None:
        self.execution_results: list[OCRTargetExecutionResult] = []

    def merge(self, **kwargs) -> OCRMergeResult:
        self.execution_results = list(kwargs["execution_results"])
        return OCRMergeResult(
            canonical_elements=kwargs["canonical_elements"],
            ocr_trace=OCRTrace(document_path=kwargs["document_path"], page_count=1),
        )


def test_workflow_renders_selected_page_and_calls_ocr_service(tmp_path) -> None:
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
        output_dir=tmp_path,
    )

    workflow.run(
        file_path="manual.pdf",
        canonical_elements=[],
        page_count=1,
    )

    assert selector.calls == [("manual.pdf", 1)]
    assert renderer.calls[0][0] == "manual.pdf"
    assert len(service.calls) == 1
    assert Path(service.calls[0]).name == "page_1.png"
    assert merger.execution_results[0].ocr_result is not None


def test_workflow_cleans_up_generated_page_artifacts_when_trace_disabled(
    tmp_path,
) -> None:
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
    workflow = PageOCRFallbackWorkflow(
        ocr_service=service,
        target_selector=selector,
        canonical_ocr_merger=FakeMerger(),
        page_renderer=renderer,
        region_cropper=None,
        output_dir=tmp_path,
        trace_enabled=False,
    )

    workflow.run(
        file_path="manual.pdf",
        canonical_elements=[],
        page_count=1,
    )

    assert not (tmp_path / "pages" / "page_1.png").exists()
    assert not (tmp_path / "pages").exists()


def test_workflow_preserves_generated_page_artifacts_when_trace_enabled(
    tmp_path,
) -> None:
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
    workflow = PageOCRFallbackWorkflow(
        ocr_service=service,
        target_selector=selector,
        canonical_ocr_merger=FakeMerger(),
        page_renderer=renderer,
        region_cropper=None,
        output_dir=tmp_path,
        trace_enabled=True,
    )

    workflow.run(
        file_path="manual.pdf",
        canonical_elements=[],
        page_count=1,
    )

    assert (tmp_path / "pages" / "page_1.png").exists()


def test_workflow_cleans_up_generated_region_artifacts_when_trace_disabled(
    tmp_path,
) -> None:
    target = OCRTarget(
        target_id="region:1",
        target_type=OCRTargetType.REGION,
        document_path="manual.pdf",
        page_number=1,
        reason="text_poor_region",
        bbox=type("BBox", (), {"x1": 0.1, "y1": 0.1, "x2": 0.9, "y2": 0.9})(),
    )
    service = FakeOCRService()
    selector = FakeTargetSelector(target)
    renderer = FakePageRenderer()
    workflow = PageOCRFallbackWorkflow(
        ocr_service=service,
        target_selector=selector,
        canonical_ocr_merger=FakeMerger(),
        page_renderer=renderer,
        region_cropper=FakeRegionCropper(),
        output_dir=tmp_path,
        trace_enabled=False,
    )

    workflow.run(
        file_path="manual.pdf",
        canonical_elements=[],
        page_count=1,
    )

    assert not (tmp_path / "pages" / "page_1.png").exists()
    assert not (tmp_path / "regions").exists()
    assert not (tmp_path / "pages").exists()


def test_workflow_renders_shared_page_only_once_for_multiple_region_targets(
    tmp_path,
) -> None:
    bbox = type("BBox", (), {"x1": 0.1, "y1": 0.1, "x2": 0.9, "y2": 0.9})()
    targets = [
        OCRTarget(
            target_id="region:1",
            target_type=OCRTargetType.REGION,
            document_path="manual.pdf",
            page_number=1,
            reason="text_poor_region",
            bbox=bbox,
        ),
        OCRTarget(
            target_id="region:2",
            target_type=OCRTargetType.REGION,
            document_path="manual.pdf",
            page_number=1,
            reason="text_poor_region",
            bbox=bbox,
        ),
    ]
    service = FakeOCRService()
    selector = FakeTargetSelector(targets)
    renderer = FakePageRenderer()
    region_cropper = FakeRegionCropper()
    workflow = PageOCRFallbackWorkflow(
        ocr_service=service,
        target_selector=selector,
        canonical_ocr_merger=FakeMerger(),
        page_renderer=renderer,
        region_cropper=region_cropper,
        output_dir=tmp_path,
        trace_enabled=True,
    )

    workflow.run(
        file_path="manual.pdf",
        canonical_elements=[],
        page_count=1,
    )

    assert len(renderer.opened_documents) == 1
    assert len(renderer.calls) == 1
    assert region_cropper.crop_calls == 2
    assert len(service.calls) == 2
    assert renderer.opened_documents[0].closed is True
