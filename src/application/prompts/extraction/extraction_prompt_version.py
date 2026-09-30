# v9 (2026-09-30): production prompt improvement 1 - identifier vocabulary
# now derives from the single shared identifier_type_guidance() (14 live
# IdentifierType values, was a stale hardcoded 9-value list); added
# EquipmentInfo name/model_number/serial_number/manufacturer_name semantic
# guidance; strengthened Specification-vs-SparePart guidance; added
# SparePart tool/material disambiguation guidance; strengthened the
# identifier contract (metadata-label/source_chunk_id exclusions); added a
# shared cross-entity disambiguation rule block. See
# outputs/architecture/ for the controlled-experiment report.
IDENTIFIER_EXTRACTION_PROMPT_VERSION = "v9"
