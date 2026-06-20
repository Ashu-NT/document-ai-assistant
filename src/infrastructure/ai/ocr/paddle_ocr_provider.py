import os
import tempfile
from pathlib import Path
from typing import Any

from src.application.contracts.ai import OCRProvider
from src.config.settings import ocr_settings
from src.shared.exceptions import OCRProviderError


def _default_paddle_lang() -> str:
    return ocr_settings.paddle_lang or "en"


def _default_paddle_use_textline_orientation() -> bool:
    return ocr_settings.paddle_use_textline_orientation


def _default_paddle_ocr_version() -> str | None:
    return ocr_settings.paddle_ocr_version


class PaddleOCRProvider(OCRProvider):
    def __init__(
        self,
        *,
        lang: str | None = None,
        use_textline_orientation: bool | None = None,
        ocr_version: str | None = None,
        ocr_engine: Any | None = None,
    ) -> None:
        self.lang = lang or _default_paddle_lang()
        self.use_textline_orientation = (
            use_textline_orientation
            if use_textline_orientation is not None
            else _default_paddle_use_textline_orientation()
        )
        self.ocr_version = (
            ocr_version
            if ocr_version is not None
            else _default_paddle_ocr_version()
        )
        self._ocr_engine = ocr_engine

    def extract_text_from_image(self, image_path: str) -> str:
        try:
            result = self._get_ocr_engine().ocr(image_path)
        except Exception as exc:
            raise OCRProviderError(
                "Failed to extract text from image.",
                details={"image_path": image_path},
            ) from exc

        return self._extract_text(result)

    def _get_ocr_engine(self) -> Any:
        if self._ocr_engine is None:
            self._ocr_engine = self._build_ocr_engine()

        return self._ocr_engine

    def _build_ocr_engine(self) -> Any:
        cache_dir = Path(tempfile.gettempdir()) / "paddlex"
        os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(cache_dir))

        from paddleocr import PaddleOCR

        return PaddleOCR(
            lang=self.lang,
            ocr_version=self.ocr_version,
            use_textline_orientation=self.use_textline_orientation,
        )

    @classmethod
    def _extract_text(cls, result: Any) -> str:
        pages = result if isinstance(result, list) else [result]
        extracted_texts: list[str] = []

        for page in pages:
            texts = cls._page_texts(page)
            extracted_texts.extend(texts)

        return "\n".join(text for text in extracted_texts if text).strip()

    @staticmethod
    def _page_texts(page: Any) -> list[str]:
        if page is None:
            return []

        texts = None

        if isinstance(page, dict):
            texts = page.get("rec_texts", page.get("rec_text"))
        elif hasattr(page, "get"):
            texts = page.get("rec_texts", page.get("rec_text"))

        if texts is None:
            texts = getattr(page, "rec_texts", getattr(page, "rec_text", None))

        if texts is None:
            return []

        if isinstance(texts, str):
            return [texts]

        if isinstance(texts, tuple):
            texts = [texts]

        return [PaddleOCRProvider._coerce_text(text) for text in texts]

    @staticmethod
    def _coerce_text(value: Any) -> str:
        if isinstance(value, tuple) and value:
            return str(value[0])

        return str(value)
