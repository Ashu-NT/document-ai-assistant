from src.infrastructure.parsing.docling import docling_conversion_fingerprint


class FakeDoclingSettings:
    def __init__(
        self,
        *,
        pdf_backend: str = "docling_parse",
        accelerator_device: str = "auto",
        images_scale: float = 1.0,
        num_threads: int = 1,
        enable_table_structure: bool = True,
        table_structure_mode: str = "accurate",
        table_cell_matching: bool = True,
        enable_ocr: bool = True,
        ocr_engine: str = "auto",
        rapidocr_backend: str = "torch",
        force_full_page_ocr: bool = False,
        bitmap_area_threshold: float = 0.05,
        ocr_batch_size: int = 4,
        layout_batch_size: int = 4,
        table_batch_size: int = 4,
        max_table_grid_cells: int = 200_000,
    ) -> None:
        self.pdf_backend = pdf_backend
        self.accelerator_device = accelerator_device
        self.images_scale = images_scale
        self.num_threads = num_threads
        self.enable_table_structure = enable_table_structure
        self.table_structure_mode = table_structure_mode
        self.table_cell_matching = table_cell_matching
        self.enable_ocr = enable_ocr
        self.ocr_engine = ocr_engine
        self.rapidocr_backend = rapidocr_backend
        self.force_full_page_ocr = force_full_page_ocr
        self.bitmap_area_threshold = bitmap_area_threshold
        self.ocr_batch_size = ocr_batch_size
        self.layout_batch_size = layout_batch_size
        self.table_batch_size = table_batch_size
        self.max_table_grid_cells = max_table_grid_cells


def test_fingerprint_is_deterministic_for_identical_settings(monkeypatch) -> None:
    monkeypatch.setattr(
        docling_conversion_fingerprint,
        "docling_settings",
        FakeDoclingSettings(),
    )

    first = docling_conversion_fingerprint.compute_docling_conversion_fingerprint()
    second = docling_conversion_fingerprint.compute_docling_conversion_fingerprint()

    assert first == second


def test_fingerprint_changes_when_a_material_setting_changes(monkeypatch) -> None:
    monkeypatch.setattr(
        docling_conversion_fingerprint,
        "docling_settings",
        FakeDoclingSettings(rapidocr_backend="torch"),
    )
    baseline = docling_conversion_fingerprint.compute_docling_conversion_fingerprint()

    monkeypatch.setattr(
        docling_conversion_fingerprint,
        "docling_settings",
        FakeDoclingSettings(rapidocr_backend="onnxruntime"),
    )
    changed = docling_conversion_fingerprint.compute_docling_conversion_fingerprint()

    assert baseline != changed


def test_fingerprint_changes_with_table_structure_mode(monkeypatch) -> None:
    monkeypatch.setattr(
        docling_conversion_fingerprint,
        "docling_settings",
        FakeDoclingSettings(table_structure_mode="accurate"),
    )
    baseline = docling_conversion_fingerprint.compute_docling_conversion_fingerprint()

    monkeypatch.setattr(
        docling_conversion_fingerprint,
        "docling_settings",
        FakeDoclingSettings(table_structure_mode="fast"),
    )
    changed = docling_conversion_fingerprint.compute_docling_conversion_fingerprint()

    assert baseline != changed


def test_fingerprint_changes_with_enable_ocr_override(monkeypatch) -> None:
    monkeypatch.setattr(
        docling_conversion_fingerprint,
        "docling_settings",
        FakeDoclingSettings(enable_ocr=True),
    )

    default_fingerprint = (
        docling_conversion_fingerprint.compute_docling_conversion_fingerprint()
    )
    override_disabled_fingerprint = (
        docling_conversion_fingerprint.compute_docling_conversion_fingerprint(
            enable_ocr_override=False
        )
    )
    override_matches_default_fingerprint = (
        docling_conversion_fingerprint.compute_docling_conversion_fingerprint(
            enable_ocr_override=True
        )
    )

    assert default_fingerprint != override_disabled_fingerprint
    assert default_fingerprint == override_matches_default_fingerprint
