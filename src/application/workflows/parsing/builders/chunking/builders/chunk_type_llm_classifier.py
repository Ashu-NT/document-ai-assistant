import re

from src.domain.common import ChunkType

_NORMALIZE = re.compile(r"[^a-z0-9]+")

_CHUNK_TYPES_DOC = "\n".join(
    f"- {ct.value}: {desc}"
    for ct, desc in [
        (ChunkType.TECHNICAL_SPECIFICATION, "Technical specs, measurements, ratings, parameters"),
        (ChunkType.MAINTENANCE_PROCEDURE, "Step-by-step maintenance or service instructions"),
        (ChunkType.MAINTENANCE_INTERVAL, "Scheduled maintenance timing, service frequencies"),
        (ChunkType.INSTALLATION_INSTRUCTION, "Installation, mounting, or assembly steps"),
        (ChunkType.OPERATION_INSTRUCTION, "Operating procedures, startup/shutdown steps"),
        (ChunkType.TROUBLESHOOTING, "Fault diagnosis, probable causes, remedies"),
        (ChunkType.SAFETY_WARNING, "Safety warnings, cautions, hazard notices"),
        (ChunkType.CERTIFICATION_INFO, "Certifications, approvals, ATEX/IECEx, compliance statements"),
        (ChunkType.SPARE_PARTS_TABLE, "Spare parts lists, part numbers, ordering data"),
        (ChunkType.DRAWING_REFERENCE, "Diagrams, figures, drawing references"),
        (ChunkType.OVERVIEW, "General overview or introduction to a product or section"),
        (ChunkType.GENERAL, "Content that does not clearly fit any other type"),
    ]
)


def build_classification_prompt(*, content: str, section_path: list[str]) -> str:
    path_str = " > ".join(section_path) if section_path else "(none)"
    return (
        "You are classifying a chunk from a technical product document.\n\n"
        f"Section path: {path_str}\n"
        f"Content (first 600 chars):\n{content[:1000]}\n\n"
        "Classify this chunk into exactly ONE of the types below.\n"
        "Reply with ONLY the type name (e.g. maintenance_interval). No explanation.\n\n"
        f"{_CHUNK_TYPES_DOC}\n\n"
        "Type:"
    )


def parse_chunk_type_response(response: str) -> ChunkType:
    normalized = _NORMALIZE.sub("_", response.strip().lower()).strip("_")
    for chunk_type in ChunkType:
        if normalized in {chunk_type.value, chunk_type.name.lower()}:
            return chunk_type
    first_word = normalized.split("_")[0] if "_" in normalized else normalized
    for chunk_type in ChunkType:
        if chunk_type.value.startswith(first_word) or chunk_type.name.lower().startswith(first_word):
            return chunk_type
    return ChunkType.GENERAL


class ChunkTypeLLMClassifier:
    """Calls an LLM to determine ChunkType for a single piece of content.

    Used by ChunkTypeClassificationWorkflow — not wired into ChunkTypeResolver.
    Stateless beyond the injected LLMService so it can be constructed once
    and called repeatedly without side effects.
    """

    def __init__(self, llm_service=None, model: str | None = None) -> None:
        self._llm_service = llm_service
        self._model = model

    def is_available(self) -> bool:
        return self._llm_service is not None

    def classify(
        self,
        *,
        content: str | None,
        section_path: list[str],
    ) -> ChunkType | None:
        """Return a ChunkType, or None when unavailable or when LLM returns GENERAL."""
        if self._llm_service is None or not content or not content.strip():
            return None
        prompt = build_classification_prompt(content=content, section_path=section_path)
        try:
            response = self._llm_service.generate(prompt, model=self._model)
            result = parse_chunk_type_response(response or "")
            return result if result != ChunkType.GENERAL else None
        except Exception:
            return None
