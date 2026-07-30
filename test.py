from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert(r"C:\Users\ashu\Downloads\SupplierDocumentation_I\1612_454157_besecke\1612 0120 Besecke DRW 1612-33.30 RevD00 Mooring Control Box SB.pdf")

doc = result.document

for item, level in doc.iterate_items():
    print(type(item).__name__)
    print(getattr(item, "text", ""))
    print("-" * 50)