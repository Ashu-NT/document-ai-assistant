from docling.document_converter import DocumentConverter
from pathlib import Path
import json

# Create converter (no OCR for speed)
converter = DocumentConverter()

pdf_path = Path(r"C:\Users\ashuf\Downloads\E6_DV-DP_Lab_SoSe26_en.pdf")
converter = DocumentConverter()
result = converter.convert(pdf_path)

doc = result.document

for item, level in doc.iterate_items():
    if not item.prov:
        continue

    for provenance in item.prov:
        bbox = provenance.bbox

        print("Type:", item.label)
        print("Page:", provenance.page_no)
        print("Text:", getattr(item, "text", ""))
        print("Left:", bbox.l)
        print("Top:", bbox.t)
        print("Right:", bbox.r)
        print("Bottom:", bbox.b)
        print("Origin:", bbox.coord_origin)
        print("-" * 50)