from docling.document_converter import DocumentConverter
from pathlib import Path
import json

# Create converter (no OCR for speed)
converter = DocumentConverter()

pdf_path = Path(r"C:\Users\ashuf\Downloads\E6_DV-DP_Lab_SoSe26_en.pdf")
result = converter.convert(pdf_path)

# Convert to Python dict
doc_dict = result.document.export_to_dict()

# Dump to Markdown file
output_path = Path("docling_dump_E6_DV-DP_Lab_SoSe26_en.md")
with open(output_path, "w", encoding="utf-8") as f:
    f.write("```json\n")
    json.dump(doc_dict, f, indent=2)
    f.write("\n```")

print(f"Dumped JSON to {output_path.resolve()}")
