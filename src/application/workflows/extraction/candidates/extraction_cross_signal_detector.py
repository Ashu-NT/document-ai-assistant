import re

from src.application.prompts.extraction import ExtractionPromptType
from src.domain.document import DocumentChunk

_NON_WORD_PATTERN = re.compile(r"[\W_]+", re.UNICODE)
_WHITESPACE_PATTERN = re.compile(r"\s+")


def _normalize(value: str | None) -> str:
    if not value:
        return ""
    normalized = _NON_WORD_PATTERN.sub(" ", value)
    return _WHITESPACE_PATTERN.sub(" ", normalized).strip().lower()


# Content markers: keyword hits anywhere in the chunk's own text.
_CONTENT_MARKERS: dict[ExtractionPromptType, tuple[str, ...]] = {
    ExtractionPromptType.MANUFACTURER: (
        "manufactured by",
        "manufacturer",
        "made in",
        "oem",
    ),
    ExtractionPromptType.SUPPLIER: (
        "supplied by",
        "supplier",
        "vendor",
        "distributor",
        "distributed by",
    ),
    ExtractionPromptType.CONTACT_POINT: (
        "contact",
        "contact details",
        "email",
        "e mail",
        "telephone",
        "phone",
        "fax",
        "website",
        "web site",
    ),
    ExtractionPromptType.EQUIPMENT: (
        "model number",
        "nameplate",
        "equipment name",
        "unit model",
    ),
    ExtractionPromptType.SPARE_PART: (
        "spare part",
        "spare parts",
        "part number",
        "qty",
        "quantity",
    ),
    ExtractionPromptType.SPECIFICATION: (
        "technical data",
        "specification",
        "specifications",
        "rated",
        "ratings",
    ),
    ExtractionPromptType.MAINTENANCE_TASK: (
        "replace",
        "inspect",
        "lubricate",
        "tighten",
    ),
    ExtractionPromptType.MAINTENANCE_INTERVAL: (
        "operating hours",
        "running hours",
        "service interval",
        "maintenance schedule",
    ),
    ExtractionPromptType.PROCEDURE: (
        "step 1",
        "step by step",
        "disassembly",
        "reassembly",
    ),
    ExtractionPromptType.SAFETY_WARNING: (
        "danger",
        "warning",
        "caution",
        "hazard",
    ),
    ExtractionPromptType.TROUBLESHOOTING: (
        "symptom",
        "probable cause",
        "possible cause",
        "corrective action",
        "remedy",
    ),
}

# Header markers: keyword hits in the chunk's section path (its heading
# breadcrumb), scanned separately from body content since a heading match
# is a stronger signal than an incidental word in the body.
_HEADER_MARKERS: dict[ExtractionPromptType, tuple[str, ...]] = {
    ExtractionPromptType.MANUFACTURER: ("manufacturer",),
    ExtractionPromptType.SUPPLIER: ("supplier", "vendor"),
    ExtractionPromptType.CONTACT_POINT: (
        "contact",
        "contact details",
        "contact information",
    ),
    ExtractionPromptType.EQUIPMENT: ("equipment", "nameplate", "overview"),
    ExtractionPromptType.SPARE_PART: ("spare parts", "parts list"),
    ExtractionPromptType.SPECIFICATION: (
        "technical data",
        "specification",
        "specifications",
    ),
    ExtractionPromptType.MAINTENANCE_TASK: ("maintenance",),
    ExtractionPromptType.MAINTENANCE_INTERVAL: (
        "maintenance schedule",
        "maintenance interval",
    ),
    ExtractionPromptType.PROCEDURE: ("procedure", "installation", "assembly"),
    ExtractionPromptType.SAFETY_WARNING: ("safety",),
    ExtractionPromptType.TROUBLESHOOTING: ("troubleshooting",),
}

# Regex overrides, applied to the RAW (un-normalized) chunk content since
# they rely on punctuation/case that word-normalization would strip.
_MANUFACTURER_SUFFIX_PATTERN = re.compile(
    r"\b(?:gmbh|ltd\.?|inc\.?|llc|s\.a\.?|s\.p\.a\.?|ag|corp\.?|co\.)\b",
    re.IGNORECASE,
)
_PART_NUMBER_PATTERN = re.compile(r"\b[A-Z]{2,}-\d{2,}\b")
_SPEC_VALUE_PATTERN = re.compile(
    r"\b\d+(?:[.,]\d+)?\s?(?:v|kv|a|ma|hz|khz|w|kw|mm|cm|bar|psi|rpm|db|%)\b",
    re.IGNORECASE,
)
_EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b", re.IGNORECASE)
_URL_PATTERN = re.compile(r"\b(?:https?://|www\.)[^\s<>()]+\b", re.IGNORECASE)
_LABELED_PHONE_PATTERN = re.compile(
    r"\b(?:tel(?:ephone)?|phone|fax)\b\s*[:#]?\s*\+?\d[\d\s()./-]{5,}\d",
    re.IGNORECASE,
)
_INTERVAL_PATTERN = re.compile(
    r"\bevery\s+\d+(?:[.,]\d+)?\s+(?:hour|hours|day|days|week|weeks|month|months|year|years)\b",
    re.IGNORECASE,
)

_EQUIPMENT_MODEL_NOUN = (
    r"(?:generator\s+set|genset|engine|generator|motor|pump|compressor|"
    r"turbine|alternator|gearbox|machine)"
)
_EQUIPMENT_MODEL_CODE_TOKEN = r"[A-Za-z0-9]{5,15}"
_EQUIPMENT_MODEL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        rf"\b{_EQUIPMENT_MODEL_NOUN}\s+with\s+({_EQUIPMENT_MODEL_CODE_TOKEN})\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\b({_EQUIPMENT_MODEL_CODE_TOKEN})\s+{_EQUIPMENT_MODEL_NOUN}\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\b(?:equipment\s+model|unit\s+model|model)\s*(?:no\.?|number|:)?\s*"
        rf"({_EQUIPMENT_MODEL_CODE_TOKEN})\b",
        re.IGNORECASE,
    ),
)
_EQUIPMENT_MODEL_EXCLUDED_PRECEDING_CONTEXT = re.compile(
    r"\b(?:certificate|cert\.?|order\s*no\.?|part\s*no\.?|spare\s*part|"
    r"serial\s*no\.?|serial\s*number|document\s*no\.?|doc\.?\s*no\.?|"
    r"reference\s*no\.?|ref\.?)\b",
    re.IGNORECASE,
)
_EQUIPMENT_MODEL_EXCLUSION_WINDOW = 30


def _looks_like_equipment_model_code(candidate: str) -> bool:
    has_letter = any(char.isalpha() for char in candidate)
    has_digit = any(char.isdigit() for char in candidate)
    return has_letter and has_digit


def _has_excluded_preceding_context(raw_content: str, match_start: int) -> bool:
    window_start = max(0, match_start - _EQUIPMENT_MODEL_EXCLUSION_WINDOW)
    preceding = raw_content[window_start:match_start]
    return bool(_EQUIPMENT_MODEL_EXCLUDED_PRECEDING_CONTEXT.search(preceding))


def _has_equipment_model_reference(raw_content: str) -> bool:
    if not raw_content:
        return False
    for pattern in _EQUIPMENT_MODEL_PATTERNS:
        for match in pattern.finditer(raw_content):
            candidate = match.group(1)
            if not _looks_like_equipment_model_code(candidate):
                continue
            if _has_excluded_preceding_context(raw_content, match.start()):
                continue
            return True
    return False


class ExtractionCrossSignalDetector:
    """
    Deterministic, multi-label signal detection layered on top of a
    chunk's single-winner ChunkType. ChunkSemanticSignalExtractor picks ONE
    dominant type per chunk (used for retrieval routing/reporting too, so
    it must stay single-label) — this detector instead flags EVERY entity
    type with at least one keyword/header/regex/table hit, since a chunk
    can legitimately carry several plausible entity types at once (e.g. a
    maintenance-interval table that also names a manufacturer).

    No scoring or threshold: any hit is enough to include a type. This
    only decides what's worth ASKING the LLM about — the LLM still decides
    whether the entity is actually present, so over-inclusion here costs a
    slightly less-narrow prompt, not a wrong extraction.
    """

    def detect(self, chunk: DocumentChunk) -> frozenset[ExtractionPromptType]:
        content_text = _normalize(chunk.content)
        header_text = _normalize(" ".join(chunk.section_path))
        raw_content = chunk.content or ""

        detected: set[ExtractionPromptType] = set()

        for entity_type, markers in _CONTENT_MARKERS.items():
            if self._any_marker_hits(content_text, markers):
                detected.add(entity_type)

        for entity_type, markers in _HEADER_MARKERS.items():
            if self._any_marker_hits(header_text, markers):
                detected.add(entity_type)

        if _MANUFACTURER_SUFFIX_PATTERN.search(raw_content):
            detected.add(ExtractionPromptType.MANUFACTURER)

        if _PART_NUMBER_PATTERN.search(raw_content):
            detected.add(ExtractionPromptType.SPARE_PART)

        if _SPEC_VALUE_PATTERN.search(raw_content):
            detected.add(ExtractionPromptType.SPECIFICATION)

        if (
            _EMAIL_PATTERN.search(raw_content)
            or _URL_PATTERN.search(raw_content)
            or _LABELED_PHONE_PATTERN.search(raw_content)
        ):
            detected.add(ExtractionPromptType.CONTACT_POINT)

        if _INTERVAL_PATTERN.search(raw_content):
            detected.add(ExtractionPromptType.MAINTENANCE_INTERVAL)

        if _has_equipment_model_reference(raw_content):
            detected.add(ExtractionPromptType.EQUIPMENT)

        if chunk.table_ids:
            detected.add(ExtractionPromptType.SPARE_PART)
            detected.add(ExtractionPromptType.SPECIFICATION)

        return frozenset(detected)

    @staticmethod
    def _any_marker_hits(text: str, markers: tuple[str, ...]) -> bool:
        if not text:
            return False
        padded = f" {text} "
        return any(f" {marker} " in padded for marker in markers)
