import threading

# A single, shared, process-wide lock around every same-process pypdfium2
# call site (PdfLinkAnnotationExtractor and PDFPageRenderer). No concurrent
# code path exists in this repo today (CLI/script-only, no web server, no
# thread pool touches parsing) - this has zero behavioral effect now, but
# makes any future introduction of threading/async/a web server around
# ingestion safe by construction rather than relying on programmer
# discipline. A lock scoped to only one of the two call sites would not
# actually prevent a future scenario where they run on two threads of the
# same process at once, so both must share this exact lock object.
PDFIUM_PROCESS_LOCK: threading.Lock = threading.Lock()

__all__ = ["PDFIUM_PROCESS_LOCK"]
